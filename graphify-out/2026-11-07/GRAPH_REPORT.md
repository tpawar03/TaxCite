# Graph Report - TaxCite.nosync  (2026-11-07)

## Corpus Check
- 281 files · ~15,088,460 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 17 file(s) not represented in the graph (top: .jsonl 9, (none) 3, .xml 3)

## Summary
- 1615 nodes · 3137 edges · 81 communities (70 shown, 11 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 241 edges (avg confidence: 0.89)
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
- embed_bench.py
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
- appeal
- test_usc.py
- Postgres
- jobs.py
- test_verify.py
- retrieval.py
- test_metrics.py
- designations
- TaxCite — Phase C exit report
- store_bench.py
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- test_temporal.py
- Chunk
- Plain-Module Package Layout
- generate.py
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- api.py
- usc_notes.py
- parse
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
- answer
- cli.py
- TaxCite: Phase F exit report
- G3 step 4: client facts from an uploaded document (dev, tracked not gated)
- decompose.py
- tracing.py
- e0_authority.py
- json
- stream_events
- Hosted
- no_recite
- test_store.py
- Checkpoint 2 demo: one question per tenant (G3)
- split_sections
- fixture
- citations.py
- in_scope
- e3_sample.py
- g4-corpus-draft.md
- client
- parse
- test_fetch_rejects_a_non_pdf
- caselaw.py

## God Nodes (most connected - your core abstractions)
1. `F0 judge check` - 41 edges
2. `F5 reference check` - 41 edges
3. `conn()` - 36 edges
4. `search()` - 31 edges
5. `F4 verdict check` - 31 edges
6. `Answer` - 26 edges
7. `Hit` - 26 edges
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
- `2. Store reads and writes` --references--> `citations()`  [INFERRED]
  eval/results/g0-threat-model.md → src/taxcite/generate.py
- `5. Where text reaches the user` --references--> `citations()`  [INFERRED]
  eval/results/g0-threat-model.md → src/taxcite/generate.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]

## Communities (81 total, 11 thin omitted)

