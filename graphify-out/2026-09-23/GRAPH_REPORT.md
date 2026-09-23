# Graph Report - TaxCite.nosync  (2026-09-22)

## Corpus Check
- 64 files · ~869,165 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 3, .jsonl 3, .xml 2)

## Summary
- 805 nodes · 1535 edges · 53 communities (47 shown, 6 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 99 edges (avg confidence: 0.88)
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
- decompose.py
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
- caselaw.py
- ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5
- taxcite
- Collaborative Working Mode
- Log #24: Adding a Second Corpus Made Retrieval Worse
- index.py
- Postgres
- test_usc.py
- retrieval.py
- score_one
- jobs.py
- store_bench.py
- conn
- test_index.py
- ragas_eval.py
- section_of
- ADR-12: Backup and Disaster Recovery
- fetch
- fetch
- eCFR Chunking Decisions
- search
- generate.py
- retrieve.py
- taxcite
- taxcite_ingest
- paragraphs
- Ingestion Pipeline (§3.2)
- parse
- title_of
- strip_boilerplate
- call_model
- rerank
- TaxCite — Status
- test_fetch_rejects_a_non_pdf

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
- `main()` --indirect_call--> `conn()`  [INFERRED]
  eval/embed_bench.py → tests/test_store.py
- `main()` --calls--> `answer()`  [INFERRED]
  eval/llm_bench.py → src/taxcite/decompose.py
- `judged()` --uses--> `Judged`  [INFERRED]
  tests/test_metrics.py → eval/ragas_eval.py
- `test_json_is_found_inside_chatter()` --calls--> `parse_json()`  [INFERRED]
  tests/test_metrics.py → eval/ragas_eval.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]
- **Measurements That Overturned a Stated Intuition** — docs_engineering_log_measured_ablation, docs_engineering_log_publication_dilution, docs_engineering_log_mis_specified_revisit_trigger, docs_engineering_log_parallel_embedding_slower, docs_engineering_log_judge_rubric_mismatch [INFERRED 0.85]

## Communities (53 total, 6 thin omitted)

