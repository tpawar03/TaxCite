# Graph Report - TaxCite.nosync  (2026-10-01)

## Corpus Check
- 99 files · ~1,038,154 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 3, .jsonl 3, .xml 3)

## Summary
- 1269 nodes · 2341 edges · 75 communities (64 shown, 11 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 145 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `aa9dd826`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.py
- test_irs_pubs.py
- test_jobs.py
- T2: Ingest eCFR Title 26
- Budget
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
- paragraphs
- taxcite
- Collaborative Working Mode
- retrieval.py
- test_metrics.py
- Postgres
- jobs.py
- test_verify.py
- decompose.py
- embed_bench.py
- store_bench.py
- TaxCite — Phase C exit report
- e0_authority.py
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- f5_golden.py
- citations.py
- Plain-Module Package Layout
- e3_sample.py
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- generate.py
- Chunk
- verify
- TaxCite — Phase D exit report
- edition_filter
- SubQuery
- taxcite_ingest_caselaw
- TaxCite: Phase E exit report
- taxcite_ingest
- taxcite_ingest_citations
- TaxCite — Phase A exit report
- ecfr.py
- report
- main
- F4 verdict check
- F0 judge check
- taxcite_ingest_ecfr
- api.py
- main
- ingest_ecfr
- TaxCite: Phase F exit report
- verify.py
- store.py
- taxcite_ingest_irs_pubs
- cli.py
- answer
- call_model
- fetch
- refusals_ok
- conn
- f4_hide.py
- suppression
- latest_as_of
- VerificationFailed
- snapshot.py

## God Nodes (most connected - your core abstractions)
1. `F0 judge check` - 41 edges
2. `F5 reference check` - 41 edges
3. `F4 verdict check` - 31 edges
4. `search()` - 27 edges
5. `Chunk` - 22 edges
6. `Hit` - 22 edges
7. `conn()` - 22 edges
8. `TaxCite Phase A — Task List` - 16 edges
9. `ingest_ecfr()` - 15 edges
10. `recall_at_k()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `What exists` --references--> `answer()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/decompose.py
- `What exists` --references--> `answer()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/decompose.py
- `Open problems handed on` --references--> `flags()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/ingest/citations.py
- `E2 and E3: the metadata, and the check that found law the parser didn't know` --references--> `save()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/store.py
- `Reproducing` --references--> `answer_from_groups()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/generate.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]

## Communities (75 total, 11 thin omitted)

