"""Citation and treatment edges between Tax Court opinions: two Postgres tables, no graph store (ADR-23).

citations   which held opinion cites which Tax Court opinion, extracted with eyecite from the case chunks
treatments  what happened to an opinion later, one row per source (C1):
            - "corpus": subsequent history in our own opinions ("X, rev'd, Y" / "Y, aff'g X", "X is overruled")
            - "courtlistener": the appeal found by name, its outcome read from the appellate opinion's
              closing sentence. Held opinions with no appeal found get kind "none", so their check date is kept.

Sources are stored side by side and merged when read (C4): CourtListener first, and where the two
disagree the flag is "unknown". A missing row is never "good law". Both loads are idempotent.
"""

import json
import logging
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
from eyecite import get_citations
from eyecite.models import FullCaseCitation

from taxcite.ingest.caselaw import load_selection
from taxcite.ingest.irs_pubs import USER_AGENT

# eyecite warns on every overlapping cite it can't classify (thousands in this corpus); none affect a Tax Court key
logging.getLogger("eyecite").setLevel(logging.ERROR)

API = "https://www.courtlistener.com/api/rest/v4"
RAW_DIR = Path("data/courtlistener")
DELAY = 7.0  # the keyed API allows 10 requests a minute, on a rolling window (C1)
COURTS = "ca1 ca2 ca3 ca4 ca5 ca6 ca7 ca8 ca9 ca10 ca11 cadc cafc"
APPEAL_YEARS = 5  # an appeal decided later than this is another case with the same name (C1)
RECHECK_YEARS = 3  # a decided appeal stays decided: only recent opinions can still change
LINEBREAK = re.compile(r"(\d{4})- (\d)")  # "T.C. Memo. 1997- 553": a PDF line break inside the cite

# Reported T.C. opinions are cited by volume and page but keyed by slip number. Matched by surname
# and checked by hand in C0; 10 of the 28 held T.C. opinions are cited by another held opinion.
# ponytail: hand table; if more T.C. opinions are ingested, take the reported cite from CourtListener's cluster
ALIAS = {
    "116 T.C. 450": "116 T.C. No. 29", "117 T.C. 263": "117 T.C. No. 22", "119 T.C. 121": "119 T.C. No. 5",
    "121 T.C. 89": "121 T.C. No. 6", "123 T.C. 64": "123 T.C. No. 4", "131 T.C. 185": "131 T.C. No. 11",
    "135 T.C. 365": "135 T.C. No. 18", "136 T.C. 120": "136 T.C. No. 6", "139 T.C. 396": "139 T.C. No. 16",
    "161 T.C. 77": "161 T.C. No. 6",
}
# Courts that can affirm or reverse the Tax Court. A B.T.A. or T.C. cite after "aff'd" is something else (C1).
APPELLATE = {"U.S.", "S. Ct.", "L. Ed. 2d", "F.", "F.2d", "F.3d", "F.4th", "F. App'x", "F. App’x", "Fed. Appx.",
             "WL", "U.S. Tax Cas. (CCH)", "A.F.T.R.2d (RIA)", "A.F.T.R.3d (RIA)", "U.S. App. D.C."}
