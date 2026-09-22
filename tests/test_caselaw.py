"""Case-law tests against two real Tax Court opinions (see tasks/todo.md B3):

- caselaw_memo.pdf: T.C. Memo. 2021-115, the current layout (one text box per
  paragraph, "[*N]" page markers, a masthead and a "Served" stamp)
- caselaw_tc.pdf: 125 T.C. No. 13 (2005), the older layout (one text box per line,
  "- N -" page numbers)

DAWSON itself is never called: selection is tested against a canned response.
"""

from pathlib import Path

import pytest

from taxcite.ingest import caselaw

MEMO = {"citation": "T.C. Memo. 2021-115", "caseCaption": "Carl L. Gregory & Leila Gregory, Petitioners",
        "filingDate": "2021-09-29T18:32:53.750Z"}
TC = {"citation": "125 T.C. No. 13", "caseCaption": "Dennis E. and Paula W. Lofstrom, Petitioners",
      "filingDate": "2005-11-22T00:00:00.000Z"}


@pytest.fixture(scope="module")
def memo():
    return caselaw.parse(Path("tests/fixtures/caselaw_memo.pdf"), MEMO)


@pytest.fixture(scope="module")
def tc():
    return caselaw.parse(Path("tests/fixtures/caselaw_tc.pdf"), TC)


def test_chunks_are_pin_cited_by_page(memo):
    assert memo[0].citation == "T.C. Memo. 2021-115, at *1-2"
    assert all(c.citation.startswith("T.C. Memo. 2021-115, at *") for c in memo)
    assert {(c.section, c.source, c.as_of) for c in memo} == {("T.C. Memo. 2021-115", "case", "2021-09-29")}


def test_heading_is_the_case_name(memo):
    assert memo[0].heading == "Carl L. Gregory & Leila Gregory v. Commissioner"


def test_consecutive_chunks_overlap_by_one_paragraph(memo):
    assert len(memo) > 3
    assert all(a.text.split("\n")[-1] == b.text.split("\n")[0] for a, b in zip(memo, memo[1:]))


def test_chunks_stay_under_the_token_limit(memo, tc):
    assert all(c.tokens <= caselaw.MAX_TOKENS for c in memo + tc)


def test_page_furniture_is_not_text(memo):
    text = "\n".join(c.text for c in memo)
    assert "[*" not in text  # page markers become the citation, not content
    assert "Served" not in text  # the service stamp
    assert all(not caselaw.PAGE_NUMBER.match(line) for c in memo for line in c.text.split("\n"))


def test_opinion_text_survives(memo):
    assert any("section 183(b)(2)" in c.text for c in memo)


def test_older_line_per_box_layout_parses(tc):
    assert tc[0].citation == "125 T.C. No. 13, at *1-2"
    assert not any(line.strip().startswith("- ") and line.strip().endswith(" -") for c in tc for line in c.text.split("\n"))


def test_an_opinion_without_text_is_recorded_not_indexed(monkeypatch):
    monkeypatch.setattr(caselaw, "paragraphs", lambda path: [])
    [c] = caselaw.parse(Path("unused.pdf"), MEMO)
    assert (c.citation, c.excluded, c.text) == ("T.C. Memo. 2021-115", "no_text", "")


def result(docket, title, filed):
    return {"docketNumber": docket, "docketEntryId": f"id-{docket}", "documentTitle": title,
            "filingDate": filed, "caseCaption": "X, Petitioner"}


def test_selection_dedupes_by_citation_and_keeps_the_newest(monkeypatch):
    canned = [
        result("1-20", "Memorandum Opinion Judge A T.C. Memo. 2020-1", "2020-01-01"),
        result("2-20", "Memorandum Opinion Judge A T.C. Memo. 2020-1", "2020-01-01"),  # consolidated docket
        result("3-21", "Memorandum Opinion Judge B T.C. Memo. 2021-5", "2021-06-01"),
        result("4-22", "Order without a citation", "2022-01-01"),
        result("5-19", "T.C. OPINION, Judge C 150 T.C. No. 2.", "2019-01-01"),
    ]
    monkeypatch.setattr(caselaw, "get", lambda client, path, **params: {"results": canned})
    monkeypatch.setattr(caselaw, "TOPICS", {"one": "q", "two": "q"})
    ops = caselaw.select(client=None, per_topic=2)
    assert [o["citation"] for o in ops] == ["T.C. Memo. 2021-5", "T.C. Memo. 2020-1"]
    assert ops[0]["topics"] == ["one", "two"]


def test_number_only_pieces_fold_into_the_next_paragraph():
    paras = [(3, "5."), (3, "are liable for additions to tax;"), (3, "$3,234"), (4, "Text."), (4, "12.")]
    assert caselaw.fold_numbers(paras) == [(3, "5. are liable for additions to tax;"), (4, "$3,234 Text."), (4, "12.")]