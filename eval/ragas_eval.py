"""Faithfulness: is every claim in the answer supported by the chunks it was given (§9.2)?

Faithfulness is not legal correctness. An answer can be perfectly faithful and still wrong,
if the sources are wrong -- and that is the point. This is the metric that catches the one
failure the whole system exists to prevent: a fluent answer with nothing behind its citations.
Correctness is graded separately (Phase A's rubric); the two must not be collapsed.

Not RAGAS the library, but RAGAS's definition of the metric. `ragas` 0.4.3 resolves to 326
packages against this project's 65 -- the langchain stack, `datasets`, `scikit-network`,
`instructor` -- for a metric that is two model calls, and B9 has to install it in CI on every
PR touching retrieval or prompts. ADR-11 also puts the judge on the other provider, which
ragas would need a custom LLM wrapper for anyway. So: split the answer into atomic claims,
check each against the retrieved context, take the ratio.

    uv run python eval/ragas_eval.py --limit 5        # smoke run, a few cents
    uv run python eval/ragas_eval.py --repeats 3      # the gate's noise band (B8 criterion)
"""

import argparse
import json
import statistics
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))  # share the plan cache with the retrieval eval
from retrieval import cached_decompose  # noqa: E402

from taxcite import decompose as dc  # noqa: E402
from taxcite.generate import call_model, cost  # noqa: E402

load_dotenv()  # eval scripts do not go through the CLI, which is where .env is loaded

JUDGE = "claude-haiku-4-5"  # ADR-11 / §9.2: the judge comes from the other provider
GATE = 0.85                 # §7: CI fails below this
RESULTS = Path("eval/results")
ANSWERS = RESULTS / "pipeline-answers.json"

CLAIMS_SYSTEM = """You split a tax answer into the atomic factual claims it makes.

Return JSON only: {"claims": ["...", "..."]}

Rules:
- One assertion per claim, each standing on its own and each capable of being true or false.
- Drop the bracketed citations; keep the substance. "The limit is $2,500,000 [26 U.S.C. § 179(b)(1)]"
  becomes "The section 179 dollar limit is $2,500,000".
- Resolve pronouns and "it"/"that" so each claim is readable alone.
- Skip hedges, questions, restatements of the question, and advice to consult someone.
- If the answer states no factual claim at all, return {"claims": []}."""

VERDICT_SYSTEM = """You check whether each claim is supported by the sources provided.

Return JSON only: {"verdicts": [{"index": 0, "supported": true, "why": "..."}]}, one entry per
claim, in order.

"supported" means the sources state the claim or it follows directly from what they state,
including arithmetic the sources make possible. It does NOT mean the claim is good law, and it
does NOT mean you agree with it: a claim you know to be legally wrong is still supported if the
sources say it. A claim that is true in general but absent from these sources is NOT supported.
Keep "why" under 20 words."""

# Anthropic's output_config enforces the shape, so a missing key or a stray sentence of
# preamble stops being a failure mode. parse_json stays as the belt to this braces: a
# refusal or a truncated response is still not the object we asked for.
CLAIMS_SCHEMA = {
    "type": "object",
    "properties": {"claims": {"type": "array", "items": {"type": "string"}}},
    "required": ["claims"],
    "additionalProperties": False,  # the API rejects an object schema without it
}
VERDICTS_SCHEMA = {
    "type": "object",
    "properties": {"verdicts": {"type": "array", "items": {
        "type": "object",
        "properties": {"index": {"type": "integer"},
                       "supported": {"type": "boolean"},
                       "why": {"type": "string"}},
        "required": ["index", "supported"],
        "additionalProperties": False,
    }}},
    "required": ["verdicts"],
    "additionalProperties": False,
}


class CostCap(RuntimeError):
    """Raised instead of quietly spending: an eval that can call a model in a loop needs a stop."""


@dataclass
class Budget:
    cap: float
    spent: float = 0.0

    def charge(self, model: str, input_tokens: int, output_tokens: int) -> None:
        self.spent += cost(model, input_tokens, output_tokens)
        if self.spent > self.cap:
            raise CostCap(f"stopped at ${self.spent:.4f}, over the ${self.cap:.2f} cap")


