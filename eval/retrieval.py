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
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from taxcite import decompose as dc
from taxcite.generate import OPINION_RE, section_of
from taxcite.retrieve import RERANK_MODEL, search

MODES = ("sparse", "dense", "hybrid", "hybrid+rerank")
DEFAULT_MODES = ("sparse", "dense", "hybrid")  # rerank costs a second model load, so it is opt-in
RESULTS = Path("eval/results")

load_dotenv()  # --decompose calls an LLM; eval scripts do not go through the CLI, which loads .env


def cached_decompose(question: str, cache: dict, path: Path | None, plan_set: int = 0):
    """Decompose once per plan set and reuse it, so a comparison measures the change under test.

    gpt-4o-mini re-plans between runs even at temperature 0 with a fixed seed: the same
    configuration scored 0.457 / 0.422 / 0.434 on the golden set across three runs, with
    9-11 of 86 questions planned differently each time. That 0.035 spread is larger than
    any effect B7 measured, so a single uncached run is unreadable two ways -- an A/B where
    each arm re-plans compares planners, and one number hides the spread. The cache holds a
    list of plans per question, one per plan set, so `--repeats n` re-plans the corpus n
    times and every arm is scored against the same n plan sets. Retrieval is not cached, so
    retrieval changes still show up.
    """
    plans = cache.setdefault(question, [])
    if isinstance(plans, dict):  # the single-plan format this cache used first
        plans = cache[question] = [plans]
    while len(plans) <= plan_set:
        plan = dc.decompose(question)
        plans.append({
            "subqueries": [{"kind": s.kind, "query": s.query} for s in plan.subqueries],
            "as_of": plan.as_of, "fallback": plan.fallback, "model": plan.model,
            "input_tokens": plan.input_tokens, "output_tokens": plan.output_tokens,
        })
        if path:
            path.write_text(json.dumps(cache, indent=2))
    hit = plans[plan_set]
    return dc.Decomposition(
        question=question, subqueries=[dc.SubQuery(s["kind"], s["query"]) for s in hit["subqueries"]],
        as_of=hit["as_of"], model=hit["model"], input_tokens=hit["input_tokens"],
        output_tokens=hit["output_tokens"], fallback=hit["fallback"])


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


# Each decomposition variant takes one thing away from the shipped path, so the table
# says what routing earns, what the model's rewriting earns, and what reranking earns.
VARIANTS = {
    "route":          dict(route=True,  rewrite=False, rerank=True),   # shipped
    "route-norerank": dict(route=True,  rewrite=False, rerank=False),
    "noroute":        dict(route=False, rewrite=False, rerank=True),
    "rewrite":        dict(route=True,  rewrite=True,  rerank=True),
}


def score_one(question: dict, mode: str, k: int, reranker: str = RERANK_MODEL,
              variant: str | None = None, cache: dict | None = None,
              cache_path: Path | None = None, plan_set: int = 0) -> dict:
    started = time.perf_counter()
    plan = None
    if variant:
        how = VARIANTS[variant]
        plan = dc.retrieve(cached_decompose(question["question"], cache if cache is not None else {},
                                            cache_path, plan_set),
                           k=k, mode=mode, route=how["route"], rewrite=how["rewrite"])
        hits = (dc.chunks(plan, k, reranker) if how["rerank"]
                else dc.merge(plan.searched, k))
    else:
        hits = search(question["question"], k=k, mode=mode, rerank_name=reranker)
    elapsed_ms = (time.perf_counter() - started) * 1000
    retrieved = [h.citation for h in hits]
    gold = groups(question["gold"])
    ranks = first_hits(retrieved, gold)
    row = {
        "id": question["id"],
        "style": question["style"],
        "category": question.get("category"),
        "mode": f"{mode}+{variant}" if variant else mode,
        "plan_set": plan_set if variant else 0,
        "chunks": len(hits),
        "recall": recall_at_k(retrieved, gold),
        "ndcg": ndcg_at_k(retrieved, gold),
        "mrr": mrr(retrieved, gold),
        "section_recall": recall_at_k([h.section for h in hits], [{section_of(c) for c in g} for g in gold]),
        "ms": elapsed_ms,
        "first_hit_rank": min(ranks) + 1 if ranks else None,
        "top1": retrieved[0] if retrieved else None,
    }
    if plan is not None:
        row |= {
            "subqueries": [{"kind": s.kind, "query": s.query} for s in plan.subqueries],
            "as_of": plan.as_of,
            "fallback": plan.fallback,
            "decompose_cost_usd": plan.cost_usd,
            "has_case_subquery": any(s.kind == "case_law" for s in plan.subqueries),
        }
    return row


