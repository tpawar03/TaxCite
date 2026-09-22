"""Statute chunker tests against eight real sections in tests/fixtures/usc_sample.xml.

Each fixture section was picked because it breaks a naive assumption; see tasks/todo.md B2.
"""

import xml.etree.ElementTree as ET

import pytest

from taxcite.ingest import usc
from taxcite.ingest.ecfr import MAX_TOKENS

FIXTURE = "tests/fixtures/usc_sample.xml"


@pytest.fixture(scope="module")
def chunks():
    return usc.parse(FIXTURE)


def of(chunks, section):
    return [c for c in chunks if c.section == section]


def test_every_chunk_carries_the_release_point(chunks):
    assert {(c.as_of, c.source_revision, c.source) for c in chunks} == {("2026-09-16", "Pub. L. 119-110", "usc")}


def test_keys_are_unique(chunks):
    assert len({c.key for c in chunks}) == len(chunks)


def test_neighbouring_subsections_pack_into_a_range(chunks):
    assert [c.citation for c in of(chunks, "183")] == ["26 U.S.C. § 183(a)-(d)", "26 U.S.C. § 183(e)"]


def test_heading_folds_into_its_first_child(chunks):
    # "(e) Special rule." alone would be a 4-word chunk
    assert of(chunks, "183")[1].text.startswith("(e) Special rule. (1) In general.")


def test_notes_are_not_text_and_source_credit_is_the_history(chunks):
    c = of(chunks, "183")[0]
    assert "Amendments" not in c.text and "Pub. L." not in c.text
    assert c.cita.startswith("(Added Pub. L. 91–172")
    assert c.heading == "Activities not engaged in for profit"


def test_section_chapeau_stays_with_the_paragraphs_it_introduces(chunks):
    [c] = of(chunks, "212")
    assert c.citation == "26 U.S.C. § 212(1)-(3)"
    assert c.text.startswith("In the case of an individual, there shall be allowed as a deduction")
    assert "(1) for the production or collection of income;" in c.text  # and no double space after "(1)"


def test_section_with_no_provisions_is_cited_bare(chunks):
    assert [c.citation for c in of(chunks, "64")] == ["26 U.S.C. § 64"]


def test_repealed_section_is_recorded_not_indexed(chunks):
    [c] = of(chunks, "4")
    assert (c.citation, c.excluded, c.text) == ("26 U.S.C. § 4", "repealed", "")


def test_repealed_paragraph_stubs_are_dropped(chunks):
    text = " ".join(c.text for c in of(chunks, "6040"))
    assert "Repealed" not in text and "(1) For the notice required" in text


def test_oversized_subsection_splits_at_level_two(chunks):
    assert [c.citation for c in of(chunks, "1311")] == [
        "26 U.S.C. § 1311(a)", "26 U.S.C. § 1311(b)(1)", "26 U.S.C. § 1311(b)(2)", "26 U.S.C. § 1311(b)(3)",
    ]


def test_continuation_text_is_kept():
    ns = {"u": "http://xml.house.gov/schemas/uslm/1.0"}
    section = next(s for s in ET.parse(FIXTURE).getroot().iter(f"{{{ns['u']}}}section")
                   if s.get("identifier") == "/us/usc/t26/s1311")
    continuation = usc.clean(usc.text_of(section.find(".//u:continuation", ns)))
    assert any(continuation in c.text for c in usc.parse(FIXTURE) if c.section == "1311")


def test_table_is_flattened_one_row_per_line(chunks):
    [c] = of(chunks, "3241")
    assert "\n2.5 | 3.0 | 18.1 | 4.9\n" in c.text


def test_en_dash_section_number_becomes_a_hyphen(chunks):
    assert [c.citation for c in of(chunks, "1400Z-1")][0] == "26 U.S.C. § 1400Z-1(a)-(b)"


def test_chunks_stay_under_the_token_limit(chunks):
    assert all(c.tokens <= MAX_TOKENS for c in chunks)