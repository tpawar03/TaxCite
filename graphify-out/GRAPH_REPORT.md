# Graph Report - TaxCite.nosync  (2026-11-07)

## Corpus Check
- 283 files · ~15,090,639 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 17 file(s) not represented in the graph (top: .jsonl 9, (none) 3, .xml 3)

## Summary
- 1644 nodes · 3216 edges · 84 communities (70 shown, 14 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 253 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6f4c8203`
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
- run
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
- test_store.py
- ragas_eval.py
- taxcite
- Collaborative Working Mode
- is_appeal
- test_usc.py
- Postgres
- jobs.py
- test_verify.py
- score_one
- test_metrics.py
- test_caselaw.py
- TaxCite — Phase C exit report
- json
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- report
- pytest
- Plain-Module Package Layout
- generate.py
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- api.py
- ecfr.py
- audit
- TaxCite — Phase D exit report
- app.js
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
- f4_hide.py
- authorities
- cli.py
- TaxCite: Phase F exit report
- G3 step 4: client facts from an uploaded document (dev, tracked not gated)
- decompose.py
- tracing.py
- e0_authority.py
- pathlib
- conn
- Hosted
- build
- SubQuery
- Checkpoint 2 demo: one question per tenant (G3)
- citations
- weigh
- citations.py
- chunks
- e3_sample.py
- g4-corpus-draft.md
- os
- taxcite
- taxcite_ingest
- taxcite_ingest_irs_pubs
- taxcite_tracing
- test_fetch_rejects_a_non_pdf
- caselaw.py

## God Nodes (most connected - your core abstractions)
1. `F0 judge check` - 41 edges
2. `F5 reference check` - 41 edges
3. `Hit` - 39 edges
4. `conn()` - 37 edges
5. `search()` - 35 edges
6. `F4 verdict check` - 31 edges
7. `Answer` - 27 edges
8. `Chunk` - 24 edges
9. `run()` - 21 edges
10. `call_model()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `Open problems handed on` --references--> `flags()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/ingest/citations.py
- `Both fixed (your call, 2026-11-02)` --references--> `run()`  [INFERRED]
  eval/results/g3-demo.md → src/taxcite/jobs.py
- `E2 and E3: the metadata, and the check that found law the parser didn't know` --references--> `save()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/store.py
- `What exists` --references--> `authority()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/chunk.py
- `3. Process-wide caches` --references--> `decompose()`  [INFERRED]
  eval/results/g0-threat-model.md → src/taxcite/decompose.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]

## Communities (84 total, 14 thin omitted)

### Community 0 - "client_docs.py"
Cohesion: 0.12
Nodes (24): 2. Store reads and writes, create_collection(), create_tables(), delete(), documents(), ingest(), kind(), ocr() (+16 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.08
Nodes (36): skipif, edition_year(), fetch(), _normalise(), page_texts(), parse(), Path, Sliding windows with overlap; a short page yields a single window. (+28 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.06
Nodes (37): opentelemetry_sdk_trace, opentelemetry_sdk_trace_export, opentelemetry_sdk_trace_export_in_memory_span_exporter, SpanExporter, BrokenExporter, clean(), fixture, Job record and SSE transport (ADR-9), with the pipeline stubbed. (+29 more)

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

### Community 7 - "run"
Cohesion: 0.13
Nodes (22): G3 step 4: five dev rows with the client's facts in a document (draft, for your review), Reproducing, answer(), chunks(), client_hits(), decompose(), Decomposition, gate() (+14 more)

### Community 8 - "store.py"
Cohesion: 0.13
Nodes (23): Connection, hashlib, psycopg, secrets, authority(), expiry(), The chunk's authority profile (E2): from its source and the citation's form,…, `source_revision` where the ingester had none (E2): what `as_of` already… (+15 more)

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
Nodes (53): gi11(), hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, C5: A cites B and C; C cites D; E cites D; Z is unheld. Hops go either…, D3b: plain-English publications outrank the statute; a statute-only search puts… (+45 more)

### Community 19 - "test_store.py"
Cohesion: 0.10
Nodes (34): chunks(), ctx(), models_(), fixture, CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., sync(), test_a_broken_qdrant_still_raises() (+26 more)

### Community 20 - "ragas_eval.py"
Cohesion: 0.07
Nodes (43): Budget, CostCap, extract_claims(), judge_claims(), Judged, main(), parse_json(), pipeline_answer() (+35 more)

### Community 23 - "is_appeal"
Cohesion: 0.32
Nodes (8): is_appeal(), party(), petitioners(), The petitioners' names alone: "Estate of James E. Caan, Deceased, …,…, Family names in a joint caption. "C. Michael & Gwendolyn E. Willock" is one…, A caseName query for the appellate caption: surnames for people ("Donald B. &…, Same-name appeals are common (C1: three unrelated Michaels for Willock). A real…, surnames()

### Community 24 - "test_usc.py"
Cohesion: 0.19
Nodes (12): of(), Statute chunker tests against eight real sections in…, test_en_dash_section_number_becomes_a_hyphen(), test_heading_folds_into_its_first_child(), test_neighbouring_subsections_pack_into_a_range(), test_notes_are_not_text_and_source_credit_is_the_history(), test_oversized_subsection_splits_at_level_two(), test_repealed_paragraph_stubs_are_dropped() (+4 more)

### Community 26 - "jobs.py"
Cohesion: 0.22
Nodes (11): Redis, client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across…, Best-effort live notification. Redis is the delivery channel, never the record,…, One server-sent event. The blank line is the record separator. (+3 more)

### Community 27 - "test_verify.py"
Cohesion: 0.10
Nodes (16): no_recite(), fixture, Claim verification (F4), tested without spending money: the verifier call is…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, A verifier stub that answers by prompt: SYSTEM gets the next of…, Re-cite (F5b C3) ships on; tests that don't stub its call turn it off, and the…, routed(), structured_answer() (+8 more)

### Community 28 - "score_one"
Cohesion: 0.17
Nodes (8): cached_decompose(), main(), Path, Decompose once per plan set and reuse it, so a comparison measures the change…, score_one(), gate_only(), Path, F2's cheap pass: for each row and plan set, the parts the shipped pipeline…

### Community 29 - "test_metrics.py"
Cohesion: 0.07
Nodes (36): aggregate(), Refusals are excluded from the mean and reported separately (§9.2). Averaging a…, mrr(), ndcg_at_k(), math, The section a citation belongs to, ignoring paragraph depth. '26 CFR…, section_of(), judged() (+28 more)

### Community 30 - "test_caselaw.py"
Cohesion: 0.12
Nodes (8): memo(), fixture, Case-law tests against two real Tax Court opinions (see tasks/todo.md B3): -…, E3 (Estate of Caan): DAWSON lists the correction's date; the opinion says when…, result(), tc(), test_a_corrected_reissue_keeps_the_opinions_own_filing_date(), test_selection_dedupes_by_citation_and_keeps_the_newest()

### Community 31 - "TaxCite — Phase C exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+4 more)

### Community 32 - "json"
Cohesion: 0.09
Nodes (33): argparse, datetime, build(), collection_for(), main(), _models(), ADR-18 revisited: hosted embedding models against bge-base, on the golden set.…, retrieve.search loads its dense model by name; hosted names resolve here… (+25 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "report"
Cohesion: 0.12
Nodes (15): abstention(), claim_unit(), f1(), On the not-supported class: what the verifier exists to catch. `supported` is…, The threshold that maximises not-supported F1 on the tune half. Ties go to the…, The small model decides only what it's sure of, the LLM the rest. Auto-accept…, Sentences no pair of this unit covers: every uncited one for sentences, only…, What ADR-15 would hide over answers that weren't refusals, for one claim unit.… (+7 more)

### Community 35 - "pytest"
Cohesion: 0.16
Nodes (15): pytest, browser(), page(), handle(), fixture, G5, the render path (ADR-13): nothing from a source, a document or an answer…, ADR-13 by construction: none of the APIs that turn a string into markup appear…, The page with every route stubbed; records outbound requests, dialogs and… (+7 more)

### Community 37 - "generate.py"
Cohesion: 0.12
Nodes (28): Answer, answer_from_groups(), answer_from_hits(), answer_schema(), authority_label(), effective_note(), format_sources(), _generate() (+20 more)

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "search"
Cohesion: 0.09
Nodes (29): Filter, SparseVector, edition_filter(), embed(), Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, Cached: every search in one pipeline run uses the original question (only the…, One source or several; several is how B7 routes a sub-query to the corpora that…, Keep chunks with no edition (everything but publications, and undated… (+21 more)

### Community 40 - "api.py"
Cohesion: 0.07
Nodes (30): asyncio, BackgroundTasks, BaseModel, contextlib, fastapi, fastapi_responses, fastapi_staticfiles, post (+22 more)

### Community 41 - "ecfr.py"
Cohesion: 0.05
Nodes (82): Chunk, estimate_tokens(), Make `part` a running count per citation, so `key` is unique by construction.…, §7805(e)(2): a temporary regulation issued after Nov. 20, 1988 expires within 3…, renumber(), sunset(), pages_label(), parse() (+74 more)

### Community 42 - "audit"
Cohesion: 0.22
Nodes (13): headings(), Each cached chunk's heading, which synthesis saw ("[citation] (heading)") but…, audit(), checkpoint(), save(), judge(), (done, save, path): results already paid for in a crashed run, and a function…, verify.verify's call, on given items and with another model; low effort, since… (+5 more)

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "app.js"
Cohesion: 0.44
Nodes (10): ADR-0013, api(), ask(), detail(), el(), events(), listDocuments(), showAnswer() (+2 more)

### Community 45 - "test_documents.py"
Cohesion: 0.06
Nodes (57): fastapi_testclient, io, needs_tesseract, shutil, ask(), clean(), pdf(), png() (+49 more)

### Community 47 - "verify.py"
Cohesion: 0.10
Nodes (34): Finding 2: a conclusion can state law on a client document's authority (D56), What exists, call_model(), cited_items(), The sentences a structured answer can show, in order: text and at least one…, (answer text, sentences dropped) from arm E's JSON. Each sentence ends with its…, One completion. Returns (text, input_tokens, output_tokens). The two providers…, render() (+26 more)

### Community 48 - "index.py"
Cohesion: 0.18
Nodes (17): psycopg_types_json, QdrantClient, batched(), count(), create_collection(), edition(), point_id(), Embed chunks and keep a Qdrant collection in step with Postgres. Postgres is… (+9 more)

### Community 50 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 51 - "f0_verify.py"
Cohesion: 0.14
Nodes (19): collections, concurrent_futures, agreement(), check_sheet(), contains(), judge(), call(), main() (+11 more)

### Community 52 - "TaxCite: Phase E exit report"
Cohesion: 0.11
Nodes (17): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E2 and E3: the metadata, and the check that found law the parser didn't know, E4: the rerank, E5: authority in answers, Failures, with examples, Open problems handed on (+9 more)

### Community 53 - "f5_golden.py"
Cohesion: 0.20
Nodes (16): A line that states no claim: a section heading, a markdown title, a label…, structural(), check(), completeness(), ladder(), latency(), load(), main() (+8 more)

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "f4_hide.py"
Cohesion: 0.29
Nodes (10): base(), check_sheet(), main(), metrics(), Path, F4: one verified run, shown three ways, so the hiding unit is decided on…, The cached answer as the verifier saw it: every cited item shown., The cache entry as `unit` would show it. (+2 more)

### Community 58 - "authorities"
Cohesion: 0.22
Nodes (9): 1. Endpoints today, 4. Where text enters a prompt, 5. Where text reaches the user, 6. What is stored that may hold PII, 7. Threat table (golden adversarial rows), 8. Open from G0, G0: threat model and inventory, authorities() (+1 more)

### Community 59 - "cli.py"
Cohesion: 0.19
Nodes (27): Namespace, backfill_authority(), create_tenant(), fetch(), fetch_usc(), ingest_case(), ingest_ecfr(), ingest_pubs() (+19 more)

### Community 60 - "TaxCite: Phase F exit report"
Cohesion: 0.25
Nodes (7): Golden, scored once on the shipped pipeline, How the phase went, Open, for later phases, Reproducing, TaxCite: Phase F exit report, The gates, What Phase F got wrong

### Community 61 - "G3 step 4: client facts from an uploaded document (dev, tracked not gated)"
Cohesion: 0.50
Nodes (3): Finding 1: taking facts out of the question changes public retrieval (D55), G3 step 4: client facts from an uploaded document (dev, tracked not gated), What this does not measure

### Community 62 - "decompose.py"
Cohesion: 0.10
Nodes (25): collections_abc, dataclasses, 3. Process-wide caches, functools, qdrant_client, citation_graph(), neighbors(), Split a question into typed sub-queries, and route each to the sources that can… (+17 more)

### Community 63 - "tracing.py"
Cohesion: 0.14
Nodes (15): base64, inspect, opentelemetry, annotate(), _brief(), generation(), _json(), Tracing (G1b): OpenTelemetry spans, exported to Langfuse Cloud over OTLP. Off… (+7 more)

### Community 64 - "e0_authority.py"
Cohesion: 0.24
Nodes (13): inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the…, Part 2: which authority fields have more than one value here, and from where. (+5 more)

### Community 65 - "pathlib"
Cohesion: 0.10
Nodes (25): dotenv, E4: apply the dev rules as written in tasks/todo.md, before looking at which…, main(), G3 step 4: do a client's facts get from an uploaded document into the answer?…, run(), checks(), judge(), main() (+17 more)

### Community 66 - "conn"
Cohesion: 0.21
Nodes (13): get, get_documents(), get_query(), Server-sent events for one job. Replays whatever the record already holds, then…, Every route but /health belongs to a tenant, resolved from its API key (Phase…, stream_events(), events(), tenant() (+5 more)

### Community 67 - "Hosted"
Cohesion: 0.32
Nodes (3): Hosted, A hosted embedding API in fastembed's shape (`embed` for chunks, `query_embed`…, ndarray

### Community 68 - "build"
Cohesion: 0.22
Nodes (9): build(), claim_text(), kind_of(), The sub-query kind a citation belongs to: what F3's sections would be. Two sub-…, Tune half / report half, by question, so near-identical answers of one question…, Split outside brackets, at . ! ? followed by a space, never after an…, The sentence without its brackets or markdown, as the claim extractor would…, sentences() (+1 more)

### Community 69 - "SubQuery"
Cohesion: 0.25
Nodes (5): merge(), parse(), (sub-queries, as_of, fallback reason). Never raises. A decomposition that…, One ranked list of k, round-robin across sub-queries, first occurrence wins.…, SubQuery

### Community 70 - "Checkpoint 2 demo: one question per tenant (G3)"
Cohesion: 0.25
Nodes (7): Both fixed (your call, 2026-11-02), Checkpoint 2 demo: one question per tenant (G3), Finding 1: A's question never retrieved § 183 (shipped retrieval, not documents), Finding 2: a question about a document the tenant doesn't have gets a legal answer, not "no such document", For your review, Tenant A: own documents, compound question, Tenant B: asks about A's client by name

### Community 71 - "citations"
Cohesion: 0.33
Nodes (7): material(), Completeness over material sentences, and the share of answers that would…, abstention(), One answer to an insufficiency row, as one of: "refused", "flagged" (cited…, refused(), citations(), Every bracketed citation, once each, in order: nested brackets flattened, "[A;…

### Community 72 - "weigh"
Cohesion: 0.40
Nodes (6): level(), A hit's authority level (E2's profile; 0 when it has none), with E4's two…, E4's reorderings of the cross-encoder's list by authority. Nothing is dropped.…, weigh(), order(), rescore()

### Community 73 - "citations.py"
Cohesion: 0.08
Nodes (44): eyecite, eyecite_models, FullCaseCitation, logging, appeal(), appeal_label(), cached(), cites() (+36 more)

### Community 75 - "e3_sample.py"
Cohesion: 0.33
Nodes (9): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze() (+1 more)

### Community 77 - "os"
Cohesion: 0.36
Nodes (7): create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), os, subprocess

### Community 85 - "caselaw.py"
Cohesion: 0.11
Nodes (26): httpx, LTTextBox, pdfminer_high_level, pdfminer_layout, re, The unit every ingester produces and every store consumes., fetch(), fold_numbers() (+18 more)

## Knowledge Gaps
- **217 isolated node(s):** `taxcite`, `STAGES`, `ADR-0013`, `P01 `G-C20#0#0s``, `P02 `G-C05#1#0s`` (+212 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 757 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `ecfr.py` to `test_irs_pubs.py`, `test_ecfr.py`, `store.py`, `index.py`, `TaxCite — Status`, `caselaw.py`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `Hit` (e.g. with `base()` and `chunks()`) actually correct?**
  _`Hit` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `search()` (e.g. with `2. Store reads and writes` and `7. Threat table (golden adversarial rows)`) actually correct?**
  _`search()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `taxcite`, `STAGES`, `ADR-0013` to the rest of the system?**
  _217 weakly-connected nodes found - possible documentation gaps or missing edges._