# Graph Report - TaxCite.nosync  (2026-09-22)

## Corpus Check
- 49 files · ~80,516 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 3, .jsonl 3, .xml 2)

## Summary
- 700 nodes · 1312 edges · 38 communities (32 shown, 6 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 77 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `df0703ec`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- store_bench.py
- test_irs_pubs.py
- test_jobs.py
- T2: Ingest eCFR Title 26
- ingest_ecfr
- test_ecfr.py
- api.py
- search
- TaxCite — Engineering Log
- ecfr.py
- test_generate.py
- Post-Generation Claim Verification
- TaxCite Phase A — Task List
- Phase A Implementation Plan
- Task List
- ADR-17: Vector Store — Qdrant, Not pgvector
- Phase A Exit Report
- ADR-11: LLM Tiering — gpt-4o-mini
- cli.py
- parse
- ADR-12: Backup and Disaster Recovery
- taxcite
- Collaborative Working Mode
- taxcite
- taxcite_ingest
- Postgres
- test_usc.py
- Decisions Log
- index.py
- jobs.py
- Repository Map
- post_query
- fetch
- fetch
- conn
- strip_boilerplate
- paragraphs
- test_fetch_rejects_a_non_pdf

## God Nodes (most connected - your core abstractions)
1. `TaxCite — Engineering Log` - 33 edges
2. `search()` - 22 edges
3. `conn()` - 18 edges
4. `Chunk` - 17 edges
5. `TaxCite Phase A — Task List` - 16 edges
6. `ingest_ecfr()` - 15 edges
7. `estimate_tokens()` - 14 edges
8. `ingest_case()` - 14 edges
9. `parse()` - 14 edges
10. `of()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Three-Way Citation Counting` --conceptually_related_to--> `Post-Generation Claim Verification`  [INFERRED]
  STATUS.md → taxcite-technical-documentation.md
- `PII Redaction Ordering as a CI Invariant` --semantically_similar_to--> `Log #18: The Counts-Match Check Caught Silent Data Loss`  [INFERRED] [semantically similar]
  taxcite-technical-documentation.md → docs/engineering-log.md
- `main()` --indirect_call--> `conn()`  [INFERRED]
  eval/embed_bench.py → tests/test_store.py
- `test_any_member_satisfies_a_group()` --calls--> `recall_at_k()`  [INFERRED]
  tests/test_metrics.py → eval/retrieval.py
- `test_recall_counts_only_gold_hits()` --calls--> `recall_at_k()`  [INFERRED]
  tests/test_metrics.py → eval/retrieval.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]
- **Measurements That Overturned a Stated Intuition** — docs_engineering_log_measured_ablation, docs_engineering_log_publication_dilution, docs_engineering_log_mis_specified_revisit_trigger, docs_engineering_log_parallel_embedding_slower, docs_engineering_log_judge_rubric_mismatch [INFERRED 0.85]

## Communities (38 total, 6 thin omitted)

