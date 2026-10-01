"""F5: Phase F scored on golden, from one run of the shipped pipeline.

    uv run python eval/temporal.py --questions eval/golden.jsonl --rows every --samples 3 \\
        --answers-cache eval/results/temporal-answers-f5.json          # the one golden run (graded)
    uv run python eval/f5_golden.py check                               # the metrics on hand-made cases first
    uv run python eval/f5_golden.py report                              # completeness, abstention, latency (no calls)
    uv run python eval/f5_golden.py seeded                              # the verifier on seeded failures (~$0.30)
    uv run python eval/f5_golden.py audit                               # the reference judge on plan set 0 (~$1.50)
    uv run python eval/f5_golden.py ladder                              # the unverified view, for temporal.py to grade

Everything reads the same answer cache: each entry carries the answer's structured items, the verifier's verdicts and
its latency (ragas_eval.pipeline_answer). Nothing here re-synthesizes; only `seeded` and `audit` call a model.
"""

import argparse
import json
import random
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from f0_verify import f1, headings, sentences, structural  # noqa: E402
from f4_hide import base, shown  # noqa: E402

from taxcite import verify  # noqa: E402
from taxcite.generate import cited_items, citations, render, section_of  # noqa: E402

RESULTS = Path("eval/results")
CACHE = RESULTS / "temporal-answers-f5.json"
QUESTIONS = "eval/golden.jsonl"
REFERENCE = "claude-sonnet-5-5"  # stronger than the runtime verifier (Haiku); price confirmed 2026-09-30
FLAG = re.compile(r"INSUFFICIENT EVIDENCE|Not in the sources", re.I)


# ---------------------------------------------------------------- metrics (pure; `check` exercises each)

def completeness(text: str) -> tuple[int, int]:
    """(material sentences cited, material sentences) of one answer's text. A line saying what's missing claims
    nothing, so it isn't material (f0_verify.structural)."""
    ss = [s for s in sentences(text) if citations(s) or not structural(s)]
    return sum(bool(citations(s)) for s in ss), len(ss)


def refused(text: str) -> bool:
    return "INSUFFICIENT EVIDENCE" in text.upper() and not citations(text)


def abstention(row: dict, text: str) -> str:
    """One answer to an insufficiency row, as one of: "refused", "flagged" (cited context and a flagged gap: right for
    a partial row, acceptable for the rest, which golden's notes allow to state current law), or "answered" (cited,
    nothing flagged: the failure `G-I06` has shown since Phase B). A partial row (with `parts`) is "handled" only if it
    cites something and flags the rest."""
    if row.get("parts"):
        return "handled" if citations(text) and FLAG.search(text) else ("refused" if refused(text) else "not handled")
    if refused(text):
        return "refused"
    return "flagged" if FLAG.search(text) else "answered"


def seed(items: list[dict], retrieved: list[str]) -> list[dict] | None:
    """Each sentence re-cited to a retrieved source of another section or opinion: a real citation, on a claim it
    wasn't cited for. Another page of the same opinion won't do, since the verifier reads every retrieved page of a
    cited opinion (the pinpoint policy), and a first try that rotated citations within an answer caught 0 of 2 for
    exactly that reason. Uncited sources first. None if no sentence has such a source."""
    cited = {c for i in items for c in i["citations"]}
    out = []
    for item in items:
        own = {section_of(c) for c in item["citations"]}
        others = [c for c in retrieved if section_of(c) not in own]
        if others:
            out.append({**item, "citations": [next((c for c in others if c not in cited), others[0])]})
    return out or None


def latency(entries: list[dict]) -> dict:
    """p50/p95 seconds per answer, for answers that were written and for refusals, the run's first answer left out
    (it loads the retrieval models)."""
    out = {}
    for name, keep in (("answered", lambda e: not e["refused"]), ("refused", lambda e: e["refused"])):
        xs = sorted(e["seconds"] for e in entries[1:] if "seconds" in e and keep(e))
        if xs:
            out[name] = {"n": len(xs), "p50": statistics.median(xs), "p95": xs[min(len(xs) - 1, int(0.95 * len(xs)))]}
    return out


