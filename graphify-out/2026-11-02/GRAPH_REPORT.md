# Graph Report - TaxCite.nosync  (2026-11-02)

## Corpus Check
- 279 files · ~15,085,028 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: .jsonl 6, (none) 3, .xml 3)

## Summary
- 1603 nodes · 3093 edges · 89 communities (77 shown, 12 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 248 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c415ed7c`
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
- decompose.py
- store.py
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
- retrieval.py
- test_usc.py
- Postgres
- jobs.py
- test_verify.py
- e0_authority.py
- test_metrics.py
- report
- embed_bench.py
- caselaw.py
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- pytest
- citations.py
- Plain-Module Package Layout
- generate.py
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- conn
- Chunk
- citations
- TaxCite — Phase D exit report
- ecfr.py
- test_documents.py
- taxcite_ingest_caselaw
- verify.py
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
- G3 step 4: client facts from an uploaded document (dev, tracked not gated)
- retrieve.py
- tracing.py
- irs_pubs.py
- store_bench.py
- f4_hide.py
- Hosted
- run
- test_store.py
- Checkpoint 2 demo: one question per tenant (G3)
- main
- audit
- history
- test_usc_notes.py
- e3_sample.py
- build
- client
- appeal
- is_appeal
- strip_boilerplate
- chunk.py
- test_fetch_rejects_a_non_pdf
- taxcite_ingest_irs_pubs
- ruling
- dehyphenate
- Path
- parametrize
- fixture

## God Nodes (most connected - your core abstractions)
1. `F0 judge check` - 41 edges
2. `F5 reference check` - 41 edges
3. `conn()` - 35 edges
4. `search()` - 31 edges
5. `F4 verdict check` - 31 edges
6. `Answer` - 26 edges
7. `Chunk` - 24 edges
8. `run()` - 21 edges
9. `Hit` - 21 edges
10. `verify()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `Both fixed (your call, 2026-11-02)` --references--> `run()`  [INFERRED]
  eval/results/g3-demo.md → src/taxcite/jobs.py
- `E2 and E3: the metadata, and the check that found law the parser didn't know` --references--> `save()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/store.py
- `3. Process-wide caches` --references--> `decompose()`  [INFERRED]
  eval/results/g0-threat-model.md → src/taxcite/decompose.py
- `2. Store reads and writes` --references--> `retrieve()`  [INFERRED]
  eval/results/g0-threat-model.md → src/taxcite/decompose.py
- `5. Where text reaches the user` --references--> `answer()`  [INFERRED]
  eval/results/g0-threat-model.md → src/taxcite/decompose.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]

## Communities (89 total, 12 thin omitted)

### Community 0 - "client_docs.py"
Cohesion: 0.12
Nodes (23): shutil, create_tables(), delete(), documents(), ingest(), kind(), ocr(), page_texts() (+15 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.14
Nodes (16): skipif, Sliding windows with overlap; a short page yields a single window., windows(), page(), Publication chunking: pure functions tested on text, no PDF needed., A page shaped like a real one: header lines, body, footer., A table row like "Line 6 amount" must survive digit-normalised matching., Pub 17 prints its title before the number, unlike Pub 587. (+8 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.06
Nodes (36): opentelemetry, opentelemetry_sdk_trace, opentelemetry_sdk_trace_export, opentelemetry_sdk_trace_export_in_memory_span_exporter, SpanExporter, BrokenExporter, clean(), fixture (+28 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.16
Nodes (15): eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark, Harvard Caselaw Access Project, Per-Document-Type Chunker (§3.2), CourtListener (+7 more)

### Community 4 - "MissingCredentials"
Cohesion: 0.40
Nodes (5): MissingCredentials, RuntimeError, Raised instead of the SDK's generic auth error, which does not say what to set., Fail early and specifically. The SDK raises a generic TypeError at request…, _require_credentials()

### Community 5 - "test_ecfr.py"
Cohesion: 0.06
Nodes (45): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+37 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "decompose.py"
Cohesion: 0.05
Nodes (52): G3 step 4: five dev rows with the client's facts in a document (draft, for your review), §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, Reproducing (+44 more)

### Community 8 - "store.py"
Cohesion: 0.13
Nodes (21): Connection, hashlib, psycopg, psycopg_types_json, secrets, authority(), expiry(), The chunk's authority profile (E2): from its source and the citation's form,… (+13 more)

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
Nodes (53): parametrize, gi11(), hit(), plan(), Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, C5: A cites B and C; C cites D; E cites D; Z is unheld. Hops go either…, D3b: plain-English publications outrank the statute; a statute-only search puts… (+45 more)

### Community 19 - "test_index.py"
Cohesion: 0.22
Nodes (17): chunks(), ctx(), models_(), fixture, CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., sync(), test_a_broken_qdrant_still_raises() (+9 more)

### Community 20 - "ragas_eval.py"
Cohesion: 0.10
Nodes (29): judge(), Judge each pair against `field`'s chunks into `out`. The main pass reads every…, Budget, CostCap, extract_claims(), judge_claims(), Judged, main() (+21 more)

### Community 23 - "retrieval.py"
Cohesion: 0.18
Nodes (18): argparse, collections, datetime, dotenv, cost_of(), estimate(), judge(), main() (+10 more)

### Community 24 - "test_usc.py"
Cohesion: 0.07
Nodes (22): memo(), fixture, Case-law tests against two real Tax Court opinions (see tasks/todo.md B3): -…, E3 (Estate of Caan): DAWSON lists the correction's date; the opinion says when…, result(), tc(), test_a_corrected_reissue_keeps_the_opinions_own_filing_date(), test_selection_dedupes_by_citation_and_keeps_the_newest() (+14 more)

### Community 26 - "jobs.py"
Cohesion: 0.17
Nodes (14): 2. Store reads and writes, Redis, client(), create(), create_table(), Event, notify(), publish() (+6 more)

### Community 27 - "test_verify.py"
Cohesion: 0.10
Nodes (16): no_recite(), fixture, Claim verification (F4), tested without spending money: the verifier call is…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, A verifier stub that answers by prompt: SYSTEM gets the next of…, Re-cite (F5b C3) ships on; tests that don't stub its call turn it off, and the…, routed(), structured_answer() (+8 more)

### Community 28 - "e0_authority.py"
Cohesion: 0.12
Nodes (25): inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the…, Part 2: which authority fields have more than one value here, and from where. (+17 more)

### Community 29 - "test_metrics.py"
Cohesion: 0.08
Nodes (35): aggregate(), Refusals are excluded from the mean and reported separately (§9.2). Averaging a…, mrr(), ndcg_at_k(), recall_at_k(), math, judged(), parametrize (+27 more)

### Community 30 - "report"
Cohesion: 0.12
Nodes (15): abstention(), claim_unit(), f1(), On the not-supported class: what the verifier exists to catch. `supported` is…, The threshold that maximises not-supported F1 on the tune half. Ties go to the…, The small model decides only what it's sure of, the LLM the rest. Auto-accept…, Sentences no pair of this unit covers: every uncited one for sentences, only…, What ADR-15 would hide over answers that weren't refusals, for one claim unit.… (+7 more)

### Community 31 - "embed_bench.py"
Cohesion: 0.17
Nodes (14): build(), collection_for(), main(), _models(), ADR-18 revisited: hosted embedding models against bge-base, on the golden set.…, retrieve.search loads its dense model by name; hosted names resolve here…, Index every chunk with one hosted model, skipping sources already complete (a…, score_one() (+6 more)

### Community 32 - "caselaw.py"
Cohesion: 0.16
Nodes (19): LTTextBox, fetch(), fold_numbers(), font_size(), get(), load_selection(), pages_label(), paragraphs() (+11 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "pytest"
Cohesion: 0.12
Nodes (16): as_of_match(), kappa(), passed(), Year-level match of the plan's as-of against the row's tax year. None = not…, Cohen's kappa for two raters over the same items., Per sample index: rates over the rows, first judge repeat (E5). Conflict and…, sample_summary(), pytest (+8 more)

### Community 35 - "citations.py"
Cohesion: 0.16
Nodes (18): Open problems handed on, eyecite, eyecite_models, logging, cites(), flag(), flags(), load() (+10 more)

### Community 37 - "generate.py"
Cohesion: 0.12
Nodes (25): Answer, answer_from_groups(), answer_from_hits(), answer_schema(), authority_label(), cost(), effective_note(), format_sources() (+17 more)

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "search"
Cohesion: 0.11
Nodes (25): Filter, edition_filter(), Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, One source or several; several is how B7 routes a sub-query to the corpora that…, Keep chunks with no edition (everything but publications, and undated…, search(), source_filter(), hit() (+17 more)

### Community 40 - "conn"
Cohesion: 0.09
Nodes (36): asyncio, BackgroundTasks, BaseModel, contextlib, fastapi, fastapi_responses, get, post (+28 more)

### Community 41 - "Chunk"
Cohesion: 0.14
Nodes (25): Chunk, amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes() (+17 more)

### Community 42 - "citations"
Cohesion: 0.33
Nodes (7): material(), Completeness over material sentences, and the share of answers that would…, abstention(), One answer to an insufficiency row, as one of: "refused", "flagged" (cited…, refused(), citations(), Every bracketed citation, once each, in order: nested brackets flattened, "[A;…

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "ecfr.py"
Cohesion: 0.16
Nodes (26): estimate_tokens(), Make `part` a running count per citation, so `key` is unique by construction.…, §7805(e)(2): a temporary regulation issued after Nov. 20, 1988 expires within 3…, renumber(), sunset(), make(), Block, blocks() (+18 more)

### Community 45 - "test_documents.py"
Cohesion: 0.06
Nodes (52): fastapi_testclient, fixture, needs_tesseract, taxcite_ingest, ask(), clean(), pdf(), png() (+44 more)

### Community 47 - "verify.py"
Cohesion: 0.11
Nodes (32): Finding 2: a conclusion can state law on a client document's authority (D56), What exists, call_model(), A source's text as every prompt shows it. A client document is the questioner's…, The section a citation belongs to, ignoring paragraph depth. '26 CFR…, One completion. Returns (text, input_tokens, output_tokens). The two providers…, section_of(), source_text() (+24 more)

### Community 48 - "index.py"
Cohesion: 0.14
Nodes (21): qdrant_client, QdrantClient, backfill_authority(), batched(), count(), create_collection(), edition(), point_id() (+13 more)

### Community 50 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 51 - "f0_verify.py"
Cohesion: 0.16
Nodes (16): concurrent_futures, agreement(), check_sheet(), contains(), call(), main(), nli(), pages() (+8 more)

### Community 52 - "TaxCite: Phase E exit report"
Cohesion: 0.17
Nodes (11): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E2 and E3: the metadata, and the check that found law the parser didn't know, E4: the rerank, E5: authority in answers, Failures, with examples, Reproducing (+3 more)

### Community 53 - "f5_golden.py"
Cohesion: 0.20
Nodes (16): A line that states no claim: a section heading, a markdown title, a label…, structural(), check(), completeness(), ladder(), latency(), load(), main() (+8 more)

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
Cohesion: 0.22
Nodes (9): 1. Endpoints today, 4. Where text enters a prompt, 5. Where text reaches the user, 6. What is stored that may hold PII, 7. Threat table (golden adversarial rows), 8. Open from G0, G0: threat model and inventory, authorities() (+1 more)

### Community 59 - "cli.py"
Cohesion: 0.17
Nodes (26): io, Namespace, backfill_authority(), create_tenant(), fetch(), fetch_usc(), ingest_case(), ingest_ecfr() (+18 more)

### Community 60 - "TaxCite: Phase F exit report"
Cohesion: 0.25
Nodes (7): Golden, scored once on the shipped pipeline, How the phase went, Open, for later phases, Reproducing, TaxCite: Phase F exit report, The gates, What Phase F got wrong

### Community 61 - "G3 step 4: client facts from an uploaded document (dev, tracked not gated)"
Cohesion: 0.50
Nodes (3): Finding 1: taking facts out of the question changes public retrieval (D55), G3 step 4: client facts from an uploaded document (dev, tracked not gated), What this does not measure

### Community 62 - "retrieve.py"
Cohesion: 0.17
Nodes (15): collections_abc, dataclasses, 3. Process-wide caches, SparseVector, embed(), _models(), Search the indexed corpus. Modes, because the eval ablation ladder (§9) needs…, Loaded once per process and per model: ~4s, which every query would otherwise… (+7 more)

### Community 63 - "tracing.py"
Cohesion: 0.12
Nodes (17): base64, functools, inspect, os, lifespan(), annotate(), _brief(), generation() (+9 more)

### Community 64 - "irs_pubs.py"
Cohesion: 0.17
Nodes (15): pdfminer_high_level, pdfminer_layout, edition_year(), fetch(), page_texts(), parse(), Path, Ingest IRS publications (PDF). Publications have no paragraph numbering to cut… (+7 more)

### Community 65 - "store_bench.py"
Cohesion: 0.12
Nodes (18): E4: apply the dev rules as written in tasks/todo.md, before looking at which…, main(), G3 step 4: do a client's facts get from an uploaded document into the answer?…, run(), load(), main(), pg_filtered(), pg_hybrid() (+10 more)

### Community 66 - "f4_hide.py"
Cohesion: 0.29
Nodes (10): base(), check_sheet(), main(), metrics(), Path, F4: one verified run, shown three ways, so the hiding unit is decided on…, The cached answer as the verifier saw it: every cited item shown., The cache entry as `unit` would show it. (+2 more)

### Community 67 - "Hosted"
Cohesion: 0.32
Nodes (3): Hosted, A hosted embedding API in fastembed's shape (`embed` for chunks, `query_embed`…, ndarray

### Community 68 - "run"
Cohesion: 0.14
Nodes (15): cited_items(), The sentences a structured answer can show, in order: text and at least one…, (answer text, sentences dropped) from arm E's JSON. Each sentence ends with its…, F2: every part judged insufficient before synthesis. A refusal with what each…, render(), skipped_only(), traced, The pipeline, reporting each stage. Phases C-F add their steps here. One run is… (+7 more)

### Community 69 - "test_store.py"
Cohesion: 0.21
Nodes (15): chunks(), parametrize, Transaction time (D6): an amendment rewrites a chunk in place; the old text…, test_a_dropped_paragraph_is_retired_by_the_sweep(), test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(), test_authority_profile_comes_from_source_and_citation_form(), test_excluded_rows_are_stored_but_not_counted_as_indexable(), test_reingest_is_idempotent() (+7 more)

### Community 70 - "Checkpoint 2 demo: one question per tenant (G3)"
Cohesion: 0.25
Nodes (7): Both fixed (your call, 2026-11-02), Checkpoint 2 demo: one question per tenant (G3), Finding 1: A's question never retrieved § 183 (shipped retrieval, not documents), Finding 2: a question about a document the tenant doesn't have gets a legal answer, not "no such document", For your review, Tenant A: own documents, compound question, Tenant B: asks about A's client by name

### Community 71 - "main"
Cohesion: 0.25
Nodes (3): main(), needs_case_law(), A row whose gold includes an opinion: routing must send a sub-query to the case…

### Community 72 - "audit"
Cohesion: 0.22
Nodes (13): headings(), Each cached chunk's heading, which synthesis saw ("[citation] (heading)") but…, audit(), checkpoint(), save(), judge(), (done, save, path): results already paid for in a crashed run, and a function…, verify.verify's call, on given items and with another model; low effort, since… (+5 more)

### Community 73 - "history"
Cohesion: 0.19
Nodes (13): FullCaseCitation, full_cites(), history(), label(), The year in the parenthetical right after the cite. eyecite's own guess can…, Explanatory parentheticals push "aff'd" past the window: "113 T.C. 254 (1999)…, The appeal as one stable string, "560 F.3d 620 (ca7 2009)": no case name or pin…, (opinion, kind, by) from subsequent history in a passage. by is the appellate… (+5 more)

### Community 74 - "test_usc_notes.py"
Cohesion: 0.26
Nodes (11): chunks(), effective(), fixture, Effective dates from the statutory notes (D4), on six real sections in…, test_a_new_section_dated_by_its_own_effective_date_note(), test_a_range_chunk_holds_its_subsections_whole(), test_amendment_below_the_label_found_after_a_heading(), test_an_exclusion_is_not_the_rule() (+3 more)

### Community 75 - "e3_sample.py"
Cohesion: 0.33
Nodes (9): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze() (+1 more)

### Community 76 - "build"
Cohesion: 0.22
Nodes (9): build(), claim_text(), kind_of(), The sub-query kind a citation belongs to: what F3's sections would be. Two sub-…, Tune half / report half, by question, so near-identical answers of one question…, Split outside brackets, at . ! ? followed by a space, never after an…, The sentence without its brackets or markdown, as the claim extractor would…, sentences() (+1 more)

### Community 77 - "client"
Cohesion: 0.33
Nodes (8): create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), httpx, client(), subprocess

### Community 78 - "appeal"
Cohesion: 0.25
Nodes (9): appeal(), appeal_label(), cached(), get(), Client, Path, One format for both sources, so a reader sees the same appeal the same way., A response cached with the time it was fetched: re-running from cache must not… (+1 more)

### Community 79 - "is_appeal"
Cohesion: 0.32
Nodes (8): is_appeal(), party(), petitioners(), The petitioners' names alone: "Estate of James E. Caan, Deceased, …,…, Family names in a joint caption. "C. Michael & Gwendolyn E. Willock" is one…, A caseName query for the appellate caption: surnames for people ("Donald B. &…, Same-name appeals are common (C1: three unrelated Michaels for Willock). A real…, surnames()

### Community 80 - "strip_boilerplate"
Cohesion: 0.36
Nodes (8): _normalise(), Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count(), edges(), Edges must never cover the whole page, or a 5-line page is deleted entirely., test_short_pages_never_lose_everything()

### Community 81 - "chunk.py"
Cohesion: 0.29
Nodes (6): re, The unit every ingester produces and every store consumes., `source_revision` where the ingester had none (E2): what `as_of` already…, revision(), make(), test_revision_fills_from_as_of_where_the_ingester_had_none()

### Community 84 - "ruling"
Cohesion: 0.40
Nodes (5): kind(), A mixed disposition takes its most serious part: "aff'd in part, rev'd in part"…, The outcome in an appellate opinion's last disposition sentence, or None (e.g.…, ruling(), split()

### Community 85 - "dehyphenate"
Cohesion: 0.50
Nodes (4): dehyphenate(), Join words split across a line break ("mo-\ntel" or "mo- tel" -> "motel"). A…, test_dehyphenate_joins_line_wrapped_words(), test_dehyphenate_keeps_real_hyphens()

## Knowledge Gaps
- **214 isolated node(s):** `Tenant A: own documents, compound question`, `Tenant B: asks about A's client by name`, `Finding 1: A's question never retrieved § 183 (shipped retrieval, not documents)`, `Finding 2: a question about a document the tenant doesn't have gets a legal answer, not "no such document"`, `For your review` (+209 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 747 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `caselaw.py`, `irs_pubs.py`, `test_ecfr.py`, `store.py`, `ecfr.py`, `index.py`, `chunk.py`, `TaxCite — Status`, `usc.py`?**
  _High betweenness centrality (0.155) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `search()` (e.g. with `2. Store reads and writes` and `7. Threat table (golden adversarial rows)`) actually correct?**
  _`search()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Tenant A: own documents, compound question`, `Tenant B: asks about A's client by name`, `Finding 1: A's question never retrieved § 183 (shipped retrieval, not documents)` to the rest of the system?**
  _214 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `client_docs.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._