# "X, rev'd, Y". The window can't cross a sentence: "X (1978). We have also vacated a decision…" is prose (C3 #33).
AFTER = re.compile(r"^(?:(?!\. (?-i:[A-Z]))[^;]){0,40}?\b(aff[’']?d|affd\.|rev[’']?d|revd\.|vacated)\b(?P<part>\s+in\s+part)?", re.I)
BEFORE = re.compile(r"\b(aff[’']?g|affg\.|rev[’']?g|revg\.|vacating)\b(?P<part>\s+in\s+part)?[^;]{0,30}$", re.I)  # Y, rev'g X
HISTORY = re.compile(r"\b(aff[’']?[dg]|aff[dg]\.|rev[’']?[dg]|rev[dg]\.|vacat)", re.I)
# Parallel cites of the same opinion sit between it and its history: "T.C. Memo. 2007-368, 2007 WL 4410771, at *19, aff'd"
PARALLEL = {"T.C.M. (CCH)", "T.C.M. (RIA)", "T.C.M. (P-H)", "P-H Memo T.C.", "Tax Ct. Memo LEXIS", "WL"}
# Between an appeal and "aff'g X" only pin cites and balanced parentheticals ("(6th Cir. 1995) (captive insurance)")
# may appear. Anything else means the cite eyecite found isn't the appeal, e.g. a 1944 Supreme Court cite before
# a garbled "…))). 72, 73–74 (9th Cir. 1996)" (C3 #56).
GAP = re.compile(r"[\s,\d–\-*n.]*(\([^()]*\)[\s,]*)*")
PARENS = re.compile(r"\([^()]*\)")
OVERRULED_AFTER = re.compile(r"^[^;]{0,120}?\bis\s+overruled\b", re.I)  # "Wuebker…, 110 T.C. 431 (1998), rev'd, 205 F.3d 897 (…), is overruled"
OVERRULE_BEFORE = re.compile(r"\bwe\s+overrule\b[^;]{0,60}$", re.I)  # "we overrule our holding in Wuebker v. …"
# The disposition of an appellate opinion. "Court" must not be the Tax Court: "the Tax Court reversed the
# Commissioner's assessment" is history, not the ruling (C1: Visco). Spaced capitals ("R EVERSED") are rejoined first.
RULING = re.compile(r"\b(?:[Ww]e|(?<!Tax )[Cc]ourt|therefore|accordingly|hereby|is|are|be)\s+(?:\w+\s+){0,2}?"
                    r"(affirm|revers|vacat|dismiss)\w*\b|\b(AFFIRM|REVERS|VACAT|DISMISS)\w*\b")
KIND = {"aff": "affirmed", "rev": "reversed", "vac": "vacated", "dis": "dismissed"}
ORG = re.compile(r"\b(Inc|LLC|L\.L\.C|Corp|Co|Company|Partnership|Partners|Trust|Associates|Group|Ltd|P\.C|S\.C|Holdings|Realty|Center)\b", re.I)
TAX = re.compile(r"v\. (CIR\b|Commissioner of (Internal Revenue|IRS)|Commissioner$|Commissioner,? (IRS|Internal))", re.I)
NOT_TAX = re.compile(r"Social Security|Department|Correction|Prison|Securities|Patents|Education", re.I)


SPACED = re.compile(r"\s+(?=[.,;:])")  # scanned opinions: "Higbee v . Commissioner , 116 T .C . 438" (C3)
MEMO_DOT = re.compile(r"\bT\.C\. Memo(?= \d{4}-)")  # "T.C. Memo 2010-92", period dropped
SPLIT_PAGE = re.compile(r"(\bT\.C\. \d{1,4}) (\d{1,3})(?= \(\d{4})")  # OCR: "129 T.C. 1 1 (2007)" is page 11


def normalize(text: str) -> str:
    text = SPACED.sub("", " ".join(text.split()))
    return SPLIT_PAGE.sub(r"\1\2", MEMO_DOT.sub("T.C. Memo.", LINEBREAK.sub(r"\1-\2", text)))


def tc_key(c: FullCaseCitation) -> str | None:
    """Our key for a Tax Court citation (memo, T.C. volume/page, or T.C. No.); None for any other court."""
    g = c.groups
    rep, vol, page = g.get("reporter"), g.get("volume"), g.get("page")
    if not (vol and page and page.isdigit()):
        return None
    if rep == "T.C. Memo.":
        return f"T.C. Memo. {vol}-{int(page)}"
    if rep == "T.C. No.":
        return f"{vol} T.C. No. {page}"
    if rep == "T.C.":
        return ALIAS.get(f"{vol} T.C. {page}", f"{vol} T.C. {page}")
    return None


def full_cites(text: str) -> list[FullCaseCitation]:
    """Full case cites, without short forms eyecite sometimes misreads as full ones ("72 T.C. at 669" with
    reporter "T.C. at"). It does so depending on the process's hash seed, and a phantom cite between an
    opinion and its appeal breaks the adjacency history relies on, so without this the load isn't repeatable (C3)."""
    return [c for c in get_citations(text)
            if isinstance(c, FullCaseCitation) and not (c.groups.get("reporter") or "").endswith(" at")]


def cites(text: str, citing: str) -> set[str]:
    """Tax Court opinions a passage cites, without the opinion citing itself -- including its own masthead
    garbled by OCR, "T.C. Memo. 2010-1 7", which would otherwise read as a cite of T.C. Memo. 2010-1."""
    return {k for c in full_cites(normalize(text)) if (k := tc_key(c)) and not own(k, citing)}


def own(key: str, citing: str) -> bool:
    return key == citing or (citing.startswith(key) and citing[len(key)].isdigit())


