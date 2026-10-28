# Graph Report - TaxCite.nosync  (2026-10-28)

## Corpus Check
- 259 files · ~14,971,212 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: .jsonl 4, (none) 3, .xml 3)

## Summary
- 1493 nodes · 2859 edges · 77 communities (65 shown, 12 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 223 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8d7e4d1c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.py
- test_irs_pubs.py
- test_jobs.py
- T2: Ingest eCFR Title 26
- generate.py
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
- ragas_eval.py
- taxcite
- Collaborative Working Mode
- json
- decompose.py
- Postgres
- jobs.py
- test_verify.py
- retrieval.py
- test_metrics.py
- history
- TaxCite — Phase C exit report
- usc.py
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- f5_golden.py
- citations.py
- Plain-Module Package Layout
- flags
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- Hit
- usc_notes.py
- store_bench.py
- TaxCite — Phase D exit report
- test_store.py
- taxcite/__init__.py
- taxcite_ingest_caselaw
- TaxCite: Phase E exit report
- conn
- taxcite_ingest_citations
- TaxCite — Status
- ecfr.py
- caselaw.py
- appeal
- F4 verdict check
- F0 judge check
- taxcite_ingest_ecfr
- api.py
- fetch
- cli.py
- TaxCite: Phase F exit report
- verify.py
- store.py
- taxcite_ingest_irs_pubs
- call_model
- authorities
- taxcite_tracing
- Hosted
- is_appeal
- run
- tenant
- test_fetch_rejects_a_non_pdf
- taxcite
- taxcite_ingest
- aggregate
- snapshot.py
- MissingCredentials

## God Nodes (most connected - your core abstractions)
1. `F0 judge check` - 41 edges
2. `F5 reference check` - 41 edges
3. `Hit` - 35 edges
4. `search()` - 31 edges
5. `F4 verdict check` - 31 edges
6. `conn()` - 27 edges
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

## Communities (77 total, 12 thin omitted)

### Community 0 - "index.py"
Cohesion: 0.16
Nodes (18): psycopg_types_json, qdrant_client, QdrantClient, batched(), count(), create_collection(), edition(), point_id() (+10 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.08
Nodes (36): skipif, edition_year(), fetch(), _normalise(), page_texts(), parse(), Path, Sliding windows with overlap; a short page yields a single window. (+28 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.07
Nodes (36): opentelemetry, opentelemetry_sdk_trace, opentelemetry_sdk_trace_export, opentelemetry_sdk_trace_export_in_memory_span_exporter, SpanExporter, BrokenExporter, clean(), fixture (+28 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.16
Nodes (15): eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark, Harvard Caselaw Access Project, Per-Document-Type Chunker (§3.2), CourtListener (+7 more)

### Community 4 - "generate.py"
Cohesion: 0.10
Nodes (21): base64, dataclasses, inspect, os, answer_schema(), Answer a question, with and without retrieval. Two modes, because the §9…, The JSON schema for arm E: strict, so every field is required and nothing else…, (label, text) per "Part N: ..." section (F3), the unit ADR-15 hides. No… (+13 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.06
Nodes (45): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+37 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "f0_verify.py"
Cohesion: 0.07
Nodes (39): concurrent_futures, abstention(), agreement(), build(), check_sheet(), claim_text(), claim_unit(), contains() (+31 more)

### Community 8 - "test_usc.py"
Cohesion: 0.16
Nodes (14): chunks(), of(), fixture, Statute chunker tests against eight real sections in…, test_en_dash_section_number_becomes_a_hyphen(), test_heading_folds_into_its_first_child(), test_neighbouring_subsections_pack_into_a_range(), test_notes_are_not_text_and_source_credit_is_the_history() (+6 more)

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
Nodes (51): gi11(), hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, C5: A cites B and C; C cites D; E cites D; Z is unheld. Hops go either…, D3b: plain-English publications outrank the statute; a statute-only search puts… (+43 more)

### Community 19 - "test_index.py"
Cohesion: 0.22
Nodes (17): chunks(), ctx(), models_(), fixture, CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., sync(), test_a_broken_qdrant_still_raises() (+9 more)

### Community 20 - "ragas_eval.py"
Cohesion: 0.07
Nodes (46): datetime, Budget, CostCap, extract_claims(), judge_claims(), main(), parse_json(), pipeline_answer() (+38 more)

### Community 23 - "json"
Cohesion: 0.16
Nodes (15): dotenv, E4: apply the dev rules as written in tasks/todo.md, before looking at which…, cost_of(), estimate(), judge(), main(), ADR-11: choose the LLM by measuring answers, not by price alone. uv run python…, Rough spend before committing: RAG prompts dominate the input tokens. (+7 more)

### Community 24 - "decompose.py"
Cohesion: 0.08
Nodes (28): collections_abc, 3. Process-wide caches, functools, SparseVector, chunks(), citation_graph(), merge(), neighbors() (+20 more)

### Community 26 - "jobs.py"
Cohesion: 0.22
Nodes (11): 2. Store reads and writes, Redis, client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across…, Best-effort live notification. Redis is the delivery channel, never the record,… (+3 more)

### Community 27 - "test_verify.py"
Cohesion: 0.10
Nodes (16): no_recite(), fixture, Claim verification (F4), tested without spending money: the verifier call is…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, A verifier stub that answers by prompt: SYSTEM gets the next of…, Re-cite (F5b C3) ships on; tests that don't stub its call turn it off, and the…, routed(), structured_answer() (+8 more)

### Community 28 - "retrieval.py"
Cohesion: 0.09
Nodes (30): argparse, inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the… (+22 more)

### Community 29 - "test_metrics.py"
Cohesion: 0.08
Nodes (35): build(), collection_for(), main(), _models(), ADR-18 revisited: hosted embedding models against bge-base, on the golden set.…, retrieve.search loads its dense model by name; hosted names resolve here…, Index every chunk with one hosted model, skipping sources already complete (a…, score_one() (+27 more)

### Community 30 - "history"
Cohesion: 0.19
Nodes (13): FullCaseCitation, full_cites(), history(), label(), The year in the parenthetical right after the cite. eyecite's own guess can…, Explanatory parentheticals push "aff'd" past the window: "113 T.C. 254 (1999)…, The appeal as one stable string, "560 F.3d 620 (ca7 2009)": no case name or pin…, (opinion, kind, by) from subsequent history in a passage. by is the appellate… (+5 more)

### Community 31 - "TaxCite — Phase C exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+4 more)

### Community 32 - "usc.py"
Cohesion: 0.25
Nodes (17): blocks(), child_text(), chunk_section(), clean(), designation(), lead_in(), parse(), provision_blocks() (+9 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "f5_golden.py"
Cohesion: 0.07
Nodes (50): f1(), headings(), material(), Each cached chunk's heading, which synthesis saw ("[citation] (heading)") but…, On the not-supported class: what the verifier exists to catch. `supported` is…, Completeness over material sentences, and the share of answers that would…, Split outside brackets, at . ! ? followed by a space, never after an…, A line that states no claim: a section heading, a markdown title, a label… (+42 more)

### Community 35 - "citations.py"
Cohesion: 0.19
Nodes (13): eyecite, eyecite_models, logging, cites(), kind(), normalize(), own(), Citation and treatment edges between Tax Court opinions: two Postgres tables,… (+5 more)

### Community 37 - "flags"
Cohesion: 0.20
Nodes (12): Open problems handed on, load_selection(), The selection is cached so the corpus stays fixed while new opinions are filed., flag(), flags(), load(), opinion_chunks(), datetime (+4 more)

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "search"
Cohesion: 0.11
Nodes (25): Filter, edition_filter(), Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, One source or several; several is how B7 routes a sub-query to the corpora that…, Keep chunks with no edition (everything but publications, and undated…, search(), source_filter(), hit() (+17 more)

### Community 40 - "Hit"
Cohesion: 0.18
Nodes (14): level(), (sub-query, its chunks) for the synthesis prompt, limited to `keep` if given.…, A hit's authority level (E2's profile; 0 when it has none), with E4's two…, E4's reorderings of the cross-encoder's list by authority. Nothing is dropped.…, weigh(), order(), rescore(), answer_from_hits() (+6 more)

### Community 41 - "usc_notes.py"
Cohesion: 0.06
Nodes (43): amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes(), own_designation() (+35 more)

### Community 42 - "store_bench.py"
Cohesion: 0.23
Nodes (11): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+3 more)

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "test_store.py"
Cohesion: 0.19
Nodes (16): chunks(), parametrize, Transaction time (D6): an amendment rewrites a chunk in place; the old text…, test_a_dropped_paragraph_is_retired_by_the_sweep(), test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(), test_authority_profile_comes_from_source_and_citation_form(), test_excluded_rows_are_stored_but_not_counted_as_indexable(), test_expiry_reads_a_regulations_own_clause_against_the_snapshot_date() (+8 more)

### Community 45 - "taxcite/__init__.py"
Cohesion: 0.10
Nodes (23): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze() (+15 more)

### Community 47 - "TaxCite: Phase E exit report"
Cohesion: 0.17
Nodes (11): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E2 and E3: the metadata, and the check that found law the parser didn't know, E4: the rerank, E5: authority in answers, Failures, with examples, Reproducing (+3 more)

### Community 48 - "conn"
Cohesion: 0.27
Nodes (10): get, get_query(), Server-sent events for one job. Replays whatever the record already holds, then…, stream_events(), events(), get(), The job, if it exists and is this tenant's. Another tenant's job is None,…, StreamingResponse (+2 more)

### Community 50 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 51 - "ecfr.py"
Cohesion: 0.18
Nodes (24): estimate_tokens(), §7805(e)(2): a temporary regulation issued after Nov. 20, 1988 expires within 3…, sunset(), make(), Block, blocks(), walk(), chunk_section() (+16 more)

### Community 52 - "caselaw.py"
Cohesion: 0.11
Nodes (30): collections, LTTextBox, pdfminer_high_level, pdfminer_layout, re, Chunk, The unit every ingester produces and every store consumes., Make `part` a running count per citation, so `key` is unique by construction.… (+22 more)

### Community 53 - "appeal"
Cohesion: 0.25
Nodes (9): appeal(), appeal_label(), cached(), get(), Client, Path, One format for both sources, so a reader sees the same appeal the same way., A response cached with the time it was fetched: re-running from cache must not… (+1 more)

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "api.py"
Cohesion: 0.09
Nodes (24): asyncio, BackgroundTasks, BaseModel, contextlib, fastapi, fastapi_responses, post, psycopg (+16 more)

### Community 58 - "fetch"
Cohesion: 0.40
Nodes (5): fetch(), fetch_usc(), Path, Title 26 USLM XML for a release point (default: the current one), cached on…, Download one part (or a single section) of Title 26, cached on disk. The API…

### Community 59 - "cli.py"
Cohesion: 0.22
Nodes (23): Connection, io, Namespace, backfill_authority(), create_tenant(), ingest_case(), ingest_ecfr(), ingest_pubs() (+15 more)

### Community 60 - "TaxCite: Phase F exit report"
Cohesion: 0.25
Nodes (7): Golden, scored once on the shipped pipeline, How the phase went, Open, for later phases, Reproducing, TaxCite: Phase F exit report, The gates, What Phase F got wrong

### Community 61 - "verify.py"
Cohesion: 0.10
Nodes (37): What exists, Answer, cited_items(), _generate_structured(), parse_citations(), The sentences a structured answer can show, in order: text and at least one…, (answer text, sentences dropped) from arm E's JSON. Each sentence ends with its…, Says INSUFFICIENT EVIDENCE and cites nothing. F3: a cited answer that flags one… (+29 more)

### Community 62 - "store.py"
Cohesion: 0.16
Nodes (17): hashlib, secrets, authority(), expiry(), The chunk's authority profile (E2): from its source and the citation's form,…, `source_revision` where the ingester had none (E2): what `as_of` already…, whole' or 'partly' when a regulation's own clause says its applicability ended…, revision() (+9 more)

### Community 64 - "call_model"
Cohesion: 0.22
Nodes (8): The gate's verdict on one part: {"part", "sufficient", "missing", "supports",…, sufficiency(), sufficiency_schema(), call_model(), cost(), Fail early and specifically. The SDK raises a generic TypeError at request…, One completion. Returns (text, input_tokens, output_tokens). The two providers…, _require_credentials()

### Community 65 - "authorities"
Cohesion: 0.15
Nodes (13): 1. Endpoints today, 4. Where text enters a prompt, 5. Where text reaches the user, 6. What is stored that may hold PII, 7. Threat table (golden adversarial rows), 8. Open from G0, G0: threat model and inventory, What exists (+5 more)

### Community 67 - "Hosted"
Cohesion: 0.32
Nodes (3): Hosted, A hosted embedding API in fastembed's shape (`embed` for chunks, `query_embed`…, ndarray

### Community 68 - "is_appeal"
Cohesion: 0.32
Nodes (8): is_appeal(), party(), petitioners(), The petitioners' names alone: "Estate of James E. Caan, Deceased, …,…, Family names in a joint caption. "C. Michael & Gwendolyn E. Willock" is one…, A caseName query for the appellate caption: surnames for people ("Donald B. &…, Same-name appeals are common (C1: three unrelated Michaels for Willock). A real…, surnames()

### Community 69 - "run"
Cohesion: 0.18
Nodes (18): Reproducing, answer(), decompose(), Decomposition, gate(), One structured-output call (ADR-11). Temperature 0 and a fixed seed, so a re-…, Search once per sub-query, filtered to the sources its kind allows. Fills…, (parts to synthesize, (label, missing) for parts skipped, every verdict). A… (+10 more)

### Community 70 - "tenant"
Cohesion: 0.29
Nodes (7): Every route but /health belongs to a tenant, resolved from its API key (Phase…, tenant(), create_tenant(), Create a tenant and return its API key. The caller commits., The tenant id an API key belongs to, or None., _sha256(), tenant_for()

### Community 74 - "aggregate"
Cohesion: 0.18
Nodes (12): aggregate(), Judged, None when there is nothing to score: a refusal, or an answer making no claim., Refusals are excluded from the mean and reported separately (§9.2). Averaging a…, judged(), An answer the extractor found nothing in would otherwise score 0/0., A row with one claim per entry in `supported`., Averaging refusals in either direction breaks the gate: 0 punishes the… (+4 more)

### Community 75 - "snapshot.py"
Cohesion: 0.33
Nodes (8): create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), httpx, client(), subprocess

### Community 76 - "MissingCredentials"
Cohesion: 0.67
Nodes (3): MissingCredentials, RuntimeError, Raised instead of the SDK's generic auth error, which does not say what to set.

## Knowledge Gaps
- **207 isolated node(s):** `taxcite`, `P01 `G-C20#0#0s``, `P02 `G-C05#1#0s``, `P03 `G-X19#1#0``, `P04 `G-X07#3#0s`` (+202 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 703 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `caselaw.py` to `index.py`, `test_irs_pubs.py`, `usc.py`, `test_ecfr.py`, `usc_notes.py`, `TaxCite — Status`, `ecfr.py`, `store.py`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `Hit` (e.g. with `base()` and `chunks()`) actually correct?**
  _`Hit` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `search()` (e.g. with `2. Store reads and writes` and `7. Threat table (golden adversarial rows)`) actually correct?**
  _`search()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `taxcite`, `P01 `G-C20#0#0s``, `P02 `G-C05#1#0s`` to the rest of the system?**
  _207 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_irs_pubs.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08108108108108109 - nodes in this community are weakly interconnected._