"""Effective dates from the statutory notes (D4), on six real sections in tests/fixtures/usc_notes.xml.

Each case is a failure class the hand checks found (tasks/todo.md D4)."""

import pytest

from taxcite.chunk import Chunk
from taxcite.ingest import usc
from taxcite.ingest.usc_notes import clause_for, covers, positive_rule


@pytest.fixture(scope="module")
def chunks():
    return {c.key: c for c in usc.parse("tests/fixtures/usc_notes.xml")}


def effective(chunks, key):
    return chunks[f"26 U.S.C. § {key}"].effective


def test_quoted_law_rule_for_a_substituted_amount(chunks):
    e = effective(chunks, "179(b)(1)#body#1")
    assert (e["year"], e["date"]) == (2025, "December 31, 2024")
    assert e["rule"] == "shall apply to property placed in service in taxable years beginning after December 31, 2024"
    assert "“$2,500,000” for “$1,000,000”" in e["amendment"]  # the replaced text comes along (D35, G-T02)


def test_amendment_below_the_label_found_after_a_heading(chunks):
    # "(6) Inflation adjustment. (A) In general. ..." -- the 2025 insertion is in (b)(6)(A)
    assert effective(chunks, "179(b)(6)#body#1")["year"] == 2025


def test_a_new_section_dated_by_its_own_effective_date_note(chunks):
    for key in ("224(a)-(c)#body#1", "224(d)-(h)#body#1"):
        e = effective(chunks, key)
        assert (e["year"], e["date"], e["amendment"]) == (2025, "Dec. 31, 2024", "section added")


def test_the_clause_for_the_amendments_own_subsection_wins(chunks):
    # 45P's note: (1) extension ... after December 31, 2014; (2) subsection (b) ... after December 31, 2015
    assert effective(chunks, "45P(a)-(e)#body#1")["date"] == "December 31, 2015"


def test_a_range_chunk_holds_its_subsections_whole(chunks):
    assert effective(chunks, "23(b)-(c)#body#1")["year"] == 2025  # (c)(1) changed in 2025, inline in the chunk


def test_no_rule_is_not_a_guess(chunks):
    assert all(c.effective is None for c in chunks.values() if c.section == "246A")  # only a "not applicable" rule
    assert effective(chunks, "25D(d)(2)#body#1") is None  # a catchline rename changed no text here


def test_an_exclusion_is_not_the_rule():
    note = "Amendment by Pub. L. 113–295 not applicable to preferred stock issued before Oct. 1, 1942."
    assert positive_rule(note) is None
    assert positive_rule("shall apply to taxable years beginning after December 31, 2017.").group(2) == "December 31, 2017"


def test_comma_chained_exceptions_pick_the_own_subsection():
    note = ("Amendment by section 70513 of Pub. L. 119–21 applicable to taxable years beginning after July 4, 2025, "
            "except that amendment by section 70513(a) of Pub. L. 119–21 applicable to facilities the construction "
            "of which begins after the date which is 12 months after July 4, 2025, amendment by section 70513(d) of "
            "Pub. L. 119–21 applicable on or after June 16, 2025")
    assert positive_rule(clause_for(note, "70513", "d")).group(2) == "June 16, 2025"
    assert positive_rule(clause_for(note, "70513", "b")).group(2) == "July 4, 2025"


def test_a_cross_reference_is_not_a_subparagraph_marker():
    chunk = Chunk("26 U.S.C. § 163(h)(3)", "163", "h", "(3) Qualified residence interest. (A) In general. "
                  "... the limitation of subparagraph (F) ...", 10, None, "2026-09-16", source="usc")
    assert covers(chunk, "(h)(3)(A)")
    assert not covers(chunk, "(h)(3)(F)")
