# Graph Report - TaxCite.nosync  (2026-10-01)

## Corpus Check
- 249 files · ~14,906,131 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 3, .jsonl 3, .xml 3)

## Summary
- 1415 nodes · 2678 edges · 76 communities (64 shown, 12 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 197 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9c3d46b4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.py
- irs_pubs.py
- test_jobs.py
- T2: Ingest eCFR Title 26
- main
- test_ecfr.py
- TaxCite — Phase B exit report
- f0_verify.py
- test_usc.py
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
- cli.py
- test_metrics.py
- Postgres
- jobs.py
- test_verify.py
- Chunk
- test_store.py
- store_bench.py
- TaxCite — Phase C exit report
- e0_authority.py
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- f5_golden.py
- citations.py
- Plain-Module Package Layout
- aggregate
- ADR-17: Vector Store — Qdrant, Not pgvector
- retrieve.py
- generate.py
- usc_notes.py
- verify
- TaxCite — Phase D exit report
- TaxCite — Status
- test_usc_notes.py
- taxcite_ingest_caselaw
- TaxCite: Phase E exit report
- taxcite_ingest
- taxcite_ingest_citations
- audit
- ecfr.py
- report
- parse_json
- F4 verdict check
- F0 judge check
- taxcite_ingest_ecfr
- api.py
- main
- ingest_ecfr
- TaxCite: Phase F exit report
- verify.py
- weigh
- taxcite_ingest_irs_pubs
- chunk.py
- decompose.py
- post_query
- test_a_failed_verification_sends_a_refusal_never_the_unverified_answer
- refusals_ok
- conn
- f4_hide.py
- test_health.py
- stub_pipeline
- RuntimeError
- snapshot.py
- fixture

## God Nodes (most connected - your core abstractions)
1. `F0 judge check` - 41 edges
2. `F5 reference check` - 41 edges
3. `Hit` - 34 edges
4. `F4 verdict check` - 31 edges
5. `search()` - 28 edges
6. `Chunk` - 24 edges
7. `conn()` - 23 edges
8. `Answer` - 17 edges
9. `verify()` - 16 edges
10. `run()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Open problems handed on` --references--> `flags()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/ingest/citations.py
- `What exists` --references--> `authority()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/chunk.py
- `E2 and E3: the metadata, and the check that found law the parser didn't know` --references--> `save()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/store.py
- `What exists` --references--> `citations()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/generate.py
- `Reproducing` --references--> `answer_from_groups()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/generate.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]

## Communities (76 total, 12 thin omitted)

### Community 0 - "index.py"
Cohesion: 0.10
Nodes (30): E2 and E3: the metadata, and the check that found law the parser didn't know, QdrantClient, authority(), expiry(), The chunk's authority profile (E2): from its source and the citation's form,…, `source_revision` where the ingester had none (E2): what `as_of` already…, whole' or 'partly' when a regulation's own clause says its applicability ended…, revision() (+22 more)

### Community 1 - "irs_pubs.py"
Cohesion: 0.06
Nodes (45): pdfminer_high_level, pdfminer_layout, skipif, dehyphenate(), edition_year(), fetch(), _normalise(), page_texts() (+37 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.13
Nodes (18): pytest, Job record and SSE transport (ADR-9), with the pipeline stubbed., ADR-9: nothing unverified reaches the user, so the answer is buffered., A Redis outage must degrade liveness, not correctness (ADR-16)., The record and the live channel can race; sequence numbers settle it., C4: flags sit beside the answer; its text is untouched., F2's refusal path, with the gate on: the stream shows its verdicts and goes…, Phase D filters on as_of; B7 only records it, so the record already shows what… (+10 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.16
Nodes (15): eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark, Harvard Caselaw Access Project, Per-Document-Type Chunker (§3.2), CourtListener (+7 more)

### Community 4 - "main"
Cohesion: 0.07
Nodes (36): Budget, CostCap, extract_claims(), judge_claims(), main(), pipeline_answer(), Path, RuntimeError (+28 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.06
Nodes (45): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+37 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "f0_verify.py"
Cohesion: 0.11
Nodes (24): concurrent_futures, agreement(), build(), check_sheet(), claim_text(), contains(), call(), kind_of() (+16 more)

### Community 8 - "test_usc.py"
Cohesion: 0.07
Nodes (22): memo(), fixture, Case-law tests against two real Tax Court opinions (see tasks/todo.md B3): -…, E3 (Estate of Caan): DAWSON lists the correction's date; the opinion says when…, result(), tc(), test_a_corrected_reissue_keeps_the_opinions_own_filing_date(), test_selection_dedupes_by_citation_and_keeps_the_newest() (+14 more)

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
Cohesion: 0.05
Nodes (54): premises(), prompt(), Indexes into `answer.retrieved` a sentence is judged against: the chunks it…, gi11(), hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is… (+46 more)

### Community 19 - "test_index.py"
Cohesion: 0.22
Nodes (17): chunks(), ctx(), models_(), fixture, CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., sync(), test_a_broken_qdrant_still_raises() (+9 more)

### Community 20 - "caselaw.py"
Cohesion: 0.16
Nodes (20): LTTextBox, ingest_case(), fetch(), fold_numbers(), font_size(), get(), load_selection(), pages_label() (+12 more)

### Community 23 - "cli.py"
Cohesion: 0.12
Nodes (27): argparse, collections, datetime, dotenv, E4: apply the dev rules as written in tasks/todo.md, before looking at which…, cost_of(), estimate(), judge() (+19 more)

### Community 24 - "test_metrics.py"
Cohesion: 0.10
Nodes (30): build(), collection_for(), main(), ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, Index every chunk with one model into its own collection; returns build time., score(), mrr(), ndcg_at_k() (+22 more)

### Community 26 - "jobs.py"
Cohesion: 0.22
Nodes (11): Redis, client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across…, One server-sent event. The blank line is the record separator., Append a stage to the record, then notify listeners. Record first: a listener… (+3 more)

### Community 27 - "test_verify.py"
Cohesion: 0.13
Nodes (7): taxcite, Claim verification (F4), tested without spending money: the verifier call is…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, structured_answer(), test_a_note_about_a_missing_detail_survives_when_its_part_is_shown(), test_checked_fails_closed_and_leaves_refusals_alone(), test_sentence_hiding_ships()

### Community 28 - "Chunk"
Cohesion: 0.23
Nodes (19): Chunk, Make `part` a running count per citation, so `key` is unique by construction.…, renumber(), blocks(), child_text(), chunk_section(), clean(), designation() (+11 more)

### Community 29 - "test_store.py"
Cohesion: 0.21
Nodes (15): chunks(), parametrize, Transaction time (D6): an amendment rewrites a chunk in place; the old text…, test_a_dropped_paragraph_is_retired_by_the_sweep(), test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(), test_authority_profile_comes_from_source_and_citation_form(), test_excluded_rows_are_stored_but_not_counted_as_indexable(), test_reingest_is_idempotent() (+7 more)

### Community 30 - "store_bench.py"
Cohesion: 0.23
Nodes (11): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+3 more)

### Community 31 - "TaxCite — Phase C exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+4 more)

### Community 32 - "e0_authority.py"
Cohesion: 0.13
Nodes (24): inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the…, Part 2: which authority fields have more than one value here, and from where. (+16 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "f5_golden.py"
Cohesion: 0.14
Nodes (24): material(), Completeness over material sentences, and the share of answers that would…, Split outside brackets, at . ! ? followed by a space, never after an…, A line that states no claim: a section heading, a markdown title, a label…, sentences(), structural(), abstention(), check() (+16 more)

### Community 35 - "citations.py"
Cohesion: 0.06
Nodes (61): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze() (+53 more)

### Community 37 - "aggregate"
Cohesion: 0.18
Nodes (12): aggregate(), Judged, None when there is nothing to score: a refusal, or an answer making no claim., Refusals are excluded from the mean and reported separately (§9.2). Averaging a…, judged(), An answer the extractor found nothing in would otherwise score 0/0., A row with one claim per entry in `supported`., Averaging refusals in either direction breaks the gate: 0 punishes the… (+4 more)

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "retrieve.py"
Cohesion: 0.08
Nodes (38): collections_abc, Filter, functools, SparseVector, edition_filter(), embed(), _models(), Search the indexed corpus. Modes, because the eval ablation ladder (§9) needs… (+30 more)

### Community 40 - "generate.py"
Cohesion: 0.10
Nodes (35): What exists, run_ask(), Answer, answer_from_groups(), answer_from_hits(), answer_schema(), authorities(), authority_label() (+27 more)

### Community 41 - "usc_notes.py"
Cohesion: 0.14
Nodes (24): amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes(), own_designation() (+16 more)

### Community 42 - "verify"
Cohesion: 0.19
Nodes (12): fixture, (one verdict per shown sentence, input tokens, output tokens). One call for the…, verify(), no_recite(), A verifier stub that answers by prompt: SYSTEM gets the next of…, Re-cite (F5b C3) ships on; tests that don't stub its call turn it off, and the…, routed(), stub() (+4 more)

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 45 - "test_usc_notes.py"
Cohesion: 0.26
Nodes (11): chunks(), effective(), fixture, Effective dates from the statutory notes (D4), on six real sections in…, test_a_new_section_dated_by_its_own_effective_date_note(), test_a_range_chunk_holds_its_subsections_whole(), test_amendment_below_the_label_found_after_a_heading(), test_an_exclusion_is_not_the_rule() (+3 more)

### Community 47 - "TaxCite: Phase E exit report"
Cohesion: 0.17
Nodes (11): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E4: the rerank, E5: authority in answers, Failures, with examples, Open problems handed on, Reproducing (+3 more)

### Community 50 - "audit"
Cohesion: 0.21
Nodes (14): headings(), Each cached chunk's heading, which synthesis saw ("[citation] (heading)") but…, audit(), checkpoint(), save(), judge(), load(), (done, save, path): results already paid for in a crashed run, and a function… (+6 more)

### Community 51 - "ecfr.py"
Cohesion: 0.20
Nodes (22): estimate_tokens(), make(), Block, blocks(), walk(), chunk_section(), make(), cite() (+14 more)

### Community 52 - "report"
Cohesion: 0.12
Nodes (15): abstention(), claim_unit(), f1(), On the not-supported class: what the verifier exists to catch. `supported` is…, The threshold that maximises not-supported F1 on the tune half. Ties go to the…, The small model decides only what it's sure of, the LLM the rest. Auto-accept…, Sentences no pair of this unit covers: every uncited one for sentences, only…, What ADR-15 would hide over answers that weren't refusals, for one claim unit.… (+7 more)

### Community 53 - "parse_json"
Cohesion: 0.25
Nodes (8): judge(), Judge each pair against `field`'s chunks into `out`. The main pass reads every…, parse_json(), The judge returns JSON by instruction, not by API guarantee, so parse…, parametrize, Instruction is not a guarantee; the model sometimes wraps its JSON in prose., test_a_judge_that_returns_junk_does_not_crash_the_run(), test_json_is_found_inside_chatter()

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "api.py"
Cohesion: 0.16
Nodes (13): asyncio, fastapi, fastapi_responses, psycopg, psycopg_types_json, pydantic, Response, _check() (+5 more)

### Community 58 - "main"
Cohesion: 0.25
Nodes (3): main(), needs_case_law(), A row whose gold includes an opinion: routing must send a sub-query to the case…

### Community 59 - "ingest_ecfr"
Cohesion: 0.18
Nodes (22): Connection, Namespace, _run_job(), backfill_authority(), fetch(), fetch_usc(), ingest_ecfr(), ingest_pubs() (+14 more)

### Community 60 - "TaxCite: Phase F exit report"
Cohesion: 0.25
Nodes (7): Golden, scored once on the shipped pipeline, How the phase went, Open, for later phases, Reproducing, TaxCite: Phase F exit report, The gates, What Phase F got wrong

### Community 61 - "verify.py"
Cohesion: 0.12
Nodes (26): Answer, dataclasses, What exists, os, RuntimeError, cited_items(), The sentences a structured answer can show, in order: text and at least one…, (answer text, sentences dropped) from arm E's JSON. Each sentence ends with its… (+18 more)

### Community 62 - "weigh"
Cohesion: 0.40
Nodes (6): level(), A hit's authority level (E2's profile; 0 when it has none), with E4's two…, E4's reorderings of the cross-encoder's list by authority. Nothing is dropped.…, weigh(), order(), rescore()

### Community 64 - "chunk.py"
Cohesion: 0.40
Nodes (4): re, The unit every ingester produces and every store consumes., §7805(e)(2): a temporary regulation issued after Nov. 20, 1988 expires within 3…, sunset()

### Community 65 - "decompose.py"
Cohesion: 0.08
Nodes (33): Reproducing, answer(), chunks(), citation_graph(), decompose(), Decomposition, gate(), merge() (+25 more)

### Community 66 - "post_query"
Cohesion: 0.25
Nodes (8): BackgroundTasks, BaseModel, post, post_query(), Query, Accept a question and return immediately (ADR-9). The pipeline runs 20-30s,…, create(), create_table()

### Community 67 - "test_a_failed_verification_sends_a_refusal_never_the_unverified_answer"
Cohesion: 0.40
Nodes (4): F4, fail closed: the verifier errors, and the answer event carries none of the…, test_a_failed_verification_sends_a_refusal_never_the_unverified_answer(), test_a_failing_pipeline_is_recorded_not_swallowed(), boom()

### Community 68 - "refusals_ok"
Cohesion: 0.50
Nodes (4): Refusals sit outside the faithfulness mean (see `aggregate`), so a build that…, refusals_ok(), D7's first build: faithfulness passed at 0.866 while refusing more than half…, test_refusal_rate_gate()

### Community 69 - "conn"
Cohesion: 0.23
Nodes (12): get, get_query(), Server-sent events for one job. Replays whatever the record already holds, then…, stream_events(), events(), get(), StreamingResponse, ADR-16: Redis carries progress; the record is the source of truth behind it. (+4 more)

### Community 70 - "f4_hide.py"
Cohesion: 0.29
Nodes (10): base(), check_sheet(), main(), metrics(), Path, F4: one verified run, shown three ways, so the hiding unit is decided on…, The cached answer as the verifier saw it: every cited item shown., The cache entry as `unit` would show it. (+2 more)

### Community 72 - "stub_pipeline"
Cohesion: 0.50
Nodes (4): clean(), fixture, No decomposition, no retrieval, no LLM: this test is about the transport., stub_pipeline()

### Community 75 - "snapshot.py"
Cohesion: 0.33
Nodes (8): create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), httpx, client(), subprocess

## Knowledge Gaps
- **204 isolated node(s):** `The gates`, `Golden, scored once on the shipped pipeline`, `What Phase F got wrong`, `Open, for later phases`, `Reproducing` (+199 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 667 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `chunk.py`, `index.py`, `irs_pubs.py`, `test_ecfr.py`, `usc_notes.py`, `TaxCite — Status`, `ecfr.py`, `caselaw.py`, `api.py`?**
  _High betweenness centrality (0.185) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.168) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `Hit` (e.g. with `base()` and `chunks()`) actually correct?**
  _`Hit` has 27 INFERRED edges - model-reasoned connections that need verification._
- **What connects `The gates`, `Golden, scored once on the shipped pipeline`, `What Phase F got wrong` to the rest of the system?**
  _204 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1032258064516129 - nodes in this community are weakly interconnected._
- **Should `irs_pubs.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06184012066365008 - nodes in this community are weakly interconnected._