@dataclass
class Judged:
    id: str
    question: str
    refused: bool
    claims: list[str] = field(default_factory=list)
    verdicts: list[dict] = field(default_factory=list)
    pipeline_cost: float = 0.0

    @property
    def faithfulness(self) -> float | None:
        """None when there is nothing to score: a refusal, or an answer making no claim."""
        if self.refused or not self.claims:
            return None
        return sum(bool(v.get("supported")) for v in self.verdicts) / len(self.claims)

    @property
    def unsupported(self) -> list[str]:
        return [self.claims[v["index"]] for v in self.verdicts
                if not v.get("supported") and v["index"] < len(self.claims)]


def parse_json(text: str, key: str, default):
    """The judge returns JSON by instruction, not by API guarantee, so parse defensively."""
    try:
        value = json.loads(text[text.index("{"):text.rindex("}") + 1])[key]
    except (ValueError, KeyError, TypeError):
        return default
    return value if isinstance(value, list) else default


def extract_claims(answer: str, model: str, budget: Budget) -> list[str]:
    text, tin, tout = call_model(CLAIMS_SYSTEM, f"Answer:\n{answer}", model,
                                 json_schema=CLAIMS_SCHEMA)
    budget.charge(model, tin, tout)
    return [c.strip() for c in parse_json(text, "claims", []) if isinstance(c, str) and c.strip()]


def judge_claims(claims: list[str], contexts: list[dict], model: str, budget: Budget) -> list[dict]:
    """One batched call per row, not one per claim (ADR-10)."""
    if not claims:
        return []
    sources = "\n\n".join(f"[{c['citation']}]\n{c['text']}" for c in contexts)
    numbered = "\n".join(f"{i}. {c}" for i, c in enumerate(claims))
    text, tin, tout = call_model(
        VERDICT_SYSTEM, f"Sources:\n\n{sources}\n\nClaims:\n{numbered}", model,
        json_schema=VERDICTS_SCHEMA)
    budget.charge(model, tin, tout)
    verdicts = [v for v in parse_json(text, "verdicts", []) if isinstance(v, dict) and "index" in v]
    seen = {v["index"]: v for v in verdicts}
    # a claim the judge skipped is unsupported: silence is not support
    return [seen.get(i, {"index": i, "supported": False, "why": "no verdict returned"})
            for i in range(len(claims))]


PROMPTS = ("shipped", "pre-e5", "labels", "labels+rule4", "labels+rule4b", "pre-f3", "f3-cite", "f3-sections",
           "f3-structured", "broken")
# B9's broken arm, rebuilt on whatever ships: the grounding rule dropped, the citation requirement kept, so every
# citation check still passes it and only faithfulness sees the failure. The gate's bands are measured against it.
GROUNDING_RULE = "1. Use ONLY the numbered sources. Do not add rules, dollar amounts or dates from memory.\n"


def set_prompt(arm: str) -> None:
    """E5's prompt arms, each built from the pre-E5 prompt: "pre-e5" is it unchanged (what "shipped" meant
    before E5 shipped (ii′)); "labels" adds each source's authority label; "labels+rule4" also widens rule 4;
    "labels+rule4b" is (ii′), which now ships, so "shipped" leaves the module as it is. F3's arms build on the
    pre-F3 prompt ((ii′), "pre-f3"): "f3-cite" rewrites rule 2 (every sentence cited, only what its source says),
    "f3-sections" also asks for a section per sub-query, "f3-structured" (arm E, which now ships) writes the answer as
    JSON items, one sentence each with its citations. Every arm but "shipped" sets both F3 switches, so an older arm
    can't run structured by accident. Use a separate --answers-cache per arm: cached answers don't know their prompt."""
    from taxcite import generate as g
    if arm == "broken":
        assert GROUNDING_RULE in g.RAG_SYSTEM, "the shipped prompt no longer has B9's grounding rule to drop"
        g.RAG_SYSTEM = g.RAG_SYSTEM.replace(GROUNDING_RULE, "")
        return
    if arm == "shipped":
        return
    g.SECTIONS, g.STRUCTURED = arm == "f3-sections", arm == "f3-structured"
    if arm == "f3-structured":
        g.RAG_SYSTEM = g.PRE_F3_SYSTEM.replace(g.RULE_2, g.RULE_2_STRUCTURED).replace(g.RULE_3, g.RULE_3_STRUCTURED)
        return
    if arm == "pre-f3":
        g.RAG_SYSTEM = g.PRE_F3_SYSTEM
        return
    if arm.startswith("f3-"):
        g.RAG_SYSTEM = g.PRE_F3_SYSTEM.replace(g.RULE_2, g.RULE_2_EVERY)
        return
    rule = {"labels+rule4": g.RULE_4_AUTHORITY, "labels+rule4b": g.RULE_4_AUTHORITY_B}.get(arm, g.RULE_4)
    g.SOURCE_LABELS = arm != "pre-e5"
    g.RAG_SYSTEM = g.PRE_E5_SYSTEM.replace(g.RULE_4, rule)


