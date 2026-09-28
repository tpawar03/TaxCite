"""The unit every ingester produces and every store consumes."""

import re
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime

REPORTED = re.compile(r"\d+ T\.C\. No\. \d+")
MEMO = re.compile(r"T\.C\. Memo\. \d{4}-\d+")
# A temporary regulation can date its own end, for the whole section ("The applicability of this section
# expires on December 6, 2019") or for named paragraphs ("The applicability of paragraph (g)(4) of this
# section ... expires May 7, 2018"). Pre-1988 temporary regulations carry no such clause and stay in force.
EXPIRES = re.compile(r"applicability of (this section|paragraphs?\b.*?) expires (?:on )?(?:or before )?"
                     r"([A-Z][a-z]+ \d{1,2}, \d{4})")


@dataclass
class Chunk:
    citation: str
    section: str
    heading: str
    text: str
    tokens: int
    cita: str | None
    as_of: str
    excluded: str | None = None
    part: int = 1  # 1-based index when one citation needs more than one chunk
    source: str = "ecfr"  # which corpus this came from: "ecfr", "irs_pub", "usc", "case"
    source_revision: str | None = None  # upstream version, e.g. the US Code release point "Pub. L. 119-110"
    effective: dict | None = None  # statute only (D4): when this text's latest amendment applies, from the notes

    @property
    def key(self) -> str:
        """Stable primary key. A citation alone is not unique: one citation can
        need several parts, and a skipped table shares its section's citation."""
        return f"{self.citation}#{self.excluded or 'body'}#{self.part}"


def authority(source: str, citation: str, section: str, partly_expired: bool = False) -> dict:
    """The chunk's authority profile (E2): from its source and the citation's form, never from what the
    text claims about itself (ADR-13), so a document can't promote itself. Statute and regulation share a
    level on purpose; which should rank first is measured in E4, not decided here. Unknown is 0 and is
    counted where it's stored, never defaulted to a safe level (FR-16)."""
    if source == "usc":
        kind, status, level = "statute", "enacted", 4
    elif source == "ecfr":
        kind, level = "regulation", 4
        status = ("temporary_partly_expired" if partly_expired else "temporary") if section.endswith("T") else "final"
    elif source == "case" and REPORTED.search(citation):
        kind, status, level = "opinion", "reported", 3
    elif source == "case" and MEMO.search(citation):
        kind, status, level = "opinion", "memorandum", 2
    elif source == "irs_pub":
        kind, status, level = "publication", "not_binding", 1
    else:
        kind, status, level = "unknown", "unknown", 0
    return {"type": kind, "status": status, "level": level}


def revision(source: str, as_of) -> str | None:
    """`source_revision` where the ingester had none (E2): what `as_of` already records, labelled.
    The statute's release point is set by its own ingester."""
    as_of = str(as_of)
    if source == "ecfr":
        return f"eCFR {as_of}"
    if source == "case":
        return f"filed {as_of}"
    if source == "irs_pub" and as_of > "1900-01-01":  # 1900-01-01 marks an edition year that couldn't be read
        return f"{as_of[:4]} edition"
    return None


def expiry(text: str, as_of) -> str | None:
    """'whole' or 'partly' when a regulation's own clause says its applicability ended before `as_of`
    (the snapshot's date, not today's, so a re-run of an old snapshot gives the same answer)."""
    found = None
    for m in EXPIRES.finditer(text):
        if datetime.strptime(m.group(2), "%B %d, %Y").date() < date.fromisoformat(str(as_of)):
            if m.group(1) == "this section":
                return "whole"
            found = "partly"
    return found


def estimate_tokens(text: str) -> int:
    return round(len(text.split()) * 1.3)


def renumber(chunks: list[Chunk]) -> list[Chunk]:
    """Make `part` a running count per citation, so `key` is unique by construction.

    Splitting already numbers its own pieces, but a document can legitimately reach
    the same citation twice (quoted matter, outlines, restarted numbering, a page
    that yields several windows). Without this, two chunks share a key and the
    second silently overwrites the first.
    """
    seen: Counter[tuple[str, str | None]] = Counter()
    for c in chunks:
        seen[(c.citation, c.excluded)] += 1
        c.part = seen[(c.citation, c.excluded)]
    return chunks