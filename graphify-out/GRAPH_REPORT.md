# Graph Report - TaxCite.nosync  (2026-10-01)

## Corpus Check
- 236 files · ~13,244,101 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 3, .jsonl 3, .xml 3)

## Summary
- 1397 nodes · 2663 edges · 69 communities (59 shown, 10 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 190 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8dd00e03`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.py
- test_irs_pubs.py
- test_jobs.py
- T2: Ingest eCFR Title 26
- ragas_eval.py
- test_ecfr.py
- TaxCite — Phase B exit report
- f0_verify.py
- test_store.py
- F5 reference check
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
- caselaw.py
- taxcite
- Collaborative Working Mode
- json
- test_metrics.py
- Postgres
- Chunk
- test_verify.py
- weigh
- jobs.py
- store_bench.py
- TaxCite — Phase C exit report
- e0_authority.py
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- f5_golden.py
- fetch
- Plain-Module Package Layout
- authorities
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- generate.py
- usc_notes.py
- temporal.py
- TaxCite — Phase D exit report
- TaxCite — Status
- fetch
- taxcite_ingest_caselaw
- TaxCite: Phase E exit report
- taxcite_ingest
- taxcite_ingest_citations
- suppression
- ecfr.py
- report
- citations.py
- F4 verdict check
- F0 judge check
- taxcite_ingest_ecfr
- conn
- retrieval.py
- cli.py
- e3_sample.py
- Answer
- citations
- taxcite_ingest_irs_pubs
- taxcite
- decompose.py
- store.py
- f4_hide.py
- snapshot.py

## God Nodes (most connected - your core abstractions)
1. `F0 judge check` - 41 edges
2. `F5 reference check` - 41 edges
3. `Hit` - 34 edges
4. `F4 verdict check` - 31 edges
5. `search()` - 28 edges
6. `Chunk` - 24 edges
7. `Answer` - 24 edges
8. `conn()` - 23 edges
9. `call_model()` - 16 edges
10. `run()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Open problems handed on` --references--> `flags()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/ingest/citations.py
- `E2 and E3: the metadata, and the check that found law the parser didn't know` --references--> `save()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/store.py
- `What exists` --references--> `authority()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/chunk.py
- `Reproducing` --references--> `decompose()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/decompose.py
- `Reproducing` --references--> `retrieve()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/decompose.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]

## Communities (69 total, 10 thin omitted)

