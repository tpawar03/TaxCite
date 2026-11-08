"""ADR-18 revisited: hosted embedding models against bge-base, on the golden set.

    uv run python eval/embed_bench.py                          # every model with a key in .env
    uv run python eval/embed_bench.py --model kanon-2-embedder # repeatable

ADR-18 benchmarked self-hosted models on CPU and excluded anything slower than ~50 ms
a query embed. A hosted API moves the model off this machine, so the 8B and
legal-tuned models become testable; query latency is now a network round trip and
is measured with everything else.

Each hosted model gets its own Qdrant collection built from the same Postgres rows,
with the same BM25 sparse vectors, so differences come from the dense model alone.
The baseline is the live `chunks` collection (bge-base), never rebuilt or touched.

Paid work is checkpointed: a collection is rebuilt only for sources whose point
count doesn't match Postgres, and every scored row is appended to a JSONL that a
re-run resumes from.

Octen-Embedding-8B is not here: no provider hosts it, and it is a tuned
Qwen3-Embedding-8B, which is (2026-10-28).
"""

import argparse
import json
import os
import sys
import time
from datetime import date
from functools import cache
from pathlib import Path

import httpx
import numpy as np
from dotenv import load_dotenv
from qdrant_client import models as qmodels

from taxcite import index, retrieve, store
from taxcite.retrieve import search

sys.path.insert(0, str(Path(__file__).parent))
from retrieval import groups, mrr, ndcg_at_k, recall_at_k, section_of  # noqa: E402

load_dotenv()

SOURCES = ("ecfr", "irs_pub", "usc", "case")
BASELINE = index.DENSE_MODEL  # scored on the live collection
QWEN_QUERY = "Instruct: Given a tax question, retrieve passages that answer it\nQuery: "
RESULTS = Path("eval/results")


class Hosted:
    """A hosted embedding API in fastembed's shape (`embed` for chunks, `query_embed` for a query),
    so index.sync and retrieve.search use it unchanged. Vectors come back as numpy arrays for
    the same reason: both callers call `.tolist()`."""

    def __init__(self, model: str, base_url: str, key_env: str, usd_per_m: float,
                 query_prefix: str = "", input_type: bool = False, isaacus: bool = False,
                 extra: dict | None = None, per_request: int = 16):
        self.model, self.base_url, self.key_env, self.usd_per_m = model, base_url, key_env, usd_per_m
        self.query_prefix, self.input_type, self.isaacus = query_prefix, input_type, isaacus
        self.extra, self.per_request = extra or {}, per_request
        self.tokens = 0
        self.http = httpx.Client(timeout=120)  # keep-alive: a new TLS handshake per query added ~100 ms

    def _call(self, texts: list[str], query: bool) -> list[np.ndarray]:
        if self.isaacus:
            body = {"model": self.model, "texts": texts,
                    "task": "retrieval/query" if query else "retrieval/document"}
        else:
            body = {"model": self.model, "input": [self.query_prefix + t if query else t for t in texts]} | self.extra
            if self.input_type:  # NVIDIA: asymmetric query/passage encoders
                body |= {"input_type": "query" if query else "passage", "truncate": "END"}
        headers = {"Authorization": f"Bearer {os.environ[self.key_env]}"}
        for attempt in range(8):
            try:
                r = self.http.post(f"{self.base_url}/embeddings", json=body, headers=headers)
            except httpx.TransportError:  # one read timeout ended a 33-minute BGE-M3 build
                if attempt == 7:
                    raise
                time.sleep(2 ** attempt)
                continue
            if r.status_code not in (429, 500, 502, 503, 504):
                break
            time.sleep(2 ** attempt)  # rate limits: NVIDIA's free tier is ~40 requests a minute
        r.raise_for_status()
        data = r.json()
        usage = data.get("usage") or {}
        self.tokens += usage.get("input_tokens") or usage.get("prompt_tokens") or usage.get("total_tokens") or 0
        items = data["embeddings"] if self.isaacus else data["data"]
        return [np.asarray(e["embedding"], dtype=np.float32) for e in sorted(items, key=lambda e: e["index"])]

    def embed(self, texts, **_):
        texts = list(texts)
        return [v for i in range(0, len(texts), self.per_request)
                for v in self._call(texts[i:i + self.per_request], query=False)]

    def query_embed(self, query: str):
        return self._call([query], query=True)

    @property
    def usd(self) -> float:
        return self.tokens / 1e6 * self.usd_per_m


