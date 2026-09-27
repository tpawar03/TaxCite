# Graph Report - TaxCite.nosync  (2026-09-26)

## Corpus Check
- 68 files · ~395,435 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 3, .jsonl 3, .xml 2)

## Summary
- 834 nodes · 1603 edges · 43 communities (36 shown, 7 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 93 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ddd875cf`
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
- aggregate
- SubQuery
- taxcite
- Collaborative Working Mode
- embed_bench.py
- retrieve.py
- Postgres
- test_usc.py
- llm_bench.py
- retrieval.py
- jobs.py
- store_bench.py
- call_model
- taxcite
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- test_metrics.py
- source_filter
- Plain-Module Package Layout
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- generate.py
- taxcite_ingest
- taxcite_ingest_ecfr
- TaxCite — Status

## God Nodes (most connected - your core abstractions)
1. `search()` - 26 edges
2. `Hit` - 20 edges
3. `conn()` - 20 edges
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
- `main()` --indirect_call--> `conn()`  [INFERRED]
  eval/embed_bench.py → tests/test_store.py
- `main()` --calls--> `answer()`  [INFERRED]
  eval/llm_bench.py → src/taxcite/decompose.py
- `judged()` --uses--> `Judged`  [INFERRED]
  tests/test_metrics.py → eval/ragas_eval.py
- `test_a_judge_that_returns_junk_does_not_crash_the_run()` --calls--> `parse_json()`  [INFERRED]
  tests/test_metrics.py → eval/ragas_eval.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]

## Communities (43 total, 7 thin omitted)

### Community 0 - "ragas_eval.py"
Cohesion: 0.13
Nodes (20): Budget, CostCap, extract_claims(), judge_claims(), Judged, main(), parse_json(), pipeline_answer() (+12 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.07
Nodes (32): skipif, edition_year(), _normalise(), Sliding windows with overlap; a short page yields a single window., Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count() (+24 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.06
Nodes (45): fastapi_testclient, pytest, chunks(), ctx(), models_(), fixture, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard… (+37 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.13
Nodes (19): The Pilot Set Is Data, Not Code, eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T10: Phase A exit report, T2: Ingest eCFR Title 26, T3: Hybrid search CLI with citations, T4: Pilot Set and Retrieval Eval Script, T5: Ingest IRS Publications (+11 more)

### Community 4 - "cli.py"
Cohesion: 0.07
Nodes (58): argparse, Connection, create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), httpx (+50 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.07
Nodes (41): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+33 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "Decomposition"
Cohesion: 0.21
Nodes (10): answer(), chunks(), decompose(), Decomposition, (sub-query, its chunks) for the synthesis prompt, limited to `keep` if given.…, One structured-output call (ADR-11). Temperature 0 and a fixed seed, so a re-…, Search once per sub-query, filtered to the sources its kind allows. Fills…, The k chunks synthesis sees: every sub-query's hits, ordered by the cross-… (+2 more)

### Community 8 - "citations.py"
Cohesion: 0.07
Nodes (50): eyecite, eyecite_models, FullCaseCitation, logging, load_selection(), The selection is cached so the corpus stays fixed while new opinions are filed., appeal(), appeal_label() (+42 more)

### Community 9 - "ecfr.py"
Cohesion: 0.06
Nodes (74): collections, LTTextBox, pdfminer_high_level, pdfminer_layout, Chunk, estimate_tokens(), The unit every ingester produces and every store consumes., Make `part` a running count per citation, so `key` is unique by construction.… (+66 more)

### Community 10 - "test_generate.py"
Cohesion: 0.08
Nodes (11): fixture, Answer generation, tested without spending money: the model call is stubbed., Sampling at the default temperature made the same question answerable two ways,…, Replace the model call; record what it was asked., Chunk citations are sometimes ranges; citing one paragraph inside is precision,…, A citation not among the sources is the failure mode this system exists to…, stub(), test_a_narrower_paragraph_of_a_retrieved_section_counts_as_derived() (+3 more)

### Community 11 - "TaxCite"
Cohesion: 0.14
Nodes (23): TaxCite, TaxCite PRD, Functional Requirements FR-1..FR-17, Goals G1-G6 (research time, seat displacement, groundedness, gates, cost, leakage), Non-Functional Requirements (latency, reliability, cost, security), Non-Goals (no full GraphRAG, no BM25 engine, no token streaming, federal only), Open Questions (embedding, LLM provider, frontend, backup storage, market scope), Renee (Enrolled Agent persona) (+15 more)

### Community 12 - "TaxCite Phase A — Task List"
Cohesion: 0.17
Nodes (11): ✅ Checkpoint 1 — after T1–T3, ✅ Checkpoint 2 — after T4–T6, ✅ Checkpoint 3 — after T7–T8, ✅ Checkpoint: Phase A complete, T2: Ingest eCFR Title 26 into Postgres + Qdrant, T4: Pilot set (20 questions) and retrieval eval script, T6: Embedding-model benchmark and decision, T6b: ADR-17 revisit trigger — Qdrant vs. pgvector (+3 more)

### Community 13 - "Phase A Implementation Plan"
Cohesion: 0.19
Nodes (14): Qdrant Service (compose), Redis Service (compose), Host Port Offsets (5433 / 6380), Phase A Implementation Plan, Phase A Risks and Mitigations, T1: Local stack and package skeleton, T9: Job Record and SSE Transport, ADR-16: Live Delivery Decoupled From Tracing (+6 more)

### Community 14 - "Task List"
Cohesion: 0.12
Nodes (15): Architecture Decisions (for this phase), Checkpoint 1, Checkpoint 2 (human review: embedding decision), Checkpoint 3 (human review: ADR-11 decision), Checkpoint: Phase A complete, Dependency Graph, Implementation Plan: TaxCite Phase A — Core Retrieval Baseline, Overview (+7 more)

### Community 15 - "test_citations.py"
Cohesion: 0.06
Nodes (7): memo(), fixture, Case-law tests against two real Tax Court opinions (see tasks/todo.md B3): -…, result(), tc(), test_selection_dedupes_by_citation_and_keeps_the_newest(), Citation and treatment extraction (tasks/todo.md C3), on text shaped like the…

### Community 16 - "Phase A Exit Report"
Cohesion: 0.09
Nodes (24): Decisions settled, with the evidence, Phase A Exit Report, Phase A Known Failures, Known failures, with examples, Phase A Recalibration Notes for §9.3, Recalibration notes for §9.3, TaxCite — Phase A exit report, The ablation ladder so far (+16 more)

### Community 17 - "ADR-11: LLM Tiering — gpt-4o-mini"
Cohesion: 0.27
Nodes (10): Three-Way Citation Counting, T8: ADR-11 LLM Benchmark, ADR-11: LLM Tiering — gpt-4o-mini, ADR-15: Zero-Tolerance Claim Suppression, ADR-3: Post-Generation Claim Verification, ADR-4: Self-Hosted NLI Model for Production Verification, Post-Generation Claim Verification, claude-haiku-4-5 (+2 more)

### Community 18 - "test_decompose.py"
Cohesion: 0.16
Nodes (16): hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, Phase A's path is the floor: a bad plan must not fail a question the corpus can…, The model is trusted for the routing, not the wording: rewritten text measured…, test_an_unusable_plan_falls_back_to_one_unrouted_search() (+8 more)

### Community 19 - "aggregate"
Cohesion: 0.24
Nodes (10): aggregate(), Refusals are excluded from the mean and reported separately (§9.2). Averaging a…, judged(), An answer the extractor found nothing in would otherwise score 0/0., A row with one claim per entry in `supported`., Averaging refusals in either direction breaks the gate: 0 punishes the…, test_a_refusal_is_not_scored_as_zero_or_as_one(), test_aggregate_counts_claims_and_unsupported_claims() (+2 more)

### Community 20 - "SubQuery"
Cohesion: 0.25
Nodes (5): merge(), parse(), (sub-queries, as_of, fallback reason). Never raises. A decomposition that…, One ranked list of k, round-robin across sub-queries, first occurrence wins.…, SubQuery

### Community 23 - "embed_bench.py"
Cohesion: 0.18
Nodes (12): datetime, build(), collection_for(), main(), ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, Index every chunk with one model into its own collection; returns build time., score(), qdrant_client (+4 more)

### Community 24 - "retrieve.py"
Cohesion: 0.18
Nodes (13): collections_abc, dataclasses, functools, SparseVector, Split a question into typed sub-queries, and route each to the sources that can…, embed(), _models(), Search the indexed corpus. Modes, because the eval ablation ladder (§9) needs… (+5 more)

### Community 26 - "test_usc.py"
Cohesion: 0.16
Nodes (14): chunks(), of(), fixture, Statute chunker tests against eight real sections in…, test_en_dash_section_number_becomes_a_hyphen(), test_heading_folds_into_its_first_child(), test_neighbouring_subsections_pack_into_a_range(), test_notes_are_not_text_and_source_credit_is_the_history() (+6 more)

### Community 27 - "llm_bench.py"
Cohesion: 0.22
Nodes (12): dotenv, cost_of(), estimate(), judge(), main(), ADR-11: choose the LLM by measuring answers, not by price alone. uv run python…, Rough spend before committing: RAG prompts dominate the input tokens., Grade one answer. `alt` applies the same rubric in different words, which is… (+4 more)

### Community 28 - "retrieval.py"
Cohesion: 0.12
Nodes (21): cached_decompose(), first_hits(), groups(), main(), mrr(), needs_case_law(), Path, Score retrieval against the pilot set: the first rungs of the §9 ablation… (+13 more)

### Community 29 - "jobs.py"
Cohesion: 0.07
Nodes (36): asyncio, BackgroundTasks, BaseModel, fastapi, fastapi_responses, get, json, post (+28 more)

### Community 30 - "store_bench.py"
Cohesion: 0.23
Nodes (11): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+3 more)

### Community 31 - "call_model"
Cohesion: 0.29
Nodes (7): call_model(), MissingCredentials, RuntimeError, Raised instead of the SDK's generic auth error, which does not say what to set., Fail early and specifically. The SDK raises a generic TypeError at request…, One completion. Returns (text, input_tokens, output_tokens). The two providers…, _require_credentials()

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "test_metrics.py"
Cohesion: 0.20
Nodes (14): ndcg_at_k(), recall_at_k(), parametrize, The metrics must be right before any number computed with them means anything., Instruction is not a guarantee; the model sometimes wraps its JSON in prose., test_a_group_counts_once_even_when_several_members_are_retrieved(), test_a_judge_that_returns_junk_does_not_crash_the_run(), test_any_member_satisfies_a_group() (+6 more)

### Community 35 - "source_filter"
Cohesion: 0.67
Nodes (3): Filter, One source or several; several is how B7 routes a sub-query to the corpora that…, source_filter()

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.20
Nodes (12): Postgres Service (pgvector/pgvector:pg16), Approximate Search Loses 22% Under a Strict Filter, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity, Bi-Temporal Fact Validity, Single-Engineer Operational Bus Factor (+4 more)

### Community 39 - "search"
Cohesion: 0.18
Nodes (17): Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, search(), hit(), RRF ties used to break differently per process, moving a chunk across the k…, The cross-encoder's job: an example that quotes a rule is not the rule., No final 280A regulations exist, so the home-office rules live only in Pub 587., test_dense_finds_the_hobby_loss_factor(), test_hybrid_returns_k_hits_with_payload() (+9 more)

### Community 40 - "generate.py"
Cohesion: 0.23
Nodes (13): Answer, answer_from_groups(), answer_from_hits(), cost(), format_sources(), _generate(), parse_citations(), Answer a question, with and without retrieval. Two modes, because the §9… (+5 more)

### Community 51 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

## Knowledge Gaps
- **58 isolated node(s):** `taxcite`, `What exists`, `The ablation ladder`, `Phase C's baseline`, `Faithfulness` (+53 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 338 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `ecfr.py` to `TaxCite — Status`, `cli.py`, `test_ecfr.py`?**
  _High betweenness centrality (0.265) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.249) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `Hit` (e.g. with `chunks()` and `Decomposition`) actually correct?**
  _`Hit` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `conn()` (e.g. with `main()` and `restore()`) actually correct?**
  _`conn()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Chunk` (e.g. with `parse()` and `parse()`) actually correct?**
  _`Chunk` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `taxcite`, `What exists`, `The ablation ladder` to the rest of the system?**
  _58 weakly-connected nodes found - possible documentation gaps or missing edges._