### Community 0 - "store_bench.py"
Cohesion: 0.06
Nodes (60): argparse, dotenv, build(), collection_for(), main(), ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, Index every chunk with one model into its own collection; returns build time., score() (+52 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.15
Nodes (16): dehyphenate(), Sliding windows with overlap; a short page yields a single window., Join words split across a line break ("mo-\ntel" or "mo- tel" -> "motel"). A…, windows(), page(), Publication chunking: pure functions tested on text, no PDF needed., A page shaped like a real one: header lines, body, footer., A table row like "Line 6 amount" must survive digit-normalised matching. (+8 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.07
Nodes (39): fastapi_testclient, pytest, chunks(), ctx(), models_(), fixture, sync(), test_both_vectors_are_stored() (+31 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.07
Nodes (32): Log #1: Spec Chunk Size Didn't Survive the Data, Log #18: The Counts-Match Check Caught Silent Data Loss, Log #13: The iCloud Bug That Broke Editable Installs, Log #4: Italic Designations Are a Different Hierarchy Level, Log #2: Chunk at Paragraph Designations, Two Levels Deep, Log #15: Fixtures From Real Edge Cases, Not Invented, Log #7: Origin for Content, Mirror for Change Detection, Log #3: Tables — A Few Huge, Many Small and Meaningful (+24 more)

### Community 4 - "ingest_ecfr"
Cohesion: 0.34
Nodes (16): Connection, Namespace, ingest_case(), ingest_ecfr(), ingest_pubs(), ingest_usc(), main(), progress() (+8 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.07
Nodes (41): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+33 more)

### Community 6 - "api.py"
Cohesion: 0.19
Nodes (11): asyncio, datetime, fastapi, fastapi_responses, os, psycopg, pydantic, Response (+3 more)

### Community 7 - "search"
Cohesion: 0.08
Nodes (36): dataclasses, functools, RuntimeError, SparseVector, Answer, answer_from_hits(), call_model(), format_sources() (+28 more)

### Community 8 - "TaxCite — Engineering Log"
Cohesion: 0.06
Nodes (33): 10. Keep live delivery separate from tracing, 11. Stay true to the architecture but defer stores until they have work, 12. Vercel is the wrong host for this backend, 13. The iCloud bug that silently broke editable installs, 14. Table-of-contents sections would poison retrieval, 15. Test fixtures chosen from real edge cases, not invented, 16. Parallel workers made embedding slower, not faster, 17. The chunker's output is 12× the section count (+25 more)

### Community 9 - "ecfr.py"
Cohesion: 0.12
Nodes (39): estimate_tokens(), make(), Block, blocks(), walk(), chunk_section(), make(), cite() (+31 more)

### Community 10 - "test_generate.py"
Cohesion: 0.09
Nodes (9): fixture, Answer generation, tested without spending money: the model call is stubbed., Replace the model call; record what it was asked., Chunk citations are sometimes ranges; citing one paragraph inside is precision,…, A citation not among the sources is the failure mode this system exists to…, stub(), test_a_narrower_paragraph_of_a_retrieved_section_counts_as_derived(), test_closed_book_does_not_retrieve() (+1 more)

### Community 11 - "Post-Generation Claim Verification"
Cohesion: 0.14
Nodes (20): Log #5: Corpus Gaps Shape the Evaluation, Log #24: Adding a Second Corpus Made Retrieval Worse, Log #14: Table-of-Contents Sections Would Poison Retrieval, Phase A Known Failures, Functional Requirements FR-1..FR-17, ADR-1: Decomposition + Bounded Citation-Graph Traversal, ADR-10: Batch the Sufficiency Gate Into One Call Per Sub-Query, ADR-3: Post-Generation Claim Verification (+12 more)

### Community 12 - "TaxCite Phase A — Task List"
Cohesion: 0.08
Nodes (28): Log #29: The Closed-Book Baseline Cited a Publication That No Longer Exists, Log #23: A Discontinued Publication Returns HTTP 200 With HTML, Log #21: Gold Sets Need Validating Before They Can Validate Anything, Log #19: Hybrid Retrieval Is Not Uniformly Better Than Dense, Log #20: Measurement Overturned What One Query Suggested, Log #16: Parallel Workers Made Embedding Slower, Log #22: Choosing a PDF Library by Measuring It on the Real Document, Log #25: Screen Candidates for Viability Before Measuring Quality (+20 more)

### Community 13 - "Phase A Implementation Plan"
Cohesion: 0.13
Nodes (20): Qdrant Service (compose), Redis Service (compose), Log #11: Stay True to the Architecture, Defer Stores Until They Have Work, Log #9: Redis vs Postgres LISTEN/NOTIFY for Live Events, Log #10: Keep Live Delivery Separate From Tracing, Log #12: Vercel Is the Wrong Host for This Backend, Simplify Inside Components, Never By Dropping a Store, Host Port Offsets (5433 / 6380) (+12 more)

### Community 14 - "Task List"
Cohesion: 0.12
Nodes (15): Architecture Decisions (for this phase), Checkpoint 1, Checkpoint 2 (human review: embedding decision), Checkpoint 3 (human review: ADR-11 decision), Checkpoint: Phase A complete, Dependency Graph, Implementation Plan: TaxCite Phase A — Core Retrieval Baseline, Overview (+7 more)

### Community 15 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.40
Nodes (6): Postgres Service (pgvector/pgvector:pg16), Log #17: Chunker Output Is 12x the Section Count, Log #8: Qdrant Over pgvector, With a Measurable Revisit Trigger, T6b: Qdrant vs pgvector Benchmark, ADR-17: Vector Store — Qdrant, Not pgvector, pgvector

### Community 16 - "Phase A Exit Report"
Cohesion: 0.11
Nodes (20): Log #26: The Benchmark Died Because of Unrelated Software, Log #28: One Tied Score Made the Eval Unreproducible, Decisions settled, with the evidence, Phase A Exit Report, Known failures, with examples, Phase A Recalibration Notes for §9.3, Recalibration notes for §9.3, TaxCite — Phase A exit report (+12 more)

### Community 17 - "ADR-11: LLM Tiering — gpt-4o-mini"
Cohesion: 0.21
Nodes (12): Log #31: The Reliability Check Measured Two Standards and Called It Noise, Log #27: The Revisit Trigger I Wrote Was Mis-Specified, Log #30: The Two Models Fail in Different Directions, Three-Way Citation Counting, T10: Phase A exit report, T8: ADR-11 LLM Benchmark, ADR-11: LLM Tiering — gpt-4o-mini, ADR-15: Zero-Tolerance Claim Suppression (+4 more)

### Community 18 - "cli.py"
Cohesion: 0.15
Nodes (21): collections, httpx, io, pathlib, pdfminer_high_level, pdfminer_layout, re, Chunk (+13 more)

### Community 19 - "parse"
Cohesion: 0.14
Nodes (16): skipif, edition_year(), fetch(), page_texts(), parse(), Path, Every chunk in one publication PDF., Download one publication, cached on disk. `delay` rate-limits bulk fetches. (+8 more)

### Community 20 - "ADR-12: Backup and Disaster Recovery"
Cohesion: 0.50
Nodes (4): ADR-12: Backup and Disaster Recovery, Single-Engineer Operational Bus Factor, Phase H — Resilience + Load, Production SLOs and Alerting (§3.4)

### Community 26 - "test_usc.py"
Cohesion: 0.07
Nodes (20): memo(), fixture, Case-law tests against two real Tax Court opinions (see tasks/todo.md B3): -…, result(), tc(), test_selection_dedupes_by_citation_and_keeps_the_newest(), chunks(), of() (+12 more)

### Community 27 - "Decisions Log"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 28 - "index.py"
Cohesion: 0.18
Nodes (16): collections_abc, qdrant_client, QdrantClient, batched(), count(), create_collection(), point_id(), Embed chunks and keep a Qdrant collection in step with Postgres. Postgres is… (+8 more)

### Community 29 - "jobs.py"
Cohesion: 0.22
Nodes (12): Redis, client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across…, The pipeline, reporting each stage. Phases C-F add their steps here., One server-sent event. The blank line is the record separator. (+4 more)

### Community 30 - "Repository Map"
Cohesion: 0.23
Nodes (11): Confirmed Intent, Repository Map, TaxCite, TaxCite PRD, Goals G1-G6 (research time, seat displacement, groundedness, gates, cost, leakage), Non-Functional Requirements (latency, reliability, cost, security), Open Questions (embedding, LLM provider, frontend, backup storage, market scope), Renee (Enrolled Agent persona) (+3 more)

### Community 31 - "post_query"
Cohesion: 0.22
Nodes (9): BackgroundTasks, BaseModel, post, post_query(), Query, Accept a question and return immediately (ADR-9). The pipeline runs 20-30s,…, _run_job(), create() (+1 more)

### Community 32 - "fetch"
Cohesion: 0.28
Nodes (9): Client, fetch(), get(), load_selection(), Path, The newest `per_topic` distinct opinions for each topic. A consolidated case is…, The selection is cached so the corpus stays fixed while new opinions are filed., One opinion's PDF, cached. DAWSON hands out a short-lived signed S3 link. (+1 more)

### Community 33 - "fetch"
Cohesion: 0.40
Nodes (5): fetch(), fetch_usc(), Path, Title 26 USLM XML for a release point (default: the current one), cached on…, Download one part (or a single section) of Title 26, cached on disk. The API…

### Community 34 - "conn"
Cohesion: 0.31
Nodes (9): get, get_query(), Server-sent events for one job. Replays whatever the record already holds, then…, stream_events(), events(), get(), StreamingResponse, conn() (+1 more)

### Community 35 - "strip_boilerplate"
Cohesion: 0.36
Nodes (8): _normalise(), Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count(), edges(), Edges must never cover the whole page, or a 5-line page is deleted entirely., test_short_pages_never_lose_everything()

### Community 36 - "paragraphs"
Cohesion: 0.33
Nodes (6): LTTextBox, fold_numbers(), font_size(), paragraphs(), (page, text) for each paragraph, in reading order. Body text is the opinion's…, Prefix number-only pieces to the paragraph after them: a list number rejoins…

## Knowledge Gaps
- **79 isolated node(s):** `taxcite`, `✅ Checkpoint 1 — after T1–T3`, `✅ Checkpoint 2 — after T4–T6`, `✅ Checkpoint 3 — after T7–T8`, `✅ Checkpoint: Phase A complete` (+74 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 278 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `cli.py` to `ingest_ecfr`, `test_ecfr.py`, `api.py`, `ecfr.py`, `parse`, `Decisions Log`?**
  _High betweenness centrality (0.407) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `Decisions Log` to `T2: Ingest eCFR Title 26`, `TaxCite Phase A — Task List`, `Phase A Exit Report`, `ADR-11: LLM Tiering — gpt-4o-mini`, `Repository Map`?**
  _High betweenness centrality (0.395) - this node is a cross-community bridge._
- **Why does `Confirmed Intent` connect `Repository Map` to `Decisions Log`, `Phase A Implementation Plan`?**
  _High betweenness centrality (0.179) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Chunk` (e.g. with `parse()` and `parse()`) actually correct?**
  _`Chunk` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `taxcite`, `✅ Checkpoint 1 — after T1–T3`, `✅ Checkpoint 2 — after T4–T6` to the rest of the system?**
  _79 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `store_bench.py` be split into smaller, more focused modules?**
  _Cohesion score 0.056338028169014086 - nodes in this community are weakly interconnected._