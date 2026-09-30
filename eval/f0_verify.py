"""F0: can a self-hosted NLI model stand in for the judge, and what would zero tolerance suppress? (Phase F spike)

A diagnosis on the shipped pipeline's cached golden answers (`pipeline-answers-e5.json`: 96 rows x 5 runs,
305 distinct answers). No product code changes and no new synthesis calls: only the judge is paid for.

A claim is checked against the sources it *cites*, not all eight retrieved chunks as today's faithfulness does
(which is why that can't see a real citation on a claim the chunk doesn't make: Phase B's laundering). Two units:
a sentence with its citations, and a span (the uncited sentences just before a citation, plus the one carrying it).
A cited opinion counts with every retrieved page of it; whether the cited page itself holds the claim is scored
apart (`pinpoint`). The judge sees the question and the whole answer as context.

    uv run python eval/f0_verify.py pairs                              # split, pair, judge (~$1.65 with the page pass)
    uv run --group spike python eval/f0_verify.py nli --model base     # also: large, hhem
    uv run python eval/f0_verify.py report                             # F1, suppression, check sheet
    uv run python eval/f0_verify.py agreement                          # check-sheet verdicts vs the judge
"""

import argparse
import hashlib
import json
import random
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RESULTS = Path("eval/results")
ANSWERS = RESULTS / "pipeline-answers-e5.json"
RAGAS = RESULTS / "ragas-golden-2026-09-28-pipeline-answers-e5.json"  # the same answers, judged the old way
PAIRS = RESULTS / "f0-pairs.json"
CHECK = RESULTS / "f0-judge-check.md"
QUESTIONS = "eval/golden.jsonl"
REPORT = RESULTS / "f0-report.json"
MODELS = {
    "base": "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
    "large": "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli",
    "hhem": "vectara/hallucination_evaluation_model",
    # trained for exactly this (does a document support a sentence?), after F0's first three missed
    "minicheck-roberta": "lytang/MiniCheck-RoBERTa-Large",
    "minicheck-deberta": "lytang/MiniCheck-DeBERTa-v3-Large",
}
TOP = 3  # --premise top: the windows the reranker ranks highest for the claim, instead of every page of an opinion
WINDOW, STRIDE = 200, 100  # premise words per window: legal text runs ~1.5 tokens a word, so 512 holds it + the claim

CITATION_RE = re.compile(r"\[([^\[\]]+)\]")
OPINION_RE = re.compile(r"\d+ T\.C\. No\. \d+|T\.C\. Memo\. \d{4}-\d+")
ABBREV = re.compile(r"\b(?:U\.S\.C|U\.S|Treas|Reg|Regs|Sec|Pub|No|Nos|Memo|v|e\.g|i\.e|Inc|Co|Corp|Rev|Proc|Rul|"
                    r"T\.C|Cir|Stat|ch|pt|p|pp|cf|Mr|Ms|Dr|Jr|St|seq|par|para|art|[A-Z])\.$", re.I)
# re.I: "I.R.C. sec. 1402(a)(1)" split mid-citation; [A-Z]: "Joseph M. Smith"
MARKER = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")


def sentences(text: str) -> list[str]:
    """Split outside brackets, at . ! ? followed by a space, never after an abbreviation. A citation the model
    put after the full stop ("... profit. [26 CFR 1.183-1(c)(1)]") is handed back to the sentence it closes."""
    pieces = []
    for line in text.splitlines():
        line = MARKER.sub("", line).strip()
        depth, start = 0, 0
        for i, ch in enumerate(line):
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth = max(0, depth - 1)
            elif (ch in ".!?" and depth == 0 and line[i + 1:i + 2] == " "
                  and not ABBREV.search(line[start:i + 1])):
                pieces.append(line[start:i + 1].strip())
                start = i + 2
        pieces.append(line[start:].strip())
    out: list[str] = []
    for s in pieces:
        lead = re.match(r"^((?:\[[^\[\]]+\][,;.\s]*)+)(.*)$", s)
        if lead and out:
            out[-1] += " " + lead.group(1).strip()
            s = lead.group(2).strip()
        if re.search(r"[A-Za-z]{3}", CITATION_RE.sub("", s)):
            out.append(s)
    return out


