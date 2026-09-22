"""Parse US Code Title 26 (USLM XML from uscode.house.gov) into citation-anchored chunks.

USLM marks every subsection and paragraph as its own element with an identifier,
so unlike eCFR there are no designations to infer from text. Packing and splitting
reuse the eCFR rules (`ecfr.pack`): level 1 is a section's top provisions (usually
subsections, sometimes paragraphs, as in §212), level 2 is their children.
"""

import re
import xml.etree.ElementTree as ET

from taxcite.chunk import Chunk, estimate_tokens, renumber
from taxcite.ingest.ecfr import Block, pack

PREFIX = "26 U.S.C. §"
SECTION_ID = "/us/usc/t26/s"  # sections quoted inside notes carry no identifier, so this skips them
PROVISIONS = {"subsection", "paragraph", "subparagraph", "clause", "subclause", "item", "subitem", "level"}
SKIP = {"num", "heading", "notes", "sourceCredit"}


def tag(el) -> str:
    return el.tag.rsplit("}", 1)[-1]


def text_of(el) -> str:
    """Text with whitespace collapsed. A table becomes one line per row; the largest
    table in Title 26's text has 86 cells, so none needs eCFR's large-table exclusion."""
    if tag(el) == "table":
        rows = (" | ".join(text_of(c).strip() for c in tr if tag(c) in ("td", "th"))
                for tr in el.iter() if tag(tr) == "tr")
        return "\n" + "\n".join(r for r in rows if r.strip()) + "\n"
    norm = lambda s: re.sub(r"\s+", " ", s or "")
    return norm(el.text) + "".join(text_of(c) + norm(c.tail) for c in el)


def clean(text: str) -> str:
    return "\n".join(re.sub(" {2,}", " ", line).strip() for line in text.split("\n") if line.strip())


def child_text(el, name: str) -> str:
    found = next((c for c in el if tag(c) == name), None)
    return clean(text_of(found)) if found is not None else ""


def designation(el) -> str:
    """'b' for /us/usc/t26/s183/b."""
    return el.get("identifier", "").rsplit("/", 1)[-1] or child_text(el, "num").strip("().")


def lead_in(lead: str, first: Block, l1: str | None = None, l2: str | None = None) -> Block:
    """Fold a lead-in into the block it introduces.

    Statute text leans on chapeaus: "…shall be allowed as a deduction all expenses—"
    followed by "(1) for the production of income". Split apart, the chapeau means
    nothing and the paragraph has no verb, and a bare heading like "(d) Definitions."
    would become a 12-token chunk. The merged block opens both levels, like eCFR's
    "(a) Heading. (1) …", so it is cited (d)(1).
    """
    return Block(clean(f"{lead} {first.text}"), l1=first.l1 or l1, l2=first.l2 or l2)


def provision_blocks(el, level: int) -> list[Block]:
    """A provision's own text (designation, heading, text before its first child) tagged
    with its level and folded into its first child, then the rest in order."""
    if el.get("status") or child_text(el, "num").startswith("["):
        return []  # "[(24) Repealed. Pub. L. 113–295 …]": a stub, like eCFR's [Reserved]
    d = designation(el)
    tags = {"l1": d} if level == 1 else {"l2": d} if level == 2 else {}
    heading = child_text(el, "heading")
    buf = [child_text(el, "num") + (f" {heading.rstrip('.')}." if heading else "")]
    out: list[Block] = []

    for c in el:
        if tag(c) in PROVISIONS:
            kids = provision_blocks(c, level + 1)
            lead = clean(" ".join(buf))
            if lead and not out and kids:
                kids[0] = lead_in(lead, kids[0], **tags)
            elif lead:
                out.append(Block(lead, **(tags if not out else {})))
            out.extend(kids)
            buf.clear()
        elif tag(c) not in SKIP:
            buf.append(text_of(c))
    if text := clean(" ".join(buf)):  # text after the children, e.g. a continuation
        out.append(Block(text, **(tags if not out else {})))
    return out


def blocks(section) -> list[Block]:
    out: list[Block] = []
    lead: list[str] = []  # a section's chapeau, folded into its first provision
    for c in section:
        if tag(c) in PROVISIONS:
            kids = provision_blocks(c, 1)
            if lead and kids:
                kids[0] = lead_in(" ".join(lead), kids[0])
                lead = []
            out.extend(kids)
        elif tag(c) not in SKIP and (text := clean(text_of(c))):
            if out:
                out.append(Block(text))  # a section-level continuation
            else:
                lead.append(text)
    return out + [Block(t) for t in lead]  # a section with no provisions is all lead


def chunk_section(section, as_of: str, revision: str | None) -> list[Chunk]:
    # USLM writes "1400Z–2" with an en dash; citations use a hyphen
    number = section.get("identifier").removeprefix(SECTION_ID).replace("–", "-")
    heading = child_text(section, "heading")
    cita = child_text(section, "sourceCredit") or None

    def make(citation: str, text: str, excluded: str | None = None, part: int = 1) -> Chunk:
        return Chunk(citation, number, heading, text, estimate_tokens(text), cita, as_of, excluded, part,
                     source="usc", source_revision=revision)

    if status := section.get("status"):  # repealed, renumbered, reserved, omitted
        return [make(f"{PREFIX} {number}", "", excluded=status)]
    return renumber([make(label, text, part=i) for label, text, i in pack(blocks(section), number, PREFIX)])


def parse(xml) -> list[Chunk]:
    """Every chunk in a Title 26 USLM file or element tree.

    as_of is the release point's creation date; source_revision is the Public Law
    the release point is current through ("Online@119-110" -> "Pub. L. 119-110").
    """
    root = xml if isinstance(xml, ET.Element) else ET.parse(xml).getroot()
    meta = {tag(c): (c.text or "").strip() for e in root.iter() if tag(e) == "meta" for c in e}
    as_of = meta.get("created", "")[:10]
    point = meta.get("docPublicationName", "").partition("@")[2]
    revision = f"Pub. L. {point}" if point else None
    sections = (e for e in root.iter() if tag(e) == "section" and e.get("identifier", "").startswith(SECTION_ID))
    return [c for s in sections for c in chunk_section(s, as_of, revision)]