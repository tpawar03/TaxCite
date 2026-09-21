import xml.etree.ElementTree as ET

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
        c.commit()
        yield c
        c.execute("DELETE FROM chunks WHERE source = 'test'")
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