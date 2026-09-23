"""Search the indexed corpus.

Modes, because the eval ablation ladder (§9) needs to measure what each one
contributes: `dense` is meaning-only, `hybrid` fuses dense with sparse BM25 so
literal terms like "section 183" or "Form 8829" match as themselves, and a
`+rerank` suffix re-scores the fused candidates with a cross-encoder.
"""

from collections.abc import Sequence
from dataclasses import dataclass, replace
from functools import cache

from qdrant_client import models

from taxcite.index import COLLECTION, DENSE_MODEL, SPARSE_MODEL, client

PREFETCH = 1  # SEEDED REGRESSION for the B9 tier-2 proof; the real value is 50
OVERFETCH = 20  # extra results requested so a tie at the k boundary is resolved here, not by the store
# Chosen on the dev set (B6): jina-turbo beat both ms-marco MiniLMs and BAAI/bge-reranker-base,
# which was the slowest and the worst. 25 candidates, because hybrid Recall@25 and @50 are the
# same 0.750 on the dev set -- the extra 25 cost 900 ms a query and cannot contain a new answer.
RERANK_MODEL = "jinaai/jina-reranker-v1-turbo-en"
RERANK_CANDIDATES = 25  # fused candidates handed to the cross-encoder


@dataclass
class Hit:
    citation: str
    heading: str
    text: str
    score: float
    section: str
    source: str


@cache
def _models(dense_name: str = DENSE_MODEL):
    """Loaded once per process and per model: ~4s, which every query would otherwise pay."""
    from fastembed import SparseTextEmbedding, TextEmbedding

    return TextEmbedding(dense_name), SparseTextEmbedding(SPARSE_MODEL)


def embed(query: str, dense_name: str = DENSE_MODEL) -> tuple[list[float], models.SparseVector]:
    dense_model, sparse_model = _models(dense_name)
    dense = next(iter(dense_model.query_embed(query))).tolist()
    sparse = next(iter(sparse_model.query_embed(query)))
    return dense, models.SparseVector(indices=sparse.indices.tolist(), values=sparse.values.tolist())


@cache
def _reranker(name: str = RERANK_MODEL):
    """Loaded once per process and per model, like the embedding models."""
    from fastembed.rerank.cross_encoder import TextCrossEncoder

    return TextCrossEncoder(name)


def rerank(query: str, hits: list[Hit], k: int, name: str = RERANK_MODEL) -> list[Hit]:
    """Re-score candidates with a cross-encoder, which reads query and chunk together.

    Retrieval scores a chunk without the question in front of it; the cross-encoder
    sees both, so it can tell a rule paragraph from an example that quotes it.
    """
    if not hits:
        return []
    docs = [f"{h.citation} {h.heading}\n{h.text}" for h in hits]
    scores = _reranker(name).rerank(query, docs)
    scored = [replace(h, score=float(s)) for h, s in zip(hits, scores)]
    return sorted(scored, key=lambda h: (-h.score, h.citation))[:k]


def source_filter(source: str | Sequence[str] | None) -> models.Filter | None:
    """One source or several; several is how B7 routes a sub-query to the corpora that can answer it."""
    if not source:
        return None
    match = (models.MatchValue(value=source) if isinstance(source, str)
             else models.MatchAny(any=list(source)))
    return models.Filter(must=[models.FieldCondition(key="source", match=match)])


def search(query: str, k: int = 10, mode: str = "hybrid", source: str | Sequence[str] | None = None,
           collection: str = COLLECTION, qc=None, dense_name: str = DENSE_MODEL,
           rerank_name: str = RERANK_MODEL) -> list[Hit]:
    """Top-k chunks for a query.

    Modes are the rungs of the eval ablation ladder (§9): "sparse" is BM25 only,
    "dense" is embeddings only, "hybrid" fuses both with reciprocal rank fusion.
    Which one wins is query-dependent, so T4 measures it rather than assuming.
    A "+rerank" suffix ("hybrid+rerank") reranks those candidates with a cross-encoder.
    """
    qc = qc or client()
    mode, _, suffix = mode.partition("+")
    if suffix not in ("", "rerank"):
        raise ValueError(f"unknown mode suffix {suffix!r}; only '+rerank' exists")
    flt = source_filter(source)
    dense, sparse = embed(query, dense_name)
    limit = RERANK_CANDIDATES if suffix else k + OVERFETCH
    if mode == "dense":
        result = qc.query_points(collection, query=dense, using="dense", limit=limit, query_filter=flt)
    elif mode == "sparse":
        result = qc.query_points(collection, query=sparse, using="sparse", limit=limit, query_filter=flt)
    elif mode == "hybrid":
        result = qc.query_points(
            collection,
            prefetch=[
                models.Prefetch(query=dense, using="dense", limit=PREFETCH, filter=flt),
                models.Prefetch(query=sparse, using="sparse", limit=PREFETCH, filter=flt),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=limit,
            query_filter=flt,
        )
    else:
        raise ValueError(f"mode must be 'dense', 'sparse' or 'hybrid' (optionally '+rerank'), not {mode!r}")

    hits = [
        Hit(citation=p.payload["citation"], heading=p.payload["heading"], text=p.payload["text"],
            score=p.score, section=p.payload["section"], source=p.payload["source"])
        for p in result.points
    ]
    # Reciprocal rank fusion produces exact ties (1/61 + 1/63 is a common total). When
    # the store cuts at k itself, which tied chunk survives varies between runs, which
    # showed up as +/-1 question of jitter in the eval. Over-fetch, then break ties by
    # citation here, so a measurement is reproducible.
    hits = sorted(hits, key=lambda h: (-h.score, h.citation))
    return rerank(query, hits, k, rerank_name) if suffix else hits[:k]