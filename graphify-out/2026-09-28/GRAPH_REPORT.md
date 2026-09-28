# Graph Report - TaxCite.nosync  (2026-09-27)

## Corpus Check
- 87 files · ~819,874 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 3, .jsonl 3, .xml 3)

## Summary
- 944 nodes · 1824 edges · 53 communities (43 shown, 10 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 112 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b2dc3dba`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ragas_eval.py
- test_irs_pubs.py
- test_jobs.py
- T2: Ingest eCFR Title 26
- conn
- test_ecfr.py
- TaxCite — Phase B exit report
- retrieve
- citations.py
- ecfr.py
- test_generate.py
- TaxCite
- TaxCite Phase A — Task List
- Phase A Implementation Plan
- Task List
- test_citations.py
- Phase A Exit Report
- ADR-11: LLM Tiering — gpt-4o-mini
- test_decompose.py
- test_index.py
- cli.py
- taxcite
- Collaborative Working Mode
- snapshot.py
- decompose.py
- Postgres
- test_usc.py
- temporal.py
- embed_bench.py
- jobs.py
- store_bench.py
- TaxCite — Phase C exit report
- index.py
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- test_metrics.py
- retrieval.py
- Plain-Module Package Layout
- edition_filter
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- generate.py
- usc_notes.py
- pytest
- taxcite_ingest_ecfr
- taxcite
- taxcite_ingest
- taxcite_ingest_caselaw
- taxcite_ingest_irs_pubs
- SubQuery
- store.py
- fetch
- TaxCite — Status
- cost

## God Nodes (most connected - your core abstractions)
1. `search()` - 27 edges
2. `Chunk` - 22 edges
3. `Hit` - 20 edges
4. `conn()` - 20 edges
5. `TaxCite Phase A — Task List` - 16 edges
6. `ingest_ecfr()` - 15 edges
7. `recall_at_k()` - 14 edges
8. `estimate_tokens()` - 14 edges
9. `ingest_case()` - 14 edges
10. `parse()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `What exists` --references--> `answer()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/decompose.py
- `Reproducing` --references--> `answer_from_groups()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/generate.py
- `Reproducing` --references--> `decompose()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/decompose.py
- `Reproducing` --references--> `retrieve()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/decompose.py
- `Reproducing` --references--> `flags()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/ingest/citations.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]

## Communities (53 total, 10 thin omitted)

### Community 0 - "ragas_eval.py"
Cohesion: 0.13
Nodes (22): aggregate(), Budget, CostCap, extract_claims(), judge_claims(), Judged, main(), parse_json() (+14 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.08
Nodes (30): skipif, _normalise(), Sliding windows with overlap; a short page yields a single window., Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count(), edges() (+22 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.09
Nodes (24): fastapi_testclient, clean(), fixture, Job record and SSE transport (ADR-9), with the pipeline stubbed., ADR-9: nothing unverified reaches the user, so the answer is buffered., ADR-16: Redis carries progress; the record is the source of truth behind it., A Redis outage must degrade liveness, not correctness (ADR-16)., The record and the live channel can race; sequence numbers settle it. (+16 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.16
Nodes (15): eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark, Harvard Caselaw Access Project, Per-Document-Type Chunker (§3.2), CourtListener (+7 more)

### Community 4 - "conn"
Cohesion: 0.12
Nodes (23): asyncio, BackgroundTasks, BaseModel, fastapi, fastapi_responses, get, post, pydantic (+15 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.06
Nodes (51): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+43 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "retrieve"
Cohesion: 0.13
Nodes (19): Reproducing, answer(), chunks(), citation_graph(), decompose(), Decomposition, neighbors(), (sub-query, its chunks) for the synthesis prompt, limited to `keep` if given.… (+11 more)

### Community 8 - "citations.py"
Cohesion: 0.07
Nodes (52): eyecite, eyecite_models, FullCaseCitation, logging, load_selection(), The selection is cached so the corpus stays fixed while new opinions are filed., appeal(), appeal_label() (+44 more)

### Community 9 - "ecfr.py"
Cohesion: 0.06
Nodes (79): collections, httpx, LTTextBox, pdfminer_high_level, pdfminer_layout, re, Chunk, estimate_tokens() (+71 more)

### Community 10 - "test_generate.py"
Cohesion: 0.08
Nodes (11): fixture, Answer generation, tested without spending money: the model call is stubbed., Sampling at the default temperature made the same question answerable two ways,…, Replace the model call; record what it was asked., Chunk citations are sometimes ranges; citing one paragraph inside is precision,…, A citation not among the sources is the failure mode this system exists to…, stub(), test_a_narrower_paragraph_of_a_retrieved_section_counts_as_derived() (+3 more)

### Community 11 - "TaxCite"
Cohesion: 0.12
Nodes (27): TaxCite, Three-Way Citation Counting, TaxCite PRD, Functional Requirements FR-1..FR-17, Goals G1-G6 (research time, seat displacement, groundedness, gates, cost, leakage), Non-Functional Requirements (latency, reliability, cost, security), Non-Goals (no full GraphRAG, no BM25 engine, no token streaming, federal only), Open Questions (embedding, LLM provider, frontend, backup storage, market scope) (+19 more)

### Community 12 - "TaxCite Phase A — Task List"
Cohesion: 0.12
Nodes (16): The Pilot Set Is Data, Not Code, ✅ Checkpoint 1 — after T1–T3, ✅ Checkpoint 2 — after T4–T6, ✅ Checkpoint 3 — after T7–T8, ✅ Checkpoint: Phase A complete, T2: Ingest eCFR Title 26 into Postgres + Qdrant, T3: Hybrid search CLI with citations, T4: Pilot Set and Retrieval Eval Script (+8 more)

### Community 13 - "Phase A Implementation Plan"
Cohesion: 0.23
Nodes (12): Redis Service (compose), Host Port Offsets (5433 / 6380), Phase A Implementation Plan, Phase A Risks and Mitigations, T1: Local stack and package skeleton, T9: Job Record and SSE Transport, ADR-16: Live Delivery Decoupled From Tracing, ADR-9: SSE Progress Stream Over a Durable Job Record (+4 more)

### Community 14 - "Task List"
Cohesion: 0.12
Nodes (15): Architecture Decisions (for this phase), Checkpoint 1, Checkpoint 2 (human review: embedding decision), Checkpoint 3 (human review: ADR-11 decision), Checkpoint: Phase A complete, Dependency Graph, Implementation Plan: TaxCite Phase A — Core Retrieval Baseline, Overview (+7 more)

### Community 15 - "test_citations.py"
Cohesion: 0.05
Nodes (8): memo(), fixture, Case-law tests against two real Tax Court opinions (see tasks/todo.md B3): -…, result(), tc(), test_selection_dedupes_by_citation_and_keeps_the_newest(), Citation and treatment extraction (tasks/todo.md C3), on text shaped like the…, test_a_failed_lookup_fails_open_and_rolls_back()

### Community 16 - "Phase A Exit Report"
Cohesion: 0.11
Nodes (20): Decisions settled, with the evidence, Phase A Exit Report, Phase A Known Failures, Known failures, with examples, Phase A Recalibration Notes for §9.3, Recalibration notes for §9.3, TaxCite — Phase A exit report, The ablation ladder so far (+12 more)

### Community 17 - "ADR-11: LLM Tiering — gpt-4o-mini"
Cohesion: 0.38
Nodes (7): T10: Phase A exit report, T8: ADR-11 LLM Benchmark, ADR-11: LLM Tiering — gpt-4o-mini, ADR-4: Self-Hosted NLI Model for Production Verification, claude-haiku-4-5, gpt-4o-mini, Substantive-Correctness Grading Protocol (§9.2)

### Community 18 - "test_decompose.py"
Cohesion: 0.12
Nodes (22): hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, C5: A cites B and C; C cites D; E cites D; Z is unheld. Hops go either…, D3b: plain-English publications outrank the statute; a statute-only search puts…, Phase A's path is the floor: a bad plan must not fail a question the corpus can… (+14 more)

### Community 19 - "test_index.py"
Cohesion: 0.23
Nodes (15): chunks(), ctx(), models_(), fixture, CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., sync(), test_a_broken_qdrant_still_raises() (+7 more)

### Community 20 - "cli.py"
Cohesion: 0.24
Nodes (21): Connection, io, Namespace, ingest_case(), ingest_ecfr(), ingest_pubs(), ingest_usc(), latest_as_of() (+13 more)

### Community 23 - "snapshot.py"
Cohesion: 0.33
Nodes (8): create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), os, client(), subprocess

### Community 24 - "decompose.py"
Cohesion: 0.16
Nodes (15): collections_abc, dataclasses, functools, SparseVector, Split a question into typed sub-queries, and route each to the sources that can…, The plan's one tax year, or None: no year, or several ("2016 and 2026"), filter…, tax_year(), embed() (+7 more)

### Community 26 - "test_usc.py"
Cohesion: 0.16
Nodes (14): chunks(), of(), fixture, Statute chunker tests against eight real sections in…, test_en_dash_section_number_becomes_a_hyphen(), test_heading_folds_into_its_first_child(), test_neighbouring_subsections_pack_into_a_range(), test_notes_are_not_text_and_source_credit_is_the_history() (+6 more)

### Community 27 - "temporal.py"
Cohesion: 0.19
Nodes (16): argparse, datetime, dotenv, cost_of(), estimate(), judge(), main(), ADR-11: choose the LLM by measuring answers, not by price alone. uv run python… (+8 more)

### Community 28 - "embed_bench.py"
Cohesion: 0.19
Nodes (11): build(), collection_for(), main(), ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, Index every chunk with one model into its own collection; returns build time., score(), The section a citation belongs to, ignoring paragraph depth. '26 CFR…, section_of() (+3 more)

### Community 29 - "jobs.py"
Cohesion: 0.20
Nodes (12): Redis, client(), create(), create_table(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across… (+4 more)

### Community 30 - "store_bench.py"
Cohesion: 0.23
Nodes (11): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+3 more)

### Community 31 - "TaxCite — Phase C exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+4 more)

### Community 32 - "index.py"
Cohesion: 0.16
Nodes (18): qdrant_client, QdrantClient, batched(), count(), create_collection(), edition(), point_id(), Embed chunks and keep a Qdrant collection in step with Postgres. Postgres is… (+10 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "test_metrics.py"
Cohesion: 0.10
Nodes (29): mrr(), ndcg_at_k(), recall_at_k(), math, judged(), parametrize, The metrics must be right before any number computed with them means anything., An answer the extractor found nothing in would otherwise score 0/0. (+21 more)

### Community 35 - "retrieval.py"
Cohesion: 0.14
Nodes (16): cached_decompose(), first_hits(), groups(), main(), needs_case_law(), Path, Score retrieval against the pilot set: the first rungs of the §9 ablation…, A row whose gold includes an opinion: routing must send a sub-query to the case… (+8 more)

### Community 37 - "edition_filter"
Cohesion: 0.25
Nodes (8): Filter, edition_filter(), One source or several; several is how B7 routes a sub-query to the corpora that…, Keep chunks with no edition (everything but publications, and undated…, source_filter(), D3's filter, against Qdrant's own semantics (in-memory), not a re-…, test_edition_filter_keeps_undated_chunks_and_nearby_editions(), kept()

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "search"
Cohesion: 0.18
Nodes (17): Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, search(), hit(), RRF ties used to break differently per process, moving a chunk across the k…, The cross-encoder's job: an example that quotes a rule is not the rule., No final 280A regulations exist, so the home-office rules live only in Pub 587., test_dense_finds_the_hobby_loss_factor(), test_hybrid_returns_k_hits_with_payload() (+9 more)

### Community 40 - "generate.py"
Cohesion: 0.18
Nodes (19): Answer, answer_from_groups(), answer_from_hits(), call_model(), format_sources(), _generate(), MissingCredentials, parse_citations() (+11 more)

### Community 41 - "usc_notes.py"
Cohesion: 0.09
Nodes (35): amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes(), own_designation() (+27 more)

### Community 42 - "pytest"
Cohesion: 0.15
Nodes (12): as_of_match(), kappa(), passed(), Year-level match of the plan's as-of against the row's tax year. None = not…, Cohen's kappa for two raters over the same items., pytest, sys, parametrize (+4 more)

### Community 48 - "SubQuery"
Cohesion: 0.25
Nodes (5): merge(), parse(), (sub-queries, as_of, fallback reason). Never raises. A decomposition that…, One ranked list of k, round-robin across sub-queries, first occurrence wins.…, SubQuery

### Community 49 - "store.py"
Cohesion: 0.33
Nodes (6): psycopg, psycopg_types_json, held_at(), datetime, Postgres storage for chunks. One table, created on demand. Writes are…, (key, text) TaxCite held for `citation` at `at`, current or since retired (D6).

### Community 50 - "fetch"
Cohesion: 0.40
Nodes (5): fetch(), fetch_usc(), Path, Title 26 USLM XML for a release point (default: the current one), cached on…, Download one part (or a single section) of Title 26, cached on disk. The API…

### Community 51 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

## Knowledge Gaps
- **67 isolated node(s):** `taxcite`, `What exists`, `The ablation ladder`, `Phase C's baseline`, `Faithfulness` (+62 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 387 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `ecfr.py` to `test_ecfr.py`, `usc_notes.py`, `store.py`, `TaxCite — Status`, `cli.py`?**
  _High betweenness centrality (0.250) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.225) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `Chunk` (e.g. with `parse()` and `covers()`) actually correct?**
  _`Chunk` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `Hit` (e.g. with `chunks()` and `Decomposition`) actually correct?**
  _`Hit` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `conn()` (e.g. with `main()` and `restore()`) actually correct?**
  _`conn()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **What connects `taxcite`, `What exists`, `The ablation ladder` to the rest of the system?**
  _67 weakly-connected nodes found - possible documentation gaps or missing edges._