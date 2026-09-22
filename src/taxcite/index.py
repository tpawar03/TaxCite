"""Embed chunks and keep a Qdrant collection in step with Postgres.

Postgres is the source of truth; this module mirrors its indexable rows into
Qdrant. Dense vectors come from a local embedding model, sparse vectors from
BM25, and both live in one collection so a single query can fuse them (ADR-6).
"""

import os
import time
import uuid
from collections.abc import Iterator

from qdrant_client import QdrantClient, models

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.environ.get("QDRANT_COLLECTION", "chunks")
DENSE_MODEL = os.environ.get("EMBED_MODEL", "BAAI/bge-base-en-v1.5")  # ADR-18
SPARSE_MODEL = "Qdrant/bm25"
DENSE_DIM = 768  # bge-base; bge-small was 384
# Every text in a batch is padded to the longest, and ONNX keeps the memory it grabs.
# Measured on the 128 longest chunks: 16 -> 2.91/s at 1.5 GB, 128 -> 2.86/s at 4.5 GB.
# 256 grew the ingest to 8.6 GB and 20 GB of swap, at 0.45/s (log #35).
BATCH = 16
NAMESPACE = uuid.UUID("6f1d4f9a-6a5e-5f1e-9a8b-2c3d4e5f6a7b")  # fixed: point ids must be reproducible

ROWS_SQL = """
    SELECT key, citation, part, section, heading, text, tokens, source, as_of
    FROM chunks WHERE source = %s AND excluded IS NULL ORDER BY key
"""


# Bulk upserts of 768-dimension vectors exceed the client's short default timeout
# when the machine is busy, and the failure surfaces as a bare "timed out".
CLIENT_TIMEOUT = 120


def client(url: str | None = None, timeout: int = CLIENT_TIMEOUT) -> QdrantClient:
    return QdrantClient(url=url or QDRANT_URL, timeout=timeout)


def point_id(key: str) -> str:
    """Qdrant ids must be UUIDs or ints, so derive one from the chunk key."""
    return str(uuid.uuid5(NAMESPACE, key))


def create_collection(qc: QdrantClient, name: str = COLLECTION, dim: int = DENSE_DIM) -> None:
    if qc.collection_exists(name):
        return
    qc.create_collection(
        name,
        vectors_config={"dense": models.VectorParams(size=dim, distance=models.Distance.COSINE)},
        # IDF is required for BM25 scoring: without it Qdrant cannot down-weight
        # words that appear in most documents ("activity", "taxable", "section")
        sparse_vectors_config={"sparse": models.SparseVectorParams(modifier=models.Modifier.IDF)},
    )
    for field in ("source", "section", "citation"):
        qc.create_payload_index(name, field, models.PayloadSchemaType.KEYWORD)


def batched(rows: list[dict], size: int = BATCH) -> Iterator[list[dict]]:
    for i in range(0, len(rows), size):
        yield rows[i:i + size]


def sync(conn, qc: QdrantClient, source: str, name: str = COLLECTION, dense=None, sparse=None,
         parallel: int | None = None, progress=None, dim: int = DENSE_DIM) -> dict:
    """Mirror Postgres' indexable rows for one source into Qdrant.

    Returns counts of what was written and removed. `parallel` is off by default:
    measured at 7.0/s single-process vs 3.4/s with four workers, because the
    ONNX runtime already uses every core.
    """
    from fastembed import SparseTextEmbedding, TextEmbedding

    dense = dense or TextEmbedding(DENSE_MODEL)
    sparse = sparse or SparseTextEmbedding(SPARSE_MODEL)
    create_collection(qc, name, dim)

    with conn.cursor() as cur:
        cur.execute(ROWS_SQL, (source,))
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    # end the read transaction now: embedding takes up to ~90 min, and an open
    # transaction holds a lock that blocks any schema change (e.g. store.create_table)
    conn.commit()

    written = 0
    started = time.time()
    for batch in batched(rows):
        texts = [r["text"] for r in batch]
        kw = {"parallel": parallel} if parallel is not None else {}
        dvecs = list(dense.embed(texts, **kw))
        svecs = list(sparse.embed(texts, **kw))
        upsert_with_retry(
            qc, name,
            [
                models.PointStruct(
                    id=point_id(r["key"]),
                    vector={
                        "dense": d.tolist(),
                        "sparse": models.SparseVector(indices=s.indices.tolist(), values=s.values.tolist()),
                    },
                    payload={
                        "key": r["key"], "citation": r["citation"], "part": r["part"],
                        "section": r["section"], "heading": r["heading"], "text": r["text"],
                        "tokens": r["tokens"], "source": r["source"], "as_of": str(r["as_of"]),
                    },
                )
                for r, d, s in zip(batch, dvecs, svecs)
            ],
        )
        written += len(batch)
        if progress:
            progress(written, len(rows), started)

    removed = sweep(qc, source, {r["key"] for r in rows}, name)
    return {"written": written, "removed": removed}


def upsert_with_retry(qc: QdrantClient, name: str, points: list, attempts: int = 3) -> None:
    """Retry a batch once or twice: a busy host turns a slow upsert into a timeout."""
    for attempt in range(1, attempts + 1):
        try:
            qc.upsert(name, points=points)
            return
        except Exception:
            if attempt == attempts:
                raise
            time.sleep(5 * attempt)


def sweep(qc: QdrantClient, source: str, live_keys: set[str], name: str = COLLECTION) -> int:
    """Delete points whose chunk no longer exists in Postgres (renumbered or repealed text)."""
    stale: list[str] = []
    offset = None
    flt = models.Filter(must=[models.FieldCondition(key="source", match=models.MatchValue(value=source))])
    while True:
        points, offset = qc.scroll(name, scroll_filter=flt, limit=1000, offset=offset, with_payload=["key"], with_vectors=False)
        stale += [p.id for p in points if p.payload["key"] not in live_keys]
        if offset is None:
            break
    if stale:
        qc.delete(name, points_selector=models.PointIdsList(points=stale))
    return len(stale)


def count(qc: QdrantClient, source: str | None = None, name: str = COLLECTION) -> int:
    flt = None
    if source:
        flt = models.Filter(must=[models.FieldCondition(key="source", match=models.MatchValue(value=source))])
    return qc.count(name, count_filter=flt, exact=True).count