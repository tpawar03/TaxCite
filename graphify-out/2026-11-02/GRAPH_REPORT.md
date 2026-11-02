# Graph Report - TaxCite.nosync  (2026-11-02)

## Corpus Check
- 267 files · ~15,010,117 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: .jsonl 6, (none) 3, .xml 3)

## Summary
- 1577 nodes · 3077 edges · 81 communities (68 shown, 13 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 242 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `01c57219`
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
- f0_verify.py
- run
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
- ecfr.py
- TaxCite — Phase C exit report
- usc.py
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- client
- citations.py
- Plain-Module Package Layout
- format_sources
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- conn
- usc_notes.py
- store_bench.py
- TaxCite — Phase D exit report
- test_store.py
- test_documents.py
- taxcite_ingest_caselaw
- TaxCite: Phase E exit report
- index.py
- taxcite_ingest_citations
- TaxCite — Status
- estimate_tokens
- paragraphs
- f5_golden.py
- F4 verdict check
- F0 judge check
- taxcite_ingest_ecfr
- designations
- authorities
- cli.py
- TaxCite: Phase F exit report
- verify.py
- split_sections
- taxcite
- taxcite_ingest
- taxcite_ingest_irs_pubs
- e3_sample.py
- Hosted
- f4_hide.py
- Hit
- score_one
- store.py
- section_of
- main
- judged
- taxcite_tracing
- G3 step 4: client facts from an uploaded document (dev, tracked not gated)
- _brief
- in_scope
- generate.py
- test_documents

## God Nodes (most connected - your core abstractions)
1. `F0 judge check` - 41 edges
2. `F5 reference check` - 41 edges
3. `Hit` - 39 edges
4. `search()` - 34 edges
5. `conn()` - 34 edges
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
- `5. Where text reaches the user` --references--> `answer()`  [INFERRED]
  eval/results/g0-threat-model.md → src/taxcite/decompose.py
- `G3 step 4: five dev rows with the client's facts in a document (draft, for your review)` --references--> `answer()`  [INFERRED]
  eval/results/g3-dev-rows-draft.md → src/taxcite/decompose.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]

## Communities (81 total, 13 thin omitted)

