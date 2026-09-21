"""ADR-11: choose the LLM by measuring answers, not by price alone.

    uv run python eval/llm_bench.py --estimate        # cost estimate, no API calls
    uv run python eval/llm_bench.py                   # run it
    uv run python eval/llm_bench.py --limit 3         # short run while iterating

Measures four things per candidate model, in both `closed_book` and `rag` mode:

  correctness        §9.2's 3-point rubric, graded by an LLM judge
  citation fidelity  exact / derived / fabricated, per generate.parse_citations
  abstention         does it refuse when the corpus cannot answer (P19, P20)
  cost and latency   measured per call, projected to $/month at two volumes

§9.2 requires the judge to differ from the model being graded, so answers from an
Anthropic model are judged by an OpenAI one and vice versa, and a second judge
applying the same rubric in different words gives the agreement figure (Cohen's kappa).
"""

import argparse
import json
import statistics
import time
from collections import Counter
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from taxcite.generate import PRICES, answer, call_model

load_dotenv()  # eval scripts do not go through the CLI, which is where .env is normally loaded

CANDIDATES = ("gpt-4o-mini", "claude-haiku-4-5")
JUDGE_FOR = {  # a model is never graded by its own family (§9.2)
    "gpt-4o-mini": "claude-haiku-4-5",
    "claude-haiku-4-5": "gpt-4o-mini",
}
MODES = ("closed_book", "rag")
RESULTS = Path("eval/results")
DEFAULT_MAX_SPEND = 2.00
VOLUMES = (200, 900)  # persona volume (dozens/week) and §4.1's "few dozen daily"

# The reliability check needs a second judge that applies the SAME standard, worded
# differently — not a stricter one, which measures two standards instead of agreement.
# Temperature would be the cleaner knob, but current Anthropic models removed sampling
# parameters, so a neutral paraphrase keeps the method identical across providers.
JUDGE_SYSTEM = """You grade answers to US federal tax questions against a reference answer.

Reply with JSON only: {"grade": "correct" | "partial" | "incorrect", "defect": "<tag>"}

grade:
  correct   — states the same rule as the reference, with no material error
  partial   — right direction, but misses a material condition, exception or limit
  incorrect — wrong rule, wrong conclusion, or a fabricated authority

defect (use "none" when the grade is correct):
  wrong_section_cited | superseded_rule | wrong_tax_year | authority_misweighted |
  hallucinated_fact | missing_condition | none

Judge only the substance against the reference. Do not reward length or confidence."""

JUDGE_SYSTEM_ALT = """Your task is to compare a candidate answer to a reference answer about US federal tax.

Return JSON and nothing else: {"grade": "correct" | "partial" | "incorrect", "defect": "<tag>"}

Meaning of each grade:
  correct   — the candidate conveys the same rule as the reference, with no material error
  partial   — broadly right, but a material condition, exception or limit is absent
  incorrect — a different rule, a wrong conclusion, or an authority that does not exist

Defect tags (use "none" for a correct grade):
  wrong_section_cited | superseded_rule | wrong_tax_year | authority_misweighted |
  hallucinated_fact | missing_condition | none

Assess substance only, against the reference. Length and confident tone are not evidence."""


def judge(question: str, reference: str, candidate: str, model: str, alt: bool = False) -> dict:
    """Grade one answer. `alt` applies the same rubric in different words, which is the
    reliability check: a second judge given a *stricter* rubric would measure two
    different standards rather than agreement."""
    prompt = (f"Question: {question}\n\nReference answer: {reference}\n\n"
              f"Answer to grade: {candidate}\n\nReply with JSON only.")
    text, tin, tout = call_model(JUDGE_SYSTEM_ALT if alt else JUDGE_SYSTEM, prompt, model)
    try:
        start, end = text.index("{"), text.rindex("}") + 1
        parsed = json.loads(text[start:end])
        grade = str(parsed.get("grade", "unparsed")).lower()
        defect = str(parsed.get("defect", "none")).lower()
    except (ValueError, json.JSONDecodeError):
        grade, defect = "unparsed", "none"
    return {"grade": grade, "defect": defect, "in": tin, "out": tout, "model": model}


def cost_of(model: str, tin: int, tout: int) -> float:
    pin, pout = PRICES.get(model, (0.0, 0.0))
    return (tin * pin + tout * pout) / 1e6


