"""Parse eCFR Title 26 XML into citation-anchored chunks.
"""

import re
import xml.etree.ElementTree as ET

from taxcite.chunk import Chunk, estimate_tokens, renumber

MAX_TOKENS = 500
MAX_TABLE_CELLS = 100
META_TAGS = {"CITA", "SECAUTH", "EDNOTE", "AUTH", "SOURCE", "APPRO", "HEAD"}
TEXT_TAGS = {"P", "PSPACE", "FP", "HED", "HD1", "HD2", "HD3", "NOTE", "FTNT", "LI"}
DESIGNATION = re.compile(r"\s*\(([A-Za-z0-9]+)\)")
EMBEDDED_L2 = re.compile(r"^[^(]{0,5}\((\d+)\)")
RESERVED = re.compile(r"\[Reserved\]", re.I)


from dataclasses import dataclass


@dataclass
class Block:
    text: str
    l1: str | None = None  # level-1 designation this block opens, e.g. "a"
    l2: str | None = None  # level-2 designation, e.g. "1"


def clean(el) -> str:
    return re.sub(r"\s+", " ", " ".join(el.itertext())).strip()


def level_of(token: str, prev_l1: str | None) -> int | None:
    """1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.

    `(i)`, `(v)` and `(x)` are both letters and Roman numerals; they are only
    level-1 letters when they follow the preceding letter of the alphabet.
    """
    if token.isdigit():
        return 2
    if len(token) == 1 and token.islower():
        if token in "ivx":
            return 1 if prev_l1 and ord(token) == ord(prev_l1) + 1 else None
        return 1
    return None


def designations(p, prev_l1: str | None) -> tuple[str | None, str | None]:
    """Level-1 and level-2 designations a paragraph opens with.

    Read from raw text, never from itertext(), so italic designations like
    `(<I>2</I>)` (a level-5 marker) are not mistaken for level 2.
    """
    l1 = l2 = None
    rest = p.text or ""
    while (m := DESIGNATION.match(rest)) and (l1 is None or l2 is None):
        level = level_of(m.group(1), prev_l1)
        if level == 1 and l1 is None and l2 is None:
            l1 = m.group(1)
        elif level == 2 and l2 is None:
            l2 = m.group(1)
        else:
            break
        rest = rest[m.end():]
    # "(a) <I>Heading.</I> (1) ..." — the (1) sits in the italic element's tail
    if l1 and not l2 and len(p) and p[0].tag == "I" and (tail := p[0].tail):
        if m := EMBEDDED_L2.match(tail):
            l2 = m.group(1)
    return l1, l2


def table_block(table) -> Block | None:
    """A small table as pipe-joined rows; None when it is too large to embed."""
    if sum(1 for c in table.iter() if c.tag in ("TD", "TH")) > MAX_TABLE_CELLS:
        return None
    rows = [
        " | ".join(clean(c) for c in tr if c.tag in ("TD", "TH"))
        for tr in table.iter("TR")
    ]
    return Block(text="\n".join(r for r in rows if r.strip()))


def blocks(section) -> tuple[list[Block], list[int]]:
    """Ordered text blocks of a section, plus the cell count of each oversized table."""
    out: list[Block] = []
    oversized: list[int] = []
    prev_l1: str | None = None

    def walk(el):
        nonlocal prev_l1
        if el.tag in META_TAGS:
            return
        if el.tag == "TABLE":
            if (block := table_block(el)) is None:
                oversized.append(sum(1 for c in el.iter() if c.tag in ("TD", "TH")))
            elif block.text:
                out.append(block)
            return
        if el.tag == "EXTRACT":
            # quoted matter and in-section outlines: keep the text, but never read
            # designations from it — §1.61-21's outline repeats every (a)(1) heading
            # and would otherwise restart the numbering mid-section
            if (text := clean(el)) and not RESERVED.search(text):
                out.append(Block(text=text))
            return
        if el.tag in TEXT_TAGS:
            text = clean(el)
            if not text or RESERVED.search(text):
                return
            l1, l2 = designations(el, prev_l1) if el.tag == "P" else (None, None)
            if l1:
                prev_l1 = l1
            out.append(Block(text=text, l1=l1, l2=l2))
            return
        for child in el:
            walk(child)

    for child in section:
        walk(child)
    return out, oversized


