import xml.etree.ElementTree as ET

import pytest

from taxcite import index, store
from taxcite.ingest.ecfr import parse

COLLECTION = "chunks_test"
CITE = "26 CFR 1.test-1(a)-(b)"
SECTION = """<ECFR><DIV8 N="1.test-1" TYPE="SECTION">
  <HEAD>§ 1.test-1 Home office deduction.</HEAD>
  <P>(a) <I>General rule.</I> A taxpayer may deduct expenses for business use of a home.</P>
  <P>(b) <I>Exception.</I> No deduction is allowed for personal use of the space.</P>
</DIV8></ECFR>"""
TOC = """<ECFR><DIV8 N="1.test-2" TYPE="SECTION">
  <HEAD>§ 1.test-2 Table of contents.</HEAD><P>(a) Something.</P></DIV8></ECFR>"""


@pytest.fixture(scope="module")
def models_():
    from fastembed import SparseTextEmbedding, TextEmbedding
    return TextEmbedding(index.DENSE_MODEL), SparseTextEmbedding(index.SPARSE_MODEL)


@pytest.fixture
def ctx():
    qc = index.client()
    if qc.collection_exists(COLLECTION):
        qc.delete_collection(COLLECTION)
    with store.connect() as conn:
        store.create_table(conn)
        conn.execute("DELETE FROM chunks WHERE source = 'test'")
        conn.execute("DELETE FROM chunk_versions WHERE source = 'test'")
        conn.commit()
        yield conn, qc
        conn.execute("DELETE FROM chunks WHERE source = 'test'")
        conn.execute("DELETE FROM chunk_versions WHERE source = 'test'")
        conn.commit()
    if qc.collection_exists(COLLECTION):
        qc.delete_collection(COLLECTION)


def chunks(xml=SECTION):
    return parse(ET.fromstring(xml), "2026-09-17", source="test")


def sync(conn, qc, models_):
    return index.sync(conn, qc, "test", COLLECTION, dense=models_[0], sparse=models_[1])


def test_indexes_postgres_rows(ctx, models_):
    conn, qc = ctx
    store.save(conn, chunks())
    assert sync(conn, qc, models_) == {"written": 1, "removed": 0}
    assert index.count(qc, "test", COLLECTION) == 1


def test_reindex_does_not_duplicate(ctx, models_):
    conn, qc = ctx
    store.save(conn, chunks())
    sync(conn, qc, models_)
    sync(conn, qc, models_)
    assert index.count(qc, "test", COLLECTION) == 1


def test_excluded_rows_are_not_indexed(ctx, models_):
    conn, qc = ctx
    store.save(conn, chunks(TOC))
    assert sync(conn, qc, models_)["written"] == 0
    assert store.count(conn, "test") == 1  # kept in Postgres with its reason


def test_stale_points_are_swept(ctx, models_):
    conn, qc = ctx
    store.save(conn, chunks())
    sync(conn, qc, models_)
    shortened = SECTION.replace("<P>(b) <I>Exception.</I> No deduction is allowed for personal use of the space.</P>", "")
    store.save(conn, chunks(shortened))
    assert sync(conn, qc, models_)["removed"] == 1
    assert index.count(qc, "test", COLLECTION) == 1


def test_payload_carries_citation_and_text(ctx, models_):
    conn, qc = ctx
    store.save(conn, chunks())
    sync(conn, qc, models_)
    (point,), _ = qc.scroll(COLLECTION, limit=1, with_payload=True)
    assert point.payload["citation"] == "26 CFR 1.test-1(a)-(b)"
    assert "business use of a home" in point.payload["text"]
    assert point.payload["source"] == "test"


def test_both_vectors_are_stored(ctx, models_):
    conn, qc = ctx
    store.save(conn, chunks())
    sync(conn, qc, models_)
    (point,), _ = qc.scroll(COLLECTION, limit=1, with_vectors=True)
    assert len(point.vector["dense"]) == index.DENSE_DIM
    assert len(point.vector["sparse"].indices) > 0

def test_count_is_zero_when_the_collection_does_not_exist():
    """CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard calls this
    at import time, so a 404 here failed the whole run instead of skipping a few tests."""
    assert index.count(index.client(), name="collection-that-does-not-exist") == 0
    assert index.count(index.client(), "ecfr", name="collection-that-does-not-exist") == 0


def test_a_broken_qdrant_still_raises():
    """"No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed."""
    from qdrant_client import QdrantClient

    with pytest.raises(Exception):
        index.count(QdrantClient(url="http://localhost:1", timeout=2), name="anything")


def test_payload_carries_the_authority_profile_into_hits(ctx, models_):
    from taxcite.retrieve import search
    conn, qc = ctx
    store.save(conn, chunks())
    sync(conn, qc, models_)
    (hit,) = search("home office deduction", k=1, collection=COLLECTION, qc=qc)
    assert hit.authority == {"type": "unknown", "status": "unknown", "level": 0}


def test_backfill_fills_rows_stored_before_e2_and_is_idempotent(ctx, models_):
    conn, qc = ctx
    store.save(conn, chunks())
    sync(conn, qc, models_)
    conn.execute("UPDATE chunks SET authority = NULL WHERE source = 'test'")  # as a pre-E2 row
    conn.commit()
    qc.delete_payload(COLLECTION, keys=["authority"], points=[index.point_id(f"{CITE}#body#1")])
    first = index.backfill_authority(conn, qc, COLLECTION, sources=["test"])
    assert (first["updated"], first["points"], first["expired"]) == (1, 1, [])
    assert index.backfill_authority(conn, qc, COLLECTION, sources=["test"])["updated"] == 0
    (point,) = qc.retrieve(COLLECTION, [index.point_id(f"{CITE}#body#1")])
    assert point.payload["authority"]["level"] == 0
    assert conn.execute("SELECT count(*) FROM chunk_versions WHERE source = 'test'").fetchone()[0] == 0  # no text change
