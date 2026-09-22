"""Ingest IRS publications (PDF).

Publications have no paragraph numbering to cut at, so chunking is a sliding
window over each page with overlap, cited to the page. Text comes from pdfminer
rather than pypdf: IRS publications are two-column, and pypdf either interleaves
the columns (layout mode) or breaks words mid-token ("Y ou do not meet"), which
would be embedded as-is.
"""

import re
import time
from collections import Counter
from pathlib import Path

import httpx
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

from taxcite.chunk import Chunk, estimate_tokens, renumber

# Pub 535 (Business Expenses) was discontinued after 2022: its URL now redirects to
# an HTML page. 946 and 527 replace it and match the pilot topics (depreciation,
# listed property, rental improvements).
PUBS = ("587", "463", "17", "334", "946", "527")
URL = "https://www.irs.gov/pub/irs-pdf/p{num}.pdf"
RAW_DIR = Path("data/pubs")
# identifies the client, as a courtesy scraper should; /pub is not disallowed by robots.txt
USER_AGENT = "TaxCite/0.1 (+https://github.com/tpawar03/TaxCite; research project)"
TARGET_TOKENS = 300
OVERLAP = 0.15
MIN_PAGE_WORDS = 20  # below this a page is treated as failed extraction, not content
BOILERPLATE_SHARE = 0.5  # a line on this share of pages is a header/footer, not content
EDGE_LINES = 3  # headers and footers live at the top or bottom of a page

# Print-shop artifacts from the IRS composition system. They appear on single pages
# and share lines with real text, so they are removed as spans rather than whole lines.
PRINT_ARTIFACTS = re.compile(
    r"Fileid:.*?source|Userid:\s*\w+|Schema:\s*\w+|Leadpct:\s*[\d.]+%|Pt\. size:\s*\d+"
    r"|Draft\s+Ok to Print|AH\s+XSL/XML|Init\.\s*&\s*Date|Page \d+ of \d+"
    r"|The type and rule above.{0,90}?printing\.|MUST be removed before printing\."
    r"|\d{1,2}:\d{2}\s*-\s*\d{1,2}-[A-Za-z]{3}-\d{4}",  # composition timestamp
    re.I | re.S,
)
YEAR_RE = re.compile(r"For use in preparing\s+(\d{4})\s+Returns")
# Publications put their title either after the number (587: "Publication 587
# Business Use of Your Home") or before it (17: "Your Federal Income Tax For
# Individuals Publication 17"), so both positions are tried.
TITLE_AFTER = re.compile(
    r"Publication\s+\d+[A-Z]?\s+(?!For use in|Get forms)(.{3,80}?)(?=\s+For use in|\s+Get forms|\s+•)")
TITLE_BEFORE = re.compile(r"([A-Z][^•]{5,80}?)\s+Publication\s+\d+[A-Z]?\s+(?:For use in|Get forms)")


