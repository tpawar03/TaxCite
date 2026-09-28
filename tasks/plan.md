# Implementation Plan: TaxCite Phase A — Core Retrieval Baseline

## Overview

Phase A (tech doc §7) builds single-hop hybrid retrieval over **eCFR Title 26 + IRS Publications**, for one tenant, with no decomposition. It is measured against a ~20-question pilot set and compared with a closed-book baseline. Phase A also has to **settle three architecture decisions**: the dense embedding model (§3.2), the LLM provider/model tiering (ADR-11), and the SSE-over-durable-job transport (ADR-9, decided but not yet built).

The exit condition is evidence plus a runnable path. A reviewer can `POST /queries` a regulations or IRS-publication question, watch the SSE stage events, and get a cited answer. The pilot-set numbers for closed-book, dense-only and hybrid runs, the embedding benchmark, and the LLM benchmark are all written down.

Source docs: `taxcite-technical-documentation.md` §3, §4, §7, §9, §11, ADR-6/9/11/16 · `docs/intent/taxcite.md`.

## Architecture Decisions (for this phase)

- **Stores used in Phase A: Qdrant, Postgres, Redis.** Neo4j arrives in Phase C with the citation graph and Langfuse with tracing. Both stay in the architecture; they just aren't needed until they have work to do. For ADR-11 benchmarking, cost comes from token counts in the provider responses.
- **Local dev uses one `docker compose`** (Qdrant, Postgres 16, Redis). Supabase and hosting are deployment choices for later phases; the code only sees a `DATABASE_URL`.
- **Hybrid retrieval uses Qdrant's native dense + sparse vectors with its built-in fusion** (ADR-6). Sparse vectors come from `fastembed` (BM25-style), so there's no second engine.
- **Chunking follows §3.2.** Regulations get section-level chunks of 200–500 tokens with no overlap and keep their parent-section metadata. IRS publications use the §3.2 fallback: ~300-token sliding windows with 15% overlap.
- **Package layout:** `src/taxcite/`, with plain modules and no framework layers. Each stage is one function. Where a model is swappable (embedding, LLM), the choice is one config value, not an interface hierarchy.
- **The pilot set is data, not code:** `eval/pilot.jsonl` holds question, gold section citations and a reference answer. The eval scripts are small and live next to it.
- **Transport (ADR-9 + ADR-16):** `POST /queries` inserts a `jobs` row in Postgres and returns the id. A background worker runs the pipeline and publishes stage events to Redis pub/sub. `GET /queries/{id}/events` streams SSE. On reconnect it replays the terminal state from the job row. The answer is sent once, as the terminal event, never streamed token by token.

## Dependency Graph

```
docker compose (Qdrant, Postgres, Redis) + package skeleton
        │
        ├── eCFR T26 ingest ──► hybrid search CLI ──► pilot set + retrieval eval
        │                              │                        │
        │                              ├── IRS pubs ingest ─────┤
        │                              │                        ▼
        │                              │            embedding benchmark (decision)
        │                              ▼                        │
        │                     answer generation + closed-book baseline
        │                              │
        │                              ▼
        │                     ADR-11 LLM benchmark (decision)
        │                              │
        └──────────────────────────────┴──► ADR-9 job + SSE transport ──► Phase A exit report
```

## Task List

Full task details are in `tasks/todo.md`.

### Slice 1 — Retrieval works end to end (regulations)
- [x] T1: Local stack and package skeleton
- [x] T2: Ingest eCFR Title 26 into Postgres + Qdrant
- [x] T3: Hybrid search CLI with citations

### Checkpoint 1
- [ ] `taxcite search "…"` returns relevant 26 CFR sections for 3 hand-picked questions

### Slice 2 — Measure retrieval, add publications, pick the embedding model
- [x] T4: Pilot set (20 questions) and retrieval eval script
- [x] T5: Ingest IRS Publications
- [x] T6: Embedding-model benchmark (≥2 candidates) and the decision recorded
- [x] T6b: ADR-17 revisit trigger — Qdrant vs. pgvector (hybrid recall, filtered-recall loss, latency, size)

### Checkpoint 2 (human review: embedding decision)
- [x] Recall@10/nDCG@10 recorded for dense-only vs. hybrid across each candidate; model locked
- [x] ADR-17 confirmed or reopened from the T6b Qdrant-vs-pgvector numbers

### Slice 3 — Answers, baseline, pick the LLM
- [x] T7: Cited answer generation and closed-book baseline
- [x] T8: ADR-11 LLM benchmark (quality per dollar) and the decision recorded

### Checkpoint 3 (human review: ADR-11 decision)
- [ ] Pilot scores for closed-book vs. RAG per candidate model; projected monthly cost under $50

### Slice 4 — Delivery
- [x] T9: ADR-9 job record + SSE transport
- [x] T10: Phase A exit report

### Checkpoint: Phase A complete
- [x] All Phase A acceptance items met; ready to plan Phase B

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| The pilot set needs tax-domain judgment to label gold sections | High | Claude drafts questions and gold citations from the ingested text, and the user reviews all 20 before any numbers count. The set stays at 20, per §7. |
| eCFR XML structure is messier than expected (nested paragraphs, tables) | Med | Get T2 working on one Part (§1.1-1 area) first, then scale up. Tables are kept as text in Phase A. |
| Local embedding on a Mac CPU is slow for a full Title 26 re-index per candidate model | Med | Benchmark on a fixed subset (the Parts the pilot questions touch, plus distractors), not the full title. Document the subset. |
| LLM API keys and spend for the benchmark | Med | Cap the benchmark at 20 questions × ≤3 models × 2 modes. The script prints the running cost and stops at a configurable limit. |
| IRS PDF extraction quality (multi-column, tables) | Med | Use `pypdf` text extraction. Pages that come out empty or garbled are marked `extraction_failed` and excluded (§3.2 rule), never silently indexed. |
| No public statute (26 U.S.C.) in Phase A skews compound questions | Low | By design (§7): the pilot set is limited to regulation and publication questions. Statute is ingested in Phase B. |