### Community 0 - "index.py"
Cohesion: 0.18
Nodes (17): QdrantClient, batched(), count(), create_collection(), edition(), point_id(), Embed chunks and keep a Qdrant collection in step with Postgres. Postgres is…, Retry a batch once or twice: a busy host turns a slow upsert into a timeout. (+9 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.08
Nodes (29): skipif, _normalise(), Sliding windows with overlap; a short page yields a single window., Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count(), edges() (+21 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.08
Nodes (29): fastapi_testclient, clean(), fixture, Job record and SSE transport (ADR-9), with the pipeline stubbed., ADR-9: nothing unverified reaches the user, so the answer is buffered., ADR-16: Redis carries progress; the record is the source of truth behind it., A Redis outage must degrade liveness, not correctness (ADR-16)., The record and the live channel can race; sequence numbers settle it. (+21 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.16
Nodes (15): eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark, Harvard Caselaw Access Project, Per-Document-Type Chunker (§3.2), CourtListener (+7 more)

### Community 4 - "ragas_eval.py"
Cohesion: 0.09
Nodes (30): aggregate(), Budget, CostCap, extract_claims(), judge_claims(), Judged, main(), parse_json() (+22 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.06
Nodes (45): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+37 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "f0_verify.py"
Cohesion: 0.11
Nodes (26): concurrent_futures, agreement(), build(), check_sheet(), claim_text(), contains(), judge(), call() (+18 more)

### Community 8 - "test_store.py"
Cohesion: 0.08
Nodes (31): chunks(), parametrize, Transaction time (D6): an amendment rewrites a chunk in place; the old text…, test_a_dropped_paragraph_is_retired_by_the_sweep(), test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(), test_authority_profile_comes_from_source_and_citation_form(), test_excluded_rows_are_stored_but_not_counted_as_indexable(), test_expiry_reads_a_regulations_own_clause_against_the_snapshot_date() (+23 more)

### Community 9 - "F5 reference check"
Cohesion: 0.05
Nodes (41): F5 reference check, R01 `G-C17#0#1`, R02 `G-S18#0#1`, R03 `G-X14#0#1`, R04 `G-C14#0#3`, R05 `G-X05#0#3`, R06 `G-S06#0#2`, R07 `G-S24#0#0` (+33 more)

### Community 10 - "test_generate.py"
Cohesion: 0.04
Nodes (25): fixture, Answer generation, tested without spending money: the model call is stubbed., Sampling at the default temperature made the same question answerable two ways,…, E5: the label map covers every (type, status) chunk.authority() can return,…, E5: every E5 arm is built from the pre-E5 prompt, so "pre-e5" reproduces that…, Replace the model call; record what it was asked., F3: arm E ships ((ii′)'s rules with rules 2 and 3 for JSON items); "pre-f3" is…, F0 found both shapes in golden answers; the old regex saw only the inner… (+17 more)

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
Cohesion: 0.06
Nodes (6): Citation and treatment extraction (tasks/todo.md C3), on text shaped like the…, E3 (Gregory): CourtListener found the Eleventh Circuit's opinion but its ruling…, E3 (Banaitis): reversed in part by the Ninth Circuit, which the Supreme Court…, test_a_decided_appeal_whose_ruling_did_not_parse_is_not_pending(), test_a_failed_lookup_fails_open_and_rolls_back(), test_a_hand_checked_record_overrides_a_one_level_reading()

### Community 16 - "Phase A Exit Report"
Cohesion: 0.11
Nodes (20): Decisions settled, with the evidence, Phase A Exit Report, Phase A Known Failures, Known failures, with examples, Phase A Recalibration Notes for §9.3, Recalibration notes for §9.3, TaxCite — Phase A exit report, The ablation ladder so far (+12 more)

### Community 17 - "ADR-11: LLM Tiering — gpt-4o-mini"
Cohesion: 0.38
Nodes (7): T10: Phase A exit report, T8: ADR-11 LLM Benchmark, ADR-11: LLM Tiering — gpt-4o-mini, ADR-4: Self-Hosted NLI Model for Production Verification, claude-haiku-4-5, gpt-4o-mini, Substantive-Correctness Grading Protocol (§9.2)

### Community 18 - "test_decompose.py"
Cohesion: 0.06
Nodes (51): gi11(), hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, C5: A cites B and C; C cites D; E cites D; Z is unheld. Hops go either…, D3b: plain-English publications outrank the statute; a statute-only search puts… (+43 more)

### Community 19 - "test_index.py"
Cohesion: 0.22
Nodes (17): chunks(), ctx(), models_(), fixture, CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., sync(), test_a_broken_qdrant_still_raises() (+9 more)

### Community 20 - "caselaw.py"
Cohesion: 0.09
Nodes (35): collections, httpx, LTTextBox, pdfminer_high_level, pdfminer_layout, re, estimate_tokens(), The unit every ingester produces and every store consumes. (+27 more)

### Community 23 - "json"
Cohesion: 0.16
Nodes (14): argparse, datetime, dotenv, E4: apply the dev rules as written in tasks/todo.md, before looking at which…, cost_of(), estimate(), main(), ADR-11: choose the LLM by measuring answers, not by price alone. uv run python… (+6 more)

### Community 24 - "test_metrics.py"
Cohesion: 0.10
Nodes (32): build(), collection_for(), main(), ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, Index every chunk with one model into its own collection; returns build time., score(), mrr(), ndcg_at_k() (+24 more)

### Community 26 - "Chunk"
Cohesion: 0.23
Nodes (19): Chunk, Make `part` a running count per citation, so `key` is unique by construction.…, renumber(), blocks(), child_text(), chunk_section(), clean(), designation() (+11 more)

### Community 27 - "test_verify.py"
Cohesion: 0.11
Nodes (14): fixture, Claim verification (F4), tested without spending money: the verifier call is…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, A verifier stub that answers by prompt: SYSTEM gets the next of…, routed(), structured_answer(), stub(), fake() (+6 more)

### Community 28 - "weigh"
Cohesion: 0.40
Nodes (6): level(), A hit's authority level (E2's profile; 0 when it has none), with E4's two…, E4's reorderings of the cross-encoder's list by authority. Nothing is dropped.…, weigh(), order(), rescore()

### Community 29 - "jobs.py"
Cohesion: 0.18
Nodes (15): Reproducing, Redis, answer_from_groups(), Synthesis over sources grouped by the sub-query that retrieved them (B7). The…, client(), Event, notify(), publish() (+7 more)

### Community 30 - "store_bench.py"
Cohesion: 0.23
Nodes (11): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+3 more)

### Community 31 - "TaxCite — Phase C exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+4 more)

### Community 32 - "e0_authority.py"
Cohesion: 0.33
Nodes (10): inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the…, Part 2: which authority fields have more than one value here, and from where. (+2 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "f5_golden.py"
Cohesion: 0.15
Nodes (25): headings(), Each cached chunk's heading, which synthesis saw ("[citation] (heading)") but…, audit(), check(), checkpoint(), save(), judge(), ladder() (+17 more)

### Community 35 - "fetch"
Cohesion: 0.38
Nodes (7): fetch(), get(), Client, Path, The newest `per_topic` distinct opinions for each topic. A consolidated case is…, One opinion's PDF, cached. DAWSON hands out a short-lived signed S3 link., select()

### Community 37 - "authorities"
Cohesion: 0.40
Nodes (5): What exists, authorities(), Each cited source's authority and label, for the API (E5): an exact citation…, ADR-13, G-A05's payload: text claiming to be binding authority can't become the…, test_a_label_comes_from_the_profile_never_from_the_source_text()

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "search"
Cohesion: 0.09
Nodes (29): Filter, SparseVector, edition_filter(), embed(), _models(), Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, Loaded once per process and per model: ~4s, which every query would otherwise…, One source or several; several is how B7 routes a sub-query to the corpora that… (+21 more)

### Community 40 - "generate.py"
Cohesion: 0.09
Nodes (25): collections_abc, dataclasses, functools, answer_from_hits(), answer_schema(), authority_label(), effective_note(), format_sources() (+17 more)

### Community 41 - "usc_notes.py"
Cohesion: 0.06
Nodes (43): amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes(), own_designation() (+35 more)

### Community 42 - "temporal.py"
Cohesion: 0.10
Nodes (30): judge(), Grade one answer. `alt` applies the same rubric in different words, which is…, pipeline_answer(), Path, Run the full pipeline once per run index and reuse it, so re-judging is free.…, cached_decompose(), Decompose once per plan set and reuse it, so a comparison measures the change…, as_of_match() (+22 more)

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 45 - "fetch"
Cohesion: 0.40
Nodes (5): fetch(), fetch_usc(), Path, Title 26 USLM XML for a release point (default: the current one), cached on…, Download one part (or a single section) of Title 26, cached on disk. The API…

### Community 47 - "TaxCite: Phase E exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E2 and E3: the metadata, and the check that found law the parser didn't know, E4: the rerank, E5: authority in answers, Failures, with examples, Open problems handed on (+4 more)

### Community 50 - "suppression"
Cohesion: 0.50
Nodes (4): Sentences no pair of this unit covers: every uncited one for sentences, only…, What ADR-15 would hide over answers that weren't refusals, for one claim unit.…, suppression(), uncited()

### Community 51 - "ecfr.py"
Cohesion: 0.19
Nodes (21): §7805(e)(2): a temporary regulation issued after Nov. 20, 1988 expires within 3…, sunset(), Block, blocks(), walk(), chunk_section(), cite(), clean() (+13 more)

### Community 52 - "report"
Cohesion: 0.17
Nodes (11): abstention(), claim_unit(), f1(), On the not-supported class: what the verifier exists to catch. `supported` is…, The threshold that maximises not-supported F1 on the tune half. Ties go to the…, The small model decides only what it's sure of, the LLM the rest. Auto-accept…, Each F0 unit (cited chunks only) against today's faithfulness (LLM-extracted…, Rule 3's refusals today, over all 5 cached runs: the baseline F2's gate has to… (+3 more)

### Community 53 - "citations.py"
Cohesion: 0.06
Nodes (54): eyecite, eyecite_models, FullCaseCitation, logging, load_selection(), The selection is cached so the corpus stays fixed while new opinions are filed., appeal(), appeal_label() (+46 more)

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "conn"
Cohesion: 0.10
Nodes (27): asyncio, BackgroundTasks, BaseModel, fastapi, fastapi_responses, get, post, psycopg (+19 more)

### Community 58 - "retrieval.py"
Cohesion: 0.11
Nodes (19): authority_facts(), first_hits(), groups(), main(), needs_case_law(), Path, Score retrieval against the pilot set: the first rungs of the §9 ablation…, A row whose gold includes an opinion: routing must send a sub-query to the case… (+11 more)

### Community 59 - "cli.py"
Cohesion: 0.24
Nodes (22): Connection, io, Namespace, backfill_authority(), ingest_case(), ingest_ecfr(), ingest_pubs(), ingest_usc() (+14 more)

### Community 60 - "e3_sample.py"
Cohesion: 0.33
Nodes (9): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze() (+1 more)

### Community 61 - "Answer"
Cohesion: 0.10
Nodes (36): Answer, call_model(), cited_items(), _generate_structured(), parse_citations(), The sentences a structured answer can show, in order: text and at least one…, (answer text, sentences dropped) from arm E's JSON. Each sentence ends with its…, Says INSUFFICIENT EVIDENCE and cites nothing. F3: a cited answer that flags one… (+28 more)

### Community 62 - "citations"
Cohesion: 0.19
Nodes (13): material(), Completeness over material sentences, and the share of answers that would…, Split outside brackets, at . ! ? followed by a space, never after an…, A line that states no claim: a section heading, a markdown title, a label…, sentences(), structural(), abstention(), completeness() (+5 more)

### Community 65 - "decompose.py"
Cohesion: 0.09
Nodes (33): answer(), chunks(), citation_graph(), decompose(), Decomposition, gate(), merge(), neighbors() (+25 more)

### Community 69 - "store.py"
Cohesion: 0.19
Nodes (15): psycopg_types_json, authority(), expiry(), The chunk's authority profile (E2): from its source and the citation's form,…, `source_revision` where the ingester had none (E2): what `as_of` already…, whole' or 'partly' when a regulation's own clause says its applicability ended…, revision(), backfill_authority() (+7 more)

### Community 70 - "f4_hide.py"
Cohesion: 0.29
Nodes (10): base(), check_sheet(), main(), metrics(), Path, F4: one verified run, shown three ways, so the hiding unit is decided on…, The cached answer as the verifier saw it: every cited item shown., The cache entry as `unit` would show it. (+2 more)

### Community 75 - "snapshot.py"
Cohesion: 0.36
Nodes (7): create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), os, subprocess

## Knowledge Gaps
- **199 isolated node(s):** `taxcite`, `P01 `G-C20#0#0s``, `P02 `G-C05#1#0s``, `P03 `G-X19#1#0``, `P04 `G-X07#3#0s`` (+194 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 656 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `index.py`, `store.py`, `test_ecfr.py`, `usc_notes.py`, `TaxCite — Status`, `ecfr.py`, `caselaw.py`?**
  _High betweenness centrality (0.176) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `Hit` (e.g. with `base()` and `chunks()`) actually correct?**
  _`Hit` has 27 INFERRED edges - model-reasoned connections that need verification._
- **What connects `taxcite`, `P01 `G-C20#0#0s``, `P02 `G-C05#1#0s`` to the rest of the system?**
  _199 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_irs_pubs.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0773109243697479 - nodes in this community are weakly interconnected._
- **Should `test_jobs.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0761904761904762 - nodes in this community are weakly interconnected._