def needs_case_law(question: dict) -> bool:
    """A row whose gold includes an opinion: routing must send a sub-query to the case corpus."""
    return any(OPINION_RE.search(c) for group in groups(question["gold"]) for c in group)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--mode", choices=MODES, action="append", help="repeatable; default is all three")
    ap.add_argument("--pilot", default="eval/pilot.jsonl")
    ap.add_argument("--reranker", default=RERANK_MODEL, help="cross-encoder for the +rerank modes")
    ap.add_argument("--decompose", choices=tuple(VARIANTS), action="append",
                    help="also run each mode through a B7 decomposition variant; repeatable")
    ap.add_argument("--plan-cache", default="eval/results/decompositions.json",
                    help="reuse decompositions across runs and arms; '' re-plans every run")
    ap.add_argument("--fail-under", type=float, metavar="RECALL",
                    help="exit non-zero if the last mode's Recall@k is below this. For CI: with the "
                         "plan cache pinned this comparison is deterministic, so any drop is a real one")
    ap.add_argument("--repeats", type=int, default=1, metavar="N",
                    help="score the decomposition arms against N independently planned sets and "
                         "report the mean and the spread; the planner is the noise source, so a "
                         "single number overstates what one run can resolve")
    args = ap.parse_args()
    cache_path = Path(args.plan_cache) if args.plan_cache else None
    plans = json.loads(cache_path.read_text()) if cache_path and cache_path.exists() else {}
    modes = args.mode or list(DEFAULT_MODES)
    runs = [(m, None) for m in modes] + [(m, v) for v in (args.decompose or []) for m in modes]
    labels = [f"{m}+{v}" if v else m for m, v in runs]

    questions = [json.loads(line) for line in open(args.pilot) if line.strip()]
    # the golden set marks the phase a row starts being scored in; the pilot marks `scorable`
    questions = [q for q in questions if q.get("scorable", q.get("scored_from") == "B")]
    scored = [q for q in questions if q["gold"]]
    abstain = [q for q in questions if not q["gold"]]
    print(f"{len(scored)} scorable questions, {len(abstain)} abstention questions, k={args.k}\n")

    for mode, variant in runs:  # pay the model load before timing, so p50 is a query, not a cold start
        if mode.endswith("+rerank") or (variant and VARIANTS[variant]["rerank"]):
            score_one(scored[0], mode, args.k, args.reranker, variant, plans, cache_path)
            break
    # only the decomposition arms are re-planned; the rest are deterministic and run once
    rows = [score_one(q, mode, args.k, args.reranker, variant, plans, cache_path, i)
            for mode, variant in runs
            for i in range(args.repeats if variant else 1)
            for q in scored]

    def pct(mode: str, p: float) -> float:
        vals = sorted(r["ms"] for r in rows if r["mode"] == mode)
        return vals[min(int(p * len(vals)), len(vals) - 1)] if vals else 0.0

    def avg(mode: str, key: str, style: str | None = None) -> float:
        vals = [r[key] for r in rows if r["mode"] == mode and (style is None or r["style"] == style)]
        return sum(vals) / len(vals) if vals else 0.0

    def per_plan_set(mode: str, key: str = "recall") -> list[float]:
        """That mode's score under each plan set, so the spread is visible next to the mean."""
        out = []
        for i in sorted({r["plan_set"] for r in rows if r["mode"] == mode}):
            vals = [r[key] for r in rows if r["mode"] == mode and r["plan_set"] == i]
            out.append(sum(vals) / len(vals))
        return out

    width = max(len(m) for m in labels) + 2
    header = (f"{'mode':<{width}}{'Recall':>8}{'nDCG':>8}{'MRR':>8}{'SectR':>8}   {'nl':>6}{'keyword':>9}"
              f"   {'chunks':>7}{'p50 ms':>8}{'p95 ms':>8}")
    print(header)
    print("-" * len(header))
    for mode in labels:
        print(f"{mode:<{width}}{avg(mode,'recall'):>8.3f}{avg(mode,'ndcg'):>8.3f}{avg(mode,'mrr'):>8.3f}"
              f"{avg(mode,'section_recall'):>8.3f}   {avg(mode,'recall','nl'):>6.3f}{avg(mode,'recall','keyword'):>9.3f}"
              f"   {avg(mode,'chunks'):>7.1f}{pct(mode,0.5):>8.0f}{pct(mode,0.95):>8.0f}")
    spread = {m: per_plan_set(m) for m in labels if len(per_plan_set(m)) > 1}
    if spread:
        print("\nRecall@k under each plan set (the planner is not deterministic; "
              "an effect smaller than this spread is not resolved):")
        for mode, vals in spread.items():
            print(f"   {mode:<{width}}" + "  ".join(f"{v:.3f}" for v in vals)
                  + f"   mean {sum(vals)/len(vals):.3f}  range {max(vals)-min(vals):.3f}")

    categories = sorted({r["category"] for r in rows if r["category"]})
    if len(categories) > 1:
        print("\nrecall by category: " + "  ".join(f"{c} ({sum(q.get('category') == c for q in scored)})" for c in categories))
        for mode in labels:
            vals = {c: [r["recall"] for r in rows if r["mode"] == mode and r["category"] == c] for c in categories}
            print(f"{mode:<{width}}" + "".join(f"{sum(v) / len(v):>12.3f}" for v in vals.values()))

    routing = {}
    for mode in labels:
        planned = [r for r in rows if r["mode"] == mode and "subqueries" in r]
        if not planned:
            continue
        case_rows = [r for r in planned if needs_case_law(next(q for q in scored if q["id"] == r["id"]))]
        routing[mode] = {
            "rows_needing_case_law": len(case_rows),
            "case_subquery_present": sum(r["has_case_subquery"] for r in case_rows),
            "spurious_case_subquery": sum(r["has_case_subquery"] for r in planned) - sum(r["has_case_subquery"] for r in case_rows),
            "fallbacks": sum(bool(r["fallback"]) for r in planned),
            "subqueries_per_question": sum(len(r["subqueries"]) for r in planned) / len(planned),
            "cost_usd": sum(r["decompose_cost_usd"] for r in planned),
        }
        s = routing[mode]
        hit_rate = s["case_subquery_present"] / s["rows_needing_case_law"] if s["rows_needing_case_law"] else 0.0
        print(f"\n{mode}: case-law sub-query on {s['case_subquery_present']}/{s['rows_needing_case_law']} rows whose "
              f"gold needs one ({hit_rate:.3f}); {s['spurious_case_subquery']} on rows that do not; "
              f"{s['fallbacks']} fallback plans; {s['subqueries_per_question']:.2f} sub-queries/question; "
              f"${s['cost_usd']:.4f}")

    print("\nper-question recall (strict):")
    print(f"{'id':<6}" + "".join(f"{m:>{width + 2}}" for m in labels))
    for q in scored:
        cells = "".join(f"{next(r['recall'] for r in rows if r['id'] == q['id'] and r['mode'] == m):>{width + 2}.2f}"
                        for m in labels)
        print(f"{q['id']:<6}{cells}")

    RESULTS.mkdir(parents=True, exist_ok=True)
    # the question-set name is in the filename: a golden run and a pilot run on the same
    # day used to write the same file, and the second silently replaced the first
    out = RESULTS / f"retrieval-{Path(args.pilot).stem}-{date.today()}-k{args.k}.json"
    out.write_text(json.dumps({
        "k": args.k, "modes": labels, "rows": rows,
        "reranker": args.reranker,
        "repeats": args.repeats,
        "routing": routing,
        "recall_per_plan_set": {m: per_plan_set(m) for m in labels},
        "summary": {m: {key: avg(m, key) for key in ("recall", "ndcg", "mrr", "section_recall", "chunks")}
                    | {"p50_ms": pct(m, 0.5), "p95_ms": pct(m, 0.95)} for m in labels},
    }, indent=2))
    print(f"\nwrote {out}")
    if args.fail_under is not None:
        got = avg(labels[-1], "recall")
        ok = got >= args.fail_under
        print(f"\ngate: {labels[-1]} Recall@{args.k} {got:.4f} "
              f"{'>=' if ok else '<'} {args.fail_under:.4f} -> {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())