### Community 0 - "client_docs.py"
Cohesion: 0.10
Nodes (28): io, create_collection(), create_tables(), delete(), documents(), ingest(), kind(), ocr() (+20 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.14
Nodes (20): _normalise(), Sliding windows with overlap; a short page yields a single window., Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count(), edges(), windows() (+12 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.06
Nodes (38): opentelemetry, opentelemetry_sdk_trace, opentelemetry_sdk_trace_export, opentelemetry_sdk_trace_export_in_memory_span_exporter, SpanExporter, BrokenExporter, clean(), fixture (+30 more)

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

### Community 7 - "embed_bench.py"
Cohesion: 0.17
Nodes (13): build(), collection_for(), main(), _models(), ADR-18 revisited: hosted embedding models against bge-base, on the golden set.…, retrieve.search loads its dense model by name; hosted names resolve here…, Index every chunk with one hosted model, skipping sources already complete (a…, score_one() (+5 more)

### Community 8 - "store.py"
Cohesion: 0.15
Nodes (15): hashlib, psycopg, psycopg_types_json, secrets, Every route but /health belongs to a tenant, resolved from its API key (Phase…, tenant(), create_tenant(), held_at() (+7 more)

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
Nodes (53): gi11(), hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, C5: A cites B and C; C cites D; E cites D; Z is unheld. Hops go either…, D3b: plain-English publications outrank the statute; a statute-only search puts… (+45 more)

### Community 19 - "test_index.py"
Cohesion: 0.22
Nodes (17): chunks(), ctx(), models_(), fixture, CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., sync(), test_a_broken_qdrant_still_raises() (+9 more)

### Community 20 - "ragas_eval.py"
Cohesion: 0.10
Nodes (29): judge(), Judge each pair against `field`'s chunks into `out`. The main pass reads every…, aggregate(), Budget, CostCap, extract_claims(), judge_claims(), Judged (+21 more)

### Community 23 - "appeal"
Cohesion: 0.17
Nodes (15): appeal(), cached(), get(), is_appeal(), party(), petitioners(), Client, Path (+7 more)

### Community 24 - "test_usc.py"
Cohesion: 0.16
Nodes (14): chunks(), of(), fixture, Statute chunker tests against eight real sections in…, test_en_dash_section_number_becomes_a_hyphen(), test_heading_folds_into_its_first_child(), test_neighbouring_subsections_pack_into_a_range(), test_notes_are_not_text_and_source_credit_is_the_history() (+6 more)

### Community 26 - "jobs.py"
Cohesion: 0.16
Nodes (18): 2. Store reads and writes, Reproducing, Redis, F2: every part judged insufficient before synthesis. A refusal with what each…, skipped_only(), flags(), Treatment flags for the opinions an answer cites. Fails open: if the table…, client() (+10 more)

### Community 27 - "test_verify.py"
Cohesion: 0.11
Nodes (12): pytest, Claim verification (F4), tested without spending money: the verifier call is…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, A verifier stub that answers by prompt: SYSTEM gets the next of…, routed(), structured_answer(), test_a_conclusion_is_shown_first_only_when_it_follows_from_the_sentences_that_passed(), test_a_note_about_a_missing_detail_survives_when_its_part_is_shown() (+4 more)

### Community 28 - "retrieval.py"
Cohesion: 0.10
Nodes (23): authority_facts(), cached_decompose(), first_hits(), groups(), main(), needs_case_law(), Path, Score retrieval against the pilot set: the first rungs of the §9 ablation… (+15 more)

### Community 29 - "test_metrics.py"
Cohesion: 0.09
Nodes (32): mrr(), ndcg_at_k(), recall_at_k(), judged(), parametrize, The metrics must be right before any number computed with them means anything., An answer the extractor found nothing in would otherwise score 0/0., Instruction is not a guarantee; the model sometimes wraps its JSON in prose. (+24 more)

### Community 30 - "designations"
Cohesion: 0.24
Nodes (12): Element, designations(), level_of(), 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.…, Level-1 and level-2 designations a paragraph opens with. Read from raw text,…, p(), test_compact_two_level_designation(), test_designation_split_by_italic_heading() (+4 more)

### Community 31 - "TaxCite — Phase C exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+4 more)

### Community 32 - "store_bench.py"
Cohesion: 0.23
Nodes (11): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+3 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "test_temporal.py"
Cohesion: 0.13
Nodes (15): as_of_match(), kappa(), passed(), Year-level match of the plan's as-of against the row's tax year. None = not…, Cohen's kappa for two raters over the same items., Per sample index: rates over the rows, first judge repeat (E5). Conflict and…, sample_summary(), parametrize (+7 more)

### Community 35 - "Chunk"
Cohesion: 0.24
Nodes (12): Chunk, estimate_tokens(), Make `part` a running count per citation, so `key` is unique by construction.…, renumber(), pages_label(), parse(), make(), Paragraphs packed up to MAX_TOKENS, each chunk opening with the previous… (+4 more)

### Community 37 - "generate.py"
Cohesion: 0.14
Nodes (24): 4. Where text enters a prompt, Hit, answer_from_groups(), answer_from_hits(), answer_schema(), authority_label(), call_model(), cost() (+16 more)

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "search"
Cohesion: 0.10
Nodes (28): Filter, SparseVector, edition_filter(), embed(), Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, Cached: every search in one pipeline run uses the original question (only the…, One source or several; several is how B7 routes a sub-query to the corpora that…, Keep chunks with no edition (everything but publications, and undated… (+20 more)

### Community 40 - "api.py"
Cohesion: 0.09
Nodes (27): asyncio, BackgroundTasks, BaseModel, contextlib, fastapi, fastapi_responses, post, pydantic (+19 more)

### Community 41 - "usc_notes.py"
Cohesion: 0.06
Nodes (43): amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes(), own_designation() (+35 more)

### Community 42 - "parse"
Cohesion: 0.14
Nodes (16): skipif, edition_year(), fetch(), page_texts(), parse(), Path, Every chunk in one publication PDF., Download one publication, cached on disk. `delay` rate-limits bulk fetches. (+8 more)

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "ecfr.py"
Cohesion: 0.22
Nodes (19): Block, blocks(), walk(), chunk_section(), cite(), clean(), pack(), flush() (+11 more)

### Community 45 - "test_documents.py"
Cohesion: 0.06
Nodes (55): fastapi_testclient, fixture, needs_tesseract, shutil, taxcite_ingest, ask(), clean(), pdf() (+47 more)

### Community 47 - "verify.py"
Cohesion: 0.10
Nodes (38): What exists, Answer, cited_items(), The sentences a structured answer can show, in order: text and at least one…, (answer text, sentences dropped) from arm E's JSON. Each sentence ends with its…, Says INSUFFICIENT EVIDENCE and cites nothing. F3: a cited answer that flags one…, A source's text as every prompt shows it. A client document is the questioner's…, Answer a question with retrieval (`rag`) or without it (`closed_book`). (+30 more)

### Community 48 - "index.py"
Cohesion: 0.10
Nodes (29): QdrantClient, authority(), expiry(), The chunk's authority profile (E2): from its source and the citation's form,…, `source_revision` where the ingester had none (E2): what `as_of` already…, whole' or 'partly' when a regulation's own clause says its applicability ended…, §7805(e)(2): a temporary regulation issued after Nov. 20, 1988 expires within 3…, revision() (+21 more)

### Community 50 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 51 - "f0_verify.py"
Cohesion: 0.09
Nodes (31): concurrent_futures, abstention(), agreement(), check_sheet(), claim_unit(), contains(), f1(), call() (+23 more)

### Community 52 - "TaxCite: Phase E exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E2 and E3: the metadata, and the check that found law the parser didn't know, E4: the rerank, E5: authority in answers, Failures, with examples, Open problems handed on (+4 more)

### Community 53 - "f5_golden.py"
Cohesion: 0.06
Nodes (55): build(), claim_text(), headings(), kind_of(), material(), The sub-query kind a citation belongs to: what F3's sections would be. Two sub-…, Tune half / report half, by question, so near-identical answers of one question…, Each cached chunk's heading, which synthesis saw ("[citation] (heading)") but… (+47 more)

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "usc.py"
Cohesion: 0.33
Nodes (13): blocks(), child_text(), clean(), designation(), lead_in(), provision_blocks(), Parse US Code Title 26 (USLM XML from uscode.house.gov) into citation-anchored…, Text with whitespace collapsed. A table becomes one line per row; the largest… (+5 more)

### Community 58 - "answer"
Cohesion: 0.14
Nodes (14): 1. Endpoints today, 5. Where text reaches the user, 6. What is stored that may hold PII, 7. Threat table (golden adversarial rows), 8. Open from G0, G0: threat model and inventory, G3 step 4: five dev rows with the client's facts in a document (draft, for your review), What exists (+6 more)

### Community 59 - "cli.py"
Cohesion: 0.17
Nodes (31): Connection, Namespace, backfill_authority(), create_tenant(), fetch(), fetch_usc(), ingest_case(), ingest_ecfr() (+23 more)

### Community 60 - "TaxCite: Phase F exit report"
Cohesion: 0.25
Nodes (7): Golden, scored once on the shipped pipeline, How the phase went, Open, for later phases, Reproducing, TaxCite: Phase F exit report, The gates, What Phase F got wrong

### Community 61 - "G3 step 4: client facts from an uploaded document (dev, tracked not gated)"
Cohesion: 0.40
Nodes (4): Finding 1: taking facts out of the question changes public retrieval (D55), Finding 2: a conclusion can state law on a client document's authority (D56), G3 step 4: client facts from an uploaded document (dev, tracked not gated), What this does not measure

### Community 62 - "decompose.py"
Cohesion: 0.07
Nodes (49): collections_abc, 3. Process-wide caches, functools, qdrant_client, chunks(), citation_graph(), client_hits(), decompose() (+41 more)

### Community 63 - "tracing.py"
Cohesion: 0.13
Nodes (16): base64, dataclasses, inspect, os, annotate(), _brief(), generation(), _json() (+8 more)

### Community 64 - "e0_authority.py"
Cohesion: 0.33
Nodes (10): inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the…, Part 2: which authority fields have more than one value here, and from where. (+2 more)

### Community 65 - "json"
Cohesion: 0.10
Nodes (30): argparse, collections, datetime, dotenv, E4: apply the dev rules as written in tasks/todo.md, before looking at which…, main(), G3 step 4: do a client's facts get from an uploaded document into the answer?…, run() (+22 more)

### Community 66 - "stream_events"
Cohesion: 0.25
Nodes (9): get, get_documents(), get_query(), Server-sent events for one job. Replays whatever the record already holds, then…, stream_events(), events(), get(), The job, if it exists and is this tenant's. Another tenant's job is None,… (+1 more)

### Community 67 - "Hosted"
Cohesion: 0.32
Nodes (3): Hosted, A hosted embedding API in fastembed's shape (`embed` for chunks, `query_embed`…, ndarray

### Community 68 - "no_recite"
Cohesion: 0.40
Nodes (5): no_recite(), fixture, Re-cite (F5b C3) ships on; tests that don't stub its call turn it off, and the…, stub(), fake()

### Community 69 - "test_store.py"
Cohesion: 0.21
Nodes (15): chunks(), parametrize, Transaction time (D6): an amendment rewrites a chunk in place; the old text…, test_a_dropped_paragraph_is_retired_by_the_sweep(), test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(), test_authority_profile_comes_from_source_and_citation_form(), test_excluded_rows_are_stored_but_not_counted_as_indexable(), test_reingest_is_idempotent() (+7 more)

### Community 70 - "Checkpoint 2 demo: one question per tenant (G3)"
Cohesion: 0.25
Nodes (7): Both fixed (your call, 2026-11-02), Checkpoint 2 demo: one question per tenant (G3), Finding 1: A's question never retrieved § 183 (shipped retrieval, not documents), Finding 2: a question about a document the tenant doesn't have gets a legal answer, not "no such document", For your review, Tenant A: own documents, compound question, Tenant B: asks about A's client by name

### Community 73 - "citations.py"
Cohesion: 0.09
Nodes (37): eyecite, eyecite_models, FullCaseCitation, logging, load_selection(), The selection is cached so the corpus stays fixed while new opinions are filed., appeal_label(), cites() (+29 more)

### Community 74 - "in_scope"
Cohesion: 0.67
Nodes (3): in_scope(), True when a section is one of these prefixes, or a numbered child of one.…, test_in_scope_matches_children_but_not_longer_numbers()

### Community 75 - "e3_sample.py"
Cohesion: 0.33
Nodes (9): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze() (+1 more)

### Community 77 - "client"
Cohesion: 0.48
Nodes (6): create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), client()

### Community 81 - "parse"
Cohesion: 0.14
Nodes (14): parse(), Every chunk in an eCFR XML file or element tree., chunks(), fixture, A section can embed its own outline (§1.61-21 does); it must not create new…, Two chunks reaching the same citation get distinct parts, so keys cannot…, E2: §1.988-1T says "The applicability of this section expires on December 6,…, E3: §7805(e)(2) ends a post-1988 temporary regulation within 3 years, whatever… (+6 more)

### Community 85 - "caselaw.py"
Cohesion: 0.12
Nodes (24): httpx, LTTextBox, pdfminer_high_level, pdfminer_layout, re, The unit every ingester produces and every store consumes., fetch(), fold_numbers() (+16 more)

## Knowledge Gaps
- **215 isolated node(s):** `G4: dev injection corpus (draft, for your review)`, `✅ Checkpoint 1 — after T1–T3`, `✅ Checkpoint 2 — after T4–T6`, `✅ Checkpoint 3 — after T7–T8`, `✅ Checkpoint: Phase A complete` (+210 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 747 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `test_ecfr.py`, `store.py`, `usc_notes.py`, `parse`, `ecfr.py`, `index.py`, `parse`, `TaxCite — Status`, `caselaw.py`, `usc.py`, `cli.py`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `search()` (e.g. with `2. Store reads and writes` and `7. Threat table (golden adversarial rows)`) actually correct?**
  _`search()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `G4: dev injection corpus (draft, for your review)`, `✅ Checkpoint 1 — after T1–T3`, `✅ Checkpoint 2 — after T4–T6` to the rest of the system?**
  _215 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `client_docs.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09655172413793103 - nodes in this community are weakly interconnected._