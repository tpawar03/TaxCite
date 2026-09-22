# Graph Report - TaxCite.nosync  (2026-09-21)

## Corpus Check
- 41 files · ~57,814 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 609 nodes · 1077 edges · 26 communities (21 shown, 5 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 60 edges (avg confidence: 0.87)
- Token cost: 194,099 input · 0 output

## Community Hubs (Navigation)
- Eval Harness Scripts
- IRS Publication Ingestion
- Test Suite & Fixtures
- Data & Parsing Lessons
- CLI & Ingest Orchestration
- CFR Paragraph Parser
- Job Record & SSE API
- Answer Generation & Cost
- Engineering Log Index
- Chunk Model & Keys
- Citation-Parsing Tests
- Product Intent & Requirements
- Benchmark Method Lessons
- Store Choices & Failure Domains
- Phase A Plan & Checkpoints
- Vector Store Decision
- Embedding Model & Thresholds
- LLM Choice & Verification
- Retrieval Measurement Findings
- Phase A Exit Report
- Resilience & Operations
- Package Root
- Working Mode
- Package Alias
- Ingest Package
- Postgres Node

## God Nodes (most connected - your core abstractions)
1. `TaxCite — Engineering Log` - 33 edges
2. `search()` - 22 edges
3. `TaxCite Phase A — Task List` - 16 edges
4. `conn()` - 16 edges
5. `ingest_ecfr()` - 15 edges
6. `parse()` - 14 edges
7. `of()` - 14 edges
8. `ingest_pubs()` - 13 edges
9. `chunk_section()` - 13 edges
10. `ADR-11: LLM Tiering — gpt-4o-mini` - 13 edges

## Surprising Connections (you probably didn't know these)
- `events()` --indirect_call--> `conn()`  [INFERRED]
  src/taxcite/api.py → tests/test_store.py
- `PII Redaction Ordering as a CI Invariant` --semantically_similar_to--> `Log #18: The Counts-Match Check Caught Silent Data Loss`  [INFERRED] [semantically similar]
  taxcite-technical-documentation.md → docs/engineering-log.md
- `Qdrant Service (compose)` --implements--> `T1: Local stack and package skeleton`  [INFERRED]
  docker-compose.yml → tasks/todo.md
- `main()` --indirect_call--> `conn()`  [INFERRED]
  eval/embed_bench.py → tests/test_store.py
- `test_recall_counts_only_gold_hits()` --calls--> `recall_at_k()`  [INFERRED]
  tests/test_metrics.py → eval/retrieval.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Measurements That Overturned a Stated Intuition** — docs_engineering_log_measured_ablation, docs_engineering_log_publication_dilution, docs_engineering_log_mis_specified_revisit_trigger, docs_engineering_log_parallel_embedding_slower, docs_engineering_log_judge_rubric_mismatch [INFERRED 0.85]

## Communities (26 total, 5 thin omitted)

### Community 0 - "Eval Harness Scripts"
Cohesion: 0.05
Nodes (60): argparse, collections, dotenv, build(), collection_for(), main(), ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, Index every chunk with one model into its own collection; returns build time. (+52 more)

### Community 1 - "IRS Publication Ingestion"
Cohesion: 0.06
Nodes (46): httpx, pdfminer_high_level, pdfminer_layout, skipif, dehyphenate(), edition_year(), fetch(), _normalise() (+38 more)

### Community 2 - "Test Suite & Fixtures"
Cohesion: 0.07
Nodes (41): fastapi_testclient, pytest, chunks(), ctx(), models_(), fixture, sync(), test_both_vectors_are_stored() (+33 more)

### Community 3 - "Data & Parsing Lessons"
Cohesion: 0.05
Nodes (47): Log #1: Spec Chunk Size Didn't Survive the Data, Log #18: The Counts-Match Check Caught Silent Data Loss, Log #13: The iCloud Bug That Broke Editable Installs, Log #4: Italic Designations Are a Different Hierarchy Level, Log #2: Chunk at Paragraph Designations, Two Levels Deep, Log #24: Adding a Second Corpus Made Retrieval Worse, Log #15: Fixtures From Real Edge Cases, Not Invented, Log #7: Origin for Content, Mirror for Change Detection (+39 more)

### Community 4 - "CLI & Ingest Orchestration"
Cohesion: 0.09
Nodes (38): collections_abc, Connection, datetime, Namespace, QdrantClient, fetch(), ingest_ecfr(), ingest_pubs() (+30 more)

### Community 5 - "CFR Paragraph Parser"
Cohesion: 0.07
Nodes (36): Element, designations(), in_scope(), level_of(), True when a section is one of these prefixes, or a numbered child of one.…, 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.…, Level-1 and level-2 designations a paragraph opens with. Read from raw text,…, of() (+28 more)

### Community 6 - "Job Record & SSE API"
Cohesion: 0.08
Nodes (36): asyncio, BackgroundTasks, BaseModel, fastapi, fastapi_responses, os, post, psycopg (+28 more)

### Community 7 - "Answer Generation & Cost"
Cohesion: 0.10
Nodes (31): RuntimeError, Answer, answer_from_hits(), call_model(), format_sources(), _generate(), MissingCredentials, parse_citations() (+23 more)

### Community 8 - "Engineering Log Index"
Cohesion: 0.06
Nodes (33): 10. Keep live delivery separate from tracing, 11. Stay true to the architecture but defer stores until they have work, 12. Vercel is the wrong host for this backend, 13. The iCloud bug that silently broke editable installs, 14. Table-of-contents sections would poison retrieval, 15. Test fixtures chosen from real edge cases, not invented, 16. Parallel workers made embedding slower, not faster, 17. The chunker's output is 12× the section count (+25 more)

### Community 9 - "Chunk Model & Keys"
Cohesion: 0.14
Nodes (28): dataclasses, Chunk, estimate_tokens(), The unit every ingester produces and every store consumes., Make `part` a running count per citation, so `key` is unique by construction.…, renumber(), Block, blocks() (+20 more)

### Community 10 - "Citation-Parsing Tests"
Cohesion: 0.09
Nodes (9): fixture, Answer generation, tested without spending money: the model call is stubbed., Replace the model call; record what it was asked., Chunk citations are sometimes ranges; citing one paragraph inside is precision,…, A citation not among the sources is the failure mode this system exists to…, stub(), test_a_narrower_paragraph_of_a_retrieved_section_counts_as_derived(), test_closed_book_does_not_retrieve() (+1 more)

### Community 11 - "Product Intent & Requirements"
Cohesion: 0.15
Nodes (22): Log #5: Corpus Gaps Shape the Evaluation, Confirmed Intent, TaxCite, TaxCite PRD, Functional Requirements FR-1..FR-17, Goals G1-G6 (research time, seat displacement, groundedness, gates, cost, leakage), Non-Functional Requirements (latency, reliability, cost, security), Open Questions (embedding, LLM provider, frontend, backup storage, market scope) (+14 more)

### Community 12 - "Benchmark Method Lessons"
Cohesion: 0.11
Nodes (18): Log #23: A Discontinued Publication Returns HTTP 200 With HTML, Log #16: Parallel Workers Made Embedding Slower, Log #22: Choosing a PDF Library by Measuring It on the Real Document, Log #25: Screen Candidates for Viability Before Measuring Quality, ✅ Checkpoint 1 — after T1–T3, ✅ Checkpoint 2 — after T4–T6, ✅ Checkpoint 3 — after T7–T8, ✅ Checkpoint: Phase A complete (+10 more)

### Community 13 - "Store Choices & Failure Domains"
Cohesion: 0.15
Nodes (17): Qdrant Service (compose), Redis Service (compose), Log #11: Stay True to the Architecture, Defer Stores Until They Have Work, Log #9: Redis vs Postgres LISTEN/NOTIFY for Live Events, Log #10: Keep Live Delivery Separate From Tracing, Log #12: Vercel Is the Wrong Host for This Backend, Simplify Inside Components, Never By Dropping a Store, Host Port Offsets (5433 / 6380) (+9 more)

### Community 14 - "Phase A Plan & Checkpoints"
Cohesion: 0.12
Nodes (15): Architecture Decisions (for this phase), Checkpoint 1, Checkpoint 2 (human review: embedding decision), Checkpoint 3 (human review: ADR-11 decision), Checkpoint: Phase A complete, Dependency Graph, Implementation Plan: TaxCite Phase A — Core Retrieval Baseline, Overview (+7 more)

### Community 15 - "Vector Store Decision"
Cohesion: 0.23
Nodes (12): Postgres Service (pgvector/pgvector:pg16), Log #17: Chunker Output Is 12x the Section Count, Log #27: The Revisit Trigger I Wrote Was Mis-Specified, Log #8: Qdrant Over pgvector, With a Measurable Revisit Trigger, Repository Map, Phase A Complete (Status), T6b: Qdrant vs pgvector Benchmark, Non-Goals (no full GraphRAG, no BM25 engine, no token streaming, federal only) (+4 more)

### Community 16 - "Embedding Model & Thresholds"
Cohesion: 0.20
Nodes (12): Log #26: The Benchmark Died Because of Unrelated Software, Log #28: One Tied Score Made the Eval Unreproducible, Phase A Exit Report, Phase A Recalibration Notes for §9.3, What Phase A did not do, Acceptance Thresholds by Phase (§9.3), ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5, BAAI/bge-base-en-v1.5 (+4 more)

### Community 17 - "LLM Choice & Verification"
Cohesion: 0.24
Nodes (12): Log #31: The Reliability Check Measured Two Standards and Called It Noise, Log #30: The Two Models Fail in Different Directions, Three-Way Citation Counting, T8: ADR-11 LLM Benchmark, ADR-11: LLM Tiering — gpt-4o-mini, ADR-15: Zero-Tolerance Claim Suppression, ADR-3: Post-Generation Claim Verification, ADR-4: Self-Hosted NLI Model for Production Verification (+4 more)

### Community 18 - "Retrieval Measurement Findings"
Cohesion: 0.20
Nodes (11): Log #29: The Closed-Book Baseline Cited a Publication That No Longer Exists, Log #21: Gold Sets Need Validating Before They Can Validate Anything, Log #19: Hybrid Retrieval Is Not Uniformly Better Than Dense, Log #20: Measurement Overturned What One Query Suggested, Phase A Known Failures, The Pilot Set Is Data, Not Code, T3: Hybrid search CLI with citations, T4: Pilot Set and Retrieval Eval Script (+3 more)

### Community 19 - "Phase A Exit Report"
Cohesion: 0.29
Nodes (6): Decisions settled, with the evidence, Known failures, with examples, Recalibration notes for §9.3, TaxCite — Phase A exit report, The ablation ladder so far, What exists

### Community 20 - "Resilience & Operations"
Cohesion: 0.50
Nodes (4): ADR-12: Backup and Disaster Recovery, Single-Engineer Operational Bus Factor, Phase H — Resilience + Load, Production SLOs and Alerting (§3.4)

## Knowledge Gaps
- **79 isolated node(s):** `10. Keep live delivery separate from tracing`, `11. Stay true to the architecture but defer stores until they have work`, `12. Vercel is the wrong host for this backend`, `13. The iCloud bug that silently broke editable installs`, `14. Table-of-contents sections would poison retrieval` (+74 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 250 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk Model & Keys` to `IRS Publication Ingestion`, `Data & Parsing Lessons`, `CLI & Ingest Orchestration`, `CFR Paragraph Parser`?**
  _High betweenness centrality (0.358) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `Data & Parsing Lessons` to `Embedding Model & Thresholds`, `Product Intent & Requirements`, `Benchmark Method Lessons`, `Vector Store Decision`?**
  _High betweenness centrality (0.353) - this node is a cross-community bridge._
- **Why does `Confirmed Intent` connect `Product Intent & Requirements` to `Data & Parsing Lessons`, `Store Choices & Failure Domains`, `Vector Store Decision`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `ingest_ecfr()` (e.g. with `progress()` and `conn()`) actually correct?**
  _`ingest_ecfr()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `10. Keep live delivery separate from tracing`, `11. Stay true to the architecture but defer stores until they have work`, `12. Vercel is the wrong host for this backend` to the rest of the system?**
  _79 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Eval Harness Scripts` be split into smaller, more focused modules?**
  _Cohesion score 0.0532724505327245 - nodes in this community are weakly interconnected._