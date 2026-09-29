"""E0: where does authority cost retrieval, and which authority fields vary in this corpus?

    uv run python eval/e0_authority.py              # 5 plan sets, ~30 min (reranking is the cost)
    uv run python eval/e0_authority.py --plan-sets 1

A diagnosis on golden, as D0 was: nothing here is tuned, and no product code changes. The shipped
path (`route+statute1`) with the live D7 planner's cached plans, read at k=8 (what synthesis sees)
and k=20 (what the ladder scores). Writes eval/results/phase-e-e0-authority.json and a file of
inversions to read by hand (phase-e-e0-reads.txt).

Authority here is a throwaway classifier on the citation's form, for this spike only; E2 builds
the real one. Levels: statute = regulation (4) > reported T.C. (3) > T.C. Memo. (2) > publication (1).
"""

import argparse
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # retrieval.py, as the other eval scripts import it

from retrieval import VARIANTS, cached_decompose, first_hits, groups  # noqa: E402

from taxcite import decompose as dc, store  # noqa: E402
from taxcite.generate import section_of  # noqa: E402
from taxcite.ingest.citations import flags  # noqa: E402

RESULTS = Path("eval/results")
LEVEL = {"statute": 4, "regulation": 4, "temp_regulation": 4, "tc": 3, "memo": 2, "pub": 1, "unknown": 0}


def kind(citation: str) -> str:
    c = citation.split("#")[0]
    if c.startswith("26 U.S.C."):
        return "statute"
    if "IRS Pub" in c:
        return "pub"
    if "T.C. Memo." in c:
        return "memo"
    if "T.C. No." in c:
        return "tc"
    if c.startswith("26 CFR"):
        return "temp_regulation" if section_of(c).endswith("T") else "regulation"
    return "unknown"


def level(citation: str) -> int:
    return LEVEL[kind(citation)]


def row_facts(q: dict, top: list[str], pool: list[str]) -> dict:
    """One row at one depth. Per gold group: its highest authority, its rank in the top k, whether
    the reranked pool holds it at all. A group is *displaced* when it's missing from the top k,
    present in the pool, and the top k holds a non-gold hit of lower authority: the case a prior
    could fix (C0's reachability question). *Outranked*: in the top k, below such a hit."""
    gold = groups(q["gold"])
    is_gold = lambda c: any(c in g or c.split("#")[0] in g for g in gold)  # noqa: E731
    out = []
    for g in gold:
        lv = max(level(c) for c in g)
        rank = next(iter(first_hits(top, [g])), None)
        in_pool = bool(first_hits(pool, [g]))
        lower = [c for c in (top if rank is None else top[:rank]) if not is_gold(c) and level(c) < lv]
        out.append({"level": lv, "rank": None if rank is None else rank + 1, "in_pool": in_pool,
                    "displaced": rank is None and in_pool and bool(lower),
                    "outranked": rank is not None and bool(lower), "lower": lower[:3]})
    top_lv = max(x["level"] for x in out)
    return {"top1": top[0] if top else None, "top1_kind": kind(top[0]) if top else None,
            "mix": dict(Counter(kind(c) for c in top)), "groups": out,
            # top-1 is not gold and sits below the row's highest-authority gold, which the pool holds
            "inverted1": bool(top) and not is_gold(top[0]) and level(top[0]) < top_lv
                         and any(x["in_pool"] and x["level"] == top_lv for x in out)}


def run(q: dict, plans: dict, plan_set: int, k: int) -> tuple[dict, list]:
    d = dc.retrieve(cached_decompose(q["question"], plans, None, plan_set), k=k, mode="hybrid",
                    route=True, statute=VARIANTS["route+statute1"]["statute"])
    hits = dc.chunks(d, k)
    pool = [h.key or h.citation for s in d.searched for h in s.hits]
    return row_facts(q, [h.key or h.citation for h in hits], pool), hits


def mean_sd(xs: list[float]) -> str:
    return f"{statistics.mean(xs):.2f} ± {statistics.stdev(xs):.2f}" if len(xs) > 1 else f"{xs[0]:.2f}"


