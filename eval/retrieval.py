"""Score retrieval against the pilot set: the first rungs of the §9 ablation ladder.

    uv run python eval/retrieval.py                  # all modes, k=10
    uv run python eval/retrieval.py --k 20 --mode dense

Every metric is reported twice: strict (the exact cited paragraph was retrieved)
and section-level (any paragraph of the right section). The gap between them is
the headroom reranking has to work with.

Gold is a list of groups of interchangeable citations; a group is satisfied when any
member is retrieved (log #36). A bare string is a group of one, so the pilot's flat
lists score exactly as before.

    uv run python eval/retrieval.py --pilot eval/golden.jsonl
"""

import argparse
import json
import math
from datetime import date
from pathlib import Path

from taxcite.generate import section_of
from taxcite.retrieve import search

MODES = ("sparse", "dense", "hybrid")
RESULTS = Path("eval/results")


Gold = list[set[str]]  # groups of interchangeable citations


def groups(gold: list) -> Gold:
    """["a", ["b", "c"]] -> [{"a"}, {"b", "c"}]; also accepts a plain set of citations."""
    return [{g} if isinstance(g, str) else set(g) for g in gold]


def first_hits(retrieved: list[str], gold: Gold) -> list[int]:
    """0-based rank at which each group is first satisfied, for the groups that are."""
    ranks = []
    for group in gold:
        rank = next((i for i, c in enumerate(retrieved) if c in group), None)
        if rank is not None:
            ranks.append(rank)
    return ranks


def recall_at_k(retrieved: list[str], gold) -> float:
    gold = groups(gold)
    return len(first_hits(retrieved, gold)) / len(gold) if gold else 0.0


def ndcg_at_k(retrieved: list[str], gold) -> float:
    gold = groups(gold)
    dcg = sum(1 / math.log2(r + 2) for r in first_hits(retrieved, gold))
    ideal = sum(1 / math.log2(i + 2) for i in range(min(len(gold), len(retrieved))))
    return dcg / ideal if ideal else 0.0


def mrr(retrieved: list[str], gold) -> float:
    ranks = first_hits(retrieved, groups(gold))
    return 1 / (min(ranks) + 1) if ranks else 0.0


def score_one(question: dict, mode: str, k: int) -> dict:
    hits = search(question["question"], k=k, mode=mode)
    retrieved = [h.citation for h in hits]
    gold = groups(question["gold"])
    ranks = first_hits(retrieved, gold)
    return {
        "id": question["id"],
        "style": question["style"],
        "category": question.get("category"),
        "mode": mode,
        "recall": recall_at_k(retrieved, gold),
        "ndcg": ndcg_at_k(retrieved, gold),
        "mrr": mrr(retrieved, gold),
        "section_recall": recall_at_k([h.section for h in hits], [{section_of(c) for c in g} for g in gold]),
        "first_hit_rank": min(ranks) + 1 if ranks else None,
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
    # the golden set marks the phase a row starts being scored in; the pilot marks `scorable`
    questions = [q for q in questions if q.get("scorable", q.get("scored_from") == "B")]
    scored = [q for q in questions if q["gold"]]
    abstain = [q for q in questions if not q["gold"]]
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

    categories = sorted({r["category"] for r in rows if r["category"]})
    if len(categories) > 1:
        print("\nrecall by category: " + "  ".join(f"{c} ({sum(q.get('category') == c for q in scored)})" for c in categories))
        for mode in modes:
            vals = {c: [r["recall"] for r in rows if r["mode"] == mode and r["category"] == c] for c in categories}
            print(f"{mode:<8}" + "".join(f"{sum(v) / len(v):>12.3f}" for v in vals.values()))

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