def year_of(text: str, c: FullCaseCitation, key: str | None = None) -> int | None:
    """The year in the parenthetical right after the cite. eyecite's own guess can come from a later one:
    "5 T.C. 1283 (1945)), affd. 987 F.2d 770 (5th Cir. 1993)" gives 1993 (C3: Lavery)."""
    if key and (m := re.match(r"T\.C\. Memo\. (\d{4})", key)):
        return int(m.group(1))
    m = re.match(r"[\s,\d–\-*n.]*\([^()]*?(\d{4})\)", text[c.span()[1]: c.span()[1] + 60])
    return int(m.group(1)) if m else None


def kind(word: str, part: str | None) -> str:
    k = KIND[word.lower()[:3]]
    return f"{k} in part" if part else k


def split(segment: str, word: str, part: str | None) -> str:
    """A mixed disposition takes its most serious part: "aff'd in part, rev'd in part" is reversed in part,
    "aff'd in part, vacated in part" vacated in part (C3 hand check)."""
    words = {w.lower()[:3] for w in re.findall(r"\b(aff|rev|vac)", segment, re.I)}
    if len(words) > 1:
        return f"{KIND[next(w for w in ('rev', 'vac', 'aff') if w in words)]} in part"
    return kind(word, part)


def unparen(text: str) -> str:
    """Explanatory parentheticals push "aff'd" past the window: "113 T.C. 254 (1999) (corporate-owned…), aff'd"."""
    for _ in range(2):
        text = PARENS.sub("", text)
    return text


def label(c: FullCaseCitation) -> str:
    """The appeal as one stable string, "560 F.3d 620 (ca7 2009)": no case name or pin cite, so two opinions
    citing the same appeal at different pages agree on it."""
    return appeal_label(c.corrected_citation(), c.metadata.court, c.metadata.year)


def appeal_label(cite: str, court: str | None, year: str | None) -> str:
    """One format for both sources, so a reader sees the same appeal the same way."""
    detail = " ".join(x for x in (court, year) if x)
    return f"{cite} ({detail})" if detail else cite


def history(text: str, citing: str) -> set[tuple[str, str, str]]:
    """(opinion, kind, by) from subsequent history in a passage. by is the appellate cite, or the citing
    opinion for an overruling."""
    text = normalize(text)
    cs = full_cites(text)
    found = set()
    for i, c in enumerate(cs):
        key = tc_key(c)
        if not key:
            continue
        start, end = c.span()
        j = i + 1  # step over parallel cites of this opinion that come before any history word
        while (j < len(cs) and cs[j].groups.get("reporter") in PARALLEL
               and not HISTORY.search(text[cs[j - 1].span()[1]: cs[j].span()[0]])):
            j += 1
        nxt = cs[j] if j < len(cs) else None
        prv = cs[i - 1] if i else None
        tail = text[cs[j - 1].span()[1] if j > i + 1 else end: nxt.span()[0] if nxt else len(text)]
        h = HISTORY.search(tail)
        # "(citing Tokarski, 87 T.C. 74 (1986)), aff'd": a ")" closing an outer parenthetical first means the
        # history belongs to the outer case, not this one (C3 #88)
        nested = h is not None and tail[: h.start()].count(")") > tail[: h.start()].count("(")
        after = None if nested else AFTER.search(unparen(tail))
        # and the appeal follows the history word closely ("per curiam, ", "sub nom. Murphy v. Commissioner, "); a
        # blank appeal cite ("aff'd, __ Fed. Appx. _") would otherwise borrow the next cite in the text (C3: Cave)
        if after and len(unparen(tail)) - after.end() > 60:
            after = None
        before = BEFORE.search(text[prv.span()[1]: start]) if prv else None
        if before and not GAP.fullmatch(text[prv.span()[1]: prv.span()[1] + before.start()]):
            before = None
        for other, m, segment in ((nxt, after, unparen(tail)), (prv, before, before.group(0) if before else "")):
            if not (m and other and other.groups.get("reporter") in APPELLATE):
                continue
            ours, theirs = year_of(text, c, key), year_of(text, other)
            if ours and theirs and theirs < ours:  # a 2003 case can't decide a 2011 appeal (C1)
                continue
            found.add((key, split(segment, m.group(1), m.group("part")), label(other)))
        # a fixed window, not up to the next cite: the appellate cite often sits between X and "is overruled"
        if OVERRULED_AFTER.search(text[end: end + 160]) or OVERRULE_BEFORE.search(text[max(0, start - 80): start]):
            found.add((key, "overruled", citing))
    return found


