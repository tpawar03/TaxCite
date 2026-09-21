"""Score retrieval against the pilot set: the first rungs of the §9 ablation ladder.

    uv run python eval/retrieval.py                  # all modes, k=10
    uv run python eval/retrieval.py --k 20 --mode dense

Every metric is reported twice: strict (the exact cited paragraph was retrieved)
and section-level (any paragraph of the right section). The gap between them is
the headroom reranking has to work with.
"""

import argparse
import json
import math
from datetime import date
from pathlib import Path

from taxcite.retrieve import search

MODES = ("sparse", "dense", "hybrid")
RESULTS = Path("eval/results")


def section_of(citation: str) -> str:
    """'26 CFR 1.263(a)-3(k)(1)' -> '1.263(a)-3'; '26 CFR 1.183-2(b)(3)' -> '1.183-2'."""
    body = citation.removeprefix("26 CFR ")
    head, dash, tail = body.partition("-")
    return f"{head}-{tail.split('(')[0]}" if dash else head


def recall_at_k(retrieved: list[str], gold: set[str]) -> float:
    return len(set(retrieved) & gold) / len(gold) if gold else 0.0


def ndcg_at_k(retrieved: list[str], gold: set[str]) -> float:
    dcg = sum(1 / math.log2(i + 2) for i, c in enumerate(retrieved) if c in gold)
    ideal = sum(1 / math.log2(i + 2) for i in range(min(len(gold), len(retrieved))))
    return dcg / ideal if ideal else 0.0


def mrr(retrieved: list[str], gold: set[str]) -> float:
    return next((1 / i for i, c in enumerate(retrieved, 1) if c in gold), 0.0)


def score_one(question: dict, mode: str, k: int) -> dict:
    hits = search(question["question"], k=k, mode=mode)
    retrieved = [h.citation for h in hits]
    gold = set(question["gold"])
    gold_sections = {section_of(c) for c in gold}
    return {
        "id": question["id"],
        "style": question["style"],
        "mode": mode,
        "recall": recall_at_k(retrieved, gold),
        "ndcg": ndcg_at_k(retrieved, gold),
        "mrr": mrr(retrieved, gold),
        "section_recall": len({h.section for h in hits} & gold_sections) / len(gold_sections),
        "first_hit_rank": next((i for i, c in enumerate(retrieved, 1) if c in gold), None),
        "top1": retrieved[0] if retrieved else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--mode", choices=MODES, action="append", help="repeatable; default is all three")
    ap.add_argument("--pilot", default="eval/pilot.jsonl")
    args = ap.parse_args()
    modes = args.mode or list(MODES)

    questions = [json.loads(line) for line in open(args.pilot) if line.strip()]
    scored = [q for q in questions if q["scorable"] and q["gold"]]
    abstain = [q for q in questions if q["scorable"] and not q["gold"]]
    print(f"{len(scored)} scorable questions, {len(abstain)} abstention questions, k={args.k}\n")

    rows = [score_one(q, mode, args.k) for mode in modes for q in scored]

    def avg(mode: str, key: str, style: str | None = None) -> float:
        vals = [r[key] for r in rows if r["mode"] == mode and (style is None or r["style"] == style)]
        return sum(vals) / len(vals) if vals else 0.0

    header = f"{'mode':<8}{'Recall':>8}{'nDCG':>8}{'MRR':>8}{'SectR':>8}   {'nl':>6}{'keyword':>9}"
    print(header)
    print("-" * len(header))
    for mode in modes:
        print(f"{mode:<8}{avg(mode,'recall'):>8.3f}{avg(mode,'ndcg'):>8.3f}{avg(mode,'mrr'):>8.3f}"
              f"{avg(mode,'section_recall'):>8.3f}   {avg(mode,'recall','nl'):>6.3f}{avg(mode,'recall','keyword'):>9.3f}")

    print("\nper-question recall (strict):")
    print(f"{'id':<6}" + "".join(f"{m:>9}" for m in modes))
    for q in scored:
        cells = "".join(f"{next(r['recall'] for r in rows if r['id'] == q['id'] and r['mode'] == m):>9.2f}" for m in modes)
        print(f"{q['id']:<6}{cells}")

    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / f"retrieval-{date.today()}-k{args.k}.json"
    out.write_text(json.dumps({
        "k": args.k, "modes": modes, "rows": rows,
        "summary": {m: {key: avg(m, key) for key in ("recall", "ndcg", "mrr", "section_recall")} for m in modes},
    }, indent=2))
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())