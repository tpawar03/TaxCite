"""Tax Court opinions from DAWSON, the court's own system, into page-cited chunks.

DAWSON has no documented API. Its public web app calls the endpoints below, found
in its JavaScript bundle (B3); a changed response shape fails loudly rather than
indexing partial data. Requests are spaced and send an identifying User-Agent.

Opinions don't number their paragraphs; they are pin-cited by page ("at *12"), and
each page after the first opens with a "[*12]" marker. Chunks are cited the same way.
"""

import json
import re
import time
from collections import Counter
from pathlib import Path

import httpx
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTTextBox

from taxcite.chunk import Chunk, estimate_tokens, renumber
from taxcite.ingest.irs_pubs import USER_AGENT, dehyphenate

API = "https://public-api-green.dawson.ustaxcourt.gov/public-api"
RAW_DIR = Path("data/caselaw")
# DAWSON's search syntax: quotes for a phrase, + for AND
TOPICS = {
    "hobby loss (§183)": '"activity not engaged in for profit"',
    "trade or business (§162)": '"ordinary and necessary" + "trade or business"',
    "substantiation (§274(d))": '"274(d)"',
    "home office (§280A)": '"280A"',
    "material participation (§469)": '"material participation"',
    "constructive receipt (§451)": '"constructive receipt"',
    "worker classification (§7436)": '"independent contractor" + "7436"',
    "accuracy penalty (§6662)": '"6662"',
}
TYPES = "MOP,TCOP"  # memorandum and T.C. opinions; summary and bench opinions are nonprecedential
SINCE = "01/01/2000"
PER_TOPIC = 50  # the search has no relevance ranking, so this is the 50 newest
DELAY = 1.0  # seconds between API requests
CITE = re.compile(r"\d+ T\.C\. No\. \d+|T\.C\. Memo\. \d{4}-\d+")
MAX_TOKENS = 400  # §3.2: case law 150-400 tokens, one paragraph of overlap
MIN_WORDS = 200  # an opinion with less text than this is a failed extraction
PAGE_NUMBER = re.compile(r"^[-\s]*\d+[-\s]*$")  # "12" or "- 12 -"
SERVED = re.compile(r"^Served \d{2}/\d{2}/\d{2}$")  # the service stamp; larger than body text in 2026, smaller in 2021
STAR_PAGE = re.compile(r"^\[\*\d+\]\s*")
NUMERIC = re.compile(r"[\d\s$,.%()-]{1,40}")  # "5." split from its list item, or a table cell


def get(client: httpx.Client, path: str, **params) -> dict:
    time.sleep(DELAY)
    return client.get(API + path, params=params).raise_for_status().json()


def select(client: httpx.Client, per_topic: int = PER_TOPIC) -> list[dict]:
    """The newest `per_topic` distinct opinions for each topic.

    A consolidated case is listed once per docket, and a few memos are coded as
    T.C. opinions, so opinions are identified by the citation in their title.
    """
    chosen: dict[str, dict] = {}
    for topic, keyword in TOPICS.items():
        results = get(client, "/opinion-search", keyword=keyword, dateRange="customDates",
                      startDate=SINCE, opinionTypes=TYPES)["results"]
        taken = 0
        for r in sorted(results, key=lambda r: r["filingDate"], reverse=True):
            if taken == per_topic:
                break
            if not (m := CITE.search(r["documentTitle"])):
                continue
            op = chosen.setdefault(m.group(), {**r, "citation": m.group(), "topics": []})
            if topic not in op["topics"]:
                op["topics"].append(topic)
                taken += 1
    return list(chosen.values())


def load_selection(refresh: bool = False) -> list[dict]:
    """The selection is cached so the corpus stays fixed while new opinions are filed."""
    path = RAW_DIR / "opinions.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=60) as client:
        ops = select(client)
    path.write_text(json.dumps(ops, indent=1))
    return ops


