# Graph Report - TaxCite.nosync  (2026-09-22)

## Corpus Check
- 61 files · ~241,071 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 3, .jsonl 3, .xml 2)

## Summary
- 767 nodes · 1455 edges · 41 communities (36 shown, 5 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 87 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bdacd027`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_metrics.py
- test_irs_pubs.py
- test_jobs.py
- T2: Ingest eCFR Title 26
- cli.py
- test_ecfr.py
- api.py
- search
- TaxCite — Engineering Log
- ecfr.py
- test_generate.py
- Evidence-Sufficiency Gate
- TaxCite Phase A — Task List
- Phase A Implementation Plan
- Task List
- Phase A Exit Report
- TaxCite — Phase A exit report
- ADR-11: LLM Tiering — gpt-4o-mini
- test_decompose.py
- caselaw.py
- ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5
- taxcite
- Collaborative Working Mode
- Log #24: Adding a Second Corpus Made Retrieval Worse
- retrieve.py
- Postgres
- test_usc.py
- llm_bench.py
- retrieval.py
- jobs.py
- store_bench.py
- conn
- test_index.py
- TaxCite
- embed_bench.py
- ADR-12: Backup and Disaster Recovery
- fetch
- fetch
- ADR-17: Vector Store — Qdrant, Not pgvector
- taxcite
- taxcite_ingest

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
- `PII Redaction Ordering as a CI Invariant` --semantically_similar_to--> `Log #18: The Counts-Match Check Caught Silent Data Loss`  [INFERRED] [semantically similar]
  taxcite-technical-documentation.md → docs/engineering-log.md
- `score()` --calls--> `section_of()`  [INFERRED]
  eval/embed_bench.py → src/taxcite/generate.py
- `main()` --indirect_call--> `conn()`  [INFERRED]
  eval/embed_bench.py → tests/test_store.py
- `main()` --calls--> `answer()`  [INFERRED]
  eval/llm_bench.py → src/taxcite/decompose.py
- `test_any_member_satisfies_a_group()` --calls--> `recall_at_k()`  [INFERRED]
  tests/test_metrics.py → eval/retrieval.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]
- **Measurements That Overturned a Stated Intuition** — docs_engineering_log_measured_ablation, docs_engineering_log_publication_dilution, docs_engineering_log_mis_specified_revisit_trigger, docs_engineering_log_parallel_embedding_slower, docs_engineering_log_judge_rubric_mismatch [INFERRED 0.85]

## Communities (41 total, 5 thin omitted)