def structural(sentence: str) -> bool:
    """A line that states no claim: a section heading, a markdown title, a label ending in a colon, or the tax-year
    statement rule 6 asks for. §9's completeness is over material claims, so these are not counted as uncited (F3
    found F0's count included them: 71 headings and 59 year statements in one arm)."""
    from taxcite.generate import PART_RE
    s = sentence.strip().strip("*").strip()
    if re.match(r"(Not in the sources|INSUFFICIENT EVIDENCE)\b", s, re.I):  # says what's missing, claims nothing
        return True
    return bool(PART_RE.match(sentence) or re.match(r"^#+\s", sentence) or s.endswith(":")
                or (sentence.startswith("**") and sentence.rstrip().endswith("**"))
                or (len(s) < 90 and re.search(r"\b20\d\d\b", s)
                    and re.search(r"\b(tax year|year I answer|answer(ing)? for)\b", s, re.I)))


def claim_text(sentence: str) -> str:
    """The sentence without its brackets or markdown, as the claim extractor would state it."""
    s = CITATION_RE.sub("", sentence).replace("**", "")
    return re.sub(r"\s+([,.;:])", r"\1", re.sub(r"\s{2,}", " ", s)).strip(" ,;")


def kind_of(citation: str) -> str:
    """The sub-query kind a citation belongs to: what F3's sections would be. Two sub-queries of one kind
    share their search (`decompose.retrieve`), so kind is the section in practice."""
    return "case_law" if OPINION_RE.search(citation) else "statutory"


def split(row_id: str) -> str:
    """Tune half / report half, by question, so near-identical answers of one question never straddle."""
    return "tune" if int(hashlib.sha256(row_id.encode()).hexdigest(), 16) % 2 == 0 else "report"


# ---------------------------------------------------------------- pairs: split, pair, judge

def headings(cache: dict) -> dict[tuple[str, str], str]:
    """Each cached chunk's heading, which synthesis saw ("[citation] (heading)") but the answer cache didn't keep.
    An opinion's case name is only in its heading, so without it a claim naming the case can't be supported."""
    from taxcite.store import connect

    wanted = {(c["citation"], c["text"]) for runs in cache.values() for x in runs for c in x["contexts"]}
    with connect() as conn:
        rows = conn.execute("SELECT citation, heading, text FROM chunks WHERE citation = ANY(%s)",
                            (sorted({c for c, _ in wanted}),)).fetchall()
    found = {(c, t): h for c, h, t in rows}
    assert wanted <= found.keys(), f"{len(wanted - found.keys())} cached chunks not in Postgres"
    return found


def premise(c: dict) -> str:
    return f"[{c['citation']}] ({c['heading']})"


def pages(citation: str) -> set[int]:
    m = re.search(r"at \*(\d+)(?:-\*?(\d+))?", citation)
    return set(range(int(m.group(1)), int(m.group(2) or m.group(1)) + 1)) if m else set()


def contains(citation: str, chunk: str) -> bool:
    """Does this retrieved chunk hold the (derived) citation? An opinion page range overlaps, or one paragraph path is a
    prefix of the other ('280A(e)(1)' is in the chunk '280A(e)'; '183(a)-(c)' in '183(a)-(d)')."""
    head = lambda c: re.split(r"-\(", c)[0]  # noqa: E731  '183(a)-(c)' -> '183(a)'
    return bool(pages(citation) & pages(chunk)) or citation.startswith(head(chunk)) or chunk.startswith(head(citation))


