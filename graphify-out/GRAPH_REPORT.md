# Graph Report - TaxCite.nosync  (2026-11-02)

## Corpus Check
- 271 files · ~15,013,470 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: .jsonl 6, (none) 3, .xml 3)

## Summary
- 1592 nodes · 3109 edges · 85 communities (71 shown, 14 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 244 edges (avg confidence: 0.89)
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
- call_model
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
- temporal.py
- taxcite
- Collaborative Working Mode
- retrieval.py
- test_store.py
- Postgres
- jobs.py
- test_verify.py
- e0_authority.py
- test_metrics.py
- Budget
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
- checked
- test_caselaw.py
- decompose.py
- citations
- cited_items
- aggregate
- Hosted
- f4_hide.py
- store.py
- Checkpoint 2 demo: one question per tenant (G3)
- main
- SubQuery
- section_of
- weigh
- test_fetch_rejects_a_non_pdf
- suppression
- refusals_ok
- generation
- split_sections
- _brief
- taxcite
- taxcite_ingest
- taxcite_ingest_irs_pubs
- taxcite_tracing

## God Nodes (most connected - your core abstractions)
1. `F0 judge check` - 41 edges
2. `F5 reference check` - 41 edges
3. `Hit` - 39 edges
4. `conn()` - 35 edges
5. `search()` - 34 edges
6. `F4 verdict check` - 31 edges
7. `Answer` - 26 edges
8. `Chunk` - 24 edges
9. `call_model()` - 20 edges
10. `run()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `E2 and E3: the metadata, and the check that found law the parser didn't know` --references--> `save()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/store.py
- `What exists` --references--> `authority()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/chunk.py
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

## Communities (85 total, 14 thin omitted)

### Community 0 - "client_docs.py"
Cohesion: 0.10
Nodes (27): 2. Store reads and writes, io, shutil, create_collection(), create_tables(), delete(), documents(), ingest() (+19 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.08
Nodes (38): skipif, edition_year(), fetch(), _normalise(), page_texts(), parse(), Path, Sliding windows with overlap; a short page yields a single window. (+30 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.06
Nodes (36): opentelemetry, opentelemetry_sdk_trace, opentelemetry_sdk_trace_export, opentelemetry_sdk_trace_export_in_memory_span_exporter, SpanExporter, BrokenExporter, clean(), fixture (+28 more)

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
Cohesion: 0.17
Nodes (11): abstention(), claim_unit(), f1(), On the not-supported class: what the verifier exists to catch. `supported` is…, The threshold that maximises not-supported F1 on the tune half. Ties go to the…, The small model decides only what it's sure of, the LLM the rest. Auto-accept…, Each F0 unit (cited chunks only) against today's faithfulness (LLM-extracted…, Rule 3's refusals today, over all 5 cached runs: the baseline F2's gate has to… (+3 more)

### Community 8 - "call_model"
Cohesion: 0.09
Nodes (33): 4. Where text enters a prompt, G3 step 4: five dev rows with the client's facts in a document (draft, for your review), Reproducing, answer(), chunks(), client_hits(), decompose(), Decomposition (+25 more)

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
Cohesion: 0.06
Nodes (51): gi11(), hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, C5: A cites B and C; C cites D; E cites D; Z is unheld. Hops go either…, D3b: plain-English publications outrank the statute; a statute-only search puts… (+43 more)

### Community 19 - "test_index.py"
Cohesion: 0.22
Nodes (17): chunks(), ctx(), models_(), fixture, CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., sync(), test_a_broken_qdrant_still_raises() (+9 more)

### Community 20 - "temporal.py"
Cohesion: 0.10
Nodes (28): pipeline_answer(), Path, F4's and F2's switches for an eval run: the verifier off (the unverified arm),…, Run the full pipeline once per run index and reuse it, so re-judging is free.…, set_verify(), How the phase went, as_of_match(), gate_only() (+20 more)

### Community 23 - "retrieval.py"
Cohesion: 0.09
Nodes (33): argparse, datetime, dotenv, E4: apply the dev rules as written in tasks/todo.md, before looking at which…, _models(), ADR-18 revisited: hosted embedding models against bge-base, on the golden set.…, retrieve.search loads its dense model by name; hosted names resolve here…, cost_of() (+25 more)

### Community 24 - "test_store.py"
Cohesion: 0.08
Nodes (31): chunks(), parametrize, Transaction time (D6): an amendment rewrites a chunk in place; the old text…, test_a_dropped_paragraph_is_retired_by_the_sweep(), test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(), test_authority_profile_comes_from_source_and_citation_form(), test_excluded_rows_are_stored_but_not_counted_as_indexable(), test_expiry_reads_a_regulations_own_clause_against_the_snapshot_date() (+23 more)

### Community 26 - "jobs.py"
Cohesion: 0.24
Nodes (10): Redis, client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across…, Best-effort live notification. Redis is the delivery channel, never the record,…, One server-sent event. The blank line is the record separator. (+2 more)

### Community 27 - "test_verify.py"
Cohesion: 0.10
Nodes (18): (one verdict per shown sentence, input tokens, output tokens). One call for the…, verify(), no_recite(), fixture, Claim verification (F4), tested without spending money: the verifier call is…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, A verifier stub that answers by prompt: SYSTEM gets the next of…, Re-cite (F5b C3) ships on; tests that don't stub its call turn it off, and the… (+10 more)

### Community 28 - "e0_authority.py"
Cohesion: 0.19
Nodes (17): inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the…, Part 2: which authority fields have more than one value here, and from where. (+9 more)

### Community 29 - "test_metrics.py"
Cohesion: 0.16
Nodes (19): mrr(), ndcg_at_k(), recall_at_k(), math, The metrics must be right before any number computed with them means anything., C6: three chunks share "T.C. Memo. 2023-128, at *15" and only #3 states the…, E4: a conflict row passes when its controlling source reaches its target rank;…, test_a_group_counts_once_even_when_several_members_are_retrieved() (+11 more)

### Community 30 - "Budget"
Cohesion: 0.12
Nodes (20): judge(), call(), Judge each pair against `field`'s chunks into `out`. The main pass reads every…, Budget, CostCap, extract_claims(), judge_claims(), main() (+12 more)

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
Cohesion: 0.28
Nodes (9): create(), main(), Path, restore(), post, post_document(), Upload one client document (G2). Synchronous: a 50-page text PDF took 16 s,…, client() (+1 more)

### Community 35 - "citations.py"
Cohesion: 0.05
Nodes (64): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze() (+56 more)

### Community 37 - "generate.py"
Cohesion: 0.17
Nodes (18): What exists, authority_facts(), E1's tag on one row (E4): does the controlling source reach its target rank (1,…, answer_from_hits(), authorities(), authority_label(), effective_note(), format_sources() (+10 more)

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "search"
Cohesion: 0.11
Nodes (26): Filter, edition_filter(), Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, One source or several; several is how B7 routes a sub-query to the corpora that…, Keep chunks with no edition (everything but publications, and undated…, search(), source_filter(), test_client_documents_cant_be_searched_without_a_tenant() (+18 more)

### Community 40 - "conn"
Cohesion: 0.08
Nodes (36): asyncio, BackgroundTasks, BaseModel, contextlib, fastapi, fastapi_responses, get, pydantic (+28 more)

### Community 41 - "usc_notes.py"
Cohesion: 0.09
Nodes (35): amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes(), own_designation() (+27 more)

### Community 42 - "store_bench.py"
Cohesion: 0.23
Nodes (11): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+3 more)

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "ecfr.py"
Cohesion: 0.18
Nodes (24): estimate_tokens(), §7805(e)(2): a temporary regulation issued after Nov. 20, 1988 expires within 3…, sunset(), make(), Block, blocks(), walk(), chunk_section() (+16 more)

### Community 45 - "test_documents.py"
Cohesion: 0.06
Nodes (54): main(), G3 step 4: do a client's facts get from an uploaded document into the answer?…, run(), fastapi_testclient, needs_tesseract, test_documents, ask(), clean() (+46 more)

### Community 47 - "verify.py"
Cohesion: 0.16
Nodes (16): Answer, Says INSUFFICIENT EVIDENCE and cites nothing. F3: a cited answer that flags one…, A source's text as every prompt shows it. A client document is the questioner's…, Answer a question with retrieval (`rag`) or without it (`closed_book`)., source_text(), _json(), premises(), prompt() (+8 more)

### Community 48 - "index.py"
Cohesion: 0.12
Nodes (25): psycopg_types_json, QdrantClient, authority(), expiry(), The chunk's authority profile (E2): from its source and the citation's form,…, `source_revision` where the ingester had none (E2): what `as_of` already…, whole' or 'partly' when a regulation's own clause says its applicability ended…, revision() (+17 more)

### Community 50 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 51 - "f0_verify.py"
Cohesion: 0.12
Nodes (23): concurrent_futures, agreement(), build(), check_sheet(), claim_text(), contains(), kind_of(), main() (+15 more)

### Community 52 - "TaxCite: Phase E exit report"
Cohesion: 0.17
Nodes (11): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E2 and E3: the metadata, and the check that found law the parser didn't know, E4: the rerank, E5: authority in answers, Failures, with examples, Reproducing (+3 more)

### Community 53 - "f5_golden.py"
Cohesion: 0.15
Nodes (25): headings(), Each cached chunk's heading, which synthesis saw ("[citation] (heading)") but…, audit(), check(), checkpoint(), save(), judge(), ladder() (+17 more)

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "usc.py"
Cohesion: 0.25
Nodes (17): blocks(), child_text(), chunk_section(), make(), clean(), designation(), lead_in(), parse() (+9 more)

### Community 58 - "G0: threat model and inventory"
Cohesion: 0.29
Nodes (6): 1. Endpoints today, 5. Where text reaches the user, 6. What is stored that may hold PII, 7. Threat table (golden adversarial rows), 8. Open from G0, G0: threat model and inventory

### Community 59 - "cli.py"
Cohesion: 0.17
Nodes (29): Connection, Namespace, backfill_authority(), create_tenant(), fetch(), fetch_usc(), ingest_case(), ingest_ecfr() (+21 more)

### Community 60 - "TaxCite: Phase F exit report"
Cohesion: 0.29
Nodes (6): Golden, scored once on the shipped pipeline, Open, for later phases, Reproducing, TaxCite: Phase F exit report, The gates, What Phase F got wrong

### Community 61 - "checked"
Cohesion: 0.16
Nodes (13): Finding 1: taking facts out of the question changes public retrieval (D55), Finding 2: a conclusion can state law on a client document's authority (D56), G3 step 4: client facts from an uploaded document (dev, tracked not gated), What this does not measure, What exists, checked(), conclude(), displayed() (+5 more)

### Community 62 - "test_caselaw.py"
Cohesion: 0.12
Nodes (8): memo(), fixture, Case-law tests against two real Tax Court opinions (see tasks/todo.md B3): -…, E3 (Estate of Caan): DAWSON lists the correction's date; the opinion says when…, result(), tc(), test_a_corrected_reissue_keeps_the_opinions_own_filing_date(), test_selection_dedupes_by_citation_and_keeps_the_newest()

### Community 63 - "decompose.py"
Cohesion: 0.09
Nodes (29): base64, collections_abc, dataclasses, 3. Process-wide caches, functools, inspect, qdrant_client, SparseVector (+21 more)

### Community 64 - "citations"
Cohesion: 0.19
Nodes (13): material(), Completeness over material sentences, and the share of answers that would…, Split outside brackets, at . ! ? followed by a space, never after an…, A line that states no claim: a section heading, a markdown title, a label…, sentences(), structural(), abstention(), completeness() (+5 more)

### Community 65 - "cited_items"
Cohesion: 0.14
Nodes (15): answer_schema(), cited_items(), _generate_structured(), parse_citations(), The JSON schema for arm E: strict, so every field is required and nothing else…, The sentences a structured answer can show, in order: text and at least one…, (answer text, sentences dropped) from arm E's JSON. Each sentence ends with its…, Split the answer's citations three ways: exact, derived, unsupported. The three… (+7 more)

### Community 66 - "aggregate"
Cohesion: 0.18
Nodes (12): aggregate(), Judged, None when there is nothing to score: a refusal, or an answer making no claim., Refusals are excluded from the mean and reported separately (§9.2). Averaging a…, judged(), An answer the extractor found nothing in would otherwise score 0/0., A row with one claim per entry in `supported`., Averaging refusals in either direction breaks the gate: 0 punishes the… (+4 more)

### Community 67 - "Hosted"
Cohesion: 0.32
Nodes (3): Hosted, A hosted embedding API in fastembed's shape (`embed` for chunks, `query_embed`…, ndarray

### Community 68 - "f4_hide.py"
Cohesion: 0.29
Nodes (10): base(), check_sheet(), main(), metrics(), Path, F4: one verified run, shown three ways, so the hiding unit is decided on…, The cached answer as the verifier saw it: every cited item shown., The cache entry as `unit` would show it. (+2 more)

### Community 69 - "store.py"
Cohesion: 0.21
Nodes (11): psycopg, secrets, create_tenant(), held_at(), datetime, Postgres storage for chunks. One table, created on demand. Writes are…, Create a tenant and return its API key. The caller commits., The tenant id an API key belongs to, or None. (+3 more)

### Community 70 - "Checkpoint 2 demo: one question per tenant (G3)"
Cohesion: 0.29
Nodes (6): Checkpoint 2 demo: one question per tenant (G3), Finding 1: A's question never retrieved § 183 (shipped retrieval, not documents), Finding 2: a question about a document the tenant doesn't have gets a legal answer, not "no such document", For your review, Tenant A: own documents, compound question, Tenant B: asks about A's client by name

### Community 72 - "SubQuery"
Cohesion: 0.33
Nodes (3): parse(), (sub-queries, as_of, fallback reason). Never raises. A decomposition that…, SubQuery

### Community 73 - "section_of"
Cohesion: 0.22
Nodes (9): build(), collection_for(), main(), Index every chunk with one hosted model, skipping sources already complete (a…, score_one(), The section a citation belongs to, ignoring paragraph depth. '26 CFR…, section_of(), test_section_of_strips_paragraph_markers() (+1 more)

### Community 74 - "weigh"
Cohesion: 0.40
Nodes (6): level(), A hit's authority level (E2's profile; 0 when it has none), with E4's two…, E4's reorderings of the cross-encoder's list by authority. Nothing is dropped.…, weigh(), order(), rescore()

### Community 76 - "suppression"
Cohesion: 0.50
Nodes (4): Sentences no pair of this unit covers: every uncited one for sentences, only…, What ADR-15 would hide over answers that weren't refusals, for one claim unit.…, suppression(), uncited()

### Community 77 - "refusals_ok"
Cohesion: 0.50
Nodes (4): Refusals sit outside the faithfulness mean (see `aggregate`), so a build that…, refusals_ok(), D7's first build: faithfulness passed at 0.866 while refusing more than half…, test_refusal_rate_gate()

### Community 78 - "generation"
Cohesion: 0.50
Nodes (4): annotate(), generation(), Attributes on the current span; None values are left out. A no-op when tracing…, Mark the current span as one LLM call, in the attribute names Langfuse reads.

### Community 80 - "_brief"
Cohesion: 0.40
Nodes (5): _brief(), _json(), A readable, bounded copy of a step's arguments or result., wrap(), inner()

## Knowledge Gaps
- **214 isolated node(s):** `taxcite`, `P01 `G-C20#0#0s``, `P02 `G-C05#1#0s``, `P03 `G-X19#1#0``, `P04 `G-X07#3#0s`` (+209 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 741 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `caselaw.py` to `test_irs_pubs.py`, `test_ecfr.py`, `store.py`, `usc_notes.py`, `ecfr.py`, `index.py`, `TaxCite — Status`, `usc.py`, `cli.py`?**
  _High betweenness centrality (0.164) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.152) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `Hit` (e.g. with `base()` and `chunks()`) actually correct?**
  _`Hit` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `search()` (e.g. with `2. Store reads and writes` and `7. Threat table (golden adversarial rows)`) actually correct?**
  _`search()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `taxcite`, `P01 `G-C20#0#0s``, `P02 `G-C05#1#0s`` to the rest of the system?**
  _214 weakly-connected nodes found - possible documentation gaps or missing edges._