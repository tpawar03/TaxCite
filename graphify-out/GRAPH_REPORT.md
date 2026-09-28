# Graph Report - TaxCite.nosync  (2026-09-28)

## Corpus Check
- 99 files · ~1,038,154 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 3, .jsonl 3, .xml 3)

## Summary
- 966 nodes · 1850 edges · 50 communities (41 shown, 9 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 114 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `12ffe7da`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- aggregate
- test_irs_pubs.py
- test_jobs.py
- T2: Ingest eCFR Title 26
- ragas_eval.py
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
- embed_bench.py
- decompose.py
- Postgres
- test_usc.py
- llm_bench.py
- rerank
- jobs.py
- retrieve.py
- TaxCite — Phase C exit report
- taxcite
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- test_metrics.py
- retrieval.py
- Plain-Module Package Layout
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- generate.py
- usc_notes.py
- sys
- TaxCite — Phase D exit report
- TaxCite — Status
- taxcite_ingest_caselaw
- taxcite_ingest_irs_pubs
- SubQuery
- call_model
- taxcite_ingest
- taxcite_ingest_ecfr

## God Nodes (most connected - your core abstractions)
1. `search()` - 27 edges
2. `Chunk` - 22 edges
3. `Hit` - 21 edges
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

## Communities (50 total, 9 thin omitted)

### Community 0 - "aggregate"
Cohesion: 0.24
Nodes (10): aggregate(), Refusals are excluded from the mean and reported separately (§9.2). Averaging a…, judged(), An answer the extractor found nothing in would otherwise score 0/0., A row with one claim per entry in `supported`., Averaging refusals in either direction breaks the gate: 0 punishes the…, test_a_refusal_is_not_scored_as_zero_or_as_one(), test_aggregate_counts_claims_and_unsupported_claims() (+2 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.07
Nodes (32): skipif, edition_year(), _normalise(), Sliding windows with overlap; a short page yields a single window., Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count() (+24 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.08
Nodes (25): fastapi_testclient, pytest, clean(), fixture, Job record and SSE transport (ADR-9), with the pipeline stubbed., ADR-9: nothing unverified reaches the user, so the answer is buffered., ADR-16: Redis carries progress; the record is the source of truth behind it., A Redis outage must degrade liveness, not correctness (ADR-16). (+17 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.16
Nodes (15): eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark, Harvard Caselaw Access Project, Per-Document-Type Chunker (§3.2), CourtListener (+7 more)

### Community 4 - "ragas_eval.py"
Cohesion: 0.11
Nodes (27): Budget, CostCap, extract_claims(), judge_claims(), Judged, main(), parse_json(), pipeline_answer() (+19 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.06
Nodes (51): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+43 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "retrieve"
Cohesion: 0.18
Nodes (15): Reproducing, answer(), chunks(), decompose(), Decomposition, (sub-query, its chunks) for the synthesis prompt, limited to `keep` if given.…, One structured-output call (ADR-11). Temperature 0 and a fixed seed, so a re-…, Search once per sub-query, filtered to the sources its kind allows. Fills… (+7 more)

### Community 8 - "citations.py"
Cohesion: 0.07
Nodes (52): eyecite, eyecite_models, FullCaseCitation, logging, load_selection(), The selection is cached so the corpus stays fixed while new opinions are filed., appeal(), appeal_label() (+44 more)

### Community 9 - "ecfr.py"
Cohesion: 0.06
Nodes (76): httpx, LTTextBox, pdfminer_high_level, pdfminer_layout, re, Chunk, estimate_tokens(), The unit every ingester produces and every store consumes. (+68 more)

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
Cohesion: 0.05
Nodes (79): asyncio, BackgroundTasks, BaseModel, Connection, create(), main(), Path, restore() (+71 more)

### Community 23 - "embed_bench.py"
Cohesion: 0.27
Nodes (8): datetime, build(), collection_for(), main(), ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, Index every chunk with one model into its own collection; returns build time., score(), time

### Community 24 - "decompose.py"
Cohesion: 0.15
Nodes (10): collections_abc, functools, citation_graph(), neighbors(), Split a question into typed sub-queries, and route each to the sources that can…, Held opinions within `hops` citation steps of the seeds, in either direction;…, (edges, held opinions), loaded once: 5,278 edges is small enough to walk in…, The plan's one tax year, or None: no year, or several ("2016 and 2026"), filter… (+2 more)

### Community 26 - "test_usc.py"
Cohesion: 0.16
Nodes (14): chunks(), of(), fixture, Statute chunker tests against eight real sections in…, test_en_dash_section_number_becomes_a_hyphen(), test_heading_folds_into_its_first_child(), test_neighbouring_subsections_pack_into_a_range(), test_notes_are_not_text_and_source_credit_is_the_history() (+6 more)

### Community 27 - "llm_bench.py"
Cohesion: 0.17
Nodes (15): argparse, dotenv, cost_of(), estimate(), judge(), main(), ADR-11: choose the LLM by measuring answers, not by price alone. uv run python…, Rough spend before committing: RAG prompts dominate the input tokens. (+7 more)

### Community 28 - "rerank"
Cohesion: 0.50
Nodes (4): Loaded once per process and per model, like the embedding models., Re-score candidates with a cross-encoder, which reads query and chunk together.…, rerank(), _reranker()

### Community 29 - "jobs.py"
Cohesion: 0.22
Nodes (11): Redis, client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across…, One server-sent event. The blank line is the record separator., Append a stage to the record, then notify listeners. Record first: a listener… (+3 more)

### Community 30 - "retrieve.py"
Cohesion: 0.14
Nodes (18): dataclasses, load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run… (+10 more)

### Community 31 - "TaxCite — Phase C exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+4 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "test_metrics.py"
Cohesion: 0.11
Nodes (26): mrr(), ndcg_at_k(), recall_at_k(), The section a citation belongs to, ignoring paragraph depth. '26 CFR…, section_of(), parametrize, The metrics must be right before any number computed with them means anything., Instruction is not a guarantee; the model sometimes wraps its JSON in prose. (+18 more)

### Community 35 - "retrieval.py"
Cohesion: 0.13
Nodes (18): collections, cached_decompose(), first_hits(), groups(), main(), needs_case_law(), Path, Score retrieval against the pilot set: the first rungs of the §9 ablation… (+10 more)

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "search"
Cohesion: 0.11
Nodes (25): Filter, edition_filter(), One source or several; several is how B7 routes a sub-query to the corpora that…, Keep chunks with no edition (everything but publications, and undated…, Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, search(), source_filter(), hit() (+17 more)

### Community 40 - "generate.py"
Cohesion: 0.26
Nodes (14): Answer, answer_from_groups(), answer_from_hits(), effective_note(), format_sources(), _generate(), parse_citations(), Answer a question, with and without retrieval. Two modes, because the §9… (+6 more)

### Community 41 - "usc_notes.py"
Cohesion: 0.09
Nodes (35): amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes(), own_designation() (+27 more)

### Community 42 - "sys"
Cohesion: 0.22
Nodes (8): kappa(), Cohen's kappa for two raters over the same items., sys, parametrize, The temporal gate's scoring rules (D2), on fixture values: no API calls., test_as_of_match(), test_kappa_hand_computed(), test_pass_needs_a_correct_answer_and_no_as_of_miss()

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 48 - "SubQuery"
Cohesion: 0.25
Nodes (5): merge(), parse(), (sub-queries, as_of, fallback reason). Never raises. A decomposition that…, One ranked list of k, round-robin across sub-queries, first occurrence wins.…, SubQuery

### Community 54 - "call_model"
Cohesion: 0.29
Nodes (7): call_model(), MissingCredentials, RuntimeError, Raised instead of the SDK's generic auth error, which does not say what to set., Fail early and specifically. The SDK raises a generic TypeError at request…, One completion. Returns (text, input_tokens, output_tokens). The two providers…, _require_credentials()

## Knowledge Gaps
- **80 isolated node(s):** `taxcite`, `What exists`, `The ablation ladder`, `Phase C's baseline`, `Faithfulness` (+75 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 404 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `ecfr.py` to `usc_notes.py`, `cli.py`, `TaxCite — Status`, `test_ecfr.py`?**
  _High betweenness centrality (0.240) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.217) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `Chunk` (e.g. with `parse()` and `covers()`) actually correct?**
  _`Chunk` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `Hit` (e.g. with `chunks()` and `Decomposition`) actually correct?**
  _`Hit` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `conn()` (e.g. with `main()` and `restore()`) actually correct?**
  _`conn()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **What connects `taxcite`, `What exists`, `The ablation ladder` to the rest of the system?**
  _80 weakly-connected nodes found - possible documentation gaps or missing edges._