def build(rows: list[dict], cache: dict) -> dict:
    from taxcite.generate import citations, section_of

    heading = headings(cache)
    answers, pairs = [], []
    for r in rows:
        runs = cache[r["question"]]
        for text in dict.fromkeys(x["text"] for x in runs):  # distinct answers, in run order
            run = next(i for i, x in enumerate(runs) if x["text"] == text)
            contexts = [{**c, "heading": heading[(c["citation"], c["text"])]} for c in runs[run]["contexts"]]
            a = {"id": f"{r['id']}#{run}", "row": r["id"], "run": run, "category": r["category"],
                 # recomputed, not read from the cache: F3 narrowed "refused" to "cites nothing", and caches made
                 # before that marked a cited answer with a caveat as refused
                 "refused": "INSUFFICIENT EVIDENCE" in text.upper() and not citations(text),
                 "text": text, "contexts": contexts, "uncited": 0, "covered": 0,
                 "question": r["question"]}
            answers.append(a)
            if a["refused"]:
                continue
            exact = {c["citation"]: i for i, c in enumerate(contexts)}
            by_section = defaultdict(list)
            for i, c in enumerate(contexts):
                by_section[section_of(c["citation"])].append(i)
            n = 0
            for para in text.splitlines():
                buffer: list[str] = []
                for s in sentences(para):
                    cites = citations(s)  # generate's parser (F3), which learned F0's nested and packed brackets
                    if not cites:
                        a["uncited"] += 1
                        buffer.append(s)
                        continue
                    cited, kinds = [], []
                    for c in cites:
                        if c in exact:
                            cited.append(exact[c]); kinds.append("exact")
                        elif same := by_section.get(section_of(c)):
                            # the chunk that holds this paragraph or page; the whole section only if none does
                            cited += [i for i in same if contains(c, contexts[i]["citation"])] or same
                            kinds.append("derived")
                        else:
                            kinds.append("unsupported")
                    # a wrong page of a retrieved opinion isn't misattribution: the claim is checked against every
                    # retrieved page of the opinions it cites, and the page itself is scored apart (`pinpoint`)
                    opinions = {section_of(contexts[i]["citation"]) for i in cited if OPINION_RE.search(contexts[i]["citation"])}
                    chunks = cited + [
                        i for i, x in enumerate(contexts)
                        if OPINION_RE.search(x["citation"]) and section_of(x["citation"]) in opinions]
                    base = {"answer": a["id"], "row": r["id"], "split": split(r["id"]), "citations": cites,
                            "kinds": kinds, "chunks": list(dict.fromkeys(chunks)), "cited": list(dict.fromkeys(cited)),
                            "sections": sorted({kind_of(c) for c in cites}),
                            # a citation to nothing retrieved fails before any model looks (ADR-15)
                            "auto_fail": "unsupported" in kinds}
                    pairs.append({"id": f"{a['id']}#{n}", "units": ["sentence"] + ([] if buffer else ["span"]),
                                  "sentence": s, "claim": claim_text(s), **base})
                    if buffer:  # the same citation, over the sentences it closes
                        span = " ".join(buffer + [s])
                        pairs.append({"id": f"{a['id']}#{n}s", "units": ["span"], "sentence": span,
                                      "claim": claim_text(span), **base})
                    a["covered"] += len(buffer)
                    buffer = []
                    n += 1
    return {"answers": answers, "pairs": pairs}


def judge(data: dict, model: str, cap: float, field: str = "chunks", out: str = "judge",
          only=lambda p: True) -> float:
    """Judge each pair against `field`'s chunks into `out`. The main pass reads every retrieved page of a cited
    opinion (`chunks`); the pinpoint pass re-reads the pairs that passed, against the cited pages alone (`cited`)."""
    from ragas_eval import VERDICT_SYSTEM, VERDICTS_SCHEMA, Budget, parse_json
    from taxcite.generate import call_model

    # found by reading 40 of its verdicts (the F0 judge check): without the question, a claim restating the client's
    # facts can't be supported; without the answer, "Therefore..." has nothing to refer to; and the old wording let a
    # claim with an unsupported qualifier pass (30 of 40 agreed with a careful read before; after, 15 of 16 sentences,
    # 16 of 22 multi-sentence spans, where it still misses extra assertions)
    system = VERDICT_SYSTEM.replace(
        "supported by the sources provided.",
        "supported by the sources it cites.\n\nYou also get the question and the whole answer the claims come from. The "
        "question's facts about the client may be taken as given (they are facts, not law); the answer only tells you "
        "what a claim refers to. Judge each claim's content against the sources it cites by number, never the others, "
        "even if another one supports it. A claim citing several sources is supported if they state it together, even "
        "if some of them say nothing relevant. Every assertion in the claim must be supported: a claim with any "
        "unsupported part, qualifier or condition is NOT supported.")
    assert system != VERDICT_SYSTEM
    budget = Budget(cap)
    by_answer = defaultdict(list)  # one call per answer and unit, so a span's verdict can't lean on its sentence's
    for p in data["pairs"]:
        if not p["auto_fail"] and out not in p and only(p):
            by_answer[(p["answer"], p["units"] == ["span"])].append(p)
    contexts = {a["id"]: a["contexts"] for a in data["answers"]}
    answers = {a["id"]: a for a in data["answers"]}

    def call(aid: str, ps: list[dict]) -> tuple[str, int, int]:
        used = sorted({i for p in ps for i in p[field]})
        num = {i: k + 1 for k, i in enumerate(used)}
        sources = "\n\n".join(f"Source {num[i]}: {premise(contexts[aid][i])}\n{contexts[aid][i]['text']}"
                              for i in used)
        claims = "\n".join(f"{k}. {p['claim']} (cites: {', '.join(f'Source {num[i]}' for i in p[field])})"
                           for k, p in enumerate(ps))
        a = answers[aid]
        return call_model(system, f"Question: {a['question']}\n\nThe answer (context only; judge the numbered claims):\n"
                                  f"{a['text']}\n\nSources:\n\n{sources}\n\nClaims:\n{claims}", model,
                          json_schema=VERDICTS_SCHEMA)

    groups = list(by_answer.items())
    # 8 at a time, in batches of 32 so the cap stops it within a batch; results are applied in this thread,
    # so the budget needs no lock
    batches = [groups[b:b + 32] for b in range(0, len(groups), 32)]
    with ThreadPoolExecutor(8) as pool:
        done = ((g, r) for batch in batches for g, r in zip(batch, list(pool.map(lambda g: call(g[0][0], g[1]), batch))))
        for n, (((aid, spans), ps), (text, tin, tout)) in enumerate(done, 1):
            seen = {v["index"]: v for v in parse_json(text, "verdicts", []) if isinstance(v, dict) and "index" in v}
            for k, p in enumerate(ps):  # silence is not support
                v = seen.get(k, {"supported": False, "why": "no verdict returned"})
                p[out], p[out + "_why"] = bool(v.get("supported")), str(v.get("why", ""))
            print(f"  [{n:>3}/{len(groups)}] {aid:<10} {'span' if spans else 'sent'} {len(ps):>2} claims  "
                  f"${budget.spent:.3f}")
            sys.stdout.flush()
            budget.charge(model, tin, tout)  # after the verdicts are kept: a capped run keeps what it paid for
    return budget.spent