### Community 0 - "index.py"
Cohesion: 0.18
Nodes (17): QdrantClient, batched(), count(), create_collection(), edition(), point_id(), Embed chunks and keep a Qdrant collection in step with Postgres. Postgres is…, Retry a batch once or twice: a busy host turns a slow upsert into a timeout. (+9 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.06
Nodes (42): skipif, dehyphenate(), edition_year(), fetch(), _normalise(), page_texts(), parse(), Path (+34 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.08
Nodes (25): fastapi_testclient, pytest, clean(), fixture, Job record and SSE transport (ADR-9), with the pipeline stubbed., ADR-9: nothing unverified reaches the user, so the answer is buffered., ADR-16: Redis carries progress; the record is the source of truth behind it., A Redis outage must degrade liveness, not correctness (ADR-16). (+17 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.13
Nodes (19): The Pilot Set Is Data, Not Code, eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, T3: Hybrid search CLI with citations, T4: Pilot Set and Retrieval Eval Script, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark (+11 more)

### Community 4 - "Budget"
Cohesion: 0.09
Nodes (28): Budget, extract_claims(), judge_claims(), main(), parse_json(), pipeline_answer(), Path, The judge returns JSON by instruction, not by API guarantee, so parse… (+20 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.05
Nodes (52): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+44 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "f0_verify.py"
Cohesion: 0.14
Nodes (19): concurrent_futures, build(), claim_text(), contains(), headings(), kind_of(), material(), pages() (+11 more)

### Community 8 - "test_usc.py"
Cohesion: 0.16
Nodes (14): chunks(), of(), fixture, Statute chunker tests against eight real sections in…, test_en_dash_section_number_becomes_a_hyphen(), test_heading_folds_into_its_first_child(), test_neighbouring_subsections_pack_into_a_range(), test_notes_are_not_text_and_source_credit_is_the_history() (+6 more)

### Community 9 - "F5 reference check"
Cohesion: 0.05
Nodes (41): F5 reference check, R01 `G-C17#0#1`, R02 `G-S18#0#1`, R03 `G-X14#0#1`, R04 `G-C14#0#3`, R05 `G-X05#0#3`, R06 `G-S06#0#2`, R07 `G-S24#0#0` (+33 more)

### Community 10 - "test_generate.py"
Cohesion: 0.08
Nodes (11): fixture, Answer generation, tested without spending money: the model call is stubbed., Sampling at the default temperature made the same question answerable two ways,…, Replace the model call; record what it was asked., Chunk citations are sometimes ranges; citing one paragraph inside is precision,…, A citation not among the sources is the failure mode this system exists to…, stub(), test_a_narrower_paragraph_of_a_retrieved_section_counts_as_derived() (+3 more)

### Community 11 - "TaxCite"
Cohesion: 0.15
Nodes (20): TaxCite, TaxCite PRD, Functional Requirements FR-1..FR-17, Goals G1-G6 (research time, seat displacement, groundedness, gates, cost, leakage), Non-Functional Requirements (latency, reliability, cost, security), Open Questions (embedding, LLM provider, frontend, backup storage, market scope), Renee (Enrolled Agent persona), ADR-1: Decomposition + Bounded Citation-Graph Traversal (+12 more)

### Community 12 - "TaxCite Phase A — Task List"
Cohesion: 0.13
Nodes (15): ✅ Checkpoint 1 — after T1–T3, ✅ Checkpoint 2 — after T4–T6, ✅ Checkpoint 3 — after T7–T8, ✅ Checkpoint: Phase A complete, T10: Phase A exit report, T2: Ingest eCFR Title 26 into Postgres + Qdrant, T4: Pilot set (20 questions) and retrieval eval script, T6: Embedding-model benchmark and decision (+7 more)

### Community 13 - "Phase A Implementation Plan"
Cohesion: 0.17
Nodes (16): Qdrant Service (compose), Redis Service (compose), Host Port Offsets (5433 / 6380), Phase A Implementation Plan, Phase A Risks and Mitigations, T1: Local stack and package skeleton, T9: Job Record and SSE Transport, Non-Goals (no full GraphRAG, no BM25 engine, no token streaming, federal only) (+8 more)

### Community 14 - "Task List"
Cohesion: 0.12
Nodes (15): Architecture Decisions (for this phase), Checkpoint 1, Checkpoint 2 (human review: embedding decision), Checkpoint 3 (human review: ADR-11 decision), Checkpoint: Phase A complete, Dependency Graph, Implementation Plan: TaxCite Phase A — Core Retrieval Baseline, Overview (+7 more)

### Community 15 - "test_citations.py"
Cohesion: 0.05
Nodes (8): memo(), fixture, Case-law tests against two real Tax Court opinions (see tasks/todo.md B3): -…, result(), tc(), test_selection_dedupes_by_citation_and_keeps_the_newest(), Citation and treatment extraction (tasks/todo.md C3), on text shaped like the…, test_a_failed_lookup_fails_open_and_rolls_back()

### Community 16 - "Phase A Exit Report"
Cohesion: 0.19
Nodes (14): Phase A Exit Report, Phase A Recalibration Notes for §9.3, What Phase A did not do, Repository Map, Phase A Complete (Status), Acceptance Thresholds by Phase (§9.3), ADR-18: Dense Embedding Model — BAAI/bge-base-en-v1.5, BAAI/bge-base-en-v1.5 (+6 more)

### Community 17 - "ADR-11: LLM Tiering — gpt-4o-mini"
Cohesion: 0.22
Nodes (11): Phase A Known Failures, Three-Way Citation Counting, ADR-11: LLM Tiering — gpt-4o-mini, ADR-15: Zero-Tolerance Claim Suppression, ADR-3: Post-Generation Claim Verification, ADR-4: Self-Hosted NLI Model for Production Verification, Post-Generation Claim Verification, claude-haiku-4-5 (+3 more)

### Community 18 - "test_decompose.py"
Cohesion: 0.12
Nodes (22): hit(), plan(), parametrize, Decomposition: parsing a plan, routing it, and degrading when the plan is…, Routing gets a corpus into the pool; the floor stops the reranker taking it…, C5: A cites B and C; C cites D; E cites D; Z is unheld. Hops go either…, D3b: plain-English publications outrank the statute; a statute-only search puts…, Phase A's path is the floor: a bad plan must not fail a question the corpus can… (+14 more)

### Community 19 - "test_index.py"
Cohesion: 0.23
Nodes (15): chunks(), ctx(), models_(), fixture, CI starts with an empty Qdrant. The suite's "needs an ingested corpus" guard…, No corpus" and "no Qdrant" must not look alike: only the 404 is swallowed., sync(), test_a_broken_qdrant_still_raises() (+7 more)

### Community 20 - "paragraphs"
Cohesion: 0.18
Nodes (13): LTTextBox, fetch(), fold_numbers(), font_size(), get(), paragraphs(), Client, Path (+5 more)

### Community 23 - "retrieval.py"
Cohesion: 0.14
Nodes (23): argparse, datetime, dotenv, E4: apply the dev rules as written in tasks/todo.md, before looking at which…, cost_of(), estimate(), judge(), main() (+15 more)

### Community 24 - "test_metrics.py"
Cohesion: 0.10
Nodes (29): aggregate(), Judged, None when there is nothing to score: a refusal, or an answer making no claim., Refusals are excluded from the mean and reported separately (§9.2). Averaging a…, mrr(), ndcg_at_k(), recall_at_k(), math (+21 more)

### Community 26 - "jobs.py"
Cohesion: 0.24
Nodes (10): Redis, client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across…, One server-sent event. The blank line is the record separator., Append a stage to the record, then notify listeners. Record first: a listener… (+2 more)

### Community 27 - "test_verify.py"
Cohesion: 0.13
Nodes (8): taxcite, no_recite(), Claim verification (F4), tested without spending money: the verifier call is…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, Re-cite (F5b C3) ships on; tests that don't stub its call turn it off, and the…, structured_answer(), test_a_note_about_a_missing_detail_survives_when_its_part_is_shown(), test_sentence_hiding_ships()

### Community 28 - "decompose.py"
Cohesion: 0.16
Nodes (15): collections_abc, dataclasses, functools, SparseVector, neighbors(), Split a question into typed sub-queries, and route each to the sources that can…, Held opinions within `hops` citation steps of the seeds, in either direction;…, embed() (+7 more)

### Community 29 - "embed_bench.py"
Cohesion: 0.18
Nodes (11): build(), collection_for(), main(), ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, Index every chunk with one model into its own collection; returns build time., score(), qdrant_client, The section a citation belongs to, ignoring paragraph depth. '26 CFR… (+3 more)

### Community 30 - "store_bench.py"
Cohesion: 0.23
Nodes (11): load(), main(), pg_filtered(), pg_hybrid(), qd_filtered(), qd_hybrid(), ADR-17 revisit trigger: Qdrant against pgvector on identical data. uv run…, Top-k inside one section: approximate (HNSW) or exact (sequential scan). (+3 more)

### Community 31 - "TaxCite — Phase C exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+4 more)

### Community 32 - "e0_authority.py"
Cohesion: 0.14
Nodes (22): inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the…, Part 2: which authority fields have more than one value here, and from where. (+14 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "f5_golden.py"
Cohesion: 0.12
Nodes (30): A line that states no claim: a section heading, a markdown title, a label…, structural(), abstention(), audit(), check(), checkpoint(), save(), completeness() (+22 more)

### Community 35 - "citations.py"
Cohesion: 0.06
Nodes (54): eyecite, eyecite_models, FullCaseCitation, logging, load_selection(), The selection is cached so the corpus stays fixed while new opinions are filed., appeal(), appeal_label() (+46 more)

### Community 37 - "e3_sample.py"
Cohesion: 0.36
Nodes (8): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze()

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.20
Nodes (12): Postgres Service (pgvector/pgvector:pg16), Approximate Search Loses 22% Under a Strict Filter, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity, Bi-Temporal Fact Validity, Single-Engineer Operational Bus Factor (+4 more)

### Community 39 - "search"
Cohesion: 0.18
Nodes (17): Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, search(), hit(), RRF ties used to break differently per process, moving a chunk across the k…, The cross-encoder's job: an example that quotes a rule is not the rule., No final 280A regulations exist, so the home-office rules live only in Pub 587., test_dense_finds_the_hobby_loss_factor(), test_hybrid_returns_k_hits_with_payload() (+9 more)

### Community 40 - "generate.py"
Cohesion: 0.20
Nodes (15): Answer, answer_from_groups(), answer_from_hits(), cost(), effective_note(), format_sources(), _generate(), parse_citations() (+7 more)

### Community 41 - "Chunk"
Cohesion: 0.07
Nodes (44): Chunk, Stable primary key. A citation alone is not unique: one citation can need…, amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link() (+36 more)

### Community 42 - "verify"
Cohesion: 0.20
Nodes (10): (one verdict per shown sentence, input tokens, output tokens). One call for the…, verify(), A verifier stub that answers by prompt: SYSTEM gets the next of…, routed(), stub(), fake(), test_a_conclusion_is_shown_first_only_when_it_follows_from_the_sentences_that_passed(), test_checked_fails_closed_and_leaves_refusals_alone() (+2 more)

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "edition_filter"
Cohesion: 0.25
Nodes (8): Filter, edition_filter(), One source or several; several is how B7 routes a sub-query to the corpora that…, Keep chunks with no edition (everything but publications, and undated…, source_filter(), D3's filter, against Qdrant's own semantics (in-memory), not a re-…, test_edition_filter_keeps_undated_chunks_and_nearby_editions(), kept()

### Community 45 - "SubQuery"
Cohesion: 0.25
Nodes (5): merge(), parse(), (sub-queries, as_of, fallback reason). Never raises. A decomposition that…, One ranked list of k, round-robin across sub-queries, first occurrence wins.…, SubQuery

### Community 47 - "TaxCite: Phase E exit report"
Cohesion: 0.14
Nodes (13): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E2 and E3: the metadata, and the check that found law the parser didn't know, E4: the rerank, E5: authority in answers, Failures, with examples, Open problems handed on (+5 more)

### Community 50 - "TaxCite — Phase A exit report"
Cohesion: 0.29
Nodes (6): Decisions settled, with the evidence, Known failures, with examples, Recalibration notes for §9.3, TaxCite — Phase A exit report, The ablation ladder so far, What exists

### Community 51 - "ecfr.py"
Cohesion: 0.10
Nodes (44): estimate_tokens(), Make `part` a running count per citation, so `key` is unique by construction.…, renumber(), pages_label(), parse(), make(), Paragraphs packed up to MAX_TOKENS, each chunk opening with the previous…, Block (+36 more)

### Community 52 - "report"
Cohesion: 0.14
Nodes (13): abstention(), claim_unit(), f1(), Overlapping word windows covering the whole chunk: the last one starts at or…, On the not-supported class: what the verifier exists to catch. `supported` is…, The threshold that maximises not-supported F1 on the tune half. Ties go to the…, The small model decides only what it's sure of, the LLM the rest. Auto-accept…, Each F0 unit (cited chunks only) against today's faithfulness (LLM-extracted… (+5 more)

### Community 53 - "main"
Cohesion: 0.20
Nodes (11): agreement(), check_sheet(), judge(), call(), main(), nli(), premise(), Judge each pair against `field`'s chunks into `out`. The main pass reads every… (+3 more)

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "api.py"
Cohesion: 0.14
Nodes (16): asyncio, BackgroundTasks, BaseModel, fastapi, fastapi_responses, post, pydantic, Response (+8 more)

### Community 58 - "main"
Cohesion: 0.33
Nodes (3): main(), needs_case_law(), A row whose gold includes an opinion: routing must send a sub-query to the case…

### Community 59 - "ingest_ecfr"
Cohesion: 0.34
Nodes (16): Connection, Namespace, ingest_case(), ingest_ecfr(), ingest_pubs(), ingest_usc(), load_citations(), main() (+8 more)

### Community 60 - "TaxCite: Phase F exit report"
Cohesion: 0.25
Nodes (7): Golden, scored once on the shipped pipeline, How the phase went, Open, for later phases, Reproducing, TaxCite: Phase F exit report, The gates, What Phase F got wrong

### Community 61 - "verify.py"
Cohesion: 0.16
Nodes (19): What exists, apply(), checked(), conclude(), displayed(), _json(), premises(), prompt() (+11 more)

### Community 62 - "store.py"
Cohesion: 0.33
Nodes (6): psycopg, psycopg_types_json, held_at(), datetime, Postgres storage for chunks. One table, created on demand. Writes are…, (key, text) TaxCite held for `citation` at `at`, current or since retired (D6).

### Community 64 - "cli.py"
Cohesion: 0.23
Nodes (12): collections, httpx, io, pdfminer_high_level, pdfminer_layout, re, The unit every ingester produces and every store consumes., Command line: fetch, parse, store and index the corpora. taxcite ingest ecfr… (+4 more)

### Community 65 - "answer"
Cohesion: 0.15
Nodes (17): Reproducing, answer(), chunks(), citation_graph(), decompose(), Decomposition, (sub-query, its chunks) for the synthesis prompt, limited to `keep` if given.…, One structured-output call (ADR-11). Temperature 0 and a fixed seed, so a re-… (+9 more)

### Community 66 - "call_model"
Cohesion: 0.29
Nodes (7): call_model(), MissingCredentials, RuntimeError, Raised instead of the SDK's generic auth error, which does not say what to set., Fail early and specifically. The SDK raises a generic TypeError at request…, One completion. Returns (text, input_tokens, output_tokens). The two providers…, _require_credentials()

### Community 67 - "fetch"
Cohesion: 0.40
Nodes (5): fetch(), fetch_usc(), Path, Title 26 USLM XML for a release point (default: the current one), cached on…, Download one part (or a single section) of Title 26, cached on disk. The API…

### Community 68 - "refusals_ok"
Cohesion: 0.50
Nodes (4): Refusals sit outside the faithfulness mean (see `aggregate`), so a build that…, refusals_ok(), D7's first build: faithfulness passed at 0.866 while refusing more than half…, test_refusal_rate_gate()

### Community 69 - "conn"
Cohesion: 0.31
Nodes (9): get, get_query(), Server-sent events for one job. Replays whatever the record already holds, then…, stream_events(), events(), get(), StreamingResponse, conn() (+1 more)

### Community 70 - "f4_hide.py"
Cohesion: 0.33
Nodes (9): base(), check_sheet(), main(), metrics(), F4: one verified run, shown three ways, so the hiding unit is decided on…, The cached answer as the verifier saw it: every cited item shown., The cache entry as `unit` would show it., Half failed, half passed verdicts, one per answer; the verdict under a fold,… (+1 more)

### Community 71 - "suppression"
Cohesion: 0.50
Nodes (4): Sentences no pair of this unit covers: every uncited one for sentences, only…, What ADR-15 would hide over answers that weren't refusals, for one claim unit.…, suppression(), uncited()

### Community 75 - "snapshot.py"
Cohesion: 0.33
Nodes (8): create(), main(), Path, Freeze the corpus so CI can retrieve against it without a 90-minute ingest. The…, restore(), os, client(), subprocess

## Knowledge Gaps
- **205 isolated node(s):** `taxcite`, `What exists`, `The ablation ladder`, `Phase C's baseline`, `Faithfulness` (+200 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 607 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `cli.py`, `test_irs_pubs.py`, `test_ecfr.py`, `ecfr.py`, `ingest_ecfr`, `store.py`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `Chunk` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `Chunk`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **What connects `taxcite`, `What exists`, `The ablation ladder` to the rest of the system?**
  _205 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_irs_pubs.py` be split into smaller, more focused modules?**
  _Cohesion score 0.061170212765957445 - nodes in this community are weakly interconnected._
- **Should `test_jobs.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08266129032258064 - nodes in this community are weakly interconnected._
- **Should `T2: Ingest eCFR Title 26` be split into smaller, more focused modules?**
  _Cohesion score 0.1286549707602339 - nodes in this community are weakly interconnected._