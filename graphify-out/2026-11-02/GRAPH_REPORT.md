# Graph Report - TaxCite.nosync  (2026-11-02)

## Corpus Check
- 268 files · ~15,010,770 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: .jsonl 6, (none) 3, .xml 3)

## Summary
- 1589 nodes · 3074 edges · 75 communities (68 shown, 7 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 230 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5c62f62f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- client_docs.py
- test_irs_pubs.py
- test_jobs.py
- T2: Ingest eCFR Title 26
- MissingCredentials
- test_ecfr.py
- TaxCite — Phase B exit report
- report
- decompose.py
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
- ragas_eval.py
- taxcite
- Collaborative Working Mode
- json
- test_store.py
- Postgres
- run
- test_verify.py
- retrieval.py
- test_metrics.py
- pytest
- TaxCite — Phase C exit report
- caselaw.py
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- client
- citations.py
- Plain-Module Package Layout
- generate.py
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- conn
- usc_notes.py
- store_bench.py
- TaxCite — Phase D exit report
- ecfr.py
- test_documents.py
- taxcite_ingest_caselaw
- Answer
- index.py
- taxcite_ingest_citations
- TaxCite — Status
- f0_verify.py
- TaxCite: Phase E exit report
- f5_golden.py
- F4 verdict check
- F0 judge check
- taxcite_ingest_ecfr
- usc.py
- authorities
- cli.py
- TaxCite: Phase F exit report
- verify.py
- strip_boilerplate
- retrieve.py
- citations
- fetch
- edition_filter
- Hosted
- f4_hide.py
- estimate_tokens
- fetch
- rerank
- embed_bench.py
- G3 step 4: client facts from an uploaded document (dev, tracked not gated)
- tracing.py

## God Nodes (most connected - your core abstractions)
1. `F0 judge check` - 41 edges
2. `F5 reference check` - 41 edges
3. `conn()` - 35 edges
4. `F4 verdict check` - 31 edges
5. `search()` - 30 edges
6. `Answer` - 25 edges
7. `Chunk` - 24 edges
8. `call_model()` - 20 edges
9. `run()` - 20 edges
10. `verify()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `Open problems handed on` --references--> `flags()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/ingest/citations.py
- `E2 and E3: the metadata, and the check that found law the parser didn't know` --references--> `save()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/store.py
- `G3 step 4: five dev rows with the client's facts in a document (draft, for your review)` --references--> `answer()`  [INFERRED]
  eval/results/g3-dev-rows-draft.md → src/taxcite/decompose.py
- `What exists` --references--> `authority()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/chunk.py
- `3. Process-wide caches` --references--> `decompose()`  [INFERRED]
  eval/results/g0-threat-model.md → src/taxcite/decompose.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]

## Communities (75 total, 7 thin omitted)

### Community 0 - "client_docs.py"
Cohesion: 0.10
Nodes (26): io, shutil, create_collection(), create_tables(), documents(), ingest(), kind(), ocr() (+18 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.10
Nodes (18): skipif, Sliding windows with overlap; a short page yields a single window., title_of(), windows(), Publication chunking: pure functions tested on text, no PDF needed., A discontinued publication redirects to HTML and still returns HTTP 200., Pub 17 prints its title before the number, unlike Pub 587., Pub 946 has no edition line; the bullet list ends the title. (+10 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.07
Nodes (35): opentelemetry_sdk_trace, opentelemetry_sdk_trace_export, opentelemetry_sdk_trace_export_in_memory_span_exporter, SpanExporter, BrokenExporter, clean(), fixture, Job record and SSE transport (ADR-9), with the pipeline stubbed. (+27 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.16
Nodes (15): eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark, Harvard Caselaw Access Project, Per-Document-Type Chunker (§3.2), CourtListener (+7 more)

### Community 4 - "MissingCredentials"
Cohesion: 0.67
Nodes (3): MissingCredentials, RuntimeError, Raised instead of the SDK's generic auth error, which does not say what to set.

### Community 5 - "test_ecfr.py"
Cohesion: 0.06
Nodes (45): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+37 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "report"
Cohesion: 0.12
Nodes (15): abstention(), claim_unit(), Overlapping word windows covering the whole chunk: the last one starts at or…, The threshold that maximises not-supported F1 on the tune half. Ties go to the…, The small model decides only what it's sure of, the LLM the rest. Auto-accept…, Sentences no pair of this unit covers: every uncited one for sentences, only…, What ADR-15 would hide over answers that weren't refusals, for one claim unit.…, Each F0 unit (cited chunks only) against today's faithfulness (LLM-extracted… (+7 more)

### Community 8 - "decompose.py"
Cohesion: 0.07
Nodes (43): G3 step 4: five dev rows with the client's facts in a document (draft, for your review), Reproducing, answer(), chunks(), citation_graph(), client_hits(), decompose(), Decomposition (+35 more)

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
Nodes (52): Hit, gi11(), hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, C5: A cites B and C; C cites D; E cites D; Z is unheld. Hops go either… (+44 more)

### Community 19 - "test_index.py"
Cohesion: 0.22
Nodes (17): chunks(), ctx(), models_(), fixture, CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., sync(), test_a_broken_qdrant_still_raises() (+9 more)

### Community 20 - "ragas_eval.py"
Cohesion: 0.09
Nodes (36): Budget, CostCap, extract_claims(), judge_claims(), Judged, main(), parse_json(), pipeline_answer() (+28 more)

### Community 23 - "json"
Cohesion: 0.12
Nodes (21): argparse, datetime, dotenv, E4: apply the dev rules as written in tasks/todo.md, before looking at which…, main(), G3 step 4: do a client's facts get from an uploaded document into the answer?…, run(), cost_of() (+13 more)

### Community 24 - "test_store.py"
Cohesion: 0.08
Nodes (31): chunks(), parametrize, Transaction time (D6): an amendment rewrites a chunk in place; the old text…, test_a_dropped_paragraph_is_retired_by_the_sweep(), test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(), test_authority_profile_comes_from_source_and_citation_form(), test_excluded_rows_are_stored_but_not_counted_as_indexable(), test_expiry_reads_a_regulations_own_clause_against_the_snapshot_date() (+23 more)

### Community 26 - "run"
Cohesion: 0.31
Nodes (9): Redis, client(), notify(), publish(), traced, Best-effort live notification. Redis is the delivery channel, never the record,…, The pipeline, reporting each stage. Phases C-F add their steps here. One run is…, Append a stage to the record, then notify listeners. Record first: a listener… (+1 more)

### Community 27 - "test_verify.py"
Cohesion: 0.10
Nodes (16): no_recite(), fixture, Claim verification (F4), tested without spending money: the verifier call is…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, A verifier stub that answers by prompt: SYSTEM gets the next of…, Re-cite (F5b C3) ships on; tests that don't stub its call turn it off, and the…, routed(), structured_answer() (+8 more)

### Community 28 - "retrieval.py"
Cohesion: 0.10
Nodes (27): inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the…, Part 2: which authority fields have more than one value here, and from where. (+19 more)

### Community 29 - "test_metrics.py"
Cohesion: 0.09
Nodes (30): aggregate(), Refusals are excluded from the mean and reported separately (§9.2). Averaging a…, mrr(), ndcg_at_k(), judged(), parametrize, The metrics must be right before any number computed with them means anything., An answer the extractor found nothing in would otherwise score 0/0. (+22 more)

### Community 30 - "pytest"
Cohesion: 0.18
Nodes (11): kappa(), Cohen's kappa for two raters over the same items., pytest, parametrize, The temporal gate's scoring rules (D2), on fixture values: no API calls., E5: one answer per plan set; rates per sample, misweighted tags counted on…, test_as_of_match(), test_eval_switches_leave_the_gate_as_shipped_unless_asked() (+3 more)

### Community 31 - "TaxCite — Phase C exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+4 more)

### Community 32 - "caselaw.py"
Cohesion: 0.12
Nodes (29): collections, httpx, LTTextBox, pdfminer_high_level, pdfminer_layout, re, Chunk, The unit every ingester produces and every store consumes. (+21 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "client"
Cohesion: 0.23
Nodes (11): 2. Store reads and writes, create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), delete_document(), client() (+3 more)

### Community 35 - "citations.py"
Cohesion: 0.06
Nodes (61): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze() (+53 more)

### Community 37 - "generate.py"
Cohesion: 0.15
Nodes (23): answer_from_groups(), answer_from_hits(), answer_schema(), authority_label(), effective_note(), format_sources(), _generate(), _generate_structured() (+15 more)

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "search"
Cohesion: 0.22
Nodes (14): Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, search(), RRF ties used to break differently per process, moving a chunk across the k…, No final 280A regulations exist, so the home-office rules live only in Pub 587., test_dense_finds_the_hobby_loss_factor(), test_hybrid_returns_k_hits_with_payload(), test_modes_can_disagree(), test_publications_answer_what_regulations_cannot() (+6 more)

### Community 40 - "conn"
Cohesion: 0.07
Nodes (38): asyncio, BackgroundTasks, BaseModel, contextlib, fastapi, fastapi_responses, get, post (+30 more)

### Community 41 - "usc_notes.py"
Cohesion: 0.06
Nodes (43): amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes(), own_designation() (+35 more)

### Community 42 - "store_bench.py"
Cohesion: 0.17
Nodes (15): recall_at_k(), load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run… (+7 more)

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "ecfr.py"
Cohesion: 0.17
Nodes (23): expiry(), whole' or 'partly' when a regulation's own clause says its applicability ended…, §7805(e)(2): a temporary regulation issued after Nov. 20, 1988 expires within 3…, sunset(), Block, blocks(), walk(), chunk_section() (+15 more)

### Community 45 - "test_documents.py"
Cohesion: 0.07
Nodes (48): fastapi_testclient, needs_tesseract, taxcite_ingest, ask(), clean(), pdf(), png(), fixture (+40 more)

### Community 47 - "Answer"
Cohesion: 0.12
Nodes (16): Answer, Says INSUFFICIENT EVIDENCE and cites nothing. F3: a cited answer that flags one…, (label, text) per "Part N: ..." section (F3), the unit ADR-15 hides. No…, Answer a question with retrieval (`rag`) or without it (`closed_book`)., split_sections(), premises(), prompt(), RuntimeError (+8 more)

### Community 48 - "index.py"
Cohesion: 0.15
Nodes (21): psycopg_types_json, QdrantClient, authority(), The chunk's authority profile (E2): from its source and the citation's form,…, backfill_authority(), batched(), count(), create_collection() (+13 more)

### Community 50 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 51 - "f0_verify.py"
Cohesion: 0.12
Nodes (24): concurrent_futures, agreement(), build(), check_sheet(), claim_text(), contains(), judge(), call() (+16 more)

### Community 52 - "TaxCite: Phase E exit report"
Cohesion: 0.11
Nodes (17): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E2 and E3: the metadata, and the check that found law the parser didn't know, E4: the rerank, E5: authority in answers, Failures, with examples, Open problems handed on (+9 more)

### Community 53 - "f5_golden.py"
Cohesion: 0.13
Nodes (27): f1(), headings(), Each cached chunk's heading, which synthesis saw ("[citation] (heading)") but…, On the not-supported class: what the verifier exists to catch. `supported` is…, audit(), check(), checkpoint(), save() (+19 more)

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "usc.py"
Cohesion: 0.27
Nodes (16): blocks(), child_text(), chunk_section(), clean(), designation(), lead_in(), parse(), provision_blocks() (+8 more)

### Community 58 - "authorities"
Cohesion: 0.18
Nodes (11): 1. Endpoints today, 4. Where text enters a prompt, 5. Where text reaches the user, 6. What is stored that may hold PII, 7. Threat table (golden adversarial rows), 8. Open from G0, G0: threat model and inventory, authorities() (+3 more)

### Community 59 - "cli.py"
Cohesion: 0.14
Nodes (35): Connection, hashlib, Namespace, secrets, backfill_authority(), create_tenant(), ingest_case(), ingest_ecfr() (+27 more)

### Community 60 - "TaxCite: Phase F exit report"
Cohesion: 0.25
Nodes (7): Golden, scored once on the shipped pipeline, How the phase went, Open, for later phases, Reproducing, TaxCite: Phase F exit report, The gates, What Phase F got wrong

### Community 61 - "verify.py"
Cohesion: 0.09
Nodes (31): dataclasses, Finding 2: a conclusion can state law on a client document's authority (D56), What exists, os, cited_items(), The sentences a structured answer can show, in order: text and at least one…, (answer text, sentences dropped) from arm E's JSON. Each sentence ends with its…, F2: every part judged insufficient before synthesis. A refusal with what each… (+23 more)

### Community 62 - "strip_boilerplate"
Cohesion: 0.19
Nodes (15): _normalise(), Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count(), edges(), page(), A page shaped like a real one: header lines, body, footer. (+7 more)

### Community 63 - "retrieve.py"
Cohesion: 0.19
Nodes (13): collections_abc, 3. Process-wide caches, functools, SparseVector, embed(), _models(), Search the indexed corpus. Modes, because the eval ablation ladder (§9) needs…, Loaded once per process and per model: ~4s, which every query would otherwise… (+5 more)

### Community 64 - "citations"
Cohesion: 0.19
Nodes (13): material(), Completeness over material sentences, and the share of answers that would…, Split outside brackets, at . ! ? followed by a space, never after an…, A line that states no claim: a section heading, a markdown title, a label…, sentences(), structural(), abstention(), completeness() (+5 more)

### Community 65 - "fetch"
Cohesion: 0.28
Nodes (9): fetch(), get(), load_selection(), Client, Path, The newest `per_topic` distinct opinions for each topic. A consolidated case is…, The selection is cached so the corpus stays fixed while new opinions are filed., One opinion's PDF, cached. DAWSON hands out a short-lived signed S3 link. (+1 more)

### Community 66 - "edition_filter"
Cohesion: 0.25
Nodes (8): Filter, edition_filter(), One source or several; several is how B7 routes a sub-query to the corpora that…, Keep chunks with no edition (everything but publications, and undated…, source_filter(), D3's filter, against Qdrant's own semantics (in-memory), not a re-…, test_edition_filter_keeps_undated_chunks_and_nearby_editions(), kept()

### Community 67 - "Hosted"
Cohesion: 0.32
Nodes (3): Hosted, A hosted embedding API in fastembed's shape (`embed` for chunks, `query_embed`…, ndarray

### Community 68 - "f4_hide.py"
Cohesion: 0.29
Nodes (10): base(), check_sheet(), main(), metrics(), Path, F4: one verified run, shown three ways, so the hiding unit is decided on…, The cached answer as the verifier saw it: every cited item shown., The cache entry as `unit` would show it. (+2 more)

### Community 69 - "estimate_tokens"
Cohesion: 0.40
Nodes (6): estimate_tokens(), `source_revision` where the ingester had none (E2): what `as_of` already…, revision(), make(), make(), make()

### Community 70 - "fetch"
Cohesion: 0.40
Nodes (5): fetch(), fetch_usc(), Path, Title 26 USLM XML for a release point (default: the current one), cached on…, Download one part (or a single section) of Title 26, cached on disk. The API…

### Community 71 - "rerank"
Cohesion: 0.40
Nodes (5): Re-score candidates with a cross-encoder, which reads query and chunk together.…, rerank(), hit(), The cross-encoder's job: an example that quotes a rule is not the rule., test_rerank_promotes_the_rule_over_a_chunk_that_only_mentions_it()

### Community 73 - "embed_bench.py"
Cohesion: 0.25
Nodes (9): build(), collection_for(), main(), _models(), ADR-18 revisited: hosted embedding models against bge-base, on the golden set.…, retrieve.search loads its dense model by name; hosted names resolve here…, Index every chunk with one hosted model, skipping sources already complete (a…, score_one() (+1 more)

### Community 76 - "G3 step 4: client facts from an uploaded document (dev, tracked not gated)"
Cohesion: 0.50
Nodes (3): Finding 1: taking facts out of the question changes public retrieval (D55), G3 step 4: client facts from an uploaded document (dev, tracked not gated), What this does not measure

### Community 80 - "tracing.py"
Cohesion: 0.11
Nodes (20): base64, inspect, opentelemetry, lifespan(), annotate(), _brief(), generation(), _json() (+12 more)

## Knowledge Gaps
- **209 isolated node(s):** `Finding 1: taking facts out of the question changes public retrieval (D55)`, `What this does not measure`, `§9.3 recalibration`, `E0: where authority costs, before building`, `E1: the rows that decide it` (+204 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 733 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `caselaw.py` to `test_ecfr.py`, `usc_notes.py`, `ecfr.py`, `index.py`, `TaxCite — Status`, `usc.py`, `cli.py`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `search()` (e.g. with `2. Store reads and writes` and `7. Threat table (golden adversarial rows)`) actually correct?**
  _`search()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Finding 1: taking facts out of the question changes public retrieval (D55)`, `What this does not measure`, `§9.3 recalibration` to the rest of the system?**
  _209 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `client_docs.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10317460317460317 - nodes in this community are weakly interconnected._