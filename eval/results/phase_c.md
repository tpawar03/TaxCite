# TaxCite — Phase C exit report

*2026-09-27. Plan: `tasks/plan.md` (Phase C). Tasks: `tasks/todo.md` C0–C7. Every number here traces to a file in
`eval/results/` or a command under [Reproducing](#reproducing).*

Phase C set out to build a citation graph and use it to find more case law. It measured that idea before
building it, found the ceiling was zero, and gave the graph a different job: telling the reader when a cited
opinion was later reversed. It also found that most of the case-law "gap" Phase B handed over was the answer
key, not the retriever.

## What exists

| | |
|---|---|
| Citation graph | Two Postgres tables, no graph database (ADR-23). `citations`: 5,278 edges from 304 citing opinions to 2,649 Tax Court opinions. `treatments`: 718 rows (698 opinions) from the corpus's own subsequent history, 307 from CourtListener (19 held opinions with an appeal) |
| Load | `taxcite citations`, ~2 min from cache, idempotent under any hash seed |
| Treatment flags | Every opinion an answer cites carries `status` (reversed, overruled, vacated, affirmed, appealed, unknown, none), the appeal, its sources, the check date and a stale mark, in the SSE `answer` event |
| Graph expansion | `retrieve(..., hops=0)`: built, measured, off |
| Eval | Gold may name a chunk key where a page label is shared; 24 gold groups widened and 6 narrowed, all reviewed |
| Tests | 186 |
| Stores | Qdrant, Postgres, Redis (Neo4j dropped, ADR-23) |

## The gate

§9.3's Phase C gate as first written, and as revised on 2026-09-26 (after C0, before any of C3–C5 was measured):

| criterion | threshold | measured | |
|---|---|---|---|
| Case-law Recall@20 delta from graph expansion *(original gate)* | ≥ +5 points | **−3.9** (0.777 → 0.738) | **not met** |
| Edge extraction, citations *(both versions)* | precision ≥ 90%, recall ≥ 85% | **100/100** sampled; **99.9%** recall | met |
| Edge extraction, treatments *(both versions)* | precision ≥ 90%, recall ≥ 85% | **75/76 (98.7%)**; recall **88%** on the loose yardstick, ~95% after classifying misses | met |
| Golden negative-treatment rows *(revised gate)* | 3/3 reversed flagged, 0 false flags | **3/3, 0** | met |

The original gate is **not met**, and not reinterpreted: expansion lowers recall. The revised gate replaced it
because C0 showed, before anything was built, that no design of expansion could meet it on this golden set
(ADR-1, revised). The original gate named four edge types (`CITES`, `DISTINGUISHES`, `OVERRULES`, `AMENDS`); the
revised plan scored the two types something reads, citations and treatments.

## C0: the ceiling, before building

For the case-law gold that the shipped path misses at k=20, how far is it from the opinions that *were*
retrieved? (26 case-law rows, plan set 0; command below.)

| where the missed gold is | at C0 (2026-09-23) | now (post-audit gold) |
|---|---|---|
| a wrong page of an opinion already retrieved | 6 rows (23.1 points) | 3 rows: G-C10, G-C24, G-C26 |
| 1 citation hop away | 0 | **0** |
| 2 hops, through any opinion | 0 | **0** |
| further, or unreachable | 2 (7.7 points) | 2: G-C05, G-C21 |

Only 4.7% of the corpus's citation edges resolve to an opinion it holds (231 of 4,911 at C0; the "8.9%"
carried into Phase C was an overestimate).

## The ladder

Golden set, k=20, hybrid + routing + rerank, 5 plan sets, key-aware scoring
(`retrieval-golden-2026-09-27-k20-c5-graph.json`):

| rung | case law (26) | all scored (86) | p50 |
|---|---|---|---|
| hybrid, no routing | 0.808 | 0.504 | 29 ms |
| **shipped: routing + rerank** | **0.777 ± 0.029** | **0.563 ± 0.010** | 1,247 ms |
| + 1-hop graph expansion | 0.738 ± 0.029 | 0.540 ± 0.010 | 1,953 ms |
| + 2-hop graph expansion | 0.738 ± 0.029 | 0.522 ± 0.010 | 1,977 ms |

By category for the shipped arm (`retrieval-golden-2026-09-27-k20-c6-keyed.json`): statutory 0.500,
compound 0.459 ± 0.012.