def fetch(num: str, refresh: bool = False, delay: float = 2.0) -> Path:
    """Download one publication, cached on disk. `delay` rate-limits bulk fetches."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"p{num}.pdf"
    if path.exists() and not refresh:
        return path
    time.sleep(delay)
    with httpx.stream("GET", URL.format(num=num), headers={"User-Agent": USER_AGENT},
                      timeout=300, follow_redirects=True) as r:
        r.raise_for_status()
        with path.open("wb") as fh:
            for block in r.iter_bytes():
                fh.write(block)
    # A discontinued publication redirects to an HTML page and downloads with status
    # 200, so the content has to be checked rather than the status code.
    if path.read_bytes()[:5] != b"%PDF-":
        path.unlink()
        raise ValueError(f"publication {num} did not return a PDF — has it been discontinued or renumbered?")
    return path


def page_texts(path: Path) -> list[str]:
    return [
        "\n".join(el.get_text() for el in page if isinstance(el, LTTextContainer))
        for page in extract_pages(str(path))
    ]


def _normalise(line: str) -> str:
    return re.sub(r"\d+", "#", " ".join(line.split()))


def dehyphenate(page: str) -> str:
    """Join words split across a line break ("mo-\ntel" or "mo- tel" -> "motel").

    A hyphen followed by whitespace is a line-wrap artifact: genuine hyphenated
    terms ("self-employment") are written without a space, so they survive.
    """
    return re.sub(r"(\w)-\s+(\w)", r"\1\2", page)


def strip_boilerplate(pages: list[str], share: float = BOILERPLATE_SHARE) -> list[str]:
    """Drop lines that repeat across most pages at the top or bottom of the page.

    Generic rather than IRS-specific, so it works on any publication without a
    list of magic strings to maintain. Two guards keep it from eating content:
    digits are normalised (so "Page 3 of 35" matches "Page 4 of 35") but only
    lines near a page edge are candidates, because a table row that differs only
    by its numbers would otherwise look like a repeated header.
    """
    def edge_count(n: int) -> int:
        """How many lines at each end count as edges; never the whole page."""
        return EDGE_LINES if n > 2 * EDGE_LINES else 1

    def edges(page: str) -> list[str]:
        lines = [line for line in page.splitlines() if line.strip()]
        e = edge_count(len(lines))
        return lines[:e] + lines[-e:]

    counts = Counter(_normalise(line) for page in pages for line in edges(page))
    boiler = {line for line, n in counts.items() if n >= len(pages) * share}

    def clean(page: str) -> str:
        lines = [line for line in page.splitlines() if line.strip()]
        e = edge_count(len(lines))
        kept = [
            line for i, line in enumerate(lines)
            # the same text in the middle of a page is content, not a header
            if _normalise(line) not in boiler or e <= i < len(lines) - e
        ]
        return "\n".join(kept)

    return [clean(page) for page in pages]


def edition_year(first_page: str) -> str | None:
    match = YEAR_RE.search(" ".join(first_page.split()))
    return match.group(1) if match else None


def title_of(first_page: str, num: str) -> str:
    flat = " ".join(PRINT_ARTIFACTS.sub(" ", first_page).split())
    for pattern in (TITLE_AFTER, TITLE_BEFORE):
        if match := pattern.search(flat):
            return f"Publication {num} {match.group(1).strip()}"
    return f"Publication {num}"


def windows(words: list[str], size: int, overlap: float) -> list[list[str]]:
    """Sliding windows with overlap; a short page yields a single window."""
    if len(words) <= size:
        return [words]
    step = max(1, int(size * (1 - overlap)))
    out = [words[i:i + size] for i in range(0, len(words), step)]
    return [w for w in out if len(w) > size * overlap]  # drop a tail that is pure overlap


def parse(path: Path, num: str) -> list[Chunk]:
    """Every chunk in one publication PDF."""
    pages = [dehyphenate(PRINT_ARTIFACTS.sub(" ", p)) for p in strip_boilerplate(page_texts(path))]
    year = edition_year(pages[0]) if pages else None
    heading = title_of(pages[0], num) if pages else f"Publication {num}"
    as_of = f"{year}-01-01" if year else "1900-01-01"  # edition year, not a precise date
    label = f"IRS Pub {num} ({year})" if year else f"IRS Pub {num}"
    size = int(TARGET_TOKENS / 1.3)  # target is tokens; windows are counted in words

    chunks: list[Chunk] = []
    for page_no, page in enumerate(pages, 1):
        citation = f"{label}, p. {page_no}"
        words = page.split()
        if len(words) < MIN_PAGE_WORDS:
            chunks.append(Chunk(citation, f"Pub {num}", heading,
                                f"[page {page_no}: extraction produced {len(words)} words]",
                                0, None, as_of, excluded="extraction_failed", source="irs_pub"))
            continue
        for window in windows(words, size, OVERLAP):
            text = " ".join(window)
            chunks.append(Chunk(citation, f"Pub {num}", heading, text,
                                estimate_tokens(text), None, as_of, source="irs_pub"))
    return renumber(chunks)