# ---------------------------------------------------------------- nli: score every judged pair

def windows(text: str) -> list[str]:
    """Overlapping word windows covering the whole chunk: the last one starts at or past len - WINDOW."""
    words = text.split()
    return [" ".join(words[i:i + WINDOW]) for i in range(0, max(len(words) - WINDOW, 0) + STRIDE, STRIDE)] or [""]


def nli(data: dict, name: str, batch: int = 16, premise_mode: str = "all", unit: str | None = None) -> dict:
    """P(entailed) per pair: the best window of the best cited chunk. Looser than the judge, which reads the cited
    chunks together: a claim needing two sources at once can't be entailed by either window alone. F0 counts those.

    `premise_mode` "top" keeps only the TOP windows the reranker ranks highest for the claim: with every page of an
    opinion in play (870 of 981 premises windowed), the best of many windows finds a spurious match."""
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    torch.set_grad_enabled(False)
    hhem = name == "hhem"
    model = AutoModelForSequenceClassification.from_pretrained(MODELS[name], trust_remote_code=hhem).eval()
    tok = None if hhem else AutoTokenizer.from_pretrained(MODELS[name])
    entail = None if hhem else next(i for i, l in model.config.id2label.items()
                                    if l.lower().startswith("entail") or l == "1")  # MiniCheck: "1" = supported
    contexts = {a["id"]: a["contexts"] for a in data["answers"]}

    def score(premises: list[str], claims: list[str]) -> list[float]:
        if hhem:
            return model.predict(list(zip(premises, claims))).tolist()
        enc = tok(premises, claims, return_tensors="pt", padding=True, truncation="only_first", max_length=512)
        return model(**enc).logits.softmax(-1)[:, entail].tolist()

    todo = [p for p in data["pairs"] if "judge" in p and (unit is None or unit in p["units"])]
    jobs = []
    for p in todo:  # the heading on every window: a case name lives there
        ws = [f"{premise(c)}\n{w}" for c in (contexts[p["answer"]][i] for i in p["chunks"]) for w in windows(c["text"])]
        if premise_mode == "top" and len(ws) > TOP:
            from taxcite.retrieve import RERANK_MODEL, _scores
            ranked = sorted(zip(_scores(RERANK_MODEL, p["claim"], tuple(ws)), ws), key=lambda x: -x[0])
            ws = [w for _, w in ranked[:TOP]]
        jobs += [(p["id"], w, p["claim"]) for w in ws]
    best: dict[str, float] = {}
    start = time.time()
    for b in range(0, len(jobs), batch):
        chunk = jobs[b:b + batch]
        for (pid, _, _), s in zip(chunk, score([w for _, w, _ in chunk], [c for _, _, c in chunk])):
            best[pid] = max(best.get(pid, 0.0), s)
        if b // batch % 50 == 0:
            print(f"  {b + len(chunk)}/{len(jobs)} windows, {time.time() - start:.0f}s")
    seconds = time.time() - start
    answers = len({p["answer"] for p in todo})
    return {"model": MODELS[name], "premise": premise_mode, "scores": best, "windows": len(jobs), "seconds": seconds,
            "seconds_per_answer": seconds / answers, "answers": answers}


# ---------------------------------------------------------------- report

