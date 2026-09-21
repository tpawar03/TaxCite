"""Publication chunking: pure functions tested on text, no PDF needed."""

from pathlib import Path

import pytest

from taxcite.ingest.irs_pubs import (
    PRINT_ARTIFACTS, dehyphenate, edition_year, parse, strip_boilerplate, title_of, windows,
)

PDF = Path("data/pubs/p587.pdf")


def page(n: int) -> str:
    """A page shaped like a real one: header lines, body, footer."""
    letter = chr(64 + n)
    return "\n".join([
        f"Page {n} of 3", "Printed header",
        f"Intro paragraph {letter}", "Line 6 amount", "Line 7 amount", f"Closing paragraph {letter}",
        "IRS.gov footer",
    ])


def test_dehyphenate_joins_line_wrapped_words():
    assert dehyphenate("mo-\ntel") == "motel"
    assert dehyphenate("Is- lands") == "Islands"


def test_dehyphenate_keeps_real_hyphens():
    assert dehyphenate("self-employment tax") == "self-employment tax"
    assert dehyphenate("call 1-800-829-3676") == "call 1-800-829-3676"


def test_strip_boilerplate_drops_repeated_headers_and_footers():
    cleaned = strip_boilerplate([page(i) for i in range(1, 4)])
    assert all("Printed header" not in c and "IRS.gov footer" not in c for c in cleaned)
    assert all("Page" not in c for c in cleaned)


def test_strip_boilerplate_keeps_the_body():
    cleaned = strip_boilerplate([page(i) for i in range(1, 4)])
    assert all(f"Intro paragraph {chr(64 + i)}" in cleaned[i - 1] for i in range(1, 4))


def test_strip_boilerplate_keeps_mid_page_rows_that_differ_only_by_numbers():
    """A table row like "Line 6 amount" must survive digit-normalised matching."""
    cleaned = strip_boilerplate([page(i) for i in range(1, 4)])
    assert all("Line 6 amount" in c for c in cleaned)


def test_short_pages_never_lose_everything():
    """Edges must never cover the whole page, or a 5-line page is deleted entirely."""
    pages = ["Header\nreal body text\nFooter"] * 3
    assert all("real body text" in c for c in strip_boilerplate(pages))


def test_strip_boilerplate_keeps_lines_seen_once():
    pages = [page(i) for i in range(1, 4)]
    pages[0] = pages[0].replace("Intro paragraph A", "a line only page one has")
    assert "a line only page one has" in strip_boilerplate(pages)[0]


def test_print_artifacts_are_recognised():
    assert PRINT_ARTIFACTS.sub("", "Userid: CPM Schema: tipx Pt. size: 10 real text").strip() == "real text"
    assert PRINT_ARTIFACTS.sub("", "MUST be removed before printing. real text").strip() == "real text"
    assert PRINT_ARTIFACTS.sub("", "13:01 - 27-Feb-2026 real text").strip() == "real text"


def test_edition_year_and_title():
    first = "Publication 587 Business Use of Your Home For use in preparing 2025 Returns"
    assert edition_year(first) == "2025"
    assert title_of(first, "587") == "Publication 587 Business Use of Your Home"


def test_title_when_it_precedes_the_number():
    """Pub 17 prints its title before the number, unlike Pub 587."""
    first = "Your Federal Income Tax For Individuals Publication 17 For use in preparing 2025 Returns"
    assert title_of(first, "17") == "Publication 17 Your Federal Income Tax For Individuals"


def test_title_without_a_for_use_in_line():
    """Pub 946 has no edition line; the bullet list ends the title."""
    first = "Publication 946 How To Depreciate Property • Section 179 Deduction • MACRS"
    assert title_of(first, "946") == "Publication 946 How To Depreciate Property"


def test_title_falls_back_to_the_number():
    assert title_of("no recognisable title here", "463") == "Publication 463"


def test_windows_overlap_and_cover_everything():
    words = [str(i) for i in range(500)]
    got = windows(words, 200, 0.15)
    assert len(got) > 1
    assert got[1][0] == words[170]  # each window advances by 85% of its size
    assert got[1][:30] == got[0][-30:]  # and overlaps the previous one
    assert words[-1] in got[-1]  # nothing dropped off the end


def test_short_page_is_one_window():
    words = ["a", "b", "c"]
    assert windows(words, 200, 0.15) == [words]


def test_fetch_rejects_a_non_pdf(tmp_path, monkeypatch):
    """A discontinued publication redirects to HTML and still returns HTTP 200."""
    import taxcite.ingest.irs_pubs as mod

    class FakeStream:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def raise_for_status(self): pass
        def iter_bytes(self): yield b"<!DOCTYPE html><html>not a pdf</html>"

    monkeypatch.setattr(mod, "RAW_DIR", tmp_path)
    monkeypatch.setattr(mod.httpx, "stream", lambda *a, **k: FakeStream())
    with pytest.raises(ValueError, match="did not return a PDF"):
        mod.fetch("535", delay=0)
    assert not (tmp_path / "p535.pdf").exists()  # the bad file is not left behind


@pytest.mark.skipif(not PDF.exists(), reason="run `taxcite ingest irs-pubs --skip-index` first")
def test_real_publication_parses_into_cited_pages():
    chunks = parse(PDF, "587")
    assert len(chunks) > 50
    assert all(c.source == "irs_pub" for c in chunks)
    assert all(c.citation.startswith("IRS Pub 587 (20") for c in chunks)
    assert len({c.key for c in chunks}) == len(chunks)
    assert any("exclusive use" in c.text for c in chunks)