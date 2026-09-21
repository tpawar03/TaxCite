"""ADR-17 revisit trigger: Qdrant against pgvector on identical data.

    uv run python eval/store_bench.py --load     # copy vectors into pgvector, build indexes
    uv run python eval/store_bench.py            # run the comparison

Both stores hold the same bge-base vectors (copied from Qdrant, not re-embedded),
so differences come from the store rather than the model. The live `chunks`
collection and the app's `chunks` table are never touched: the benchmark uses the
`bench_bge_base_en_v1_5` collection and a `bench_chunks` table.

ADR-17 reopens in favour of pgvector only if all three hold: it fits the managed
Postgres free tier, it loses no more than 2 points of recall under a strict filter,
AND its hybrid recall is within 2 points of Qdrant's. The third condition was
missing from the ADR as first written, and it is the one that decided the outcome:
Postgres full-text ranking is not BM25 and scores far worse on the lexical half.
"""

import argparse
import json
import re
import statistics
import sys
import time
from datetime import date
from pathlib import Path

from qdrant_client import models as qmodels

from taxcite import index, store
from taxcite.retrieve import embed

sys.path.insert(0, str(Path(__file__).parent))
from retrieval import recall_at_k, section_of  # noqa: E402

COLLECTION = "bench_bge_base_en_v1_5"  # same vectors as bench_chunks
TABLE = "bench_chunks"
PREFETCH = 50
RRF_K = 60  # the usual reciprocal-rank-fusion constant
RESULTS = Path("eval/results")
FREE_TIER_MB = 500  # managed Postgres free tier (Supabase) — the ADR-17 storage question

DDL = (
    f"DROP TABLE IF EXISTS {TABLE}",
    f"""CREATE TABLE {TABLE} (
        key text PRIMARY KEY, source text, citation text, section text, text text,
        embedding vector(768),
        tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED
    )""",
)
INDEXES = (
    f"CREATE INDEX bench_hnsw ON {TABLE} USING hnsw (embedding vector_cosine_ops)",
    f"CREATE INDEX bench_gin ON {TABLE} USING gin (tsv)",
    f"CREATE INDEX bench_section ON {TABLE} (section)",
)


def tsquery(text: str) -> str:
    """OR the terms: a question's words rarely all appear in one chunk, and
    websearch_to_tsquery's implicit AND returns nothing for most questions."""
    return " | ".join(w for w in re.findall(r"[A-Za-z0-9]+", text.lower()) if len(w) > 2)


def load(conn) -> None:
    qc = index.client()
    for stmt in DDL:
        conn.execute(stmt)
    conn.commit()
    offset, rows = None, 0
    t0 = time.time()
    while True:
        points, offset = qc.scroll(COLLECTION, limit=500, offset=offset, with_payload=True, with_vectors=True)
        with conn.cursor() as cur:
            cur.executemany(
                f"INSERT INTO {TABLE} (key, source, citation, section, text, embedding) "
                "VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (key) DO NOTHING",
                [(p.payload["key"], p.payload["source"], p.payload["citation"], p.payload["section"],
                  p.payload["text"], str(p.vector["dense"])) for p in points])
        rows += len(points)
        if offset is None:
            break
    conn.commit()
    print(f"copied {rows} vectors in {time.time() - t0:.0f}s")
    for stmt in INDEXES:
        t = time.time()
        conn.execute(stmt)
        conn.commit()
        print(f"  {stmt.split()[2]} in {time.time() - t:.1f}s")


# --- pgvector ---

def pg_hybrid(conn, question: str, dense: list[float], k: int) -> list[str]:
    """Dense ANN and full-text, fused with reciprocal rank fusion in SQL."""
    sql = f"""
    WITH d AS (SELECT key, row_number() OVER () AS rn FROM
                 (SELECT key FROM {TABLE} ORDER BY embedding <=> %(vec)s::vector LIMIT %(pre)s) a),
         t AS (SELECT key, row_number() OVER () AS rn FROM
                 (SELECT key FROM {TABLE} WHERE tsv @@ to_tsquery('english', %(q)s)
                  ORDER BY ts_rank_cd(tsv, to_tsquery('english', %(q)s)) DESC LIMIT %(pre)s) b)
    SELECT c.citation FROM (
        SELECT key, sum(score) AS s FROM (
            SELECT key, 1.0 / (%(rrf)s + rn) AS score FROM d
            UNION ALL SELECT key, 1.0 / (%(rrf)s + rn) FROM t) u
        GROUP BY key ORDER BY s DESC LIMIT %(k)s) ranked
    JOIN {TABLE} c ON c.key = ranked.key ORDER BY ranked.s DESC
    """
    params = {"vec": str(dense), "q": tsquery(question), "pre": PREFETCH, "k": k, "rrf": RRF_K}
    return [r[0] for r in conn.execute(sql, params).fetchall()]


def pg_filtered(conn, dense: list[float], section: str, k: int, exact: bool) -> list[str]:
    """Top-k inside one section: approximate (HNSW) or exact (sequential scan)."""
    with conn.cursor() as cur:
        if exact:  # force the planner past the index so the result is ground truth
            cur.execute("SET LOCAL enable_indexscan = off")
            cur.execute("SET LOCAL enable_bitmapscan = off")
        cur.execute(f"SELECT citation FROM {TABLE} WHERE section = %s ORDER BY embedding <=> %s::vector LIMIT %s",
                    (section, str(dense), k))
        rows = [r[0] for r in cur.fetchall()]
    conn.rollback()  # end the transaction that SET LOCAL belongs to
    return rows