### Community 0 - "test_metrics.py"
Cohesion: 0.13
Nodes (25): cached_decompose(), first_hits(), mrr(), ndcg_at_k(), Path, Decompose once per plan set and reuse it, so a comparison measures the change…, 0-based rank at which each group is first satisfied, for the groups that are., recall_at_k() (+17 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.06
Nodes (42): skipif, dehyphenate(), edition_year(), fetch(), _normalise(), page_texts(), parse(), Path (+34 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.09
Nodes (23): fastapi_testclient, pytest, clean(), fixture, Job record and SSE transport (ADR-9), with the pipeline stubbed., ADR-9: nothing unverified reaches the user, so the answer is buffered., ADR-16: Redis carries progress; the record is the source of truth behind it., A Redis outage must degrade liveness, not correctness (ADR-16). (+15 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.08
Nodes (29): Log #1: Spec Chunk Size Didn't Survive the Data, Log #18: The Counts-Match Check Caught Silent Data Loss, Log #13: The iCloud Bug That Broke Editable Installs, Log #4: Italic Designations Are a Different Hierarchy Level, Log #2: Chunk at Paragraph Designations, Two Levels Deep, Log #15: Fixtures From Real Edge Cases, Not Invented, Log #7: Origin for Content, Mirror for Change Detection, Log #3: Tables — A Few Huge, Many Small and Meaningful (+21 more)

### Community 4 - "cli.py"
Cohesion: 0.24
Nodes (20): Connection, io, Namespace, ingest_case(), ingest_ecfr(), ingest_pubs(), ingest_usc(), latest_as_of() (+12 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.06
Nodes (48): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+40 more)

### Community 6 - "api.py"
Cohesion: 0.13
Nodes (17): asyncio, BackgroundTasks, BaseModel, datetime, fastapi, fastapi_responses, os, post (+9 more)

### Community 7 - "search"
Cohesion: 0.05
Nodes (63): dataclasses, Filter, RuntimeError, answer(), chunks(), decompose(), Decomposition, merge() (+55 more)

### Community 8 - "TaxCite — Engineering Log"
Cohesion: 0.06
Nodes (33): 10. Keep live delivery separate from tracing, 11. Stay true to the architecture but defer stores until they have work, 12. Vercel is the wrong host for this backend, 13. The iCloud bug that silently broke editable installs, 14. Table-of-contents sections would poison retrieval, 15. Test fixtures chosen from real edge cases, not invented, 16. Parallel workers made embedding slower, not faster, 17. The chunker's output is 12× the section count (+25 more)

### Community 9 - "ecfr.py"
Cohesion: 0.12
Nodes (37): Block, blocks(), walk(), chunk_section(), make(), cite(), clean(), pack() (+29 more)

### Community 10 - "test_generate.py"
Cohesion: 0.09
Nodes (9): fixture, Answer generation, tested without spending money: the model call is stubbed., Replace the model call; record what it was asked., Chunk citations are sometimes ranges; citing one paragraph inside is precision,…, A citation not among the sources is the failure mode this system exists to…, stub(), test_a_narrower_paragraph_of_a_retrieved_section_counts_as_derived(), test_closed_book_does_not_retrieve() (+1 more)

### Community 11 - "Evidence-Sufficiency Gate"
Cohesion: 0.17
Nodes (15): Log #5: Corpus Gaps Shape the Evaluation, Log #21: Gold Sets Need Validating Before They Can Validate Anything, The Pilot Set Is Data, Not Code, T3: Hybrid search CLI with citations, T4: Pilot Set and Retrieval Eval Script, Functional Requirements FR-1..FR-17, ADR-1: Decomposition + Bounded Citation-Graph Traversal, ADR-7: Sufficiency Gate Runs Before Synthesis (+7 more)

### Community 12 - "TaxCite Phase A — Task List"
Cohesion: 0.11
Nodes (20): Log #29: The Closed-Book Baseline Cited a Publication That No Longer Exists, Log #23: A Discontinued Publication Returns HTTP 200 With HTML, Log #16: Parallel Workers Made Embedding Slower, ✅ Checkpoint 1 — after T1–T3, ✅ Checkpoint 2 — after T4–T6, ✅ Checkpoint 3 — after T7–T8, ✅ Checkpoint: Phase A complete, T10: Phase A exit report (+12 more)

### Community 13 - "Phase A Implementation Plan"
Cohesion: 0.19
Nodes (13): Log #11: Stay True to the Architecture, Defer Stores Until They Have Work, Log #9: Redis vs Postgres LISTEN/NOTIFY for Live Events, Log #10: Keep Live Delivery Separate From Tracing, Log #12: Vercel Is the Wrong Host for This Backend, Simplify Inside Components, Never By Dropping a Store, Plain-Module Package Layout, Phase A Implementation Plan, Phase A Risks and Mitigations (+5 more)

### Community 14 - "Task List"
Cohesion: 0.12
Nodes (15): Architecture Decisions (for this phase), Checkpoint 1, Checkpoint 2 (human review: embedding decision), Checkpoint 3 (human review: ADR-11 decision), Checkpoint: Phase A complete, Dependency Graph, Implementation Plan: TaxCite Phase A — Core Retrieval Baseline, Overview (+7 more)

### Community 15 - "Phase A Exit Report"
Cohesion: 0.18
Nodes (11): Log #19: Hybrid Retrieval Is Not Uniformly Better Than Dense, Log #20: Measurement Overturned What One Query Suggested, Phase A Exit Report, Phase A Recalibration Notes for §9.3, What Phase A did not do, Repository Map, Phase A Complete (Status), Ablation Ladder (+3 more)

### Community 16 - "TaxCite — Phase A exit report"
Cohesion: 0.29
Nodes (6): Decisions settled, with the evidence, Known failures, with examples, Recalibration notes for §9.3, TaxCite — Phase A exit report, The ablation ladder so far, What exists

### Community 17 - "ADR-11: LLM Tiering — gpt-4o-mini"
Cohesion: 0.23
Nodes (12): Log #31: The Reliability Check Measured Two Standards and Called It Noise, Log #27: The Revisit Trigger I Wrote Was Mis-Specified, Log #30: The Two Models Fail in Different Directions, Three-Way Citation Counting, ADR-11: LLM Tiering — gpt-4o-mini, ADR-15: Zero-Tolerance Claim Suppression, ADR-3: Post-Generation Claim Verification, ADR-4: Self-Hosted NLI Model for Production Verification (+4 more)

### Community 18 - "test_decompose.py"
Cohesion: 0.16
Nodes (16): parametrize, hit(), plan(), Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, Phase A's path is the floor: a bad plan must not fail a question the corpus can…, The model is trusted for the routing, not the wording: rewritten text measured…, test_an_unusable_plan_falls_back_to_one_unrouted_search() (+8 more)

### Community 19 - "caselaw.py"
Cohesion: 0.14
Nodes (24): collections, httpx, LTTextBox, pdfminer_high_level, pdfminer_layout, re, Chunk, estimate_tokens() (+16 more)

### Community 20 - "ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5"
Cohesion: 0.13
Nodes (16): Log #26: The Benchmark Died Because of Unrelated Software, Log #22: Choosing a PDF Library by Measuring It on the Real Document, Log #28: One Tied Score Made the Eval Unreproducible, Log #25: Screen Candidates for Viability Before Measuring Quality, Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering (+8 more)

### Community 23 - "Log #24: Adding a Second Corpus Made Retrieval Worse"
Cohesion: 0.33
Nodes (7): Log #24: Adding a Second Corpus Made Retrieval Worse, Log #14: Table-of-Contents Sections Would Poison Retrieval, Phase A Known Failures, ADR-8: Authority-Aware Reranking, Authority-Aware Retrieval, Phase E — Authority-Aware Retrieval, Phase F — Evidence Sufficiency + Claim Verification

### Community 24 - "retrieve.py"
Cohesion: 0.13
Nodes (22): collections_abc, functools, qdrant_client, QdrantClient, SparseVector, batched(), client(), count() (+14 more)

### Community 26 - "test_usc.py"
Cohesion: 0.07
Nodes (20): memo(), fixture, Case-law tests against two real Tax Court opinions (see tasks/todo.md B3): -…, result(), tc(), test_selection_dedupes_by_citation_and_keeps_the_newest(), chunks(), of() (+12 more)

### Community 27 - "llm_bench.py"
Cohesion: 0.20
Nodes (13): dotenv, cost_of(), estimate(), judge(), main(), ADR-11: choose the LLM by measuring answers, not by price alone. uv run python…, Rough spend before committing: RAG prompts dominate the input tokens., Grade one answer. `alt` applies the same rubric in different words, which is… (+5 more)

### Community 28 - "retrieval.py"
Cohesion: 0.18
Nodes (10): groups(), main(), needs_case_law(), Score retrieval against the pilot set: the first rungs of the §9 ablation…, A row whose gold includes an opinion: routing must send a sub-query to the case…, ["a", ["b", "c"]] -> [{"a"}, {"b", "c"}]; also accepts a plain set of citations., content_words(), main() (+2 more)

### Community 29 - "jobs.py"
Cohesion: 0.22
Nodes (11): Redis, client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across…, One server-sent event. The blank line is the record separator., Append a stage to the record, then notify listeners. Record first: a listener… (+3 more)

### Community 30 - "store_bench.py"
Cohesion: 0.23
Nodes (11): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+3 more)

### Community 31 - "conn"
Cohesion: 0.21
Nodes (12): get, Response, _check(), get_query(), health(), Server-sent events for one job. Replays whatever the record already holds, then…, stream_events(), events() (+4 more)

### Community 32 - "test_index.py"
Cohesion: 0.36
Nodes (11): chunks(), ctx(), models_(), fixture, sync(), test_both_vectors_are_stored(), test_excluded_rows_are_not_indexed(), test_indexes_postgres_rows() (+3 more)

### Community 33 - "TaxCite"
Cohesion: 0.27
Nodes (11): Confirmed Intent, TaxCite, TaxCite PRD, Goals G1-G6 (research time, seat displacement, groundedness, gates, cost, leakage), Non-Functional Requirements (latency, reliability, cost, security), Open Questions (embedding, LLM provider, frontend, backup storage, market scope), Renee (Enrolled Agent persona), ADR-10: Batch the Sufficiency Gate Into One Call Per Sub-Query (+3 more)

### Community 34 - "embed_bench.py"
Cohesion: 0.31
Nodes (7): argparse, build(), collection_for(), main(), ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, Index every chunk with one model into its own collection; returns build time., score()

### Community 35 - "ADR-12: Backup and Disaster Recovery"
Cohesion: 0.50
Nodes (4): ADR-12: Backup and Disaster Recovery, Single-Engineer Operational Bus Factor, Phase H — Resilience + Load, Production SLOs and Alerting (§3.4)

### Community 36 - "fetch"
Cohesion: 0.32
Nodes (8): Client, fetch(), get(), load_selection(), The newest `per_topic` distinct opinions for each topic. A consolidated case is…, The selection is cached so the corpus stays fixed while new opinions are filed., One opinion's PDF, cached. DAWSON hands out a short-lived signed S3 link., select()

### Community 37 - "fetch"
Cohesion: 0.40
Nodes (5): fetch(), fetch_usc(), Path, Title 26 USLM XML for a release point (default: the current one), cached on…, Download one part (or a single section) of Title 26, cached on disk. The API…

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.14
Nodes (17): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Redis Service (compose), Log #17: Chunker Output Is 12x the Section Count, Log #8: Qdrant Over pgvector, With a Measurable Revisit Trigger, Log #6: The Source XML Already Carries Temporal Signals, Approximate Search Loses 22% Under a Strict Filter, Host Port Offsets (5433 / 6380) (+9 more)

## Knowledge Gaps
- **79 isolated node(s):** `taxcite`, `✅ Checkpoint 1 — after T1–T3`, `✅ Checkpoint 2 — after T4–T6`, `✅ Checkpoint 3 — after T7–T8`, `✅ Checkpoint: Phase A complete` (+74 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 306 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `caselaw.py` to `test_irs_pubs.py`, `cli.py`, `test_ecfr.py`, `api.py`, `ecfr.py`, `ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5`?**
  _High betweenness centrality (0.384) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5` to `ADR-11: LLM Tiering — gpt-4o-mini`, `T2: Ingest eCFR Title 26`, `TaxCite`?**
  _High betweenness centrality (0.373) - this node is a cross-community bridge._
- **Why does `Confirmed Intent` connect `TaxCite` to `ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5`, `Phase A Implementation Plan`, `Phase A Exit Report`?**
  _High betweenness centrality (0.169) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `Hit` (e.g. with `chunks()` and `Decomposition`) actually correct?**
  _`Hit` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Chunk` (e.g. with `parse()` and `parse()`) actually correct?**
  _`Chunk` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `taxcite`, `✅ Checkpoint 1 — after T1–T3`, `✅ Checkpoint 2 — after T4–T6` to the rest of the system?**
  _79 weakly-connected nodes found - possible documentation gaps or missing edges._