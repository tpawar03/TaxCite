"""When did a statute chunk's current text start to apply? Read from the USLM statutory notes (D4).

Two notes answer it together. The Amendments note says which provision each law changed
("Subsec. (b)(1). Pub. L. 119–21, § 70306(a)(1), substituted “$2,500,000” for “$1,000,000”"),
and the Effective Date of Amendment note says when that law applies ("§ 70306(c) ... shall apply
to property placed in service in taxable years beginning after December 31, 2024"). A section
added by a recent law has an Effective Date note of its own. The parser skips notes for the
chunk text (B2); this reads them only for dates.

Each chunk gets its latest amendment since MIN_YEAR, the rule quoted from the note, and the
entry itself (which often quotes the replaced text). A chunk nothing can be linked for gets no
date, never a guess: 66% of the 2,576 chunks amended since 2012 link, 48-49 of a fresh 50 right
by hand check after two rounds of fixes (tasks/todo.md D4).
"""

import re
import xml.etree.ElementTree as ET

from taxcite.chunk import Chunk

MIN_YEAR = 2012  # the years questions ask about; older amendments are history the corpus doesn't need
PL = r"Pub\. L\. (\d+)[–-](\d+)"
DATE = r"((?:Jan|Feb|Mar|Apr|May|June|July|Aug|Sept|Oct|Nov|Dec)[a-z]*\.? \d{1,2}, \d{4})"
RULE = re.compile(r"((?:shall )?(?:apply|applicable|effective)[^.;“”]*?(?:on or )?(?:after|before) " + DATE + r"[^.;“”]*)")


def tag(el) -> str:
    return el.tag.rsplit("}", 1)[-1]


def text(el) -> str:
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def notes(section, topic: str) -> list[str]:
    return [text(n) for n in section.iter() if tag(n) == "note" and n.get("topic") == topic]


def amendment_entries(section) -> list[tuple]:
    """(year, designations, law, (law section, its subsection), entry) from the Amendments note.
    No designations means the whole section."""
    out = []
    for note in notes(section, "amendments"):
        for ym in re.finditer(r"(\d{4})—(.*?)(?=\s\d{4}—|$)", note.removeprefix("Amendments")):
            year, block = int(ym.group(1)), ym.group(2)
            for e in re.split(r"(?=\b(?:Subsecs?|Pars?|Subpars?)\. \()", block):
                law = re.search(PL + r"(?:, (?:title [IVXL]+, )?(?:div\. [A-Z]+, )?(?:title [IVXL]+, )?"
                                     r"§ (\d+)((?:\([a-z0-9]+\))*))?", e)
                if not law:
                    continue
                whole = not re.match(r"Subsecs?|Pars?|Subpars?", e)
                if whole and "section catchline" in e and "subsec" not in e.lower():
                    continue  # a catchline rename changes no provision's text
                head = e.split(". Pub.")[0] if not whole else (re.search(r"in subsecs?\. (.*)", e) or [None, ""])[1]
                desig = re.findall(r"\(([a-z0-9]+)\)((?:\([A-Za-z0-9]+\))*)", head)
                for base, lo, hi in re.findall(r"\(([a-z])\)\((\d+)\) to \((\d+)\)", head):  # "(h)(4) to (6)"
                    desig += [(base, f"({n})") for n in range(int(lo), int(hi) + 1)]
                if whole and desig:
                    whole = False  # "wherever appearing ... in subsecs. (a)(4), (b)(4)(C)"
                sub = re.match(r"\(([a-z0-9]+)\)", law.group(4) or "")
                out.append((year, [] if whole else [f"({a}){b}" for a, b in desig],
                            f"{law.group(1)}-{law.group(2)}", (law.group(3), sub and sub.group(1)), e.strip()))
    return out


def clause_for(part: str, law_section: str, sub: str | None) -> str:
    """A note may give a general rule and exceptions for particular subsections of the law
    ("(2) ... amendments made by subsection (b)", ", amendment by section 70513(d) ... applicable
    ..."). Prefer the clause naming this amendment's own subsection, else the general one."""
    clauses = re.split(r"(?=“?\(\d\) )|(?=, except that )|(?=, amendment by section )|(?=\. Amendment by )", part)
    if sub:
        own = [c for c in clauses if f"subsection ({sub})" in c or f"{law_section}({sub})" in c]
        if own:
            return own[0]
        clauses = [c for c in clauses if not re.search(r"subsection \([a-z]\)|\d+\([a-z]\) of Pub", c)] or clauses
    return clauses[0] if clauses[0].strip() else part


def positive_rule(note: str):
    """The first '... apply ... after <date>' that isn't an exclusion ('not applicable to ...')."""
    for r in RULE.finditer(note):
        if not re.search(r"\bnot\s*$", note[max(0, r.start() - 12):r.start()]) and " not " not in r.group(1)[:25]:
            return r
    return None