OPENROUTER = "https://openrouter.ai/api/v1"
# OpenRouter otherwise routes each request to any host, and some serve fp8: one collection could mix
# precisions. DeepInfra serves both models (bge-m3 at fp32); no fallback, so a refusal fails loudly.
DEEPINFRA_ONLY = {"provider": {"order": ["deepinfra"], "allow_fallbacks": False}}
HOSTED = {
    "kanon-2-embedder": Hosted("kanon-2-embedder", "https://api.isaacus.com/v1", "ISAACUS_API_KEY", 0.35,
                               isaacus=True),
    "nvidia/nemotron-3.5-embed-8b": Hosted("nvidia/nemotron-3.5-embed-8b", "https://integrate.api.nvidia.com/v1",
                                           "NVIDIA_API_KEY", 0.0, input_type=True),
    "qwen/qwen3-embedding-8b": Hosted("qwen/qwen3-embedding-8b", OPENROUTER, "OPENROUTER_API_KEY", 0.01,
                                      query_prefix=QWEN_QUERY, extra=DEEPINFRA_ONLY),
    # OpenRouter checks a request's total tokens against the 8K context: 16 chunks of ~500 overflow it
    "baai/bge-m3": Hosted("baai/bge-m3", OPENROUTER, "OPENROUTER_API_KEY", 0.01, extra=DEEPINFRA_ONLY,
                          per_request=4),
}

_local_models = retrieve._models


@cache
def _models(name: str = BASELINE):
    """retrieve.search loads its dense model by name; hosted names resolve here instead."""
    if name in HOSTED:
        from fastembed import SparseTextEmbedding  # not via _local_models: under EMBED_MODEL its default is hosted

        return HOSTED[name], SparseTextEmbedding(index.SPARSE_MODEL)
    return _local_models(name)


retrieve._models = _models  # embed() looks _models up at call time


def collection_for(model: str) -> str:
    if model == BASELINE:
        return index.COLLECTION
    return "bench_" + model.split("/")[-1].replace(".", "_").replace("-", "_")


def build(model: str, conn) -> str:
    """Index every chunk with one hosted model, skipping sources already complete (a resumed run)."""
    from fastembed import SparseTextEmbedding

    name, dense = collection_for(model), HOSTED[model]
    qc = index.client()
    sparse = None
    for source in SOURCES:
        want = store.count(conn, source, indexable_only=True)
        have = 0
        if qc.collection_exists(name):
            only = qmodels.Filter(must=[qmodels.FieldCondition(key="source", match=qmodels.MatchValue(value=source))])
            have = qc.count(name, count_filter=only, exact=True).count
        if have == want:
            print(f"  {source}: {have} points already indexed", flush=True)
            continue
        sparse = sparse or SparseTextEmbedding(index.SPARSE_MODEL)
        dim = len(dense.embed(["dimension probe"])[0])
        started = time.time()
        index.sync(conn, qc, source, name, dense=dense, sparse=sparse, dim=dim,
                   progress=lambda n, total, t0: n % 1600 == 0 and print(f"    {n}/{total}", flush=True))
        print(f"  {source}: {want} points in {(time.time() - started) / 60:.1f} min "
              f"(${dense.usd:.2f} so far)", flush=True)
    return name


