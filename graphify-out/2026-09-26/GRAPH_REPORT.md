# Graph Report - TaxCite.nosync  (2026-09-23)

## Corpus Check
- 68 files · ~398,015 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 3, .jsonl 3, .xml 2)

## Summary
- 831 nodes · 1572 edges · 42 communities (36 shown, 6 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 99 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `78bcf82e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ragas_eval.py
- test_irs_pubs.py
- test_jobs.py
- T2: Ingest eCFR Title 26
- cli.py
- test_ecfr.py
- TaxCite — Phase B exit report
- Decomposition
- TaxCite — Engineering Log
- ecfr.py
- test_generate.py
- TaxCite
- TaxCite Phase A — Task List
- Phase A Implementation Plan
- Task List
- T5: Ingest IRS Publications
- TaxCite — Phase A exit report
- ADR-11: LLM Tiering — gpt-4o-mini
- test_decompose.py
- judged
- SubQuery
- taxcite
- Collaborative Working Mode
- test_index.py
- retrieve.py
- Postgres
- test_usc.py
- llm_bench.py
- retrieval.py
- jobs.py
- store_bench.py
- snapshot.py
- taxcite
- ADR-12: Backup and Disaster Recovery
- test_metrics.py
- source_filter
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- generate.py
- taxcite_ingest
- taxcite_ingest_ecfr
- ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5

## God Nodes (most connected - your core abstractions)
1. `TaxCite — Engineering Log` - 33 edges
2. `search()` - 26 edges
3. `Hit` - 20 edges
4. `conn()` - 18 edges
5. `Chunk` - 17 edges
6. `TaxCite Phase A — Task List` - 16 edges
7. `ingest_ecfr()` - 15 edges
8. `estimate_tokens()` - 14 edges
9. `ingest_case()` - 14 edges
10. `parse()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Three-Way Citation Counting` --conceptually_related_to--> `Post-Generation Claim Verification`  [INFERRED]
  STATUS.md → taxcite-technical-documentation.md
- `PII Redaction Ordering as a CI Invariant` --semantically_similar_to--> `Log #18: The Counts-Match Check Caught Silent Data Loss`  [INFERRED] [semantically similar]
  taxcite-technical-documentation.md → docs/engineering-log.md
- `main()` --indirect_call--> `conn()`  [INFERRED]
  eval/embed_bench.py → tests/test_store.py
- `main()` --calls--> `answer()`  [INFERRED]
  eval/llm_bench.py → src/taxcite/decompose.py
- `judged()` --uses--> `Judged`  [INFERRED]
  tests/test_metrics.py → eval/ragas_eval.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]
- **Measurements That Overturned a Stated Intuition** — docs_engineering_log_measured_ablation, docs_engineering_log_publication_dilution, docs_engineering_log_mis_specified_revisit_trigger, docs_engineering_log_parallel_embedding_slower, docs_engineering_log_judge_rubric_mismatch [INFERRED 0.85]

## Communities (42 total, 6 thin omitted)