## Resolved Inputs (2026-09-18)

- **Embedding:** `BAAI/bge-small-en-v1.5` is the primary candidate. §3.2 requires ≥2 candidates, so T6 benchmarks it against one challenger (default `nomic-embed-text-v1.5`, long-context).
- **LLM providers for ADR-11:** Anthropic and OpenAI (keys available). T8 benchmarks the budget tier of each (Claude Haiku 4.5, plus OpenAI's current small model). A pricier model is considered for synthesis only if it fits under $50/mo. The judge model is always from the other provider (§9.2).
- **Statute source (§11.1):** decided. uscode.house.gov release-point XML is the content source, and GovInfo modified-since is used only for weekly change detection. Built in Phase B.
- **Pilot set:** Claude drafts, the user reviews every row (defaulted).

---
---

# Implementation Plan: TaxCite Phase B — Decomposition + Eval Infrastructure

_Approved 2026-09-21. Phase A's plan above is kept as history._

## Overview

Phase B (tech doc §7) adds the two corpora Phase A left out: the statute (26 U.S.C.) and Tax Court case law. It splits compound questions into sub-queries and builds the 100-question golden set (§9.1). It also makes RAGAS faithfulness a **standing** CI check: any PR that touches retrieval, prompts, reranking or verification fails if faithfulness on the golden set drops below 0.85.

The exit condition is evidence plus a check that enforces itself. A reviewer can `POST /queries` a compound question and watch a `decomposing` stage. The answer cites statute, regulation and case law. The golden-set ablation ladder is written down. A PR that breaks the synthesis prompt fails CI without anyone running anything by hand.

Source docs: `taxcite-technical-documentation.md` §3.2, §3.3, §5.1, §7, §9, §9.1, §11.1, §11.5–11.7, ADR-1/11 · `eval/results/phase_a.md` · `docs/intent/taxcite.md`.

## Architecture Decisions (for this phase)

- **Stores stay the same: Qdrant, Postgres, Redis.** Neo4j arrives in Phase C with the citation graph. Phase B's case-law chunks are its input, so they keep the CourtListener id, docket and reporter citation Phase C will need.
- **One Qdrant collection, separated by `source`.** Two new values join `ecfr` and `irs_pub`: `usc` and `case`. The existing `Chunk` and store code gain values, not new types. Routing by source is how decomposition avoids the dilution Phase A measured, where adding publications cost regulation retrieval 12.4 points.
- **The statute comes from uscode.house.gov USLM XML** (§11.1, already decided). All 1,900 live sections are loaded, not just the topics (B1). It is split by section, and by subsection `(a)` when long, into 200–500-token chunks, reusing the eCFR packing rules. Citations look like `26 U.S.C. § 183(d)`. The release point's Public Law id is stored as `source_revision`. GovInfo's weekly change check is deferred to Phase H's incremental reindexing, because nothing in B re-ingests on a schedule.
- **Case law is Tax Court opinions, limited to the golden set's topics**, like Phase A's 21 regulation section families. They are split into paragraph chunks of 150–400 tokens, each overlapping the previous by one paragraph (§3.2). **Citations are page pin-cites**, `T.C. Memo. 2021-115, at *4-5`, because opinions don't number their paragraphs (B3; the plan first assumed `¶14`). **Source: DAWSON, the Tax Court's own system, not CourtListener** (B1). CourtListener has about a fifth of the relevant opinions (108 vs 560 for §183) because memorandum opinions are mostly missing. Scope: T.C. and memorandum opinions filed 2000 or later, **the 50 newest per topic**, because DAWSON's search has no relevance ranking (B3): 307 opinions. Opinion metadata for Phase C (docket, judge, type) stays in the cached selection, `data/caselaw/opinions.json`.
- **Decomposition is one structured-output call** (`gpt-4o-mini`, ADR-11). It returns typed sub-queries (`statutory | case_law | client_fact`) and an as-of year.
  - Statutory sub-queries search `usc + ecfr + irs_pub`.
  - Case-law sub-queries search `case`.
  - Client-fact sub-queries are not searched in B, because client documents arrive in Phase G. The facts go straight to synthesis.
  - The as-of year is stored on the job but not used as a filter; filtering is Phase D.
  - A question that decomposes into one sub-query takes exactly Phase A's path.
- **Sub-query results are merged by grouping, not re-ranking.** The synthesis prompt lists sources under the sub-query that found them. Phase B doesn't need a fusion step across sub-queries.
- **Gold citations are groups, any one of which counts** (B2). Adding the statute "lost" a pilot question whose statute answer outranked its gold regulation, because a flat gold list can't credit an equally correct authority. Each golden-set row lists groups of interchangeable citations; a group is satisfied when any member is retrieved, and recall is satisfied groups over groups. A flat list, like the pilot's, is one citation per group, so Phase A's numbers are unchanged.
- **§9.1's counts are minimums, not caps** (B4 audit). The golden set grew past 25 statutory / 20 case-law rows to cover the topics practitioners ask about most; more rows also raise the set's resolution above one question = 2 points.
- **Compound and temporal rows carry gold sub-queries** (B5): one per gold group, with the source to search. They prove each gold group is reachable and give B7 a held-out yardstick for decomposition (routing and sub-query quality). They are measurement only; tuning never reads them.
- **Golden set vs. dev set.** `eval/golden.jsonl` (100 rows, §9.1) is the gate and the report. It is frozen once reviewed, and any change is a logged commit. All tuning (prompts, k, decomposition) happens on the dev set: the 18-question pilot plus ~12 new case-law and compound questions. This is the "held-out test set that isn't repeatedly tuned against" that §9 asks for.
- **Every row is written in B; some are only scored in later phases.** Each row carries `scored_from`:
  - B: statutory, case-law and compound rows.
  - Temporal rows run in B for faithfulness only. Their accuracy is scored from Phase D.
  - Insufficiency rows run in B, and their abstention rate is recorded but not gated.
  - The 5 adversarial rows need client documents, so they are written now and scored in Phase G.
- **The RAGAS gate scores the answers the pipeline actually gave.** Refusals are excluded from the faithfulness mean and reported as a separate refusal rate, so the gate can't be passed by refusing more. The RAGAS judge model comes from the other provider (`claude-haiku-4-5`), per ADR-11 and §9.2.
- **CI restores the corpus instead of rebuilding it.** Re-embedding takes hours (7 chunks/s), so the gate job restores a Qdrant snapshot and a `chunks` table dump. Both are published as a GitHub release asset, and a script regenerates them when the corpus changes. Embedding models are kept in the CI cache.

## Dependency Graph

```
B1 topic scope + source spike
   ├── B2 statute ingest ──┐
   └── B3 case-law ingest ─┤
                           ├──► B4 golden set: statutory + case law (45)
                           │        └──► B5 golden set: compound, temporal, insufficiency, adversarial (55)
                           │                    │
                           ├──► B6 cross-encoder rerank ───┐
                           │                               ▼
                           └────────────────────────► B7 decomposition ──► B8 RAGAS harness ──► B9 CI + gate
                                                                                                    │
                                                                                     B10 Phase B exit report
```

## Task List

Full task details are in `tasks/todo.md` (Phase B section).

### Slice 1 — The corpus: statute + case law
- [x] B1: Topic scope and source spike
- [ ] B2: Ingest 26 U.S.C. (statute)
- [ ] B3: Ingest Tax Court opinions (case law)

### Checkpoint 1
- [ ] `taxcite search "…" --source usc` and `--source case` return relevant hits for 3 hand-picked questions each

### Slice 2 — The golden set
- [x] B4: Golden set, part 1 — 27 statutory-only + 26 case-law-only (§9.1 counts are minimums)
- [x] B5: Golden set, part 2 — 30 compound + 11 temporal + 11 insufficiency + 6 adversarial

### Checkpoint 2 (human review: golden set)
- [x] All 111 rows reviewed by you; the validator passes; category counts meet §9.1's minimums; the set is frozen

### Slice 3 — Reranking and decomposition
- [ ] B6: Cross-encoder rerank
- [ ] B7: Query decomposition

### Checkpoint 3 (human review: does decomposition earn its place?)
- [ ] Ladder on the golden set: closed-book → dense → hybrid → +rerank → +decomposition. Decomposition helps compound questions, or the report says it doesn't.

### Slice 4 — The RAGAS gate
- [ ] B8: RAGAS faithfulness harness
- [ ] B9: CI in GitHub Actions + the RAGAS gate
- [ ] B10: Phase B exit report

### Checkpoint: Phase B complete
- [ ] All tests pass in CI; the RAGAS gate is live and green; ready to plan Phase C

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| ~~CourtListener bulk files too large to slice~~ | — | **Resolved by B1:** the bigger problem was coverage, and DAWSON replaced CourtListener. New risk in its place, below. |
| DAWSON's undocumented API changes | Med | The selection and PDFs are cached, so an API change can't alter an existing corpus; a changed response shape raises instead of indexing partial data; the endpoints are written down in `caselaw.py`. |
| Gold citations are chunk labels, so re-chunking can orphan them (B2 changed 84 regulation labels) | Med | The validator checks every gold citation exists in the corpus, and runs in CI (B9). |
| Labeling 100 rows needs tax judgment, and case law needs more than regulations did | High | Same method as the pilot: Claude drafts questions and gold citations from ingested text, and you review every row. The set is not reviewed by a tax professional, and that limitation is stated next to every published number. The work is split across B4 and B5 so the review comes in two batches. |
| Faithfulness starts below 0.85 | High | Fix it against the dev set, never the golden set. If the shortfall is structural, §9.3 allows recalibration, but only with the measurement written down. |
| A check graded by an LLM is noisy, so CI becomes flaky | Med | B8 measures the spread over 3 runs before B9 enforces anything. Generations are cached, so a re-run only re-judges. Temperature can't be the lever: current Anthropic models reject sampling parameters, and the judge is `claude-haiku-4-5`. The report states the noise band, and a gate inside its own noise is flagged. |
| Adding statute and case law to the same collection dilutes regulation retrieval again | Med | Routing by source in decomposition is the mitigation. B2 and B3 each record pilot recall before and after, so any dilution is measured, not guessed. |
| CI cost and runtime | Med | The gate runs only on PRs touching the listed paths. Estimated under $1 per run (to be measured in B8), with a hard per-run cap. The corpus is restored from a snapshot, and models are cached. |
| RAGAS pulls in LangChain, and its API changes often | Med | Pin the version. Fallback: implement its faithfulness metric directly (extract claims, check each against the retrieved context, take the ratio), in about 40 lines. |

## Resolved Inputs (2026-09-21, Claude's recommendations accepted)

- **Cross-encoder rerank is in Phase B (B6).** §9's ladder puts "hybrid+reranked" before "+decomposition", no phase scheduled a reranker, and Phase E's authority weighting assumes one exists. It also puts Phase A's section-vs-paragraph recall gap to use.
- **RAGAS: the library, version pinned**, so "RAGAS faithfulness" means what reviewers expect. Fall back to our own implementation of the metric if the dependencies cause trouble.
- ~~Holding/dicta tags: the field is added in B3 and left empty.~~ **Changed in B3:** no empty column. Nothing reads it until Phase E, which adds the column with values, the way B2 added `source_revision`.
- **CI corpus: a Qdrant snapshot plus a Postgres `chunks` dump, published as a GitHub release asset.** A self-hosted runner on the Mac was rejected as fragile.

---

# Phase C Implementation Plan: Citation graph

_Drafted 2026-09-26 from the C0 spike. Claude revised the phase under your standing permission to change the plan when findings require it. The reasons are in ADR-1 (revised) and engineering log #53._

## Overview

The tech doc's Phase C (§7) built a citation graph to widen case-law search. C0 measured that before building it, and the ceiling is **0 points**: none of the case-law gold that decomposition misses is within two citation hops of anything retrieved. So the phase keeps the graph but gives it a job that pays off, and moves the recall work to where the gap actually is.

**What Phase C delivers:**
1. **Negative treatment.** When an answer relies on a Tax Court opinion that was later reversed, overruled or is on appeal, the answer says so. This is the question every practitioner asks of a case ("is it still good law?"). Three golden rows already test it (G-C03, G-X02, G-X09), and two check it doesn't over-flag (G-C06, G-X19).
2. **Page selection.** 23.1 of the 30.8 missed case-law points were the right opinion at the wrong pages. C2 found 15.4 of them were answer keys that were too narrow (fixed, approved); the real gap is **2 rows, 7.7 points**, against an audited baseline of **0.833 ± 0.018** (3 cached plan sets).
3. **Graph expansion as a measured rung**, not a gate. It goes on the ablation ladder with its honest number.

**Exit condition:** a reviewer asks about CRP payments (G-X02) and the answer cites *Morehouse* with a visible "reversed by the Eighth Circuit" flag. The ladder shows what expansion and page selection each add, including zero.

Source docs: tech doc §3.2, §5.2, §7, §9.3, ADR-1 (revised) · `eval/results/phase_b.md` · `tasks/todo.md` C0.

## Architecture Decisions (for this phase)

- **No graph database: the edges are two Postgres tables (ADR-23).** `citations (citing, cited)` and `treatments (citation, kind, by_citation, source, recorded_at, checked_at)`, keyed by the corpus citation (`T.C. Memo. 2021-115`, `119 T.C. No. 5`). Opinions we cite but don't hold appear as keys with no chunks. Appellate opinions appear only as `by_citation`; there is still no appellate corpus. *Changed 2026-09-26, you confirmed:* the first draft of this plan kept Neo4j, but the treatment check is a lookup by key, not a traversal.
- **Edges follow what reads them.**
  - `CITES`: from eyecite, over the opinion text C0 already extracts.
  - `AFFIRMED_BY`, `REVERSED_BY`, `OVERRULED_BY`: from subsequent history. Our own corpus supplies some ("140 T.C. 350 (2013), *rev'd*, 769 F.3d 616"), and C1 measures how much, plus what CourtListener adds.
  - `DISTINGUISHES` is dropped: it needs an LLM pass and nothing reads it. `AMENDS` is statute versioning, which is Phase D.
- **Reported T.C. opinions get an alias.** They are cited by volume and page (`119 T.C. 121`) but keyed by slip number (`119 T.C. No. 5`). C0 recovered 10 of 28 by surname match. C3 makes that a table, checked by hand.
- **Treatment is looked up at synthesis, not in retrieval.** For each opinion the answer cites, read its treatment edges and attach a flag to the citation: `reversed`, `overruled`, `on appeal` or `affirmed`. The flag travels in the answer payload and the SSE `answer` event. The answer text doesn't change; Phase E decides whether treatment should also change ranking.
- **The lookup fails open.** If the treatment table can't be read, the answer is unchanged and marked "treatment unknown", never "good law".
- **The golden set stays frozen except through its audit rule.** C2 may widen gold groups (adding pages that state the same holding) only as a logged commit that you review, the same process as the B4/B5 audits. It never narrows them. Whether a page "states the holding" is judged from the opinion text, not from what the retriever returned.

## Dependency Graph

```
C0 reachability spike ✅
   ├── C1 treatment-source spike ──► C3 edge tables ───► C4 treatment flags ──┐
   │                                      └──► C5 expansion rung (ablation) ───┤
   └── C2 wrong-page audit ──► C6 page selection ─────────────────────────────┤
                                                                              ▼
                                                                  C7 Phase C exit report
```

## Task List

Full task details are in `tasks/todo.md` (Phase C section).

### Slice 1 — Find out what's there
- [x] C0: Citation-graph reachability spike
- [x] C1: Treatment-source spike: where "reversed / on appeal" data comes from, and how much
- [x] C2: Wrong-page audit of the 6 golden rows (all 6 widened; Recall@20 0.692 → 0.833 ± 0.018 on the audited set)

### Checkpoint 1 (human review)
- [x] You approve C2's gold changes, if any. The treatment source is chosen from C1's numbers

### Slice 2 — The graph
- [x] C3: Citation and treatment edge tables in Postgres (with the 200-edge hand-labeled sample): CITES 100% / 99.9%, treatment 98.7% / ~95%
- [x] C4: Treatment flags in answers (gate met: 3/3 reversed flagged, 0 false flags; 26/26 held-opinion flags match hand-verified records)
- [x] C5: Graph expansion as an ablation rung (−3.8 points case-law, −2.3/−4.1 overall, +0.55 s; zero gains)

### Slice 3 — The real recall gap
- [x] C6: Page selection (scope set by C2): key-aware eval shipped, baseline 0.777 ± 0.029; page selection stopped, dev can't measure it

### Checkpoint: Phase C complete
- [x] C7: Phase C exit report (`eval/results/phase_c.md`). Gate met: edges ≥90% precision / ≥85% recall; 3/3 reversed rows flagged; G-C06 and G-X19 not flagged. Ladder shows expansion and page selection with their measured deltas

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| No reliable source for appellate outcomes: DAWSON doesn't track appeals, and CourtListener's coverage of unpublished dispositions is incomplete | High | C1 measures coverage before anything depends on it. A missing record shows as "treatment unknown", never as "good law". The flag says which source it came from. |
| Treatment flags give false comfort: "no flag" read as "good law" | High | The absence of a flag is displayed as "no negative treatment found in <sources>", not as a clean bill. |
| The wrong-page audit is contaminated: Claude has already seen the retriever's output for these rows | Med | You judge each change from the opinion text. Gold groups may only widen, never narrow, and every change is a logged commit. |
| Page-selection tuning overfits the 6 rows | Med | Tune on the dev set only. The golden set scores once, at the end, as in Phase B. |

---

# Phase D Implementation Plan: Temporal validity

_Approved 2026-09-27 with Claude's defaults below. Revised the same day after D0, and you confirmed the changes: versioning dropped, publication valid time and a statutory-recall task (D3b) added, gate unchanged. The reasons are in D0 (`tasks/todo.md`) and engineering log #65. Phase C's plan above is kept as history._

## Overview

The tech doc's Phase D (§7) adds valid time and transaction time to chunks, filters retrieval by the question's as-of year, and versions amendments at ingestion. Its gate: **≥90% accuracy on a held-out set of retroactive/amended-rule questions** (§9.3). The held-out set is the 11 temporal golden rows (G-T01–G-T11), which have run since Phase B for faithfulness only.

**What D0 measured (2026-09-27):** today 1 of 11 temporal rows is right, and that one unfaithfully.
- **Retrieval blocks 8 rows before time matters.** Temporal gold Recall@20 is 0.200. The question's plain words match IRS publications and regulations rather than the statute, even though each row's legal-vocabulary sub-query ranks its statute 1st–4th.
- **No row needs an earlier version of the text,** so the spec's amendment versioning is not built.
- **Two rows need an effective date** that only the statutory notes carry (G-T02, G-T10).
- **Four rows need synthesis to reason about the year** (G-T01, G-T04, G-T09, G-T11).
- **One row is outside every source** (G-T03).

So the phase does three things:
1. **Time in retrieval.** Publications get valid time from their edition year, which removes the plain-English competitor for a dated question (0.200 → 0.350, measured). Statute recall on dated questions gets its own task (D3b).
2. **Effective dates** from the statutory notes, so the system knows when today's text began to apply.
3. **Year-aware answers.**

**Exit condition:** a reviewer asks G-T02 ("the §179 limit for property placed in service in 2023"). The answer doesn't apply today's $2.5M. It says the current limit applies from taxable years beginning after 2024 (the 2025 amendment's note), and that the 2023 figure isn't in its sources. It names the tax year it answered for. The ladder shows what the filter adds to temporal rows and what it costs everywhere else (at most 2 points).

Source docs: tech doc §5.3, §7, §9, §9.3, ADR-2, ADR-17 (the 22% filtered-ANN note) · `eval/results/phase_c.md` · engineering log #40–41, #65.

## Architecture Decisions (for this phase)

- **Valid time is two new columns, not a new table:** `effective_date` and `superseded_date` (null = open) on `chunks` and in the Qdrant payload. The existing `as_of` column is *not* valid time: it records the download date or publication edition. It keeps that meaning, and the report says so.
- **Where the dates come from:**
  - **Publications:** the edition year gives the tax year the edition is written for, so Pub 17 (2025) is valid for tax year 2025.
  - **Statute:** the effective date of the latest amendment note, where D4 can read one; otherwise undated.
  - **Regulations and case law:** undated in this phase.
- **No amendment versioning (changed after D0).** No temporal row needs an earlier version of the text, so earlier release points are not ingested. When the as-of year falls before today's text took effect, the answer says the earlier version isn't in its sources. It doesn't apply today's rule, and it doesn't guess. Chunk keys don't change. **To reopen:** a golden or dev row whose correct answer needs earlier statutory text.
- **The filter applies only when the decomposer finds an as-of year.** It keeps chunks where `effective_date ≤ as_of < superseded_date`. For a publication, that is its own edition year. Undated chunks always pass, so the filter never hides the only copy of a section. A statute chunk whose current text began after the as-of year stays in, flagged to synthesis, because it is still the best available evidence and the answer must say it may not apply. With no as-of year, the answer is about current law and says so.
- **Filtered search is exact, not approximate.** ADR-17 measured a 22.1% loss for approximate top-10 search under a strict filter, in both stores, and a date filter has the same shape. At 28k points, exact search is a brute-force scan of a few milliseconds. D3 measures both before choosing, and the ladder records the cost.
- **Statute recall on dated questions is its own task (D3b, added after D0).** The pipeline searches with the question's words (log #44, measured on dev). For temporal rows that finds publications. The planner's rewritten sub-queries reached 0.250, below the filter alone. Candidates are chosen on D1's dev rows, never on golden.
- **Effective dates come from USLM's statutory notes, read selectively.** Only "Effective Date of [year] Amendment" notes are read, not the whole notes body, and cross-references are followed (§224's date is a note "under section 45B"). Each date gets a hand-checked accuracy figure (§3.2's pattern), like Phase C's edges.
- **Transaction time is kept, but only in Postgres.** `recorded_at` (from `fetched_at`) and `retired_at`: a re-ingest retires a superseded row instead of the sweep deleting it. Retired text is removed from Qdrant as it is today, because retrieval never reads it. "What did TaxCite believe on date Y" is a SQL query for audit (ADR-2), not a retrieval mode. No golden row tests it; see Resolved Inputs.
- **Temporal accuracy is scored two ways per row.**
  - **As-of extraction:** does the decomposer's year match the row's? D0 found "as-of" means two things: the return's tax year (substantive rules) and the date of an event like a claim or an audit (procedure). D2 fixes the rule, and gold rows with an event date also record the tax year. A plan with one year can't express G-T01's two years, and D2 scores that row by its answer alone.
  - **Answer correctness for that year:** an LLM judge from the other provider checks the answer against the reference answer (§9.2's rubric, including its "wrong tax year" and "superseded rule applied" defect tags). A second judge checks the first, and the score is reported only if Cohen's κ ≥ 0.7.
  - **Grounding is reported, not gated** (decided after D2): each answer is also checked claim by claim against its sources, because the reference-answer judge can't tell a right answer from memory from one the sources support.
  - A row passes only if both do. The gate is 10 of 11 rows. **One row is 9.1 points**, so the gate allows exactly one miss, and the report says that.
- **The gate is at risk, and is kept as written.** G-T03 needs the sufficiency gate (Phase F), so it is probably the one allowed miss. G-T05 and G-T07 turn on date arithmetic (the §7503 weekend rule, the §6651(c)(1) offset) that no temporal mechanism supplies. They pass only if retrieval brings their statute in and synthesis does the arithmetic. Not met is a valid outcome, reported as such.
- **Tuning happens on dev, which first needs temporal rows.** Dev has none today (only D24 carries an as-of year). C6 stopped at this exact wall, so D1 writes dev temporal rows before anything is tuned. The golden set's audit rule still applies: logged commits you review, and no citation or opinion shared between sets.

## Dependency Graph

```
D0 temporal failure spike ✅
   ├── D1 dev temporal rows ──────────────────────────────────────┐
   ├── D2 temporal scorer (as-of + judged answer) ────────────────┤
   └── D3 valid-time columns + as-of filter (pubs by edition) ─┬──┤
            ├── D3b statute recall on dated questions (dev) ───┤  │
            ├── D4 effective dates from USLM notes ────────────┤  │
            └── D6 transaction time ───────────────────────────┘  │
                                                                  ▼
                                      D7 as-of-aware synthesis (tuned on dev)
                                                                  ▼
                                                     D8 Phase D exit report
```

## Task List

Full task details are in `tasks/todo.md` (Phase D section).

### Slice 1 — Find out what the temporal rows need
- [x] D0: Temporal failure spike (1/11 right today; retrieval blocks 8; no row needs an earlier version)
- [x] D1: Dev temporal rows (14, D26–D39, validated in two scans, approved)
- [ ] D2: Temporal scorer (built and calibrated: dev 0.381 ± 0.041, κ ≥ 0.81; as-of change applied; awaiting your verdict read)

### Checkpoint 1 (human review)
- [x] You confirm D0's decision: D4 built (G-T02, G-T10), D5 dropped, D3b added
- [x] D1's rows are approved

### Slice 2 — Time in retrieval
- [x] D3: The as-of filter (publications dated by edition): built, window ed-1 chosen on dev recall; **off live until D7** (it cost dev answers 0.36–0.43 → 0.29)
- [x] D3b: Statute recall on dated questions (statute search + 1 slot, live; golden 0.563 → 0.602, temporal 0.200 → 0.400)
- [x] D4: Effective dates from statutory notes (1,795 statute chunks dated; fresh hand check 48–49/50)
- ~~D5: Prior versions of changed sections~~ (dropped after D0: no row needs one)
- [x] D6: Transaction time: retire, don't delete (a trigger into `chunk_versions`, covering in-place rewrites too; `store.held_at` answers "what did TaxCite hold on date Y")

### Slice 3 — Answers
- [x] D7: As-of-aware synthesis (dev 0.381 → 0.452; **golden gate not met: 0.394, 4–5 of 11**; the edition filter stays off)

### Checkpoint: Phase D complete
- [x] D8: Phase D exit report (`eval/results/phase_d.md`): gate **not met**. Gate ≥90% (10/11) on the temporal rows, stated as met or not; ≤2-point regression on other categories; CI green with a new snapshot

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Retrieval, not time, blocks most temporal rows (D0: 8/11), so temporal mechanisms alone can't reach the gate | High | D3's publication filter (measured +15 points) and D3b target it directly; D8 reports the gate with both, and not met is a valid outcome |
| The gate is 11 rows, so one row is 9.1 points; a noisy judge can pass or fail it alone | High | Each row is scored on both parts; the judged part runs ≥3 repeats and reports its spread; the report lists every row, not just the total |
| Some rows can't pass from any source in the corpus (G-T03's rescheduling is a DEA rule, not tax text) | High | The correct answer is an honest "the corpus can't establish this", and G-T03's reference answer says so (checked in D0). Never reword the question to make it pass |
| D3b's recall fix helps temporal rows and hurts the rest (log #44 chose question wording on dev for a reason) | High | Chosen on dev; every golden category re-scored, ≤2-point regression, ≥5 plan sets |
| The as-of filter hides the only copy of a section, or the decomposer invents a year | High | Undated chunks always pass the filter; the filter needs an extracted year; statute whose text began later stays in, flagged; D3 measures every non-temporal golden row with the filter on (≤2-point regression) |
| Dropping a publication edition removes the only source that states a year's figure (G-T11's cutoff is in Pub 463 (2025)) | Med | Only editions whose year differs from the as-of year are dropped; G-T11 asks about 2025 and keeps its 2025 edition. Dev rows cover a year with no matching edition |
| Effective-date notes are free text, and some are cross-references to another section's note | Med | A hand-checked sample with a stated accuracy target; cross-references followed; an unparsed note leaves the date null (always passes), never a guess |
| Tuning on the 11 golden rows | Med | D1 first; the golden temporal rows score once, at the end |

## Resolved Inputs (2026-09-27, Claude's defaults confirmed)

- **Transaction time: build the minimum (D6), with no retrieval mode.** ADR-2 decided both time dimensions, and retiring instead of deleting is one column plus a changed sweep. A transaction-time *query* path ("answer as TaxCite would have on date Y") has no row that tests it and nothing that reads it, so it isn't built. Alternative: defer D6 to Phase H's incremental reindexing, where re-ingest becomes routine.
- **Questions with an ambiguous year (G-T09) are answered for current law, with the change stated,** not sent back with a clarifying question. The API has no conversation turn to ask one in.
- **Sources outside the corpus stay out.** G-T03 turns on a DEA scheduling rule. Adding Federal Register rules is its own ingestion source. D0 reports what it would unlock, and adding it is your call. G-T03's correct answer is an honest limit ("the statute says X; scheduling is outside the sources"). D0 checks that its reference answer says that.

---

# Phase E Implementation Plan: Authority-aware retrieval

_Drafted 2026-09-28; approved the same day with Claude's four defaults below. E0 is a go/no-go on E4. Phase D's plan above is kept as history._

## Overview

The tech doc's Phase E (§7, §5.5, ADR-8) tags every chunk with an authority profile at ingestion, uses it as an explicit reranking signal, and shows each citation's authority in the answer. **Gate (§9.3):** authority metadata ≥95% field-level accuracy on a 150-chunk hand-labeled sample; reranking changes the top-1 result on a curated authority-conflict subset, with ≤2 points of Recall@20 regression elsewhere.

**What is known before building (one plan set, golden, shipped `route+statute1`, `retrieval-golden-2026-09-27-k20-d3b.json`):** on the 28 statutory rows, top-1 is an IRS publication on 14, a Tax Court opinion on 6, a regulation on 4 and the statute on 6. The gold chunk is top-1 on 3. Phase A measured the same thing another way: publications cost regulation recall 12.4 points. So lower-authority sources outranking the controlling one is common, not an edge case. **But Phase D's filter taught the counter-lesson:** the publication that outranks the statute is often the only plain-English evidence for the answer (D32). Authority must reorder, never remove.

**What doesn't exist yet:**
- **No authority-conflict subset.** No golden or dev row is tagged as one, and the gate needs it. Two golden rows come close: the Eleventh Circuit reversal read through the post-remand opinion, and the reversed *Morehouse*/*Menard* rows (Phase C).
- **Most spec fields have one value across this corpus.** Every opinion is the Tax Court's; every source is federal; there are no circuit opinions, Revenue Rulings or proposed regulations. The fields that vary are few: source type, T.C. vs. Memo., temporary vs. final regulation, and negative treatment (Phase C). A uniform 150-chunk sample would pass 95% on the constant fields alone, so the sample is stratified (E3).

So the phase opens with a spike (E0), as C and D did, and writes its conflict rows (E1) before anything is tuned.

**Exit condition:** a reviewer asks a statutory question whose plain words match Pub 17. The statute (or regulation) is top-1 and Pub 17 is still in the eight sources synthesis reads. Each citation in the answer carries a label from structured fields ("Statute", "Treasury regulation", "Tax Court (reported)", "Tax Court memorandum", "IRS publication: not binding"; reversed opinions flagged, as in Phase C). The ladder shows what the authority rung adds on the conflict subset and what it costs everywhere else (≤2 points).

Source docs: tech doc §3.2, §5.5, §7, §9, §9.3, ADR-8, ADR-13 · `eval/results/phase_a.md` (the 12.4 points) · `eval/results/phase_c.md` (treatment) · `eval/results/phase_d.md` (the filter that removed evidence).

## Architecture Decisions (for this phase)

- **The authority profile is computed by one function from structured fields, and stored.** `authority(chunk)` reads `source`, the citation's form (T.C. No. vs. T.C. Memo.; a `T` suffix on a regulation section) and Phase C's `treatments` table. It is stored as one `authority` jsonb column on `chunks`, like D4's `effective`, so the hand check, the reranker and the answer labels all read the same stored value (ADR-13: badges come only from ingestion fields). Backfilled, no re-embed. A field with no source for its value is stored as `"unknown"` and logged (FR-16), never defaulted.
- **Spec fields that are constant in this corpus are recorded once, not tagged per chunk.** `court`, `jurisdiction` and `binding_on` are stored where they vary (the reversing circuit in a treatment) and documented as constants otherwise. E0 confirms which. If a later source (circuit opinions, Revenue Rulings) makes one vary, it gets a value then.
- **Not in the Qdrant payload.** The reranker runs after search, on `Hit`s, so nothing filters on authority. Add it to the payload only if a filter needs it.
- **Authority reorders; it never filters.** The candidate is a prior added to the cross-encoder score by authority level, inside `decompose.chunks()`, where the statute slot already lives. Alternatives E4 compares on dev: a per-level additive prior; a tie-break only within a score margin; a reserved "controlling" slot (the statute slot generalised). Nothing is removed from the pool, so a publication can still reach synthesis on relevance. **Added after E0:** searching deeper than synthesis reads, because 45.6 of 119 golden gold groups aren't in the k=8 pool at all, and no prior reaches them.
- **No blanket demotion for negative treatment (changed after E0).** The same reversed opinion is the answer to G-C03 (how did the Tax Court decide *Morehouse*?) and the thing to demote for G-X02 (an Iowa client, Eighth Circuit). Which one applies is the taxpayer's circuit, `binding_on`, so it waits for Phase G. Phase C's flag stays on every answer.
- **The gate's "changes top-1" is scored as "the controlling source becomes top-1".** Changing top-1 to the wrong chunk shouldn't count. Each conflict row names its controlling source; the score is the share of rows where it's top-1, before and after. Also reported: whether the lower-authority source is still in synthesis depth (k=8), which is D32's lesson made a metric.
- **Tuning happens on dev; the golden conflict subset is scored once, at the end.** E1 writes both before E4 starts. The golden audit rule applies: logged commits you review, no citation shared between sets.
- **Answers are reported, not gated, and sampled properly.** Phase D's handoff: an answer-level metric on few rows needs several generated answers per row. `eval/temporal.py --samples N` (or the same flag on the faithfulness harness) is built in E5 before any answer number is quoted. The faithfulness gate and its refusal-rate check run as usual.

## Dependency Graph

```
E0 authority spike (where authority costs, which fields vary, which rows conflict)
   ├── E1 authority-conflict rows (dev + golden subset) ──────────┐
   └── E2 authority profile at ingestion (+ backfill) ─┬──────────┤
            └── E3 150-chunk stratified hand check ────┤          │
                                                       ▼          ▼
                                      E4 authority-weighted rerank (tuned on dev)
                                                       ▼
                                      E5 authority in answers (labels, prompt, --samples)
                                                       ▼
                                                E6 Phase E exit report
```

## Task List

Full task details are in `tasks/todo.md` (Phase E section).

### Slice 1 — Find out where authority costs
- [x] E0: Authority spike (~20 rows inverted at top-1, ~15 displaced, stable over 5 plan sets; 1 of 15 lower sources was better evidence: **E4 go**)
- [ ] E1: Authority-conflict rows (dev + golden subset)

### Checkpoint 1 (human review)
- [x] You confirm E0's field list and the conflict-row definition (2026-09-28)
- [ ] E1's rows are approved

### Slice 2 — Metadata
- [ ] E2: Authority profile at ingestion
- [ ] E3: Stratified 150-chunk hand check (≥95% field-level)

### Slice 3 — Ranking and answers
- [ ] E4: Authority-weighted rerank
- [ ] E5: Authority in answers

### Checkpoint: Phase E complete
- [ ] E6: Phase E exit report (`eval/results/phase_e.md`): both gates stated as met or not; ≤2-point regression per category; CI green with a new snapshot

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Boosting the statute pushes the plain-English publication out of synthesis depth, and answers get worse (D3's filter did exactly this) | High | Reorder only, never filter; E4 reports "lower-authority source still in k=8" and dev answers with `--samples`, not recall alone |
| The 95% metadata gate passes vacuously on constant fields | High | Stratified sample (E3): most labels go to the fields that vary; accuracy reported per field, and the gate is read per field |
| "Changes top-1" passes by changing it to the wrong chunk | Med | Scored as "controlling source becomes top-1" (E1 names it per row) |
| The conflict subset is small, so one row is many points (Phase D: 9.1 points a row) | Med | E1 aims for ≥10 golden and ≥10 dev rows; the report lists every row |
| The statute is the right authority but the wrong section (G-T08: the slot went to §225) | Med | Out of E's gate; E4 reports G-T08's rank as a side effect, not a target |
| Tuning on the golden subset | Med | E1 before E4; golden conflict rows scored once, at the end |
| Answer-level numbers on few rows are one sample of a brittle generator (Phase D: 0.394 → 0.152) | Med | `--samples` in E5 before any answer number is quoted |

## Resolved Inputs (2026-09-28, Claude's defaults confirmed)

- **Publication tables (G-S28, Pub 946's depreciation caps) are not in Phase E.** The tech doc lists them under "Phase E (publication handling)", but it's a chunking and extraction problem, not authority. Default: record it as open with no phase; you can move it into E as E7.
- **The 12.4-point publication dilution is reported, not gated.** Phase A named restoring it as E's baseline to beat, measured on regulations-only before routing existed. E4 reports regulation recall with and without the rung; the gate stays §9.3's.
- **Conflict subset: new golden rows, written before E4, reviewed by you.** Alternative: tag existing rows only (probably 3–5 rows, too few to read).
- **`binding_on` / Golsen is documented, not modelled.** Which circuit's law binds the Tax Court depends on the taxpayer's residence, a client fact. Without client documents (Phase G) there is nothing to key it on. Default: store the reversing circuit where a treatment has one; revisit in Phase G.
