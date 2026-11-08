# Graph Report - TaxCite.nosync  (2026-11-07)

## Corpus Check
- 285 files · ~15,098,069 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: .jsonl 13, (none) 3, .xml 3)

## Summary
- 1667 nodes · 3249 edges · 100 communities (78 shown, 22 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 261 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d7b065da`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- client_docs.py
- test_irs_pubs.py
- test_jobs.py
- T2: Ingest eCFR Title 26
- json
- test_ecfr.py
- TaxCite — Phase B exit report
- history
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
- pytest
- taxcite
- Collaborative Working Mode
- ragas_eval.py
- test_usc.py
- Postgres
- jobs.py
- test_verify.py
- TaxCite — Phase C exit report
- test_metrics.py
- ecfr.py
- retrieval.py
- citations
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- flags
- test_render.py
- Plain-Module Package Layout
- generate.py
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- api.py
- usc_notes.py
- appeal
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
- is_appeal
- TaxCite: Phase G exit report
- cli.py
- TaxCite: Phase F exit report
- authorities
- usc.py
- retrieve.py
- e0_authority.py
- taxcite
- test_store.py
- Hosted
- report
- decompose.py
- Checkpoint 2 demo: one question per tenant (G3)
- caselaw.py
- parse
- citations.py
- designations
- e3_sample.py
- g4-corpus-draft.md
- snapshot.py
- embed_bench.py
- f4_hide.py
- store_bench.py
- taxcite_tracing
- taxcite_ingest_irs_pubs
- g4_injection.py
- split_sections
- in_scope
- taxcite_ingest
- set_prompt
- weigh
- ruling
- stub
- gate_only
- test_openai_gets_the_schema_as_strict_structured_outputs
- test_synthesis_is_pinned_not_sampled
- test_every_profile_e2_produces_has_a_label
- test_citations_flatten_nested_brackets_and_split_packed_ones
- test_the_tax_year_line_is_the_questions_year_never_the_models_guess
- test_a_narrower_paragraph_of_a_retrieved_section_counts_as_derived
- test_invented_citations_are_flagged
- test_closed_book_does_not_retrieve

## God Nodes (most connected - your core abstractions)
1. `F0 judge check` - 41 edges
2. `F5 reference check` - 41 edges
3. `Hit` - 39 edges
4. `conn()` - 37 edges
5. `search()` - 36 edges
6. `F4 verdict check` - 31 edges
7. `Answer` - 27 edges
8. `Chunk` - 24 edges
9. `run()` - 22 edges
10. `call_model()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `Both fixed (your call, 2026-11-02)` --references--> `run()`  [INFERRED]
  eval/results/g3-demo.md → src/taxcite/jobs.py
- `E2 and E3: the metadata, and the check that found law the parser didn't know` --references--> `save()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/store.py
- `What exists` --references--> `authority()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/chunk.py
- `3. Process-wide caches` --references--> `decompose()`  [INFERRED]
  eval/results/g0-threat-model.md → src/taxcite/decompose.py
- `2. Store reads and writes` --references--> `retrieve()`  [INFERRED]
  eval/results/g0-threat-model.md → src/taxcite/decompose.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]

## Communities (100 total, 22 thin omitted)

