"""Command line: fetch, parse, store and index the corpora.

    taxcite ingest ecfr --part 1
    taxcite ingest ecfr --section 1.61-1 --skip-index
"""

import argparse
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

from taxcite import index, store

# Load .env at the entry point only: library code reads os.environ and stays
# unaware of where the values came from, so tests and imports are unaffected.
load_dotenv()
from taxcite.ingest import ecfr

ECFR_API = "https://www.ecfr.gov/api/versioner/v1"

# Topics the Phase A pilot questions will cover, plus four large unrelated families
# as distractors so retrieval has something to get wrong. ~5,000 chunks, ~12 min to
# embed, against ~44,000 and ~105 min for all of Part 1.
PILOT_PREFIXES = [
    "1.61", "1.62", "1.63",           # gross income, AGI, taxable income
    "1.162", "1.212", "1.262",        # business vs. personal expenses
    "1.263", "1.263A",                # capitalization vs. current deduction
    "1.167", "1.168", "1.179",        # depreciation, MACRS, expensing
    "1.183", "1.274", "1.280F",       # hobby loss, travel/meals, listed property
    "1.446", "1.451", "1.461",        # accounting methods and timing
    "1.469", "1.1402",                # passive activity, self-employment
    "1.401(a)", "1.704", "1.988", "1.482",  # distractors
]
RAW_DIR = Path("data/raw")
TITLE = 26


def latest_as_of(title: int = TITLE) -> str:
    """The date eCFR considers Title 26 current to."""
    titles = httpx.get(f"{ECFR_API}/titles.json", timeout=30).raise_for_status().json()["titles"]
    return next(t["up_to_date_as_of"] for t in titles if t["number"] == title)