def ruling(text: str) -> str | None:
    """The outcome in an appellate opinion's last disposition sentence, or None (e.g. it ends in a dissent)."""
    text = re.sub(r"\b([A-Z]) ([A-Z]{3,})\b", r"\1\2", " ".join(text.split()))
    last = None
    for last in RULING.finditer(text):
        pass
    if not last:
        return None
    return kind((last.group(1) or last.group(2)), re.match(r"\s+in\s+part", text[last.end(): last.end() + 12], re.I))


def petitioners(caption: str) -> str:
    """The petitioners' names alone: "Estate of James E. Caan, Deceased, …, Petitioner" -> "James E. Caan"."""
    first = re.sub(r",? Petitioners?$", "", caption).split("; ")[0]
    first = re.sub(r"^Estate of ", "", first).split(", Deceased")[0]
    return re.sub(r",? (Jr|Sr)\.?(?=$| &)|,? I{2,3}(?=$| &)", "", first)


def surnames(names: str) -> set[str]:
    """Family names in a joint caption. "C. Michael & Gwendolyn E. Willock" is one family (Willock): a part
    with a single non-initial word is a first name. "Michael P. Schwab & Kathryn J. Kleinman" is two (C3)."""
    parts = [p.split() for p in names.split(",")[0].split(" & ") if p.split()]
    found = {parts[-1][-1]} | {p[-1] for p in parts[:-1] if len([w for w in p if not w.endswith(".")]) >= 2}
    return {n.rstrip(".") for n in found}


def party(caption: str) -> str:
    """A caseName query for the appellate caption: surnames for people ("Donald B. & Arvilla Meinhardt"
    -> Meinhardt), the leading words for entities."""
    first = petitioners(caption)
    if ORG.search(first):
        names = {" ".join(re.sub(r"[^\w\s'-]", "", first.split(",")[0]).split()[:2])}
        # a firm named after its owner is appealed under the owner's surname: "Joseph M. Grey Public Accountant, P.C."
        names |= {m.group(1)} if (m := re.match(r"[A-Z][a-z]+ [A-Z]\. ([A-Z][\w'-]+)", first)) else set()
        return " OR ".join(f'"{n}"' for n in sorted(names))
    return " OR ".join(f'"{n}"' for n in sorted(surnames(first)))


def is_appeal(op: dict, hit: dict, text: str) -> bool:
    """Same-name appeals are common (C1: three unrelated Michaels for Willock). A real one names the
    family in its caption and a petitioner in its text, comes from the Tax Court, and within five years."""
    caption = petitioners(op["caseCaption"])
    org = bool(ORG.search(caption))
    family = [n.strip('"') for n in party(op["caseCaption"]).split(" OR ")] if org else sorted(surnames(caption))
    given = {p.split()[0] for p in caption.split(" & ") if p.split() and not p.split()[0].endswith(".")}
    years = int(hit["dateFiled"][:4]) - int(op["filingDate"][:4])
    return (TAX.search(hit["caseName"]) is not None and not NOT_TAX.search(hit["caseName"])
            and 0 <= years <= APPEAL_YEARS and "Tax Court" in text
            and any(f.split()[0] in hit["caseName"] for f in family) and (org or any(g in text for g in given)))


def get(client: httpx.Client, path: str, **params) -> dict:
    while (r := client.get(API + path, params=params)).status_code == 429:
        time.sleep(int(r.headers.get("retry-after", 30)) + 2)
    r.raise_for_status()
    time.sleep(DELAY)
    return r.json()


def cached(path: Path, fetch) -> dict:
    """A response cached with the time it was fetched: re-running from cache must not pretend to be a new check."""
    if path.exists():
        return json.loads(path.read_text())
    data = {"fetched": datetime.now(timezone.utc).isoformat(), **fetch()}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    return data


