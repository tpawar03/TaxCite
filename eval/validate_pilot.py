"""Check a pilot set against the real corpus before any scores are computed.

A gold citation that does not exist, or that points at an excluded chunk, makes
every downstream number meaningless. Run this after editing pilot.jsonl.

    uv run python eval/validate_pilot.py eval/pilot.jsonl
    uv run python eval/validate_pilot.py eval/golden.jsonl

Gold may be groups of interchangeable citations (log #36): every member must exist,
and a group is reachable when any member is.

Compound and temporal rows carry `gold_subqueries`, one per gold group: the sub-query an
ideal decomposer would issue, and the source it would search. A group the whole question
misses but its sub-query reaches is reported as needing decomposition (B7's job), not
as a problem. The sub-queries are measurement only; tuning never uses them.
"""

import json
import re
import sys
from collections import Counter

from retrieval import groups
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
    problems, expected, diluted, needs_decomposition = [], [], [], []

    with store.connect() as conn:
        for r in rows:
            issues = []
            # insufficiency rows must have no answer in the corpus; adversarial rows are scored
            # on behaviour (Phase G), not retrieval
            if not r["gold"] and r["category"] not in ("insufficiency", "adversarial") and not r.get("expect_insufficient"):
                issues.append("empty gold but not an insufficiency or adversarial question")
            # An adversarial row must say what the system should do, and must decide explicitly
            # whether the attack arrives in a document: "client_doc": "" means it is in the
            # question itself (the trusted channel), which is its own test.
            if r["category"] == "adversarial":
                if not r.get("expected_behavior"):
                    issues.append("adversarial row needs expected_behavior")
                if r.get("client_doc") is None:
                    issues.append('adversarial row needs client_doc (use "" if the attack is in the question)')

            top50 = {h.citation for h in search(r["question"], k=50, mode="hybrid")} if r["gold"] else set()
            texts = []
            subqueries = r.get("gold_subqueries") or []
            if subqueries and len(subqueries) != len(r["gold"]):
                issues.append(f"{len(subqueries)} gold_subqueries for {len(r['gold'])} gold groups")
            for gi, group in enumerate(groups(r["gold"])):
                sources = set()
                for cit in sorted(group):
                    # every source lives in the chunks table: regulation, publication, statute, opinion
                    count, text, excluded, source = conn.execute(
                        "SELECT count(*), max(text), max(excluded::text), max(source) FROM chunks WHERE citation=%s", (cit,)
                    ).fetchone()
                    if not count:
                        issues.append(f"gold citation not in corpus: {cit}")
                    elif excluded:
                        issues.append(f"gold citation is an excluded chunk ({excluded}): {cit}")
                    else:
                        texts.append(text)
                        sources.add(source)

                # can retrieval reach the group at all? If not, search within the gold's own
                # source: found there, the gold is right and other corpora are crowding it out
                # (B3's dilution, which routing is meant to fix); not found even there, suspect it.
                if not group & top50:
                    if gi < len(subqueries):
                        sq = subqueries[gi]
                        if group & {h.citation for h in search(sq["query"], k=50, mode="hybrid", source=sq["source"])}:
                            needs_decomposition.append(f"{r['id']}: {' | '.join(sorted(group))}")
                            continue
                        issues.append(f"gold not reached even by its sub-query ({sq['source']}: {sq['query']!r}): {' | '.join(sorted(group))}")
                        continue
                    own = {h.citation for src in sources for h in search(r["question"], k=50, mode="hybrid", source=src)}
                    if group & own:
                        diluted.append(f"{r['id']}: {' | '.join(sorted(group))}")
                        continue
                    msg = f"gold not in hybrid top-50, even within its own source: {' | '.join(sorted(group))}"
                    if r.get("expect_hard"):
                        expected.append(f"{r['id']}: {msg}")
                    else:
                        issues.append(msg + " — wrong gold, or a question worth keeping as a known-hard case")

            # the answer should be a paraphrase of the cited sources, not of memory
            if texts and not r.get("verified"):
                words = content_words(r["answer"])
                ratio = len(words & set().union(*map(content_words, texts))) / max(len(words), 1)
                if ratio < 0.30:
                    issues.append(f"answer shares only {ratio:.0%} of its content words with its gold — read the sources and set verified:true")

            print(f"{r['id']} {'OK' if not issues else 'ISSUES'}")
            for i in issues:
                print(f"    - {i}")
            if issues:
                problems.append(r["id"])

    print("\ncategories: " + ", ".join(f"{c} {n}" for c, n in sorted(Counter(r["category"] for r in rows).items())))
    for n in needs_decomposition:
        print(f"  needs decomposition (reached only by its gold sub-query): {n}")
    for d in diluted:
        print(f"  diluted (found only within its own source): {d}")
    for e in expected:
        print(f"\n  expected-hard: {e}")
    print(f"\n{len(problems)} of {len(rows)} questions need attention; "
          f"{len(expected)} known-hard gold citations unreachable today; "
          f"{len(diluted)} gold groups reachable only within their own source; "
          f"{len(needs_decomposition)} reachable only by their gold sub-query")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "eval/pilot.jsonl"))