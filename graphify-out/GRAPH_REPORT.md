# Graph Report - TaxCite.nosync  (2026-09-22)

## Corpus Check
- 50 files · ~88,015 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 3, .jsonl 3, .xml 2)

## Summary
- 701 nodes · 1308 edges · 32 communities (28 shown, 4 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 84 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0de6c09a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- store_bench.py
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
- TaxCite
- TaxCite Phase A — Task List
- Phase A Implementation Plan
- Task List
- ADR-17: Vector Store — Qdrant, Not pgvector
- TaxCite — Phase A exit report
- ADR-11: LLM Tiering — gpt-4o-mini
- generate.py
- ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5
- test_index.py
- taxcite
- Collaborative Working Mode
- Postgres
- test_usc.py
- TaxCite — Status
- index.py
- jobs.py
- T3: Hybrid search CLI with citations
- post_query
- fetch

## God Nodes (most connected - your core abstractions)
1. `TaxCite — Engineering Log` - 33 edges
2. `search()` - 20 edges
3. `conn()` - 18 edges
4. `Chunk` - 17 edges
5. `TaxCite Phase A — Task List` - 16 edges
6. `ingest_ecfr()` - 15 edges
7. `estimate_tokens()` - 14 edges
8. `ingest_case()` - 14 edges
9. `parse()` - 14 edges
10. `of()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `events()` --indirect_call--> `conn()`  [INFERRED]
  src/taxcite/api.py → tests/test_store.py
- `PII Redaction Ordering as a CI Invariant` --semantically_similar_to--> `Log #18: The Counts-Match Check Caught Silent Data Loss`  [INFERRED] [semantically similar]
  taxcite-technical-documentation.md → docs/engineering-log.md
- `test_any_member_satisfies_a_group()` --calls--> `recall_at_k()`  [INFERRED]
  tests/test_metrics.py → eval/retrieval.py
- `test_recall_counts_only_gold_hits()` --calls--> `recall_at_k()`  [INFERRED]
  tests/test_metrics.py → eval/retrieval.py
- `test_recall_ignores_duplicates()` --calls--> `recall_at_k()`  [INFERRED]
  tests/test_metrics.py → eval/retrieval.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]
- **Measurements That Overturned a Stated Intuition** — docs_engineering_log_measured_ablation, docs_engineering_log_publication_dilution, docs_engineering_log_mis_specified_revisit_trigger, docs_engineering_log_parallel_embedding_slower, docs_engineering_log_judge_rubric_mismatch [INFERRED 0.85]

## Communities (32 total, 4 thin omitted)

