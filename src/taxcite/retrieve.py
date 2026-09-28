"""Search the indexed corpus.

Modes, because the eval ablation ladder (§9) needs to measure what each one
contributes: `dense` is meaning-only, `hybrid` fuses dense with sparse BM25 so
literal terms like "section 183" or "Form 8829" match as themselves, and a
`+rerank` suffix re-scores the fused candidates with a cross-encoder.
"""

from collections.abc import Sequence
from dataclasses import dataclass, replace
from functools import cache, lru_cache

from qdrant_client import models

from taxcite.index import COLLECTION, DENSE_MODEL, SPARSE_MODEL, client

PREFETCH = 50  # candidates per branch before fusion
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
    key: str = ""  # the chunk itself: several chunks can share one citation label (C2, C6)
    effective: dict | None = None  # statute (D4): when this text's latest amendment applies
    authority: dict | None = None  # E2: {"type", "status", "level"}, from structured fields only (ADR-13)


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


@lru_cache(maxsize=1024)
def _scores(name: str, query: str, docs: tuple[str, ...]) -> tuple[float, ...]:
    """The cross-encoder is deterministic, so a pool scored once needn't be scored again. E4 compares a
    dozen orderings of the same pools; bounded, so a long-running server can't grow it without limit."""
    return tuple(float(s) for s in _reranker(name).rerank(query, list(docs)))


def rerank(query: str, hits: list[Hit], k: int, name: str = RERANK_MODEL) -> list[Hit]:
    """Re-score candidates with a cross-encoder, which reads query and chunk together.

    Retrieval scores a chunk without the question in front of it; the cross-encoder
    sees both, so it can tell a rule paragraph from an example that quotes it.
    """
    if not hits:
        return []
    scores = _scores(name, query, tuple(f"{h.citation} {h.heading}\n{h.text}" for h in hits))
    scored = [replace(h, score=float(s)) for h, s in zip(hits, scores)]
    return sorted(scored, key=lambda h: (-h.score, h.citation))[:k]


def source_filter(source: str | Sequence[str] | None) -> models.Filter | None:
    """One source or several; several is how B7 routes a sub-query to the corpora that can answer it."""
    if not source:
        return None
    match = (models.MatchValue(value=source) if isinstance(source, str)
             else models.MatchAny(any=list(source)))
    return models.Filter(must=[models.FieldCondition(key="source", match=match)])


def edition_filter(year: int, back: int, forward: int) -> models.Filter:
    """Keep chunks with no edition (everything but publications, and undated publications) and
    publications whose edition lies within [year - back, year + forward] (D3)."""
    return models.Filter(should=[
        models.IsEmptyCondition(is_empty=models.PayloadField(key="edition")),
        models.FieldCondition(key="edition", range=models.Range(gte=year - back, lte=year + forward)),
    ])


def search(query: str, k: int = 10, mode: str = "hybrid", source: str | Sequence[str] | None = None,
           collection: str = COLLECTION, qc=None, dense_name: str = DENSE_MODEL,
           rerank_name: str = RERANK_MODEL, sections: Sequence[str] | None = None,
           year: int | None = None, editions: tuple[int, int] = (0, 0)) -> list[Hit]:
    """Top-k chunks for a query.

    Modes are the rungs of the eval ablation ladder (§9): "sparse" is BM25 only,
    "dense" is embeddings only, "hybrid" fuses both with reciprocal rank fusion.
    Which one wins is query-dependent, so T4 measures it rather than assuming.
    A "+rerank" suffix ("hybrid+rerank") reranks those candidates with a cross-encoder.
    `sections` limits the search to those sections, e.g. the opinions a citation hop reached (C5).
    `year` limits publications to editions within `editions` = (back, forward) years of it (D3).
    """
    qc = qc or client()
    mode, _, suffix = mode.partition("+")
    if suffix not in ("", "rerank"):
        raise ValueError(f"unknown mode suffix {suffix!r}; only '+rerank' exists")
    flt = source_filter(source)
    if sections:
        within = models.FieldCondition(key="section", match=models.MatchAny(any=list(sections)))
        flt = models.Filter(must=[*(flt.must if flt else []), within])
    if year is not None:
        flt = models.Filter(must=[*(flt.must if flt else []), edition_filter(year, *editions)])
    # Dense search is exact (E4). Approximate (HNSW) kept 98.7% of the exact top 50 on average but 88% at
    # worst, and its misses moved when Qdrant re-optimised the collection: the CI gate read 0.70, then 0.72,
    # on identical code and data. Exact costs 6 ms a query against 4 (and ~1 s of reranking), and makes
    # retrieval a function of code and data again. Sparse search is exact already.
    exact = models.SearchParams(exact=True)
    dense, sparse = embed(query, dense_name)
    limit = RERANK_CANDIDATES if suffix else k + OVERFETCH
    if mode == "dense":
        result = qc.query_points(collection, query=dense, using="dense", limit=limit, query_filter=flt,
                                 search_params=exact)
    elif mode == "sparse":
        result = qc.query_points(collection, query=sparse, using="sparse", limit=limit, query_filter=flt)
    elif mode == "hybrid":
        result = qc.query_points(
            collection,
            prefetch=[
                models.Prefetch(query=dense, using="dense", limit=PREFETCH, filter=flt, params=exact),
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
            score=p.score, section=p.payload["section"], source=p.payload["source"], key=p.payload.get("key", ""),
            effective=p.payload.get("effective"), authority=p.payload.get("authority"))
        for p in result.points
    ]
    # Reciprocal rank fusion produces exact ties (1/61 + 1/63 is a common total). When
    # the store cuts at k itself, which tied chunk survives varies between runs, which
    # showed up as +/-1 question of jitter in the eval. Over-fetch, then break ties by
    # citation here, so a measurement is reproducible.
    hits = sorted(hits, key=lambda h: (-h.score, h.citation))
    return rerank(query, hits, k, rerank_name) if suffix else hits[:k]