def f1(pairs: list[dict], supported: dict[str, bool]) -> dict:
    """On the not-supported class: what the verifier exists to catch. `supported` is the verifier's call."""
    tp = sum(not p["judge"] and not supported[p["id"]] for p in pairs)
    fp = sum(p["judge"] and not supported[p["id"]] for p in pairs)
    fn = sum(not p["judge"] and supported[p["id"]] for p in pairs)
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    return {"f1": 2 * prec * rec / (prec + rec) if prec + rec else 0.0, "precision": prec, "recall": rec,
            "false_accept": fn / (tp + fn) if tp + fn else 0.0, "n": len(pairs), "unsupported": tp + fn}


def tuned(pairs: list[dict], scores: dict[str, float]) -> float:
    """The threshold that maximises not-supported F1 on the tune half. Ties go to the lower threshold."""
    grid = sorted({round(s, 3) for s in scores.values()} | {0.5})
    return max(grid, key=lambda t: (f1(pairs, {p["id"]: scores[p["id"]] >= t for p in pairs})["f1"], -t))


UNITS = ("sentence", "span")


def triage(tune: list[dict], rep: list[dict], scores: dict[str, float], leak: float = 0.02) -> dict:
    """The small model decides only what it's sure of, the LLM the rest. Auto-accept above `hi`, auto-reject below `lo`,
    thresholds fitted on one half: accepted claims may be at most `leak` unsupported (a wrong accept shows an
    unsupported claim), rejected ones at most 10% supported (a wrong reject only hides one). Scored on the other half,
    both ways round; "coverage" is the share of claims the LLM never sees."""
    def fit(ps):
        grid = sorted({round(scores[p["id"]], 3) for p in ps})
        ok_hi = [t for t in grid if (acc := [p for p in ps if scores[p["id"]] >= t])
                 and sum(not p["judge"] for p in acc) <= leak * len(acc)]
        ok_lo = [t for t in grid if (rej := [p for p in ps if scores[p["id"]] < t])
                 and sum(p["judge"] for p in rej) <= 0.10 * len(rej)]
        return (max(ok_lo) if ok_lo else 0.0), (min(ok_hi) if ok_hi else 1.01)

    def apply(ps, lo, hi):
        acc = [p for p in ps if scores[p["id"]] >= hi]
        rej = [p for p in ps if scores[p["id"]] < lo]
        return {"coverage": (len(acc) + len(rej)) / len(ps), "accepted": len(acc), "rejected": len(rej),
                "accepted_but_unsupported": sum(not p["judge"] for p in acc),
                "rejected_but_supported": sum(p["judge"] for p in rej), "n": len(ps)}
    a, b = apply(rep, *fit(tune)), apply(tune, *fit(rep))
    return {"held_out": [a, b], "coverage": (a["coverage"] + b["coverage"]) / 2,
            "leaked": a["accepted_but_unsupported"] + b["accepted_but_unsupported"],
            "unsupported_total": sum(not p["judge"] for p in tune + rep)}


def uncited(a: dict, unit: str) -> int:
    """Sentences no pair of this unit covers: every uncited one for sentences, only trailing ones for spans."""
    return a["uncited"] - (a["covered"] if unit == "span" else 0)


def suppression(answers: list[dict], pairs: list[dict], ok: dict[str, bool], unit: str) -> dict:
    """What ADR-15 would hide over answers that weren't refusals, for one claim unit. `ok` is the verifier's call per
    pair; auto-fail pairs always fail. Hidden at three granularities: the whole answer, a section (one per sub-query
    kind), the claim itself."""
    live = [a for a in answers if not a["refused"]]
    by_answer = defaultdict(list)
    for p in pairs:
        if unit in p["units"]:
            by_answer[p["answer"]].append(p)
    fails = lambda p: p["auto_fail"] or not ok.get(p["id"], True)  # noqa: E731
    kinds = {a["id"]: {s for p in by_answer[a["id"]] for s in p["sections"]} for a in live}
    hidden = {(a["id"], s): any(fails(p) for p in by_answer[a["id"]] if s in p["sections"])
              for a in live for s in kinds[a["id"]]}
    claims = [p for ps in by_answer.values() for p in ps]
    return {"answers": len(live), "claims": len(claims),
            "whole_answer": sum(any(map(fails, by_answer[a["id"]])) for a in live) / len(live),
            "section": sum(hidden.values()) / len(hidden),
            "answer_emptied_by_sections": sum(bool(kinds[a["id"]]) and all(hidden[(a["id"], s)] for s in kinds[a["id"]])
                                              for a in live) / len(live),
            "claim": sum(map(fails, claims)) / len(claims),
            "whole_answer_if_uncited_fails": sum(any(map(fails, by_answer[a["id"]])) or uncited(a, unit) > 0
                                                 for a in live) / len(live)}