def set_verify(off: bool, unit: str | None, no_gate: bool = False) -> None:
    """F4's and F2's switches for an eval run: the verifier off (the unverified arm), its hiding unit, the gate off."""
    from taxcite import decompose as dc
    dc.VERIFY = not off
    dc.GATE = not no_gate
    if unit:
        from taxcite import verify
        verify.HIDE = unit


def pipeline_answer(question: str, k: int, cache: dict, path: Path | None, run: int,
                    plans: dict | None = None, plan_path: Path | None = None, plan_set: int = 0,
                    model: str | None = None) -> dict:
    """Run the full pipeline once per run index and reuse it, so re-judging is free.

    The plan is pinned from the shared cache (plan set 0), not made fresh each time. Without
    that the planner re-routes 16% of golden questions between runs and the faithfulness score
    moves by sd 0.030 -- wide enough to swallow the 0.05 a broken prompt costs, which would
    leave the gate unable to tell a regression from a Tuesday (log #49).

    `plan_set` pins another cached plan set instead (E5: one answer per plan set is the variance that
    reaches synthesis, which runs at temperature 0). Each cached answer records its plan set, and a cache
    built with another one is refused rather than silently reused.

    `model` changes synthesis only when the plan is pinned (F3's Haiku arm); unpinned, it would plan too.
    """
    runs = cache.setdefault(question, [])
    if run < len(runs) and runs[run].get("plan_set", 0) != plan_set:
        raise ValueError(f"answer {run} of {question[:40]!r} is cached from plan set {runs[run].get('plan_set', 0)}, "
                         f"not {plan_set}: use another --answers-cache")
    while len(runs) <= run:
        pinned = cached_decompose(question, plans, plan_path, plan_set if len(runs) == run else 0) if plans is not None else None
        started = time.monotonic()
        plan, answer = dc.answer(question, k=k, plan=pinned, **({"model": model} if model else {}))
        seconds = time.monotonic() - started  # F5: retrieval, synthesis and verification, the user's wait
        from taxcite.verify import UNVERIFIED
        if answer.text == UNVERIFIED:  # F5: the verifier didn't run (a run died on exhausted credit); never cache that
            raise RuntimeError(f"verification failed, not caching it as an answer: {answer.hidden[0]['why'] if answer.hidden else ''}")
        runs.append({
            "text": answer.text,
            "refused": answer.refused,
            "citations": answer.citations,
            "unsupported_citations": answer.unsupported_citations,
            "contexts": [{"citation": h.citation, "text": h.text} for h in answer.retrieved],
            "cost_usd": answer.cost_usd + plan.cost_usd,
            "model": answer.model,
            "plan_set": plan_set if len(runs) == run else 0,
            "dropped_sentences": answer.dropped_sentences,  # F3 arm E: written without a citation, not shown
            # F4: what the verifier saw and said, so eval/f4_hide.py can show the same answer under either unit
            "structured": answer.structured, "verdicts": answer.verdicts, "hidden": answer.hidden,
            "sufficiency": answer.sufficiency,  # F2: the gate's verdict per part
            "seconds": round(seconds, 2),
        })
        if path:
            path.write_text(json.dumps(cache, indent=2))
    return runs[run]


def aggregate(judged: list[Judged]) -> dict:
    """Refusals are excluded from the mean and reported separately (§9.2).

    Averaging a refusal as 0 would punish the system for the behaviour we want, and averaging
    it as 1 would let it score a perfect gate by refusing everything. It is a different metric.
    """
    scored = [j for j in judged if j.faithfulness is not None]
    refused = [j for j in judged if j.refused]
    silent = [j for j in judged if not j.refused and not j.claims]
    values = [j.faithfulness for j in scored]
    return {
        "rows": len(judged),
        "scored": len(scored),
        "faithfulness": sum(values) / len(values) if values else 0.0,
        "perfect_rows": sum(v == 1.0 for v in values),
        "refusals": len(refused),
        "refusal_rate": len(refused) / len(judged) if judged else 0.0,
        "answers_with_no_claim": len(silent),
        "claims": sum(len(j.claims) for j in scored),
        "unsupported_claims": sum(len(j.unsupported) for j in scored),
    }


