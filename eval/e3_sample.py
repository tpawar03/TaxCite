"""E3: draw the stratified 150-chunk sample for the authority hand check, with its evidence.

    uv run python eval/e3_sample.py            # writes eval/results/phase-e-e3-sample.json and the handcheck file
    uv run python eval/e3_sample.py --seed 20260929 --exclude eval/results/phase-e-e3-sample.json   # the re-check

§3.2 asks for >=95% field-level accuracy on 150 hand-labelled chunks. Most profile values follow from the
source alone, so a uniform sample would pass on those; the strata weight the fields that vary (E0). Opinion
labels (reported vs. memo, treatment) belong to an opinion, not a chunk, so those strata take one chunk per
distinct opinion. Each chunk carries the evidence a labeller checks it against: the eCFR heading and any
expiry clause, the opinion's caption and filing date, the treatment record. Fixed seed: a re-run draws the
same sample. A fixed sample is graded once; if E3 fails and gets fixed, the re-check draws a fresh one
(--seed), never this one (D4's rule).
"""

import argparse
import json
import random
import re
import sys
from pathlib import Path

from taxcite import store
from taxcite.chunk import EXPIRES
from taxcite.ingest.citations import flags

RESULTS = Path("eval/results")
# DAWSON's own record per opinion: documentType/eventCode are independent of the citation form our label is
# read from (the ingester notes a few memos are coded as T.C. opinions); filingDate is where as_of came from.
DAWSON = {op["citation"]: op for op in json.loads(Path("data/caselaw/opinions.json").read_text())}
COLS = "key, source, citation, section, heading, text, as_of, excluded, source_revision, authority"


def rows(conn, where: str, args=()) -> list[dict]:
    cur = conn.execute(f"SELECT {COLS} FROM chunks WHERE {where} ORDER BY key", args)
    names = [d.name for d in cur.description]
    return [dict(zip(names, r)) for r in cur.fetchall()]


def one_per_opinion(rs: list[dict], rng: random.Random) -> dict[str, dict]:
    by: dict[str, list[dict]] = {}
    for r in rs:
        by.setdefault(r["section"], []).append(r)
    return {op: rng.choice(cs) for op, cs in by.items()}


# Matched on text with spaces and periods removed: scanned opinions read "T .C . Memo ." and "Filed Feb . 26, 2003".
# Capitalised "Filed"/"FILED" is the court's own line; lowercase "filed June 6" is usually a return being filed.
FILED = re.compile(r"(?:Filed|FILED)([A-Z][a-z]+)(\d{1,2}),(\d{4})")


def squeeze(text: str) -> str:
    return re.sub(r"[\s.]+", "", text)


def page(citation: str) -> int:
    m = re.search(r"\*(\d+)", citation)
    return int(m.group(1)) if m else 10**6


