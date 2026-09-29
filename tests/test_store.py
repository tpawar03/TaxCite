import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

import pytest

from taxcite import store
from taxcite.chunk import authority, expiry, revision, sunset
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


@pytest.mark.parametrize("source, citation, section, partly, expected", [
    ("usc", "26 U.S.C. § 280A(c)(1)", "280A", False, ("statute", "enacted", 4)),
    ("ecfr", "26 CFR 1.274-2(a)", "1.274-2", False, ("regulation", "final", 4)),
    ("ecfr", "26 CFR 1.274-5T(c)(1)", "1.274-5T", False, ("regulation", "temporary", 4)),
    ("ecfr", "26 CFR 1.274-5A(c)(6)", "1.274-5A", False, ("regulation", "final_prior_version", 4)),
    ("ecfr", "26 CFR 1.263A-1(b)(4)", "1.263A-1", False, ("regulation", "final", 4)),  # "A" inside a section number
    ("ecfr", "26 CFR 1.482-1T(f)", "1.482-1T", True, ("regulation", "temporary_partly_expired", 4)),
    ("case", "140 T.C. No. 16, at *1-2", "140 T.C. No. 16", False, ("opinion", "reported", 3)),
    ("case", "T.C. Memo. 2004-207, at *3", "T.C. Memo. 2004-207", False, ("opinion", "memorandum", 2)),
    ("irs_pub", "IRS Pub 587 (2025), p. 5", "Pub 587", False, ("publication", "not_binding", 1)),
    ("case", "Some v. Court, 1 F.4th 2", "x", False, ("unknown", "unknown", 0)),  # an opinion we can't classify
    ("test", "anything", "x", False, ("unknown", "unknown", 0)),
])
def test_authority_profile_comes_from_source_and_citation_form(source, citation, section, partly, expected):
    assert tuple(authority(source, citation, section, partly).values()) == expected


def test_expiry_reads_a_regulations_own_clause_against_the_snapshot_date():
    whole = "The applicability of this section expires on December 6, 2019."
    part = ("The applicability of paragraph (g)(4) of this section and paragraph (g)(6) Examples 2, 3 and 4 "
            "of this section expires May 7, 2018.")
    later = "The applicability of paragraphs (f)(2)(i)(A) through (E) of this section expires on or before September 14, 2018."
    assert expiry(whole, "2026-09-17") == "whole"
    assert expiry(part, "2026-09-17") == "partly"
    assert expiry(later, "2026-09-17") == "partly"
    assert expiry(whole, "2019-01-01") is None           # not yet expired at that snapshot
    assert expiry(part + " " + whole, "2026-09-17") == "whole"
    assert expiry("A rule with no end date.", "2026-09-17") is None


def test_revision_fills_from_as_of_where_the_ingester_had_none():
    assert revision("ecfr", "2026-09-17") == "eCFR 2026-09-17"
    assert revision("case", "2019-03-04") == "filed 2019-03-04"
    assert revision("irs_pub", "2025-01-01") == "2025 edition"
    assert revision("irs_pub", "1900-01-01") is None      # the edition year couldn't be read
    assert revision("usc", "2026-09-16") is None          # its ingester sets the release point


def test_save_stores_the_profile(conn):
    store.save(conn, chunks())
    (profile,) = conn.execute("SELECT authority FROM chunks WHERE source = 'test'").fetchone()
    assert profile == {"type": "unknown", "status": "unknown", "level": 0}  # 'test' is no real source


@pytest.mark.parametrize("cita, expired", [
    ("[T.D. 8253, 54 FR 20542, May 12, 1989]", True),     # §1.469-4T: after the cutoff, 3 years long gone
    ("[T.D. 8175, 53 FR 5700, Feb. 25, 1988, as amended by T.D. 8253, 54 FR 20535, May 12, 1989]", False),  # issued before it
    ("[T.D. 8215, 53 FR 27043, July 18, 1988]", False),
    ("[59 FR 11922, Mar. 15, 1994]", True),               # no T.D. number in the note: the date still decides
    ("[T.D. 9999, 90 FR 1, Jan. 5, 2025]", False),        # issued after the cutoff but not yet 3 years old
    (None, False),
])
def test_section_7805e2_sunsets_temporary_regulations_issued_after_1988(cita, expired):
    assert sunset(cita, "2026-09-17") is expired