### Community 0 - "client_docs.py"
Cohesion: 0.11
Nodes (26): io, authority(), The chunk's authority profile (E2): from its source and the citation's form,…, create_collection(), create_tables(), ingest(), kind(), ocr() (+18 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.08
Nodes (27): skipif, _normalise(), Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count(), edges(), page() (+19 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.06
Nodes (38): opentelemetry, opentelemetry_sdk_trace, opentelemetry_sdk_trace_export, opentelemetry_sdk_trace_export_in_memory_span_exporter, SpanExporter, BrokenExporter, clean(), fixture (+30 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.16
Nodes (15): eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark, Harvard Caselaw Access Project, Per-Document-Type Chunker (§3.2), CourtListener (+7 more)

### Community 4 - "json"
Cohesion: 0.13
Nodes (22): argparse, datetime, dotenv, E4: apply the dev rules as written in tasks/todo.md, before looking at which…, main(), G3 step 4: do a client's facts get from an uploaded document into the answer?…, run(), cost_of() (+14 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.14
Nodes (16): of(), Chunker tests against nine real sections in tests/fixtures/ecfr_sample.xml.…, eCFR ships its own citation string in hierarchy_metadata; ours must agree., test_cita_is_kept_out_of_the_text(), test_example_text_in_pspace_is_captured(), test_large_table_is_recorded_with_a_reason(), test_letter_i_section_cites_through_j(), test_neighbouring_units_pack_into_a_range_citation() (+8 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "history"
Cohesion: 0.19
Nodes (13): FullCaseCitation, full_cites(), history(), label(), The year in the parenthetical right after the cite. eyecite's own guess can…, Explanatory parentheticals push "aff'd" past the window: "113 T.C. 254 (1999)…, The appeal as one stable string, "560 F.3d 620 (ca7 2009)": no case name or pin…, (opinion, kind, by) from subsequent history in a passage. by is the appellate… (+5 more)

### Community 8 - "store.py"
Cohesion: 0.18
Nodes (13): psycopg, secrets, Every route but /health belongs to a tenant, resolved from its API key (Phase…, tenant(), create_tenant(), held_at(), datetime, Postgres storage for chunks. One table, created on demand. Writes are… (+5 more)

### Community 9 - "F5 reference check"
Cohesion: 0.05
Nodes (41): F5 reference check, R01 `G-C17#0#1`, R02 `G-S18#0#1`, R03 `G-X14#0#1`, R04 `G-C14#0#3`, R05 `G-X05#0#3`, R06 `G-S06#0#2`, R07 `G-S24#0#0` (+33 more)

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

### Community 19 - "test_index.py"
Cohesion: 0.22
Nodes (17): chunks(), ctx(), models_(), fixture, CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., sync(), test_a_broken_qdrant_still_raises() (+9 more)

### Community 20 - "pytest"
Cohesion: 0.12
Nodes (16): as_of_match(), kappa(), passed(), Year-level match of the plan's as-of against the row's tax year. None = not…, Cohen's kappa for two raters over the same items., Per sample index: rates over the rows, first judge repeat (E5). Conflict and…, sample_summary(), pytest (+8 more)

### Community 23 - "ragas_eval.py"
Cohesion: 0.11
Nodes (27): aggregate(), Budget, CostCap, extract_claims(), judge_claims(), Judged, main(), parse_json() (+19 more)

### Community 24 - "test_usc.py"
Cohesion: 0.16
Nodes (14): chunks(), of(), fixture, Statute chunker tests against eight real sections in…, test_en_dash_section_number_becomes_a_hyphen(), test_heading_folds_into_its_first_child(), test_neighbouring_subsections_pack_into_a_range(), test_notes_are_not_text_and_source_credit_is_the_history() (+6 more)

### Community 26 - "jobs.py"
Cohesion: 0.22
Nodes (11): os, Redis, client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across…, Best-effort live notification. Redis is the delivery channel, never the record,… (+3 more)

### Community 27 - "test_verify.py"
Cohesion: 0.09
Nodes (18): no_recite(), fixture, Claim verification (F4), tested without spending money: the verifier call is…, G6 (G-A01): sentences tagged parts 2 and 3 of a one-part answer render under…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, A verifier stub that answers by prompt: SYSTEM gets the next of…, Re-cite (F5b C3) ships on; tests that don't stub its call turn it off, and the…, routed() (+10 more)

### Community 28 - "TaxCite — Phase C exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+4 more)

### Community 29 - "test_metrics.py"
Cohesion: 0.08
Nodes (34): mrr(), ndcg_at_k(), recall_at_k(), judged(), parametrize, The metrics must be right before any number computed with them means anything., An answer the extractor found nothing in would otherwise score 0/0., Instruction is not a guarantee; the model sometimes wraps its JSON in prose. (+26 more)

### Community 30 - "ecfr.py"
Cohesion: 0.18
Nodes (22): §7805(e)(2): a temporary regulation issued after Nov. 20, 1988 expires within 3…, sunset(), Block, blocks(), walk(), chunk_section(), make(), cite() (+14 more)

### Community 31 - "retrieval.py"
Cohesion: 0.11
Nodes (20): authority_facts(), cached_decompose(), first_hits(), groups(), main(), needs_case_law(), Path, Score retrieval against the pilot set: the first rungs of the §9 ablation… (+12 more)

### Community 32 - "citations"
Cohesion: 0.19
Nodes (13): material(), Completeness over material sentences, and the share of answers that would…, Split outside brackets, at . ! ? followed by a space, never after an…, A line that states no claim: a section heading, a markdown title, a label…, sentences(), structural(), abstention(), completeness() (+5 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "flags"
Cohesion: 0.40
Nodes (5): Open problems handed on, flag(), flags(), One opinion's treatment flag from its (source, kind, by, checked_at) rows (C4).…, Treatment flags for the opinions an answer cites. Fails open: if the table…

### Community 35 - "test_render.py"
Cohesion: 0.17
Nodes (14): browser(), page(), handle(), fixture, G5, the render path (ADR-13): nothing from a source, a document or an answer…, ADR-13 by construction: none of the APIs that turn a string into markup appear…, The page with every route stubbed; records outbound requests, dialogs and…, render_everything() (+6 more)

### Community 37 - "generate.py"
Cohesion: 0.11
Nodes (30): 4. Where text enters a prompt, (sub-query, its chunks) for the synthesis prompt, limited to `keep` if given.…, answer_from_groups(), answer_from_hits(), answer_schema(), authority_label(), call_model(), effective_note() (+22 more)

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "search"
Cohesion: 0.11
Nodes (26): Filter, edition_filter(), Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, One source or several; several is how B7 routes a sub-query to the corpora that…, Keep chunks with no edition (everything but publications, and undated…, search(), source_filter(), test_client_documents_cant_be_searched_without_a_tenant() (+18 more)

### Community 40 - "api.py"
Cohesion: 0.06
Nodes (36): asyncio, BackgroundTasks, BaseModel, contextlib, fastapi, fastapi_responses, fastapi_staticfiles, get (+28 more)

### Community 41 - "usc_notes.py"
Cohesion: 0.06
Nodes (43): amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes(), own_designation() (+35 more)

### Community 42 - "appeal"
Cohesion: 0.25
Nodes (9): appeal(), appeal_label(), cached(), get(), Client, Path, One format for both sources, so a reader sees the same appeal the same way., A response cached with the time it was fetched: re-running from cache must not… (+1 more)

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "app.js"
Cohesion: 0.44
Nodes (10): ADR-0013, api(), ask(), detail(), el(), events(), listDocuments(), showAnswer() (+2 more)

### Community 45 - "test_documents.py"
Cohesion: 0.05
Nodes (61): fastapi_testclient, needs_tesseract, shutil, ask(), clean(), pdf(), png(), fixture (+53 more)

### Community 47 - "verify.py"
Cohesion: 0.08
Nodes (40): Finding 1: taking facts out of the question changes public retrieval (D55), Finding 2: a conclusion can state law on a client document's authority (D56), G3 step 4: client facts from an uploaded document (dev, tracked not gated), What this does not measure, What exists, Answer, cited_items(), The sentences a structured answer can show, in order: text and at least one… (+32 more)

### Community 48 - "index.py"
Cohesion: 0.13
Nodes (24): psycopg_types_json, QdrantClient, expiry(), `source_revision` where the ingester had none (E2): what `as_of` already…, whole' or 'partly' when a regulation's own clause says its applicability ended…, revision(), backfill_authority(), batched() (+16 more)

### Community 50 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 51 - "f0_verify.py"
Cohesion: 0.12
Nodes (24): concurrent_futures, agreement(), build(), check_sheet(), claim_text(), contains(), judge(), call() (+16 more)

### Community 52 - "TaxCite: Phase E exit report"
Cohesion: 0.17
Nodes (11): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E2 and E3: the metadata, and the check that found law the parser didn't know, E4: the rerank, E5: authority in answers, Failures, with examples, Reproducing (+3 more)

### Community 53 - "f5_golden.py"
Cohesion: 0.13
Nodes (27): f1(), headings(), Each cached chunk's heading, which synthesis saw ("[citation] (heading)") but…, On the not-supported class: what the verifier exists to catch. `supported` is…, audit(), check(), checkpoint(), save() (+19 more)

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "is_appeal"
Cohesion: 0.32
Nodes (8): is_appeal(), party(), petitioners(), The petitioners' names alone: "Estate of James E. Caan, Deceased, …,…, Family names in a joint caption. "C. Michael & Gwendolyn E. Willock" is one…, A caseName query for the appellate caption: surnames for people ("Donald B. &…, Same-name appeals are common (C1: three unrelated Michaels for Willock). A real…, surnames()

### Community 58 - "TaxCite: Phase G exit report"
Cohesion: 0.15
Nodes (14): Cost, Deferred, by decision, Golden adversarial rows, scored once on the shipped pipeline, Reproducing, TaxCite: Phase G exit report, The gates, Threat table, as built, What each control caught, with the payload (+6 more)

### Community 59 - "cli.py"
Cohesion: 0.15
Nodes (34): Connection, Namespace, delete_document(), _run_job(), backfill_authority(), create_tenant(), fetch(), fetch_usc() (+26 more)

### Community 60 - "TaxCite: Phase F exit report"
Cohesion: 0.25
Nodes (7): Golden, scored once on the shipped pipeline, How the phase went, Open, for later phases, Reproducing, TaxCite: Phase F exit report, The gates, What Phase F got wrong

### Community 61 - "authorities"
Cohesion: 0.14
Nodes (14): 1. Endpoints today, 2. Store reads and writes, 5. Where text reaches the user, 6. What is stored that may hold PII, 7. Threat table (golden adversarial rows), 8. Open from G0, G0: threat model and inventory, What exists (+6 more)

### Community 62 - "usc.py"
Cohesion: 0.27
Nodes (16): blocks(), child_text(), chunk_section(), clean(), designation(), lead_in(), parse(), provision_blocks() (+8 more)

### Community 63 - "retrieve.py"
Cohesion: 0.08
Nodes (29): base64, collections_abc, dataclasses, 3. Process-wide caches, functools, inspect, SparseVector, lifespan() (+21 more)

### Community 64 - "e0_authority.py"
Cohesion: 0.33
Nodes (10): inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the…, Part 2: which authority fields have more than one value here, and from where. (+2 more)

### Community 66 - "test_store.py"
Cohesion: 0.18
Nodes (17): chunks(), parametrize, Transaction time (D6): an amendment rewrites a chunk in place; the old text…, test_a_dropped_paragraph_is_retired_by_the_sweep(), test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(), test_authority_profile_comes_from_source_and_citation_form(), test_excluded_rows_are_stored_but_not_counted_as_indexable(), test_expiry_reads_a_regulations_own_clause_against_the_snapshot_date() (+9 more)

### Community 67 - "Hosted"
Cohesion: 0.32
Nodes (3): Hosted, A hosted embedding API in fastembed's shape (`embed` for chunks, `query_embed`…, ndarray

### Community 68 - "report"
Cohesion: 0.12
Nodes (15): abstention(), claim_unit(), Overlapping word windows covering the whole chunk: the last one starts at or…, The threshold that maximises not-supported F1 on the tune half. Ties go to the…, The small model decides only what it's sure of, the LLM the rest. Auto-accept…, Sentences no pair of this unit covers: every uncited one for sentences, only…, What ADR-15 would hide over answers that weren't refusals, for one claim unit.…, Each F0 unit (cited chunks only) against today's faithfulness (LLM-extracted… (+7 more)

### Community 69 - "decompose.py"
Cohesion: 0.08
Nodes (37): G3 step 4: five dev rows with the client's facts in a document (draft, for your review), Reproducing, answer(), chunks(), citation_graph(), client_hits(), decompose(), Decomposition (+29 more)

### Community 70 - "Checkpoint 2 demo: one question per tenant (G3)"
Cohesion: 0.25
Nodes (7): Both fixed (your call, 2026-11-02), Checkpoint 2 demo: one question per tenant (G3), Finding 1: A's question never retrieved § 183 (shipped retrieval, not documents), Finding 2: a question about a document the tenant doesn't have gets a legal answer, not "no such document", For your review, Tenant A: own documents, compound question, Tenant B: asks about A's client by name

### Community 71 - "caselaw.py"
Cohesion: 0.09
Nodes (40): collections, httpx, LTTextBox, pdfminer_high_level, pdfminer_layout, re, Chunk, estimate_tokens() (+32 more)

### Community 72 - "parse"
Cohesion: 0.14
Nodes (14): parse(), Every chunk in an eCFR XML file or element tree., chunks(), fixture, A section can embed its own outline (§1.61-21 does); it must not create new…, Two chunks reaching the same citation get distinct parts, so keys cannot…, E2: §1.988-1T says "The applicability of this section expires on December 6,…, E3: §7805(e)(2) ends a post-1988 temporary regulation within 3 years, whatever… (+6 more)

### Community 73 - "citations.py"
Cohesion: 0.19
Nodes (15): eyecite, eyecite_models, logging, load_selection(), The selection is cached so the corpus stays fixed while new opinions are filed., cites(), load(), normalize() (+7 more)

### Community 74 - "designations"
Cohesion: 0.24
Nodes (12): Element, designations(), level_of(), 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.…, Level-1 and level-2 designations a paragraph opens with. Read from raw text,…, p(), test_compact_two_level_designation(), test_designation_split_by_italic_heading() (+4 more)

### Community 75 - "e3_sample.py"
Cohesion: 0.33
Nodes (9): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze() (+1 more)

### Community 77 - "snapshot.py"
Cohesion: 0.43
Nodes (6): create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), subprocess

### Community 78 - "embed_bench.py"
Cohesion: 0.21
Nodes (10): build(), collection_for(), main(), _models(), ADR-18 revisited: hosted embedding models against bge-base, on the golden set.…, retrieve.search loads its dense model by name; hosted names resolve here…, Index every chunk with one hosted model, skipping sources already complete (a…, score_one() (+2 more)

### Community 79 - "f4_hide.py"
Cohesion: 0.29
Nodes (10): base(), check_sheet(), main(), metrics(), Path, F4: one verified run, shown three ways, so the hiding unit is decided on…, The cached answer as the verifier saw it: every cited item shown., The cache entry as `unit` would show it. (+2 more)

### Community 80 - "store_bench.py"
Cohesion: 0.23
Nodes (11): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+3 more)

### Community 83 - "g4_injection.py"
Cohesion: 0.31
Nodes (9): checks(), golden_rows(), judge(), main(), G4: the prompt-path injection corpus. Does a hostile document (or user) change…, Shown sentences that don't end with a citation. Headers and INSUFFICIENT…, G6: the golden adversarial rows in this runner's shape: the universal checks,…, run() (+1 more)

### Community 85 - "in_scope"
Cohesion: 0.67
Nodes (3): in_scope(), True when a section is one of these prefixes, or a numbered child of one.…, test_in_scope_matches_children_but_not_longer_numbers()

### Community 87 - "set_prompt"
Cohesion: 0.20
Nodes (10): E5's prompt arms, each built from the pre-E5 prompt: "pre-e5" is it unchanged…, set_prompt(), E5: every E5 arm is built from the pre-E5 prompt, so "pre-e5" reproduces that…, F3: arm E ships ((ii′)'s rules with rules 2 and 3 for JSON items); "pre-f3" is…, B9's calibration arm, rebuilt on the shipped (structured) prompt for F3's band…, test_e5_arms_rebuild_from_pre_e5_and_run_unstructured(), test_f3_arms_rewrite_rule_2_and_only_the_sections_arm_numbers_parts(), test_structured_synthesis_renders_json_and_refuses_on_an_unusable_response() (+2 more)

### Community 88 - "weigh"
Cohesion: 0.40
Nodes (6): level(), A hit's authority level (E2's profile; 0 when it has none), with E4's two…, E4's reorderings of the cross-encoder's list by authority. Nothing is dropped.…, weigh(), order(), rescore()

### Community 89 - "ruling"
Cohesion: 0.40
Nodes (5): kind(), A mixed disposition takes its most serious part: "aff'd in part, rev'd in part"…, The outcome in an appellate opinion's last disposition sentence, or None (e.g.…, ruling(), split()

### Community 90 - "stub"
Cohesion: 0.50
Nodes (3): fixture, Replace the model call; record what it was asked., stub()

### Community 91 - "gate_only"
Cohesion: 0.67
Nodes (3): gate_only(), Path, F2's cheap pass: for each row and plan set, the parts the shipped pipeline…

## Knowledge Gaps
- **223 isolated node(s):** `taxcite`, `STAGES`, `ADR-0013`, `P01 `G-C20#0#0s``, `P02 `G-C05#1#0s`` (+218 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 770 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `caselaw.py` to `test_ecfr.py`, `parse`, `usc_notes.py`, `store.py`, `index.py`, `TaxCite — Status`, `ecfr.py`, `cli.py`, `usc.py`?**
  _High betweenness centrality (0.132) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `Hit` (e.g. with `base()` and `chunks()`) actually correct?**
  _`Hit` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `search()` (e.g. with `2. Store reads and writes` and `7. Threat table (golden adversarial rows)`) actually correct?**
  _`search()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `taxcite`, `STAGES`, `ADR-0013` to the rest of the system?**
  _223 weakly-connected nodes found - possible documentation gaps or missing edges._