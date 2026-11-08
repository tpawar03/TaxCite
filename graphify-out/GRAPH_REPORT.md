# Graph Report - TaxCite.nosync  (2026-11-07)

## Corpus Check
- 285 files · ~15,098,069 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: .jsonl 13, (none) 3, .xml 3)

## Summary
- 1670 nodes · 3229 edges · 98 communities (79 shown, 19 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 251 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2247d9e9`
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
- conn
- api.py
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
- verify.py
- test_verify.py
- TaxCite — Phase C exit report
- test_metrics.py
- ecfr.py
- score_one
- citations
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- run
- test_render.py
- Plain-Module Package Layout
- generate.py
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- ingest
- usc_notes.py
- Hit
- TaxCite — Phase D exit report
- app.js
- test_documents.py
- taxcite_ingest_caselaw
- verify
- index.py
- taxcite_ingest_citations
- TaxCite — Status
- f0_verify.py
- TaxCite: Phase E exit report
- f5_golden.py
- F4 verdict check
- F0 judge check
- taxcite_ingest_ecfr
- aggregate
- authorities
- cli.py
- TaxCite: Phase F exit report
- answer
- usc.py
- tracing.py
- e0_authority.py
- retrieve.py
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
- client
- score_one
- f4_hide.py
- store_bench.py
- section_of
- recite
- fetch
- MissingCredentials
- fastapi_testclient
- test_refusal_rate_gate
- set_prompt
- weigh
- stub
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
3. `conn()` - 37 edges
4. `search()` - 32 edges
5. `F4 verdict check` - 31 edges
6. `Answer` - 26 edges
7. `Chunk` - 24 edges
8. `Hit` - 23 edges
9. `run()` - 22 edges
10. `call_model()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `Open problems handed on` --references--> `flags()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/ingest/citations.py
- `E2 and E3: the metadata, and the check that found law the parser didn't know` --references--> `save()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/store.py
- `Both fixed (your call, 2026-11-02)` --references--> `run()`  [INFERRED]
  eval/results/g3-demo.md → src/taxcite/jobs.py
- `What exists` --references--> `trace_id()`  [INFERRED]
  eval/results/phase_g.md → src/taxcite/tracing.py
- `Threat table, as built` --references--> `search()`  [INFERRED]
  eval/results/phase_g.md → src/taxcite/retrieve.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]

## Communities (98 total, 19 thin omitted)