def appeal(client: httpx.Client, op: dict, recheck: bool = False) -> tuple[str, str, str]:
    """(kind, by, checked_at) for one held opinion; kind "none" when no appeal is found."""
    path = RAW_DIR / "search" / f"{op['docketEntryId']}.json"
    if recheck and int(op["filingDate"][:4]) >= datetime.now().year - RECHECK_YEARS:
        path.unlink(missing_ok=True)
    q = f"caseName:({party(op['caseCaption'])}) AND (caseName:Commissioner OR caseName:CIR)"
    found = cached(path, lambda: {"results": [
        {k: h.get(k) for k in ("caseName", "court_id", "dateFiled", "citation", "cluster_id")}
        for h in get(client, "/search/", type="o", q=q, court=COURTS, filed_after=op["filingDate"][:10])["results"]]})
    # the first appeal decides our case (C1: Thompson); on a tie, the record with a reporter cite (CourtListener
    # often lists one appeal twice on the same day, once without it)
    for hit in sorted(found["results"], key=lambda h: (h["dateFiled"], not h["citation"])):
        if not TAX.search(hit["caseName"]) or NOT_TAX.search(hit["caseName"]):
            continue
        text = cached(RAW_DIR / "opinions" / f"{hit['cluster_id']}.json", lambda: {"text": " ".join(
            o.get("plain_text") or re.sub(r"<[^>]+>", " ", o.get("html_with_citations") or o.get("html") or "")
            for o in get(client, "/opinions/", cluster=hit["cluster_id"])["results"])})["text"]
        if is_appeal(op, hit, text):
            by = appeal_label((hit["citation"] or [hit["caseName"]])[0], hit["court_id"], hit["dateFiled"][:4])
            return ruling(text) or "decided", by, found["fetched"]  # decided on appeal; the ruling didn't parse
    return "none", "", found["fetched"]


def opinion_chunks(conn) -> list[tuple[str, str, datetime]]:
    rows = conn.execute("SELECT citation, text, fetched_at FROM chunks WHERE source = 'case' AND excluded IS NULL").fetchall()
    return [(c.split(", at ")[0], t, f) for c, t, f in rows]


def upsert(conn, source: str, rows: list[tuple[str, str, str, datetime]]) -> None:
    """Replace one source's rows; recorded_at (when we first learned it) survives, checked_at moves."""
    with conn.transaction():
        conn.cursor().executemany(
            """INSERT INTO treatments (citation, kind, by_citation, source, checked_at) VALUES (%s, %s, %s, %s, %s)
               ON CONFLICT (citation, source, by_citation) DO UPDATE SET kind = EXCLUDED.kind, checked_at = EXCLUDED.checked_at""",
            [(c, k, b, source, t) for c, k, b, t in rows])
        keep = {(c, b) for c, k, b, t in rows}
        stale = [(source, c, b) for c, b in conn.execute(
            "SELECT citation, by_citation FROM treatments WHERE source = %s", (source,)).fetchall() if (c, b) not in keep]
        conn.cursor().executemany("DELETE FROM treatments WHERE source = %s AND citation = %s AND by_citation = %s", stale)


STALE_DAYS = 7  # the weekly refresh the intent doc allows; Phase H schedules it
NEGATIVE = ("overruled", "reversed", "vacated", "reversed in part", "vacated in part")  # most serious first
POSITIVE = ("affirmed in part", "affirmed", "dismissed")
SOURCES = {"courtlistener": "CourtListener", "corpus": "later Tax Court opinions", "manual": "a hand-checked record"}
# Treatment one appeal deep misses a reversal that was itself reversed. Hand-entered where known, with the
# evidence; it overrides the other sources (E3). (citation, kind, by, note)
MANUAL = [
    ("T.C. Memo. 2002-5", "upheld", "Commissioner v. Banks, 543 U.S. 426 (2005)",
     "Upheld: the Ninth Circuit reversed in part (340 F.3d 1074 (ca9 2003)), and the Supreme Court reversed the "
     "Ninth Circuit in Commissioner v. Banks, 543 U.S. 426 (2005), decided with Banaitis: a litigant's income "
     "includes the contingent fee paid to the attorney. T.C. Memo. 2025-80 at *11 states the rule from Banks."),
]