def fetch(op: dict, client: httpx.Client) -> Path:
    """One opinion's PDF, cached. DAWSON hands out a short-lived signed S3 link."""
    path = RAW_DIR / "pdf" / f"{op['docketEntryId']}.pdf"
    if path.exists():
        return path
    url = get(client, f"/{op['docketNumber']}/{op['docketEntryId']}/public-document-download-url")["url"]
    pdf = httpx.get(url, timeout=120).raise_for_status().content
    if not pdf.startswith(b"%PDF"):  # an error page can arrive with status 200
        raise ValueError(f"{op['citation']}: download is not a PDF")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pdf)
    return path


def font_size(box: LTTextBox) -> float:
    sizes = Counter(round(ch.size) for line in box for ch in line if isinstance(ch, LTChar))
    return sizes.most_common(1)[0][0] if sizes else 0


def paragraphs(path: Path) -> list[tuple[int, str]]:
    """(page, text) for each paragraph, in reading order.

    Body text is the opinion's most common font size, one text box per paragraph
    (one per line in pre-2010 layouts, so their "paragraphs" are lines). Larger text
    is the masthead; page numbers and the "Served" stamp are dropped by pattern,
    because the stamp's size varies by year. Smaller text is footnotes or
    table cells; footnotes sit below a page's last paragraph and are kept as one
    block per page, while table cells arrive scattered one per box and are dropped.
    """
    pages = [[(b, font_size(b), " ".join(b.get_text().split())) for b in page if isinstance(b, LTTextBox)]
             for page in extract_pages(path)]
    weights = Counter()
    for boxes in pages:
        for _, size, text in boxes:
            weights[size] += len(text)
    body = weights.most_common(1)[0][0] if weights else 0

    pages = [[(b, s, t) for b, s, t in boxes if t and not PAGE_NUMBER.match(t) and not SERVED.match(t)] for boxes in pages]
    out: list[tuple[int, str]] = []
    for number, boxes in enumerate(pages, 1):
        main = [(b, t) for b, s, t in boxes if s == body]
        bottom = min((b.y0 for b, _ in main), default=0)
        notes = " ".join(t for b, s, t in sorted(boxes, key=lambda x: -x[0].y1) if s < body and b.y1 <= bottom)
        for _, text in sorted(main, key=lambda x: -x[0].y1):
            out.append((number, dehyphenate(STAR_PAGE.sub("", text))))
        if notes:
            out.append((number, dehyphenate(notes)))
    return fold_numbers(out)


def fold_numbers(paras: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Prefix number-only pieces to the paragraph after them: a list number rejoins its
    item, and a table figure stays searchable without becoming a paragraph (and so an
    overlap unit) of its own. ~3,800 such pieces across the 307 opinions."""
    out: list[tuple[int, str]] = []
    pending: list[str] = []
    for page, text in paras:
        if NUMERIC.fullmatch(text):
            pending.append(text)
            continue
        out.append((page, " ".join(pending + [text])))
        pending = []
    if pending:
        out.append((paras[-1][0], " ".join(pending)))
    return out


def pages_label(first: int, last: int) -> str:
    return f"at *{first}" if first == last else f"at *{first}-{last}"


def parse(path: Path, op: dict) -> list[Chunk]:
    """Paragraphs packed up to MAX_TOKENS, each chunk opening with the previous chunk's
    last paragraph (§3.2), so a reference like "that test" keeps its antecedent."""
    cite = op["citation"]
    caption = re.sub(r",? Petitioners?$", "", op["caseCaption"]) + " v. Commissioner"
    filed = op["filingDate"][:10]

    def make(label: str, text: str, excluded: str | None = None) -> Chunk:
        return Chunk(label, cite, caption, text, estimate_tokens(text), None, filed, excluded, source="case")

    paras = paragraphs(path)
    if sum(len(t.split()) for _, t in paras) < MIN_WORDS:
        return [make(cite, "", excluded="no_text")]

    chunks: list[Chunk] = []
    start = 0
    while start < len(paras):
        end = start + 1
        while end < len(paras) and estimate_tokens(" ".join(t for _, t in paras[start:end + 1])) <= MAX_TOKENS:
            end += 1
        chunk = paras[start:end]
        chunks.append(make(f"{cite}, {pages_label(chunk[0][0], chunk[-1][0])}", "\n".join(t for _, t in chunk)))
        if end == len(paras):
            break
        start = end - 1 if end - start > 1 else end  # overlap one paragraph, but always move forward
    return renumber(chunks)