# --- qdrant ---

def qd_hybrid(qc, question: str, dense: list[float], sparse, k: int) -> list[str]:
    result = qc.query_points(
        COLLECTION,
        prefetch=[qmodels.Prefetch(query=dense, using="dense", limit=PREFETCH),
                  qmodels.Prefetch(query=sparse, using="sparse", limit=PREFETCH)],
        query=qmodels.FusionQuery(fusion=qmodels.Fusion.RRF), limit=k)
    return [p.payload["citation"] for p in result.points]


def qd_filtered(qc, dense: list[float], section: str, k: int, exact: bool) -> list[str]:
    flt = qmodels.Filter(must=[qmodels.FieldCondition(key="section", match=qmodels.MatchValue(value=section))])
    result = qc.query_points(COLLECTION, query=dense, using="dense", limit=k, query_filter=flt,
                             search_params=qmodels.SearchParams(exact=exact))
    return [p.payload["citation"] for p in result.points]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--load", action="store_true", help="(re)build the pgvector table from Qdrant")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--pilot", default="eval/pilot.jsonl")
    args = ap.parse_args()

    questions = [json.loads(line) for line in open(args.pilot) if line.strip()]
    scored = [q for q in questions if q["scorable"] and q["gold"]]
    qc = index.client()

    with store.connect() as conn:
        if args.load:
            load(conn)
            return 0

        rows, timings = [], {"qdrant": [], "pgvector": []}
        for q in scored:
            dense, sparse = embed(q["question"])
            gold = set(q["gold"])
            sections = {section_of(c) for c in gold if c.startswith("26 CFR")}

            t0 = time.time(); qd = qd_hybrid(qc, q["question"], dense, sparse, args.k)
            timings["qdrant"].append((time.time() - t0) * 1000)
            t0 = time.time(); pg = pg_hybrid(conn, q["question"], dense, args.k)
            timings["pgvector"].append((time.time() - t0) * 1000)

            row = {"id": q["id"], "qdrant_recall": recall_at_k(qd, gold), "pg_recall": recall_at_k(pg, gold)}

            # filtered recall: approximate vs exact, inside one section
            if sections:
                section = sorted(sections)[0]
                for store_name, fn in (("qdrant", lambda e: qd_filtered(qc, dense, section, args.k, e)),
                                       ("pgvector", lambda e: pg_filtered(conn, dense, section, args.k, e))):
                    exact = fn(True)
                    approx = fn(False)
                    row[f"{store_name}_filtered_recall"] = (
                        len(set(approx) & set(exact)) / len(exact) if exact else 1.0)
            rows.append(row)

        size_mb = float(conn.execute(f"SELECT pg_total_relation_size('{TABLE}') / 1e6").fetchone()[0])
        chunk_count = conn.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]

    def avg(key):
        vals = [r[key] for r in rows if key in r]
        return sum(vals) / len(vals) if vals else 0.0

    print(f"{len(rows)} questions, k={args.k}\n")
    print(f"{'store':<12}{'hybrid recall':>15}{'filtered recall':>17}{'p50 ms':>9}{'p95 ms':>9}")
    print("-" * 62)
    for store_name, rkey, fkey in (("qdrant", "qdrant_recall", "qdrant_filtered_recall"),
                                   ("pgvector", "pg_recall", "pgvector_filtered_recall")):
        lat = sorted(timings[store_name])
        p50 = statistics.median(lat)
        p95 = lat[int(len(lat) * 0.95) - 1]
        print(f"{store_name:<12}{avg(rkey):>15.3f}{avg(fkey):>17.3f}{p50:>9.0f}{p95:>9.0f}")

    print(f"\npgvector table + indexes: {size_mb:.0f} MB for {chunk_count} chunks")
    for label, factor in (("phase A corpus", 1), ("+ case law (phase B/C, ~5x)", 5)):
        print(f"  {label:<30} {size_mb * factor:>6.0f} MB  "
              f"{'fits' if size_mb * factor < FREE_TIER_MB else 'EXCEEDS'} the {FREE_TIER_MB} MB free tier")

    filtered_gap = avg("qdrant_filtered_recall") - avg("pgvector_filtered_recall")
    quality_gap = avg("qdrant_recall") - avg("pg_recall")
    fits = size_mb * 5 < FREE_TIER_MB
    print(f"\nADR-17 trigger")
    print(f"  storage projected          {'PASS' if fits else 'FAIL'}")
    print(f"  filtered-recall gap {filtered_gap:+.3f}  {'PASS' if filtered_gap <= 0.02 else 'FAIL'} (reopen if <= 0.02)")
    print(f"  hybrid-recall gap   {quality_gap:+.3f}  {'PASS' if quality_gap <= 0.02 else 'FAIL'} (reopen if <= 0.02)")
    reopen = fits and filtered_gap <= 0.02 and quality_gap <= 0.02
    print("VERDICT:", "reopen in favour of pgvector" if reopen else "confirmed — Qdrant stays")

    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / f"store_bench-{date.today()}.json"
    out.write_text(json.dumps({"k": args.k, "rows": rows, "timings": timings,
                               "size_mb": size_mb, "chunks": chunk_count}, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())