def refusals_ok(rates: list[float], limit: float | None) -> bool:
    """Refusals sit outside the faithfulness mean (see `aggregate`), so a build that refuses more can pass
    it: D7's first build passed at 0.866 while refusing 55% of golden rows (log #72). This bounds them."""
    return limit is None or (statistics.mean(rates) if rates else 0.0) <= limit


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", default="eval/golden.jsonl")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--judge", default=JUDGE)
    ap.add_argument("--limit", type=int, help="first N rows only, for a smoke run")
    ap.add_argument("--repeats", type=int, default=1, metavar="N",
                    help="run the pipeline and the judge N times; the gate needs its noise band")
    ap.add_argument("--max-cost", type=float, default=5.0, help="stop once the run has spent this much")
    ap.add_argument("--fail-under", type=float, metavar="MEAN",
                    help="exit non-zero if the mean faithfulness is below this. Set it from a measured "
                         "band, not from the quality target: the two are different objects (ADR-22)")
    ap.add_argument("--max-refusal-rate", type=float, metavar="RATE",
                    help="exit non-zero if the mean refusal rate is above this; the faithfulness mean excludes refusals")
    ap.add_argument("--answers-cache", default=str(ANSWERS), help="'' regenerates every run")
    ap.add_argument("--prompt", choices=PROMPTS, default="shipped", help="E5's and F3's synthesis prompt arms")
    ap.add_argument("--synth-model", help="synthesis model for this run (F3's arm D); plans stay pinned")
    ap.add_argument("--no-verify", action="store_true", help="skip F4's verifier: the unverified pipeline")
    ap.add_argument("--hide", choices=("part", "sentence"), help="F4's hiding unit for this run")
    ap.add_argument("--question-as-source", action="store_true",
                    help="judge claims against the question too, as temporal.py's grounding check does (F3 measurement)")
    ap.add_argument("--plan-cache", default="eval/results/decompositions.json",
                    help="pin decompositions from this cache; '' re-plans every run (noisy)")
    ap.add_argument("--pin-answers", action="store_true",
                    help="judge the SAME answers on every repeat, isolating the judge's own variation "
                         "from the pipeline's (the gate needs to know which half to pin)")
    args = ap.parse_args()

    set_prompt(args.prompt)
    set_verify(args.no_verify, args.hide)
    rows = [json.loads(line) for line in open(args.questions) if line.strip()]
    rows = [r for r in rows if r.get("scored_from") == "B"]
    if args.limit:
        rows = rows[:args.limit]
    cache_path = Path(args.answers_cache) if args.answers_cache else None
    cache = json.loads(cache_path.read_text()) if cache_path and cache_path.exists() else {}
    plan_path = Path(args.plan_cache) if args.plan_cache else None
    plans = json.loads(plan_path.read_text()) if plan_path and plan_path.exists() else ({} if plan_path else None)
    budget = Budget(args.max_cost)
    RESULTS.mkdir(parents=True, exist_ok=True)

    print(f"{len(rows)} rows x {args.repeats} run(s), judge {args.judge}, cap ${args.max_cost:.2f}\n")
    # every judged row is saved as it's done and a crashed run resumes from it (your rule, F5); deleted once the
    # run's results are written, so a deliberate re-run measures afresh
    stem = Path(args.answers_cache).stem if args.answers_cache else ANSWERS.stem
    progress = RESULTS / (f"ragas-{Path(args.questions).stem}-{stem}{'-q' if args.question_as_source else ''}"
                          f"-{args.judge}.progress.json")
    done = {(d["run"], d["id"]): d for d in json.loads(progress.read_text())} if progress.exists() else {}
    runs, stopped = [], None
    for run in range(args.repeats):
        judged = []
        try:
            for i, r in enumerate(rows, 1):
                if (run, r["id"]) in done:
                    d = done[(run, r["id"])]
                    judged.append(Judged(id=d["id"], question=r["question"], refused=d["refused"], claims=d["claims"],
                                         verdicts=d["verdicts"], pipeline_cost=d["pipeline_cost"]))
                    continue
                out = pipeline_answer(r["question"], args.k, cache, cache_path,
                                      0 if args.pin_answers else run, plans, plan_path, model=args.synth_model)
                j = Judged(id=r["id"], question=r["question"], refused=out["refused"],
                           pipeline_cost=out["cost_usd"])
                if not out["refused"]:
                    j.claims = extract_claims(out["text"], args.judge, budget)
                    # F3: the question as a source too, so restating the client's facts isn't counted unsupported
                    given = [{"citation": "the question", "text": r["question"]}] if args.question_as_source else []
                    j.verdicts = judge_claims(j.claims, given + out["contexts"], args.judge, budget)
                judged.append(j)
                done[(run, j.id)] = {"run": run, "id": j.id, "refused": j.refused, "claims": j.claims,
                                     "verdicts": j.verdicts, "pipeline_cost": j.pipeline_cost}
                progress.write_text(json.dumps(list(done.values())))
                mark = "refused" if j.refused else f"{j.faithfulness:.2f}" if j.faithfulness is not None else "no claims"
                print(f"  run {run + 1} [{i:>3}/{len(rows)}] {j.id:<7} {mark:>9}  judge ${budget.spent:.3f}")
                sys.stdout.flush()
        except CostCap as e:
            stopped = str(e)
            print(f"\n!! {e}\n")
        runs.append((judged, aggregate(judged)))
        s = runs[-1][1]
        print(f"  -> run {run + 1}: faithfulness {s['faithfulness']:.3f} over {s['scored']} rows, "
              f"refusal rate {s['refusal_rate']:.3f}\n")
        if stopped:
            break

    values = [s["faithfulness"] for _, s in runs]
    print(f"{'faithfulness':<16}" + "  ".join(f"{v:.3f}" for v in values)
          + (f"   mean {statistics.mean(values):.3f}" if len(values) > 1 else "")
          + (f"  sd {statistics.stdev(values):.3f}" if len(values) > 2 else ""))
    print(f"{'gate ' + str(GATE):<16}" + ("PASS" if statistics.mean(values) >= GATE else "FAIL")
          + "   (§7: CI fails below 0.85)")
    print(f"judge spend ${budget.spent:.4f}; pipeline spend "
          f"${sum(j.pipeline_cost for judged, _ in runs for j in judged):.4f}")

    worst = sorted((j for judged, _ in runs for j in judged if j.faithfulness is not None),
                   key=lambda j: j.faithfulness)[:5]
    if worst:
        print("\nlowest-scoring rows (read these before trusting the number):")
        for j in worst:
            print(f"  {j.id} {j.faithfulness:.2f}")
            for claim, v in zip(j.claims, j.verdicts):
                if not v.get("supported"):
                    print(f"      unsupported: {claim[:96]}")
                    print(f"                   why: {str(v.get('why'))[:90]}")

    # named by question set and answer cache, like the temporal scorer: same-day arms used to overwrite each other
    stem = Path(args.answers_cache).stem if args.answers_cache else ANSWERS.stem
    tag = "" if stem == ANSWERS.stem else f"-{stem}"
    out = RESULTS / f"ragas-{Path(args.questions).stem}-{date.today()}{tag}.json"
    out.write_text(json.dumps({
        "judge": args.judge, "k": args.k, "repeats": args.repeats, "gate": GATE,
        "questions": args.questions, "stopped": stopped,
        "summary_per_run": [s for _, s in runs],
        "faithfulness_per_run": values,
        "judge_cost_usd": budget.spent,
        "rows": [{"id": j.id, "refused": j.refused, "faithfulness": j.faithfulness,
                  "claims": j.claims, "verdicts": j.verdicts} for judged, _ in runs for j in judged],
    }, indent=2))
    print(f"\nwrote {out}")
    progress.unlink(missing_ok=True)  # the results are written; the checkpoint has done its job
    ok = True
    if args.fail_under is not None:
        mean = statistics.mean(values) if values else 0.0
        ok = mean >= args.fail_under
        print(f"gate: mean faithfulness {mean:.4f} {'>=' if ok else '<'} {args.fail_under:.4f} "
              f"-> {'PASS' if ok else 'FAIL'}")
    if args.max_refusal_rate is not None:
        rates = [s["refusal_rate"] for _, s in runs]
        refusing = refusals_ok(rates, args.max_refusal_rate)
        print(f"gate: mean refusal rate {statistics.mean(rates):.4f} {'<=' if refusing else '>'} "
              f"{args.max_refusal_rate:.4f} -> {'PASS' if refusing else 'FAIL'}")
        ok = ok and refusing
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())