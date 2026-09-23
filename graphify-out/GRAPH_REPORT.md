# Graph Report - TaxCite.nosync  (2026-09-23)

## Corpus Check
- 66 files · ~383,556 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 3, .jsonl 3, .xml 2)

## Summary
- 814 nodes · 1556 edges · 41 communities (38 shown, 3 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 102 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d376b291`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_metrics.py
- test_irs_pubs.py
- test_jobs.py
- T2: Ingest eCFR Title 26
- paragraphs
- test_ecfr.py
- cli.py
- Decomposition
- TaxCite — Engineering Log
- ecfr.py
- test_generate.py
- TaxCite
- TaxCite Phase A — Task List
- Phase A Implementation Plan
- Task List
- ADR-17: Vector Store — Qdrant, Not pgvector
- TaxCite — Phase A exit report
- ADR-11: LLM Tiering — gpt-4o-mini
- test_decompose.py
- T5: Ingest IRS Publications
- Log #24: Adding a Second Corpus Made Retrieval Worse
- taxcite
- Collaborative Working Mode
- SubQuery
- ADR-12: Backup and Disaster Recovery
- Postgres
- test_usc.py
- llm_bench.py
- retrieval.py
- jobs.py
- store_bench.py
- source_filter
- ragas_eval.py
- caselaw.py
- eCFR Chunking Decisions
- search
- generate.py
- Ingestion Pipeline (§3.2)
- call_model
- retrieve.py
- Decisions Log

## God Nodes (most connected - your core abstractions)
1. `TaxCite — Engineering Log` - 33 edges
2. `search()` - 26 edges
3. `Hit` - 20 edges
4. `conn()` - 18 edges
5. `Chunk` - 17 edges
6. `TaxCite Phase A — Task List` - 16 edges
7. `ingest_ecfr()` - 15 edges
8. `ingest_case()` - 14 edges
9. `of()` - 14 edges
10. `estimate_tokens()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `PII Redaction Ordering as a CI Invariant` --semantically_similar_to--> `Log #18: The Counts-Match Check Caught Silent Data Loss`  [INFERRED] [semantically similar]
  taxcite-technical-documentation.md → docs/engineering-log.md
- `judged()` --uses--> `Judged`  [INFERRED]
  tests/test_metrics.py → eval/ragas_eval.py
- `test_a_refusal_is_not_scored_as_zero_or_as_one()` --calls--> `aggregate()`  [INFERRED]
  tests/test_metrics.py → eval/ragas_eval.py
- `test_aggregate_counts_claims_and_unsupported_claims()` --calls--> `aggregate()`  [INFERRED]
  tests/test_metrics.py → eval/ragas_eval.py
- `test_an_answer_with_no_claims_is_reported_not_averaged()` --calls--> `aggregate()`  [INFERRED]
  tests/test_metrics.py → eval/ragas_eval.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]
- **Measurements That Overturned a Stated Intuition** — docs_engineering_log_measured_ablation, docs_engineering_log_publication_dilution, docs_engineering_log_mis_specified_revisit_trigger, docs_engineering_log_parallel_embedding_slower, docs_engineering_log_judge_rubric_mismatch [INFERRED 0.85]

## Communities (41 total, 3 thin omitted)