### Community 0 - "client_docs.py"
Cohesion: 0.16
Nodes (14): qdrant_client, kind(), ocr(), page_texts(), _pages(), Client documents (G2): a tenant's own uploads, searchable by that tenant only.…, Tesseract's text for one page image; "" when tesseract isn't installed, so the…, One text per page: the text layer where there is one, OCR where there isn't. (+6 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.07
Nodes (31): skipif, _normalise(), Sliding windows with overlap; a short page yields a single window., Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count(), edges() (+23 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.06
Nodes (36): opentelemetry, opentelemetry_sdk_trace, opentelemetry_sdk_trace_export, opentelemetry_sdk_trace_export_in_memory_span_exporter, SpanExporter, BrokenExporter, clean(), fixture (+28 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.16
Nodes (15): eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark, Harvard Caselaw Access Project, Per-Document-Type Chunker (§3.2), CourtListener (+7 more)

### Community 4 - "json"
Cohesion: 0.09
Nodes (37): argparse, datetime, dotenv, E4: apply the dev rules as written in tasks/todo.md, before looking at which…, _models(), ADR-18 revisited: hosted embedding models against bge-base, on the golden set.…, retrieve.search loads its dense model by name; hosted names resolve here…, main() (+29 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.12
Nodes (19): in_scope(), True when a section is one of these prefixes, or a numbered child of one.…, of(), Chunker tests against nine real sections in tests/fixtures/ecfr_sample.xml.…, eCFR ships its own citation string in hierarchy_metadata; ours must agree., test_cita_is_kept_out_of_the_text(), test_example_text_in_pspace_is_captured(), test_in_scope_matches_children_but_not_longer_numbers() (+11 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "conn"
Cohesion: 0.13
Nodes (20): get, Response, _check(), delete_document(), get_documents(), get_query(), health(), Server-sent events for one job. Replays whatever the record already holds, then… (+12 more)

### Community 8 - "api.py"
Cohesion: 0.10
Nodes (22): asyncio, contextlib, fastapi, fastapi_responses, fastapi_staticfiles, hashlib, psycopg, pydantic (+14 more)

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
Nodes (17): as_of_match(), kappa(), passed(), Year-level match of the plan's as-of against the row's tax year. None = not…, Cohen's kappa for two raters over the same items., Per sample index: rates over the rows, first judge repeat (E5). Conflict and…, sample_summary(), pytest (+9 more)

### Community 23 - "ragas_eval.py"
Cohesion: 0.16
Nodes (20): Budget, CostCap, extract_claims(), judge_claims(), main(), parse_json(), pipeline_answer(), Path (+12 more)

### Community 24 - "test_usc.py"
Cohesion: 0.16
Nodes (14): chunks(), of(), fixture, Statute chunker tests against eight real sections in…, test_en_dash_section_number_becomes_a_hyphen(), test_heading_folds_into_its_first_child(), test_neighbouring_subsections_pack_into_a_range(), test_notes_are_not_text_and_source_credit_is_the_history() (+6 more)

### Community 26 - "verify.py"
Cohesion: 0.14
Nodes (15): dataclasses, os, Redis, client(), Event, notify(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across…, Best-effort live notification. Redis is the delivery channel, never the record,… (+7 more)

### Community 27 - "test_verify.py"
Cohesion: 0.08
Nodes (19): taxcite, no_recite(), fixture, Claim verification (F4), tested without spending money: the verifier call is…, G6 (G-A01): sentences tagged parts 2 and 3 of a one-part answer render under…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, A verifier stub that answers by prompt: SYSTEM gets the next of…, Re-cite (F5b C3) ships on; tests that don't stub its call turn it off, and the… (+11 more)

### Community 28 - "TaxCite — Phase C exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+4 more)

### Community 29 - "test_metrics.py"
Cohesion: 0.11
Nodes (26): first_hits(), mrr(), ndcg_at_k(), 0-based rank at which each group is first satisfied, for the groups that are. A…, recall_at_k(), Gold, math, parametrize (+18 more)

### Community 30 - "ecfr.py"
Cohesion: 0.18
Nodes (22): §7805(e)(2): a temporary regulation issued after Nov. 20, 1988 expires within 3…, sunset(), Block, blocks(), walk(), chunk_section(), make(), cite() (+14 more)

### Community 31 - "score_one"
Cohesion: 0.17
Nodes (8): cached_decompose(), main(), Path, Decompose once per plan set and reuse it, so a comparison measures the change…, score_one(), gate_only(), Path, F2's cheap pass: for each row and plan set, the parts the shipped pipeline…

### Community 32 - "citations"
Cohesion: 0.20
Nodes (11): material(), Completeness over material sentences, and the share of answers that would…, Split outside brackets, at . ! ? followed by a space, never after an…, A line that states no claim: a section heading, a markdown title, a label…, sentences(), structural(), abstention(), One answer to an insufficiency row, as one of: "refused", "flagged" (cited… (+3 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "run"
Cohesion: 0.22
Nodes (14): 2. Store reads and writes, Reproducing, decompose(), One structured-output call (ADR-11). Temperature 0 and a fixed seed, so a re-…, Search once per sub-query, filtered to the sources its kind allows. Fills…, retrieve(), flags(), Treatment flags for the opinions an answer cites. Fails open: if the table… (+6 more)

### Community 35 - "test_render.py"
Cohesion: 0.17
Nodes (14): browser(), page(), handle(), fixture, G5, the render path (ADR-13): nothing from a source, a document or an answer…, ADR-13 by construction: none of the APIs that turn a string into markup appear…, The page with every route stubbed; records outbound requests, dialogs and…, render_everything() (+6 more)

### Community 37 - "generate.py"
Cohesion: 0.12
Nodes (28): 4. Where text enters a prompt, Hit, Answer, answer_from_groups(), answer_from_hits(), answer_schema(), call_model(), effective_note() (+20 more)

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "search"
Cohesion: 0.11
Nodes (25): Filter, edition_filter(), Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, One source or several; several is how B7 routes a sub-query to the corpora that…, Keep chunks with no edition (everything but publications, and undated…, search(), source_filter(), hit() (+17 more)

### Community 40 - "ingest"
Cohesion: 0.11
Nodes (20): BackgroundTasks, BaseModel, post, _over_quota(), post_document(), post_query(), Query, Upload one client document (G2). Synchronous: a 50-page text PDF took 16 s,… (+12 more)

### Community 41 - "usc_notes.py"
Cohesion: 0.06
Nodes (43): amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes(), own_designation() (+35 more)

### Community 42 - "Hit"
Cohesion: 0.17
Nodes (12): chunks(), client_hits(), Decomposition, merge(), (sub-query, its chunks) for the synthesis prompt, limited to `keep` if given.…, The k chunks synthesis sees: every sub-query's hits, ordered by the cross-…, G3: the asking tenant's own document chunks, searched with each client fact and…, One ranked list of k, round-robin across sub-queries, first occurrence wins.… (+4 more)

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "app.js"
Cohesion: 0.44
Nodes (10): ADR-0013, api(), ask(), detail(), el(), events(), listDocuments(), showAnswer() (+2 more)

### Community 45 - "test_documents.py"
Cohesion: 0.06
Nodes (62): io, needs_tesseract, shutil, taxcite_ingest, ask(), clean(), pdf(), png() (+54 more)

### Community 47 - "verify"
Cohesion: 0.12
Nodes (21): Finding 1: taking facts out of the question changes public retrieval (D55), Finding 2: a conclusion can state law on a client document's authority (D56), G3 step 4: client facts from an uploaded document (dev, tracked not gated), What this does not measure, What exists, cited_items(), The sentences a structured answer can show, in order: text and at least one…, (answer text, sentences dropped) from arm E's JSON. Each sentence ends with its… (+13 more)

### Community 48 - "index.py"
Cohesion: 0.12
Nodes (25): psycopg_types_json, QdrantClient, authority(), expiry(), The chunk's authority profile (E2): from its source and the citation's form,…, whole' or 'partly' when a regulation's own clause says its applicability ended…, backfill_authority(), batched() (+17 more)

### Community 50 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 51 - "f0_verify.py"
Cohesion: 0.11
Nodes (25): concurrent_futures, agreement(), build(), check_sheet(), claim_text(), contains(), judge(), call() (+17 more)

### Community 52 - "TaxCite: Phase E exit report"
Cohesion: 0.11
Nodes (17): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E2 and E3: the metadata, and the check that found law the parser didn't know, E4: the rerank, E5: authority in answers, Failures, with examples, Open problems handed on (+9 more)

### Community 53 - "f5_golden.py"
Cohesion: 0.13
Nodes (29): f1(), headings(), Each cached chunk's heading, which synthesis saw ("[citation] (heading)") but…, On the not-supported class: what the verifier exists to catch. `supported` is…, audit(), check(), checkpoint(), save() (+21 more)

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "aggregate"
Cohesion: 0.18
Nodes (12): aggregate(), Judged, None when there is nothing to score: a refusal, or an answer making no claim., Refusals are excluded from the mean and reported separately (§9.2). Averaging a…, judged(), An answer the extractor found nothing in would otherwise score 0/0., A row with one claim per entry in `supported`., Averaging refusals in either direction breaks the gate: 0 punishes the… (+4 more)

### Community 58 - "authorities"
Cohesion: 0.12
Nodes (19): Cost, Deferred, by decision, Golden adversarial rows, scored once on the shipped pipeline, Reproducing, TaxCite: Phase G exit report, The gates, Threat table, as built, What each control caught, with the payload (+11 more)

### Community 59 - "cli.py"
Cohesion: 0.17
Nodes (29): Connection, Namespace, backfill_authority(), create_tenant(), fetch(), fetch_usc(), ingest_case(), ingest_ecfr() (+21 more)

### Community 60 - "TaxCite: Phase F exit report"
Cohesion: 0.20
Nodes (9): F4's and F2's switches for an eval run: the verifier off (the unverified arm),…, set_verify(), Golden, scored once on the shipped pipeline, How the phase went, Open, for later phases, Reproducing, TaxCite: Phase F exit report, The gates (+1 more)

### Community 61 - "answer"
Cohesion: 0.18
Nodes (9): 1. Endpoints today, 5. Where text reaches the user, 6. What is stored that may hold PII, 7. Threat table (golden adversarial rows), 8. Open from G0, G0: threat model and inventory, G3 step 4: five dev rows with the client's facts in a document (draft, for your review), answer() (+1 more)

### Community 62 - "usc.py"
Cohesion: 0.27
Nodes (16): blocks(), child_text(), chunk_section(), clean(), designation(), lead_in(), parse(), provision_blocks() (+8 more)

### Community 63 - "tracing.py"
Cohesion: 0.12
Nodes (18): base64, functools, inspect, lifespan(), annotate(), _brief(), generation(), _json() (+10 more)

### Community 64 - "e0_authority.py"
Cohesion: 0.17
Nodes (17): inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the…, Part 2: which authority fields have more than one value here, and from where. (+9 more)

### Community 65 - "retrieve.py"
Cohesion: 0.21
Nodes (12): collections_abc, 3. Process-wide caches, SparseVector, embed(), _models(), Search the indexed corpus. Modes, because the eval ablation ladder (§9) needs…, Loaded once per process and per model: ~4s, which every query would otherwise…, Cached: every search in one pipeline run uses the original question (only the… (+4 more)

### Community 66 - "test_store.py"
Cohesion: 0.19
Nodes (16): chunks(), parametrize, Transaction time (D6): an amendment rewrites a chunk in place; the old text…, test_a_dropped_paragraph_is_retired_by_the_sweep(), test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(), test_authority_profile_comes_from_source_and_citation_form(), test_excluded_rows_are_stored_but_not_counted_as_indexable(), test_reingest_is_idempotent() (+8 more)

### Community 67 - "Hosted"
Cohesion: 0.32
Nodes (3): Hosted, A hosted embedding API in fastembed's shape (`embed` for chunks, `query_embed`…, ndarray

### Community 68 - "report"
Cohesion: 0.13
Nodes (13): abstention(), claim_unit(), The threshold that maximises not-supported F1 on the tune half. Ties go to the…, The small model decides only what it's sure of, the LLM the rest. Auto-accept…, Sentences no pair of this unit covers: every uncited one for sentences, only…, What ADR-15 would hide over answers that weren't refusals, for one claim unit.…, Each F0 unit (cited chunks only) against today's faithfulness (LLM-extracted…, Rule 3's refusals today, over all 5 cached runs: the baseline F2's gate has to… (+5 more)

### Community 69 - "decompose.py"
Cohesion: 0.13
Nodes (15): citation_graph(), gate(), neighbors(), parse(), Split a question into typed sub-queries, and route each to the sources that can…, (sub-queries, as_of, fallback reason). Never raises. A decomposition that…, Held opinions within `hops` citation steps of the seeds, in either direction;…, (edges, held opinions), loaded once: 5,278 edges is small enough to walk in… (+7 more)

### Community 70 - "Checkpoint 2 demo: one question per tenant (G3)"
Cohesion: 0.25
Nodes (7): Both fixed (your call, 2026-11-02), Checkpoint 2 demo: one question per tenant (G3), Finding 1: A's question never retrieved § 183 (shipped retrieval, not documents), Finding 2: a question about a document the tenant doesn't have gets a legal answer, not "no such document", For your review, Tenant A: own documents, compound question, Tenant B: asks about A's client by name

### Community 71 - "caselaw.py"
Cohesion: 0.10
Nodes (37): collections, httpx, LTTextBox, pdfminer_high_level, pdfminer_layout, re, Chunk, estimate_tokens() (+29 more)

### Community 72 - "parse"
Cohesion: 0.14
Nodes (14): parse(), Every chunk in an eCFR XML file or element tree., chunks(), fixture, A section can embed its own outline (§1.61-21 does); it must not create new…, Two chunks reaching the same citation get distinct parts, so keys cannot…, E2: §1.988-1T says "The applicability of this section expires on December 6,…, E3: §7805(e)(2) ends a post-1988 temporary regulation within 3 years, whatever… (+6 more)

### Community 73 - "citations.py"
Cohesion: 0.07
Nodes (52): eyecite, eyecite_models, FullCaseCitation, logging, load_selection(), The selection is cached so the corpus stays fixed while new opinions are filed., appeal(), appeal_label() (+44 more)

### Community 74 - "designations"
Cohesion: 0.24
Nodes (12): Element, designations(), level_of(), 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.…, Level-1 and level-2 designations a paragraph opens with. Read from raw text,…, p(), test_compact_two_level_designation(), test_designation_split_by_italic_heading() (+4 more)

### Community 75 - "e3_sample.py"
Cohesion: 0.33
Nodes (9): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze() (+1 more)

### Community 77 - "client"
Cohesion: 0.39
Nodes (7): create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), client(), subprocess

### Community 78 - "score_one"
Cohesion: 0.40
Nodes (5): build(), collection_for(), main(), Index every chunk with one hosted model, skipping sources already complete (a…, score_one()

### Community 79 - "f4_hide.py"
Cohesion: 0.29
Nodes (10): base(), check_sheet(), main(), metrics(), Path, F4: one verified run, shown three ways, so the hiding unit is decided on…, The cached answer as the verifier saw it: every cited item shown., The cache entry as `unit` would show it. (+2 more)

### Community 80 - "store_bench.py"
Cohesion: 0.23
Nodes (11): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+3 more)

### Community 81 - "section_of"
Cohesion: 0.29
Nodes (7): parse_citations(), The section a citation belongs to, ignoring paragraph depth. '26 CFR…, Split the answer's citations three ways: exact, derived, unsupported. The three…, section_of(), premises(), prompt(), Indexes into `answer.retrieved` a sentence is judged against: the chunks it…

### Community 82 - "recite"
Cohesion: 0.29
Nodes (7): _json(), RuntimeError, The verifier's response was unusable. The caller shows nothing unverified., {item index: the retrieved citation that states it} for failed items, from one…, recite(), VerificationFailed, with_documents()

### Community 83 - "fetch"
Cohesion: 0.47
Nodes (6): fetch(), get(), Client, The newest `per_topic` distinct opinions for each topic. A consolidated case is…, One opinion's PDF, cached. DAWSON hands out a short-lived signed S3 link., select()

### Community 84 - "MissingCredentials"
Cohesion: 0.40
Nodes (5): MissingCredentials, RuntimeError, Raised instead of the SDK's generic auth error, which does not say what to set., Fail early and specifically. The SDK raises a generic TypeError at request…, _require_credentials()

### Community 87 - "set_prompt"
Cohesion: 0.20
Nodes (10): E5's prompt arms, each built from the pre-E5 prompt: "pre-e5" is it unchanged…, set_prompt(), E5: every E5 arm is built from the pre-E5 prompt, so "pre-e5" reproduces that…, F3: arm E ships ((ii′)'s rules with rules 2 and 3 for JSON items); "pre-f3" is…, B9's calibration arm, rebuilt on the shipped (structured) prompt for F3's band…, test_e5_arms_rebuild_from_pre_e5_and_run_unstructured(), test_f3_arms_rewrite_rule_2_and_only_the_sections_arm_numbers_parts(), test_structured_synthesis_renders_json_and_refuses_on_an_unusable_response() (+2 more)

### Community 88 - "weigh"
Cohesion: 0.40
Nodes (6): level(), A hit's authority level (E2's profile; 0 when it has none), with E4's two…, E4's reorderings of the cross-encoder's list by authority. Nothing is dropped.…, weigh(), order(), rescore()

### Community 90 - "stub"
Cohesion: 0.50
Nodes (3): fixture, Replace the model call; record what it was asked., stub()

## Knowledge Gaps
- **223 isolated node(s):** `The gates`, `Golden adversarial rows, scored once on the shipped pipeline`, `What Phase G got wrong`, `Deferred, by decision`, `Cost` (+218 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 770 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `caselaw.py` to `test_ecfr.py`, `parse`, `usc_notes.py`, `api.py`, `index.py`, `TaxCite — Status`, `ecfr.py`, `cli.py`, `usc.py`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `conn()` (e.g. with `main()` and `main()`) actually correct?**
  _`conn()` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `search()` (e.g. with `2. Store reads and writes` and `7. Threat table (golden adversarial rows)`) actually correct?**
  _`search()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `The gates`, `Golden adversarial rows, scored once on the shipped pipeline`, `What Phase G got wrong` to the rest of the system?**
  _223 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_irs_pubs.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07207207207207207 - nodes in this community are weakly interconnected._