def effective_rule(sections: dict, section, year: int, law: str, where, seen=()) -> dict | None:
    """The rule for the amendment by `law` in `year`, following 'note under section X' references."""
    law_section, sub = where if where else (None, None)
    for note in notes(section, "effectiveDateOfAmendment"):
        m = re.match(rf"Effective Date of {year} Amendments?", note)
        if not m:
            continue
        body = note[m.end():]
        for part in re.split(r"(?<=[.”])\s+(?=(?:Amendment|Amendments|Pub\. L\.))", body):
            if law not in {f"{a}-{b}" for a, b in re.findall(PL, part)}:
                continue
            nos = re.findall(r"§ (\d+)", part) + re.findall(r"section (\d+)", part)
            if law_section and nos and law_section not in nos and "by Pub." not in part[:40]:
                continue
            home = re.match(r"Pub\. L\. [^§]*§ (\d+)\(([a-z])\)", part)  # a rule in subsection (a) governs (a)
            if sub and home and home.group(1) == law_section and home.group(2) != sub and "this subsection" in part:
                continue
            if law_section:
                part = clause_for(part, law_section, sub)
            retro = "as if included" in part
            if r := positive_rule(part):
                return {"rule": r.group(1).strip(), "date": r.group(2), "retroactive": retro}
            if "date of the enactment" in part:
                d = re.search(DATE, part)
                return {"rule": "on or after the date of enactment", "date": d and d.group(1), "retroactive": retro}
            if retro:
                return {"rule": "as if included in an earlier law", "date": None, "retroactive": True}
            x = re.search(r"note under section ([\dA-Za-z-]+)", part)
            if x and x.group(1) in sections and x.group(1) not in seen:
                return effective_rule(sections, sections[x.group(1)], year, law, None, seen + (x.group(1),))
        x = re.search(r"note under section ([\dA-Za-z-]+)", body)
        if x and x.group(1) in sections and x.group(1) not in seen and len(body) < 120:
            return effective_rule(sections, sections[x.group(1)], year, law, None, seen + (x.group(1),))
    return None


def section_start(section) -> dict | None:
    """A section added since MIN_YEAR: 'Section applicable to taxable years beginning after Dec. 31, 2024'."""
    credit = next((text(e) for e in section if tag(e) == "sourceCredit"), "")
    m = re.match(r"\(Added " + PL + r".*?(\d{4}),", credit)
    if not m or int(m.group(3)) < MIN_YEAR:
        return None
    for note in notes(section, "effectiveDate"):
        if r := positive_rule(note):
            return {"year": int(m.group(3)), "rule": r.group(1).strip(), "date": r.group(2),
                    "retroactive": "as if included" in note, "amendment": "section added"}
    return None


def own_designation(citation: str) -> tuple[list[str], str | None]:
    """'26 U.S.C. § 179(b)(1)' -> (['b', '1'], None); '26 U.S.C. § 67(e)-(h)' -> (['e'], 'h')."""
    m = re.search(r"§ [\dA-Za-z-]+?((?:\([^)]+\))*)(?:-\(([^)]+)\))?$", citation)
    return re.findall(r"\(([^)]+)\)", m.group(1)), m.group(2)


def covers(chunk: Chunk, designation: str) -> bool:
    """Does the amendment of `designation` change this chunk? Same branch of the outline, and when the
    amendment reaches below the chunk's label the chunk must hold that sub-provision: the parts of one
    label (163(h)(3) #1-#3) carry different subparagraphs."""
    own, upto = own_designation(chunk.citation)
    d = re.findall(r"\(([^)]+)\)", designation)
    if not own:
        return True
    if upto:
        return len(own) == 1 and own[0] <= d[0] <= upto
    if not (d[:len(own)] == own or own[:len(d)] == d):
        return False
    if len(d) <= len(own):
        return True
    # the marker opens a line, or follows a heading ("Inflation adjustment. (A) In general"); a
    # cross-reference ("subparagraph (F)") is neither
    return re.search(r"(?:^|\n|\.\s)\(" + re.escape(d[len(own)]) + r"\) ", chunk.text) is not None


def evidenced(chunk: Chunk, entry: tuple) -> bool:
    """An entry that quotes what it put in ('substituted “X” for', 'inserted “X”') changed only the
    chunk that now contains X; a heading-only change, only the chunk that opens with that heading."""
    e = entry[4]
    norm = lambda s: re.sub(r"\s+", " ", s).replace("’", "'").lower()  # noqa: E731
    new = re.search(r"(?:substituted|inserted) “([^”]{6,})”", e)
    if new and not re.search(r"in (?:heading|section catchline)", e):
        return norm(new.group(1))[:40] in norm(chunk.text)
    if re.search(r"\bin heading\b", e) and entry[1]:
        return chunk.text.lstrip().startswith(f"({re.findall(r'[(]([^)]+)[)]', entry[1][0])[-1]})")
    return True


def link(root, chunks: list[Chunk]) -> dict[str, dict]:
    """chunk key -> {year, rule, date, retroactive, amendment} for chunks whose text changed since MIN_YEAR."""
    sections = {s.get("identifier").rsplit("/s", 1)[1]: s for s in root.iter()
                if tag(s) == "section" and re.fullmatch(r"/us/usc/t26/s[\dA-Za-z-]+", s.get("identifier") or "")}
    out = {}
    for c in chunks:
        section = sections.get(c.section)
        if c.excluded or section is None:
            continue
        hits = [e for e in amendment_entries(section) if e[0] >= MIN_YEAR
                and (not e[1] or any(covers(c, d) for d in e[1])) and evidenced(c, e)]
        if not hits:
            if start := section_start(section):
                out[c.key] = start
            continue
        year = max(e[0] for e in hits)
        latest = [e for e in hits if e[0] == year]
        rule = next((r for e in latest if (r := effective_rule(sections, section, year, e[2], e[3]))), None)
        if rule:
            out[c.key] = {"year": year, **rule, "amendment": latest[0][4][:600]}
    return out


if __name__ == "__main__":  # print the links for a section: python -m taxcite.ingest.usc_notes <xml> 179
    import sys

    from taxcite.ingest import usc

    xml = ET.parse(sys.argv[1]).getroot()
    for key, v in link(xml, [c for c in usc.parse(sys.argv[1]) if c.section == sys.argv[2]]).items():
        print(key, v["year"], v["rule"][:100])
