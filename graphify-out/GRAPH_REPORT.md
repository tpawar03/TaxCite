# Graph Report - TaxCite.nosync  (2026-11-02)

## Corpus Check
- 281 files · ~15,088,194 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 17 file(s) not represented in the graph (top: .jsonl 9, (none) 3, .xml 3)

## Summary
- 1611 nodes · 3153 edges · 86 communities (73 shown, 13 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 248 edges (avg confidence: 0.89)
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
- test_index.py
- ragas_eval.py
- taxcite
- Collaborative Working Mode
- llm_bench.py
- test_usc.py
- Postgres
- jobs.py
- test_verify.py
- e0_authority.py
- test_metrics.py
- designations
- TaxCite — Phase C exit report
- fetch
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- pytest
- SubQuery
- Plain-Module Package Layout
- generate.py
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- api.py
- usc_notes.py
- title_of
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
- G0: threat model and inventory
- cli.py
- TaxCite: Phase F exit report
- G3 step 4: client facts from an uploaded document (dev, tracked not gated)
- decompose.py
- tracing.py
- parse
- citations.py
- f4_hide.py
- Hosted
- weigh
- test_store.py
- Checkpoint 2 demo: one question per tenant (G3)
- fetch
- post_document
- appeal
- in_scope
- sys
- g4-corpus-draft.md
- snapshot.py
- taxcite
- taxcite_ingest
- strip_boilerplate
- Chunk
- test_fetch_rejects_a_non_pdf
- taxcite_ingest_irs_pubs
- taxcite_tracing
- paragraphs

## God Nodes (most connected - your core abstractions)
1. `F0 judge check` - 41 edges
2. `F5 reference check` - 41 edges
3. `Hit` - 39 edges
4. `conn()` - 36 edges
5. `search()` - 34 edges
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

## Communities (86 total, 13 thin omitted)

### Community 0 - "client_docs.py"
Cohesion: 0.12
Nodes (23): io, shutil, create_tables(), delete(), ingest(), kind(), ocr(), page_texts() (+15 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.20
Nodes (12): Sliding windows with overlap; a short page yields a single window., windows(), page(), Publication chunking: pure functions tested on text, no PDF needed., A page shaped like a real one: header lines, body, footer., A table row like "Line 6 amount" must survive digit-normalised matching., test_short_page_is_one_window(), test_strip_boilerplate_drops_repeated_headers_and_footers() (+4 more)

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
Cohesion: 0.14
Nodes (16): of(), Chunker tests against nine real sections in tests/fixtures/ecfr_sample.xml.…, eCFR ships its own citation string in hierarchy_metadata; ours must agree., test_cita_is_kept_out_of_the_text(), test_example_text_in_pspace_is_captured(), test_large_table_is_recorded_with_a_reason(), test_letter_i_section_cites_through_j(), test_neighbouring_units_pack_into_a_range_citation() (+8 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "run"
Cohesion: 0.11
Nodes (27): 2. Store reads and writes, 5. Where text reaches the user, G3 step 4: five dev rows with the client's facts in a document (draft, for your review), Reproducing, What exists, answer(), chunks(), client_hits() (+19 more)

### Community 8 - "store.py"
Cohesion: 0.11
Nodes (27): Connection, hashlib, psycopg, psycopg_types_json, secrets, authority(), expiry(), The unit every ingester produces and every store consumes. (+19 more)

### Community 9 - "F5 reference check"
Cohesion: 0.05
Nodes (41): F5 reference check, R01 `G-C17#0#1`, R02 `G-S18#0#1`, R03 `G-X14#0#1`, R04 `G-C14#0#3`, R05 `G-X05#0#3`, R06 `G-S06#0#2`, R07 `G-S24#0#0` (+33 more)

### Community 10 - "test_generate.py"
Cohesion: 0.04
Nodes (27): E5's prompt arms, each built from the pre-E5 prompt: "pre-e5" is it unchanged…, set_prompt(), fixture, Answer generation, tested without spending money: the model call is stubbed., Sampling at the default temperature made the same question answerable two ways,…, E5: the label map covers every (type, status) chunk.authority() can return,…, E5: every E5 arm is built from the pre-E5 prompt, so "pre-e5" reproduces that…, Replace the model call; record what it was asked. (+19 more)

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
Nodes (54): prompt(), gi11(), hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, C5: A cites B and C; C cites D; E cites D; Z is unheld. Hops go either… (+46 more)

### Community 19 - "test_index.py"
Cohesion: 0.22
Nodes (17): chunks(), ctx(), models_(), fixture, CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., sync(), test_a_broken_qdrant_still_raises() (+9 more)

### Community 20 - "ragas_eval.py"
Cohesion: 0.09
Nodes (36): aggregate(), Budget, CostCap, extract_claims(), judge_claims(), Judged, main(), parse_json() (+28 more)

### Community 23 - "llm_bench.py"
Cohesion: 0.26
Nodes (10): dotenv, cost_of(), estimate(), judge(), main(), ADR-11: choose the LLM by measuring answers, not by price alone. uv run python…, Rough spend before committing: RAG prompts dominate the input tokens., Grade one answer. `alt` applies the same rubric in different words, which is… (+2 more)

### Community 24 - "test_usc.py"
Cohesion: 0.16
Nodes (14): chunks(), of(), fixture, Statute chunker tests against eight real sections in…, test_en_dash_section_number_becomes_a_hyphen(), test_heading_folds_into_its_first_child(), test_neighbouring_subsections_pack_into_a_range(), test_notes_are_not_text_and_source_credit_is_the_history() (+6 more)

### Community 26 - "jobs.py"
Cohesion: 0.24
Nodes (10): Redis, client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across…, Best-effort live notification. Redis is the delivery channel, never the record,…, One server-sent event. The blank line is the record separator. (+2 more)

### Community 27 - "test_verify.py"
Cohesion: 0.10
Nodes (16): no_recite(), fixture, Claim verification (F4), tested without spending money: the verifier call is…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, A verifier stub that answers by prompt: SYSTEM gets the next of…, Re-cite (F5b C3) ships on; tests that don't stub its call turn it off, and the…, routed(), structured_answer() (+8 more)

### Community 28 - "e0_authority.py"
Cohesion: 0.10
Nodes (25): inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the…, Part 2: which authority fields have more than one value here, and from where. (+17 more)

### Community 29 - "test_metrics.py"
Cohesion: 0.07
Nodes (42): build(), collection_for(), main(), _models(), ADR-18 revisited: hosted embedding models against bge-base, on the golden set.…, retrieve.search loads its dense model by name; hosted names resolve here…, Index every chunk with one hosted model, skipping sources already complete (a…, score_one() (+34 more)

### Community 30 - "designations"
Cohesion: 0.17
Nodes (16): Element, designations(), level_of(), 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.…, Level-1 and level-2 designations a paragraph opens with. Read from raw text,…, p(), E2: §1.988-1T says "The applicability of this section expires on December 6,…, E3: §7805(e)(2) ends a post-1988 temporary regulation within 3 years, whatever… (+8 more)

### Community 31 - "TaxCite — Phase C exit report"
Cohesion: 0.17
Nodes (11): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+3 more)

### Community 32 - "fetch"
Cohesion: 0.38
Nodes (7): fetch(), get(), Client, Path, The newest `per_topic` distinct opinions for each topic. A consolidated case is…, One opinion's PDF, cached. DAWSON hands out a short-lived signed S3 link., select()

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "pytest"
Cohesion: 0.17
Nodes (12): kappa(), Cohen's kappa for two raters over the same items., pytest, parametrize, The temporal gate's scoring rules (D2), on fixture values: no API calls., E5: one answer per plan set; rates per sample, misweighted tags counted on…, test_an_answer_cached_from_another_plan_set_is_refused(), test_as_of_match() (+4 more)

### Community 35 - "SubQuery"
Cohesion: 0.25
Nodes (5): merge(), parse(), (sub-queries, as_of, fallback reason). Never raises. A decomposition that…, One ranked list of k, round-robin across sub-queries, first occurrence wins.…, SubQuery

### Community 37 - "generate.py"
Cohesion: 0.12
Nodes (30): Answer, answer_from_groups(), answer_from_hits(), answer_schema(), authorities(), authority_label(), effective_note(), format_sources() (+22 more)

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "search"
Cohesion: 0.06
Nodes (39): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), Top-k inside one section: approximate (HNSW) or exact (sequential scan)., OR the terms: a question's words rarely all appear in one chunk, and… (+31 more)

### Community 40 - "api.py"
Cohesion: 0.08
Nodes (27): asyncio, BaseModel, contextlib, fastapi, fastapi_responses, get, pydantic, Response (+19 more)

### Community 41 - "usc_notes.py"
Cohesion: 0.06
Nodes (43): amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes(), own_designation() (+35 more)

### Community 42 - "title_of"
Cohesion: 0.25
Nodes (8): edition_year(), title_of(), Pub 17 prints its title before the number, unlike Pub 587., Pub 946 has no edition line; the bullet list ends the title., test_edition_year_and_title(), test_title_falls_back_to_the_number(), test_title_when_it_precedes_the_number(), test_title_without_a_for_use_in_line()

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "ecfr.py"
Cohesion: 0.22
Nodes (18): Block, blocks(), walk(), cite(), clean(), pack(), flush(), Parse eCFR Title 26 XML into citation-anchored chunks. (+10 more)

### Community 45 - "test_documents.py"
Cohesion: 0.06
Nodes (53): fastapi_testclient, needs_tesseract, ask(), clean(), pdf(), png(), fixture, Client-document ingestion (G2). Fixtures are built here, not stored: each is a… (+45 more)

### Community 47 - "verify.py"
Cohesion: 0.10
Nodes (35): Finding 2: a conclusion can state law on a client document's authority (D56), What exists, call_model(), cited_items(), The sentences a structured answer can show, in order: text and at least one…, (answer text, sentences dropped) from arm E's JSON. Each sentence ends with its…, A source's text as every prompt shows it. A client document is the questioner's…, Fail early and specifically. The SDK raises a generic TypeError at request… (+27 more)

### Community 48 - "index.py"
Cohesion: 0.16
Nodes (18): qdrant_client, QdrantClient, batched(), count(), create_collection(), edition(), point_id(), Embed chunks and keep a Qdrant collection in step with Postgres. Postgres is… (+10 more)

### Community 50 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 51 - "f0_verify.py"
Cohesion: 0.07
Nodes (42): concurrent_futures, abstention(), agreement(), build(), check_sheet(), claim_text(), claim_unit(), contains() (+34 more)

### Community 52 - "TaxCite: Phase E exit report"
Cohesion: 0.11
Nodes (17): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E2 and E3: the metadata, and the check that found law the parser didn't know, E4: the rerank, E5: authority in answers, Failures, with examples, Open problems handed on (+9 more)

### Community 53 - "f5_golden.py"
Cohesion: 0.11
Nodes (34): f1(), headings(), Each cached chunk's heading, which synthesis saw ("[citation] (heading)") but…, On the not-supported class: what the verifier exists to catch. `supported` is…, A line that states no claim: a section heading, a markdown title, a label…, structural(), abstention(), audit() (+26 more)

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "usc.py"
Cohesion: 0.27
Nodes (16): blocks(), child_text(), chunk_section(), clean(), designation(), lead_in(), parse(), provision_blocks() (+8 more)

### Community 58 - "G0: threat model and inventory"
Cohesion: 0.29
Nodes (6): 1. Endpoints today, 4. Where text enters a prompt, 6. What is stored that may hold PII, 7. Threat table (golden adversarial rows), 8. Open from G0, G0: threat model and inventory

### Community 59 - "cli.py"
Cohesion: 0.15
Nodes (33): BackgroundTasks, Namespace, delete_document(), post_query(), Every route but /health belongs to a tenant, resolved from its API key (Phase…, Accept a question and return immediately (ADR-9). The pipeline runs 20-30s,…, _run_job(), tenant() (+25 more)

### Community 60 - "TaxCite: Phase F exit report"
Cohesion: 0.25
Nodes (7): Golden, scored once on the shipped pipeline, How the phase went, Open, for later phases, Reproducing, TaxCite: Phase F exit report, The gates, What Phase F got wrong

### Community 61 - "G3 step 4: client facts from an uploaded document (dev, tracked not gated)"
Cohesion: 0.50
Nodes (3): Finding 1: taking facts out of the question changes public retrieval (D55), G3 step 4: client facts from an uploaded document (dev, tracked not gated), What this does not measure

### Community 62 - "decompose.py"
Cohesion: 0.09
Nodes (26): collections_abc, dataclasses, 3. Process-wide caches, functools, citation_graph(), neighbors(), Split a question into typed sub-queries, and route each to the sources that can…, Held opinions within `hops` citation steps of the seeds, in either direction;… (+18 more)

### Community 63 - "tracing.py"
Cohesion: 0.14
Nodes (15): base64, inspect, opentelemetry, annotate(), _brief(), generation(), _json(), Tracing (G1b): OpenTelemetry spans, exported to Langfuse Cloud over OTLP. Off… (+7 more)

### Community 64 - "parse"
Cohesion: 0.29
Nodes (8): skipif, fetch(), page_texts(), parse(), Path, Every chunk in one publication PDF., Download one publication, cached on disk. `delay` rate-limits bulk fetches., test_real_publication_parses_into_cited_pages()

### Community 65 - "citations.py"
Cohesion: 0.10
Nodes (31): argparse, collections, datetime, main(), G3 step 4: do a client's facts get from an uploaded document into the answer?…, run(), checks(), judge() (+23 more)

### Community 66 - "f4_hide.py"
Cohesion: 0.29
Nodes (10): base(), check_sheet(), main(), metrics(), Path, F4: one verified run, shown three ways, so the hiding unit is decided on…, The cached answer as the verifier saw it: every cited item shown., The cache entry as `unit` would show it. (+2 more)

### Community 67 - "Hosted"
Cohesion: 0.32
Nodes (3): Hosted, A hosted embedding API in fastembed's shape (`embed` for chunks, `query_embed`…, ndarray

### Community 68 - "weigh"
Cohesion: 0.40
Nodes (6): level(), A hit's authority level (E2's profile; 0 when it has none), with E4's two…, E4's reorderings of the cross-encoder's list by authority. Nothing is dropped.…, weigh(), order(), rescore()

### Community 69 - "test_store.py"
Cohesion: 0.18
Nodes (17): chunks(), parametrize, Transaction time (D6): an amendment rewrites a chunk in place; the old text…, test_a_dropped_paragraph_is_retired_by_the_sweep(), test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(), test_authority_profile_comes_from_source_and_citation_form(), test_excluded_rows_are_stored_but_not_counted_as_indexable(), test_expiry_reads_a_regulations_own_clause_against_the_snapshot_date() (+9 more)

### Community 70 - "Checkpoint 2 demo: one question per tenant (G3)"
Cohesion: 0.25
Nodes (7): Both fixed (your call, 2026-11-02), Checkpoint 2 demo: one question per tenant (G3), Finding 1: A's question never retrieved § 183 (shipped retrieval, not documents), Finding 2: a question about a document the tenant doesn't have gets a legal answer, not "no such document", For your review, Tenant A: own documents, compound question, Tenant B: asks about A's client by name

### Community 71 - "fetch"
Cohesion: 0.40
Nodes (5): fetch(), fetch_usc(), Path, Title 26 USLM XML for a release point (default: the current one), cached on…, Download one part (or a single section) of Title 26, cached on disk. The API…

### Community 72 - "post_document"
Cohesion: 0.50
Nodes (4): post, post_document(), Upload one client document (G2). Synchronous: a 50-page text PDF took 16 s,…, UploadFile

### Community 73 - "appeal"
Cohesion: 0.06
Nodes (46): FullCaseCitation, appeal(), appeal_label(), cached(), cites(), flag(), full_cites(), get() (+38 more)

### Community 74 - "in_scope"
Cohesion: 0.67
Nodes (3): in_scope(), True when a section is one of these prefixes, or a numbered child of one.…, test_in_scope_matches_children_but_not_longer_numbers()

### Community 75 - "sys"
Cohesion: 0.21
Nodes (11): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze() (+3 more)

### Community 77 - "snapshot.py"
Cohesion: 0.36
Nodes (7): create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), os, subprocess

### Community 80 - "strip_boilerplate"
Cohesion: 0.36
Nodes (8): _normalise(), Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count(), edges(), Edges must never cover the whole page, or a 5-line page is deleted entirely., test_short_pages_never_lose_everything()

### Community 81 - "Chunk"
Cohesion: 0.13
Nodes (21): Chunk, estimate_tokens(), Make `part` a running count per citation, so `key` is unique by construction.…, renumber(), pages_label(), parse(), make(), Paragraphs packed up to MAX_TOKENS, each chunk opening with the previous… (+13 more)

### Community 85 - "paragraphs"
Cohesion: 0.20
Nodes (10): LTTextBox, fold_numbers(), font_size(), paragraphs(), (page, text) for each paragraph, in reading order. Body text is the opinion's…, Prefix number-only pieces to the paragraph after them: a list number rejoins…, dehyphenate(), Join words split across a line break ("mo-\ntel" or "mo- tel" -> "motel"). A… (+2 more)

## Knowledge Gaps
- **215 isolated node(s):** `taxcite`, `P01 `G-C20#0#0s``, `P02 `G-C05#1#0s``, `P03 `G-X19#1#0``, `P04 `G-X07#3#0s`` (+210 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 748 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `parse`, `citations.py`, `test_ecfr.py`, `store.py`, `usc_notes.py`, `ecfr.py`, `index.py`, `TaxCite — Status`, `usc.py`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `Hit` (e.g. with `base()` and `chunks()`) actually correct?**
  _`Hit` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `search()` (e.g. with `2. Store reads and writes` and `7. Threat table (golden adversarial rows)`) actually correct?**
  _`search()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `taxcite`, `P01 `G-C20#0#0s``, `P02 `G-C05#1#0s`` to the rest of the system?**
  _215 weakly-connected nodes found - possible documentation gaps or missing edges._