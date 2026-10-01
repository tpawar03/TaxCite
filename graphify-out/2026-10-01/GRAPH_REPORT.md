# Graph Report - TaxCite.nosync  (2026-09-30)

## Corpus Check
- 219 files · ~11,182,200 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 3, .jsonl 3, .xml 3)

## Summary
- 1313 nodes · 2464 edges · 76 communities (58 shown, 18 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 158 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f2db3e5d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- sync
- test_irs_pubs.py
- test_jobs.py
- T2: Ingest eCFR Title 26
- ragas_eval.py
- test_ecfr.py
- TaxCite — Phase B exit report
- f0_verify.py
- test_caselaw.py
- test_usc.py
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
- temporal.py
- aggregate
- Postgres
- test_store.py
- retrieval.py
- ecfr.py
- jobs.py
- store_bench.py
- TaxCite — Phase C exit report
- test_metrics.py
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- CostCap
- e0_authority.py
- Plain-Module Package Layout
- refusals_ok
- ADR-17: Vector Store — Qdrant, Not pgvector
- retrieve.py
- generate.py
- Chunk
- sample_summary
- TaxCite — Phase D exit report
- TaxCite — Status
- decompose.py
- taxcite_ingest_caselaw
- TaxCite: Phase E exit report
- taxcite_ingest
- taxcite_ingest_citations
- validate_pilot.py
- e3_sample.py
- as_of_match
- citations.py
- F4 verdict check
- F0 judge check
- taxcite_ingest_ecfr
- conn
- stub
- ingest_ecfr
- test_a_claim_the_judge_skipped_counts_as_unsupported
- Answer
- chunks
- taxcite_ingest_irs_pubs
- parametrize
- run
- fetch
- test_verify.py
- fixture
- index.py
- f4_hide.py
- fixture
- snapshot.py
- split_sections
- Hit
- Path

## God Nodes (most connected - your core abstractions)
1. `F0 judge check` - 41 edges
2. `F4 verdict check` - 31 edges
3. `search()` - 26 edges
4. `Chunk` - 24 edges
5. `conn()` - 23 edges
6. `Answer` - 22 edges
7. `run()` - 16 edges
8. `TaxCite Phase A — Task List` - 16 edges
9. `ingest_ecfr()` - 15 edges
10. `main()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `What exists` --references--> `answer()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/decompose.py
- `E2 and E3: the metadata, and the check that found law the parser didn't know` --references--> `save()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/store.py
- `Open problems handed on` --references--> `flags()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/ingest/citations.py
- `What exists` --references--> `answer()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/decompose.py
- `What exists` --references--> `authorities()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/generate.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]

## Communities (76 total, 18 thin omitted)

