"""Temporal accuracy (Phase D gate, §9.3): is the answer right for the year the question is about?

    uv run python eval/temporal.py --questions eval/dev.jsonl --repeats 3   # calibrate on dev
    uv run python eval/temporal.py                                          # golden, once, at the end

A row passes when both halves hold:
  as-of   the plan's year is the row's tax year (no judge; D0 found "as-of" means two things,
          and the rule is the tax year whose rules apply, never the date of a later event)
  answer  §9.2's judge grades the answer "correct" against the reference answer

Two-year rows ("2016 and 2026") can't be expressed by a one-year plan, so they pass on the
answer alone. A second judge applies the same rubric in other words (llm_bench's alt
phrasing, log #31), and the score is flagged untrusted below kappa 0.7 (§9.2).
Answers are cached and plans pinned, so repeats re-judge the same answers: the spread
reported is the judge's, not the pipeline's.

The reference-answer judge never sees the sources, so an answer can be right from the model's
memory (D0's G-T06; D1's D35 cites a page that doesn't state its number). Each answer is also
checked claim by claim against its retrieved sources with the faithfulness gate's judge, and
"grounded" accuracy is reported beside the gate figure. It is a diagnostic, not the pass rule.
"""

import argparse
import json
import statistics
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from llm_bench import judge  # noqa: E402
from ragas_eval import JUDGE, RESULTS, Budget, CostCap, extract_claims, judge_claims, pipeline_answer  # noqa: E402
from retrieval import cached_decompose  # noqa: E402

load_dotenv()

ANSWERS = RESULTS / "temporal-answers.json"
KAPPA_MIN = 0.7  # §9.2


def as_of_match(plan: str | None, gold: str | None) -> bool | None:
    """Year-level match of the plan's as-of against the row's tax year. None = not scored."""
    if gold and " and " in gold:
        return None
    year = lambda s: str(s)[:4] if s else None  # noqa: E731
    return year(plan) == year(gold)


def passed(as_of_ok: bool | None, grade: str) -> bool:
    return as_of_ok is not False and grade == "correct"


def kappa(a: list[str], b: list[str]) -> float:
    """Cohen's kappa for two raters over the same items."""
    n = len(a)
    observed = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    expected = sum(ca[k] * cb[k] for k in ca) / (n * n)
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", default="eval/golden.jsonl")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--judge", default=JUDGE)
    ap.add_argument("--repeats", type=int, default=1, help="judge repeats over the same answers")
    ap.add_argument("--max-cost", type=float, default=2.0)
    ap.add_argument("--answers-cache", default=str(ANSWERS))
    ap.add_argument("--plan-cache", default="eval/results/decompositions.json")
    ap.add_argument("--editions", help="turn D3's edition filter on for this run, e.g. 1,0 (off live until D7 decides)")
    args = ap.parse_args()
    if args.editions:
        from taxcite import decompose as dc
        dc.EDITIONS = tuple(int(x) for x in args.editions.split(","))

    rows = [json.loads(l) for l in open(args.questions) if l.strip()]
    rows = [r for r in rows if r["category"] == "temporal"]
    cache_path, plan_path = Path(args.answers_cache), Path(args.plan_cache)
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    plans = json.loads(plan_path.read_text()) if plan_path.exists() else {}
    budget = Budget(args.max_cost)

    out, stopped = [], None
    try:
        for r in rows:
            plan = cached_decompose(r["question"], plans, plan_path, 0)
            ans = pipeline_answer(r["question"], args.k, cache, cache_path, 0, plans, plan_path)
            ok = as_of_match(plan.as_of, r["as_of"])
            claims = [] if ans["refused"] else extract_claims(ans["text"], args.judge, budget)
            # the question is a source too: restating its facts, or arithmetic on them, is not a memory claim
            given = [{"citation": "the question", "text": r["question"]}]
            verdicts = judge_claims(claims, given + ans["contexts"], args.judge, budget)
            grounded = all(v.get("supported") for v in verdicts)  # a refusal makes no claim
            grades = []
            for _ in range(args.repeats):
                g1 = judge(r["question"], r["answer"], ans["text"], args.judge)
                g2 = judge(r["question"], r["answer"], ans["text"], args.judge, alt=True)
                for g in (g1, g2):
                    budget.charge(args.judge, g["in"], g["out"])
                grades.append({"grade": g1["grade"], "defect": g1["defect"],
                               "alt_grade": g2["grade"], "alt_defect": g2["defect"]})
            out.append({"id": r["id"], "as_of_gold": r["as_of"], "as_of_plan": plan.as_of,
                        "as_of_ok": ok, "refused": ans["refused"], "grounded": grounded,
                        "unsupported": [claims[v["index"]] for v in verdicts if not v.get("supported")],
                        "grades": grades,
                        "passes": [passed(ok, g["grade"]) for g in grades]})
            marks = " ".join(g["grade"][:4] + "/" + g["alt_grade"][:4] for g in grades)
            print(f"  {r['id']:<6} as-of {str(r['as_of']):<14} plan {str(plan.as_of):<6} "
                  f"{'-' if ok is None else 'ok' if ok else 'XX'}  {'  ' if grounded else 'UG'}  {marks}  "
                  f"${budget.spent:.3f}", flush=True)
    except CostCap as e:
        stopped = str(e)
        print(f"\n!! {e}")

    if not out:
        return 1
    per_repeat = [sum(o["passes"][i] for o in out) / len(out) for i in range(len(out[0]["passes"]))]
    grounded = [sum(o["passes"][i] and o["grounded"] for o in out) / len(out) for i in range(len(per_repeat))]
    k = kappa([g["grade"] for o in out for g in o["grades"]],
              [g["alt_grade"] for o in out for g in o["grades"]])
    scored = [o for o in out if o["as_of_ok"] is not None]
    as_of_acc = sum(o["as_of_ok"] for o in scored) / len(scored) if scored else 0.0
    print(f"\ntemporal accuracy {' '.join(f'{v:.3f}' for v in per_repeat)}"
          + (f"  mean {statistics.mean(per_repeat):.3f}" if len(per_repeat) > 1 else "")
          + (f"  sd {statistics.stdev(per_repeat):.3f}" if len(per_repeat) > 1 else "")
          + f"  ({len(out)} rows)")
    print(f"  grounded only   {' '.join(f'{v:.3f}' for v in grounded)}  (passes whose every claim is in the sources)")
    print(f"as-of extraction  {as_of_acc:.3f} ({sum(o['as_of_ok'] for o in scored)}/{len(scored)} scored rows)")
    print(f"judge agreement   kappa {k:.3f}" + ("" if k >= KAPPA_MIN else f"  UNTRUSTED (< {KAPPA_MIN})"))
    print(f"judge spend ${budget.spent:.4f}")

    # a non-default answer cache is a different arm: name the file for it, so one run can't overwrite another's
    tag = Path(args.answers_cache).stem.removeprefix(ANSWERS.stem)
    path = RESULTS / f"temporal-{Path(args.questions).stem}-{date.today()}{tag}.json"
    path.write_text(json.dumps({
        "questions": args.questions, "judge": args.judge, "repeats": args.repeats, "k": args.k,
        "accuracy_per_repeat": per_repeat, "grounded_accuracy_per_repeat": grounded, "as_of_accuracy": as_of_acc, "kappa": k,
        "judge_cost_usd": budget.spent, "stopped": stopped, "rows": out}, indent=2))
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