### Community 0 - "ragas_eval.py"
Cohesion: 0.10
Nodes (26): aggregate(), Budget, CostCap, extract_claims(), judge_claims(), Judged, main(), parse_json() (+18 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.06
Nodes (42): skipif, dehyphenate(), edition_year(), fetch(), _normalise(), page_texts(), parse(), Path (+34 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.09
Nodes (22): fastapi_testclient, clean(), fixture, Job record and SSE transport (ADR-9), with the pipeline stubbed., ADR-9: nothing unverified reaches the user, so the answer is buffered., ADR-16: Redis carries progress; the record is the source of truth behind it., A Redis outage must degrade liveness, not correctness (ADR-16)., The record and the live channel can race; sequence numbers settle it. (+14 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.07
Nodes (32): Log #1: Spec Chunk Size Didn't Survive the Data, Log #18: The Counts-Match Check Caught Silent Data Loss, Log #13: The iCloud Bug That Broke Editable Installs, Log #4: Italic Designations Are a Different Hierarchy Level, Log #2: Chunk at Paragraph Designations, Two Levels Deep, Log #24: Adding a Second Corpus Made Retrieval Worse, Log #15: Fixtures From Real Edge Cases, Not Invented, Log #7: Origin for Content, Mirror for Change Detection (+24 more)

### Community 4 - "cli.py"
Cohesion: 0.06
Nodes (69): asyncio, BackgroundTasks, BaseModel, Connection, fastapi, fastapi_responses, get, io (+61 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.07
Nodes (41): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+33 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "Decomposition"
Cohesion: 0.18
Nodes (9): answer(), decompose(), Decomposition, (sub-query, its chunks) for the synthesis prompt, limited to `keep` if given.…, One structured-output call (ADR-11). Temperature 0 and a fixed seed, so a re-…, Search once per sub-query, filtered to the sources its kind allows. Fills…, Decompose, retrieve per sub-query, synthesize over the grouped sources. `plan`…, retrieve() (+1 more)

### Community 8 - "TaxCite — Engineering Log"
Cohesion: 0.06
Nodes (33): 10. Keep live delivery separate from tracing, 11. Stay true to the architecture but defer stores until they have work, 12. Vercel is the wrong host for this backend, 13. The iCloud bug that silently broke editable installs, 14. Table-of-contents sections would poison retrieval, 15. Test fixtures chosen from real edge cases, not invented, 16. Parallel workers made embedding slower, not faster, 17. The chunker's output is 12× the section count (+25 more)

### Community 9 - "ecfr.py"
Cohesion: 0.07
Nodes (68): Client, collections, httpx, LTTextBox, pdfminer_high_level, pdfminer_layout, re, Chunk (+60 more)

### Community 10 - "test_generate.py"
Cohesion: 0.08
Nodes (11): fixture, Answer generation, tested without spending money: the model call is stubbed., Sampling at the default temperature made the same question answerable two ways,…, Replace the model call; record what it was asked., Chunk citations are sometimes ranges; citing one paragraph inside is precision,…, A citation not among the sources is the failure mode this system exists to…, stub(), test_a_narrower_paragraph_of_a_retrieved_section_counts_as_derived() (+3 more)

### Community 11 - "TaxCite"
Cohesion: 0.11
Nodes (29): Log #29: The Closed-Book Baseline Cited a Publication That No Longer Exists, Log #5: Corpus Gaps Shape the Evaluation, Confirmed Intent, Phase A Known Failures, TaxCite, TaxCite PRD, Functional Requirements FR-1..FR-17, Goals G1-G6 (research time, seat displacement, groundedness, gates, cost, leakage) (+21 more)

### Community 12 - "TaxCite Phase A — Task List"
Cohesion: 0.13
Nodes (16): Log #19: Hybrid Retrieval Is Not Uniformly Better Than Dense, Log #20: Measurement Overturned What One Query Suggested, ✅ Checkpoint 1 — after T1–T3, ✅ Checkpoint 2 — after T4–T6, ✅ Checkpoint 3 — after T7–T8, ✅ Checkpoint: Phase A complete, T2: Ingest eCFR Title 26 into Postgres + Qdrant, T3: Hybrid search CLI with citations (+8 more)

### Community 13 - "Phase A Implementation Plan"
Cohesion: 0.15
Nodes (17): Qdrant Service (compose), Redis Service (compose), Log #11: Stay True to the Architecture, Defer Stores Until They Have Work, Log #9: Redis vs Postgres LISTEN/NOTIFY for Live Events, Log #10: Keep Live Delivery Separate From Tracing, Log #12: Vercel Is the Wrong Host for This Backend, Simplify Inside Components, Never By Dropping a Store, Host Port Offsets (5433 / 6380) (+9 more)

### Community 14 - "Task List"
Cohesion: 0.12
Nodes (15): Architecture Decisions (for this phase), Checkpoint 1, Checkpoint 2 (human review: embedding decision), Checkpoint 3 (human review: ADR-11 decision), Checkpoint: Phase A complete, Dependency Graph, Implementation Plan: TaxCite Phase A — Core Retrieval Baseline, Overview (+7 more)

### Community 15 - "T5: Ingest IRS Publications"
Cohesion: 0.22
Nodes (9): Log #23: A Discontinued Publication Returns HTTP 200 With HTML, Log #21: Gold Sets Need Validating Before They Can Validate Anything, Log #16: Parallel Workers Made Embedding Slower, The Pilot Set Is Data, Not Code, T4: Pilot Set and Retrieval Eval Script, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark, IRS Publications and Guidance (+1 more)

### Community 16 - "TaxCite — Phase A exit report"
Cohesion: 0.25
Nodes (7): Decisions settled, with the evidence, Known failures, with examples, Recalibration notes for §9.3, TaxCite — Phase A exit report, The ablation ladder so far, What exists, What Phase A did not do

### Community 17 - "ADR-11: LLM Tiering — gpt-4o-mini"
Cohesion: 0.24
Nodes (11): Log #31: The Reliability Check Measured Two Standards and Called It Noise, Log #27: The Revisit Trigger I Wrote Was Mis-Specified, Log #30: The Two Models Fail in Different Directions, Three-Way Citation Counting, T10: Phase A exit report, T8: ADR-11 LLM Benchmark, ADR-11: LLM Tiering — gpt-4o-mini, ADR-4: Self-Hosted NLI Model for Production Verification (+3 more)

### Community 18 - "test_decompose.py"
Cohesion: 0.16
Nodes (16): hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, Phase A's path is the floor: a bad plan must not fail a question the corpus can…, The model is trusted for the routing, not the wording: rewritten text measured…, test_an_unusable_plan_falls_back_to_one_unrouted_search() (+8 more)

### Community 19 - "judged"
Cohesion: 0.25
Nodes (8): judged(), An answer the extractor found nothing in would otherwise score 0/0., A row with one claim per entry in `supported`., Averaging refusals in either direction breaks the gate: 0 punishes the…, test_a_refusal_is_not_scored_as_zero_or_as_one(), test_aggregate_counts_claims_and_unsupported_claims(), test_an_answer_with_no_claims_is_reported_not_averaged(), test_faithfulness_is_the_supported_ratio()

### Community 20 - "SubQuery"
Cohesion: 0.33
Nodes (3): parse(), (sub-queries, as_of, fallback reason). Never raises. A decomposition that…, SubQuery

### Community 23 - "test_index.py"
Cohesion: 0.23
Nodes (15): chunks(), ctx(), models_(), fixture, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, sync(), test_a_broken_qdrant_still_raises() (+7 more)

### Community 24 - "retrieve.py"
Cohesion: 0.15
Nodes (17): collections_abc, dataclasses, functools, SparseVector, chunks(), merge(), Split a question into typed sub-queries, and route each to the sources that can…, The k chunks synthesis sees: every sub-query's hits, ordered by the cross-… (+9 more)

### Community 26 - "test_usc.py"
Cohesion: 0.06
Nodes (28): pytest, memo(), fixture, Case-law tests against two real Tax Court opinions (see tasks/todo.md B3): -…, result(), tc(), test_selection_dedupes_by_citation_and_keeps_the_newest(), chunks() (+20 more)

### Community 27 - "llm_bench.py"
Cohesion: 0.24
Nodes (11): dotenv, cost_of(), estimate(), judge(), main(), ADR-11: choose the LLM by measuring answers, not by price alone. uv run python…, Rough spend before committing: RAG prompts dominate the input tokens., Grade one answer. `alt` applies the same rubric in different words, which is… (+3 more)

### Community 28 - "retrieval.py"
Cohesion: 0.12
Nodes (18): argparse, datetime, build(), collection_for(), main(), ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, Index every chunk with one model into its own collection; returns build time., groups() (+10 more)

### Community 29 - "jobs.py"
Cohesion: 0.20
Nodes (13): Redis, client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across…, The pipeline, reporting each stage. Phases C-F add their steps here., One server-sent event. The blank line is the record separator. (+5 more)

### Community 30 - "store_bench.py"
Cohesion: 0.21
Nodes (12): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+4 more)

### Community 31 - "snapshot.py"
Cohesion: 0.36
Nodes (7): create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), subprocess, sys

### Community 33 - "ADR-12: Backup and Disaster Recovery"
Cohesion: 0.50
Nodes (4): ADR-12: Backup and Disaster Recovery, Single-Engineer Operational Bus Factor, Phase H — Resilience + Load, Production SLOs and Alerting (§3.4)

### Community 34 - "test_metrics.py"
Cohesion: 0.13
Nodes (26): score(), cached_decompose(), first_hits(), mrr(), ndcg_at_k(), Path, Decompose once per plan set and reuse it, so a comparison measures the change…, 0-based rank at which each group is first satisfied, for the groups that are. (+18 more)

### Community 35 - "source_filter"
Cohesion: 0.67
Nodes (3): Filter, One source or several; several is how B7 routes a sub-query to the corpora that…, source_filter()

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.13
Nodes (20): Postgres Service (pgvector/pgvector:pg16), Log #17: Chunker Output Is 12x the Section Count, Log #8: Qdrant Over pgvector, With a Measurable Revisit Trigger, Log #6: The Source XML Already Carries Temporal Signals, Approximate Search Loses 22% Under a Strict Filter, Phase A Exit Report, Phase A Recalibration Notes for §9.3, Repository Map (+12 more)

### Community 39 - "search"
Cohesion: 0.18
Nodes (17): Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, search(), hit(), RRF ties used to break differently per process, moving a chunk across the k…, The cross-encoder's job: an example that quotes a rule is not the rule., No final 280A regulations exist, so the home-office rules live only in Pub 587., test_dense_finds_the_hobby_loss_factor(), test_hybrid_returns_k_hits_with_payload() (+9 more)

### Community 40 - "generate.py"
Cohesion: 0.18
Nodes (19): Answer, answer_from_groups(), answer_from_hits(), call_model(), format_sources(), _generate(), MissingCredentials, parse_citations() (+11 more)

### Community 51 - "ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5"
Cohesion: 0.12
Nodes (16): Log #26: The Benchmark Died Because of Unrelated Software, Log #22: Choosing a PDF Library by Measuring It on the Real Document, Log #28: One Tied Score Made the Eval Unreproducible, Log #25: Screen Candidates for Viability Before Measuring Quality, Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering (+8 more)

## Knowledge Gaps
- **88 isolated node(s):** `taxcite`, `What exists`, `The ablation ladder`, `Phase C's baseline`, `Faithfulness` (+83 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 339 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `ecfr.py` to `test_irs_pubs.py`, `ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5`, `cli.py`, `test_ecfr.py`?**
  _High betweenness centrality (0.358) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5` to `T2: Ingest eCFR Title 26`, `ADR-11: LLM Tiering — gpt-4o-mini`, `TaxCite`?**
  _High betweenness centrality (0.348) - this node is a cross-community bridge._
- **Why does `Confirmed Intent` connect `TaxCite` to `ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5`, `Phase A Implementation Plan`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.157) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `Hit` (e.g. with `chunks()` and `Decomposition`) actually correct?**
  _`Hit` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Chunk` (e.g. with `parse()` and `parse()`) actually correct?**
  _`Chunk` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `taxcite`, `What exists`, `The ablation ladder` to the rest of the system?**
  _88 weakly-connected nodes found - possible documentation gaps or missing edges._