### Community 0 - "store_bench.py"
Cohesion: 0.05
Nodes (62): argparse, dotenv, build(), collection_for(), main(), ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, Index every chunk with one model into its own collection; returns build time., score() (+54 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.07
Nodes (31): skipif, _normalise(), Sliding windows with overlap; a short page yields a single window., Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count(), edges() (+23 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.08
Nodes (27): fastapi_testclient, pytest, clean(), fixture, Job record and SSE transport (ADR-9), with the pipeline stubbed., A Redis outage must degrade liveness, not correctness (ADR-16)., The record and the live channel can race; sequence numbers settle it., No retrieval, no LLM: this test is about the transport. (+19 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.08
Nodes (28): Log #1: Spec Chunk Size Didn't Survive the Data, Log #18: The Counts-Match Check Caught Silent Data Loss, Log #13: The iCloud Bug That Broke Editable Installs, Log #4: Italic Designations Are a Different Hierarchy Level, Log #2: Chunk at Paragraph Designations, Two Levels Deep, Log #15: Fixtures From Real Edge Cases, Not Invented, Log #7: Origin for Content, Mirror for Change Detection, Log #3: Tables — A Few Huge, Many Small and Meaningful (+20 more)

### Community 4 - "cli.py"
Cohesion: 0.19
Nodes (25): Connection, io, Namespace, ingest_case(), ingest_ecfr(), ingest_pubs(), ingest_usc(), latest_as_of() (+17 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.07
Nodes (37): Element, designations(), in_scope(), level_of(), True when a section is one of these prefixes, or a numbered child of one.…, 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.…, Level-1 and level-2 designations a paragraph opens with. Read from raw text,…, of() (+29 more)

### Community 6 - "api.py"
Cohesion: 0.12
Nodes (19): asyncio, datetime, fastapi, fastapi_responses, get, json, os, psycopg (+11 more)

### Community 7 - "search"
Cohesion: 0.14
Nodes (20): functools, qdrant_client, SparseVector, embed(), Hit, _models(), Search the indexed corpus. Two modes, because the eval ablation ladder (§9)…, Loaded once per process and per model: ~4s, which every query would otherwise… (+12 more)

### Community 8 - "TaxCite — Engineering Log"
Cohesion: 0.06
Nodes (33): 10. Keep live delivery separate from tracing, 11. Stay true to the architecture but defer stores until they have work, 12. Vercel is the wrong host for this backend, 13. The iCloud bug that silently broke editable installs, 14. Table-of-contents sections would poison retrieval, 15. Test fixtures chosen from real edge cases, not invented, 16. Parallel workers made embedding slower, not faster, 17. The chunker's output is 12× the section count (+25 more)

### Community 9 - "ecfr.py"
Cohesion: 0.05
Nodes (83): Client, collections, dataclasses, httpx, LTTextBox, pdfminer_high_level, pdfminer_layout, re (+75 more)

### Community 10 - "test_generate.py"
Cohesion: 0.09
Nodes (9): fixture, Answer generation, tested without spending money: the model call is stubbed., Replace the model call; record what it was asked., Chunk citations are sometimes ranges; citing one paragraph inside is precision,…, A citation not among the sources is the failure mode this system exists to…, stub(), test_a_narrower_paragraph_of_a_retrieved_section_counts_as_derived(), test_closed_book_does_not_retrieve() (+1 more)

### Community 11 - "TaxCite"
Cohesion: 0.17
Nodes (20): Log #5: Corpus Gaps Shape the Evaluation, Confirmed Intent, TaxCite, TaxCite PRD, Functional Requirements FR-1..FR-17, Goals G1-G6 (research time, seat displacement, groundedness, gates, cost, leakage), Non-Functional Requirements (latency, reliability, cost, security), Open Questions (embedding, LLM provider, frontend, backup storage, market scope) (+12 more)

### Community 12 - "TaxCite Phase A — Task List"
Cohesion: 0.11
Nodes (18): Log #23: A Discontinued Publication Returns HTTP 200 With HTML, Log #16: Parallel Workers Made Embedding Slower, ✅ Checkpoint 1 — after T1–T3, ✅ Checkpoint 2 — after T4–T6, ✅ Checkpoint 3 — after T7–T8, ✅ Checkpoint: Phase A complete, T10: Phase A exit report, T2: Ingest eCFR Title 26 into Postgres + Qdrant (+10 more)

### Community 13 - "Phase A Implementation Plan"
Cohesion: 0.13
Nodes (20): Qdrant Service (compose), Redis Service (compose), Log #11: Stay True to the Architecture, Defer Stores Until They Have Work, Log #9: Redis vs Postgres LISTEN/NOTIFY for Live Events, Log #10: Keep Live Delivery Separate From Tracing, Log #12: Vercel Is the Wrong Host for This Backend, Simplify Inside Components, Never By Dropping a Store, Host Port Offsets (5433 / 6380) (+12 more)

### Community 14 - "Task List"
Cohesion: 0.12
Nodes (15): Architecture Decisions (for this phase), Checkpoint 1, Checkpoint 2 (human review: embedding decision), Checkpoint 3 (human review: ADR-11 decision), Checkpoint: Phase A complete, Dependency Graph, Implementation Plan: TaxCite Phase A — Core Retrieval Baseline, Overview (+7 more)

### Community 15 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.11
Nodes (22): Postgres Service (pgvector/pgvector:pg16), Log #17: Chunker Output Is 12x the Section Count, Log #8: Qdrant Over pgvector, With a Measurable Revisit Trigger, Log #6: The Source XML Already Carries Temporal Signals, Approximate Search Loses 22% Under a Strict Filter, Phase A Exit Report, Phase A Recalibration Notes for §9.3, Repository Map (+14 more)

### Community 16 - "TaxCite — Phase A exit report"
Cohesion: 0.25
Nodes (7): Decisions settled, with the evidence, Known failures, with examples, Recalibration notes for §9.3, TaxCite — Phase A exit report, The ablation ladder so far, What exists, What Phase A did not do

### Community 17 - "ADR-11: LLM Tiering — gpt-4o-mini"
Cohesion: 0.22
Nodes (13): Log #31: The Reliability Check Measured Two Standards and Called It Noise, Log #30: The Two Models Fail in Different Directions, Three-Way Citation Counting, T8: ADR-11 LLM Benchmark, ADR-11: LLM Tiering — gpt-4o-mini, ADR-15: Zero-Tolerance Claim Suppression, ADR-3: Post-Generation Claim Verification, ADR-4: Self-Hosted NLI Model for Production Verification (+5 more)

### Community 18 - "generate.py"
Cohesion: 0.16
Nodes (17): Hit, RuntimeError, Answer, answer_from_hits(), call_model(), format_sources(), _generate(), MissingCredentials (+9 more)

### Community 19 - "ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5"
Cohesion: 0.20
Nodes (11): Log #26: The Benchmark Died Because of Unrelated Software, Log #27: The Revisit Trigger I Wrote Was Mis-Specified, Log #22: Choosing a PDF Library by Measuring It on the Real Document, Log #28: One Tied Score Made the Eval Unreproducible, Log #25: Screen Candidates for Viability Before Measuring Quality, Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5 (+3 more)

### Community 20 - "test_index.py"
Cohesion: 0.36
Nodes (11): chunks(), ctx(), models_(), fixture, sync(), test_both_vectors_are_stored(), test_excluded_rows_are_not_indexed(), test_indexes_postgres_rows() (+3 more)

### Community 26 - "test_usc.py"
Cohesion: 0.07
Nodes (21): taxcite_ingest, memo(), fixture, Case-law tests against two real Tax Court opinions (see tasks/todo.md B3): -…, result(), tc(), test_selection_dedupes_by_citation_and_keeps_the_newest(), chunks() (+13 more)

### Community 27 - "TaxCite — Status"
Cohesion: 0.33
Nodes (6): Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 28 - "index.py"
Cohesion: 0.20
Nodes (15): collections_abc, QdrantClient, batched(), count(), create_collection(), point_id(), Embed chunks and keep a Qdrant collection in step with Postgres. Postgres is…, Retry a batch once or twice: a busy host turns a slow upsert into a timeout. (+7 more)

### Community 29 - "jobs.py"
Cohesion: 0.22
Nodes (12): Redis, client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across…, The pipeline, reporting each stage. Phases C-F add their steps here., One server-sent event. The blank line is the record separator. (+4 more)

### Community 30 - "T3: Hybrid search CLI with citations"
Cohesion: 0.14
Nodes (16): Log #29: The Closed-Book Baseline Cited a Publication That No Longer Exists, Log #21: Gold Sets Need Validating Before They Can Validate Anything, Log #19: Hybrid Retrieval Is Not Uniformly Better Than Dense, Log #20: Measurement Overturned What One Query Suggested, Log #24: Adding a Second Corpus Made Retrieval Worse, Phase A Known Failures, The Pilot Set Is Data, Not Code, T3: Hybrid search CLI with citations (+8 more)

### Community 31 - "post_query"
Cohesion: 0.22
Nodes (9): BackgroundTasks, BaseModel, post, post_query(), Query, Accept a question and return immediately (ADR-9). The pipeline runs 20-30s,…, _run_job(), create() (+1 more)

### Community 33 - "fetch"
Cohesion: 0.40
Nodes (5): fetch(), fetch_usc(), Path, Title 26 USLM XML for a release point (default: the current one), cached on…, Download one part (or a single section) of Title 26, cached on disk. The API…

## Knowledge Gaps
- **79 isolated node(s):** `✅ Checkpoint 1 — after T1–T3`, `✅ Checkpoint 2 — after T4–T6`, `✅ Checkpoint 3 — after T7–T8`, `✅ Checkpoint: Phase A complete`, `T2: Ingest eCFR Title 26 into Postgres + Qdrant` (+74 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 277 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `ecfr.py` to `ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5`, `cli.py`, `test_ecfr.py`, `api.py`?**
  _High betweenness centrality (0.408) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5` to `T2: Ingest eCFR Title 26`, `TaxCite — Status`, `TaxCite`?**
  _High betweenness centrality (0.395) - this node is a cross-community bridge._
- **Why does `Confirmed Intent` connect `TaxCite` to `ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5`, `Phase A Implementation Plan`, `T3: Hybrid search CLI with citations`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.179) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `search()` (e.g. with `score_one()` and `main()`) actually correct?**
  _`search()` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Chunk` (e.g. with `parse()` and `parse()`) actually correct?**
  _`Chunk` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `✅ Checkpoint 1 — after T1–T3`, `✅ Checkpoint 2 — after T4–T6`, `✅ Checkpoint 3 — after T7–T8` to the rest of the system?**
  _79 weakly-connected nodes found - possible documentation gaps or missing edges._