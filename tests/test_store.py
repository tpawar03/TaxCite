import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

import pytest

from taxcite import store
from taxcite.ingest.ecfr import parse

SECTION = """<ECFR><DIV8 N="1.test-1" TYPE="SECTION">
  <HEAD>§ 1.test-1 Scope.</HEAD>
  <P>(a) <I>General rule.</I> A taxpayer shall do the thing described here.</P>
  <P>(b) <I>Exception.</I> Unless the thing is not applicable.</P>
</DIV8></ECFR>"""


@pytest.fixture
def conn():
    with store.connect() as c:
        store.create_table(c)
        c.execute("DELETE FROM chunks WHERE source = 'test'")
        c.execute("DELETE FROM chunk_versions WHERE source = 'test'")
        c.commit()
        yield c
        c.execute("DELETE FROM chunks WHERE source = 'test'")
        c.execute("DELETE FROM chunk_versions WHERE source = 'test'")
        c.commit()


def chunks(xml=SECTION):
    return parse(ET.fromstring(xml), "2026-09-17", source="test")


def test_save_then_count(conn):
    assert store.save(conn, chunks()) == 1
    assert store.count(conn, "test") == 1


def test_reingest_is_idempotent(conn):
    store.save(conn, chunks())
    store.save(conn, chunks())
    assert store.count(conn, "test") == 1


def test_updated_text_replaces_the_old_row(conn):
    store.save(conn, chunks())
    store.save(conn, chunks(SECTION.replace("do the thing", "do the amended thing")))
    (text,) = conn.execute("SELECT text FROM chunks WHERE source = 'test'").fetchone()
    assert "amended" in text


def test_rows_no_longer_upstream_are_swept(conn):
    store.save(conn, chunks())  # (a) and (b) packed into one chunk
    shortened = SECTION.replace("<P>(b) <I>Exception.</I> Unless the thing is not applicable.</P>", "")
    store.save(conn, chunks(shortened))
    rows = conn.execute("SELECT citation FROM chunks WHERE source = 'test'").fetchall()
    assert [r[0] for r in rows] == ["26 CFR 1.test-1(a)"]


def test_excluded_rows_are_stored_but_not_counted_as_indexable(conn):
    toc = """<ECFR><DIV8 N="1.test-2" TYPE="SECTION">
      <HEAD>§ 1.test-2 Table of contents.</HEAD><P>(a) Something.</P></DIV8></ECFR>"""
    store.save(conn, chunks(toc))
    assert store.count(conn, "test") == 1
    assert store.count(conn, "test", indexable_only=True) == 0

T1, T2 = datetime(2024, 1, 5, tzinfo=timezone.utc), datetime(2025, 7, 4, tzinfo=timezone.utc)
CITE = "26 CFR 1.test-1(a)-(b)"


def test_rewritten_text_is_retired_not_lost(conn):
    """Transaction time (D6): an amendment rewrites a chunk in place; the old text stays answerable."""
    store.save(conn, chunks(), fetched_at=T1)
    store.save(conn, chunks(SECTION.replace("do the thing", "do the amended thing")), fetched_at=T2)
    between = store.held_at(conn, CITE, datetime(2025, 1, 1, tzinfo=timezone.utc))
    after = store.held_at(conn, CITE, datetime(2025, 8, 1, tzinfo=timezone.utc))
    assert len(between) == len(after) == 1
    assert "amended" not in between[0][1] and "amended" in after[0][1]
    assert store.held_at(conn, CITE, datetime(2023, 1, 1, tzinfo=timezone.utc)) == []  # before it was recorded


def test_a_dropped_paragraph_is_retired_by_the_sweep(conn):
    with_c = SECTION.replace("</DIV8>", "<P>(c) <I>Later rule.</I> A third paragraph.</P></DIV8>")
    store.save(conn, chunks(with_c), fetched_at=T1)   # one chunk, 26 CFR 1.test-1(a)-(c)
    store.save(conn, chunks(), fetched_at=T2)         # upstream dropped (c): the sweep removes (a)-(c)
    assert [k for (k,) in conn.execute("SELECT key FROM chunks WHERE source = 'test'")] == [f"{CITE}#body#1"]
    gone = "26 CFR 1.test-1(a)-(c)"
    (text,) = store.held_at(conn, gone, datetime(2024, 6, 1, tzinfo=timezone.utc))[0][1:]
    assert "Later rule" in text                                   # still answerable for when it was held
    assert store.held_at(conn, gone, datetime.now(timezone.utc) + timedelta(days=1)) == []


def test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(conn):
    store.save(conn, chunks(), fetched_at=T1)
    store.save(conn, chunks(), fetched_at=T2)
    (recorded,) = conn.execute("SELECT recorded_at FROM chunks WHERE source = 'test'").fetchone()
    assert recorded == T1
    assert conn.execute("SELECT count(*) FROM chunk_versions WHERE source = 'test'").fetchone()[0] == 0
