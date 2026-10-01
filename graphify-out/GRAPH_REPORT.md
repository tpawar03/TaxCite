# Graph Report - TaxCite.nosync  (2026-10-01)

## Corpus Check
- 248 files · ~14,903,612 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 3, .jsonl 3, .xml 3)

## Summary
- 1406 nodes · 2667 edges · 77 communities (65 shown, 12 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 194 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `89e754e0`
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
- caselaw.py
- taxcite
- Collaborative Working Mode
- temporal.py
- test_metrics.py
- Postgres
- jobs.py
- test_verify.py
- usc.py
- parse
- retrieval.py
- TaxCite — Phase C exit report
- e0_authority.py
- ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements
- f5_golden.py
- history
- Plain-Module Package Layout
- e3_sample.py
- ADR-17: Vector Store — Qdrant, Not pgvector
- search
- generate.py
- usc_notes.py
- test_temporal.py
- TaxCite — Phase D exit report
- TaxCite — Status
- appeal
- taxcite_ingest_caselaw
- TaxCite: Phase E exit report
- taxcite_ingest
- taxcite_ingest_citations
- audit
- ecfr.py
- report
- citations.py
- F4 verdict check
- F0 judge check
- taxcite_ingest_ecfr
- api.py
- main
- cli.py
- is_appeal
- verify
- material
- taxcite_ingest_irs_pubs
- run
- decompose.py
- post_query
- ruling
- nli
- conn
- base
- flags
- estimate_tokens
- test_fetch_rejects_a_non_pdf
- RuntimeError
- client
- fixture

## God Nodes (most connected - your core abstractions)
1. `F0 judge check` - 41 edges
2. `F5 reference check` - 41 edges
3. `Hit` - 34 edges
4. `F4 verdict check` - 31 edges
5. `search()` - 28 edges
6. `Chunk` - 24 edges
7. `conn()` - 23 edges
8. `Answer` - 17 edges
9. `verify()` - 16 edges
10. `run()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `E2 and E3: the metadata, and the check that found law the parser didn't know` --references--> `save()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/store.py
- `What exists` --references--> `authority()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/chunk.py
- `Reproducing` --references--> `answer_from_groups()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/generate.py
- `What exists` --references--> `authorities()`  [INFERRED]
  eval/results/phase_e.md → src/taxcite/generate.py
- `Reproducing` --references--> `flags()`  [INFERRED]
  eval/results/phase_c.md → src/taxcite/ingest/citations.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Answer-Correctness Gate Stack** — taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_authority_aware_retrieval, taxcite_technical_documentation_adr_7, taxcite_technical_documentation_adr_15, taxcite_technical_documentation_adr_4 [EXTRACTED 1.00]
- **Phase A Decisions Settled by Measurement** — taxcite_technical_documentation_adr_11, taxcite_technical_documentation_adr_17, taxcite_technical_documentation_adr_18, eval_results_phase_a_exit_report, status_phase_a_complete [EXTRACTED 1.00]

## Communities (77 total, 12 thin omitted)

### Community 0 - "index.py"
Cohesion: 0.13
Nodes (26): QdrantClient, authority(), expiry(), The chunk's authority profile (E2): from its source and the citation's form,…, `source_revision` where the ingester had none (E2): what `as_of` already…, whole' or 'partly' when a regulation's own clause says its applicability ended…, revision(), backfill_authority() (+18 more)

### Community 1 - "test_irs_pubs.py"
Cohesion: 0.14
Nodes (20): _normalise(), Sliding windows with overlap; a short page yields a single window., Drop lines that repeat across most pages at the top or bottom of the page.…, strip_boilerplate(), clean(), edge_count(), edges(), windows() (+12 more)

### Community 2 - "test_jobs.py"
Cohesion: 0.07
Nodes (30): fastapi_testclient, pytest, clean(), fixture, Job record and SSE transport (ADR-9), with the pipeline stubbed., ADR-9: nothing unverified reaches the user, so the answer is buffered., ADR-16: Redis carries progress; the record is the source of truth behind it., A Redis outage must degrade liveness, not correctness (ADR-16). (+22 more)

### Community 3 - "T2: Ingest eCFR Title 26"
Cohesion: 0.16
Nodes (15): eCFR Chunking Decisions, Nine-Section eCFR Test Fixture, T2: Ingest eCFR Title 26, T5: Ingest IRS Publications, T6: Embedding-Model Benchmark, Harvard Caselaw Access Project, Per-Document-Type Chunker (§3.2), CourtListener (+7 more)

### Community 4 - "ragas_eval.py"
Cohesion: 0.10
Nodes (29): aggregate(), Budget, CostCap, extract_claims(), judge_claims(), Judged, main(), pipeline_answer() (+21 more)

### Community 5 - "test_ecfr.py"
Cohesion: 0.06
Nodes (45): Element, designations(), in_scope(), level_of(), parse(), True when a section is one of these prefixes, or a numbered child of one.…, Every chunk in an eCFR XML file or element tree., 1 for a level-1 letter, 2 for a level-2 number, None for anything deeper.… (+37 more)

### Community 6 - "TaxCite — Phase B exit report"
Cohesion: 0.18
Nodes (10): §9.3 recalibration, Abstention, Failures, with examples, Faithfulness, Phase C's baseline, Reproducing, TaxCite — Phase B exit report, The ablation ladder (+2 more)

### Community 7 - "f0_verify.py"
Cohesion: 0.12
Nodes (24): concurrent_futures, agreement(), build(), check_sheet(), claim_text(), contains(), judge(), call() (+16 more)

### Community 8 - "test_store.py"
Cohesion: 0.08
Nodes (31): chunks(), parametrize, Transaction time (D6): an amendment rewrites a chunk in place; the old text…, test_a_dropped_paragraph_is_retired_by_the_sweep(), test_an_unchanged_reingest_keeps_its_recorded_time_and_retires_nothing(), test_authority_profile_comes_from_source_and_citation_form(), test_excluded_rows_are_stored_but_not_counted_as_indexable(), test_expiry_reads_a_regulations_own_clause_against_the_snapshot_date() (+23 more)

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

### Community 20 - "caselaw.py"
Cohesion: 0.12
Nodes (24): collections, httpx, LTTextBox, pdfminer_high_level, pdfminer_layout, re, fetch(), fold_numbers() (+16 more)

### Community 23 - "temporal.py"
Cohesion: 0.13
Nodes (20): argparse, dotenv, E4: apply the dev rules as written in tasks/todo.md, before looking at which…, F4: one verified run, shown three ways, so the hiding unit is decided on…, cost_of(), estimate(), judge(), main() (+12 more)

### Community 24 - "test_metrics.py"
Cohesion: 0.08
Nodes (35): main(), score(), mrr(), ndcg_at_k(), recall_at_k(), math, The section a citation belongs to, ignoring paragraph depth. '26 CFR…, section_of() (+27 more)

### Community 26 - "jobs.py"
Cohesion: 0.13
Nodes (19): dataclasses, Redis, RuntimeError, client(), Event, notify(), publish(), Durable job records for the query pipeline (ADR-9). A query takes 20-30s across… (+11 more)

### Community 27 - "test_verify.py"
Cohesion: 0.09
Nodes (17): fixture, taxcite, no_recite(), Claim verification (F4), tested without spending money: the verifier call is…, F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part"…, A verifier stub that answers by prompt: SYSTEM gets the next of…, Re-cite (F5b C3) ships on; tests that don't stub its call turn it off, and the…, routed() (+9 more)

### Community 28 - "usc.py"
Cohesion: 0.27
Nodes (16): blocks(), child_text(), chunk_section(), clean(), designation(), lead_in(), parse(), provision_blocks() (+8 more)

### Community 29 - "parse"
Cohesion: 0.14
Nodes (16): skipif, edition_year(), fetch(), page_texts(), parse(), Path, Every chunk in one publication PDF., Download one publication, cached on disk. `delay` rate-limits bulk fetches. (+8 more)

### Community 30 - "retrieval.py"
Cohesion: 0.11
Nodes (24): datetime, build(), collection_for(), ADR-18: choose the dense embedding model by measuring it on the pilot set. uv…, Index every chunk with one model into its own collection; returns build time., Score retrieval against the pilot set: the first rungs of the §9 ablation…, load(), main() (+16 more)

### Community 31 - "TaxCite — Phase C exit report"
Cohesion: 0.15
Nodes (12): §9.3 recalibration, C0: the ceiling, before building, Extraction quality, Failures, with examples, How the case-law baseline moved, Open problems handed on, TaxCite — Phase C exit report, The gate (+4 more)

### Community 32 - "e0_authority.py"
Cohesion: 0.12
Nodes (25): inventory(), kind(), level(), main(), mean_sd(), E0: where does authority cost retrieval, and which authority fields vary in…, One row at one depth. Per gold group: its highest authority, its rank in the…, Part 2: which authority fields have more than one value here, and from where. (+17 more)

### Community 33 - "ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements"
Cohesion: 0.33
Nodes (6): ADR-13: Sanitized Rendering Only, Structured Fields for UI Elements, ADR-14: Model-Boundary Prompt-Injection Defense, ADR-5: Shared Corpus + Per-Tenant Namespace, Phase G — Multi-Tenant + Hardening, Sanitized-Rendering Contract, Client-Upload Threat Model

### Community 34 - "f5_golden.py"
Cohesion: 0.18
Nodes (19): abstention(), check(), completeness(), ladder(), latency(), load(), main(), F5: Phase F scored on golden, from one run of the shipped pipeline. uv run… (+11 more)

### Community 35 - "history"
Cohesion: 0.19
Nodes (13): FullCaseCitation, full_cites(), history(), label(), The year in the parenthetical right after the cite. eyecite's own guess can…, Explanatory parentheticals push "aff'd" past the window: "113 T.C. 254 (1999)…, The appeal as one stable string, "560 F.3d 620 (ca7 2009)": no case name or pin…, (opinion, kind, by) from subsequent history in a passage. by is the appellate… (+5 more)

### Community 37 - "e3_sample.py"
Cohesion: 0.33
Nodes (9): caption(), main(), one_per_opinion(), page(), E3: draw the stratified 150-chunk sample for the authority hand check, with its…, The source of truth in the opinion's own text: does it carry its citation form,…, rows(), squeeze() (+1 more)

### Community 38 - "ADR-17: Vector Store — Qdrant, Not pgvector"
Cohesion: 0.15
Nodes (16): Postgres Service (pgvector/pgvector:pg16), Qdrant Service (compose), Approximate Search Loses 22% Under a Strict Filter, Repository Map, T6b: Qdrant vs pgvector Benchmark, ADR-12: Backup and Disaster Recovery, ADR-17: Vector Store — Qdrant, Not pgvector, ADR-2: Bi-Temporal Fact Validity (+8 more)

### Community 39 - "search"
Cohesion: 0.11
Nodes (25): Filter, edition_filter(), Top-k chunks for a query. Modes are the rungs of the eval ablation ladder (§9):…, One source or several; several is how B7 routes a sub-query to the corpora that…, Keep chunks with no edition (everything but publications, and undated…, search(), source_filter(), hit() (+17 more)

### Community 40 - "generate.py"
Cohesion: 0.11
Nodes (27): collections_abc, Answer, answer_from_groups(), answer_from_hits(), answer_schema(), authority_label(), call_model(), effective_note() (+19 more)

### Community 41 - "usc_notes.py"
Cohesion: 0.06
Nodes (43): amendment_entries(), clause_for(), covers(), effective_rule(), evidenced(), link(), notes(), own_designation() (+35 more)

### Community 42 - "test_temporal.py"
Cohesion: 0.13
Nodes (15): as_of_match(), kappa(), passed(), Year-level match of the plan's as-of against the row's tax year. None = not…, Cohen's kappa for two raters over the same items., Per sample index: rates over the rows, first judge repeat (E5). Conflict and…, sample_summary(), parametrize (+7 more)

### Community 43 - "TaxCite — Phase D exit report"
Cohesion: 0.12
Nodes (15): §9.3 recalibration, A gate that passed while the system refused half its questions, D0: what the rows needed, before building, Effective dates (D4), Failures, with examples, Open problems handed on, Reproducing, TaxCite — Phase D exit report (+7 more)

### Community 44 - "TaxCite — Status"
Cohesion: 0.22
Nodes (8): Stable primary key. A citation alone is not unique: one citation can need…, Decisions Log, Environment, Findings worth remembering, Now, Pending housekeeping, Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`), TaxCite — Status

### Community 45 - "appeal"
Cohesion: 0.25
Nodes (9): appeal(), appeal_label(), cached(), get(), Client, Path, One format for both sources, so a reader sees the same appeal the same way., A response cached with the time it was fetched: re-running from cache must not… (+1 more)

### Community 47 - "TaxCite: Phase E exit report"
Cohesion: 0.12
Nodes (16): §9.3 recalibration, E0: where authority costs, before building, E1: the rows that decide it, E2 and E3: the metadata, and the check that found law the parser didn't know, E4: the rerank, E5: authority in answers, Failures, with examples, Reproducing (+8 more)

### Community 50 - "audit"
Cohesion: 0.22
Nodes (13): headings(), Each cached chunk's heading, which synthesis saw ("[citation] (heading)") but…, audit(), checkpoint(), save(), judge(), (done, save, path): results already paid for in a crashed run, and a function…, verify.verify's call, on given items and with another model; low effort, since… (+5 more)

### Community 51 - "ecfr.py"
Cohesion: 0.16
Nodes (25): Chunk, The unit every ingester produces and every store consumes., Make `part` a running count per citation, so `key` is unique by construction.…, §7805(e)(2): a temporary regulation issued after Nov. 20, 1988 expires within 3…, renumber(), sunset(), Block, blocks() (+17 more)

### Community 52 - "report"
Cohesion: 0.12
Nodes (15): abstention(), claim_unit(), f1(), On the not-supported class: what the verifier exists to catch. `supported` is…, The threshold that maximises not-supported F1 on the tune half. Ties go to the…, The small model decides only what it's sure of, the LLM the rest. Auto-accept…, Sentences no pair of this unit covers: every uncited one for sentences, only…, What ADR-15 would hide over answers that weren't refusals, for one claim unit.… (+7 more)

### Community 53 - "citations.py"
Cohesion: 0.20
Nodes (13): eyecite, eyecite_models, logging, load_selection(), The selection is cached so the corpus stays fixed while new opinions are filed., cites(), load(), normalize() (+5 more)

### Community 54 - "F4 verdict check"
Cohesion: 0.06
Nodes (31): F4 verdict check, V01, V02, V03, V04, V05, V06, V07 (+23 more)

### Community 55 - "F0 judge check"
Cohesion: 0.05
Nodes (41): F0 judge check, P01 `G-C20#0#0s`, P02 `G-C05#1#0s`, P03 `G-X19#1#0`, P04 `G-X07#3#0s`, P05 `G-C26#2#0`, P06 `G-C12#0#0`, P07 `G-C03#1#1s` (+33 more)

### Community 57 - "api.py"
Cohesion: 0.16
Nodes (14): asyncio, fastapi, fastapi_responses, os, psycopg, psycopg_types_json, pydantic, Response (+6 more)

### Community 58 - "main"
Cohesion: 0.25
Nodes (3): main(), needs_case_law(), A row whose gold includes an opinion: routing must send a sub-query to the case…

### Community 59 - "cli.py"
Cohesion: 0.18
Nodes (26): Connection, io, Namespace, backfill_authority(), fetch(), fetch_usc(), ingest_case(), ingest_ecfr() (+18 more)

### Community 60 - "is_appeal"
Cohesion: 0.32
Nodes (8): is_appeal(), party(), petitioners(), The petitioners' names alone: "Estate of James E. Caan, Deceased, …,…, Family names in a joint caption. "C. Michael & Gwendolyn E. Willock" is one…, A caseName query for the appellate caption: surnames for people ("Donald B. &…, Same-name appeals are common (C1: three unrelated Michaels for Willock). A real…, surnames()

### Community 61 - "verify"
Cohesion: 0.13
Nodes (23): Answer, cited_items(), parse_citations(), The sentences a structured answer can show, in order: text and at least one…, (answer text, sentences dropped) from arm E's JSON. Each sentence ends with its…, Split the answer's citations three ways: exact, derived, unsupported. The three…, render(), apply() (+15 more)

### Community 62 - "material"
Cohesion: 0.33
Nodes (6): material(), Completeness over material sentences, and the share of answers that would…, Split outside brackets, at . ! ? followed by a space, never after an…, A line that states no claim: a section heading, a markdown title, a label…, sentences(), structural()

### Community 64 - "run"
Cohesion: 0.20
Nodes (11): Reproducing, decompose(), One structured-output call (ADR-11). Temperature 0 and a fixed seed, so a re-…, authorities(), Each cited source's authority and label, for the API (E5): an exact citation…, F2: every part judged insufficient before synthesis. A refusal with what each…, skipped_only(), The pipeline, reporting each stage. Phases C-F add their steps here. (+3 more)

### Community 65 - "decompose.py"
Cohesion: 0.08
Nodes (36): functools, answer(), chunks(), citation_graph(), Decomposition, gate(), level(), merge() (+28 more)

### Community 66 - "post_query"
Cohesion: 0.22
Nodes (9): BackgroundTasks, BaseModel, post, post_query(), Query, Accept a question and return immediately (ADR-9). The pipeline runs 20-30s,…, _run_job(), create() (+1 more)

### Community 67 - "ruling"
Cohesion: 0.40
Nodes (5): kind(), A mixed disposition takes its most serious part: "aff'd in part, rev'd in part"…, The outcome in an appellate opinion's last disposition sentence, or None (e.g.…, ruling(), split()

### Community 68 - "nli"
Cohesion: 0.22
Nodes (8): nli(), Overlapping word windows covering the whole chunk: the last one starts at or…, P(entailed) per pair: the best window of the best cited chunk. Looser than the…, windows(), Loaded once per process and per model, like the embedding models., The cross-encoder is deterministic, so a pool scored once needn't be scored…, _reranker(), _scores()

### Community 69 - "conn"
Cohesion: 0.31
Nodes (9): get, get_query(), Server-sent events for one job. Replays whatever the record already holds, then…, stream_events(), events(), get(), StreamingResponse, conn() (+1 more)

### Community 70 - "base"
Cohesion: 0.28
Nodes (9): base(), check_sheet(), main(), metrics(), Path, The cached answer as the verifier saw it: every cited item shown., The cache entry as `unit` would show it., Half failed, half passed verdicts, one per answer; the verdict under a fold,… (+1 more)

### Community 71 - "flags"
Cohesion: 0.33
Nodes (7): Open problems handed on, flag(), flags(), opinion_chunks(), datetime, One opinion's treatment flag from its (source, kind, by, checked_at) rows (C4).…, Treatment flags for the opinions an answer cites. Fails open: if the table…

### Community 72 - "estimate_tokens"
Cohesion: 0.33
Nodes (7): estimate_tokens(), pages_label(), parse(), make(), Paragraphs packed up to MAX_TOKENS, each chunk opening with the previous…, make(), make()

### Community 75 - "client"
Cohesion: 0.60
Nodes (5): create(), main(), Path, restore(), client()

## Knowledge Gaps
- **199 isolated node(s):** `✅ Checkpoint 1 — after T1–T3`, `✅ Checkpoint 2 — after T4–T6`, `✅ Checkpoint 3 — after T7–T8`, `✅ Checkpoint: Phase A complete`, `T2: Ingest eCFR Title 26 into Postgres + Qdrant` (+194 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 661 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `ecfr.py` to `index.py`, `test_ecfr.py`, `estimate_tokens`, `usc_notes.py`, `TaxCite — Status`, `caselaw.py`, `api.py`, `usc.py`, `parse`?**
  _High betweenness centrality (0.189) - this node is a cross-community bridge._
- **Why does `Decisions Log` connect `TaxCite — Status` to `T2: Ingest eCFR Title 26`?**
  _High betweenness centrality (0.173) - this node is a cross-community bridge._
- **Why does `eCFR Chunking Decisions` connect `T2: Ingest eCFR Title 26` to `TaxCite — Status`, `ADR-17: Vector Store — Qdrant, Not pgvector`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `Hit` (e.g. with `base()` and `chunks()`) actually correct?**
  _`Hit` has 27 INFERRED edges - model-reasoned connections that need verification._
- **What connects `✅ Checkpoint 1 — after T1–T3`, `✅ Checkpoint 2 — after T4–T6`, `✅ Checkpoint 3 — after T7–T8` to the rest of the system?**
  _199 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12535612535612536 - nodes in this community are weakly interconnected._
- **Should `test_irs_pubs.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._