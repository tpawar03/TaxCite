"""Chunker tests against nine real sections in tests/fixtures/ecfr_sample.xml.

Each fixture section was picked because it breaks a naive assumption; see tasks/todo.md T2.
"""

import json
import xml.etree.ElementTree as ET
from collections import Counter

import pytest

from taxcite.ingest.ecfr import MAX_TOKENS, Chunk, designations, parse

FIXTURE = "tests/fixtures/ecfr_sample.xml"
AS_OF = "2026-09-17"


@pytest.fixture(scope="module")
def chunks() -> list[Chunk]:
    return parse(FIXTURE, AS_OF)


def of(chunks: list[Chunk], section: str) -> list[Chunk]:
    return [c for c in chunks if c.section == section]


def p(xml: str) -> ET.Element:
    return ET.fromstring(xml)


# --- designations (the riskiest logic, tested directly) ---


def test_compact_two_level_designation():
    assert designations(p("<P>(b)(1) For further guidance, see...</P>"), None) == ("b", "1")


def test_designation_split_by_italic_heading():
    assert designations(p("<P>(a) <I>General rule.</I> (1) A taxpayer...</P>"), None) == ("a", "1")


def test_italic_designation_is_not_level_two():
    # (<I>2</I>) is a level-5 marker, not level 2
    assert designations(p("<P>(<I>2</I>) Further detail...</P>"), None) == (None, None)


def test_i_after_h_is_a_letter():
    assert designations(p("<P>(i) Effective dates...</P>"), "h") == ("i", None)


def test_i_elsewhere_is_a_roman_numeral():
    assert designations(p("<P>(i) Effective dates...</P>"), "b") == (None, None)


def test_plain_paragraph_has_no_designation():
    assert designations(p("<P>An estate is allowed...</P>"), None) == (None, None)


# --- section-level behaviour ---


def test_reserved_sections_produce_nothing(chunks):
    assert of(chunks, "1.42-2") == []
    assert of(chunks, "1.30C-1 - 1.30C-2") == []  # range in the N attribute


def test_source_is_tagged_on_every_chunk(chunks):
    assert {c.source for c in chunks} == {"ecfr"}


def test_whole_section_citations_match_the_governments_own(chunks):
    """eCFR ships its own citation string in hierarchy_metadata; ours must agree."""
    official = {
        d.get("N"): json.loads(d.get("hierarchy_metadata"))["citation"]
        for d in ET.parse(FIXTURE).getroot().iter("DIV8")
        if d.get("hierarchy_metadata")
    }
    whole = [c for c in chunks if c.citation == f"26 CFR {c.section}" and not c.excluded]
    assert whole, "expected at least one whole-section chunk"
    assert all(c.citation == official[c.section] for c in whole)


def test_short_section_is_one_chunk_cited_bare(chunks):
    (c,) = of(chunks, "1.642(e)-1")
    assert c.citation == "26 CFR 1.642(e)-1"
    assert c.heading.startswith("§ 1.642(e)-1")
    assert c.as_of == AS_OF
    assert c.tokens > 0


def test_cita_is_kept_out_of_the_text(chunks):
    (c,) = of(chunks, "1.642(e)-1")
    assert c.cita == "[T.D. 6712, 29 FR 3655, Mar. 24, 1964]"
    assert "T.D." not in c.text


def test_neighbouring_units_pack_into_a_range_citation(chunks):
    cs = of(chunks, "1.904(f)-4")
    assert [c.citation for c in cs] == ["26 CFR 1.904(f)-4(a)-(c)", "26 CFR 1.904(f)-4(d)"]


def test_example_text_in_pspace_is_captured(chunks):
    # worked examples live in <PSPACE>, not <P>: collecting only <P> would drop them
    assert any("X Corporation is a domestic corporation" in c.text for c in of(chunks, "1.904(f)-4"))


def test_oversized_unit_splits_at_level_two(chunks):
    cs = of(chunks, "1.707-9")
    assert [c.citation for c in cs] == [
        "26 CFR 1.707-9(a)(1)",  # combined "(a) Heading. (1)" opens both levels
        "26 CFR 1.707-9(a)(2)",
        "26 CFR 1.707-9(a)(3)",
        "26 CFR 1.707-9(a)(4)",
        "26 CFR 1.707-9(b)",
    ]


def test_letter_i_section_cites_through_j(chunks):
    (c,) = of(chunks, "1.42-1")
    assert c.citation == "26 CFR 1.42-1(h)-(j)"  # (i) read as a letter, between (h) and (j)


def test_roman_i_does_not_open_a_level_one_unit(chunks):
    cs = of(chunks, "1.704-1T")
    assert [c.citation for c in cs] == ["26 CFR 1.704-1T(a)-(c)"]
    assert "( g )" in cs[0].text  # italic designations stay inline as text


def test_reserved_paragraphs_are_dropped(chunks):
    assert not any("[Reserved]" in c.text for c in chunks)


def test_table_of_contents_is_recorded_not_indexed(chunks):
    (c,) = of(chunks, "1.641(c)-0")
    assert c.excluded == "toc"
    assert c.text == ""


def test_small_tables_are_flattened_into_rows(chunks):
    rows = [c for c in of(chunks, "1.280F-7") if "Tax year | Dollar amount" in c.text]
    assert len(rows) == 1


def test_large_table_is_recorded_with_a_reason(chunks):
    excluded = [c for c in of(chunks, "1.280F-7") if c.excluded]
    assert [c.excluded for c in excluded] == ["large_table"]


def test_no_chunk_exceeds_the_token_budget(chunks):
    assert all(c.tokens <= MAX_TOKENS for c in chunks)


def test_overlong_paragraph_splits_into_numbered_parts(chunks):
    b2 = [c for c in of(chunks, "1.280F-7") if c.citation == "26 CFR 1.280F-7(b)(2)"]
    assert [c.part for c in b2] == [1, 2]


# --- regressions for bugs found on the first run ---


def test_citations_are_unique(chunks):
    dupes = [key for key, n in Counter((c.citation, c.part) for c in chunks).items() if n > 1]
    assert dupes == []


def test_preamble_is_not_packed_with_a_designated_unit():
    xml = """<ECFR><DIV8 N="1.test-1" TYPE="SECTION">
      <HEAD>§ 1.test-1 Scope.</HEAD>
      <P>This section explains the rules that follow.</P>
      <P>(a) <I>General rule.</I> A taxpayer shall do the thing described here.</P>
    </DIV8></ECFR>"""
    cs = parse(ET.fromstring(xml), AS_OF)
    with_a = [c for c in cs if "A taxpayer shall do the thing" in c.text]
    assert all(c.citation.endswith("(a)") for c in with_a)
