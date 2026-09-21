"""Check a pilot set against the real corpus before any scores are computed.

A gold citation that does not exist, or that points at an excluded chunk, makes
every downstream number meaningless. Run this after editing pilot.jsonl.

    uv run python eval/validate_pilot.py eval/pilot.jsonl
"""

import json
import re
import sys

from taxcite import store
from taxcite.retrieve import search

STOP = set("the a an of to in for and or if is are was were be been that this with as by on at from "
           "not no any such shall may must can will would year taxable taxpayer client under section "
           "paragraph amount amounts".split())


def content_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]{4,}", text.lower()) if w not in STOP}


def main(path: str) -> int:
    rows = [json.loads(line) for line in open(path) if line.strip()]
    print(f"{len(rows)} questions\n")
    problems, expected = [], []

    with store.connect() as conn:
        for r in rows:
            issues = []
            if not r["gold"] and r["category"] != "insufficiency":
                issues.append("empty gold but not an insufficiency question")

            for cit in r["gold"]:
                # gold may cite a regulation ("26 CFR 1.183-2(b)(3)") or a publication
                # ("IRS Pub 587 (2025), p. 12"); both live in the chunks table
                count, text, excluded = conn.execute(
                    "SELECT count(*), max(text), max(excluded::text) FROM chunks WHERE citation=%s", (cit,)
                ).fetchone()
                if not count:
                    issues.append(f"gold citation not in corpus: {cit}")
                    continue
                if excluded:
                    issues.append(f"gold citation is an excluded chunk ({excluded}): {cit}")

                # the answer should be a paraphrase of the cited rule, not of memory
                if not r.get("verified"):
                    ratio = len(content_words(r["answer"]) & content_words(text)) / max(len(content_words(r["answer"])), 1)
                    if ratio < 0.30:
                        issues.append(f"answer shares only {ratio:.0%} of its content words with {cit} — read the rule and set verified:true")

                # can retrieval reach it at all?
                if cit not in [h.citation for h in search(r["question"], k=50, mode="hybrid")]:
                    msg = f"gold not in hybrid top-50: {cit}"
                    if r.get("expect_hard"):
                        expected.append(f"{r['id']}: {msg}")
                    else:
                        issues.append(msg + " — wrong gold, or a question worth keeping as a known-hard case")

            print(f"{r['id']} {'OK' if not issues else 'ISSUES'}")
            for i in issues:
                print(f"    - {i}")
            if issues:
                problems.append(r["id"])

    for e in expected:
        print(f"\n  expected-hard: {e}")
    print(f"\n{len(problems)} of {len(rows)} questions need attention; "
          f"{len(expected)} known-hard gold citations unreachable today")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "eval/pilot.jsonl"))