Expansion improves **no row in any plan set**. One hop loses G-C15 (its gold sat at rank 20) and G-S01 (a
statutory row whose plan also held a case-law sub-query) in all five sets; two hops also lose G-X04, G-X06 and
G-X17.

### How the case-law baseline moved

| | case-law Recall@20 | what changed |
|---|---|---|
| Phase B report | 0.692 | label scoring, pre-audit gold |
| after the C2 audit, plan set 0 | 0.846 | 24 gold groups widened to pages where the court states its holding |
| 3 plan sets | 0.833 ± 0.018 | |
| 5 plan sets | 0.815 ± 0.029 | the two new plan sets scored 0.808 and 0.769 |
| **key-aware scoring** | **0.777 ± 0.029** | G-C24 had scored through a copy of its page that doesn't state the holding |

## Treatment flags

**Golden rows**, through the live pipeline (`phase-c-treatment-gate-2026-09-27.txt`, $0.005 a run):

| row | cited opinion | flag |
|---|---|---|
| G-C03 | *Morehouse*, 140 T.C. No. 16 | **reversed**, 769 F.3d 616 (8th Cir. 2014) |
| G-X02 | *Morehouse* | **reversed** |
| G-X09 | *Menard*, T.C. Memo. 2004-207 | **reversed**, 560 F.3d 620 (7th Cir. 2009) |
| G-C06 | *Grey*, 119 T.C. No. 5 | affirmed |
| G-X19 | T.C. Memo. 2022-117, 2025-50 | none (the answer didn't cite the gold opinion) |
| G-C11 | *Patel*, 165 T.C. No. 10 | none: "Pending appeals are not tracked" |

**Every held opinion:** 26 carry a non-clean flag, and all 26 match the hand-verified records (19 from
CourtListener, 7 from the corpus only, which CourtListener doesn't carry); 281 read none.

**Sources.** CourtListener finds the appeal and reads its outcome from the appellate opinion's closing sentence;
it needs a free API key (10 requests a minute) and has no unpublished Westlaw-only dispositions. The corpus's
own subsequent history covers only opinions a later held opinion mentions (14 of 307) but supplies outcomes
for 698 cited opinions. Neither source can see a pending appeal.

## Extraction quality

Hand check of 200 edges (`phase-c-handcheck-citations.txt`, `phase-c-handcheck-treatments.txt`):

| type | precision | recall |
|---|---|---|
| citations | 100 of 100 random edges; 37 of 40 edges added by the scanned-text repair, the 3 wrong ones since blocked | 5,115 of 5,121 (99.9%) against an independent looser pattern |
| treatments, CourtListener | 19 of 19 | — |
| treatments, corpus | 75 of 76 checkable claims; 4 `unknown` (sources disagree) count as neither | 636 of 722 (88%) against a loose pattern; 16 of 30 classified misses aren't this case's history, so ~95% of real history |

## Failures, with examples

**1. A faithful answer that is wrong, and a flag that is right.** Asked whether an Iowa client's 2006 CRP
payments are subject to self-employment tax, the pipeline answers "Yes", citing *Morehouse*, faithfully. The
Eighth Circuit, which covers Iowa, reversed *Morehouse* in 2014. The flag beside the citation is the only thing
on the page that says so. Acting on it is Phase E's.

**2. A hit that was never a hit.** G-C24 scored in every plan set because a chunk labelled
`T.C. Memo. 2023-128, at *15` was retrieved. Three chunks carry that label; the one retrieved doesn't state the
holding, and the one that does isn't in the top 50 even among court opinions.

**3. Expansion displaces.** G-C15's gold page sat at exactly rank 20. One hop of citation expansion adds
court prose that pushes it out, in all five plan sets.

**4. A count that depended on the process.** A hash-seed-dependent eyecite misread ("72 T.C. at 669" read as a full
cite) dropped *Kahla*'s affirmance under some seeds, so the treatment count read 716, 717 or 718 depending on the
process. Found because a run on another machine printed 716.

**5. A table text search can't see.** G-S28's answer is a row of Pub 946's depreciation-cap table. Narrowed to
that chunk, it isn't in the top 50 even within publications.

**6. The appeal nobody can see.** *Patel* (G-C11) is on appeal to the Fifth Circuit now. Every source reads
"no negative treatment", which is why the flag says "Pending appeals are not tracked" rather than anything
resembling "good law".

**7. Retrieval misses the right case and the flags stay clean.** G-X19's answer cites two other opinions, not
its gold post-remand opinion. The flags on what it did cite are correct and say nothing about what it missed.

## §9.3 recalibration

| what | was | now | why |
|---|---|---|---|
| Phase C recall gate | +5 points Recall@20 from expansion | reported, not gated | C0's ceiling was 0 before anything was built; measured −3.9 |
| Phase C graph gate | — | 3/3 reversed golden rows flagged, 0 false flags | the graph's load-bearing job is negative treatment |
| Edge extraction | precision/recall per type, four types | per type read by the system: citations, treatments | `DISTINGUISHES` needed an LLM pass and nothing read it; `AMENDS` is Phase D's |
| Gold matching | page label | label or chunk key | 2,072 labels are shared by several chunks |
| Graph store | Neo4j | two Postgres tables | the one query is a lookup by key (ADR-23) |

## What Phase C got wrong

- **Two numbers carried in were optimistic.** 8.9% of edges resolving was really 4.7%, and Phase B's "the
  missed 30.8% is not in the candidate pool" was wrong for three quarters of it.
- **One-sample numbers, again.** 0.846 came from one plan set; five put it at 0.815. The five-sample rule
  from Phase B caught it, after it had been written into the docs once.
- **A determinism claim that held only within a hash seed** (failure 4). Repeatability is now checked across
  six seeds.
- **Neo4j was kept by finding it a job before asking whether the job needed it.** It didn't; it was dropped a
  day later.
- **Two process slips:** a results file overwritten by a later run on the same day (outputs are now named by
  task), and one CourtListener request sent with a personal email address in its user-agent header.

## Open problems handed on

| problem | owner |
|---|---|
| Page selection: G-C10, G-C26 (7.7 points) | open; needs dev rows that exercise it before any mechanism (C6) |
| Unreachable answer chunks: G-C24's holding, G-S28's table | Phase E (publication tables); open for opinions |
| Weekly treatment refresh; corpus-only flags go stale on 2026-09-29 | Phase H |
| Acting on treatment in ranking and answers | Phase E |
| Pending appeals | no source; stays "not tracked" |

## Reproducing

```bash
uv run taxcite citations                                           # both tables, ~2 min from cache
uv run pytest -q                                                   # 186 tests
uv run python eval/validate_pilot.py eval/golden.jsonl             # 0 of 115 need attention
uv run python eval/retrieval.py --pilot eval/golden.jsonl --k 20 --mode hybrid \
  --decompose route --decompose route+graph1 --decompose route+graph2 --repeats 5   # the ladder
uv run python eval/retrieval.py --pilot eval/dev.jsonl --mode hybrid --k 10 \
  --decompose route --plan-cache eval/results/decompositions.json --fail-under 0.66  # CI tier 2: 0.680
```

Table counts:

```bash
docker compose exec -T postgres psql -U taxcite -d taxcite -c \
  "select source, count(*), count(*) filter (where kind <> 'none') from treatments group by source"
```

C0's ceiling on today's gold (plan set 0):

```bash
uv run python - <<'EOF'
import json, sys; sys.path.insert(0, "eval")
import retrieval as ev
from taxcite import decompose as dc
cache = json.load(open("eval/results/decompositions.json")); edges, held = dc.citation_graph(); out = {}
for r in (r for r in map(json.loads, open("eval/golden.jsonl")) if r["category"] == "case_law"):
    hits = dc.chunks(dc.retrieve(ev.cached_decompose(r["question"], cache, None, 0), k=20, route=True), 20, ev.RERANK_MODEL)
    got, seeds = [h.key or h.citation for h in hits], {h.section for h in hits if h.source == "case"}
    for g in ev.groups(r["gold"]):
        if ev.first_hits(got, [g]): continue
        ops = {c.split("#")[0].split(", at ")[0] for c in g}
        out.setdefault("wrong page" if ops & seeds else "1 hop" if ops & dc.neighbors(edges, seeds, 1, held)
                       else "2 hops" if ops & dc.neighbors(edges, seeds, 2, held) else "unreachable", []).append(r["id"])
print(out)
EOF
```

The treatment-flag gate (G-C03, G-X02, G-X09, G-C06, G-X19, G-C11 through `decompose` → `retrieve` →
`answer_from_groups` → `citations.flags`) is the `jobs.run` path without the job record; its output is
`phase-c-treatment-gate-2026-09-27.txt`.