def caption(conn, opinion: str) -> str:
    """The source of truth in the opinion's own text: does it carry its citation form, and its 'Filed <date>'
    line? Pages sorted as numbers: Postgres' locale collation ignores punctuation and puts *11-12 before *1-2.
    Some opinions have no Filed line in their extracted text; their date came from DAWSON's record."""
    chunks = sorted(conn.execute("SELECT citation, text FROM chunks WHERE section = %s", (opinion,)).fetchall(),
                    key=lambda r: page(r[0]))
    own = next((c.split(", at ")[1] for c, t in chunks if squeeze(opinion) in squeeze(t)), None)
    filed = next(((c.split(", at ")[1], f"Filed {m[1]} {m[2]}, {m[3]}") for c, t in chunks
                  if (m := FILED.search(squeeze(t)))), None)
    d = DAWSON.get(opinion, {})
    return (f"citation form {opinion!r} in its own text: {'at ' + own if own else 'not in the extracted text'} | "
            + (f"{filed[1]!r} (at {filed[0]})" if filed else "no 'Filed <date>' line in the extracted text")
            + f" | DAWSON: {d.get('documentType')!r} ({d.get('eventCode')}), filed {d.get('filingDate')}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260928)
    ap.add_argument("--exclude", action="append", default=[], metavar="SAMPLE_JSON",
                    help="a previous sample: its chunks aren't drawn again, nor its opinions in the opinion strata (D4's rule)")
    args = ap.parse_args()
    rng = random.Random(args.seed)
    live = "(excluded IS NULL OR excluded = 'expired')"
    prior = [x for p in args.exclude for x in json.loads(Path(p).read_text())["sample"]]
    seen = {x["key"] for x in prior}
    seen_ops = {x["key"].split(", at ")[0] for x in prior if x["stratum"] in ("treatment", "memorandum opinion")}
    fresh = lambda rs: [r for r in rs if r["key"] not in seen]  # noqa: E731
    take = lambda rs, k: rng.sample(rs, min(k, len(rs)))  # noqa: E731  an exhausted stratum gives what it has
    sample: list[tuple[str, dict]] = []

    with store.connect() as conn:
        sample += [("statute", r) for r in take(fresh(rows(conn, f"source = 'usc' AND {live}")), 20)]
        sample += [("final regulation", r) for r in take(fresh(
            rows(conn, f"source = 'ecfr' AND {live} AND section !~ 'T$'")), 20)]
        temp = fresh(rows(conn, f"source = 'ecfr' AND {live} AND section ~ 'T$'"))
        expired = [r for r in temp if r["excluded"] == "expired"]
        partly = [r for r in temp if r["authority"]["status"] == "temporary_partly_expired" and not r["excluded"]]
        rest = [r for r in temp if r not in expired and r not in partly]
        # the first sample took every expired chunk there was (4); since E3's sunset fix there are 155
        chosen = expired if not prior else take(expired, 4)
        chosen += take(partly, 4) + take(rest, 20 - len(chosen) - min(4, len(partly)))
        sample += [("temporary regulation", r) for r in chosen]

        cases = fresh(rows(conn, f"source = 'case' AND {live}"))
        treat = flags(conn, sorted({r["section"] for r in cases}))
        firsts = one_per_opinion(cases, rng)
        treated = [op for op, f in treat.items() if f["status"] not in ("none",) and op not in seen_ops]
        adverse = [op for op in treated if treat[op]["status"] != "affirmed"]            # every one of them
        chosen_t = adverse + take([op for op in treated if op not in adverse], 15 - len(adverse))
        sample += [("treatment", firsts[op]) for op in chosen_t]
        reported = [op for op in firsts if " T.C. No. " in op and op not in chosen_t]
        memos = [op for op in firsts if "T.C. Memo." in op and op not in chosen_t and op not in seen_ops]
        picked = [firsts[op] for op in reported] if not prior else []  # all 28 were drawn once; then fresh chunks only
        extra = [r for r in cases if " T.C. No. " in r["section"] and r not in picked]
        sample += [("reported opinion", r) for r in picked + take(extra, 30 - len(picked))]
        sample += [("memorandum opinion", firsts[op]) for op in take(memos, 30)]
        sample += [("publication", r) for r in take(fresh(rows(conn, f"source = 'irs_pub' AND {live}")), 15)]

        assert len({r["key"] for _, r in sample}) == len(sample) and not {r["key"] for _, r in sample} & seen
        out = []
        for i, (stratum, r) in enumerate(sample, 1):
            if r["source"] == "ecfr":
                clause = EXPIRES.search(r["text"])
                evidence = f"heading: {r['heading']!r} | expiry clause in this chunk: {clause.group() if clause else 'none'}"
            elif r["source"] == "case":
                evidence = caption(conn, r["section"])
            elif r["source"] == "irs_pub":
                evidence = f"heading: {r['heading']!r} | as_of {r['as_of']}"
            else:
                evidence = f"heading: {r['heading']!r}"
            item = {"n": i, "stratum": stratum, "key": r["key"], "stored": r["authority"],
                    "source_revision": r["source_revision"], "excluded": r["excluded"], "evidence": evidence}
            if r["source"] == "case":
                f = treat[r["section"]]
                item["treatment"] = {k: f[k] for k in ("status", "by", "sources")}
            out.append(item)

    RESULTS.mkdir(exist_ok=True)
    tag = "" if args.seed == 20260928 else f"-{args.seed}"  # a re-check never overwrites the labelled first sample
    (RESULTS / f"phase-e-e3-sample{tag}.json").write_text(json.dumps({"seed": args.seed, "sample": out}, indent=1))
    with open(RESULTS / f"phase-e-handcheck-authority{tag}.txt", "w") as f:
        f.write(f"# E3 hand check: {len(out)} chunks, seed {args.seed}. Label each field against the evidence line:\n"
                "# 'ok', or 'WRONG: <true value>'. Fields: type, status, source_revision; treatment for opinions.\n\n")
        for x in out:
            s = x["stored"]
            f.write(f"## {x['n']}. [{x['stratum']}] {x['key']}\n"
                    f"stored: type={s['type']} status={s['status']} level={s['level']} | source_revision={x['source_revision']}"
                    + (f" | excluded={x['excluded']}" if x["excluded"] else "") + "\n"
                    + (f"treatment: {x['treatment']}\n" if "treatment" in x else "")
                    + f"evidence: {x['evidence']}\n"
                    "label: type=  status=  source_revision=" + ("  treatment=" if "treatment" in x else "") + "\n\n")
    from collections import Counter
    print(Counter(x["stratum"] for x in out))
    print(f"treatment opinions: {[x['key'].split(',')[0] for x in out if x['stratum'] == 'treatment']}")
    print(f"{len(out)} rows; wrote {RESULTS / f'phase-e-e3-sample{tag}.json'} and {RESULTS / f'phase-e-handcheck-authority{tag}.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())