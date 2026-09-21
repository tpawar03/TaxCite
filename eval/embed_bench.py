"""ADR-18: choose the dense embedding model by measuring it on the pilot set.

    uv run python eval/embed_bench.py                    # both candidates
    uv run python eval/embed_bench.py --model BAAI/bge-small-en-v1.5

Each candidate gets its own Qdrant collection built from the same Postgres rows,
so quality differences come from the model and nothing else. The live `chunks`
collection is never touched.

Candidates are filtered by viability first: nomic-embed-text-v1.5 scored 0.2
chunks/s and 491ms per query embed on this machine, which the 35s end-to-end
budget cannot absorb across three sub-queries, so it is excluded rather than
benchmarked for quality it could never be used for.
"""

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

from qdrant_client import models as qmodels

from taxcite import index, store
from taxcite.retrieve import search

sys.path.insert(0, str(Path(__file__).parent))
from retrieval import mrr, ndcg_at_k, recall_at_k, section_of  # noqa: E402

CANDIDATES = {
    "BAAI/bge-small-en-v1.5": 384,
    "BAAI/bge-base-en-v1.5": 768,
}
RESULTS = Path("eval/results")


def collection_for(model: str) -> str:
    return "bench_" + model.split("/")[-1].replace(".", "_").replace("-", "_")


def build(model: str, dim: int, conn) -> tuple[str, float, int]:
    """Index every chunk with one model into its own collection; returns build time."""
    from fastembed import SparseTextEmbedding, TextEmbedding

    name = collection_for(model)
    qc = index.client()
    if qc.collection_exists(name):
        qc.delete_collection(name)

    dense, sparse = TextEmbedding(model), SparseTextEmbedding(index.SPARSE_MODEL)
    started = time.time()
    points = 0
    for source in ("ecfr", "irs_pub"):
        result = index.sync(conn, qc, source, name, dense=dense, sparse=sparse, dim=dim)
        points += result["written"]
    return name, time.time() - started, points


def score(model: str, collection: str, questions: list[dict], k: int) -> list[dict]:
    rows = []
    for q in questions:
        gold = set(q["gold"])
        gold_sections = {section_of(c) for c in gold}
        for mode in ("dense", "hybrid"):
            t0 = time.time()
            hits = search(q["question"], k=k, mode=mode, collection=collection, dense_name=model)
            latency = (time.time() - t0) * 1000
            retrieved = [h.citation for h in hits]
            rows.append({
                "model": model, "id": q["id"], "mode": mode, "category": q["category"],
                "recall": recall_at_k(retrieved, gold),
                "ndcg": ndcg_at_k(retrieved, gold),
                "mrr": mrr(retrieved, gold),
                "section_recall": len({h.section for h in hits} & gold_sections) / len(gold_sections),
                "latency_ms": latency,
            })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--model", action="append", choices=list(CANDIDATES), help="repeatable; default is all")
    ap.add_argument("--pilot", default="eval/pilot.jsonl")
    args = ap.parse_args()
    candidates = {m: CANDIDATES[m] for m in (args.model or CANDIDATES)}

    questions = [json.loads(line) for line in open(args.pilot) if line.strip()]
    scored = [q for q in questions if q["scorable"] and q["gold"]]
    print(f"{len(scored)} questions, {len(candidates)} models, k={args.k}\n")

    rows, builds = [], {}
    with store.connect() as conn:
        for model, dim in candidates.items():
            print(f"building index for {model} ({dim}d)...", flush=True)
            collection, seconds, points = build(model, dim, conn)
            builds[model] = {"seconds": seconds, "points": points, "dim": dim,
                             "vector_mb": points * dim * 4 / 1e6}
            print(f"  {points} points in {seconds / 60:.1f} min "
                  f"(~{builds[model]['vector_mb']:.0f} MB of dense vectors)", flush=True)
            rows += score(model, collection, scored, args.k)

    def avg(model: str, key: str, mode: str, category: str | None = None) -> float:
        vals = [r[key] for r in rows
                if r["model"] == model and r["mode"] == mode
                and (category is None or r["category"] == category)]
        return sum(vals) / len(vals) if vals else 0.0

    header = (f"{'model':<26}{'mode':<8}{'Recall':>8}{'nDCG':>8}{'MRR':>7}{'SectR':>7}"
              f"{'reg':>7}{'pub':>7}{'ms':>7}")
    print("\n" + header)
    print("-" * len(header))
    for model in candidates:
        for mode in ("dense", "hybrid"):
            print(f"{model.split('/')[-1]:<26}{mode:<8}"
                  f"{avg(model,'recall',mode):>8.3f}{avg(model,'ndcg',mode):>8.3f}"
                  f"{avg(model,'mrr',mode):>7.3f}{avg(model,'section_recall',mode):>7.3f}"
                  f"{avg(model,'recall',mode,'regulation'):>7.3f}{avg(model,'recall',mode,'publication'):>7.3f}"
                  f"{avg(model,'latency_ms',mode):>7.0f}")

    print(f"\n{'model':<26}{'build min':>11}{'vectors MB':>12}")
    for model, b in builds.items():
        print(f"{model.split('/')[-1]:<26}{b['seconds'] / 60:>11.1f}{b['vector_mb']:>12.0f}")

    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / f"embed_bench-{date.today()}.json"
    out.write_text(json.dumps({"k": args.k, "builds": builds, "rows": rows}, indent=2))
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())