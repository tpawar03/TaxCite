# Graph Report - TaxCite.nosync  (2026-11-02)

## Corpus Check
- 263 files · ~15,005,592 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: .jsonl 4, (none) 3, .xml 3)

## Summary
- 1506 nodes · 2889 edges · 83 communities (69 shown, 14 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 228 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c5558801`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.py
- test_irs_pubs.py
- test_jobs.py
- T2: Ingest eCFR Title 26
- tracing.py
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
- ragas_eval.py
- taxcite
- Collaborative Working Mode
- json
- test_caselaw.py
- Postgres
- jobs.py
- test_verify.py
- retrieval.py
- test_metrics.py
- usc.py
- TaxCite — Phase C exit report
- report
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- f5_golden.py
- citations.py
- Plain-Module Package Layout
- generate.py
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- irs_pubs.py
- Chunk
- store_bench.py
- TaxCite — Phase D exit report
- test_usc.py
- test_leakage.py
- taxcite_ingest_caselaw
- TaxCite: Phase E exit report
- client
- taxcite_ingest_citations
- TaxCite — Status
- ecfr.py
- caselaw.py
- sufficiency
- F4 verdict check
- F0 judge check
- taxcite_ingest_ecfr
- conn
- aggregate
- cli.py
- TaxCite: Phase F exit report
- verify.py
- chunk.py
- taxcite_ingest_irs_pubs
- test_usc_notes.py
- citations
- taxcite_tracing
- Hosted
- f4_hide.py
- decompose.py
- test_fetch_rejects_a_non_pdf
- Connection
- taxcite
- taxcite_ingest
- strip_boilerplate
- retrieve.py
- MissingCredentials
- e3_sample.py
- weigh
- test_health.py
- dehyphenate
- stub_pipeline
- chunks

## God Nodes (most connected - your core abstractions)
1. `F0 judge check` - 41 edges
2. `F5 reference check` - 41 edges
3. `Hit` - 35 edges
4. `conn()` - 32 edges
5. `search()` - 31 edges
6. `F4 verdict check` - 31 edges
7. `Answer` - 25 edges
8. `Chunk` - 24 edges
9. `call_model()` - 20 edges
10. `run()` - 19 edges

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

## Communities (83 total, 14 thin omitted)

### Community 0 - "index.py"
Cohesion: 0.11
Nodes (29): os, psycopg_types_json, QdrantClient, secrets, authority(), The chunk's authority profile (E2): from its source and the citation's form,…, `source_revision` where the ingester had none (E2): what `as_of` already…, revision() (+21 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.14
Nodes (16): skipif, Sliding windows with overlap; a short page yields a single window., windows(), page(), Publication chunking: pure functions tested on text, no PDF needed., A page shaped like a real one: header lines, body, footer., A table row like "Line 6 amount" must survive digit-normalised matching., Pub 17 prints its title before the number, unlike Pub 587. (+8 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.06
Nodes (37): opentelemetry_sdk_trace, opentelemetry_sdk_trace_export, opentelemetry_sdk_trace_export_in_memory_span_exporter, SpanExporter, BrokenExporter, clean(), fixture, Job record and SSE transport (ADR-9), with the pipeline stubbed. (+29 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.16
Nodes (15): eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark, Harvard Caselaw Access Project, Per-Document-Type Chunker (§3.2), CourtListener (+7 more)

### Community 4 - "tracing.py"
Cohesion: 0.12
Nodes (18): base64, inspect, opentelemetry, lifespan(), annotate(), _brief(), generation(), _json() (+10 more)

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
Cohesion: 0.19
Nodes (16): chunks(), parametrize, Transaction time (D6): an amendment rewrites a chunk in place; the old text…, test_a_dropped_paragraph_is_retired_by_the_sweep(), test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(), test_authority_profile_comes_from_source_and_citation_form(), test_excluded_rows_are_stored_but_not_counted_as_indexable(), test_reingest_is_idempotent() (+8 more)

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

### Community 20 - "ragas_eval.py"
Cohesion: 0.07
Nodes (45): argparse, datetime, Budget, CostCap, extract_claims(), judge_claims(), main(), parse_json() (+37 more)

### Community 23 - "json"
Cohesion: 0.16
Nodes (15): dotenv, E4: apply the dev rules as written in tasks/todo.md, before looking at which…, cost_of(), estimate(), judge(), main(), ADR-11: choose the LLM by measuring answers, not by price alone. uv run python…, Rough spend before committing: RAG prompts dominate the input tokens. (+7 more)

### Community 24 - "test_caselaw.py"
Cohesion: 0.12
Nodes (8): memo(), fixture, Case-law tests against two real Tax Court opinions (see tasks/todo.md B3): -…, E3 (Estate of Caan): DAWSON lists the correction's date; the opinion says when…, result(), tc(), test_a_corrected_reissue_keeps_the_opinions_own_filing_date(), test_selection_dedupes_by_citation_and_keeps_the_newest()

### Community 26 - "jobs.py"
Cohesion: 0.18
Nodes (14): 2. Store reads and writes, Open problems handed on, Redis, flags(), Treatment flags for the opinions an answer cites. Fails open: if the table…, client(), Event, notify() (+6 more)

### Community 27 - "test_verify.py"
Cohesion: 0.10
Nodes (16): no_recite(), fixture, Claim verification (F4), tested without spending money: the verifier call is…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, A verifier stub that answers by prompt: SYSTEM gets the next of…, Re-cite (F5b C3) ships on; tests that don't stub its call turn it off, and the…, routed(), structured_answer() (+8 more)

### Community 28 - "retrieval.py"
Cohesion: 0.09
Nodes (31): collections, inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the… (+23 more)

### Community 29 - "test_metrics.py"
Cohesion: 0.12
Nodes (24): mrr(), ndcg_at_k(), recall_at_k(), parametrize, The metrics must be right before any number computed with them means anything., Instruction is not a guarantee; the model sometimes wraps its JSON in prose., C6: three chunks share "T.C. Memo. 2023-128, at *15" and only #3 states the…, D7's first build: faithfulness passed at 0.866 while refusing more than half… (+16 more)

### Community 30 - "usc.py"
Cohesion: 0.22
Nodes (19): Make `part` a running count per citation, so `key` is unique by construction.…, renumber(), blocks(), child_text(), chunk_section(), make(), clean(), designation() (+11 more)

### Community 31 - "TaxCite — Phase C exit report"
Cohesion: 0.17
Nodes (11): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+3 more)

### Community 32 - "report"
Cohesion: 0.12
Nodes (15): abstention(), claim_unit(), f1(), On the not-supported class: what the verifier exists to catch. `supported` is…, The threshold that maximises not-supported F1 on the tune half. Ties go to the…, The small model decides only what it's sure of, the LLM the rest. Auto-accept…, Sentences no pair of this unit covers: every uncited one for sentences, only…, What ADR-15 would hide over answers that weren't refusals, for one claim unit.… (+7 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "f5_golden.py"
Cohesion: 0.15
Nodes (25): headings(), Each cached chunk's heading, which synthesis saw ("[citation] (heading)") but…, audit(), check(), checkpoint(), save(), judge(), ladder() (+17 more)

### Community 35 - "citations.py"
Cohesion: 0.07
Nodes (50): eyecite, eyecite_models, FullCaseCitation, logging, appeal(), appeal_label(), cached(), cites() (+42 more)

### Community 37 - "generate.py"
Cohesion: 0.13
Nodes (24): collections_abc, (sub-query, its chunks) for the synthesis prompt, limited to `keep` if given.…, Answer, answer_from_groups(), answer_from_hits(), answer_schema(), authority_label(), effective_note() (+16 more)

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "search"
Cohesion: 0.08
Nodes (35): 3. Process-wide caches, Filter, SparseVector, edition_filter(), embed(), _models(), Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, Loaded once per process and per model: ~4s, which every query would otherwise… (+27 more)

### Community 40 - "irs_pubs.py"
Cohesion: 0.17
Nodes (15): pdfminer_high_level, pdfminer_layout, edition_year(), fetch(), page_texts(), parse(), Path, Ingest IRS publications (PDF). Publications have no paragraph numbering to cut… (+7 more)

### Community 41 - "Chunk"
Cohesion: 0.14
Nodes (25): Chunk, amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes() (+17 more)

### Community 42 - "store_bench.py"
Cohesion: 0.23
Nodes (11): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+3 more)

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "test_usc.py"
Cohesion: 0.19
Nodes (12): of(), Statute chunker tests against eight real sections in…, test_en_dash_section_number_becomes_a_hyphen(), test_heading_folds_into_its_first_child(), test_neighbouring_subsections_pack_into_a_range(), test_notes_are_not_text_and_source_credit_is_the_history(), test_oversized_subsection_splits_at_level_two(), test_repealed_paragraph_stubs_are_dropped() (+4 more)

### Community 45 - "test_leakage.py"
Cohesion: 0.16
Nodes (13): pytest, test_documents, key(), Cross-tenant leakage (Phase G gate: 0 failures). Grows with G2 (documents) and…, G-A07's setup: A holds the Henderson workpapers; B can't find, see or remove…, ADR-5: graph-traversal reads hold public opinions only, so no tenant filter is…, test_a_malformed_job_id_is_a_404_not_an_error(), test_another_tenants_document_is_never_listed_searched_or_deletable() (+5 more)

### Community 47 - "TaxCite: Phase E exit report"
Cohesion: 0.09
Nodes (20): 1. Endpoints today, 4. Where text enters a prompt, 6. What is stored that may hold PII, 7. Threat table (golden adversarial rows), 8. Open from G0, G0: threat model and inventory, §9.3 recalibration, E0: where authority costs, before building (+12 more)

### Community 48 - "client"
Cohesion: 0.39
Nodes (7): create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), client(), subprocess

### Community 50 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 51 - "ecfr.py"
Cohesion: 0.20
Nodes (22): estimate_tokens(), make(), Block, blocks(), walk(), chunk_section(), make(), cite() (+14 more)

### Community 52 - "caselaw.py"
Cohesion: 0.16
Nodes (19): LTTextBox, fetch(), fold_numbers(), font_size(), get(), load_selection(), pages_label(), paragraphs() (+11 more)

### Community 53 - "sufficiency"
Cohesion: 0.33
Nodes (4): The gate's verdict on one part: {"part", "sufficient", "missing", "supports",…, sufficiency(), sufficiency_schema(), cost()

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "conn"
Cohesion: 0.08
Nodes (40): asyncio, BackgroundTasks, BaseModel, contextlib, delete, fastapi, fastapi_responses, get (+32 more)

### Community 58 - "aggregate"
Cohesion: 0.18
Nodes (12): aggregate(), Judged, None when there is nothing to score: a refusal, or an answer making no claim., Refusals are excluded from the mean and reported separately (§9.2). Averaging a…, judged(), An answer the extractor found nothing in would otherwise score 0/0., A row with one claim per entry in `supported`., Averaging refusals in either direction breaks the gate: 0 punishes the… (+4 more)

### Community 59 - "cli.py"
Cohesion: 0.16
Nodes (27): httpx, io, Namespace, backfill_authority(), create_tenant(), fetch(), fetch_usc(), ingest_case() (+19 more)

### Community 60 - "TaxCite: Phase F exit report"
Cohesion: 0.29
Nodes (6): Golden, scored once on the shipped pipeline, Open, for later phases, Reproducing, TaxCite: Phase F exit report, The gates, What Phase F got wrong

### Community 61 - "verify.py"
Cohesion: 0.09
Nodes (36): What exists, call_model(), cited_items(), parse_citations(), The sentences a structured answer can show, in order: text and at least one…, (answer text, sentences dropped) from arm E's JSON. Each sentence ends with its…, The section a citation belongs to, ignoring paragraph depth. '26 CFR…, Split the answer's citations three ways: exact, derived, unsupported. The three… (+28 more)

### Community 62 - "chunk.py"
Cohesion: 0.22
Nodes (8): dataclasses, re, expiry(), The unit every ingester produces and every store consumes., whole' or 'partly' when a regulation's own clause says its applicability ended…, §7805(e)(2): a temporary regulation issued after Nov. 20, 1988 expires within 3…, sunset(), test_expiry_reads_a_regulations_own_clause_against_the_snapshot_date()

### Community 64 - "test_usc_notes.py"
Cohesion: 0.26
Nodes (11): chunks(), effective(), fixture, Effective dates from the statutory notes (D4), on six real sections in…, test_a_new_section_dated_by_its_own_effective_date_note(), test_a_range_chunk_holds_its_subsections_whole(), test_amendment_below_the_label_found_after_a_heading(), test_an_exclusion_is_not_the_rule() (+3 more)

### Community 65 - "citations"
Cohesion: 0.16
Nodes (15): material(), Completeness over material sentences, and the share of answers that would…, Split outside brackets, at . ! ? followed by a space, never after an…, A line that states no claim: a section heading, a markdown title, a label…, sentences(), structural(), abstention(), completeness() (+7 more)

### Community 67 - "Hosted"
Cohesion: 0.32
Nodes (3): Hosted, A hosted embedding API in fastembed's shape (`embed` for chunks, `query_embed`…, ndarray

### Community 68 - "f4_hide.py"
Cohesion: 0.29
Nodes (10): base(), check_sheet(), main(), metrics(), Path, F4: one verified run, shown three ways, so the hiding unit is decided on…, The cached answer as the verifier saw it: every cited item shown., The cache entry as `unit` would show it. (+2 more)

### Community 69 - "decompose.py"
Cohesion: 0.10
Nodes (32): Reproducing, answer(), chunks(), citation_graph(), decompose(), Decomposition, gate(), merge() (+24 more)

### Community 71 - "Connection"
Cohesion: 0.29
Nodes (8): Connection, create_tenant(), held_at(), Create a tenant and return its API key. The caller commits., The tenant id an API key belongs to, or None., (key, text) TaxCite held for `citation` at `at`, current or since retired (D6)., _sha256(), tenant_for()

### Community 74 - "strip_boilerplate"
Cohesion: 0.36
Nodes (8): _normalise(), Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count(), edges(), Edges must never cover the whole page, or a 5-line page is deleted entirely., test_short_pages_never_lose_everything()

### Community 75 - "retrieve.py"
Cohesion: 0.19
Nodes (12): build(), collection_for(), main(), _models(), ADR-18 revisited: hosted embedding models against bge-base, on the golden set.…, retrieve.search loads its dense model by name; hosted names resolve here…, Index every chunk with one hosted model, skipping sources already complete (a…, score_one() (+4 more)

### Community 76 - "MissingCredentials"
Cohesion: 0.40
Nodes (5): MissingCredentials, RuntimeError, Raised instead of the SDK's generic auth error, which does not say what to set., Fail early and specifically. The SDK raises a generic TypeError at request…, _require_credentials()

### Community 77 - "e3_sample.py"
Cohesion: 0.33
Nodes (9): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze() (+1 more)

### Community 78 - "weigh"
Cohesion: 0.40
Nodes (6): level(), A hit's authority level (E2's profile; 0 when it has none), with E4's two…, E4's reorderings of the cross-encoder's list by authority. Nothing is dropped.…, weigh(), order(), rescore()

### Community 80 - "dehyphenate"
Cohesion: 0.50
Nodes (4): dehyphenate(), Join words split across a line break ("mo-\ntel" or "mo- tel" -> "motel"). A…, test_dehyphenate_joins_line_wrapped_words(), test_dehyphenate_keeps_real_hyphens()

### Community 81 - "stub_pipeline"
Cohesion: 0.50
Nodes (4): clean(), fixture, No model, no search: isolation lives in the API and retrieval, not the LLM., stub_pipeline()

## Knowledge Gaps
- **207 isolated node(s):** `taxcite`, `P01 `G-C20#0#0s``, `P02 `G-C05#1#0s``, `P03 `G-X19#1#0``, `P04 `G-X07#3#0s`` (+202 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 709 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `index.py`, `test_ecfr.py`, `irs_pubs.py`, `TaxCite — Status`, `ecfr.py`, `caselaw.py`, `usc.py`, `chunk.py`?**
  _High betweenness centrality (0.175) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `Hit` (e.g. with `base()` and `chunks()`) actually correct?**
  _`Hit` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `search()` (e.g. with `2. Store reads and writes` and `7. Threat table (golden adversarial rows)`) actually correct?**
  _`search()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `taxcite`, `P01 `G-C20#0#0s``, `P02 `G-C05#1#0s`` to the rest of the system?**
  _207 weakly-connected nodes found - possible documentation gaps or missing edges._