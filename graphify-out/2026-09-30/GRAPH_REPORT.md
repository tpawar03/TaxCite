# Graph Report - TaxCite.nosync  (2026-09-30)

## Corpus Check
- 215 files · ~11,091,527 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 3, .jsonl 3, .xml 3)

## Summary
- 1286 nodes · 2409 edges · 85 communities (70 shown, 15 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 156 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8193fb89`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.py
- test_irs_pubs.py
- test_jobs.py
- T2: Ingest eCFR Title 26
- ragas_eval.py
- test_ecfr.py
- TaxCite — Phase B exit report
- f0_verify.py
- history
- ecfr.py
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
- caselaw.py
- taxcite
- Collaborative Working Mode
- json
- is_appeal
- Postgres
- test_store.py
- retrieval.py
- usc.py
- jobs.py
- store_bench.py
- TaxCite — Phase C exit report
- test_metrics.py
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- rerank
- e0_authority.py
- Plain-Module Package Layout
- parse
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- generate.py
- usc_notes.py
- edition_filter
- TaxCite — Phase D exit report
- TaxCite — Status
- decompose.py
- taxcite_ingest_caselaw
- TaxCite: Phase E exit report
- taxcite_ingest
- taxcite_ingest_citations
- validate_pilot.py
- e3_sample.py
- pytest
- citations.py
- F4 verdict check
- F0 judge check
- taxcite_ingest_ecfr
- conn
- retrieve.py
- ingest_ecfr
- appeal
- Answer
- test_fetch_rejects_a_non_pdf
- taxcite_ingest_irs_pubs
- weigh
- flags
- cli.py
- test_verify.py
- fixture
- api.py
- f4_hide.py
- report
- judge
- citations
- main
- snapshot.py
- fetch
- section_of
- parse_json
- nli
- triage
- suppression
- split_sections
- Hit
- Path

## God Nodes (most connected - your core abstractions)
1. `F0 judge check` - 41 edges
2. `F4 verdict check` - 31 edges
3. `search()` - 26 edges
4. `Chunk` - 24 edges
5. `conn()` - 23 edges
6. `Answer` - 21 edges
7. `TaxCite Phase A — Task List` - 16 edges
8. `ingest_ecfr()` - 15 edges
9. `main()` - 14 edges
10. `section_of()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `What exists` --references--> `answer()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/decompose.py
- `E2 and E3: the metadata, and the check that found law the parser didn't know` --references--> `save()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/store.py
- `What exists` --references--> `answer()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/decompose.py
- `Reproducing` --references--> `answer_from_groups()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/generate.py
- `What exists` --references--> `authority()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/chunk.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]

## Communities (85 total, 15 thin omitted)

### Community 0 - "index.py"
Cohesion: 0.13
Nodes (24): psycopg_types_json, qdrant_client, QdrantClient, authority(), The chunk's authority profile (E2): from its source and the citation's form,…, `source_revision` where the ingester had none (E2): what `as_of` already…, revision(), backfill_authority() (+16 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.10
Nodes (28): dehyphenate(), edition_year(), _normalise(), Join words split across a line break ("mo-\ntel" or "mo- tel" -> "motel"). A…, Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count() (+20 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.08
Nodes (27): fastapi_testclient, clean(), fixture, Job record and SSE transport (ADR-9), with the pipeline stubbed., ADR-9: nothing unverified reaches the user, so the answer is buffered., ADR-16: Redis carries progress; the record is the source of truth behind it., A Redis outage must degrade liveness, not correctness (ADR-16)., The record and the live channel can race; sequence numbers settle it. (+19 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.16
Nodes (15): eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark, Harvard Caselaw Access Project, Per-Document-Type Chunker (§3.2), CourtListener (+7 more)

### Community 4 - "ragas_eval.py"
Cohesion: 0.09
Nodes (35): aggregate(), Budget, CostCap, extract_claims(), judge_claims(), Judged, main(), pipeline_answer() (+27 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.06
Nodes (45): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+37 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "f0_verify.py"
Cohesion: 0.17
Nodes (15): concurrent_futures, build(), claim_text(), contains(), headings(), kind_of(), pages(), F0: can a self-hosted NLI model stand in for the judge, and what would zero… (+7 more)

### Community 8 - "history"
Cohesion: 0.19
Nodes (13): FullCaseCitation, full_cites(), history(), label(), The year in the parenthetical right after the cite. eyecite's own guess can…, Explanatory parentheticals push "aff'd" past the window: "113 T.C. 254 (1999)…, The appeal as one stable string, "560 F.3d 620 (ca7 2009)": no case name or pin…, (opinion, kind, by) from subsequent history in a passage. by is the appellate… (+5 more)

### Community 9 - "ecfr.py"
Cohesion: 0.17
Nodes (23): expiry(), whole' or 'partly' when a regulation's own clause says its applicability ended…, §7805(e)(2): a temporary regulation issued after Nov. 20, 1988 expires within 3…, sunset(), Block, blocks(), walk(), chunk_section() (+15 more)

### Community 10 - "test_generate.py"
Cohesion: 0.04
Nodes (24): fixture, Answer generation, tested without spending money: the model call is stubbed., Sampling at the default temperature made the same question answerable two ways,…, E5: the label map covers every (type, status) chunk.authority() can return,…, E5: every E5 arm is built from the pre-E5 prompt, so "pre-e5" reproduces that…, Replace the model call; record what it was asked., F3: arm E ships ((ii′)'s rules with rules 2 and 3 for JSON items); "pre-f3" is…, F0 found both shapes in golden answers; the old regex saw only the inner… (+16 more)

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
Cohesion: 0.08
Nodes (32): hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, C5: A cites B and C; C cites D; E cites D; Z is unheld. Hops go either…, D3b: plain-English publications outrank the statute; a statute-only search puts…, E4 (a): the prior lifts the statute over the publication; every hit survives,… (+24 more)

### Community 19 - "test_index.py"
Cohesion: 0.22
Nodes (17): chunks(), ctx(), models_(), fixture, CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., sync(), test_a_broken_qdrant_still_raises() (+9 more)

### Community 20 - "caselaw.py"
Cohesion: 0.16
Nodes (20): collections, LTTextBox, pdfminer_high_level, pdfminer_layout, re, Chunk, The unit every ingester produces and every store consumes., Make `part` a running count per citation, so `key` is unique by construction.… (+12 more)

### Community 23 - "json"
Cohesion: 0.16
Nodes (15): dotenv, E4: apply the dev rules as written in tasks/todo.md, before looking at which…, cost_of(), estimate(), judge(), main(), ADR-11: choose the LLM by measuring answers, not by price alone. uv run python…, Rough spend before committing: RAG prompts dominate the input tokens. (+7 more)

### Community 24 - "is_appeal"
Cohesion: 0.32
Nodes (8): is_appeal(), party(), petitioners(), The petitioners' names alone: "Estate of James E. Caan, Deceased, …,…, Family names in a joint caption. "C. Michael & Gwendolyn E. Willock" is one…, A caseName query for the appellate caption: surnames for people ("Donald B. &…, Same-name appeals are common (C1: three unrelated Michaels for Willock). A real…, surnames()

### Community 26 - "test_store.py"
Cohesion: 0.08
Nodes (31): chunks(), parametrize, Transaction time (D6): an amendment rewrites a chunk in place; the old text…, test_a_dropped_paragraph_is_retired_by_the_sweep(), test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(), test_authority_profile_comes_from_source_and_citation_form(), test_excluded_rows_are_stored_but_not_counted_as_indexable(), test_expiry_reads_a_regulations_own_clause_against_the_snapshot_date() (+23 more)

### Community 27 - "retrieval.py"
Cohesion: 0.23
Nodes (9): argparse, datetime, build(), collection_for(), main(), ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, Index every chunk with one model into its own collection; returns build time., score() (+1 more)

### Community 28 - "usc.py"
Cohesion: 0.20
Nodes (20): estimate_tokens(), make(), make(), blocks(), child_text(), chunk_section(), make(), clean() (+12 more)

### Community 29 - "jobs.py"
Cohesion: 0.20
Nodes (12): dataclasses, Redis, client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across…, One server-sent event. The blank line is the record separator. (+4 more)

### Community 30 - "store_bench.py"
Cohesion: 0.23
Nodes (11): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+3 more)

### Community 31 - "TaxCite — Phase C exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+4 more)

### Community 32 - "test_metrics.py"
Cohesion: 0.10
Nodes (29): mrr(), ndcg_at_k(), recall_at_k(), math, judged(), The metrics must be right before any number computed with them means anything., An answer the extractor found nothing in would otherwise score 0/0., C6: three chunks share "T.C. Memo. 2023-128, at *15" and only #3 states the… (+21 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "rerank"
Cohesion: 0.40
Nodes (6): Hit, Re-score candidates with a cross-encoder, which reads query and chunk together.…, rerank(), hit(), The cross-encoder's job: an example that quotes a rule is not the rule., test_rerank_promotes_the_rule_over_a_chunk_that_only_mentions_it()

### Community 35 - "e0_authority.py"
Cohesion: 0.14
Nodes (23): inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the…, Part 2: which authority fields have more than one value here, and from where. (+15 more)

### Community 37 - "parse"
Cohesion: 0.18
Nodes (12): skipif, fetch(), page_texts(), parse(), Path, Sliding windows with overlap; a short page yields a single window., Every chunk in one publication PDF., Download one publication, cached on disk. `delay` rate-limits bulk fetches. (+4 more)

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "search"
Cohesion: 0.22
Nodes (14): Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, search(), RRF ties used to break differently per process, moving a chunk across the k…, No final 280A regulations exist, so the home-office rules live only in Pub 587., test_dense_finds_the_hobby_loss_factor(), test_hybrid_returns_k_hits_with_payload(), test_modes_can_disagree(), test_publications_answer_what_regulations_cannot() (+6 more)

### Community 40 - "generate.py"
Cohesion: 0.15
Nodes (24): answer_from_groups(), answer_from_hits(), answer_schema(), authority_label(), call_model(), effective_note(), format_sources(), _generate() (+16 more)

### Community 41 - "usc_notes.py"
Cohesion: 0.06
Nodes (43): amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes(), own_designation() (+35 more)

### Community 42 - "edition_filter"
Cohesion: 0.25
Nodes (8): Filter, edition_filter(), One source or several; several is how B7 routes a sub-query to the corpora that…, Keep chunks with no edition (everything but publications, and undated…, source_filter(), D3's filter, against Qdrant's own semantics (in-memory), not a re-…, test_edition_filter_keeps_undated_chunks_and_nearby_editions(), kept()

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 45 - "decompose.py"
Cohesion: 0.10
Nodes (26): collections_abc, Reproducing, answer(), chunks(), citation_graph(), decompose(), Decomposition, merge() (+18 more)

### Community 47 - "TaxCite: Phase E exit report"
Cohesion: 0.17
Nodes (11): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E2 and E3: the metadata, and the check that found law the parser didn't know, E4: the rerank, E5: authority in answers, Failures, with examples, Reproducing (+3 more)

### Community 50 - "validate_pilot.py"
Cohesion: 0.50
Nodes (4): content_words(), main(), Check a pilot set against the real corpus before any scores are computed. A…, taxcite

### Community 51 - "e3_sample.py"
Cohesion: 0.33
Nodes (9): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze() (+1 more)

### Community 52 - "pytest"
Cohesion: 0.22
Nodes (8): pytest, parametrize, The temporal gate's scoring rules (D2), on fixture values: no API calls., E5: one answer per plan set; rates per sample, misweighted tags counted on…, test_as_of_match(), test_kappa_hand_computed(), test_pass_needs_a_correct_answer_and_no_as_of_miss(), test_sample_summary_splits_conflict_and_guard_rows_per_sample()

### Community 53 - "citations.py"
Cohesion: 0.19
Nodes (13): eyecite, eyecite_models, logging, cites(), kind(), normalize(), own(), Citation and treatment edges between Tax Court opinions: two Postgres tables,… (+5 more)

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "conn"
Cohesion: 0.14
Nodes (18): BackgroundTasks, BaseModel, get, post, get_query(), post_query(), Query, Accept a question and return immediately (ADR-9). The pipeline runs 20-30s,… (+10 more)

### Community 58 - "retrieve.py"
Cohesion: 0.22
Nodes (10): functools, SparseVector, embed(), _models(), Search the indexed corpus. Modes, because the eval ablation ladder (§9) needs…, Loaded once per process and per model: ~4s, which every query would otherwise…, Loaded once per process and per model, like the embedding models., The cross-encoder is deterministic, so a pool scored once needn't be scored… (+2 more)

### Community 59 - "ingest_ecfr"
Cohesion: 0.30
Nodes (19): Connection, Namespace, backfill_authority(), ingest_case(), ingest_ecfr(), ingest_pubs(), ingest_usc(), load_citations() (+11 more)

### Community 60 - "appeal"
Cohesion: 0.25
Nodes (9): appeal(), appeal_label(), cached(), get(), Client, Path, One format for both sources, so a reader sees the same appeal the same way., A response cached with the time it was fetched: re-running from cache must not… (+1 more)

### Community 61 - "Answer"
Cohesion: 0.15
Nodes (21): Answer, cited_items(), The sentences a structured answer can show, in order: text and at least one…, (answer text, sentences dropped) from arm E's JSON. Each sentence ends with its…, Says INSUFFICIENT EVIDENCE and cites nothing. F3: a cited answer that flags one…, Answer a question with retrieval (`rag`) or without it (`closed_book`)., render(), apply() (+13 more)

### Community 64 - "weigh"
Cohesion: 0.28
Nodes (8): level(), Hit, (sub-query, its chunks) for the synthesis prompt, limited to `keep` if given.…, A hit's authority level (E2's profile; 0 when it has none), with E4's two…, E4's reorderings of the cross-encoder's list by authority. Nothing is dropped.…, weigh(), order(), rescore()

### Community 65 - "flags"
Cohesion: 0.24
Nodes (10): Open problems handed on, flag(), flags(), load(), opinion_chunks(), datetime, Replace one source's rows; recorded_at (when we first learned it) survives,…, One opinion's treatment flag from its (source, kind, by, checked_at) rows (C4).… (+2 more)

### Community 66 - "cli.py"
Cohesion: 0.18
Nodes (11): io, fetch(), fetch_usc(), latest_as_of(), Path, Command line: fetch, parse, store and index the corpora. taxcite ingest ecfr…, Title 26 USLM XML for a release point (default: the current one), cached on…, The date eCFR considers Title 26 current to. (+3 more)

### Community 67 - "test_verify.py"
Cohesion: 0.12
Nodes (8): fixture, Claim verification (F4), tested without spending money: the verifier call is…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, structured_answer(), stub(), test_a_note_about_a_missing_detail_survives_when_its_part_is_shown(), test_checked_fails_closed_and_leaves_refusals_alone(), test_sentence_hiding_ships()

### Community 69 - "api.py"
Cohesion: 0.17
Nodes (13): asyncio, fastapi, fastapi_responses, os, psycopg, pydantic, Response, _check() (+5 more)

### Community 70 - "f4_hide.py"
Cohesion: 0.29
Nodes (10): base(), check_sheet(), main(), metrics(), Path, F4: one verified run, shown three ways, so the hiding unit is decided on…, The cached answer as the verifier saw it: every cited item shown., The cache entry as `unit` would show it. (+2 more)

### Community 71 - "report"
Cohesion: 0.25
Nodes (9): abstention(), claim_unit(), f1(), On the not-supported class: what the verifier exists to catch. `supported` is…, The threshold that maximises not-supported F1 on the tune half. Ties go to the…, Each F0 unit (cited chunks only) against today's faithfulness (LLM-extracted…, Rule 3's refusals today, over all 5 cached runs: the baseline F2's gate has to…, report() (+1 more)

### Community 72 - "judge"
Cohesion: 0.25
Nodes (9): agreement(), check_sheet(), judge(), call(), main(), premise(), Judge each pair against `field`'s chunks into `out`. The main pass reads every…, ~40 pairs for you to read (Checkpoint 1): half the judge called unsupported,… (+1 more)

### Community 73 - "citations"
Cohesion: 0.25
Nodes (8): material(), Completeness over material sentences, and the share of answers that would…, Split outside brackets, at . ! ? followed by a space, never after an…, A line that states no claim: a section heading, a markdown title, a label…, sentences(), structural(), citations(), Every bracketed citation, once each, in order: nested brackets flattened, "[A;…

### Community 74 - "main"
Cohesion: 0.25
Nodes (3): main(), needs_case_law(), A row whose gold includes an opinion: routing must send a sub-query to the case…

### Community 75 - "snapshot.py"
Cohesion: 0.36
Nodes (7): create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), httpx, subprocess

### Community 76 - "fetch"
Cohesion: 0.32
Nodes (8): fetch(), get(), load_selection(), Client, The newest `per_topic` distinct opinions for each topic. A consolidated case is…, The selection is cached so the corpus stays fixed while new opinions are filed., One opinion's PDF, cached. DAWSON hands out a short-lived signed S3 link., select()

### Community 77 - "section_of"
Cohesion: 0.29
Nodes (7): What exists, authorities(), Each cited source's authority and label, for the API (E5): an exact citation…, The section a citation belongs to, ignoring paragraph depth. '26 CFR…, section_of(), ADR-13, G-A05's payload: text claiming to be binding authority can't become the…, test_a_label_comes_from_the_profile_never_from_the_source_text()

### Community 78 - "parse_json"
Cohesion: 0.33
Nodes (6): parse_json(), The judge returns JSON by instruction, not by API guarantee, so parse…, parametrize, Instruction is not a guarantee; the model sometimes wraps its JSON in prose., test_a_judge_that_returns_junk_does_not_crash_the_run(), test_json_is_found_inside_chatter()

### Community 79 - "nli"
Cohesion: 0.40
Nodes (4): nli(), Overlapping word windows covering the whole chunk: the last one starts at or…, P(entailed) per pair: the best window of the best cited chunk. Looser than the…, windows()

### Community 81 - "suppression"
Cohesion: 0.50
Nodes (4): Sentences no pair of this unit covers: every uncited one for sentences, only…, What ADR-15 would hide over answers that weren't refusals, for one claim unit.…, suppression(), uncited()

## Knowledge Gaps
- **159 isolated node(s):** `V01`, `V02`, `V03`, `V04`, `V05` (+154 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 592 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `caselaw.py` to `index.py`, `parse`, `test_ecfr.py`, `api.py`, `ecfr.py`, `usc_notes.py`, `TaxCite — Status`, `ingest_ecfr`, `usc.py`?**
  _High betweenness centrality (0.188) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.171) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `search()` (e.g. with `main()` and `retrieve()`) actually correct?**
  _`search()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `Chunk` (e.g. with `parse()` and `covers()`) actually correct?**
  _`Chunk` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `V01`, `V02`, `V03` to the rest of the system?**
  _159 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12666666666666668 - nodes in this community are weakly interconnected._