def fetch(part: str, as_of: str, section: str | None = None, refresh: bool = False) -> Path:
    """Download one part (or a single section) of Title 26, cached on disk.

    The API rejects requests that do not accept compression (HTTP 406); httpx
    sends the header by default. A full part is ~12 MB and takes ~30 s.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    name = f"title{TITLE}-part{part}" + (f"-{section}" if section else "") + f"-{as_of}.xml"
    path = RAW_DIR / name
    if path.exists() and not refresh:
        return path
    params = {"part": part} | ({"section": section} if section else {})
    with httpx.stream("GET", f"{ECFR_API}/full/{as_of}/title-{TITLE}.xml", params=params, timeout=300) as r:
        r.raise_for_status()
        with path.open("wb") as fh:
            for block in r.iter_bytes():
                fh.write(block)
    return path


def progress(done: int, total: int, started: float) -> None:
    elapsed = time.time() - started
    left = (total - done) / (done / elapsed) if done else 0
    print(f"    {done}/{total} ({done / total:.0%}) {elapsed / 60:.0f}m elapsed, ~{left / 60:.0f}m left", flush=True)


def ingest_ecfr(args: argparse.Namespace) -> int:
    as_of = args.as_of or latest_as_of()
    print(f"eCFR Title {TITLE} part {args.part} as of {as_of}")

    t0 = time.time()
    path = fetch(args.part, as_of, args.section, args.refresh)
    print(f"  fetched {path} ({path.stat().st_size / 1e6:.1f} MB, {time.time() - t0:.0f}s)")

    chunks = ecfr.parse(path, as_of)
    if args.only:
        prefixes = PILOT_PREFIXES if args.only == ["pilot"] else args.only
        before = len(chunks)
        chunks = [c for c in chunks if ecfr.in_scope(c.section, prefixes)]
        print(f"  scoped  {len(chunks)} of {before} chunks to {len(prefixes)} section prefixes")
    indexable = [c for c in chunks if not c.excluded]
    skipped = len(chunks) - len(indexable)
    print(f"  parsed  {len(chunks)} chunks ({len(indexable)} indexable, {skipped} recorded as skipped)")

    with store.connect() as conn:
        store.create_table(conn)
        store.save(conn, chunks)
        print(f"  stored  {store.count(conn, 'ecfr')} rows in postgres")

        if args.skip_index:
            print("  skipped embedding (--skip-index)")
            return 0

        print(f"  embedding {len(indexable)} chunks (~{len(indexable) / 7 / 60:.0f} min at 7/s)...")
        t0 = time.time()
        result = index.sync(conn, index.client(), "ecfr", progress=progress)
        print(f"  indexed {result['written']} points, removed {result['removed']} stale, {time.time() - t0:.0f}s")
    return 0


def ingest_pubs(args: argparse.Namespace) -> int:
    from taxcite.ingest import irs_pubs

    pubs = args.pub or list(irs_pubs.PUBS)
    print(f"IRS publications: {', '.join(pubs)}")
    chunks = []
    for num in pubs:
        path = irs_pubs.fetch(num, refresh=args.refresh)
        found = irs_pubs.parse(path, num)
        failed = sum(1 for c in found if c.excluded)
        print(f"  pub {num:<4} {path.stat().st_size / 1e6:>5.1f} MB  {len(found):>4} chunks ({failed} failed pages)  {found[0].heading[:52]}")
        chunks += found

    with store.connect() as conn:
        store.create_table(conn)
        store.save(conn, chunks)
        print(f"  stored  {store.count(conn, 'irs_pub')} rows in postgres")
        if args.skip_index:
            print("  skipped embedding (--skip-index)")
            return 0
        indexable = [c for c in chunks if not c.excluded]
        print(f"  embedding {len(indexable)} chunks (~{len(indexable) / 7 / 60:.0f} min at 7/s)...")
        result = index.sync(conn, index.client(), "irs_pub", progress=progress)
        print(f"  indexed {result['written']} points, removed {result['removed']} stale")
    return 0


def run_search(args: argparse.Namespace) -> int:
    from taxcite.retrieve import search

    hits = search(args.query, k=args.k, mode=args.mode, source=args.source)
    if not hits:
        print("no results")
        return 1
    for rank, h in enumerate(hits, 1):
        snippet = " ".join(h.text.split())[:140]
        print(f"{rank:>2}. {h.score:.3f}  {h.citation}")
        print(f"     {h.heading}")
        print(f"     {snippet}...\n")
    return 0


def run_ask(args: argparse.Namespace) -> int:
    from taxcite.generate import MissingCredentials, answer

    from taxcite.generate import MODEL

    try:
        result = answer(args.question, mode=args.mode, k=args.k, model=args.model or MODEL)
    except MissingCredentials as e:  # a stack trace helps nobody here
        print(e, file=sys.stderr)
        return 2
    print(result.text.strip())
    print()
    if result.refused:
        print("  [refused: insufficient evidence]")
    if result.citations:
        print(f"  citations ({len(result.citations)}): " + "; ".join(result.citations))
    if result.unsupported_citations:
        print("  !! citations not in the retrieved sources: " + "; ".join(result.unsupported_citations))
    print(f"  {result.model} · {result.mode} · {result.input_tokens} in / {result.output_tokens} out "
          f"· ${result.cost_usd:.4f}" + (f" · {len(result.retrieved)} chunks retrieved" if result.retrieved else ""))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="taxcite")
    sub = parser.add_subparsers(dest="command", required=True)
    ingest = sub.add_parser("ingest", help="fetch, parse, store and index a corpus").add_subparsers(dest="corpus", required=True)

    cfr = ingest.add_parser("ecfr", help="26 CFR regulations")
    cfr.add_argument("--part", default="1", help="CFR part, e.g. 1 (income tax)")
    cfr.add_argument("--section", help="single section, e.g. 1.61-1 (for development)")
    cfr.add_argument("--as-of", help="eCFR date; defaults to the latest available")
    cfr.add_argument("--refresh", action="store_true", help="re-download even if cached")
    cfr.add_argument("--skip-index", action="store_true", help="store in postgres without embedding")
    cfr.add_argument("--only", nargs="+", metavar="PREFIX",
                     help='limit to section prefixes, e.g. --only 1.162 1.274; "--only pilot" uses the Phase A subset')
    cfr.set_defaults(func=ingest_ecfr)

    pubs = ingest.add_parser("irs-pubs", help="IRS publications (PDF)")
    pubs.add_argument("--pub", action="append", help="publication number, repeatable; default is the Phase A set")
    pubs.add_argument("--refresh", action="store_true", help="re-download even if cached")
    pubs.add_argument("--skip-index", action="store_true", help="store in postgres without embedding")
    pubs.set_defaults(func=ingest_pubs)

    find = sub.add_parser("search", help="search the indexed corpus")
    find.add_argument("query")
    find.add_argument("-k", type=int, default=10, help="number of results (default 10)")
    find.add_argument("--mode", default="hybrid", choices=("dense", "sparse", "hybrid"),
                      help="retrieval mode; the rungs of the eval ablation ladder")
    find.add_argument("--source", help="limit to one corpus, e.g. ecfr")
    find.set_defaults(func=run_search)

    ask = sub.add_parser("ask", help="answer a question, with or without retrieval")
    ask.add_argument("question")
    ask.add_argument("--mode", default="rag", choices=("rag", "closed_book"),
                     help="closed_book is the §9 ablation baseline: no sources at all")
    ask.add_argument("-k", type=int, default=8, help="chunks to retrieve (default 8)")
    ask.add_argument("--model", default=None, help="override TAXCITE_MODEL")
    ask.set_defaults(func=run_ask)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())