def inventory(conn) -> dict:
    """Part 2: which authority fields have more than one value here, and from where."""
    q = lambda sql: conn.execute(sql).fetchall()  # noqa: E731
    live = "excluded IS NULL"
    held = [r[0] for r in q(f"SELECT DISTINCT section FROM chunks WHERE source = 'case' AND {live}")]
    temp = q(f"""SELECT section, count(*), bool_or(text ~* 'expire') FROM chunks
                 WHERE source = 'ecfr' AND {live} AND section ~ 'T$' GROUP BY 1 ORDER BY 1""")
    finals = {r[0] for r in q(f"SELECT DISTINCT section FROM chunks WHERE source = 'ecfr' AND {live}")}
    return {
        "chunks_by_source": dict(q(f"SELECT source, count(*) FROM chunks WHERE {live} GROUP BY 1")),
        "opinions": dict(Counter("memo" if "Memo" in s else "tc" for s in held)),
        # distinct non-null values per source; 0 means the field was never recorded for that source
        "source_revision_values": dict(q(f"SELECT source, count(DISTINCT source_revision) FROM chunks "
                                         f"WHERE {live} GROUP BY 1")),
        "treatment_of_held_opinions": dict(Counter(f["status"] for f in flags(conn, held).values())),
        "treatment_rows_by_source": [list(r) for r in q("SELECT source, kind, count(*) FROM treatments GROUP BY 1, 2 ORDER BY 1, 2")],
        # a temporary regulation next to a final one of the same number (1.x-yT and 1.x-y) may be superseded
        "temporary_regulations": [{"section": s, "chunks": n, "mentions_expiry": e,
                                   "final_also_held": s[:-1] in finals} for s, n, e in temp],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", default="eval/golden.jsonl")
    ap.add_argument("--plan-cache", default="eval/results/decompositions-d7.json")
    ap.add_argument("--plan-sets", type=int, default=5)
    ap.add_argument("--reads", type=int, default=15, help="inversions written out to read by hand")
    args = ap.parse_args()

    plans = json.loads(Path(args.plan_cache).read_text())
    rows = [json.loads(line) for line in open(args.pilot)]
    rows = [r for r in rows if r["gold"] and r.get("scored_from") in ("B", "D")]
    # never re-plan here: a missing plan set would be an uncached LLM call and a different planner
    missing = [r["id"] for r in rows if len(plans.get(r["question"], [])) < args.plan_sets]
    rows = [r for r in rows if r["id"] not in missing]
    print(f"{len(rows)} rows × {args.plan_sets} plan sets; skipped for missing plans: {missing or 'none'}")

    per_row, reads = [], {}
    for p in range(args.plan_sets):
        for r in rows:
            for k in (8, 20):
                facts, hits = run(r, plans, p, k)
                per_row.append({"id": r["id"], "category": r["category"], "plan_set": p, "k": k, **facts})
                if k == 8 and p == 0 and (facts["inverted1"] or any(g["displaced"] for g in facts["groups"])):
                    text = {h.key or h.citation: h.text for h in hits}
                    lower = facts["top1"] if facts["inverted1"] else next(
                        g["lower"][0] for g in facts["groups"] if g["displaced"])
                    reads[r["id"]] = {"question": r["question"], "answer": r["answer"], "gold": r["gold"],
                                      "lower": lower, "lower_text": text.get(lower, "")[:1200]}
        print(f"plan set {p} done", flush=True)

    summary: dict = {}
    cats = sorted({r["category"] for r in rows}) + ["all"]
    for k in (8, 20):
        for cat in cats:
            sets = []
            for p in range(args.plan_sets):
                rs = [x for x in per_row if x["k"] == k and x["plan_set"] == p and cat in (x["category"], "all")]
                sets.append({
                    "rows": len(rs),
                    "top1": Counter(x["top1_kind"] for x in rs),
                    "inverted1": sum(x["inverted1"] for x in rs),
                    "rows_displaced": sum(any(g["displaced"] for g in x["groups"]) for x in rs),
                    "rows_outranked": sum(any(g["outranked"] for g in x["groups"]) for x in rs),
                    "gold_not_in_pool": sum(not g["in_pool"] for x in rs for g in x["groups"]),
                    "gold_groups": sum(len(x["groups"]) for x in rs),
                })
            kinds = sorted({kd for s in sets for kd in s["top1"]})
            summary[f"k{k}/{cat}"] = {
                "rows": sets[0]["rows"],
                "top1_kind": {kd: mean_sd([s["top1"].get(kd, 0) for s in sets]) for kd in kinds},
                **{m: mean_sd([s[m] for s in sets]) for m in
                   ("inverted1", "rows_displaced", "rows_outranked", "gold_not_in_pool", "gold_groups")},
            }

    with store.connect() as conn:
        inv = inventory(conn)

    RESULTS.mkdir(exist_ok=True)
    tag = "" if Path(args.pilot).stem == "golden" else f"-{Path(args.pilot).stem}"  # a dev run keeps golden's file
    out = RESULTS / f"phase-e-e0-authority{tag}.json"
    out.write_text(json.dumps({"plan_cache": args.plan_cache, "plan_sets": args.plan_sets, "arm": "route+statute1",
                               "summary": summary, "inventory": inv, "rows": per_row}, indent=1))
    with open(RESULTS / f"phase-e-e0-reads{tag}.txt", "w") as f:
        f.write("# E0 reads: plan set 0, k=8. For each, does the LOWER source state the answer in plain\n"
                "# English that the gold doesn't? Fill in: yes / no / partly, and one line why.\n\n")
        for rid, x in list(reads.items())[:args.reads]:
            f.write(f"## {rid}\nQ: {x['question']}\nReference: {x['answer']}\nGold: {x['gold']}\n"
                    f"Lower ({kind(x['lower'])}): {x['lower']}\n{x['lower_text']}\n\nVerdict: \n\n")

    for key, s in summary.items():
        print(key, json.dumps(s))
    print(json.dumps({k: v for k, v in inv.items() if k != "temporary_regulations"}))
    print(f"temporary regulations: {len(inv['temporary_regulations'])}, "
          f"with a final of the same number held: {sum(t['final_also_held'] for t in inv['temporary_regulations'])}")
    print(f"{len(reads)} rows with an inversion at k=8 (plan set 0); {min(len(reads), args.reads)} written to read")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())