import xml.etree.ElementTree as ET

import pytest

from taxcite import index, store
from taxcite.ingest.ecfr import parse

COLLECTION = "chunks_test"
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
        conn.commit()
        yield conn, qc
        conn.execute("DELETE FROM chunks WHERE source = 'test'")
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