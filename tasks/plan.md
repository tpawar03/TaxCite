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