def check() -> None:
    """Brief rule 0: each metric on a hand-made right and wrong case before it's trusted."""
    good = "Deductible [26 U.S.C. § 221(a)-(c)]. Capped at $2,500 [26 U.S.C. § 221(a)-(c)]."
    assert completeness(good) == (2, 2)
    assert completeness("Tax year: 2025\n\nPart 1: x\nDeductible [A]. So she can deduct it.") == (1, 2)
    assert completeness("Deductible [A]. Not in the sources: the 2026 thresholds") == (1, 1)
    partial = {"parts": [{"part": "fed"}, {"part": "NJ"}]}
    assert abstention(partial, "Deductible [A].\n\nPart 2: NJ\nINSUFFICIENT EVIDENCE: no state law") == "handled"
    assert abstention(partial, "Deductible [A].") == "not handled"
    assert abstention({}, "INSUFFICIENT EVIDENCE: not in the corpus") == "refused"
    assert abstention({}, "Section 6621 sets the formula [26 U.S.C. § 6621(a)]. Not in the sources: the Q4 rate") == "flagged"
    assert abstention({}, "The IRS takes about 16 weeks [IRS Pub 17 (2025), p. 19].") == "answered"
    a = {"part": 1, "text": "x", "citations": ["T.C. Memo. 2020-1, at *9"]}
    b = {"part": 1, "text": "y", "citations": ["26 U.S.C. § 183(d)"]}
    got = seed([a, b], ["T.C. Memo. 2020-1, at *9", "T.C. Memo. 2020-1, at *4", "26 U.S.C. § 183(d)", "26 CFR 1.183-2(b)"])
    # a's own opinion is skipped; b (a statute) takes the first uncited source of another section: the opinion's *4
    assert got == [{**a, "citations": ["26 CFR 1.183-2(b)"]}, {**b, "citations": ["T.C. Memo. 2020-1, at *4"]}]
    assert seed([a], ["T.C. Memo. 2020-1, at *9", "T.C. Memo. 2020-1, at *4"]) is None  # same opinion only: no seed
    es = [{"seconds": 30.0, "refused": False}] + [{"seconds": s, "refused": False} for s in (5, 6, 7)] \
        + [{"seconds": 1.0, "refused": True}]
    assert latency(es) == {"answered": {"n": 3, "p50": 6, "p95": 7}, "refused": {"n": 1, "p50": 1.0, "p95": 1.0}}
    print("check: every metric behaves on its hand-made cases")


# ---------------------------------------------------------------- steps

def load() -> tuple[dict, dict]:
    rows = {json.loads(l)["question"]: json.loads(l) for l in open(QUESTIONS) if l.strip()}
    return json.loads(CACHE.read_text()), rows