def score_one(model: str, collection: str, q: dict, mode: str, k: int) -> dict:
    retrieve.embed.cache_clear()  # hybrid would otherwise reuse dense's embed of the same question
    t0 = time.time()
    hits = search(q["question"], k=k, mode=mode, collection=collection, dense_name=model)
    retrieved = [h.key or h.citation for h in hits]
    gold = groups(q["gold"])
    return {
        "model": model, "id": q["id"], "mode": mode, "category": q["category"],
        "recall": recall_at_k(retrieved, gold),
        "ndcg": ndcg_at_k(retrieved, gold),
        "mrr": mrr(retrieved, gold),
        "section_recall": recall_at_k([h.section for h in hits],
                                      [{section_of(c.split("#")[0]) for c in g} for g in gold]),
        "latency_ms": (time.time() - t0) * 1000,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--model", action="append", choices=[BASELINE, *HOSTED], help="repeatable; default is all")
    ap.add_argument("--pilot", default="eval/golden.jsonl")
    args = ap.parse_args()

    wanted = args.model or [BASELINE, *HOSTED]
    missing = [m for m in wanted if m in HOSTED and not os.environ.get(HOSTED[m].key_env)]
    for m in missing:
        print(f"skipping {m}: {HOSTED[m].key_env} is not set")
    models = [m for m in wanted if m not in missing]

    questions = [json.loads(line) for line in open(args.pilot) if line.strip()]
    scored = [q for q in questions if q.get("scorable", True) and q["gold"]]
    print(f"{len(scored)} questions, {len(models)} models, k={args.k}\n")

    RESULTS.mkdir(parents=True, exist_ok=True)
    log = RESULTS / f"embed_bench-{Path(args.pilot).stem}-k{args.k}.jsonl"
    rows = [json.loads(line) for line in open(log)] if log.exists() else []
    done = {(r["model"], r["id"], r["mode"]) for r in rows}

    with store.connect() as conn, open(log, "a") as out:
        for model in models:
            print(f"{model}", flush=True)
            collection = build(model, conn) if model in HOSTED else collection_for(model)
            search(scored[0]["question"], k=1, mode="dense", collection=collection, dense_name=model)  # warm up
            for q in scored:
                for mode in ("dense", "hybrid"):
                    if (model, q["id"], mode) in done:
                        continue
                    row = score_one(model, collection, q, mode, args.k)
                    out.write(json.dumps(row) + "\n")
                    out.flush()
                    rows.append(row)

    def avg(model: str, key: str, mode: str, category: str | None = None) -> float:
        vals = [r[key] for r in rows
                if r["model"] == model and r["mode"] == mode and (category is None or r["category"] == category)]
        return sum(vals) / len(vals) if vals else 0.0

    categories = sorted({q["category"] for q in scored})
    header = (f"{'model':<26}{'mode':<8}{'Recall':>8}{'nDCG':>8}{'MRR':>7}{'SectR':>7}"
              + "".join(f"{c[:8]:>9}" for c in categories) + f"{'ms':>7}")
    print("\n" + header)
    print("-" * len(header))
    for model in models:
        for mode in ("dense", "hybrid"):
            print(f"{model.split('/')[-1]:<26}{mode:<8}"
                  f"{avg(model, 'recall', mode):>8.3f}{avg(model, 'ndcg', mode):>8.3f}"
                  f"{avg(model, 'mrr', mode):>7.3f}{avg(model, 'section_recall', mode):>7.3f}"
                  + "".join(f"{avg(model, 'recall', mode, c):>9.3f}" for c in categories)
                  + f"{avg(model, 'latency_ms', mode):>7.0f}")

    spend = {m: {"tokens": HOSTED[m].tokens, "usd": round(HOSTED[m].usd, 4)} for m in models if m in HOSTED}
    for m, s in spend.items():
        print(f"{m}: {s['tokens']:,} tokens this run, ${s['usd']:.2f}")
    summary = RESULTS / f"embed_bench-{date.today()}.json"
    summary.write_text(json.dumps({"k": args.k, "questions": args.pilot, "spend_this_run": spend, "rows": rows}, indent=2))
    print(f"\nwrote {summary} (rows also in {log})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