### Community 0 - "test_metrics.py"
Cohesion: 0.11
Nodes (27): main(), score(), mrr(), ndcg_at_k(), recall_at_k(), The section a citation belongs to, ignoring paragraph depth. '26 CFR…, section_of(), judged() (+19 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.06
Nodes (42): skipif, dehyphenate(), edition_year(), fetch(), _normalise(), page_texts(), parse(), Path (+34 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.06
Nodes (41): fastapi_testclient, pytest, chunks(), ctx(), models_(), fixture, sync(), test_both_vectors_are_stored() (+33 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.14
Nodes (14): Log #18: The Counts-Match Check Caught Silent Data Loss, Log #13: The iCloud Bug That Broke Editable Installs, Log #4: Italic Designations Are a Different Hierarchy Level, Log #15: Fixtures From Real Edge Cases, Not Invented, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense (+6 more)

### Community 4 - "paragraphs"
Cohesion: 0.15
Nodes (15): Client, LTTextBox, fetch(), fold_numbers(), font_size(), get(), load_selection(), paragraphs() (+7 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.07
Nodes (41): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+33 more)

### Community 6 - "cli.py"
Cohesion: 0.06
Nodes (70): asyncio, BackgroundTasks, BaseModel, Connection, fastapi, fastapi_responses, get, io (+62 more)

### Community 7 - "Decomposition"
Cohesion: 0.21
Nodes (10): answer(), chunks(), decompose(), Decomposition, (sub-query, its chunks) for the synthesis prompt, limited to `keep` if given.…, One structured-output call (ADR-11). Temperature 0 and a fixed seed, so a re-…, Search once per sub-query, filtered to the sources its kind allows. Fills…, The k chunks synthesis sees: every sub-query's hits, ordered by the cross-… (+2 more)

### Community 8 - "TaxCite — Engineering Log"
Cohesion: 0.06
Nodes (33): 10. Keep live delivery separate from tracing, 11. Stay true to the architecture but defer stores until they have work, 12. Vercel is the wrong host for this backend, 13. The iCloud bug that silently broke editable installs, 14. Table-of-contents sections would poison retrieval, 15. Test fixtures chosen from real edge cases, not invented, 16. Parallel workers made embedding slower, not faster, 17. The chunker's output is 12× the section count (+25 more)

### Community 9 - "ecfr.py"
Cohesion: 0.10
Nodes (46): Chunk, estimate_tokens(), The unit every ingester produces and every store consumes., Make `part` a running count per citation, so `key` is unique by construction.…, renumber(), pages_label(), parse(), make() (+38 more)

### Community 10 - "test_generate.py"
Cohesion: 0.08
Nodes (11): fixture, Answer generation, tested without spending money: the model call is stubbed., Sampling at the default temperature made the same question answerable two ways,…, Replace the model call; record what it was asked., Chunk citations are sometimes ranges; citing one paragraph inside is precision,…, A citation not among the sources is the failure mode this system exists to…, stub(), test_a_narrower_paragraph_of_a_retrieved_section_counts_as_derived() (+3 more)

### Community 11 - "TaxCite"
Cohesion: 0.15
Nodes (23): Log #5: Corpus Gaps Shape the Evaluation, Confirmed Intent, TaxCite, TaxCite PRD, Functional Requirements FR-1..FR-17, Goals G1-G6 (research time, seat displacement, groundedness, gates, cost, leakage), Non-Functional Requirements (latency, reliability, cost, security), Non-Goals (no full GraphRAG, no BM25 engine, no token streaming, federal only) (+15 more)

### Community 12 - "TaxCite Phase A — Task List"
Cohesion: 0.10
Nodes (24): Qdrant Service (compose), Log #21: Gold Sets Need Validating Before They Can Validate Anything, Log #19: Hybrid Retrieval Is Not Uniformly Better Than Dense, Log #20: Measurement Overturned What One Query Suggested, The Pilot Set Is Data, Not Code, ✅ Checkpoint 1 — after T1–T3, ✅ Checkpoint 2 — after T4–T6, ✅ Checkpoint 3 — after T7–T8 (+16 more)

### Community 13 - "Phase A Implementation Plan"
Cohesion: 0.22
Nodes (11): Log #11: Stay True to the Architecture, Defer Stores Until They Have Work, Log #9: Redis vs Postgres LISTEN/NOTIFY for Live Events, Log #10: Keep Live Delivery Separate From Tracing, Log #12: Vercel Is the Wrong Host for This Backend, Simplify Inside Components, Never By Dropping a Store, Plain-Module Package Layout, Phase A Implementation Plan, Phase A Risks and Mitigations (+3 more)

### Community 14 - "Task List"
Cohesion: 0.12
Nodes (15): Architecture Decisions (for this phase), Checkpoint 1, Checkpoint 2 (human review: embedding decision), Checkpoint 3 (human review: ADR-11 decision), Checkpoint: Phase A complete, Dependency Graph, Implementation Plan: TaxCite Phase A — Core Retrieval Baseline, Overview (+7 more)

### Community 15 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.17
Nodes (17): Log #26: The Benchmark Died Because of Unrelated Software, Log #8: Qdrant Over pgvector, With a Measurable Revisit Trigger, Log #28: One Tied Score Made the Eval Unreproducible, Phase A Exit Report, Phase A Recalibration Notes for §9.3, Repository Map, Phase A Complete (Status), Acceptance Thresholds by Phase (§9.3) (+9 more)

### Community 16 - "TaxCite — Phase A exit report"
Cohesion: 0.25
Nodes (7): Decisions settled, with the evidence, Known failures, with examples, Recalibration notes for §9.3, TaxCite — Phase A exit report, The ablation ladder so far, What exists, What Phase A did not do

### Community 17 - "ADR-11: LLM Tiering — gpt-4o-mini"
Cohesion: 0.23
Nodes (12): Log #31: The Reliability Check Measured Two Standards and Called It Noise, Log #27: The Revisit Trigger I Wrote Was Mis-Specified, Log #30: The Two Models Fail in Different Directions, Three-Way Citation Counting, ADR-11: LLM Tiering — gpt-4o-mini, ADR-15: Zero-Tolerance Claim Suppression, ADR-3: Post-Generation Claim Verification, ADR-4: Self-Hosted NLI Model for Production Verification (+4 more)

### Community 18 - "test_decompose.py"
Cohesion: 0.16
Nodes (16): hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, Phase A's path is the floor: a bad plan must not fail a question the corpus can…, The model is trusted for the routing, not the wording: rewritten text measured…, test_an_unusable_plan_falls_back_to_one_unrouted_search() (+8 more)

### Community 19 - "T5: Ingest IRS Publications"
Cohesion: 0.14
Nodes (14): Postgres Service (pgvector/pgvector:pg16), Redis Service (compose), Log #17: Chunker Output Is 12x the Section Count, Log #16: Parallel Workers Made Embedding Slower, Log #22: Choosing a PDF Library by Measuring It on the Real Document, Log #25: Screen Candidates for Viability Before Measuring Quality, Host Port Offsets (5433 / 6380), T5: Ingest IRS Publications (+6 more)

### Community 20 - "Log #24: Adding a Second Corpus Made Retrieval Worse"
Cohesion: 0.25
Nodes (9): Log #29: The Closed-Book Baseline Cited a Publication That No Longer Exists, Log #23: A Discontinued Publication Returns HTTP 200 With HTML, Log #24: Adding a Second Corpus Made Retrieval Worse, Log #14: Table-of-Contents Sections Would Poison Retrieval, Phase A Known Failures, ADR-8: Authority-Aware Reranking, Authority-Aware Retrieval, Phase E — Authority-Aware Retrieval (+1 more)

### Community 23 - "SubQuery"
Cohesion: 0.25
Nodes (5): merge(), parse(), (sub-queries, as_of, fallback reason). Never raises. A decomposition that…, One ranked list of k, round-robin across sub-queries, first occurrence wins.…, SubQuery

### Community 24 - "ADR-12: Backup and Disaster Recovery"
Cohesion: 0.50
Nodes (4): ADR-12: Backup and Disaster Recovery, Single-Engineer Operational Bus Factor, Phase H — Resilience + Load, Production SLOs and Alerting (§3.4)

### Community 26 - "test_usc.py"
Cohesion: 0.07
Nodes (20): memo(), fixture, Case-law tests against two real Tax Court opinions (see tasks/todo.md B3): -…, result(), tc(), test_selection_dedupes_by_citation_and_keeps_the_newest(), chunks(), of() (+12 more)

### Community 27 - "llm_bench.py"
Cohesion: 0.22
Nodes (12): dotenv, cost_of(), estimate(), judge(), main(), ADR-11: choose the LLM by measuring answers, not by price alone. uv run python…, Rough spend before committing: RAG prompts dominate the input tokens., Grade one answer. `alt` applies the same rubric in different words, which is… (+4 more)

### Community 28 - "retrieval.py"
Cohesion: 0.13
Nodes (19): datetime, cached_decompose(), first_hits(), groups(), main(), needs_case_law(), Path, Score retrieval against the pilot set: the first rungs of the §9 ablation… (+11 more)

### Community 29 - "jobs.py"
Cohesion: 0.17
Nodes (16): create(), main(), Path, restore(), Redis, client(), Event, notify() (+8 more)

### Community 30 - "store_bench.py"
Cohesion: 0.23
Nodes (11): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+3 more)

### Community 31 - "source_filter"
Cohesion: 0.67
Nodes (3): Filter, One source or several; several is how B7 routes a sub-query to the corpora that…, source_filter()

### Community 33 - "ragas_eval.py"
Cohesion: 0.10
Nodes (26): aggregate(), Budget, CostCap, extract_claims(), judge_claims(), Judged, main(), parse_json() (+18 more)

### Community 34 - "caselaw.py"
Cohesion: 0.15
Nodes (17): argparse, collections, build(), collection_for(), ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, Index every chunk with one model into its own collection; returns build time., Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, httpx (+9 more)

### Community 38 - "eCFR Chunking Decisions"
Cohesion: 0.22
Nodes (10): Log #1: Spec Chunk Size Didn't Survive the Data, Log #2: Chunk at Paragraph Designations, Two Levels Deep, Log #3: Tables — A Few Huge, Many Small and Meaningful, Log #6: The Source XML Already Carries Temporal Signals, Approximate Search Loses 22% Under a Strict Filter, eCFR Chunking Decisions, ADR-2: Bi-Temporal Fact Validity, Bi-Temporal Fact Validity (+2 more)

### Community 39 - "search"
Cohesion: 0.18
Nodes (17): Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, search(), hit(), RRF ties used to break differently per process, moving a chunk across the k…, The cross-encoder's job: an example that quotes a rule is not the rule., No final 280A regulations exist, so the home-office rules live only in Pub 587., test_dense_finds_the_hobby_loss_factor(), test_hybrid_returns_k_hits_with_payload() (+9 more)

### Community 40 - "generate.py"
Cohesion: 0.23
Nodes (13): Answer, answer_from_groups(), answer_from_hits(), cost(), format_sources(), _generate(), parse_citations(), Answer a question, with and without retrieval. Two modes, because the §9… (+5 more)

### Community 45 - "Ingestion Pipeline (§3.2)"
Cohesion: 0.32
Nodes (8): Log #7: Origin for Content, Mirror for Change Detection, Harvard Caselaw Access Project, CourtListener, eCFR API (26 CFR), eyecite, GovInfo (GPO), Ingestion Pipeline (§3.2), uscode.house.gov (OLRC)

### Community 49 - "call_model"
Cohesion: 0.29
Nodes (7): call_model(), MissingCredentials, RuntimeError, Raised instead of the SDK's generic auth error, which does not say what to set., Fail early and specifically. The SDK raises a generic TypeError at request…, One completion. Returns (text, input_tokens, output_tokens). The two providers…, _require_credentials()

### Community 50 - "retrieve.py"
Cohesion: 0.18
Nodes (13): collections_abc, dataclasses, functools, SparseVector, Split a question into typed sub-queries, and route each to the sources that can…, embed(), _models(), Search the indexed corpus. Modes, because the eval ablation ladder (§9) needs… (+5 more)

### Community 51 - "Decisions Log"
Cohesion: 0.20
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

## Knowledge Gaps
- **79 isolated node(s):** `✅ Checkpoint 1 — after T1–T3`, `✅ Checkpoint 2 — after T4–T6`, `✅ Checkpoint 3 — after T7–T8`, `✅ Checkpoint: Phase A complete`, `T2: Ingest eCFR Title 26 into Postgres + Qdrant` (+74 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 324 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `ecfr.py` to `test_irs_pubs.py`, `caselaw.py`, `test_ecfr.py`, `cli.py`, `Decisions Log`?**
  _High betweenness centrality (0.371) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `Decisions Log` to `eCFR Chunking Decisions`, `TaxCite`, `ADR-17: Vector Store — Qdrant, Not pgvector`, `ADR-11: LLM Tiering — gpt-4o-mini`, `T5: Ingest IRS Publications`?**
  _High betweenness centrality (0.360) - this node is a cross-community bridge._
- **Why does `Confirmed Intent` connect `TaxCite` to `Decisions Log`, `Phase A Implementation Plan`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `Hit` (e.g. with `chunks()` and `Decomposition`) actually correct?**
  _`Hit` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Chunk` (e.g. with `parse()` and `parse()`) actually correct?**
  _`Chunk` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `✅ Checkpoint 1 — after T1–T3`, `✅ Checkpoint 2 — after T4–T6`, `✅ Checkpoint 3 — after T7–T8` to the rest of the system?**
  _79 weakly-connected nodes found - possible documentation gaps or missing edges._