def report() -> dict:
    cache, rows = load()
    entries = [e for runs in cache.values() for e in runs]
    answerable = [(rows[q], e) for q, runs in cache.items() for e in runs if rows[q]["category"] != "insufficiency"]
    out = {}
    for view in ("before hiding", "as shown"):
        cited = total = 0
        for _, e in answerable:
            text = render(e["structured"]["data"], e["structured"]["labels"])[0] if view == "before hiding" and \
                e.get("structured") else e["text"]
            c, t = completeness(text)
            cited, total = cited + c, total + t
        out[f"completeness, {view}"] = {"cited": cited, "material": total, "share": cited / total if total else 0.0}
    verdicts = [v for _, e in answerable for v in e.get("verdicts") or []]
    out["verifier"] = {"sentences": len(verdicts), "hidden": sum(not v["supported"] for v in verdicts),
                       "answers_emptied": sum(e["refused"] and bool(e.get("verdicts")) for _, e in answerable),
                       "answers_refused": sum(e["refused"] for _, e in answerable), "answers": len(answerable)}
    out["abstention"] = {}
    for q, runs in cache.items():
        if rows[q]["category"] == "insufficiency":
            out["abstention"][rows[q]["id"]] = dict(Counter(abstention(rows[q], e["text"]) for e in runs))
    out["latency_seconds"] = latency(entries)
    out["cost_usd_per_answer"] = statistics.mean(e["cost_usd"] for e in entries)
    (RESULTS / "f5-report.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return out


def checkpoint(name: str):
    """(done, save, path): results already paid for in a crashed run, and a function saving one more (your rule: every
    paid row is saved as it's done). The caller deletes the file once its final results are written."""
    path = RESULTS / f"f5-{name}.progress.json"
    done = json.loads(path.read_text()) if path.exists() else {}

    def save(key: str, value) -> None:
        done[key] = value
        path.write_text(json.dumps(done))
    return done, save, path


def judge(answer, items: list[dict], question: str, model: str) -> list[verify.Verdict]:
    """verify.verify's call, on given items and with another model; low effort, since a judge needs little thinking."""
    from taxcite.generate import call_model
    raw, _, _ = call_model(verify.SYSTEM, verify.prompt(question, answer, items), model,
                           json_schema=verify.SCHEMA, **({"effort": "low"} if model.startswith("claude-sonnet") else {}))
    given = {v["index"]: v for v in json.loads(raw)["verdicts"]}
    return [verify.Verdict(k, bool(given.get(k, {}).get("supported")), str(given.get(k, {}).get("why", "no verdict")))
            for k in range(len(items))]


def with_headings(entry: dict, heading: dict):
    """f4_hide.base, with each chunk's heading: the runtime verifier saw it, so the reference must too."""
    for c in entry["contexts"]:
        c.setdefault("heading", heading.get((c["citation"], c["text"]), ""))
    return base(entry)


def seeded(n: int = 100) -> dict:
    """Recall on seeded failures: answers whose every sentence passed, citations rotated between sentences, re-verified
    by the runtime verifier. A caught seeded sentence is one it now fails."""
    cache, rows = load()
    heading = headings(cache)
    rng = random.Random(0)
    pool = [(q, e) for q, runs in cache.items() for e in runs
            if e.get("verdicts") and all(v["supported"] for v in e["verdicts"])]
    rng.shuffle(pool)
    done, save, path = checkpoint("seeded")
    caught = total = 0
    for q, e in pool:
        if total >= n:
            break
        key = f"{rows[q]['id']}#{cache[q].index(e)}"
        if key not in done:
            answer = with_headings(e, heading)
            items = seed(cited_items(e["structured"]["data"]), [h.citation for h in answer.retrieved])
            if not items:
                continue
            save(key, [v.supported for v in judge(answer, items, q, verify.VERIFIER)])
        caught, total = caught + sum(not ok for ok in done[key]), total + len(done[key])
    out = {"seeded_sentences": total, "caught": caught, "recall": caught / total if total else 0.0}
    (RESULTS / "f5-seeded.json").write_text(json.dumps(out, indent=2))
    path.unlink(missing_ok=True)
    print(json.dumps(out))
    return out


def audit(sample: int = 0, sheet_n: int = 40) -> dict:
    """The runtime verifier's verdicts against the reference judge's, on plan set `sample`'s answers: F1 on the
    "not supported" class (f0_verify.f1), false-accept rate beside it. Writes a hand-check sheet of `sheet_n` pairs,
    disagreements first, so the reference itself is checked."""
    cache, rows = load()
    heading = headings(cache)
    done, save, path = checkpoint("audit")
    pairs = []
    for q, runs in cache.items():
        if len(runs) <= sample or not runs[sample].get("verdicts"):
            continue
        e = runs[sample]
        items = cited_items(e["structured"]["data"])
        answer = with_headings(e, heading)
        if rows[q]["id"] not in done:
            save(rows[q]["id"], [{"supported": r.supported, "why": r.why} for r in judge(answer, items, q, REFERENCE)])
        ref = [verify.Verdict(k, d["supported"], d["why"]) for k, d in enumerate(done[rows[q]["id"]])]
        for item, v, r in zip(items, e["verdicts"], ref):
            pairs.append({"id": f"{rows[q]['id']}#{sample}#{v['index']}", "question": q, "text": item["text"],
                          "citations": item["citations"], "verifier": v["supported"], "verifier_why": v["why"],
                          "judge": r.supported, "judge_why": r.why, "premises": [answer.retrieved[i].citation for i
                                                                                   in verify.premises(item, answer)]})
        print(f"  {rows[q]['id']:<7} {len(items)} sentences", flush=True)
    result = {"pairs": len(pairs), "reference": REFERENCE,
              **f1(pairs, {p["id"]: p["verifier"] for p in pairs}),
              "agreement": sum(p["verifier"] == p["judge"] for p in pairs) / len(pairs) if pairs else 0.0}
    (RESULTS / "f5-audit.json").write_text(json.dumps({"summary": result, "pairs": pairs}, indent=1))
    rng = random.Random(0)
    disagree = [p for p in pairs if p["verifier"] != p["judge"]]
    agree = [p for p in pairs if p["verifier"] == p["judge"]]
    rng.shuffle(agree)
    sheet = (disagree + agree)[:sheet_n]
    rng.shuffle(sheet)
    contexts = {(rows[q]["id"]): (q, runs[sample]) for q, runs in cache.items() if len(runs) > sample}
    lines = ["# F5 reference check", "", "Does the cited source (or another retrieved page of the same opinion) state the "
             "sentence? The question's client facts count as given. Write `yes` or `no` after **Your verdict:**.", ""]
    for k, p in enumerate(sheet, 1):
        q, e = contexts[p["id"].split("#")[0]]
        texts = {c["citation"]: c["text"] for c in e["contexts"]}
        lines += [f"## R{k:02d} `{p['id']}`", "", f"**Question:** {q}", "", f"**Sentence:** {p['text']}", ""]
        for c in p["premises"]:
            lines += [f"**Source [{c}]**", "", "> " + texts.get(c, "")[:3000].replace("\n", "\n> "), ""]
        lines += ["**Your verdict:** ", "", f"<details><summary>Verifier / reference</summary>verifier "
                  f"{'yes' if p['verifier'] else 'no'} ({p['verifier_why']}); reference {'yes' if p['judge'] else 'no'} "
                  f"({p['judge_why']})</details>", "", "---", ""]
    (RESULTS / "f5-reference-check.md").write_text("\n".join(lines))
    path.unlink(missing_ok=True)
    print(json.dumps(result))
    return result


def ladder() -> None:
    """The same answers with nothing hidden, for temporal.py to grade: the "+claim verification" rung's other side."""
    cache, _ = load()
    view = {q: [shown(e, "none") for e in runs] for q, runs in cache.items()}
    out = CACHE.with_name(CACHE.stem + "-unverified.json")
    out.write_text(json.dumps(view, indent=1))
    print(f"wrote {out}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=("check", "report", "seeded", "audit", "ladder"))
    args = ap.parse_args()
    if args.step != "check":
        from dotenv import load_dotenv
        load_dotenv()
    {"check": check, "report": report, "seeded": seeded, "audit": audit, "ladder": ladder}[args.step]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
