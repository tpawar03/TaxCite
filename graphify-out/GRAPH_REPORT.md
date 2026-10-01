# Graph Report - TaxCite.nosync  (2026-10-01)

## Corpus Check
- 228 files · ~12,430,176 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 3, .jsonl 3, .xml 3)

## Summary
- 1380 nodes · 2606 edges · 76 communities (64 shown, 12 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 185 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6adbc6b7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.py
- test_irs_pubs.py
- test_jobs.py
- T2: Ingest eCFR Title 26
- main
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
- fetch
- taxcite
- Collaborative Working Mode
- retrieval.py
- test_metrics.py
- Postgres
- aggregate
- main
- usc.py
- jobs.py
- store_bench.py
- TaxCite — Phase C exit report
- e0_authority.py
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- f5_golden.py
- conn
- Plain-Module Package Layout
- refusals_ok
- ADR-17: Vector Store — Qdrant, Not pgvector
- retrieve.py
- generate.py
- usc_notes.py
- test_temporal.py
- TaxCite — Phase D exit report
- TaxCite — Status
- run
- taxcite_ingest_caselaw
- TaxCite: Phase E exit report
- taxcite_ingest
- taxcite_ingest_citations
- call_model
- ecfr.py
- report
- citations.py
- F4 verdict check
- F0 judge check
- taxcite_ingest_ecfr
- api.py
- parse
- cli.py
- Block
- verify.py
- citations
- taxcite_ingest_irs_pubs
- section_of
- decompose.py
- taxcite/__init__.py
- test_verify.py
- stub_pipeline
- save
- f4_hide.py
- test_live_events_arrive_over_redis_while_the_job_runs
- stub
- test_fetch_rejects_a_non_pdf
- client
- paragraphs

## God Nodes (most connected - your core abstractions)
1. `F5 reference check` - 41 edges
2. `F0 judge check` - 41 edges
3. `F4 verdict check` - 31 edges
4. `search()` - 27 edges
5. `Chunk` - 24 edges
6. `conn()` - 23 edges
7. `Answer` - 22 edges
8. `Hit` - 22 edges
9. `run()` - 16 edges
10. `TaxCite Phase A — Task List` - 16 edges

## Surprising Connections (you probably didn't know these)
- `E2 and E3: the metadata, and the check that found law the parser didn't know` --references--> `save()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/store.py
- `What exists` --references--> `authorities()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/generate.py
- `What exists` --references--> `citations()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/generate.py
- `Reproducing` --references--> `answer_from_groups()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/generate.py
- `What exists` --references--> `answer()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/decompose.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]

## Communities (76 total, 12 thin omitted)

### Community 0 - "index.py"
Cohesion: 0.18
Nodes (17): psycopg_types_json, QdrantClient, batched(), count(), create_collection(), edition(), point_id(), Embed chunks and keep a Qdrant collection in step with Postgres. Postgres is… (+9 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.14
Nodes (20): _normalise(), Sliding windows with overlap; a short page yields a single window., Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count(), edges(), windows() (+12 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.13
Nodes (19): Job record and SSE transport (ADR-9), with the pipeline stubbed., ADR-9: nothing unverified reaches the user, so the answer is buffered., A Redis outage must degrade liveness, not correctness (ADR-16)., The record and the live channel can race; sequence numbers settle it., C4: flags sit beside the answer; its text is untouched., F2's refusal path, with the gate on: the stream shows its verdicts and goes…, Phase D filters on as_of; B7 only records it, so the record already shows what…, The record is written before the notification, so nothing is missed on… (+11 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.16
Nodes (15): eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark, Harvard Caselaw Access Project, Per-Document-Type Chunker (§3.2), CourtListener (+7 more)

### Community 4 - "main"
Cohesion: 0.12
Nodes (23): Budget, CostCap, extract_claims(), judge_claims(), main(), parse_json(), RuntimeError, The judge returns JSON by instruction, not by API guarantee, so parse… (+15 more)

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
Cohesion: 0.09
Nodes (29): chunks(), parametrize, Transaction time (D6): an amendment rewrites a chunk in place; the old text…, test_a_dropped_paragraph_is_retired_by_the_sweep(), test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(), test_authority_profile_comes_from_source_and_citation_form(), test_excluded_rows_are_stored_but_not_counted_as_indexable(), test_reingest_is_idempotent() (+21 more)

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
Nodes (46): gi11(), hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, C5: A cites B and C; C cites D; E cites D; Z is unheld. Hops go either…, D3b: plain-English publications outrank the statute; a statute-only search puts… (+38 more)

### Community 19 - "test_index.py"
Cohesion: 0.22
Nodes (17): chunks(), ctx(), models_(), fixture, CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., sync(), test_a_broken_qdrant_still_raises() (+9 more)

### Community 20 - "fetch"
Cohesion: 0.38
Nodes (7): fetch(), get(), Client, Path, The newest `per_topic` distinct opinions for each topic. A consolidated case is…, One opinion's PDF, cached. DAWSON hands out a short-lived signed S3 link., select()

### Community 23 - "retrieval.py"
Cohesion: 0.13
Nodes (24): argparse, datetime, dotenv, E4: apply the dev rules as written in tasks/todo.md, before looking at which…, cost_of(), estimate(), judge(), main() (+16 more)

### Community 24 - "test_metrics.py"
Cohesion: 0.12
Nodes (25): build(), collection_for(), main(), ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, Index every chunk with one model into its own collection; returns build time., score(), mrr(), ndcg_at_k() (+17 more)

### Community 26 - "aggregate"
Cohesion: 0.18
Nodes (12): aggregate(), Judged, None when there is nothing to score: a refusal, or an answer making no claim., Refusals are excluded from the mean and reported separately (§9.2). Averaging a…, judged(), An answer the extractor found nothing in would otherwise score 0/0., A row with one claim per entry in `supported`., Averaging refusals in either direction breaks the gate: 0 punishes the… (+4 more)

### Community 27 - "main"
Cohesion: 0.25
Nodes (3): main(), needs_case_law(), A row whose gold includes an opinion: routing must send a sub-query to the case…

### Community 28 - "usc.py"
Cohesion: 0.27
Nodes (16): blocks(), child_text(), chunk_section(), clean(), designation(), lead_in(), parse(), provision_blocks() (+8 more)

### Community 29 - "jobs.py"
Cohesion: 0.18
Nodes (13): Redis, F2: every part judged insufficient before synthesis. A refusal with what each…, skipped_only(), client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across… (+5 more)

### Community 30 - "store_bench.py"
Cohesion: 0.23
Nodes (11): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+3 more)

### Community 31 - "TaxCite — Phase C exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+4 more)

### Community 32 - "e0_authority.py"
Cohesion: 0.12
Nodes (26): inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the…, Part 2: which authority fields have more than one value here, and from where. (+18 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "f5_golden.py"
Cohesion: 0.13
Nodes (27): headings(), Each cached chunk's heading, which synthesis saw ("[citation] (heading)") but…, audit(), check(), checkpoint(), save(), judge(), ladder() (+19 more)

### Community 35 - "conn"
Cohesion: 0.31
Nodes (9): get, get_query(), Server-sent events for one job. Replays whatever the record already holds, then…, stream_events(), events(), get(), StreamingResponse, conn() (+1 more)

### Community 37 - "refusals_ok"
Cohesion: 0.50
Nodes (4): Refusals sit outside the faithfulness mean (see `aggregate`), so a build that…, refusals_ok(), D7's first build: faithfulness passed at 0.866 while refusing more than half…, test_refusal_rate_gate()

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "retrieve.py"
Cohesion: 0.08
Nodes (36): Filter, functools, qdrant_client, SparseVector, edition_filter(), embed(), _models(), Search the indexed corpus. Modes, because the eval ablation ladder (§9) needs… (+28 more)

### Community 40 - "generate.py"
Cohesion: 0.15
Nodes (22): Hit, Answer, answer_from_groups(), answer_from_hits(), answer_schema(), authority_label(), effective_note(), format_sources() (+14 more)

### Community 41 - "usc_notes.py"
Cohesion: 0.06
Nodes (43): amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes(), own_designation() (+35 more)

### Community 42 - "test_temporal.py"
Cohesion: 0.11
Nodes (18): pipeline_answer(), Path, Run the full pipeline once per run index and reuse it, so re-judging is free.…, as_of_match(), kappa(), passed(), Year-level match of the plan's as-of against the row's tax year. None = not…, Cohen's kappa for two raters over the same items. (+10 more)

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 45 - "run"
Cohesion: 0.18
Nodes (13): Reproducing, citation_graph(), decompose(), neighbors(), One structured-output call (ADR-11). Temperature 0 and a fixed seed, so a re-…, Held opinions within `hops` citation steps of the seeds, in either direction;…, (edges, held opinions), loaded once: 5,278 edges is small enough to walk in…, The plan's one tax year, or None: no year, or several ("2016 and 2026"), filter… (+5 more)

### Community 47 - "TaxCite: Phase E exit report"
Cohesion: 0.17
Nodes (11): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E2 and E3: the metadata, and the check that found law the parser didn't know, E4: the rerank, E5: authority in answers, Failures, with examples, Reproducing (+3 more)

### Community 50 - "call_model"
Cohesion: 0.29
Nodes (7): call_model(), MissingCredentials, RuntimeError, Raised instead of the SDK's generic auth error, which does not say what to set., Fail early and specifically. The SDK raises a generic TypeError at request…, One completion. Returns (text, input_tokens, output_tokens). The two providers…, _require_credentials()

### Community 51 - "ecfr.py"
Cohesion: 0.17
Nodes (22): collections, httpx, pdfminer_high_level, pdfminer_layout, re, Chunk, estimate_tokens(), The unit every ingester produces and every store consumes. (+14 more)

### Community 52 - "report"
Cohesion: 0.12
Nodes (15): abstention(), claim_unit(), f1(), On the not-supported class: what the verifier exists to catch. `supported` is…, The threshold that maximises not-supported F1 on the tune half. Ties go to the…, The small model decides only what it's sure of, the LLM the rest. Auto-accept…, Sentences no pair of this unit covers: every uncited one for sentences, only…, What ADR-15 would hide over answers that weren't refusals, for one claim unit.… (+7 more)

### Community 53 - "citations.py"
Cohesion: 0.05
Nodes (64): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze() (+56 more)

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "api.py"
Cohesion: 0.12
Nodes (19): asyncio, BackgroundTasks, BaseModel, fastapi, fastapi_responses, os, post, psycopg (+11 more)

### Community 58 - "parse"
Cohesion: 0.14
Nodes (16): skipif, edition_year(), fetch(), page_texts(), parse(), Path, Every chunk in one publication PDF., Download one publication, cached on disk. `delay` rate-limits bulk fetches. (+8 more)

### Community 59 - "cli.py"
Cohesion: 0.19
Nodes (25): io, Namespace, backfill_authority(), fetch(), fetch_usc(), ingest_case(), ingest_ecfr(), ingest_pubs() (+17 more)

### Community 60 - "Block"
Cohesion: 0.20
Nodes (17): Block, blocks(), walk(), cite(), clean(), pack(), flush(), Split blocks into units, starting a new one wherever `key` is set. (+9 more)

### Community 61 - "verify.py"
Cohesion: 0.15
Nodes (20): cited_items(), The sentences a structured answer can show, in order: text and at least one…, (answer text, sentences dropped) from arm E's JSON. Each sentence ends with its…, render(), apply(), checked(), premises(), prompt() (+12 more)

### Community 62 - "citations"
Cohesion: 0.19
Nodes (13): material(), Completeness over material sentences, and the share of answers that would…, Split outside brackets, at . ! ? followed by a space, never after an…, A line that states no claim: a section heading, a markdown title, a label…, sentences(), structural(), abstention(), completeness() (+5 more)

### Community 64 - "section_of"
Cohesion: 0.33
Nodes (6): authorities(), Each cited source's authority and label, for the API (E5): an exact citation…, The section a citation belongs to, ignoring paragraph depth. '26 CFR…, section_of(), ADR-13, G-A05's payload: text claiming to be binding authority can't become the…, test_a_label_comes_from_the_profile_never_from_the_source_text()

### Community 65 - "decompose.py"
Cohesion: 0.09
Nodes (30): collections_abc, dataclasses, What exists, answer(), chunks(), Decomposition, gate(), level() (+22 more)

### Community 67 - "test_verify.py"
Cohesion: 0.14
Nodes (7): pytest, Claim verification (F4), tested without spending money: the verifier call is…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, structured_answer(), test_a_note_about_a_missing_detail_survives_when_its_part_is_shown(), test_checked_fails_closed_and_leaves_refusals_alone(), test_sentence_hiding_ships()

### Community 68 - "stub_pipeline"
Cohesion: 0.50
Nodes (4): clean(), fixture, No decomposition, no retrieval, no LLM: this test is about the transport., stub_pipeline()

### Community 69 - "save"
Cohesion: 0.15
Nodes (17): Connection, authority(), expiry(), The chunk's authority profile (E2): from its source and the citation's form,…, `source_revision` where the ingester had none (E2): what `as_of` already…, whole' or 'partly' when a regulation's own clause says its applicability ended…, revision(), backfill_authority() (+9 more)

### Community 70 - "f4_hide.py"
Cohesion: 0.29
Nodes (10): base(), check_sheet(), main(), metrics(), Path, F4: one verified run, shown three ways, so the hiding unit is decided on…, The cached answer as the verifier saw it: every cited item shown., The cache entry as `unit` would show it. (+2 more)

### Community 71 - "test_live_events_arrive_over_redis_while_the_job_runs"
Cohesion: 0.67
Nodes (3): ADR-16: Redis carries progress; the record is the source of truth behind it., test_live_events_arrive_over_redis_while_the_job_runs(), worker()

### Community 75 - "client"
Cohesion: 0.60
Nodes (5): create(), main(), Path, restore(), client()

### Community 76 - "paragraphs"
Cohesion: 0.20
Nodes (10): LTTextBox, fold_numbers(), font_size(), paragraphs(), (page, text) for each paragraph, in reading order. Body text is the opinion's…, Prefix number-only pieces to the paragraph after them: a list number rejoins…, dehyphenate(), Join words split across a line break ("mo-\ntel" or "mo- tel" -> "motel"). A… (+2 more)

## Knowledge Gaps
- **199 isolated node(s):** `R01 `G-C17#0#1``, `R02 `G-S18#0#1``, `R03 `G-X14#0#1``, `R04 `G-C14#0#3``, `R05 `G-X05#0#3`` (+194 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 652 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `ecfr.py` to `index.py`, `test_ecfr.py`, `save`, `usc_notes.py`, `TaxCite — Status`, `api.py`, `parse`, `usc.py`?**
  _High betweenness centrality (0.182) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.158) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `search()` (e.g. with `Answer` and `test_payload_carries_the_authority_profile_into_hits()`) actually correct?**
  _`search()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `R01 `G-C17#0#1``, `R02 `G-S18#0#1``, `R03 `G-X14#0#1`` to the rest of the system?**
  _199 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_irs_pubs.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._
- **Should `test_jobs.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12987012987012986 - nodes in this community are weakly interconnected._