def material(live: list[dict], pairs: list[dict]) -> dict:
    """Completeness over material sentences, and the share of answers that would survive ADR-15 whole: every
    material sentence cited and every citation supported (an uncited sentence is unverified, so it can't be shown)."""
    from taxcite.generate import citations
    by_answer = defaultdict(list)
    for p in pairs:
        if "sentence" in p["units"]:
            by_answer[p["answer"]].append(p)
    total = cited = whole = 0
    for a in live:
        ss = [s for s in sentences(a["text"]) if citations(s) or not structural(s)]
        uncited = sum(not citations(s) for s in ss)
        total, cited = total + len(ss), cited + len(ss) - uncited
        whole += not uncited and all(not p["auto_fail"] and p.get("judge", False) for p in by_answer[a["id"]])
    return {"material_sentences": total, "material_cited": cited,
            "completeness_material": cited / total if total else 0.0,
            "answers_fully_verified": whole / len(live) if live else 0.0}


def report(data: dict) -> dict:
    answers, pairs = data["answers"], data["pairs"]
    live = [a for a in answers if not a["refused"]]
    contexts = {a["id"]: a["contexts"] for a in answers}
    sentence_pairs = [p for p in pairs if "sentence" in p["units"]]
    n_sent = len(sentence_pairs) + sum(a["uncited"] for a in live)
    out = {"shape": {
        "answers": len(answers), "refused": len(answers) - len(live), "sentences": n_sent,
        "cited_sentences": len(sentence_pairs), "uncited_sentences": n_sent - len(sentence_pairs),
        "uncited_covered_by_spans": sum(a["covered"] for a in live),
        "answers_citing_nothing": sum(not any(p["answer"] == a["id"] for p in pairs) for a in live),
        **material(live, pairs),
        "multi_source": sum(len(p["chunks"]) > 1 for p in sentence_pairs),
        "derived": sum("derived" in p["kinds"] for p in sentence_pairs),
        "auto_fail": sum(p["auto_fail"] for p in sentence_pairs),
        "premises": sum(len(p["chunks"]) for p in sentence_pairs),
        "premises_windowed": sum(len(windows(contexts[p["answer"]][i]["text"])) > 1
                                 for p in sentence_pairs for i in p["chunks"])}}
    nli = {f.stem.removeprefix("f0-nli-"): json.loads(f.read_text()) for f in sorted(RESULTS.glob("f0-nli-*.json"))}
    for unit in UNITS:
        judged = [p for p in pairs if unit in p["units"] and "judge" in p]
        sup = sum(p["judge"] for p in judged)
        u = out[unit] = {"judged": len(judged), "judge_supported": sup / len(judged),
                         "accept_all_f1_on_supported_class": 2 * sup / (sup + len(judged)),
                         "suppression": {"judge": suppression(answers, pairs, {p["id"]: p["judge"] for p in judged}, unit)},
                         "nli": {}}
        tune = [p for p in judged if p["split"] == "tune"]
        rep = [p for p in judged if p["split"] == "report"]
        for name, res in nli.items():
            scores = res["scores"]
            if not all(p["id"] in scores for p in judged):  # a run scored for the other unit only
                continue
            t, t2 = tuned(tune, scores), tuned(rep, scores)
            call = {p["id"]: scores[p["id"]] >= t for p in judged}
            # 48 questions a half is noisy, so the threshold is also fitted the other way round; F1 is the mean of
            # the two held-out halves, and "ceiling" fits and scores on everything (optimistic, for scale)
            held = [f1(rep, call)["f1"], f1(tune, {p["id"]: scores[p["id"]] >= t2 for p in judged})["f1"]]
            u["nli"][name] = {"threshold": t, "threshold_other_way": t2, "seconds_per_answer": res["seconds_per_answer"],
                              "held_out_f1": statistics.mean(held), "held_out_f1_each": held,
                              "report": f1(rep, call),
                              "at_0.5": f1(judged, {p["id"]: scores[p["id"]] >= 0.5 for p in judged}),
                              "ceiling": f1(judged, {p["id"]: scores[p["id"]] >= tuned(judged, scores) for p in judged})}
            u["suppression"][name] = suppression(answers, pairs, call, unit)
            u["nli"][name]["triage"] = triage(tune, rep, scores)
    moved = [p for p in pairs if "sentence" in p["units"] and "pinpoint" in p]
    out["pinpoint"] = {"supported_via_another_page_checked": len(moved),
                       "cited_page_does_not_support": sum(not p["pinpoint"] for p in moved)}
    out["vs_todays_judge"] = claim_unit(data)
    out["abstention"] = abstention()
    return out


