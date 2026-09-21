"""Search the indexed corpus.

Two modes, because the eval ablation ladder (§9) needs to measure what each one
contributes: `dense` is meaning-only, `hybrid` fuses dense with sparse BM25 so
literal terms like "section 183" or "Form 8829" match as themselves.
"""

from dataclasses import dataclass
from functools import cache

from qdrant_client import models

from taxcite.index import COLLECTION, DENSE_MODEL, SPARSE_MODEL, client

PREFETCH = 50  # candidates per branch before fusion
OVERFETCH = 20  # extra results requested so a tie at the k boundary is resolved here, not by the store


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


def search(query: str, k: int = 10, mode: str = "hybrid", source: str | None = None,
           collection: str = COLLECTION, qc=None, dense_name: str = DENSE_MODEL) -> list[Hit]:
    """Top-k chunks for a query.

    Modes are the rungs of the eval ablation ladder (§9): "sparse" is BM25 only,
    "dense" is embeddings only, "hybrid" fuses both with reciprocal rank fusion.
    Which one wins is query-dependent, so T4 measures it rather than assuming.
    """
    qc = qc or client()
    dense, sparse = embed(query, dense_name)
    flt = None
    if source:
        flt = models.Filter(must=[models.FieldCondition(key="source", match=models.MatchValue(value=source))])

    limit = k + OVERFETCH
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
        raise ValueError(f"mode must be 'dense', 'sparse' or 'hybrid', not {mode!r}")

    hits = [
        Hit(citation=p.payload["citation"], heading=p.payload["heading"], text=p.payload["text"],
            score=p.score, section=p.payload["section"], source=p.payload["source"])
        for p in result.points
    ]
    # Reciprocal rank fusion produces exact ties (1/61 + 1/63 is a common total). When
    # the store cuts at k itself, which tied chunk survives varies between runs, which
    # showed up as +/-1 question of jitter in the eval. Over-fetch, then break ties by
    # citation here, so a measurement is reproducible.
    return sorted(hits, key=lambda h: (-h.score, h.citation))[:k]