### Community 0 - "client_docs.py"
Cohesion: 0.11
Nodes (24): shutil, create_collection(), create_tables(), documents(), ingest(), kind(), ocr(), page_texts() (+16 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.06
Nodes (42): skipif, dehyphenate(), edition_year(), fetch(), _normalise(), page_texts(), parse(), Path (+34 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.06
Nodes (37): opentelemetry_sdk_trace, opentelemetry_sdk_trace_export, opentelemetry_sdk_trace_export_in_memory_span_exporter, SpanExporter, BrokenExporter, clean(), fixture, Job record and SSE transport (ADR-9), with the pipeline stubbed. (+29 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.16
Nodes (15): eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark, Harvard Caselaw Access Project, Per-Document-Type Chunker (§3.2), CourtListener (+7 more)

### Community 4 - "MissingCredentials"
Cohesion: 0.40
Nodes (5): MissingCredentials, RuntimeError, Raised instead of the SDK's generic auth error, which does not say what to set., Fail early and specifically. The SDK raises a generic TypeError at request…, _require_credentials()

### Community 5 - "test_ecfr.py"
Cohesion: 0.11
Nodes (21): of(), Chunker tests against nine real sections in tests/fixtures/ecfr_sample.xml.…, A section can embed its own outline (§1.61-21 does); it must not create new…, Two chunks reaching the same citation get distinct parts, so keys cannot…, eCFR ships its own citation string in hierarchy_metadata; ours must agree., test_cita_is_kept_out_of_the_text(), test_example_text_in_pspace_is_captured(), test_large_table_is_recorded_with_a_reason() (+13 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "f0_verify.py"
Cohesion: 0.08
Nodes (36): concurrent_futures, abstention(), agreement(), build(), check_sheet(), claim_text(), claim_unit(), contains() (+28 more)

### Community 8 - "run"
Cohesion: 0.09
Nodes (30): 2. Store reads and writes, G3 step 4: five dev rows with the client's facts in a document (draft, for your review), Reproducing, Open problems handed on, answer(), citation_graph(), decompose(), gate() (+22 more)

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
Nodes (52): prompt(), gi11(), hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, C5: A cites B and C; C cites D; E cites D; Z is unheld. Hops go either… (+44 more)

### Community 19 - "test_index.py"
Cohesion: 0.22
Nodes (17): chunks(), ctx(), models_(), fixture, CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., sync(), test_a_broken_qdrant_still_raises() (+9 more)

### Community 20 - "ragas_eval.py"
Cohesion: 0.06
Nodes (51): judge(), Judge each pair against `field`'s chunks into `out`. The main pass reads every…, aggregate(), Budget, CostCap, extract_claims(), judge_claims(), Judged (+43 more)

### Community 23 - "retrieval.py"
Cohesion: 0.11
Nodes (27): collections, datetime, dotenv, _models(), ADR-18 revisited: hosted embedding models against bge-base, on the golden set.…, retrieve.search loads its dense model by name; hosted names resolve here…, cost_of(), estimate() (+19 more)

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
Cohesion: 0.33
Nodes (10): inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the…, Part 2: which authority fields have more than one value here, and from where. (+2 more)

### Community 29 - "test_metrics.py"
Cohesion: 0.12
Nodes (23): mrr(), ndcg_at_k(), recall_at_k(), math, parametrize, The metrics must be right before any number computed with them means anything., Instruction is not a guarantee; the model sometimes wraps its JSON in prose., C6: three chunks share "T.C. Memo. 2023-128, at *15" and only #3 states the… (+15 more)

### Community 30 - "ecfr.py"
Cohesion: 0.18
Nodes (18): Chunk, Make `part` a running count per citation, so `key` is unique by construction.…, §7805(e)(2): a temporary regulation issued after Nov. 20, 1988 expires within 3…, renumber(), sunset(), blocks(), walk(), chunk_section() (+10 more)

### Community 31 - "TaxCite — Phase C exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+4 more)

### Community 32 - "usc.py"
Cohesion: 0.27
Nodes (16): blocks(), child_text(), chunk_section(), clean(), designation(), lead_in(), parse(), provision_blocks() (+8 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "client"
Cohesion: 0.48
Nodes (6): create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), client()

### Community 35 - "citations.py"
Cohesion: 0.07
Nodes (52): eyecite, eyecite_models, FullCaseCitation, logging, load_selection(), The selection is cached so the corpus stays fixed while new opinions are filed., appeal(), appeal_label() (+44 more)

### Community 37 - "format_sources"
Cohesion: 0.33
Nodes (6): authority_label(), effective_note(), format_sources(), D7: flag statute text whose latest amendment took effect after the question's…, A source's text as every prompt shows it. A client document is the questioner's…, source_text()

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "search"
Cohesion: 0.09
Nodes (30): build(), collection_for(), main(), Index every chunk with one hosted model, skipping sources already complete (a…, Filter, edition_filter(), Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, One source or several; several is how B7 routes a sub-query to the corpora that… (+22 more)

### Community 40 - "conn"
Cohesion: 0.07
Nodes (42): asyncio, BackgroundTasks, BaseModel, contextlib, fastapi, fastapi_responses, get, post (+34 more)

### Community 41 - "usc_notes.py"
Cohesion: 0.06
Nodes (43): amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes(), own_designation() (+35 more)

### Community 42 - "store_bench.py"
Cohesion: 0.13
Nodes (17): E4: apply the dev rules as written in tasks/todo.md, before looking at which…, load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run… (+9 more)

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "test_store.py"
Cohesion: 0.18
Nodes (17): chunks(), parametrize, Transaction time (D6): an amendment rewrites a chunk in place; the old text…, test_a_dropped_paragraph_is_retired_by_the_sweep(), test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(), test_authority_profile_comes_from_source_and_citation_form(), test_excluded_rows_are_stored_but_not_counted_as_indexable(), test_expiry_reads_a_regulations_own_clause_against_the_snapshot_date() (+9 more)

### Community 45 - "test_documents.py"
Cohesion: 0.07
Nodes (45): fastapi_testclient, needs_tesseract, ask(), clean(), pdf(), png(), fixture, Client-document ingestion (G2). Fixtures are built here, not stored: each is a… (+37 more)

### Community 47 - "TaxCite: Phase E exit report"
Cohesion: 0.17
Nodes (11): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E2 and E3: the metadata, and the check that found law the parser didn't know, E4: the rerank, E5: authority in answers, Failures, with examples, Reproducing (+3 more)

### Community 48 - "index.py"
Cohesion: 0.13
Nodes (25): QdrantClient, authority(), expiry(), The unit every ingester produces and every store consumes., The chunk's authority profile (E2): from its source and the citation's form,…, `source_revision` where the ingester had none (E2): what `as_of` already…, whole' or 'partly' when a regulation's own clause says its applicability ended…, revision() (+17 more)

### Community 50 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 51 - "estimate_tokens"
Cohesion: 0.18
Nodes (18): estimate_tokens(), pages_label(), parse(), make(), Paragraphs packed up to MAX_TOKENS, each chunk opening with the previous…, Block, make(), cite() (+10 more)

### Community 52 - "paragraphs"
Cohesion: 0.18
Nodes (13): LTTextBox, fetch(), fold_numbers(), font_size(), get(), paragraphs(), Client, Path (+5 more)

### Community 53 - "f5_golden.py"
Cohesion: 0.09
Nodes (42): f1(), headings(), material(), Each cached chunk's heading, which synthesis saw ("[citation] (heading)") but…, On the not-supported class: what the verifier exists to catch. `supported` is…, Completeness over material sentences, and the share of answers that would…, Split outside brackets, at . ! ? followed by a space, never after an…, A line that states no claim: a section heading, a markdown title, a label… (+34 more)

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "designations"
Cohesion: 0.17
Nodes (16): Element, designations(), level_of(), 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.…, Level-1 and level-2 designations a paragraph opens with. Read from raw text,…, p(), E2: §1.988-1T says "The applicability of this section expires on December 6,…, E3: §7805(e)(2) ends a post-1988 temporary regulation within 3 years, whatever… (+8 more)

### Community 58 - "authorities"
Cohesion: 0.12
Nodes (18): 1. Endpoints today, 3. Process-wide caches, 4. Where text enters a prompt, 5. Where text reaches the user, 6. What is stored that may hold PII, 7. Threat table (golden adversarial rows), 8. Open from G0, G0: threat model and inventory (+10 more)

### Community 59 - "cli.py"
Cohesion: 0.16
Nodes (27): io, Namespace, os, backfill_authority(), create_tenant(), fetch(), fetch_usc(), ingest_case() (+19 more)

### Community 60 - "TaxCite: Phase F exit report"
Cohesion: 0.25
Nodes (7): Golden, scored once on the shipped pipeline, How the phase went, Open, for later phases, Reproducing, TaxCite: Phase F exit report, The gates, What Phase F got wrong

### Community 61 - "verify.py"
Cohesion: 0.09
Nodes (38): What exists, Answer, answer_from_hits(), call_model(), _generate(), _generate_structured(), parse_citations(), (answer text, sentences dropped) from arm E's JSON. Each sentence ends with its… (+30 more)

### Community 66 - "e3_sample.py"
Cohesion: 0.29
Nodes (10): argparse, caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows() (+2 more)

### Community 67 - "Hosted"
Cohesion: 0.32
Nodes (3): Hosted, A hosted embedding API in fastembed's shape (`embed` for chunks, `query_embed`…, ndarray

### Community 68 - "f4_hide.py"
Cohesion: 0.29
Nodes (10): base(), check_sheet(), main(), metrics(), Path, F4: one verified run, shown three ways, so the hiding unit is decided on…, The cached answer as the verifier saw it: every cited item shown., The cache entry as `unit` would show it. (+2 more)

### Community 69 - "Hit"
Cohesion: 0.11
Nodes (20): chunks(), client_hits(), Decomposition, level(), merge(), parse(), (sub-query, its chunks) for the synthesis prompt, limited to `keep` if given.…, (sub-queries, as_of, fallback reason). Never raises. A decomposition that… (+12 more)

### Community 70 - "score_one"
Cohesion: 0.22
Nodes (10): What exists, authority_facts(), first_hits(), Path, 0-based rank at which each group is first satisfied, for the groups that are. A…, E1's tag on one row (E4): does the controlling source reach its target rank (1,…, score_one(), Gold (+2 more)

### Community 71 - "store.py"
Cohesion: 0.17
Nodes (16): Connection, hashlib, psycopg, psycopg_types_json, secrets, create_tenant(), held_at(), datetime (+8 more)

### Community 72 - "section_of"
Cohesion: 0.22
Nodes (9): score_one(), groups(), ["a", ["b", "c"]] -> [{"a"}, {"b", "c"}]; also accepts a plain set of citations., content_words(), main(), The section a citation belongs to, ignoring paragraph depth. '26 CFR…, section_of(), test_section_of_strips_paragraph_markers() (+1 more)

### Community 73 - "main"
Cohesion: 0.25
Nodes (3): main(), needs_case_law(), A row whose gold includes an opinion: routing must send a sub-query to the case…

### Community 74 - "judged"
Cohesion: 0.25
Nodes (8): judged(), An answer the extractor found nothing in would otherwise score 0/0., A row with one claim per entry in `supported`., Averaging refusals in either direction breaks the gate: 0 punishes the…, test_a_refusal_is_not_scored_as_zero_or_as_one(), test_aggregate_counts_claims_and_unsupported_claims(), test_an_answer_with_no_claims_is_reported_not_averaged(), test_faithfulness_is_the_supported_ratio()

### Community 76 - "G3 step 4: client facts from an uploaded document (dev, tracked not gated)"
Cohesion: 0.40
Nodes (4): Finding 1: taking facts out of the question changes public retrieval (D55), Finding 2: a conclusion can state law on a client document's authority (D56), G3 step 4: client facts from an uploaded document (dev, tracked not gated), What this does not measure

### Community 77 - "_brief"
Cohesion: 0.40
Nodes (5): _brief(), _json(), A readable, bounded copy of a step's arguments or result., wrap(), inner()

### Community 78 - "in_scope"
Cohesion: 0.67
Nodes (3): in_scope(), True when a section is one of these prefixes, or a numbered child of one.…, test_in_scope_matches_children_but_not_longer_numbers()

### Community 80 - "generate.py"
Cohesion: 0.11
Nodes (22): base64, collections_abc, dataclasses, functools, inspect, opentelemetry, Split a question into typed sub-queries, and route each to the sources that can…, The gate's verdict on one part: {"part", "sufficient", "missing", "supports",… (+14 more)

## Knowledge Gaps
- **209 isolated node(s):** `taxcite`, `P01 `G-C20#0#0s``, `P02 `G-C05#1#0s``, `P03 `G-X19#1#0``, `P04 `G-X07#3#0s`` (+204 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 732 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `ecfr.py` to `usc.py`, `test_irs_pubs.py`, `test_ecfr.py`, `store.py`, `usc_notes.py`, `index.py`, `TaxCite — Status`, `estimate_tokens`, `retrieval.py`?**
  _High betweenness centrality (0.175) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `Hit` (e.g. with `base()` and `chunks()`) actually correct?**
  _`Hit` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `search()` (e.g. with `2. Store reads and writes` and `7. Threat table (golden adversarial rows)`) actually correct?**
  _`search()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 32 INFERRED edges - model-reasoned connections that need verification._
- **What connects `taxcite`, `P01 `G-C20#0#0s``, `P02 `G-C05#1#0s`` to the rest of the system?**
  _209 weakly-connected nodes found - possible documentation gaps or missing edges._