"""The unit every ingester produces and every store consumes."""

from collections import Counter
from dataclasses import dataclass


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
    source: str = "ecfr"  # which corpus this came from; IRS publications use "irs_pub"

    @property
    def key(self) -> str:
        """Stable primary key. A citation alone is not unique: one citation can
        need several parts, and a skipped table shares its section's citation."""
        return f"{self.citation}#{self.excluded or 'body'}#{self.part}"


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