### Community 0 - "sync"
Cohesion: 0.19
Nodes (13): QdrantClient, batched(), count(), create_collection(), edition(), Retry a batch once or twice: a busy host turns a slow upsert into a timeout., Delete points whose chunk no longer exists in Postgres (renumbered or repealed…, Points in the collection, or 0 when the collection does not exist yet. A… (+5 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.06
Nodes (42): skipif, dehyphenate(), edition_year(), fetch(), _normalise(), page_texts(), parse(), Path (+34 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.08
Nodes (27): fastapi_testclient, fixture, Replace the model call; record what it was asked., stub(), clean(), Job record and SSE transport (ADR-9), with the pipeline stubbed., ADR-9: nothing unverified reaches the user, so the answer is buffered., ADR-16: Redis carries progress; the record is the source of truth behind it. (+19 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.16
Nodes (15): eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark, Harvard Caselaw Access Project, Per-Document-Type Chunker (§3.2), CourtListener (+7 more)

### Community 4 - "ragas_eval.py"
Cohesion: 0.22
Nodes (16): Budget, extract_claims(), judge_claims(), main(), parse_json(), pipeline_answer(), Path, Faithfulness: is every claim in the answer supported by the chunks it was given… (+8 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.06
Nodes (45): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+37 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "f0_verify.py"
Cohesion: 0.06
Nodes (49): concurrent_futures, abstention(), agreement(), build(), check_sheet(), claim_text(), claim_unit(), contains() (+41 more)

### Community 8 - "test_caselaw.py"
Cohesion: 0.12
Nodes (8): memo(), fixture, Case-law tests against two real Tax Court opinions (see tasks/todo.md B3): -…, E3 (Estate of Caan): DAWSON lists the correction's date; the opinion says when…, result(), tc(), test_a_corrected_reissue_keeps_the_opinions_own_filing_date(), test_selection_dedupes_by_citation_and_keeps_the_newest()

### Community 9 - "test_usc.py"
Cohesion: 0.19
Nodes (12): of(), Statute chunker tests against eight real sections in…, test_en_dash_section_number_becomes_a_hyphen(), test_heading_folds_into_its_first_child(), test_neighbouring_subsections_pack_into_a_range(), test_notes_are_not_text_and_source_credit_is_the_history(), test_oversized_subsection_splits_at_level_two(), test_repealed_paragraph_stubs_are_dropped() (+4 more)

### Community 10 - "test_generate.py"
Cohesion: 0.05
Nodes (23): E5's prompt arms, each built from the pre-E5 prompt: "pre-e5" is it unchanged…, set_prompt(), Answer generation, tested without spending money: the model call is stubbed., Sampling at the default temperature made the same question answerable two ways,…, E5: the label map covers every (type, status) chunk.authority() can return,…, E5: every E5 arm is built from the pre-E5 prompt, so "pre-e5" reproduces that…, F3: arm E ships ((ii′)'s rules with rules 2 and 3 for JSON items); "pre-f3" is…, F0 found both shapes in golden answers; the old regex saw only the inner… (+15 more)

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
Nodes (46): parametrize, gi11(), hit(), plan(), Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, C5: A cites B and C; C cites D; E cites D; Z is unheld. Hops go either…, D3b: plain-English publications outrank the statute; a statute-only search puts… (+38 more)

### Community 19 - "test_index.py"
Cohesion: 0.22
Nodes (17): chunks(), ctx(), models_(), fixture, CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., sync(), test_a_broken_qdrant_still_raises() (+9 more)

### Community 20 - "cli.py"
Cohesion: 0.15
Nodes (20): collections, httpx, io, pathlib, pdfminer_high_level, pdfminer_layout, re, Command line: fetch, parse, store and index the corpora. taxcite ingest ecfr… (+12 more)

### Community 23 - "temporal.py"
Cohesion: 0.10
Nodes (26): argparse, datetime, dotenv, E4: apply the dev rules as written in tasks/todo.md, before looking at which…, cost_of(), estimate(), judge(), main() (+18 more)

### Community 24 - "aggregate"
Cohesion: 0.18
Nodes (12): aggregate(), Judged, None when there is nothing to score: a refusal, or an answer making no claim., Refusals are excluded from the mean and reported separately (§9.2). Averaging a…, judged(), An answer the extractor found nothing in would otherwise score 0/0., A row with one claim per entry in `supported`., Averaging refusals in either direction breaks the gate: 0 punishes the… (+4 more)

### Community 26 - "test_store.py"
Cohesion: 0.18
Nodes (17): chunks(), parametrize, Transaction time (D6): an amendment rewrites a chunk in place; the old text…, test_a_dropped_paragraph_is_retired_by_the_sweep(), test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(), test_authority_profile_comes_from_source_and_citation_form(), test_excluded_rows_are_stored_but_not_counted_as_indexable(), test_expiry_reads_a_regulations_own_clause_against_the_snapshot_date() (+9 more)

### Community 27 - "retrieval.py"
Cohesion: 0.10
Nodes (29): build(), collection_for(), main(), ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, Index every chunk with one model into its own collection; returns build time., score(), authority_facts(), cached_decompose() (+21 more)

### Community 28 - "ecfr.py"
Cohesion: 0.08
Nodes (51): LTTextBox, estimate_tokens(), Make `part` a running count per citation, so `key` is unique by construction.…, renumber(), fold_numbers(), font_size(), pages_label(), paragraphs() (+43 more)

### Community 29 - "jobs.py"
Cohesion: 0.18
Nodes (13): dataclasses, os, Redis, client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across… (+5 more)

### Community 30 - "store_bench.py"
Cohesion: 0.23
Nodes (11): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+3 more)

### Community 31 - "TaxCite — Phase C exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+4 more)

### Community 32 - "test_metrics.py"
Cohesion: 0.11
Nodes (17): math, parametrize, The metrics must be right before any number computed with them means anything., Instruction is not a guarantee; the model sometimes wraps its JSON in prose., E4: a conflict row passes when its controlling source reaches its target rank;…, test_a_judge_that_returns_junk_does_not_crash_the_run(), test_any_member_satisfies_a_group(), test_authority_facts_read_the_tag_at_its_target() (+9 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "CostCap"
Cohesion: 0.40
Nodes (4): CostCap, RuntimeError, Raised instead of quietly spending: an eval that can call a model in a loop…, test_the_cost_cap_stops_a_run()

### Community 35 - "e0_authority.py"
Cohesion: 0.33
Nodes (10): inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the…, Part 2: which authority fields have more than one value here, and from where. (+2 more)

### Community 37 - "refusals_ok"
Cohesion: 0.50
Nodes (4): Refusals sit outside the faithfulness mean (see `aggregate`), so a build that…, refusals_ok(), D7's first build: faithfulness passed at 0.866 while refusing more than half…, test_refusal_rate_gate()

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "retrieve.py"
Cohesion: 0.08
Nodes (39): collections_abc, Filter, functools, SparseVector, edition_filter(), embed(), Hit, _models() (+31 more)

### Community 40 - "generate.py"
Cohesion: 0.12
Nodes (28): answer_from_groups(), answer_from_hits(), answer_schema(), authorities(), authority_label(), call_model(), effective_note(), format_sources() (+20 more)

### Community 41 - "Chunk"
Cohesion: 0.10
Nodes (36): Chunk, amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes() (+28 more)

### Community 42 - "sample_summary"
Cohesion: 0.50
Nodes (4): Per sample index: rates over the rows, first judge repeat (E5). Conflict and…, sample_summary(), E5: one answer per plan set; rates per sample, misweighted tags counted on…, test_sample_summary_splits_conflict_and_guard_rows_per_sample()

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 45 - "decompose.py"
Cohesion: 0.09
Nodes (27): answer(), chunks(), Decomposition, gate(), level(), merge(), parse(), Hit (+19 more)

### Community 47 - "TaxCite: Phase E exit report"
Cohesion: 0.14
Nodes (13): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E2 and E3: the metadata, and the check that found law the parser didn't know, E4: the rerank, E5: authority in answers, Failures, with examples, Open problems handed on (+5 more)

### Community 50 - "validate_pilot.py"
Cohesion: 0.50
Nodes (4): content_words(), main(), Check a pilot set against the real corpus before any scores are computed. A…, taxcite

### Community 51 - "e3_sample.py"
Cohesion: 0.33
Nodes (9): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze() (+1 more)

### Community 52 - "as_of_match"
Cohesion: 0.50
Nodes (4): as_of_match(), Year-level match of the plan's as-of against the row's tax year. None = not…, parametrize, test_as_of_match()

### Community 53 - "citations.py"
Cohesion: 0.07
Nodes (50): eyecite, eyecite_models, FullCaseCitation, logging, appeal(), appeal_label(), cached(), cites() (+42 more)

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "conn"
Cohesion: 0.10
Nodes (26): asyncio, BackgroundTasks, BaseModel, fastapi, fastapi_responses, get, post, psycopg (+18 more)

### Community 59 - "ingest_ecfr"
Cohesion: 0.27
Nodes (19): Connection, Namespace, backfill_authority(), ingest_case(), ingest_ecfr(), ingest_pubs(), ingest_usc(), latest_as_of() (+11 more)

### Community 61 - "Answer"
Cohesion: 0.12
Nodes (25): Answer, cited_items(), The sentences a structured answer can show, in order: text and at least one…, (answer text, sentences dropped) from arm E's JSON. Each sentence ends with its…, Says INSUFFICIENT EVIDENCE and cites nothing. F3: a cited answer that flags one…, The section a citation belongs to, ignoring paragraph depth. '26 CFR…, Answer a question with retrieval (`rag`) or without it (`closed_book`)., render() (+17 more)

### Community 65 - "run"
Cohesion: 0.16
Nodes (15): Reproducing, citation_graph(), decompose(), neighbors(), One structured-output call (ADR-11). Temperature 0 and a fixed seed, so a re-…, Held opinions within `hops` citation steps of the seeds, in either direction;…, (edges, held opinions), loaded once: 5,278 edges is small enough to walk in…, The plan's one tax year, or None: no year, or several ("2016 and 2026"), filter… (+7 more)

### Community 66 - "fetch"
Cohesion: 0.40
Nodes (5): fetch(), fetch_usc(), Path, Title 26 USLM XML for a release point (default: the current one), cached on…, Download one part (or a single section) of Title 26, cached on disk. The API…

### Community 67 - "test_verify.py"
Cohesion: 0.14
Nodes (7): pytest, Claim verification (F4), tested without spending money: the verifier call is…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, structured_answer(), test_a_note_about_a_missing_detail_survives_when_its_part_is_shown(), test_checked_fails_closed_and_leaves_refusals_alone(), test_sentence_hiding_ships()

### Community 69 - "index.py"
Cohesion: 0.16
Nodes (21): psycopg_types_json, authority(), expiry(), The unit every ingester produces and every store consumes., The chunk's authority profile (E2): from its source and the citation's form,…, `source_revision` where the ingester had none (E2): what `as_of` already…, whole' or 'partly' when a regulation's own clause says its applicability ended…, §7805(e)(2): a temporary regulation issued after Nov. 20, 1988 expires within 3… (+13 more)

### Community 70 - "f4_hide.py"
Cohesion: 0.19
Nodes (14): base(), check_sheet(), main(), metrics(), Path, F4: one verified run, shown three ways, so the hiding unit is decided on…, The cached answer as the verifier saw it: every cited item shown., The cache entry as `unit` would show it. (+6 more)

### Community 75 - "snapshot.py"
Cohesion: 0.43
Nodes (6): create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), subprocess

## Knowledge Gaps
- **159 isolated node(s):** `✅ Checkpoint 1 — after T1–T3`, `✅ Checkpoint 2 — after T4–T6`, `✅ Checkpoint 3 — after T7–T8`, `✅ Checkpoint: Phase A complete`, `T2: Ingest eCFR Title 26 into Postgres + Qdrant` (+154 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 603 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `test_irs_pubs.py`, `test_ecfr.py`, `index.py`, `TaxCite — Status`, `cli.py`, `ecfr.py`?**
  _High betweenness centrality (0.188) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.171) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `search()` (e.g. with `main()` and `retrieve()`) actually correct?**
  _`search()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `Chunk` (e.g. with `parse()` and `covers()`) actually correct?**
  _`Chunk` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `✅ Checkpoint 1 — after T1–T3`, `✅ Checkpoint 2 — after T4–T6`, `✅ Checkpoint 3 — after T7–T8` to the rest of the system?**
  _159 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_irs_pubs.py` be split into smaller, more focused modules?**
  _Cohesion score 0.061170212765957445 - nodes in this community are weakly interconnected._