### Community 0 - "test_metrics.py"
Cohesion: 0.11
Nodes (27): first_hits(), mrr(), ndcg_at_k(), 0-based rank at which each group is first satisfied, for the groups that are., recall_at_k(), Gold, math, judged() (+19 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.20
Nodes (12): Sliding windows with overlap; a short page yields a single window., windows(), page(), Publication chunking: pure functions tested on text, no PDF needed., A page shaped like a real one: header lines, body, footer., A table row like "Line 6 amount" must survive digit-normalised matching., test_short_page_is_one_window(), test_strip_boilerplate_drops_repeated_headers_and_footers() (+4 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.09
Nodes (22): fastapi_testclient, clean(), fixture, Job record and SSE transport (ADR-9), with the pipeline stubbed., ADR-9: nothing unverified reaches the user, so the answer is buffered., ADR-16: Redis carries progress; the record is the source of truth behind it., A Redis outage must degrade liveness, not correctness (ADR-16)., The record and the live channel can race; sequence numbers settle it. (+14 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.14
Nodes (14): Log #18: The Counts-Match Check Caught Silent Data Loss, Log #13: The iCloud Bug That Broke Editable Installs, Log #4: Italic Designations Are a Different Hierarchy Level, Log #15: Fixtures From Real Edge Cases, Not Invented, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense (+6 more)

### Community 4 - "cli.py"
Cohesion: 0.24
Nodes (21): Connection, io, Namespace, ingest_case(), ingest_ecfr(), ingest_pubs(), ingest_usc(), latest_as_of() (+13 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.06
Nodes (47): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+39 more)

### Community 6 - "api.py"
Cohesion: 0.14
Nodes (16): asyncio, BackgroundTasks, BaseModel, fastapi, fastapi_responses, os, post, psycopg (+8 more)

### Community 7 - "decompose.py"
Cohesion: 0.12
Nodes (17): answer(), chunks(), decompose(), Decomposition, merge(), parse(), Split a question into typed sub-queries, and route each to the sources that can…, (sub-query, its chunks) for the synthesis prompt, limited to `keep` if given.… (+9 more)

### Community 8 - "TaxCite — Engineering Log"
Cohesion: 0.06
Nodes (33): 10. Keep live delivery separate from tracing, 11. Stay true to the architecture but defer stores until they have work, 12. Vercel is the wrong host for this backend, 13. The iCloud bug that silently broke editable installs, 14. Table-of-contents sections would poison retrieval, 15. Test fixtures chosen from real edge cases, not invented, 16. Parallel workers made embedding slower, not faster, 17. The chunker's output is 12× the section count (+25 more)

### Community 9 - "ecfr.py"
Cohesion: 0.10
Nodes (47): dataclasses, Chunk, estimate_tokens(), The unit every ingester produces and every store consumes., Make `part` a running count per citation, so `key` is unique by construction.…, renumber(), parse(), make() (+39 more)

### Community 10 - "test_generate.py"
Cohesion: 0.09
Nodes (9): fixture, Answer generation, tested without spending money: the model call is stubbed., Replace the model call; record what it was asked., Chunk citations are sometimes ranges; citing one paragraph inside is precision,…, A citation not among the sources is the failure mode this system exists to…, stub(), test_a_narrower_paragraph_of_a_retrieved_section_counts_as_derived(), test_closed_book_does_not_retrieve() (+1 more)

### Community 11 - "TaxCite"
Cohesion: 0.15
Nodes (23): Log #5: Corpus Gaps Shape the Evaluation, Confirmed Intent, TaxCite, TaxCite PRD, Functional Requirements FR-1..FR-17, Goals G1-G6 (research time, seat displacement, groundedness, gates, cost, leakage), Non-Functional Requirements (latency, reliability, cost, security), Non-Goals (no full GraphRAG, no BM25 engine, no token streaming, federal only) (+15 more)

### Community 12 - "TaxCite Phase A — Task List"
Cohesion: 0.08
Nodes (27): Log #29: The Closed-Book Baseline Cited a Publication That No Longer Exists, Log #23: A Discontinued Publication Returns HTTP 200 With HTML, Log #21: Gold Sets Need Validating Before They Can Validate Anything, Log #19: Hybrid Retrieval Is Not Uniformly Better Than Dense, Log #20: Measurement Overturned What One Query Suggested, Log #16: Parallel Workers Made Embedding Slower, The Pilot Set Is Data, Not Code, ✅ Checkpoint 1 — after T1–T3 (+19 more)

### Community 13 - "Phase A Implementation Plan"
Cohesion: 0.15
Nodes (17): Qdrant Service (compose), Redis Service (compose), Log #11: Stay True to the Architecture, Defer Stores Until They Have Work, Log #9: Redis vs Postgres LISTEN/NOTIFY for Live Events, Log #10: Keep Live Delivery Separate From Tracing, Log #12: Vercel Is the Wrong Host for This Backend, Simplify Inside Components, Never By Dropping a Store, Host Port Offsets (5433 / 6380) (+9 more)

### Community 14 - "Task List"
Cohesion: 0.12
Nodes (15): Architecture Decisions (for this phase), Checkpoint 1, Checkpoint 2 (human review: embedding decision), Checkpoint 3 (human review: ADR-11 decision), Checkpoint: Phase A complete, Dependency Graph, Implementation Plan: TaxCite Phase A — Core Retrieval Baseline, Overview (+7 more)

### Community 15 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.19
Nodes (14): Postgres Service (pgvector/pgvector:pg16), Log #17: Chunker Output Is 12x the Section Count, Log #8: Qdrant Over pgvector, With a Measurable Revisit Trigger, Phase A Exit Report, Phase A Recalibration Notes for §9.3, Repository Map, Phase A Complete (Status), T6b: Qdrant vs pgvector Benchmark (+6 more)

### Community 16 - "TaxCite — Phase A exit report"
Cohesion: 0.25
Nodes (7): Decisions settled, with the evidence, Known failures, with examples, Recalibration notes for §9.3, TaxCite — Phase A exit report, The ablation ladder so far, What exists, What Phase A did not do

### Community 17 - "ADR-11: LLM Tiering — gpt-4o-mini"
Cohesion: 0.24
Nodes (12): Log #31: The Reliability Check Measured Two Standards and Called It Noise, Log #30: The Two Models Fail in Different Directions, Three-Way Citation Counting, T8: ADR-11 LLM Benchmark, ADR-11: LLM Tiering — gpt-4o-mini, ADR-15: Zero-Tolerance Claim Suppression, ADR-3: Post-Generation Claim Verification, ADR-4: Self-Hosted NLI Model for Production Verification (+4 more)

### Community 18 - "test_decompose.py"
Cohesion: 0.15
Nodes (17): pytest, hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, Phase A's path is the floor: a bad plan must not fail a question the corpus can…, The model is trusted for the routing, not the wording: rewritten text measured… (+9 more)

### Community 19 - "caselaw.py"
Cohesion: 0.31
Nodes (8): collections, httpx, pdfminer_high_level, pdfminer_layout, re, pages_label(), Tax Court opinions from DAWSON, the court's own system, into page-cited chunks.…, Ingest IRS publications (PDF). Publications have no paragraph numbering to cut…

### Community 20 - "ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5"
Cohesion: 0.18
Nodes (12): Log #26: The Benchmark Died Because of Unrelated Software, Log #27: The Revisit Trigger I Wrote Was Mis-Specified, Log #22: Choosing a PDF Library by Measuring It on the Real Document, Log #28: One Tied Score Made the Eval Unreproducible, Log #25: Screen Candidates for Viability Before Measuring Quality, Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5 (+4 more)

### Community 23 - "Log #24: Adding a Second Corpus Made Retrieval Worse"
Cohesion: 0.33
Nodes (7): Log #24: Adding a Second Corpus Made Retrieval Worse, Log #14: Table-of-Contents Sections Would Poison Retrieval, Phase A Known Failures, ADR-8: Authority-Aware Reranking, Authority-Aware Retrieval, Phase E — Authority-Aware Retrieval, Phase F — Evidence Sufficiency + Claim Verification

### Community 24 - "index.py"
Cohesion: 0.24
Nodes (13): QdrantClient, batched(), count(), create_collection(), point_id(), Embed chunks and keep a Qdrant collection in step with Postgres. Postgres is…, Retry a batch once or twice: a busy host turns a slow upsert into a timeout., Delete points whose chunk no longer exists in Postgres (renumbered or repealed… (+5 more)

### Community 26 - "test_usc.py"
Cohesion: 0.07
Nodes (20): memo(), fixture, Case-law tests against two real Tax Court opinions (see tasks/todo.md B3): -…, result(), tc(), test_selection_dedupes_by_citation_and_keeps_the_newest(), chunks(), of() (+12 more)

### Community 27 - "retrieval.py"
Cohesion: 0.12
Nodes (25): argparse, datetime, dotenv, ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, cost_of(), estimate(), judge(), main() (+17 more)

### Community 28 - "score_one"
Cohesion: 0.29
Nodes (5): cached_decompose(), main(), Path, Decompose once per plan set and reuse it, so a comparison measures the change…, score_one()

### Community 29 - "jobs.py"
Cohesion: 0.20
Nodes (13): Redis, client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across…, The pipeline, reporting each stage. Phases C-F add their steps here., One server-sent event. The blank line is the record separator. (+5 more)

### Community 30 - "store_bench.py"
Cohesion: 0.21
Nodes (12): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+4 more)

### Community 31 - "conn"
Cohesion: 0.21
Nodes (12): get, Response, _check(), get_query(), health(), Server-sent events for one job. Replays whatever the record already holds, then…, stream_events(), events() (+4 more)

### Community 32 - "test_index.py"
Cohesion: 0.36
Nodes (11): chunks(), ctx(), models_(), fixture, sync(), test_both_vectors_are_stored(), test_excluded_rows_are_not_indexed(), test_indexes_postgres_rows() (+3 more)

### Community 33 - "ragas_eval.py"
Cohesion: 0.11
Nodes (24): aggregate(), Budget, CostCap, extract_claims(), judge_claims(), Judged, main(), parse_json() (+16 more)

### Community 34 - "section_of"
Cohesion: 0.20
Nodes (9): build(), collection_for(), main(), Index every chunk with one model into its own collection; returns build time., score(), The section a citation belongs to, ignoring paragraph depth. '26 CFR…, section_of(), test_section_of_strips_paragraph_markers() (+1 more)

### Community 35 - "ADR-12: Backup and Disaster Recovery"
Cohesion: 0.50
Nodes (4): ADR-12: Backup and Disaster Recovery, Single-Engineer Operational Bus Factor, Phase H — Resilience + Load, Production SLOs and Alerting (§3.4)

### Community 36 - "fetch"
Cohesion: 0.28
Nodes (9): Client, fetch(), get(), load_selection(), Path, The newest `per_topic` distinct opinions for each topic. A consolidated case is…, The selection is cached so the corpus stays fixed while new opinions are filed., One opinion's PDF, cached. DAWSON hands out a short-lived signed S3 link. (+1 more)

### Community 37 - "fetch"
Cohesion: 0.40
Nodes (5): fetch(), fetch_usc(), Path, Title 26 USLM XML for a release point (default: the current one), cached on…, Download one part (or a single section) of Title 26, cached on disk. The API…

### Community 38 - "eCFR Chunking Decisions"
Cohesion: 0.22
Nodes (10): Log #1: Spec Chunk Size Didn't Survive the Data, Log #2: Chunk at Paragraph Designations, Two Levels Deep, Log #3: Tables — A Few Huge, Many Small and Meaningful, Log #6: The Source XML Already Carries Temporal Signals, Approximate Search Loses 22% Under a Strict Filter, eCFR Chunking Decisions, ADR-2: Bi-Temporal Fact Validity, Bi-Temporal Fact Validity (+2 more)

### Community 39 - "search"
Cohesion: 0.22
Nodes (14): Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, search(), RRF ties used to break differently per process, moving a chunk across the k…, No final 280A regulations exist, so the home-office rules live only in Pub 587., test_dense_finds_the_hobby_loss_factor(), test_hybrid_returns_k_hits_with_payload(), test_modes_can_disagree(), test_publications_answer_what_regulations_cannot() (+6 more)

### Community 40 - "generate.py"
Cohesion: 0.30
Nodes (12): Answer, answer_from_groups(), answer_from_hits(), format_sources(), _generate(), parse_citations(), Answer a question, with and without retrieval. Two modes, because the §9…, Split the answer's citations three ways: exact, derived, unsupported. The three… (+4 more)

### Community 41 - "retrieve.py"
Cohesion: 0.18
Nodes (11): collections_abc, Filter, functools, qdrant_client, SparseVector, embed(), _models(), Search the indexed corpus. Modes, because the eval ablation ladder (§9) needs… (+3 more)

### Community 44 - "paragraphs"
Cohesion: 0.20
Nodes (10): LTTextBox, fold_numbers(), font_size(), paragraphs(), (page, text) for each paragraph, in reading order. Body text is the opinion's…, Prefix number-only pieces to the paragraph after them: a list number rejoins…, dehyphenate(), Join words split across a line break ("mo-\ntel" or "mo- tel" -> "motel"). A… (+2 more)

### Community 45 - "Ingestion Pipeline (§3.2)"
Cohesion: 0.32
Nodes (8): Log #7: Origin for Content, Mirror for Change Detection, Harvard Caselaw Access Project, CourtListener, eCFR API (26 CFR), eyecite, GovInfo (GPO), Ingestion Pipeline (§3.2), uscode.house.gov (OLRC)

### Community 46 - "parse"
Cohesion: 0.29
Nodes (8): skipif, fetch(), page_texts(), parse(), Path, Every chunk in one publication PDF., Download one publication, cached on disk. `delay` rate-limits bulk fetches., test_real_publication_parses_into_cited_pages()

### Community 47 - "title_of"
Cohesion: 0.25
Nodes (8): edition_year(), title_of(), Pub 17 prints its title before the number, unlike Pub 587., Pub 946 has no edition line; the bullet list ends the title., test_edition_year_and_title(), test_title_falls_back_to_the_number(), test_title_when_it_precedes_the_number(), test_title_without_a_for_use_in_line()

### Community 48 - "strip_boilerplate"
Cohesion: 0.36
Nodes (8): _normalise(), Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count(), edges(), Edges must never cover the whole page, or a 5-line page is deleted entirely., test_short_pages_never_lose_everything()

### Community 49 - "call_model"
Cohesion: 0.29
Nodes (7): call_model(), MissingCredentials, RuntimeError, Raised instead of the SDK's generic auth error, which does not say what to set., Fail early and specifically. The SDK raises a generic TypeError at request…, One completion. Returns (text, input_tokens, output_tokens). The two providers…, _require_credentials()

### Community 50 - "rerank"
Cohesion: 0.29
Nodes (7): Loaded once per process and per model, like the embedding models., Re-score candidates with a cross-encoder, which reads query and chunk together.…, rerank(), _reranker(), hit(), The cross-encoder's job: an example that quotes a rule is not the rule., test_rerank_promotes_the_rule_over_a_chunk_that_only_mentions_it()

### Community 51 - "TaxCite — Status"
Cohesion: 0.29
Nodes (6): Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

## Knowledge Gaps
- **79 isolated node(s):** `taxcite`, `✅ Checkpoint 1 — after T1–T3`, `✅ Checkpoint 2 — after T4–T6`, `✅ Checkpoint 3 — after T7–T8`, `✅ Checkpoint: Phase A complete` (+74 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 322 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `ecfr.py` to `cli.py`, `test_ecfr.py`, `api.py`, `parse`, `caselaw.py`, `ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5`?**
  _High betweenness centrality (0.372) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5` to `TaxCite — Status`, `TaxCite`, `eCFR Chunking Decisions`?**
  _High betweenness centrality (0.362) - this node is a cross-community bridge._
- **Why does `Confirmed Intent` connect `TaxCite` to `ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5`, `Phase A Implementation Plan`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.164) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `Hit` (e.g. with `chunks()` and `Decomposition`) actually correct?**
  _`Hit` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Chunk` (e.g. with `parse()` and `parse()`) actually correct?**
  _`Chunk` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `taxcite`, `✅ Checkpoint 1 — after T1–T3`, `✅ Checkpoint 2 — after T4–T6` to the rest of the system?**
  _79 weakly-connected nodes found - possible documentation gaps or missing edges._