def units(blocks_: list[Block], key: str) -> list[list[Block]]:
    """Split blocks into units, starting a new one wherever `key` is set."""
    grouped: list[list[Block]] = []
    for b in blocks_:
        if getattr(b, key) or not grouped:
            grouped.append([b])
        else:
            grouped[-1].append(b)
    return grouped


def cite(section: str, first: str | None, last: str | None = None, l2: str | None = None,
         prefix: str = "26 CFR") -> str:
    ref = f"{prefix} {section}"
    if first:
        ref += f"({first})"
        if last and last != first:
            ref += f"-({last})"
        elif l2:
            ref += f"({l2})"
    return ref


def split_blocks(blocks_: list[Block], label: str) -> list[tuple[str, str, int]]:
    """Blocks packed into numbered parts under one citation."""
    parts: list[str] = []
    buf: list[str] = []
    for b in blocks_:
        if buf and estimate_tokens("\n".join(buf + [b.text])) > MAX_TOKENS:
            parts.append("\n".join(buf))
            buf = []
        buf.append(b.text)
    if buf:
        parts.append("\n".join(buf))
    return [(label, text, i) for i, text in enumerate(parts, 1)]


def split_unit(unit: list[Block], section: str, prefix: str = "26 CFR") -> list[tuple[str, str, int]]:
    """An oversized level-1 unit, split at level 2 and then at block boundaries."""
    out = []
    for sub in units(unit, "l2"):
        label = cite(section, sub[0].l1 or unit[0].l1, l2=sub[0].l2, prefix=prefix)
        out += split_blocks(sub, label)
    return out


def chunk_section(section, as_of: str, source: str = "ecfr") -> list[Chunk]:
    number = section.get("N")
    heading = (section.findtext("HEAD") or "").strip()
    cita_el = section.find("CITA")
    cita = clean(cita_el) if cita_el is not None else None

    def make(citation: str, text: str, excluded: str | None = None, part: int = 1) -> Chunk:
        return Chunk(citation, number, heading, text, estimate_tokens(text), cita, as_of, excluded, part, source)

    if RESERVED.search(heading):
        return []
    if "table of contents" in heading.lower():
        return [make(cite(number, None), "", excluded="toc")]

    body, oversized = blocks(section)
    chunks = [
        make(cite(number, None), f"[table omitted: {cells} cells, over the {MAX_TABLE_CELLS}-cell limit]",
             excluded="large_table", part=i)
        for i, cells in enumerate(oversized, 1)
    ]
    chunks.extend(make(lbl, text, part=i) for lbl, text, i in pack(body, number))
    return renumber(chunks)


def pack(body: list[Block], section: str, prefix: str = "26 CFR") -> list[tuple[str, str, int]]:
    """Level-1 units packed up to MAX_TOKENS; an oversized one is split at level 2.
    Shared with the US Code parser, which only differs in the citation prefix."""
    out: list[tuple[str, str, int]] = []
    packed: list[Block] = []
    last: str | None = None  # the last packed *unit's* designation; its trailing blocks carry none

    def flush() -> None:
        nonlocal packed
        if packed:
            out.extend(split_blocks(packed, cite(section, packed[0].l1, last, prefix=prefix)))
            packed = []

    for unit in units(body, "l1"):
        if unit[0].l1 is None:  # preamble: never packs with a designated unit
            flush()
            out.extend(split_blocks(unit, cite(section, None, prefix=prefix)))
            continue
        if estimate_tokens("\n".join(b.text for b in unit)) > MAX_TOKENS:
            flush()
            out.extend(split_unit(unit, section, prefix))
            continue
        if packed and estimate_tokens("\n".join(b.text for b in packed + unit)) > MAX_TOKENS:
            flush()
        packed += unit
        last = unit[0].l1
    flush()
    return out


def in_scope(section: str, prefixes: tuple[str, ...] | list[str]) -> bool:
    """True when a section is one of these prefixes, or a numbered child of one.

    Boundary-aware on purpose: "1.61" (gross income) must match 1.61-1 and
    1.61(a)-1 but not 1.611-1, which is depletion and a different topic.
    """
    return any(section == p or section.startswith(p + "-") or section.startswith(p + "(") for p in prefixes)


def parse(xml, as_of: str, source: str = "ecfr") -> list[Chunk]:
    """Every chunk in an eCFR XML file or element tree."""
    root = xml if isinstance(xml, ET.Element) else ET.parse(xml).getroot()
    sections = (d for d in root.iter("DIV8") if d.get("TYPE") == "SECTION")
    return [c for s in sections for c in chunk_section(s, as_of, source)]