def flag(rows: list[tuple[str, str, str, datetime]], now: datetime) -> dict:
    """One opinion's treatment flag from its (source, kind, by, checked_at) rows (C4).

    The rules, in order: an overruling stands on its own; sources that disagree about an appeal give
    "unknown" (C1); otherwise the most serious negative outcome, then an open appeal, then an affirmance.
    No rows at all is "unknown", and no negative treatment is never phrased as "good law"."""
    if not rows:
        return {"status": "unknown", "by": "", "sources": [], "checked_at": None, "stale": True,
                "note": "No appeal check on record for this opinion."}
    if manual := [r for r in rows if r[0] == "manual"]:
        _, kind_, by, checked = manual[0]
        note = next(n for _, k, b, n in MANUAL if b == by)
        return {"status": kind_, "by": by, "sources": [SOURCES["manual"]], "checked_at": f"{checked:%Y-%m-%d}",
                "stale": False, "note": note}
    kinds = {k for _, k, _, _ in rows if k != "none"}
    neg, pos = [k for k in NEGATIVE if k in kinds], [k for k in POSITIVE if k in kinds]
    status = ("overruled" if "overruled" in kinds else "unknown" if (neg and pos) or "unknown" in kinds
              else neg[0] if neg else "decided" if kinds & {"decided", "appealed"} else pos[0] if pos else "none")
    # the appeal to name: CourtListener's first, it is the primary source (C1)
    by = next((b for s, k, b, _ in sorted(rows, key=lambda r: r[0] != "courtlistener")
               if k == status or (status == "decided" and k == "appealed")), "")  # "appealed": rows from before E3
    checked = max(t for _, _, _, t in rows)
    names = [SOURCES[s] for s in sorted({s for s, _, _, _ in rows})]
    notes = {"none": f"No negative treatment found in {' or '.join(names)} as of {checked:%Y-%m-%d}. "
                     "Pending appeals are not tracked.",
             "unknown": "The sources disagree about this opinion's appeal; check it before relying on it.",
             "decided": f"Decided on appeal ({by}); the outcome could not be read. Check it before relying on this opinion."}
    return {"status": status, "by": by, "sources": names, "checked_at": f"{checked:%Y-%m-%d}",
            "stale": now - checked > timedelta(days=STALE_DAYS),
            "note": notes.get(status, f"{status.capitalize()} by {by}.")}


def flags(conn, opinions: list[str], now: datetime | None = None) -> dict[str, dict]:
    """Treatment flags for the opinions an answer cites. Fails open: if the table can't be read, every
    flag is "unknown" and the answer goes out unchanged. The rollback matters because the caller keeps
    using this connection to publish the answer."""
    now = now or datetime.now(timezone.utc)
    try:
        rows = conn.execute("SELECT citation, source, kind, by_citation, checked_at FROM treatments "
                            "WHERE citation = ANY(%s)", (list(opinions),)).fetchall()
        by_op: dict[str, list] = {}
        for c, *rest in rows:
            by_op.setdefault(c, []).append(tuple(rest))
        return {op: flag(by_op.get(op, []), now) for op in opinions}
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        return {op: {"status": "unknown", "by": "", "sources": [], "checked_at": None, "stale": True,
                     "note": f"The appeal check could not be read ({type(e).__name__})."} for op in opinions}


def load(conn, token: str | None = None, recheck: bool = False) -> dict:
    chunks = opinion_chunks(conn)
    edges = {(op, k) for op, t, _ in chunks for k in cites(t, op)}
    with conn.transaction():
        conn.execute("DELETE FROM citations")
        conn.cursor().executemany("INSERT INTO citations (citing, cited) VALUES (%s, %s)", sorted(edges))

    seen: dict[tuple[str, str], set[str]] = {}
    checked: dict[tuple[str, str], datetime] = {}
    for op, t, fetched in chunks:
        for key, k, by in history(t, op):
            seen.setdefault((key, by), set()).add(k)
            checked[(key, by)] = max(checked.get((key, by), fetched), fetched)
    # two opinions describing the same appeal differently: record the disagreement, don't pick one
    upsert(conn, "corpus", [(key, ks.pop() if len(ks) == 1 else "unknown", by, checked[(key, by)])
                            for (key, by), ks in seen.items()])

    upsert(conn, "manual", [(c, k, b, datetime.now(timezone.utc)) for c, k, b, _ in MANUAL])
    appeals = 0
    if token:
        with httpx.Client(headers={"User-Agent": USER_AGENT, "Authorization": f"Token {token}"}, timeout=60) as client:
            rows = [(op["citation"], *appeal(client, op, recheck)) for op in load_selection()]
        upsert(conn, "courtlistener", [(c, k, b, datetime.fromisoformat(t)) for c, k, b, t in rows])
        appeals = sum(k != "none" for _, k, _, _ in rows)
    return {"citations": len(edges), "cited": len({k for _, k in edges}), "corpus": len(seen), "appeals": appeals}