def claim_unit(data: dict) -> dict:
    """Each F0 unit (cited chunks only) against today's faithfulness (LLM-extracted claims, all eight chunks), on
    the same answers: how many claims each makes, and whether they agree on "this answer has a failing claim"."""
    if not RAGAS or not RAGAS.exists():
        return {}
    ragas = json.loads(RAGAS.read_text())["rows"]
    per_run = len(ragas) // 5
    old = {(r["id"], i // per_run): r for i, r in enumerate(ragas)}
    out = {}
    for unit in UNITS:
        by_answer = defaultdict(list)
        for p in data["pairs"]:
            if unit in p["units"]:
                by_answer[p["answer"]].append(p)
        grid, claims, units = Counter(), [], []
        for a in data["answers"]:
            o = old.get((a["row"], a["run"]))
            if a["refused"] or not o or not o["claims"] or not by_answer[a["id"]]:
                continue
            claims.append(len(o["claims"]))
            units.append(len(by_answer[a["id"]]))
            new = any(p["auto_fail"] or not p.get("judge", True) for p in by_answer[a["id"]])
            grid[(any(not v.get("supported") for v in o["verdicts"]), new)] += 1
        out[unit] = {"answers": len(claims), "llm_claims_per_answer": statistics.mean(claims),
                     f"{unit}s_per_answer": statistics.mean(units),
                     "fail_both": grid[(True, True)], "fail_today_only": grid[(True, False)],
                     f"fail_{unit}_only": grid[(False, True)], "fail_neither": grid[(False, False)]}
    return out


def abstention() -> dict:
    """Rule 3's refusals today, over all 5 cached runs: the baseline F2's gate has to beat."""
    rows = {json.loads(l)["question"]: json.loads(l) for l in open(QUESTIONS) if l.strip()}
    cache = json.loads(ANSWERS.read_text())
    out = {"insufficient": {}, "answerable_refusals": 0, "answerable_runs": 0}
    for q, runs in cache.items():
        r = rows[q]
        if r["category"] == "insufficiency":
            out["insufficient"][r["id"]] = sum(x["refused"] for x in runs)
        else:
            out["answerable_refusals"] += sum(x["refused"] for x in runs)
            out["answerable_runs"] += len(runs)
    return out


def check_sheet(data: dict, n: int = 40, seed: int = 0) -> None:
    """~40 pairs for you to read (Checkpoint 1): half the judge called unsupported, over-sampled on purpose,
    G-S10 and G-S14 (Phase B's laundering) first. One pair per answer, so no answer dominates."""
    judged = [p for p in data["pairs"] if "judge" in p]
    rng = random.Random(seed)
    picked, answers = [], set()
    for want in (False, True):
        pool = [p for p in judged if p["judge"] is want]
        rng.shuffle(pool)
        pool.sort(key=lambda p: p["row"] not in ("G-S10", "G-S14"))
        for p in pool:
            if len([x for x in picked if x["judge"] is want]) == n // 2:
                break
            if p["answer"] not in answers:
                picked.append(p)
                answers.add(p["answer"])
    rng.shuffle(picked)  # so the order doesn't tell you the judge's verdict
    contexts = {a["id"]: a["contexts"] for a in data["answers"]}
    lines = ["# F0 judge check", "",
             "For each pair: does the **cited source** state the claim, or does it follow directly from it "
             "(arithmetic included)? Not whether it's good law, and not whether another source says it.",
             "Write `yes` or `no` after **Your verdict:** (optionally a note after it). The judge's verdict is at the "
             "end of each pair; read the source before it.", ""]
    for k, p in enumerate(picked, 1):
        lines += [f"## P{k:02d} `{p['id']}`", "", f"**Claim:** {p['claim']}", "", f"**Sentence:** {p['sentence']}", ""]
        for i in p["chunks"]:
            c = contexts[p["answer"]][i]
            lines += [f"**Source {premise(c)}**", "", "> " + c["text"][:3000].replace("\n", "\n> "), ""]
        lines += ["**Your verdict:** ", "", f"<details><summary>Judge</summary>{'supported' if p['judge'] else 'NOT supported'}: "
                  f"{p['judge_why']}</details>", "", "---", ""]
    CHECK.write_text("\n".join(lines))
    print(f"wrote {CHECK} ({len(picked)} pairs)")


def agreement(data: dict) -> dict:
    """Your verdicts (or anyone's) in the check sheet against the judge's current ones. Matched on the answer and the
    claim's text, not the pair id, so a re-run that splits an answer differently can't misalign them."""
    judged = {(p["answer"], p["claim"]): p for p in data["pairs"] if "judge" in p}
    you, missing = {}, []
    for block in CHECK.read_text().split("\n## P")[1:]:  # per pair, so a blank verdict can't borrow the next one's
        pid = re.search(r"`([^`]+)`", block).group(1)
        claim = re.search(r"\*\*Claim:\*\* (.*)", block).group(1).strip()
        v = re.search(r"\*\*Your verdict:\*\*[ \t]*(yes|no)\b", block, re.I)
        if not v:
            continue
        key = ("#".join(pid.split("#")[:2]), claim)
        if key in judged:
            you[key] = (pid, v.group(1).lower() == "yes")
        else:
            missing.append(pid)
    grid = Counter((judged[k]["judge"], v) for k, (_, v) in you.items())
    return {"read": len(you), "not_in_this_run": missing,
            "agree": (grid[(True, True)] + grid[(False, False)]) / len(you) if you else 0.0,
            "judge_yes_you_no": grid[(True, False)], "judge_no_you_yes": grid[(False, True)],
            "disagreements": [pid for k, (pid, v) in you.items() if judged[k]["judge"] != v]}


def main() -> int:
    global ANSWERS, RAGAS, PAIRS, CHECK, QUESTIONS, REPORT
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=("pairs", "nli", "report", "agreement"))
    ap.add_argument("--model", choices=MODELS, default="base")
    ap.add_argument("--judge", default="claude-haiku-4-5")
    ap.add_argument("--max-cost", type=float, default=5.0)
    ap.add_argument("--premise", choices=("all", "top"), default="all", help="nli: every window, or the reranker's top")
    ap.add_argument("--unit", choices=UNITS, help="nli: score only this unit's pairs (faster)")
    ap.add_argument("--answers", help="score another answer cache (F3's dev arms); needs --tag")
    ap.add_argument("--questions", default=QUESTIONS, help="the rows those answers are for")
    ap.add_argument("--tag", default="", help="suffix for this run's files, e.g. -f3-dev-a")
    args = ap.parse_args()
    if args.answers:
        if not args.tag:
            ap.error("--answers needs --tag, so its files can't overwrite F0's")
        # another pipeline's answers: no old-judge comparison, no check sheet
        ANSWERS, RAGAS, CHECK = Path(args.answers), None, None
    QUESTIONS = args.questions
    PAIRS, REPORT = RESULTS / f"f0-pairs{args.tag}.json", RESULTS / f"f0-report{args.tag}.json"

    if args.step == "pairs":
        sys.path.insert(0, str(Path(__file__).parent))
        from dotenv import load_dotenv
        load_dotenv()
        cache = json.loads(ANSWERS.read_text())
        rows = [r for r in (json.loads(l) for l in open(QUESTIONS) if l.strip()) if r["question"] in cache]
        data = json.loads(PAIRS.read_text()) if PAIRS.exists() else build(rows, cache)
        try:
            spent = judge(data, args.judge, args.max_cost)
            # the page, scored apart: pairs that passed on the opinion's retrieved pages, re-read on the cited ones
            spent += judge(data, args.judge, args.max_cost - spent, field="cited", out="pinpoint",
                           only=lambda p: p.get("judge") and p["cited"] != p["chunks"])
        finally:
            PAIRS.write_text(json.dumps(data, indent=1))  # a capped run keeps what it paid for
        print(f"judge spend ${spent:.3f}; wrote {PAIRS}")
    elif args.step == "nli":
        res = nli(json.loads(PAIRS.read_text()), args.model, premise_mode=args.premise, unit=args.unit)
        (RESULTS / f"f0-nli-{args.model}{'' if args.premise == 'all' else '-' + args.premise}.json").write_text(json.dumps(res))
        print(f"{args.model}: {res['windows']} windows, {res['seconds']:.0f}s, {res['seconds_per_answer']:.2f}s/answer")
    elif args.step == "report":
        data = json.loads(PAIRS.read_text())
        out = report(data)
        REPORT.write_text(json.dumps(out, indent=2))
        print(json.dumps(out, indent=2))
        if CHECK and not CHECK.exists():  # never overwrite your verdicts
            check_sheet(data)
    else:
        print(json.dumps(agreement(json.loads(PAIRS.read_text())), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