def estimate(questions: list[dict], models: list[str]) -> float:
    """Rough spend before committing: RAG prompts dominate the input tokens."""
    per_answer = {"rag": (2200, 150), "closed_book": (80, 220)}
    total = 0.0
    for model in models:
        for mode in MODES:
            tin, tout = per_answer[mode]
            total += len(questions) * cost_of(model, tin, tout)
            total += len(questions) * 2 * cost_of(JUDGE_FOR[model], 700, 60)  # two judges
    return total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", action="append", choices=list(CANDIDATES), help="repeatable; default both")
    ap.add_argument("--limit", type=int, help="only the first N questions (for iterating)")
    ap.add_argument("--estimate", action="store_true", help="print the cost estimate and exit")
    ap.add_argument("--max-spend", type=float, default=DEFAULT_MAX_SPEND, help="stop if measured spend exceeds this")
    ap.add_argument("--pilot", default="eval/pilot.jsonl")
    args = ap.parse_args()
    models = args.model or list(CANDIDATES)

    rows = [json.loads(line) for line in open(args.pilot) if line.strip()]
    questions = [q for q in rows if q["scorable"]]
    if args.limit:
        questions = questions[:args.limit]
    graded = [q for q in questions if q["gold"]]
    abstain = [q for q in questions if not q["gold"]]

    print(f"{len(graded)} graded + {len(abstain)} abstention questions x {len(models)} models x {len(MODES)} modes")
    print(f"estimated spend: ${estimate(questions, models):.2f} (cap ${args.max_spend:.2f})\n")
    if args.estimate:
        return 0

    results, spend = [], 0.0
    for model in models:
        for mode in MODES:
            for q in questions:
                t0 = time.time()
                a = answer(q["question"], mode=mode, model=model)
                latency = time.time() - t0
                spend += a.cost_usd

                row = {
                    "model": model, "mode": mode, "id": q["id"], "category": q["category"],
                    "latency_s": latency, "cost": a.cost_usd,
                    "in": a.input_tokens, "out": a.output_tokens,
                    "refused": a.refused,
                    "citations": len(a.citations), "derived": len(a.derived_citations),
                    "invented": len(a.unsupported_citations),
                    "gold_cited": any(c in a.citations for c in q["gold"]),
                    "text": a.text,
                }
                if q["gold"]:  # graded question: two judges, per §9.2's reliability protocol
                    judge_model = JUDGE_FOR[model]
                    primary = judge(q["question"], q["answer"], a.text, judge_model)
                    second = judge(q["question"], q["answer"], a.text, judge_model, alt=True)
                    spend += cost_of(judge_model, primary["in"], primary["out"])
                    spend += cost_of(judge_model, second["in"], second["out"])
                    row |= {"grade": primary["grade"], "defect": primary["defect"],
                            "grade2": second["grade"], "judge": judge_model}
                results.append(row)
                print(f"  {model:<18} {mode:<11} {q['id']} {row.get('grade','—'):<9} "
                      f"exact={row['citations']} derived={row['derived']} invented={row['invented']} "
                      f"{latency:4.1f}s ${spend:.3f}", flush=True)

                if spend > args.max_spend:
                    print(f"\nSTOPPED: spend ${spend:.2f} exceeded the ${args.max_spend:.2f} cap")
                    return 1

    report(results, models, spend, graded, abstain)
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / f"llm_bench-{date.today()}.json"
    out.write_text(json.dumps({"spend": spend, "rows": results}, indent=2))
    print(f"\nwrote {out}")
    return 0


def report(results: list[dict], models: list[str], spend: float, graded: list, abstain: list) -> None:
    def pick(model, mode, category=None):
        return [r for r in results if r["model"] == model and r["mode"] == mode
                and (category is None or r["category"] == category)]

    print(f"\n{'model':<18}{'mode':<12}{'correct':>8}{'partial':>8}{'wrong':>7}"
          f"{'gold cited':>11}{'exact':>7}{'derived':>8}{'invented':>9}{'p50 s':>7}{'$/query':>9}")
    print("-" * 104)
    for model in models:
        for mode in MODES:
            rows = [r for r in pick(model, mode) if "grade" in r]
            if not rows:
                continue
            grades = Counter(r["grade"] for r in rows)
            n = len(rows)
            all_rows = pick(model, mode)
            print(f"{model:<18}{mode:<12}{grades['correct'] / n:>8.2f}{grades['partial'] / n:>8.2f}"
                  f"{grades['incorrect'] / n:>7.2f}"
                  f"{sum(r['gold_cited'] for r in rows) / n:>11.2f}"
                  f"{sum(r['citations'] for r in rows):>7}"
                  f"{sum(r['derived'] for r in rows):>8}"
                  f"{sum(r['invented'] for r in rows):>9}"
                  f"{statistics.median(r['latency_s'] for r in all_rows):>7.1f}"
                  f"{statistics.mean(r['cost'] for r in all_rows):>9.4f}")

    if abstain:
        print(f"\nabstention ({', '.join(q['id'] for q in abstain)}): should refuse")
        for model in models:
            for mode in MODES:
                rows = [r for r in pick(model, mode) if r["category"] == "insufficiency"]
                if rows:
                    print(f"  {model:<18}{mode:<12}refused {sum(r['refused'] for r in rows)}/{len(rows)}")

    judged = [r for r in results if "grade2" in r]
    if judged:
        agree = sum(r["grade"] == r["grade2"] for r in judged) / len(judged)
        print(f"\njudge agreement (raw): {agree:.2f} over {len(judged)} graded answers")

    print(f"\n{'model':<18}{'mode':<12}" + "".join(f"${v}/mo".rjust(12) for v in VOLUMES))
    for model in models:
        for mode in MODES:
            rows = pick(model, mode)
            if rows:
                per = statistics.mean(r["cost"] for r in rows)
                print(f"{model:<18}{mode:<12}" + "".join(f"{per * v:>12.2f}" for v in VOLUMES))
    print(f"\nmeasured spend this run: ${spend:.2f}")


if __name__ == "__main__":
    raise SystemExit(main())