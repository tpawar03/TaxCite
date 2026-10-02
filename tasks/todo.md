# TaxCite Phase A — Task List

Plan: `tasks/plan.md`. Test command: `uv run pytest -q`. Every task leaves the repo runnable.

---

## T1: Local stack and package skeleton

**Description:** Add a `docker-compose.yml` with Qdrant, Postgres 16 and Redis. Rename the package to `taxcite` under `src/taxcite/` and add the Phase A dependencies. Add a FastAPI app with `/health` that checks all three stores.

**Acceptance criteria:**
- [x] `docker compose up -d` starts all three services
- [x] `GET /health` returns 200 with `{qdrant, postgres, redis: "ok"}`, and a failing store shows as not ok
- [x] `main.py` stub removed; `uv run uvicorn taxcite.api:app` works

**Verification:**
- [x] `uv run pytest -q` passes (health test against the running stack)
- [x] Manual: `curl localhost:8000/health`

**Dependencies:** None
**Files:** `docker-compose.yml`, `pyproject.toml`, `src/taxcite/__init__.py`, `src/taxcite/api.py`, `tests/test_health.py`, `.env.example`
**Scope:** S

---

## T2: Ingest eCFR Title 26 into Postgres + Qdrant

**Description:** Fetch 26 CFR from the eCFR API (no key needed) and parse it into section-level chunks (200–500 tokens, no overlap, parent-section metadata kept). Write chunk metadata to Postgres (`chunks` table: id, source, citation, part, section, heading, text, retrieved_at). Write dense + sparse vectors to one Qdrant collection. Re-running is idempotent (upsert by citation).

**Chunking decisions (2026-09-19, from exploring the Part 1 data: 3,774 sections, median ~1,000 words, 74% over 500 tokens):**
- Split at paragraph level 1 (`(a)`), and at level 2 (`(1)`) only when a level-1 unit is over ~500 tokens. Pack consecutive units up to ~500. Citation is the section plus the paragraph, e.g. `26 CFR 1.704-1(b)(2)`. When one `P` opens both levels (`(a) <I>Heading.</I> (1) …`), the first split piece is cited `(a)(1)`.
- Sections under 200 tokens are kept whole and never merged across sections. `[Reserved]` sections are skipped.
- Tables with ≤100 cells are flattened into text rows. Larger tables get no embedding and are recorded with the reason `large_table`.
- `CITA` (amendment history) is stored raw in its own column and not embedded. Every chunk stores the eCFR as-of date and the download time.
- Token counts are estimated as words × 1.3.
- Each chunk carries `source` (`ecfr` here, `irs_pub` in T5) so the corpora stay separable for filtering and for T6b's filtered-search benchmark. `fetched_at` is set by the store layer; `as_of` comes from the parser. No tenant field: 26 CFR is the shared public corpus (ADR-5), and per-tenant isolation only applies to client documents in Phase G.
- Chunks are keyed on `(citation, part)`; one citation can need several chunks.
- `[Reserved]` **paragraphs** are dropped, like reserved sections (they are cross-reference stubs: "(i) [Reserved]. For further guidance, see § 1.42-1T(i)").
- Table-of-contents sections (heading contains "Table of contents"; 178 sections, ~158k words, ~4% of Part 1) are skipped and recorded with `excluded = "toc"`. Test the heading, not the `-0` suffix: `1.954-0` is "Introduction", not a TOC.
- The designation parser reads **all** leading designations in a paragraph, so `(b)(1) …` opens level 1 `(b)` and level 2 `(1)`, exactly like `(a) <I>Heading.</I> (1) …`.

**Fixture (built 2026-09-19, `tests/fixtures/ecfr_sample.xml`, 9 real sections, 58 KB):** `1.642(e)-1` short section · `1.42-2` reserved · `1.30C-1 - 1.30C-2` reserved with a range `N` · `1.904(f)-4` packing (a)–(d) with an EXAMPLE · `1.707-9` combined `(a) …(1)` with an oversized `(a)` · `1.42-1` `(i)` after `(h)` is a letter · `1.704-1T` `(i)` after `(b)(1)` is a Roman numeral, plus italic `(<I>a</I>)` · `1.280F-7` one 617-cell table excluded and three small ones flattened · `1.641(c)-0` table of contents.

**Acceptance criteria:**
- [x] `uv run taxcite ingest ecfr --only pilot` loads the Phase A subset (4,969 chunks); Postgres indexable 4,917 = Qdrant 4,917
- [x] Every chunk has a paragraph-level citation and is ≤ ~500 estimated tokens, except single paragraphs that can't be split further
- [x] Running ingest again does not create duplicates (re-run stored the same 4,969 and swept 25 stale points)

**Verification:**
- [x] `uv run pytest -q` — 41 tests over the 9-section fixture plus store/index integration
- [x] Manual: 3 chunks spot-checked against the live ecfr.gov API

**Done 2026-09-19.** Scoped to 21 section prefixes (~5,000 chunks, 13 min) instead of all of Part 1 (43,583 chunks, ~105 min), to keep the T6 model-comparison loop fast; the full run is `--only` omitted, after the embedding model is chosen.

**Dependencies:** T1
**Files:** `src/taxcite/ingest/ecfr.py`, `src/taxcite/store.py`, `src/taxcite/cli.py`, `tests/fixtures/ecfr_sample.xml`, `tests/test_ecfr.py`
**Scope:** M

---

## T3: Hybrid search CLI with citations

**Description:** Add a `search(query, k, mode)` function: embed the query dense + sparse, run a Qdrant hybrid query with fusion, and return chunks with their citations. `mode` is `dense | hybrid` for the later ablation. Expose it as `taxcite search`.

**Acceptance criteria:**
- [x] `taxcite search "nine factors for determining profit motive" -k 5` prints ranked citations and snippets (all five from §1.183-2)
- [x] `--mode dense`, `--mode sparse` and `--mode hybrid` all work and disagree on at least one query

**Verification:**
- [x] `uv run pytest -q` — 47 tests, including dense finding §1.183-2(b)(3) and sparse finding §1.280F
- [x] Manual: 3 questions checked. One excellent (profit-motive factors), two mediocre — see the subset gap below

**Done 2026-09-20.** Added a `sparse` mode for the §9 ablation ladder. Fixed a real bug: the sparse vectors lacked Qdrant's IDF modifier, so BM25 could not down-weight common words. **Follow-up for T4:** the manual checks showed §1.263(a) (capitalization) missing from the pilot subset, and question-style queries retrieving worse than keyword-style ones.

**Dependencies:** T2
**Files:** `src/taxcite/retrieve.py`, `src/taxcite/cli.py`, `tests/test_retrieve.py`
**Scope:** S

---

## ✅ Checkpoint 1 — after T1–T3
- [ ] Tests pass
- [ ] Regulation retrieval works end to end from the CLI
- [ ] Review with the user before labeling the pilot set

---

## T4: Pilot set (20 questions) and retrieval eval script

**Description:** Draft 20 questions answerable from 26 CFR and IRS Publications, each with gold citations and a short reference answer, saved to `eval/pilot.jsonl`. The user reviews and approves every row. Add `eval/retrieval.py`, which computes Recall@10, nDCG@10 and MRR per mode and writes the results to `eval/results/`.

**Acceptance criteria:**
- [x] 20 rows: 16 regulation (scorable now), 2 publication (scorable after T5), 2 abstention
- [x] `uv run python eval/retrieval.py` scores all three modes and writes `eval/results/retrieval-<date>-k10.json`
- [x] Metric functions checked against hand calculations in `tests/test_metrics.py` (7 tests)

**Verification:**
- [x] `uv run pytest -q` — 54 tests
- [x] `uv run python eval/validate_pilot.py` — 0 problems, 4 known-hard gold citations

**Done 2026-09-20.** First numbers (k=10): hybrid Recall 0.812 / nDCG 0.468, dense 0.719 / 0.445, sparse 0.500 / 0.387. Section recall 1.000 vs strict 0.812 = the reranking headroom. Gold verified against regulation text, **not** reviewed by a tax professional; validation caught a wrong citation and two incomplete answers.

**Dependencies:** T3 (T5 is needed before the publication questions can be scored)
**Files:** `eval/pilot.jsonl`, `eval/retrieval.py`, `tests/test_metrics.py`
**Scope:** M

---

## T5: Ingest IRS Publications

**Description:** Download a fixed list of IRS pubs relevant to the pilot set (e.g. 587, 463, 17, 334, 535) from irs.gov/pub, using a rate-limited client with an identifying user-agent that respects robots.txt. Extract text with `pypdf` and chunk it into ~300-token windows with 15% overlap, cited as `IRS Pub N (YYYY), p. X`. Pages that fail extraction are marked `extraction_failed` and excluded.

**Acceptance criteria:**
- [x] `taxcite ingest irs-pubs` loads 587, 463, 17, 334, 946, 527 — 2,083 chunks, page-level citations, 0 failed pages
- [x] Failed extractions are recorded with `extraction_failed`; a non-PDF download is rejected outright
- [x] P17 and P18 are scorable; the eval re-runs over 18 questions

**Verification:**
- [x] `uv run pytest -q` — 71 tests, including window overlap, boilerplate removal and the non-PDF download
- [x] Manual: gold chunks for P17/P18 read against the source text

**Done 2026-09-20.** Text comes from pdfminer.six, not pypdf. Pub 535 is discontinued and its URL returns HTTP 200 with HTML, so downloads are validated by content; 946 and 527 replace it. **Key result:** adding publications cut hybrid recall on the *same 16 regulation questions* from 0.812 to 0.688, because plain-English guidance outranks binding law — the measured case for Phase E authority-aware reranking.

**Dependencies:** T2 (reuses the store); can run in parallel with T3/T4
**Files:** `src/taxcite/ingest/irs_pubs.py`, `tests/test_irs_pubs.py`, `tests/fixtures/pub_sample.pdf`
**Scope:** S

---

## T6: Embedding-model benchmark and decision

**Description:** Re-index a fixed benchmark subset (the Parts and pubs the pilot set touches, plus distractors) once per candidate model, with ≥2 candidates: `bge-small-en-v1.5` vs. `nomic-embed-text-v1.5`. Run T4's eval for dense and hybrid with each model. Write the results into §3.2 of the tech doc as a new ADR entry (ADR-18: embedding model).

**Acceptance criteria:**
- [x] Results table: model × mode → Recall@10, nDCG@10, MRR, section recall, per-category recall, latency, index time, vector size
- [x] ADR-18 written; `DENSE_MODEL` set to `BAAI/bge-base-en-v1.5`, `DENSE_DIM` to 768

**Verification:**
- [x] User approved bge-base (2026-09-20)

**Done 2026-09-20.** bge-base beat bge-small on every quality metric (hybrid recall 0.667 vs 0.611, nDCG 0.350 vs 0.259, dense MRR 0.315 vs 0.185) at 3.4x index time (31.6 vs 9.3 min) and 2x storage (24 vs 12 MB). nomic was excluded on latency before any quality measurement (491 ms/query). Dense scores 0.000 on publication questions for both models — publications match lexically, not semantically.

**Dependencies:** T4, T5
**Files:** `eval/embed_bench.py`, `taxcite-technical-documentation.md`, `eval/results/embed_bench.md`
**Scope:** S

---

## T6b: ADR-17 revisit trigger — Qdrant vs. pgvector

**Description:** Load the same benchmark subset, with the same winning embeddings from T6, into pgvector. Switch the compose image to `pgvector/pgvector:pg16`, which is Postgres 16 with the extension, and store the vectors in a separate `bench_chunks` table so app tables are untouched. Hybrid search on the pgvector side uses `sparsevec` or Postgres full-text search, with RRF fusion in SQL. Compare the two stores on (1) pilot-set Recall@10/nDCG@10 for hybrid search, (2) filtered-recall loss: for each pilot question, run approximate search with a strict filter (a single CFR Part or a single IRS pub) and measure recall@10 against an exact brute-force search under the same filter, (3) p95 query latency, and (4) on-disk index size, projected to the full Phase A–C corpus against the Supabase free-tier storage cap. Record the numbers in ADR-17 and apply its revisit rule.

**Acceptance criteria:**
- [x] Results table: store × {hybrid recall, dense-only, lexical-only, filtered recall, p50/p95, storage, projected}
- [x] ADR-17 outcome recorded: **confirmed, Qdrant stays** — and the trigger corrected, since as written both its conditions passed
- [x] App tables and the live collection untouched (`bench_chunks` table, `bench_*` collections)

**Verification:**
- [x] `uv run pytest -q` — 72 tests, including a reproducibility regression test
- [x] User ran the benchmark and saw the same verdict

**Done 2026-09-20.** Qdrant 0.667 hybrid recall vs pgvector 0.500; the gap is lexical (BM25 0.444 vs `ts_rank_cd` 0.111), not dense (0.583 vs 0.528) and not filtering (0.779 both). Storage would have fitted a free tier (77 MB, ~386 MB projected). Two findings: the revisit trigger omitted the deciding metric, and a tie at the k boundary made the eval unreproducible until ties were broken deterministically.

**Dependencies:** T6
**Files:** `docker-compose.yml`, `eval/store_bench.py`, `eval/results/store_bench.md`, `taxcite-technical-documentation.md`
**Scope:** S

---

## ✅ Checkpoint 2 — after T4–T6
- [ ] Tests pass
- [ ] Dense-only vs. hybrid numbers recorded (the first two rungs of the §9 ablation ladder)
- [ ] Embedding model locked, with user approval
- [ ] ADR-17 confirmed or reopened from measured numbers

---

## T7: Cited answer generation and closed-book baseline

**Description:** Add `answer(question, mode)`, where `mode` is `closed_book | rag`. RAG mode puts the top-k chunks in the prompt and requires a citation on every claim. Closed-book mode sends the question with no retrieved context. The provider and model come from config, and each call returns the answer, citations, token counts and cost. Expose it as `taxcite ask`.

**Acceptance criteria:**
- [x] `taxcite ask "…" --mode rag` prints a cited answer; citations are matched against retrieved chunks and mismatches flagged
- [x] `--mode closed_book` works through the same code path, with no retrieval
- [x] Token counts and cost returned per call ($0.0004 for a RAG answer on gpt-4o-mini)

**Verification:**
- [x] `uv run pytest -q` — 84 tests, model call stubbed so no spend
- [x] Manual: P01 in both modes — RAG cited `26 CFR 1.183-2(b)(3)` exactly; closed-book cited the **discontinued** IRS Pub 535

**Done 2026-09-20.** Default model `gpt-4o-mini` ($0.15/$0.60 per MTok, ~$0.49/mo at persona volume); `TAXCITE_MODEL` overrides. `.env` is loaded at the CLI entry point via python-dotenv and is gitignored. Invented citations are detected now, before Phase F's NLI verification.

**Dependencies:** T3 (T6 is preferred first so the final embedding model is used)
**Files:** `src/taxcite/generate.py`, `src/taxcite/llm.py`, `src/taxcite/cli.py`, `tests/test_generate.py`
**Scope:** M

---

## T8: ADR-11 LLM benchmark and decision

**Interim decision (2026-09-20):** run on the cheapest, fastest model (`claude-haiku-4-5`, no reasoning) and upgrade only if measured need appears. Measured context: at persona volume (~200 queries/mo) the pipeline costs ~$3.51/mo against a $50 ceiling, so **cost is not the binding constraint** — §4.1's "a few dozen daily queries" premise only bites above ~500 queries/mo, where Opus-tier would cost ~$79/mo. Report $/mo at both volumes, and treat reasoning as a per-call-site question (synthesis is the candidate; decomposition is formatting; claim verification is NLI per ADR-4; the §9.2 judge runs offline and can afford it).

**Description:** Run the 20 pilot questions × candidate models (Anthropic + OpenAI budget tier, ≤3 total) × {closed_book, rag}. Score each answer on the 3-point rubric from §9.2 (correct / partial / incorrect) against the reference answer, using a judge model that differs from the one being graded, with the user spot-checking. Report the score, cost per query, and projected monthly cost at persona volume (dozens of questions/week, ~5 LLM calls/query). Update ADR-11 to *Decided*.

**Acceptance criteria:**
- [ ] A results table: model × mode → correctness, $/query, projected $/mo
- [ ] The chosen tiering (decomposition / sufficiency / synthesis) fits under $50/mo at persona volume
- [ ] The script stops at a configurable spend limit

**Verification:**
- [ ] Manual: the user approves the ADR-11 decision (Checkpoint 3)

**Dependencies:** T7
**Files:** `eval/llm_bench.py`, `eval/results/llm_bench.md`, `taxcite-technical-documentation.md`
**Scope:** S

---

## ✅ Checkpoint 3 — after T7–T8
- [ ] Tests pass
- [ ] The closed-book vs. RAG gap is measured on the pilot set
- [ ] ADR-11 decided, with user approval

---

## T9: ADR-9 job record and SSE transport

**Description:** `POST /queries` inserts a `jobs` row (id, question, status, stage, result JSON, timestamps) and starts the pipeline in the background. Each stage (`retrieving`, `synthesizing`) publishes an event to Redis pub/sub (ADR-16). `GET /queries/{id}/events` streams SSE and ends with an `answer` or `error` event. A client that connects or reconnects after completion gets the terminal event replayed from the job row. The answer is never token-streamed.

**Acceptance criteria:**
- [ ] `curl -N` on the events endpoint shows the stage events followed by one terminal answer event
- [ ] Killing the client mid-job and reconnecting still delivers the terminal event
- [ ] An unknown job id returns 404

**Verification:**
- [ ] `uv run pytest -q` — an API test using FastAPI's TestClient with a stubbed pipeline covers the event order, the replay after completion, and the 404
- [ ] Manual: an end-to-end run with a real question

**Dependencies:** T7, T1
**Files:** `src/taxcite/api.py`, `src/taxcite/jobs.py`, `tests/test_jobs.py`
**Scope:** M

---

## T10: Phase A exit report

**Description:** Write `eval/results/phase_a.md` with the pilot-set ablation (closed-book → dense → hybrid), the embedding and LLM decisions, a pointer to the §11.1 statute-source decision, known failures with examples, and the recalibration notes for §9.3. Update the Implementation Status in the tech doc.

**Acceptance criteria:**
- [x] `eval/results/phase_a.md` written; every number traces to a results file or a reproducible command
- [x] 5 failure examples documented, including the closed-book model citing a discontinued publication

**Verification:**
- [x] Tech doc Implementation Status updated to say what is built and what is not

**Done 2026-09-21.**

**Dependencies:** T6, T8, T9
**Files:** `eval/results/phase_a.md`, `taxcite-technical-documentation.md`
**Scope:** S

---

## ✅ Checkpoint: Phase A complete
- [ ] All tests pass
- [ ] A reviewer can POST a question and receive a cited answer over SSE
- [ ] ADR-9 built; ADR-11 and the embedding model decided
- [ ] Ready to plan Phase B

---
---

# TaxCite Phase B — Task List

Plan: `tasks/plan.md` (Phase B section). Test command: `uv run pytest -q`. Every task leaves the repo runnable. Tuning happens on the dev set (`eval/pilot.jsonl` plus the new dev rows), never on `eval/golden.jsonl`.

---

## B1: Topic scope and source spike

**Description:** Pick the Phase B topic families by extending Phase A's 21 regulation section families with ones where case law decides the answer (candidates: hobby loss §183, home office §280A, substantiation §274(d), worker classification, constructive receipt §451). Download one Title 26 USLM release point from uscode.house.gov and record its size, section count and release-point Public Law id. Measure the CourtListener bulk opinion files (download size, format, time to extract Tax Court rows) against the alternatives: the API limited to the chosen topics (125 req/day), and GovInfo USCOURTS. Choose the case-law source.

**Acceptance criteria:**
- [x] Topic list written down, with the statute sections and the approximate number of Tax Court opinions per topic
- [x] Case-law source chosen, with the measurements that decided it
- [x] Decision logged in STATUS.md and in an engineering-log entry (#32)

**Verification:**
- [x] Manual: the numbers come from actual downloads or API calls, not documentation

**Measured 2026-09-21:**
- **Statute (uscode.house.gov):** release point `119-110` (Public Law 119-110, 09/16/2026). Zip 8.3 MB, XML 56 MB, 111 s to download, 0.7 s to parse. 2,162 sections: 1,900 live, 241 repealed, 17 renumbered, 2 reserved, 2 omitted. The whole title is ~2.3M tokens without notes (about 7,500 chunks, ~60 min to embed at bge-base's ~2 chunks/s). The topic sections alone are ~101k tokens (~350 chunks).
- **CourtListener bulk:** opinions 54.6 GB bz2 (all courts), clusters 2.5 GB, dockets 5.0 GB. Opinion rows carry no court id, so a Tax Court slice means joining dockets → clusters → a full stream of the 54.6 GB file.
- **CourtListener coverage of the Tax Court is thin:** 13,876 opinions in total, but only 1,050 filed since 2000, about 20–60 a year (2015: 32; 2024: 20). That matches the reported T.C. opinions alone. The memorandum opinions, where hobby-loss and substantiation cases are decided, are mostly missing. `"section 183"` returns 108 hits; `"section 280A"` 29; `274(d)` with substantiation 27.
- **DAWSON (ustaxcourt.gov, the court's own system):** the same `"section 183"` search returns **560** opinions, including memorandum, summary and bench opinions, covering cases filed from May 1986. It has no documented API; its public web app calls an undocumented `public-api` host. Opinions are PDFs.
- **GovInfo USCOURTS:** not measured. It covers Article III courts, and the Tax Court (Article I) is not among them, so it doesn't help here.

**Decided 2026-09-21 (you confirmed both recommendations):**
- **Statute:** ingest all live sections of Title 26, not just the topics. It's a one-time ~60-minute load, and compound questions can then reach any section.
- **Case law:** use DAWSON, not CourtListener, as the Tax Court source: 5× the coverage, and it is the source of record. Scope it to T.C. and memorandum opinions filed 2000 or later, the top ~50 per topic by relevance (~400 opinions, estimated ~16k chunks, ~2 h to embed; B3 measures the real numbers). Summary and bench opinions are nonprecedential and left out for now.
- **Topics for case law:** §183 hobby loss · §162 trade or business / ordinary and necessary · §274(d) substantiation · §280A home office · §469 material participation · §451 constructive receipt · §3121(d)/§7436 worker classification · §6662 accuracy penalty. The regulation topics stay Phase A's 21.

**Dependencies:** None
**Files:** `tasks/todo.md` (this entry), `docs/engineering-log.md`, `STATUS.md`
**Scope:** S

---

## B2: Ingest 26 U.S.C. (statute)

**Description:** Parse the Title 26 USLM XML (release point 119-110) into chunks for **all live sections** (B1 decision). Split by section, and by subsection `(a)` when a section is long, into 200–500-token chunks using the eCFR packing rules. Citations look like `26 U.S.C. § 183(d)`. Set `source = "usc"`, and store the release point's Public Law id as `source_revision`. Teach `generate.py`'s citation parsing the new format, so exact / derived / fabricated counting still works. Re-running is idempotent (keyed on `chunk.key`, like eCFR).

**Acceptance criteria:**
- [x] `uv run taxcite ingest usc` loads all 1,900 live sections; Postgres indexable 10,768 = Qdrant `usc` 10,768 (33 min to embed)
- [x] Re-running creates no duplicates (re-run stored the same 11,030 rows), and sections the XML no longer produces are swept
- [x] Repealed / `[Reserved]` sections are skipped and recorded with a reason (262 sections, `excluded = status`)
- [x] Pilot-set Recall@10 re-run and recorded before and after; any dilution noted (below)

**Verification:**
- [x] `uv run pytest -q`: 110 tests, 14 of them over an 8-section USLM fixture (`tests/fixtures/usc_sample.xml`: 183, 212, 64, 4, 6040, 1311, 3241, 1400Z–1)
- [x] Manual: 3 chunks spot-checked against uscode.house.gov (§183(a)-(d) 6/6, §280A(c)(1) 4/4, §1402(a)(11) 1/1 sentences verbatim)

**Done 2026-09-22.** Pilot hybrid Recall@10 (k=10):
| | Recall | nDCG | MRR | Section recall |
|---|---|---|---|---|
| Phase A | 0.722 | 0.385 | 0.214 | 0.778 |
| after the range-citation fix (`retrieval-2026-09-21-k10-before-usc.json`) | 0.722 | 0.385 | 0.214 | 0.778 |
| + statute (`retrieval-2026-09-22-k10.json`) | 0.667 | 0.362 | 0.204 | 0.778 |

The fix changed labels, not results. The statute costs one question (5.6 points, exactly the pilot's resolution): **P02**'s gold regulation `1.183-1(b)(1)` fell from rank 10 to 11 behind `26 U.S.C. § 183(a)-(d)` at rank 2, whose (b) "Deductions allowable" answers P02 directly. The pilot was labelled before the statute existed, so this is the instrument missing an answer, not retrieval getting worse; Phase A's pilot is left unchanged, and B4's golden set labels statute answers. Sparse lost P01 as well (0.444 → 0.389).

**Progress 2026-09-21:**
- Parser drafted and tested: 11,030 chunks (10,768 indexable) in 2.8 s; median 169 tokens; 4 over 500 (single paragraphs that can't be split, as in eCFR). Every table is flattened: the largest in the text has 86 cells, under eCFR's 100-cell limit.
- Chunking decisions: level 1 is a section's top provisions (subsections, or paragraphs as in §212), level 2 their children; **lead-ins fold into the first provision they introduce**; bracketed "[(n) Repealed …]" provisions are dropped; repealed/renumbered/reserved/omitted sections are recorded with `excluded = status`; `sourceCredit` is stored as `cita`; notes are skipped; en-dash section numbers (`1400Z–2`) become hyphens.
- `ecfr.pack` extracted and shared with a citation prefix. **It had a Phase A bug:** range citations lost their end when the last unit had several blocks, affecting 84 of 5,609 eCFR chunks. Fixed with a regression test, P03 gold relabelled `1.162-4(a)-(c)`, and the eCFR subset re-ingested from the same 2026-09-17 file.
- `source_revision` column added (ALTER, so Phase A's table picks it up); `section_of` handles statute citations, including dashed sections; the synthesis prompt shows a statute citation example; the IRS scraper's User-Agent now points to the right repo.
- Found while testing: `index.sync` held its read transaction open for the whole embedding run, so the `source_revision` ALTER queued behind a running ingest and hung the test suite. `index.sync` now commits after reading, and `create_table` only ALTERs when the column is missing.
- The first eCFR re-ingest ran at 0.45 chunks/s (8.6 GB, 20 GB swap) and was stopped at 56%. Embedding batch 256 → 16: same speed (2.91 vs 2.86/s), 1.5 GB vs 4.5 GB peak. Re-run at ~3/s.
- Known limit: long enumerations split at level 2 still yield short chapeau-less items (1,243 chunks under 50 tokens); revisit if the golden set shows it costs recall.

**Dependencies:** B1
**Files:** `src/taxcite/ingest/usc.py`, `src/taxcite/ingest/ecfr.py`, `src/taxcite/chunk.py`, `src/taxcite/store.py`, `src/taxcite/cli.py`, `src/taxcite/generate.py`, `eval/pilot.jsonl`, `tests/fixtures/usc_sample.xml`, `tests/test_usc.py`, `tests/test_ecfr.py`, `tests/test_generate.py`
**Scope:** M

---

## B3: Ingest Tax Court opinions (case law)

**Description:** Load Tax Court opinions from **DAWSON** (B1 decision): T.C. and memorandum opinions filed 2000 or later, the 50 newest per B1 topic (the search has no relevance ranking). DAWSON has no documented API, so first work out its public search endpoint from the web app, then rate-limit requests and send an identifying User-Agent. Opinions are PDFs: extract text with pdfminer.six (as in T5), and record opinions that come out empty with a reason rather than indexing them. Split into paragraph chunks of 150–400 tokens, each overlapping the previous by one paragraph (§3.2). Citations are page pin-cites, `T.C. Memo. 2021-115, at *4-5` (opinions don't number paragraphs). Docket number, opinion type, judge and filing date stay in the cached selection for Phase C's graph. Set `source = "case"`, and teach `generate.py` the case citation format. *(Revised 2026-09-22 from what B3 found; the original assumed relevance ranking, ¶ citations and an empty `holding_dicta` column.)*

**Acceptance criteria:**
- [x] `uv run taxcite ingest case` loads the topic opinions; Postgres indexable 9,973 = Qdrant `case` 9,973 (32 min to embed)
- [x] Every chunk has a page pin-cite, and consecutive chunks of one opinion overlap by exactly one paragraph (tested)
- [x] Opinions with no usable text are recorded with a reason, never indexed empty (none found: all 307 have a text layer)
- [x] Pilot-set Recall@10 re-run and recorded; dilution noted (below)
- [x] Opinion count, chunk count and embedding time recorded against B1's estimate: 307 opinions (est. ~400), 9,973 chunks (est. ~16k), 32 min (est. ~2 h)

**Verification:**
- [x] `uv run pytest -q`: 120 tests, 10 over two real opinions (T.C. Memo. 2021-115, current layout; 125 T.C. No. 13, 2005 layout) and a canned DAWSON response
- [x] Manual: parsed text checked against the source PDFs for the 2026, 2021, 2005 and 2000 layouts during development

**Done 2026-09-22.** Pilot hybrid Recall@10 (k=10), corpus now 28,393 vectors:
| | Recall | nDCG | MRR | Section recall |
|---|---|---|---|---|
| regulations + publications (Phase A) | 0.722 | 0.385 | 0.214 | 0.778 |
| + statute (B2) | 0.667 | 0.362 | 0.204 | 0.778 |
| + case law (`retrieval-2026-09-22-k10.json`) | **0.500** | 0.304 | 0.170 | 0.667 |
| + case law, case chunks dropped from the top 60 (approximates B7's routing) | ~0.611 | | | |

Three more questions lost (P01, P11, P17). **P01's top 10 is all case law**: hobby-loss opinions apply §1.183-2(b)'s factors to real horse breeders, which matches a fact-pattern question better than the regulation. Across the pilot, case law takes 53 of 180 top-10 slots (29%). This is the dilution B7's source routing exists to remove.

**Progress 2026-09-22:**
- DAWSON's interface, from its web app's bundle: `GET public-api-green.dawson.ustaxcourt.gov/public-api/opinion-search?keyword=…&dateRange=customDates&startDate=MM/DD/YYYY&opinionTypes=MOP,TCOP` (an end date in the future is a 400), then `/public-api/{docket}/{docketEntryId}/public-document-download-url` → a signed S3 link to the PDF. Requests spaced 1 s, identifying User-Agent.
- **The search has no relevance ranking**, so "top ~50 by relevance" became **the 50 newest per topic** since 2000. 307 distinct opinions (279 memos, 28 T.C.), 269 MB of PDFs, cached with the selection in `data/caselaw/opinions.json` so the corpus stays fixed.
- Opinions are deduped **by the citation in the title**: consolidated cases appear once per docket, and some memos are coded as T.C. opinions.
- **Citations are page pin-cites, not ¶ numbers:** opinions don't number paragraphs; they're cited "at *12", and each page opens with a "[*12]" marker. Chunk citation `T.C. Memo. 2021-115, at *4-5`; `section` is the opinion citation.
- Parsing: body text is the modal font size; larger is the masthead; smaller is footnotes (kept, one block per page, below the last paragraph) or table cells (dropped); page numbers and the "Served" stamp are dropped by pattern (the stamp is larger than body text in 2026, smaller in 2021); number-only pieces (list numbers, body-size table cells, ~3,800) fold into the next paragraph.
- Profile: 9,973 chunks, median 374 tokens, 28 single paragraphs over 400, no opinion without text (all have a text layer back to 2000). ~33 min to embed.
- Known limit: pre-2010 layouts put each line in its own text box, so their one-paragraph overlap is one line.
- **Deviation from the plan:** no empty `holding_dicta` column. Nothing reads it until Phase E, and Phase E can add it the way B2 added `source_revision`, with values.

**Dependencies:** B1
**Files:** `src/taxcite/ingest/caselaw.py`, `src/taxcite/chunk.py`, `src/taxcite/cli.py`, `src/taxcite/generate.py`, `tests/fixtures/caselaw_sample.*`, `tests/test_caselaw.py`
**Scope:** M

---

## ✅ Checkpoint 1
- [ ] `taxcite search "…" --source usc` and `--source case` return relevant hits for 3 hand-picked questions each

---

## B4: Golden set, part 1 — statutory-only and case-law-only (45 rows)

**Description:** Create `eval/golden.jsonl`. The schema extends the pilot set's (question, gold citations, reference answer) with `category`, `scored_from` (the phase a row starts being scored in), `as_of` and `expect_insufficient`. Claude drafts 25 statutory-only and 20 case-law-only rows from ingested text; you review every row. **Gold is a list of groups of interchangeable citations** (e.g. `[["26 U.S.C. § 183(a)-(d)", "26 CFR 1.183-1(b)(1)"]]`); a group counts when any member is retrieved. Update `eval/retrieval.py` to score groups, treating a flat list as one citation per group so the pilot's numbers don't move. Case-law rows can only use the 307 ingested opinions. Extend `eval/validate_pilot.py` to take any set file and check that every gold citation exists in the corpus. Also add ~12 dev rows (case-law and compound) for tuning, in `eval/dev.jsonl`.

**Acceptance criteria:**
- [x] 53 rows in `eval/golden.jsonl` (27 statutory, 26 case law; §9.1's 25/20 kept as minimums at your call); the validator passes
- [x] `eval/retrieval.py` scores gold groups; pilot recall and MRR unchanged (nDCG and section recall corrected)
- [x] Every row reviewed by you (`reviewed: true`); corrections logged
- [x] 12 dev rows in `eval/dev.jsonl`, validated, no gold or opinion shared with the golden set or pilot

**Verification:**
- [x] `uv run python eval/validate_pilot.py eval/golden.jsonl`: 0 of 53 need attention; 4 known-hard; 12 diluted groups

**Done 2026-09-22.** Baseline `eval/results/golden-b4-baseline-k10.json`, hybrid k=10: Recall 0.491 (statutory 0.333, case law 0.654), nDCG 0.324, MRR 0.271. **Frozen:** any change to `eval/golden.jsonl` from here is a logged commit.

**Progress 2026-09-22 (drafted, awaiting your review):**
- 45 golden rows (25 statutory, 20 case-law; 37 natural-language, 8 keyword) and 12 dev rows (6 case-law, 6 compound) in a **new `eval/dev.jsonl`**, not appended to the pilot, so Phase A's pilot numbers stay comparable. Dev rows use opinions the golden set doesn't.
- Written from the gold chunks' text: statute answers from the provision (e.g. §67(h) now suspends miscellaneous itemized deductions permanently, not through 2025); case-law answers from the court's own "Held:" or "we hold" sentences. Gold located by phrase, so every chunk containing a holding (overlap can duplicate it) is in its group.
- Gold groups used where authorities are interchangeable: 5 statute rows carry a regulation alternative; G-C16 accepts two opinions with the same holding; G-C14 and G-C20 accept the syllabus and the discussion page.
- `eval/retrieval.py` scores groups; `section_of` now comes from `generate.py`. **Two Phase A metric bugs found**: nDCG counted a gold citation once per retrieved chunk (P15 scored 1.232), and section recall never matched publications. Pilot recall and MRR unchanged; ADR-18 carries a caveat.
- `eval/validate_pilot.py` handles groups, prints category counts, and **separates diluted gold from wrong gold**: a group missing from the overall top 50 is re-searched within its own source. 12 statute groups are diluted (found within `usc` only); 2 rows are marked `expect_hard` for vocabulary mismatch (G-S03, G-S21).
- Baseline, hybrid k=10: Recall 0.467 (statutory **0.320**, case law 0.650), nDCG 0.317, MRR 0.268.

**Audit 2026-09-22 (two full passes over every row and its sources, at your request):**
- **Wrong or incomplete answers fixed (11 statute rows):** §280A(c)(5)'s carryforward; §179's $4,000,000 phase-down and post-2025 indexing; §469(c)(7)'s employee-services rule; §6662(d)'s 5% threshold for §199A claimants; §6662's 40% tiers; §6664(c)'s charitable-valuation limit; §67(b) exclusions; §274(d)'s nonpersonal-use-vehicle exemption; "modified" AGI in §469(i); G-S11 gold widened to §469(i)(2), which actually states the $25,000.
- **Ambiguity removed:** G-S02 and G-S07 now say "self-employed" (for an employee, §67(h) would make both answers "no" for a different reason). G-C01 now asks what Gregory decided, not the post-2017 consequence, which needs §67(h) too and moves to B5 as a compound question. G-C09 now asks about Caan's real issue (same property, not cash), not timing. G-C22 drops "competitive", which the opinion doesn't establish.
- **Law that changed after the source:** G-S25 asked about a state-licensed marijuana dispensary; on 2026-04-28 state-licensed *medical* marijuana moved to Schedule III, outside §280E. Reworded to what the statute says; the dispensary question moves to B5.
- **Appeals:** Morehouse (G-C03) was reversed by the Eighth Circuit (769 F.3d 616, 2014), which isn't in the corpus; reworded to ask what the Tax Court held, with a note. Patel (G-C11) is on appeal to the Fifth Circuit; Gregory, Grey and Rogerson were affirmed. Rows carry a `notes` field for facts outside the corpus.
- **Gold too narrow:** G-C06 now accepts six 2003 memo opinions with the same holding; G-C11 accepts T.C. Memo. 2026-26; G-C12 accepts Kings Road's first page; G-S26 accepts §1.446-1(c)(1).
- **Duplicate removed:** G-C13 (T.C. Memo. 2026-26) restated G-C11's rule; replaced.
- **Coverage added (8 rows):** statute §451(a) timing and §6651(a)(1) late filing; case law on vehicles under §274(d) (Hoakison; Tibin), hobby loss (Phillips), home office (Longino; Kraske), an independent-contractor win (Mayfield) and constructive receipt (Gale). The golden set had no case-law row on hobby loss, home office, substantiation or constructive receipt, the topics practitioners ask about most.
- **Dev leakage removed:** five dev compound rows shared statute gold with golden rows (§183(d), §469(i)(3), §3121(d), §274(d), §262); switched to §1.183-2(b), §469(i)(6), §7436, §1.274-5T(b)(2), §1.262-1(a). Now no citation or opinion appears in both sets, or in both golden and pilot.
- **Known-hard, kept (5):** G-S03, G-S21, G-S26, G-S27 (vocabulary or short-provision mismatch), G-C21 (rank 56 within case law). Dev D09 and D10 are compound rows only decomposition can reach.
- **Now 53 golden rows** (27 statutory, 26 case law; 46 natural-language, 7 keyword), up from §9.1's 25 + 20. Baseline, hybrid k=10: Recall **0.491** (statutory 0.333, case law 0.654), nDCG 0.324, MRR 0.271.

**Dependencies:** B2, B3
**Files:** `eval/golden.jsonl`, `eval/dev.jsonl`, `eval/retrieval.py`, `eval/validate_pilot.py`, `tests/test_metrics.py`
**Scope:** M

---

## B5: Golden set, part 2 — compound, temporal, insufficiency, adversarial (55 rows)

**Progress 2026-09-22 (drafted, awaiting your review):**
- 55 rows: 30 compound, 10 temporal, 10 insufficiency, 5 adversarial. All validate; no gold or opinion shared with dev or pilot; every calculation re-computed by script.
- **Compound rows carry `gold_subqueries`**, one per gold group: what an ideal decomposer would issue, and the source it would search. The full compound question reaches almost none of its gold (it describes client facts, not legal terms), but every gold group is reached by its sub-query (45 groups). The validator now checks that, reporting "needs decomposition" instead of an error. The sub-queries are measurement only, and they give B7 a held-out yardstick for decomposition quality.
- **Insufficiency rows are verified by running the real search**, not by text match: the first draft's "2026 mileage rate" and "2026 wage base" were both answerable (Pub 334's "What's New for 2026" gives 72.5 cents *a* mile and $184,500), and a `cents per mile` probe had missed them. Several rows are traps where search returns authoritative-looking but irrelevant chunks (New York *Liberty Zone* depreciation; outdated §1.179-2(b) amounts).
- **Temporal rows expose a Phase D gap:** effective dates live in the statutory notes, which the B2 parser drops, so the corpus can't say that the qualified-tips deduction (§224) starts in 2025 or which §179 limit applied in 2023. Those rows are `expect_insufficient`.
- The queued edge cases are in: medical marijuana 2026 (G-T03), hobby expenses after 2017 (G-X01) and in 2016 (G-T04), Morehouse in the Eighth Circuit (G-X02, Phase E).
- Adversarial rows carry `client_doc` and `expected_behavior`: prompt injection, script injection, a fabricated §183(z), a system-prompt exfiltration request, and a forged authority badge with a `javascript:` link.
- Baseline on the 30 compound rows, hybrid k=10: Recall **0.317**, the number decomposition has to beat.

**Audit 2026-09-22 (two passes over every row and its full sources, at your request):**
- **Compound rows were measuring the case-law category twice.** 22 of 30 reused an opinion already tested by a case-law-only row, usually the same chunk with client facts added. 18 were rebuilt on opinions the golden set doesn't otherwise use (Miller, Sinopoli, Martin, Day, Schwab, Menard, Veriha, Kadau, Big Apple, Rehman, Henry, Goodwill-Oikerhe, Swanton, Velasco, Carter, Maguire, Akers, Charlotte's Office Boutique). The 4 remaining overlaps are deliberate (Gregory + §67(h); Morehouse; different holdings of Anderson and Patel).
- **Two more reversed opinions found:** Carter's §6751(b) holding was reversed by the Eleventh Circuit (the gold chunk is the post-remand opinion accepting approval as timely, and the draft had the answer backwards), and Menard's reasonable-compensation holding was reversed by the Seventh Circuit (560 F.3d 620, 2009). Both are now explicit tests with notes, like Morehouse. Appellate history was checked for every published opinion in both parts; no other reversals.
- **Answers that depended on facts the question omitted:** G-X10 (Dirico) is passive only because the lessee used the towers in a *rental* activity; that fact is now in the question. G-X05's 2-of-7 horse presumption needs the activity to be mainly breeding, training, showing or racing.
- **Answers missing a rule the source states:** §1.274-5T(c)(5) reconstruction after a casualty (G-X13); §280F(d)(5)(B)(ii) for for-hire vans (G-X15); §162(f) for forfeitures (G-X16); §280A(f)(1)(B) hotel-portion exception (G-X24); §6664(c)(3) no reasonable-cause defence for charitable gross overvaluations (G-X30); §7503 weekend rule (G-T05, April 18, 2026 is a Saturday); §6501(e) disclosure carve-out (G-T06); §6651(a)(2) in the late-filing arithmetic (G-T07); the more-than-half test for a full-time nurse (G-X03).
- **Coverage added:** G-T11, a retroactive rule (100% bonus depreciation enacted July 2025 for property acquired after January 19, 2025); G-I11, a partial-insufficiency row (federal half answerable, California half not) for the per-sub-query sufficiency gate; G-A06, a PII canary for §3.4's redaction invariant.
- **Now 58 rows** (30 compound, 11 temporal, 11 insufficiency, 6 adversarial), 13 with notes. Compound baseline, hybrid k=10: Recall 0.339.

**Queued by the B4 audit:** (1) a temporal/insufficiency row: "can a state-licensed medical marijuana dispensary deduct its expenses for 2026?" (Schedule III since 2026-04-28; the corpus can't show a schedule); (2) a compound row: hobby expenses after 2017 (Gregory + §67(h)); (3) Morehouse (G-C03) as the first negative-treatment case for Phase E.

**Description:** Add 30 compound rows (statute + case law + client facts; client facts are written into the question text, since client documents arrive in Phase G), 10 temporal rows (retroactive rule, amended return, ambiguous as-of year; `scored_from: D` for accuracy), 10 expected-insufficiency rows (`expect_insufficient: true`) and 5 adversarial rows (a malicious client-document payload; `scored_from: G`). Claude drafts, you review every row. Once reviewed, the set is frozen, and any later change is a logged commit.

**Acceptance criteria:**
- [x] At least §9.1's counts per category: 27 statutory / 26 case law / 30 compound / 11 temporal / 11 insufficiency / 6 adversarial = 111
- [x] The validator passes: 0 of 111 need attention (4 known-hard, 12 diluted, 49 reachable only by their gold sub-query); category counts printed
- [x] Every row reviewed by you; the set is frozen (commit pending)

**Verification:**
- [x] `uv run python eval/validate_pilot.py eval/golden.jsonl`

**Done 2026-09-22.** Full baseline `eval/results/golden-b5-baseline-k10.json`, hybrid k=10 over the 84 rows scored in B: Recall 0.435, nDCG 0.307, MRR 0.310; by category statutory 0.333, case law 0.654, compound 0.350. Temporal (scored from D) and adversarial (from G) rows are excluded; 10 insufficiency rows count as abstention.

**Dependencies:** B4
**Files:** `eval/golden.jsonl`, `eval/validate_pilot.py`
**Scope:** M

---

## ✅ Checkpoint 2 (human review: golden set)
- [ ] All 100 rows reviewed by you; the validator passes; category counts match §9.1; the set is frozen

---

## B6: Cross-encoder rerank

**Description:** Add a rerank step using fastembed's `TextCrossEncoder` (already a dependency): take the top 50 fused hybrid candidates and rerank them down to k. Expose it as a search mode (`hybrid+rerank`) so it is its own ablation rung. Compare cross-encoder candidates on the dev set, and choose one on quality and CPU latency.

**Acceptance criteria:**
- [x] `taxcite search "…" --mode hybrid+rerank` works
- [x] Recall@10, nDCG@10, MRR and the section-vs-paragraph recall gap recorded for hybrid vs. hybrid+rerank on the dev set and the golden set
- [x] Added p50/p95 query latency recorded
- [x] Becomes the default only if the measurements support it; the decision is logged either way — **it does not; hybrid stays the default** (ADR-19)

**Verification:**
- [x] `uv run pytest -q`: 127 pass; rerank puts the rule paragraph above the example that quotes it, and the reranked list is a subset of the candidate pool
- [x] `uv run python eval/retrieval.py --pilot eval/golden.jsonl --mode hybrid --mode hybrid+rerank`

**Dependencies:** B2, B3 (golden-set numbers need B5)
**Files:** `src/taxcite/retrieve.py`, `src/taxcite/cli.py`, `eval/retrieval.py`, `tests/test_retrieve.py`
**Scope:** S

**Done (2026-09-22).** Results: `eval/results/golden-b6-rerank-k10.json` (+ `.txt`). Decision: ADR-19.
- Cross-encoder chosen on the dev set: `jinaai/jina-reranker-v1-turbo-en`, 25 candidates (Recall 0.667, nDCG 0.635, MRR 0.727, p50 878 ms). It beat `jina-v1-tiny`, both ms-marco MiniLMs and `BAAI/bge-reranker-base` — the 1 GB model was the slowest *and* the worst (0.542 at 2830 ms).
- Pool is 25 because dev hybrid Recall@25 = Recall@50 = 0.750: the second 25 doubles latency and cannot hold a new answer.
- Golden set (84 scored rows, k=10): hybrid 0.435 / nDCG 0.307 / MRR 0.310 / SectR 0.560 / p50 30 ms · p95 38 ms; hybrid+rerank 0.452 / 0.307 / 0.318 / 0.589 / p50 852 ms · p95 906 ms. By category: statutory 0.333 → 0.333, case law 0.654 → **0.731**, compound 0.350 → 0.333.
- Net is churn, not lift: 4 questions rescued, 3 lost; gold ranked 1st by hybrid fell to 10 (G-S12) and out of the top 10 (G-S19).
- **Diagnosis for B7:** golden hybrid Recall@25 is 0.530, so the reranker recovered 1.7 of the 9.5 points available inside the pool (18%); the other 47% of gold is not in the top 25 at all. First-stage recall is the bottleneck, not ranking. Re-run this comparison after B7 puts routed candidates in the pool.

---

## B7: Query decomposition

**Description:** Add `decompose(question)`: one structured-output call to `gpt-4o-mini` (ADR-11) that returns typed sub-queries (`statutory | case_law | client_fact`) and an as-of year. Retrieve for each sub-query with source routing (statutory → `usc + ecfr + irs_pub`, case_law → `case`, client_fact → not searched; its facts go to synthesis). Group the results by sub-query in the synthesis prompt. The job publishes a `decomposing` stage and stores the as-of year (it is not used as a filter until Phase D). A question that decomposes into one sub-query takes exactly Phase A's path.

**Acceptance criteria:**
- [x] `POST /queries` with a compound question shows `decomposing → retrieving → synthesizing → answer` over SSE
- [~] The answer can cite statute, regulation and case law in one response — it cites across corpora (publication + case law in one answer), but on a question that asks for all three the reranker filled all 10 slots with case law and the statutory groups reached synthesis empty. Open; see the reserved-floor note below
- [x] Golden-set retrieval with vs. without decomposition, per category
- [x] Routing accuracy recorded: **56/56** golden rows whose gold needs case law get a case-law sub-query (recall 1.000); precision 0.709 (23 of the 28 rows that need none get one)
- [ ] **Pilot recall with routing recovers the case-law dilution** — **not met.** Routing scores 0.500, the same as plain hybrid. An oracle routing those questions to statute+regulations only scores **0.667** (0.694 with rerank), so the mechanism works and the classifier's precision is the gap
- [x] Decomposition prompt tuned on the dev set only (two prompts measured; the dev set cannot see routing precision, so no tuning happened on pilot or golden)

**Verification:**
- [x] `uv run pytest -q`: 144 pass — plan parsing, the unusable-plan fallback, routing, the rewrite arm, shared searches, group filtering, SSE stage order, the recorded as-of year
- [x] Manual: 3 compound dev questions through the API — correct stage order, no unsupported citations, ~$0.001 a query

**Dependencies:** B6, B5
**Files:** `src/taxcite/decompose.py`, `src/taxcite/jobs.py`, `src/taxcite/generate.py`, `src/taxcite/retrieve.py`, `eval/retrieval.py`, `tests/test_decompose.py`, `tests/test_jobs.py`
**Scope:** M

**Done (2026-09-22), with one criterion unmet.** Results: `eval/results/golden-b7-decompose-k10.json`, `golden-b7-ladder-k10.txt`, `dev-b7-ladder-k10.txt`, `pilot-b7-decompose-k10.txt`. Decision: ADR-20.
- **The rewriting lost; the routing won.** Dev at k=10: plain hybrid 0.625, rewritten sub-query text 0.625, the original question routed by kind **0.708** (nDCG 0.663, MRR 0.743). The shipped path searches the original question, filtered to the corpora each sub-query's kind allows, and reranks the union back to k. `retrieve(rewrite=True)` keeps the losing arm runnable.
- **Golden (held out), k=10:** Recall 0.435 → 0.476, nDCG 0.307 → 0.330, MRR 0.310 → 0.336, SectR 0.560 → 0.613. Statutory 0.333 → 0.370, case law 0.654 → 0.692, compound 0.350 → 0.400. p50 28 ms → 1,915 ms; $0.00015 a query. Run-to-run spread ±0.006 (the seed is best-effort).
- **This settles ADR-19's revisit trigger:** the cross-encoder earns its place *inside* the routed path, because fused scores from differently-filtered searches are not comparable.
- **Two things are blocked on the same gap.** All 12 dev rows have case law in their gold, so the dev set can measure routing *recall* and not routing *precision*, and cannot measure a reserved per-sub-query floor either. Tuning either on the pilot or the golden set would break the held-out rule, so both stop here.

---

## B7b: Dev-set extension, routing precision, and the golden-set audit

**Done (2026-09-22).** Results: `eval/results/golden-b7b-cached-k10.{json,txt}`, `b7b-attribution-prompt-vs-floor.txt`, `b7b-planner-variance.txt`, `dev-b7b-k10.txt`, `pilot-b7b-k10.txt`. Log #45 (audit), #46 (measurement noise); ADR-20 revised.

- [x] **Dev set 12 → 25 rows.** 13 rows whose gold needs no case law (8 statute, 2 regulation, 2 publication, 1 keyword pair). This made routing *precision* measurable for the first time: the old dev set had case law in every row's gold, so a router that asked for case law on every question scored perfectly.
- [x] **Routing precision tuned on dev only:** recall 1.000 / precision 0.600 → two prompt revisions → **0.917 / 0.917**. The single recall miss (D06) is a question phrased as a pure threshold whose gold is an opinion; the router's statutory answer is arguably the better route and it costs no gold hit.
- [x] **Pilot dilution criterion met: 0.500 → 0.611** (regulation rows 0.562 → 0.688), the number B3 predicted. Recorded with its caveat: the pilot shares 3 gold citations with dev, and on the 15 uncontaminated rows it is 0.533 → 0.600.
- [x] **Reserved per-sub-query floor: exactly neutral** on gold recall (identical at floor 0 and 1 under both prompts, on dev and on 86 golden rows). Shipped anyway — it fixes a composition defect the metric cannot see (statutory sub-queries reaching synthesis with zero chunks on a question that asks for statute, regulation and case law).
- [x] **Golden-set audit, two passes.** 4 rows added (111 → 115), 10 note-level edits. Found: 13 gold groups shared across 29 of 84 scored rows (B5 applied that rule to opinions only); only one row spanned three source kinds and none had statute+regulation+case law as three groups; **no scored row had publication gold at all**; G-T06's answer turned on an unstated extension; G-I07 missing its partly-answerable note. Appellate history verified against CourtListener rather than recall — no new reversals, three positive histories, and one note I was about to write from memory (Schwab "reversed") was wrong, it was affirmed.
- [x] **Validator fixed:** adversarial rows no longer have to carry a document, so an attack arriving in the user's own message can be expressed.
- [x] **Planner noise measured and the harness fixed.** `gpt-4o-mini`'s seed is best-effort. `eval/retrieval.py` now caches plans to `eval/results/decompositions.json` (two runs from one cached set agree exactly) and `--repeats N` scores every decomposition arm against N independently planned sets, printing each set's score with the mean and range. Over six plan sets routing is **0.440 ± 0.012** vs a deterministic **0.428**.
- [x] **The noise has an address:** 14 of 86 golden questions (16%) route differently between plan sets; 39 (45%) differ only in wording, which cannot move a metric because ADR-20 searches the original question. Dropping the rewriting bought reproducibility as well as recall.
- [x] **Lesson recorded:** a range over three samples is an unstable noise estimate — it read 0.035 once and 0.006 the next time, and misled twice. Report a standard deviation over five or more plan sets.

**Corrects B7:** the golden-set gain reported for routing (0.435 → 0.476) was a single-run reading. Measured properly on the grown 86-row set it is **+0.012 ± 0.012** (six plan sets) — small, probably real, and unresolvable by one run. Checkpoint 3 is now answerable and is answered above.

**Files:** `eval/dev.jsonl`, `eval/golden.jsonl`, `eval/validate_pilot.py`, `eval/retrieval.py`
**Scope:** M

---

## ✅ Checkpoint 3 (human review: does decomposition earn its place?)
- [x] Ladder on the golden set (86 scored rows, k=10, mean over 3 plan sets): hybrid **0.428** → +rerank **0.446** → +route **0.442** → +rerank+route **0.452**. Closed-book and dense rungs are unchanged from Phase A.
- [x] **The report says it doesn't — for compound questions.** Compound recall barely moves (0.349 → 0.366 with routing, 0.328 with routing plus reranking). Decomposition earns its place on **statutory** questions instead: 0.321 → 0.357, and 0.429 in the best arm, because routing keeps case-law prose out of a pool that should hold statute and regulations. Case law is slightly worse (0.654 → 0.641). The mechanism works; the category it was designed for is not the one it helps.
- [x] Effect size stated honestly: routing is **+0.012 Recall@10 (sd 0.012 over six plan sets, SEM 0.005)** — about one gold group in 86, with one run of six below the deterministic baseline. No single run can resolve it.

---

## B8: RAGAS faithfulness harness

**Description:** Add `eval/ragas_eval.py`: run the full pipeline over the golden rows scored in B, then score RAGAS faithfulness with `claude-haiku-4-5` as the judge (the other provider, ADR-11/§9.2). Refusals are excluded from the faithfulness mean and reported as a separate refusal rate. Pipeline outputs are cached per run, so re-judging doesn't regenerate them. Print the running cost and stop at a configurable cap. Pin the `ragas` version; if its dependencies cause trouble, implement the faithfulness metric directly instead (extract claims, check each against the retrieved context, take the ratio).

**Acceptance criteria:**
- [x] `uv run python eval/ragas_eval.py` writes `eval/results/ragas-<date>.json` with per-row and aggregate faithfulness, refusal rate and cost
- [x] Run 3 times: **0.859 / 0.902 / 0.833 — mean 0.865, sd 0.035**, over 96 rows (`scored_from == "B"`, including the 10 insufficiency rows, which the retrieval eval excludes)
- [x] Faithfulness is above 0.85 on the mean, so no fix was triggered — **but run 3 is below it**, which is written down here and in ADR-21: the gate as specified would fail about one unchanged build in three

**Verification:**
- [x] `uv run pytest -q`: 157 pass, including refusals excluded from the mean, a refusal scored neither 0 nor 1, an answer with no claims reported not averaged, the cost cap stopping a run, and a skipped verdict counting as unsupported
- [x] Manual: 5 low-scoring rows read against the retrieved text (G-S03, G-S05, G-S10, G-S14, G-C13) — **the judge is right in all five**, including one I expected it to have wrong

**Dependencies:** B7
**Files:** `eval/ragas_eval.py`, `tests/test_metrics.py`, `src/taxcite/generate.py` (`pyproject.toml` unchanged — see below)
**Scope:** M

**Done (2026-09-22).** Results: `eval/results/ragas-2026-09-22.json`, `ragas-2026-09-22-3runs.txt`. Log #47, ADR-21.
- **Not the `ragas` library.** It resolves to 326 packages against this project's 65 — the langchain stack, `datasets`, `scikit-network` — for a metric that is two model calls, and B9 must install it on every PR. The metric is RAGAS's own definition (atomic claims → supported ratio) with the judge on `claude-haiku-4-5` per ADR-11. No new dependency.
- **The finding that justifies the gate:** G-S10 and G-S14 scored 0.00 in all three runs with *legally correct* answers. The gold chunk was not retrieved; the model answered from parametric knowledge and attached a citation to a chunk that was retrieved but does not state the claim. Phase A's citation checker scores those as **exact** citations and passes them. Faithfulness is the only check that sees it.
- **Abstention: 10/10 insufficiency rows refused in 3/3 runs.** The 13–18% refusal rate also includes 3–7 false refusals per run (G-C02 every run, G-X25 twice, eight rows once) — a retrieval problem, not an honesty one.
- Cost for the whole 3-run measurement: judge $1.35 + pipeline $0.22 = **$1.56**, 29 minutes.
- Two upstream bugs fixed in `call_model`: `anthropic` 1.7.0 has no `temperature` on `messages.create` (previously every claude call passed None, so it was never hit), and it *does* support schema-enforced JSON via `output_config`, which the judge now uses.

**Hands B9 a problem:** the gate cannot be a single run at 0.85. Options to weigh in B9 — gate the mean of N runs (29 min and $1.56 per PR is too slow), pin a plan cache so CI is deterministic and the gate measures the change rather than the planner, or gate a smaller subset with a band derived from its own measured sd.

---

## B9: CI in GitHub Actions + the RAGAS gate

**Description:** There is no CI today. Add three tiers (revised 2026-09-22 from the B8 measurement; you approved the change):
- `pytest` on every push, with Qdrant, Postgres and Redis as service containers.
- **A deterministic retrieval check** on PRs touching retrieval, reranking or decomposition: `eval/retrieval.py` against the pinned plan cache. No LLM, seconds to run, and two cached runs already agree to three decimals — it catches a retrieval regression unambiguously and for nothing. Not in the original plan; it is the highest value-per-second check available.
- The faithfulness gate on PRs touching prompts, synthesis or the pipeline (§7's list). It restores the corpus from a Qdrant snapshot and a Postgres `chunks` dump published as a GitHub release asset, and runs `eval/ragas_eval.py`.

**Three changes to the gate as §7 specified it, each with its reason:**
1. **It runs on the dev set, not the golden set.** A gate that fires on every qualifying PR is a tuning signal; over months it would fit the system to the held-out data, undoing what B4 and B7b exist to protect. Dev is 25 rows, ~8 minutes, ~$0.40 a run. Golden stays for phase reports.
2. **The threshold is calibrated against a broken prompt, not set at 0.85.** B8 measured 0.859 / 0.902 / 0.833 on an unchanged pipeline, so a single-run gate at 0.85 fails about one clean build in three. The acceptance criterion below defines what the gate must detect — a deliberately broken synthesis prompt — so the threshold goes between that score and the healthy floor. 0.85 stays as the reported quality target in the exit report; a CI threshold and a quality target are different objects.
3. **What can be pinned is pinned:** the plan cache (already built), and synthesis temperature (see B9a). The judge cannot be pinned — `anthropic` 1.7.0 exposes no temperature — so its variation is the gate's noise floor.

Add a script that regenerates and publishes the snapshot when the corpus changes. Embedding and cross-encoder models are kept in the CI cache. API keys come from repository secrets.

**Acceptance criteria:**
- [ ] `pytest` runs green on push
- [ ] The deterministic retrieval check runs on the listed paths and fails on a seeded retrieval regression
- [ ] The gate runs only on PRs touching the listed paths, and its cost and runtime per run are recorded
- [ ] **Proof:** a PR with a deliberately broken synthesis prompt fails the gate; reverting it passes
- [ ] The threshold is derived from the measured healthy band and the measured broken-prompt score, and both are written down

**Verification:**
- [ ] Manual: workflow runs linked in the log entry

**Dependencies:** B8
**Files:** `.github/workflows/test.yml`, `.github/workflows/retrieval-gate.yml`, `.github/workflows/faithfulness.yml`, `eval/snapshot.py`, `eval/retrieval.py` (`--fail-under`), `eval/ragas_eval.py` (`--fail-under`), `src/taxcite/generate.py` (synthesis pinned)
**Scope:** M

**Progress (2026-09-23).** Design settled and calibrated (ADR-22); files written; threshold pending one measurement.
- [x] **Calibrated the gate against the failure it exists to catch.** Dev, judge `claude-haiku-4-5`: healthy 0.823 (sd 0.033), healthy at temp 0 **0.808 (sd 0.016)**, broken prompt 0.762, broken at temp 0 0.759 (sd 0.027). A broken synthesis prompt costs ~0.05 — **2.2 pooled sd**, a 0.011-wide window, ~12% false failures and ~12% false passes. A per-PR faithfulness gate on 25 rows does not work.
- [x] **Noise decomposed by pinning one component at a time:** re-judging identical answers moves sd **0.008** (5% of variance); the planner and synthesis sampling hold the other 95%, and both are pinnable. The unpinnable component is the one that barely matters.
- [x] **Synthesis pinned to `temperature=0, seed=0`** — halves the noise, no measurable quality cost, and the right default for a legal tool independent of CI. Test added.
- [x] **Three workflows written** (`test.yml`, `retrieval-gate.yml`, `faithfulness.yml`) plus `eval/snapshot.py` for corpus freeze/restore, and `--fail-under` on both eval entry points (exit codes verified).
- [x] Tier 2 is the per-PR blocker: `eval/retrieval.py` against the committed plan cache — no LLM, deterministic, `--fail-under 0.66` against the measured dev figure.
- [x] **Tier 3 threshold: 0.83**, three sigma below the measured healthy golden mean (0.871, sd 0.013, plans pinned + temperature 0). Enabled in `faithfulness.yml`. Calibrated against the healthy distribution, since broken-on-golden is not measured yet — the proof run supplies that.
- [x] **Found and fixed a harness bug worth more than the threshold:** `ragas_eval` called `decompose` fresh per row and never used the plan cache, so faithfulness was partly measuring the planner. Pinning plans took golden sd 0.035 → 0.013; temperature 0 alone had moved it only to 0.030, because the planner dominated (16% of golden questions re-route between runs). `decompose.answer` now accepts a supplied plan.
- [x] Residual noise characterised: ~0.010 synthesis + 0.008 judge. Irreducible — OpenAI's `temperature=0` with `seed` is best effort, and two runs over identical plans and context still differ.
- [x] **Tier 1 verified:** `tests` green on `03f529c` (run 35899005211). The first run failed and the CI log confirmed the diagnosis exactly — `index.count` 404'd on an empty Qdrant during collection.
- [x] **Tier 2 verified both ways:** healthy `main` 0.6800 PASS (run 35900723401); PR #1 with `PREFETCH` 50→1 scores 0.3400 FAIL (run 35900409247), while `pytest` stays green on that same commit. Corpus restored in CI both times, 28,393 / 28,747 matching local.
- [x] **Three CI-only bugs found and fixed:** the empty-Qdrant 404; a Qdrant version mismatch (workflows pinned v1.12.4, the snapshot is v1.19.1 — the restore 500'd); and `on: release` firing the faithfulness gate when the *corpus* snapshot was published (run 35898818357), now skipped for `corpus-*` tags. `snapshot.py` also now prints Qdrant's response body, which `raise_for_status` was discarding.
- [x] **Tier 3 proof run — and it failed, correctly.** Both arms dispatched on the runner (35901633914 broken, 35901637011 healthy). Healthy `main` 0.870/0.884/0.889 → mean **0.881** sd 0.010. Grounding rule removed → 0.849/0.841/0.842 → mean **0.844** sd 0.004. **The broken build passed a gate set at 0.83**: the threshold was three sigma below a locally measured *healthy* mean and sat below where a broken build actually lands. Threshold corrected to **0.855**, between the two measured bands (~2.5 sigma margin each side); the bands do not overlap, healthy's worst run beats broken's best by 0.021. The contingency comment in the workflow was also backwards ("comes down" → must go up). Log #50, ADR-22.
- [x] Note: B9's criterion says "a *PR* with a broken prompt fails the gate". That wording predates the ADR-22 tiering, under which faithfulness deliberately does not trigger on `pull_request`. The dispatch on a branch is the equivalent proof for a nightly gate.
- [x] PR #1 closed unmerged.
- [x] **The re-run turned out to be necessary, before it even ran.** Asking whether it was found that the gate step ended in `| tee`, and GitHub runs steps as `bash -e` without `pipefail` — so a non-zero exit from `ragas_eval` was swallowed and **the gate could not fail at any threshold**. Fixed with `shell: bash`. Log #51.
- [x] **Re-ran both arms with the pipefail fix: the gate produced its first red build.** Broken 0.815/0.840/0.862 → mean 0.839 → `0.8388 < 0.8550` **FAIL** (run 35907376281). Healthy 0.862/0.868/0.856 → mean 0.862 → **PASS** (run 35907379679). Exit code propagated; the mechanism is verified end to end.
- [x] **Pooling six samples per arm corrected the error rates I had claimed.** healthy 0.8715 sd 0.0127, broken 0.8415 sd 0.0154, separation 2.1 sigma (not 4.9), bands overlap. At 5 repeats the gate is 0.2% false-fail / 2.5% false-pass — it misses about one broken build in forty. Standing rule added: re-measure both bands with ≥5 samples after any pipeline change (three-sample estimates misled this phase four times).
- [x] **Cadence corrected from nightly/3 to weekly/5**. Nightly at 3 repeats is $48.60/month against the project's $50 ceiling — the per-run cost was recorded and never multiplied by 30. Weekly at 5 is $11.65/month *and* stricter, because frequency buys latency (worth little here) while repeats buy statistical power. `workflow_dispatch` stays the primary path for a deliberate prompt change.
- [ ] Delete `proof/retrieval-regression` and `proof/broken-synthesis-prompt`.

---

## B10: Phase B exit report

**Description:** Write `eval/results/phase_b.md`, in the same shape as `phase_a.md`: the golden-set ablation ladder with per-category numbers, faithfulness with its spread across runs, refusal and abstention rates, failures with examples, and §9.3 recalibration notes. Record the **decomposition-only case-law Recall@20** — the baseline Phase C's gate is measured against. Update the tech doc's Implementation Status.

**Acceptance criteria:**
- [x] Every number traces to a results file or a reproducible command (commands listed at the foot of the report)
- [x] Seven failure examples documented, led by citation laundering — `G-S10`/`G-S14` score 0.00 faithfulness with legally correct answers that the citation checker passes
- [x] **Phase C's case-law Recall@20 baseline: 0.692**, decomposition only. Routing adds nothing to case law at k=20, which is exactly the gap graph expansion exists to close

**Verification:**
- [x] Tech doc Implementation Status rewritten: what Phase B built, its three negative results, the remaining unbuilt mechanisms, and a baselines table carrying each open problem to the phase that owns it
- [x] Corrected the B8 abstention claim: 9 of 10, not 10 of 10 — `G-I06` never refuses, and `G-I11` (the partial) over-refuses

**Dependencies:** B9
**Files:** `eval/results/phase_b.md`, `taxcite-technical-documentation.md`
**Scope:** S

---

## ✅ Checkpoint: Phase B complete
- [x] All tests pass in CI
- [x] The RAGAS gate is live and green (weekly × 5 at 0.855; its first red build was the seeded broken prompt)
- [x] Ready to plan Phase C — after C0, below

---

# TaxCite Phase C — Task List

Plan: written after C0. Phase C's gate (tech doc §7): case-law Recall@20 improves by **≥5 points over 0.692** (decomposition only, 26 case-law golden rows), and edge extraction reaches precision ≥90% / recall ≥85% on a 200-edge hand-labeled sample.

---

## C0: Citation-graph reachability spike

**Description:** Find out whether graph expansion *can* move case-law Recall@20 before building any of it. The case corpus cites 2,540 distinct opinions and holds 227 (8.9%), so most edges lead nowhere. But the gate is scored on the golden set, and every golden gold opinion is already in the corpus. So adding the cited opinions can't create new gold. They only help if a missed gold opinion is reachable through one of them. Measure three things, then choose a direction.

1. **Can extraction be trusted enough to measure with?** Run eyecite over the 307 opinions' text (it's not a dependency yet; try it in a throwaway script) and compare against whatever produced the 2,540 figure. Hand-check ~30 citations from 3 opinions for misses and false hits, especially `T.C. Memo.` forms and pin-cites.
2. **The ceiling (the number that decides Phase C).** For each of the 26 case-law golden rows, take the gold opinions that hybrid+routing misses at k=20 (the 30.8%). Is each one 1 hop or 2 hops from an opinion that *is* in the top 20, counting edges in both directions (cites and cited-by)? Count 2-hop paths two ways: only through held opinions, and also through opinions we don't hold (what ingesting them would unlock). This is an upper bound: expansion can't do better than perfect traversal plus perfect reranking.
3. **Ingestion cost curve.** Rank the 2,313 cited-but-not-held opinions by in-degree. How much of the dangling edge mass do the top 50 / 200 / 500 cover, and how many of those are Tax Court opinions DAWSON can serve? Convert the chosen N to chunks and embed time (~7 chunks/s; B3 averaged ~32 chunks per opinion).

**Acceptance criteria:**
- [x] Extraction precision/recall estimate on the hand-checked sample, and whether eyecite is good enough for C1 or needs a Tax Court–specific pass
- [x] Ceiling table: of the missed case-law gold, how many are reachable at 1 hop, at 2 hops through held opinions only, and at 2 hops through any opinion. Stated in Recall@20 points so it compares directly with the +5 gate
- [x] Coverage curve for top-N ingestion, with the cost of the recommended N
- [x] A decision you confirm, one of: **(a)** ingest top-N cited opinions and then build the graph, **(b)** build on the held set only, **(c)** record Phase C as a measured negative result and move to Phase D/E. Logged in STATUS.md and the engineering log

**Verification:**
- [ ] Manual: every number comes from running against the real corpus and golden set, not from estimates
- [ ] Decision rule, written down *before* the numbers come in: if the ceiling is under +5 points, a graph over the current golden set can't pass its gate however well it's built. Say so plainly instead of building it

**Measured 2026-09-26** (hybrid + routing + rerank, k=20, cached plan set 0, 26 case-law golden rows; reproduces the 0.692 baseline exactly):
- **Extraction:** eyecite is good enough. It found every memo citation a regex did, and missed 23 of 2,456 (0.9%), all PDF line breaks (`T.C. Memo. 1997- 553`) fixed by one substitution. 15/15 sampled volume/page citations were real. Reported T.C. opinions are cited by volume/page (`119 T.C. 121`) but keyed by slip number (`119 T.C. No. 5`), so held T.C. opinions need an alias; 10 of 28 were recovered by surname match.
- **Edges:** 271 of 307 opinions cite 2,496 distinct Tax Court opinions (4,911 edges). **4.7% of edges resolve to a held opinion** (the earlier 8.9% was an overestimate). Only 107 held opinions are cited by another.
- **Ceiling (the deciding number):**

  | Missed case-law gold at k=20 | Recall@20 points |
  |---|---|
  | Gold opinion already in top 20, wrong pages | **23.1** (6 rows) |
  | 1 hop from a retrieved opinion | 0.0 |
  | 2 hops through held opinions | 0.0 |
  | 2 hops through any opinion (co-citation; adds ~131 opinions/question) | 0.0 |
  | Unreachable | 7.7 (2 rows) |

  **Graph expansion's ceiling on the gate is 0 points, against a +5 requirement.** Under the decision rule above, Phase C as specified can't pass its gate.
- **Where the gap actually is:** in 5 of the 6 wrong-page rows the gold is the syllabus (`at *1-2`), masthead plus the court's "P/R" summary. It is not in the top 100, and when every chunk of that opinion is reranked it ranks 6th–16th. Spot check: G-C18's top sibling page states the rule (gold too narrow?); G-C10's top sibling is the petitioner's argument (a real retrieval miss). Needs an audit before it counts as 23.1 points of system gap.
- **Ingestion curve:** long tail. 1,632 of 2,389 missing opinions are cited once. The top 50 / 200 / 500 cover 20% / 37% / 54% of dangling edges (~1.6k / 6.4k / 16k chunks, ~4 / 15 / 38 min to embed); nearly all were filed in 1987 or later, so DAWSON can serve them. Moot for the gate: golden gold is in the corpus by construction.
- Spike scripts live in the session scratchpad, not the repo; ask for them if they should be kept.

**Decided 2026-09-26 (you approved the revised phase):** neither (a), (b) nor (c) as written. The graph is kept and repurposed for **negative treatment**. Expansion becomes an ablation rung. Case-law recall work moves to **page selection**. See `tasks/plan.md` (Phase C) and ADR-1 (revised).

**Dependencies:** None (Phase B complete)
**Files:** `tasks/todo.md` (this entry), `STATUS.md`, `docs/engineering-log.md` (#53)
**Scope:** S

---

## C1: Treatment-source spike

**Description:** Find out where "reversed / affirmed / on appeal" data can come from, and how much of it there is, before anything depends on it. Two candidate sources:
1. **Our own corpus.** Later Tax Court opinions cite earlier ones with subsequent history ("140 T.C. 350 (2013), *rev'd*, 769 F.3d 616 (8th Cir. 2014)"), and eyecite already parses it. Count how many held opinions pick up an `aff'd` / `rev'd` / `vacated` this way.
2. **CourtListener**, whose search works without a key. Look up each held opinion's appellate history, and record hit rate, request cost and what the response looks like.

Score both against the six golden treatment rows: G-C03, G-X02, G-X09 (reversed), G-C11 (on appeal), G-C06 (appealed, stands), G-X19 (post-remand, not reversed).

**Acceptance criteria:**
- [ ] For each source: how many of the 307 held opinions it gives any treatment for, and whether it gets the six golden rows right
- [ ] A hand check of 20 treatment records against the appellate opinion itself
- [ ] A source chosen (or both, merged), with what "no record" means for each, written down
- [ ] The cost of re-checking all held opinions (requests, minutes), for Phase H's weekly refresh

**Verification:**
- [ ] Manual: every number comes from real lookups, not documentation

**Measured 2026-09-26:**

| | Own corpus (subsequent history, eyecite) | CourtListener, no API key |
|---|---|---|
| What it gives | The outcome ("*X*, rev'd, *Y*" / "*Y*, aff'g *X*") | That an appeal was *decided*: appellate "*name* v. Commissioner" filed after our opinion |
| Coverage of our 307 held opinions | **11** (the corpus is the 50 newest per topic, so few later opinions cite them). Covers 613 *cited* opinions | 36 of the 263 searched had a tax-appeal match, before verification; some are same-name collisions |
| Golden rows | *Menard* reversed ✓, *Nu-Look* affirmed ✓; *Morehouse* missed (nothing in the corpus cites it) | *Morehouse* → 8th Cir. 2014 `769 F.3d 616` ✓, *Menard* → 7th Cir. 2009 `560 F.3d 620` ✓, *Nu-Look* → 3rd Cir. 2004 ✓; G-X19 nothing ✓; *Patel* nothing (pending) |
| Precision | Hand check of 20 records: 17 right, 1 wrong (a B.T.A. cite read as an appeal), 2 not checkable. Also: T.C. Memo. 2011-48 "affirmed" by a 2003 case | Not measured: throttled |
| Limits | Only sees an appeal a later held opinion mentions | **The outcome isn't readable**: snippets stem ("vacated" matched "vacation"), opinion pages return a bot challenge (HTTP 202, empty), and the text API returns 401 without a key. **Throttled (429)** after ~260 searches |

- Neither source detects a **pending** appeal (*Patel*, G-C11). That needs docket data; until then the flag reads "unknown", never "no appeal".
- Parser fixes found: accept only appellate reporters (F., F.2d–F.4th, F. App'x, U.S., WL, USTC, AFTR); require the appeal to be dated after the opinion; add an `overruled` pattern (*Morehouse*'s own text says *Wuebker* "is overruled", which was read as "rev'd").
- **Refresh cost:** outcomes only change for recent opinions. A decided appeal stays decided. So the weekly refresh only needs opinions filed in the last ~3 years (~150 of 307), at ~1 search each plus a text fetch per hit.

**Recommendation:** both sources, merged. The corpus is free and gives outcomes with their citation. CourtListener *with a free API key* finds the appeals the corpus misses and supplies the outcome from the appellate text. The tech doc (§11.7) records the key's free tier as 125 requests/day. The first full pass (~350 requests) takes about 3 days of quota; the weekly refresh of ~150 recent opinions fits comfortably. **Without a key the Phase C gate can't pass**: *Morehouse*'s reversal is found, but its outcome can't be read.

**With the API key (same day):** for each appeal match, the appellate opinion's text was fetched (~65 requests) and its ruling read from the last disposition sentence ("we reverse and remand", "is AFFIRMED").
- **Golden rows: all correct.** *Morehouse* reversed (8th Cir. 2014, `769 F.3d 616`), *Menard* reversed (7th Cir. 2009, `560 F.3d 620`), *Nu-Look* affirmed (3rd Cir. 2004). G-X19 has no appeal. *Patel* (G-C11): no docket found, even in docket search, so pending appeals stay `unknown`.
- **Matching an appeal to our case:** a same-surname search finds ~59 candidates for 36 opinions, most of them collisions ("Michael Kelly" for *Willock*, "Isobel Berry Culp" for *Berry*). The rule that works: the family name in the appeal's case name, a petitioner's first name in its text, the text says "Tax Court", decided within 5 years, and **the earliest such appeal** (a later same-name case picked *Thompson*'s 2016 affirmance over the 2013 reversal that decided it). That leaves **17 of the 263 searched with a confirmed appeal**.
- **Hand check of all 17 outcomes:** 13 fully right, 2 partial ("AFFIRMED IN PART; REVERSED IN PART" read as reversed), 1 wrong (*Visco*: a footnote where the *Tax Court* is the subject of "reversed"), 1 unknown (*Gregory* ends in a dissent). Fixes for C3: an `in part` outcome, and ignore sentences whose subject is the Tax Court.
- **Limits measured:** the keyed API allows **10 requests/minute** (a rolling window, with a `retry-after` header). No daily wall was hit at ~65 requests. 44 held opinions are still unsearched and will be finished in C3.

- [x] Numbers per source, golden rows scored
- [x] Hand check: 20 corpus records (17 right) and all 17 CourtListener outcomes (13 right, 2 partial, 1 wrong, 1 unknown)
- [x] **Source chosen: both, merged.** CourtListener with the key is primary (finds the appeal, reads its outcome). Corpus subsequent history is a free cross-check and covers opinions that are only cited. Disagreements show as `unknown`, never as either outcome

**Dependencies:** C0
**Files:** `tasks/todo.md`, `STATUS.md`, `docs/engineering-log.md`; spike scripts outside `src/`
**Scope:** S

---

## C2: Wrong-page audit (6 golden rows)

**Description:** In G-C10, G-C11, G-C15, G-C18, G-C19 and G-C26 the gold opinion is retrieved but not the gold pages, which costs 23.1 of the 30.8 missed points. For each row, read the opinion and decide whether other pages state the same holding as the gold (the gold group is too narrow) or whether the retriever is picking argument or background over the holding (a real miss). Claude drafts a verdict per row with the quoted sentence; you decide.

**Acceptance criteria:**
- [x] Per row: widen the gold group (list the added pages and the sentence that states the holding), or leave it (and name what the retriever picked instead)
- [ ] Changes applied as one logged commit, with the validator passing. Gold groups only widen (applied and validated; commit pending)
- [x] Case-law Recall@20 re-measured on the audited set: **0.833 ± 0.018** over the 3 cached plan sets (0.846 / 0.846 / 0.808; was 0.692). The audited rows behave identically in all three; the spread comes from other rows. The real page-selection gap C6 has to close: **2 rows, 7.7 points** (G-C10, G-C26)

**Verification:**
- [x] You review every changed row (the B4/B5 audit rule)
- [x] `uv run python eval/validate_pilot.py eval/golden.jsonl` passes

**Verdicts (2026-09-26): you approved all six; applied to `eval/golden.jsonl`, validator passes (0 of 115 need attention).** Rule: a page qualifies only if it states *the court's own conclusion* on the question (not argument, background, a dissent, or the court describing other cases). Each opinion was read in full for holding sentences, not just the retrieved pages.

| Row | Verdict | Pages to add | The sentence |
|---|---|---|---|
| G-C10 *Dirico* | widen | `139 T.C. No. 16, at *21-23` | "we do not address the issue of whether petitioner materially participated…, and we hold that section 1.469-2(f)(6)… is inapplicable" |
| G-C11 *Patel* | widen | `165 T.C. No. 10, at *16-17`, `at *17` | "we easily conclude that the statute requires a relevancy determination" |
| G-C15 *Rogerson* | widen | `T.C. Memo. 2022-49, at *19`, `at *21` | "the five of ten test has been met for each of 2014, 2015, and 2016, and Mr. Rogerson is treated as materially participating"; "(we conclude he did)" at *4 excluded: no five-of-ten rule |
| G-C18 *Hampton* | widen | `T.C. Memo. 2025-32, at *12`, `at *14` | "Mr. Hampton is barred by the public policy doctrine from reporting his… share of HCM's resulting loss"; "the public policy doctrine disallows Mr. Hampton's claimed deduction" |
| G-C19 *Mission Organic* | widen | `165 T.C. No. 13, at *2-3`, `at *10-11`, `at *11`, `at *11-12` | "We resolve the issue in favor of the Commissioner"; "it is not an abuse of discretion to disallow such expenses for reasonable collection potential purposes". Pages *45+ are a dissent and excluded |
| G-C26 *Gale* | widen | `T.C. Memo. 2002-54, at *26-27` | "Any restriction placed on the use of the settlement proceeds after payment… does not delay petitioner's receipt of the income" |

**Effect (cached plan set 0, same basis as the 0.692 baseline):** case-law Recall@20 **0.692 → 0.846** on plan set 0; **0.833 ± 0.018** over all 3 cached plan sets. G-C11 (rank 1), G-C18 (5), G-C19 (9) and G-C15 (20) become hits: **their gold was too narrow**. G-C10 and G-C26 stay missed: the retriever ranks argument and background over the holding. **The real page-selection gap for C6 is those 2 rows (7.7 points), not 23.1.** Two of the six added pages were never retrieved, some evidence the choice wasn't steered by the retriever's output.

**Validation, two scans (2026-09-26).**
*Scan 1, per page:* every chunk carrying an added label contains a holding sentence, including the duplicate-label chunks (*Hampton* *12 ×2, *14 ×2; *Mission Organic* *11 ×2, whose second copy states "it is not an abuse of discretion in the light of congressional action"). No chunk containing a holding sentence is missing from its group. Every added page is majority text, before "Decision(s) will be entered"; *Mission Organic*'s concurrences begin at *13-14. The "Roberts, J., concurring" inside *Patel* at *13-14 is a quoted D.C. Circuit citation, and *Patel* is a unanimous reviewed opinion. Two pages are weaker: *Dirico* *21-23 never says "passive" (the self-rental rule is "inapplicable", so rental income stays passive), and *Rogerson* *19 gives the five-of-ten result without the related-business link that *21 states. Neither produces a hit.
*Scan 2, around the change:* no dev/pilot leakage. G-X20 shares *Patel* as a documented deliberate pair at a different pin-cite (*36), so there's no double credit. Only `eval/retrieval.py` metrics read gold; the faithfulness judge and `generate.py` don't. All 12 new labels are indexed in Qdrant. The CI retrieval gate scores `eval/dev.jsonl`, so it's unaffected. Hits come from the strong pages in all 3 cached plan sets (G-C11 *16-17 rank 1, G-C18 *14 rank 5, G-C19 *2-3 rank 9, G-C15 *21 rank 20: **fragile**, at the cutoff). The Phase B report now notes its golden numbers predate C2.

**Follow-up audit of the other 18 summary-only groups (2026-09-26): you approved all 18; applied together with removing G-C15's `*2` (approved). 24 rows changed in total since the last commit, only `gold` fields, validator passes.** Same rule, majority text only. Each proposed label was checked for duplicate copies and for overlap chunks the proposal missed.

| Row | Add | Holding sentence |
|---|---|---|
| G-C02 *Moss* | *8-9 | "Mr. Moss' time 'on call'… does not satisfy any part of the 750-hour service performance requirement" (*9-11 excluded: REP status, broader than the question) |
| G-C03, G-X02 *Morehouse* | *42-43, *43-44 | "We hold that the CRP payments at issue do not constitute 'rentals from real estate'"; "we overrule our holding in Wuebker"; SE-tax inclusion sustained (findings at *23-24 excluded) |
| G-C04 *Medical Emergency Care* | *12-13, *15-17 | "late filing of the information returns does not prevent it from satisfying the filing requirement of section 530(a)(1)(B)"; "We hold that petitioner is entitled to relief" |
| G-C05 *Ewens & Miller* | *2-3, *9-10 | "we hold that we do have jurisdiction over additions to tax and penalties found in chapter 68" (the summary's holding runs into *2-3) |
| G-C07 *Ancira* | *6-8, *8-9 | "petitioner acted as a conduit for Pershing"; "did not result in a distribution" |
| G-C08 *McNulty* | *2-4, *12-13 | "we hold she did"; "had taxable distributions from her IRA when she received physical custody of the AE coins" |
| G-C09 *Caan* | *24-25, *28 | "were not contributed in a manner that would qualify as a nontaxable rollover"; conclusion and waiver holding at *28 (both copies). *23 excluded: quoting Lemishow |
| G-C12 *Kings Road* | *18-19 | "Section 6234(a) is subject to equitable tolling" (*7-8 is the general presumption, not a conclusion) |
| G-C17 *Lofstrom* | *2-3, *11-12 | "used the B&B for personal purposes for an indeterminate period… we hold that they may not deduct"; "personal use of the B&B, petitioners are not entitled to deduct" |
| G-C22 *Phillips* | *20-22 | "Mr. Phillips did not engage in his bowling activities for profit" |
| G-X10 *Veriha* | *9-10, *12-13 | "we conclude that each individual tractor or trailer is an 'item of property'"; "only TRI's net income is recharacterized as nonpassive" (*8-9 excluded: the IRS's contention; *11-12: side issue) |
| G-X12 *Big Apple* | *28 | "Congress did not clearly state that the 90-day filing deadline is jurisdictional… will deny respondent's Motion" |
| G-X15 *Henry* | *22 | "the cancellation of indebtedness issue is new matter and… the Commissioner therefore bears the burden of proof" (*23-24 excluded: adopted quote from Tabrezi) |
| G-X24 *Akers* | *11-12 | "the cabin is considered a residence for purposes of section 280A" |
| G-X25 *Charlotte's* | *3-5, *25-26, *26-27, *28-29, *29-30 | "[wages?] We hold they were"; "[section 530?] We hold it is not"; "lacked a reasonable basis… not entitled to relief under section 530" |
| G-X26 *Mazotti* | *11, *15-16 | "her writer-researcher activities were not engaged in for profit"; "we sustain the IRS's disallowance" |
| G-X27 *Specks* | *10-11 | "we sustain respondent's determination that Mr. Specks is liable for self-employment tax" |

**Impact:** none today. Case-law 0.833 ± 0.018 and compound 0.457 ± 0.008 are unchanged over 3 plan sets, and no row moves. These rows already hit through their summary or are unreachable. The point is consistency before C6 edits summary chunks.

**A bug found and fixed along the way:** my audit helper ordered chunks by `part`, which restarts per label, so its "majority ends here" cut-off dropped majority text. Re-run in page order, it surfaced new holding sentences in five opinions (*Morehouse* *42-43, *Mazotti* *11 and *15-16, and others) and changed nothing in the rest. The six-row validation didn't use that cut-off, so it's unaffected.

**Found, not yet acted on (your call):**
1. **The rule was applied only to rows that missed.** 18 other gold groups (10 case-law, 8 compound) still accept only the summary page. That can't inflate today's recall, but C6 edits summary chunks, so rows that hit only via their summary could flip to misses and make C6 look worse than it is. Recommendation: run the same audit over all 18 before C6.
2. **G-C15's pre-existing `*2` has no holding** (facts and contentions; "Held:" is in *2-3). Removing it narrows a key, which needs your approval. No current hit depends on it.
3. **(Checked 2026-09-26) G-C24 earns an unearned hit.** `T.C. Memo. 2023-128, at *15` is carried by 3 chunks, and only one states the holding. In all 3 plan sets the retrieved *15 (rank 10) is a non-holding copy, so today's case-law recall overstates by one row (3.8 points: honest figure ~0.795). G-C14's two *18 copies both carry answer content, so it's fine. Across all sources 2,072 labels are shared, and 5 non-case gold rows use one (G-S26, G-X10's regulation group, G-S10/G-X03, G-T11, G-S28). Fix belongs in the eval, not the gold: score gold against the chunk that was retrieved, not just its label.
4. *(original note)* **Two pre-existing gold labels are shared by two chunks** (`T.C. Memo. 2023-128, at *15`, `T.C. Memo. 2024-95, at *18`); unverified that both copies carry the gold content. Across the case corpus 579 labels are shared by 1,249 chunks, so gold matched by label can give unearned credit. Recommendation: check these two in the follow-up audit, and in C6 consider matching gold by chunk key rather than label.

**Dependencies:** C0
**Files:** `eval/golden.jsonl`, `tasks/todo.md`, `STATUS.md`
**Scope:** S

---

## ✅ Checkpoint 1 (human review)
- [x] C2's gold changes approved; the page-selection gap is known (2 rows, 7.7 points)
- [x] Treatment source chosen from C1's numbers (CourtListener keyed + corpus cross-check)

---

## C3: Citation and treatment edge tables

**Description:** Add two Postgres tables (ADR-23): `citations (citing, cited)` and `treatments (citation, kind, by_citation, source, recorded_at, checked_at)`. `checked_at` is when we last looked the case up, separate from when the court decided, because treatments go stale (a pending appeal can be decided next month). Opinions with no treatment found still get a row (`kind = none`) so their check date is kept. Extract `CITES` edges with eyecite from the case text: normalize the PDF line break (`1997- 553` → `1997-553`), add the volume/page → slip-number alias table for reported T.C. opinions, and skip self-citations. Add treatment rows (`affirmed`, `reversed`, `overruled`, `on appeal`) from C1's source. Opinions we don't hold are keys without chunks. Loading is idempotent: re-running replaces the rows.

**Acceptance criteria:**
- [x] The tables are created with the existing schema in `store.py`, and load from one CLI command (`taxcite citations`; ~2 min from cache)
- [x] A hand-labeled sample of 200 edges, stratified by type (`CITES` vs. treatment), is scored: **precision ≥90%, recall ≥85% per type** (the §9.3 gate). Results below
- [x] Row counts match C0's edge list (≈2,500 cited opinions, ≈4,900 `citations` rows) within the documented differences: with C0's normalization the load reproduced C0 exactly (4,911 / 2,496); the final 5,278 / 2,649 adds cites from scanned opinions C0 couldn't read

**Verification:**
- [x] Tests: line-break normalization, the alias table, self-cite skipping and subsequent-history parsing, on fixture text (17 tests, `tests/test_citations.py`, each built from a sentence in the corpus)
- [x] The CI corpus snapshot includes the new tables (`eval/snapshot.py`); restore tolerates an older snapshot without them. **A new snapshot still has to be published** before CI sees the tables

**Measured 2026-09-26 (hand check of 200 edges; the scripts stay in the session scratchpad):**

| Type | Precision | Recall |
|---|---|---|
| CITES (100 sampled + 40 from the spacing repair) | 100/100 on the random sample; the repair's 3 OCR false edges (a garbled masthead self-cite, a split page) are now blocked | **99.9%** (5,115 of 5,121 against a looser independent pattern), up from 95.9% before repairing scanned-text spacing ("116 T .C . 438") |
| Treatment, corpus history (81 sampled) | **75/76** verifiable claims right (1 wrong kind: *Whitehouse*'s vacatur lost across a "supplementing" chain; 4 are `unknown`, a non-claim) | **88%** against the loose yardstick (636/722); of 30 misses classified, 16 aren't history of that case (nested cites, garbled or absent appeal), so ~95% of real history is captured |
| Treatment, CourtListener (19) | **19/19** | 19 held opinions found; 7 appeals known from the corpus are absent from CourtListener (unpublished Westlaw-only dispositions, a name change); covered by the corpus source |

Found and fixed during the check, each now a test: split decisions after the cite ("aff'd in part, rev'd in part" read as affirmed); vacatur mixes; history crossing a sentence break; history belonging to an outer cite ("(citing Tokarski…)), aff'd"); a garbled cite borrowed as the appeal (gap rule); a blank appeal cite borrowing the next one (*Cave*); parallel WL/T.C.M. cites and explanatory parentheticals hiding history; a case-insensitive sentence guard ("slip op. at"); eyecite taking a year from a later parenthetical (*Lavery*); joint captions with two surnames (*Schwab*); firms named after their owner (*Grey*, *Cave*). Idempotency: two consecutive loads leave byte-identical tables (md5 of both, including `recorded_at` and `checked_at`). *Corrected after your first CLI run printed 716, not 718:* that held only within one hash seed. eyecite misreads some short forms ("72 T.C. at 669") as full cites depending on `PYTHONHASHSEED`, and a phantom cite between an opinion and its appeal dropped the history (*Kahla*, T.C. Memo. 2000-127). `full_cites` now drops reporters ending in " at"; both tables fingerprint identically under six seeds, and the *Kahla* sentence is a test.

Known limits, documented not fixed: OCR-damaged cites ("288.F.2d"), "supplemented by…" chains and list forms ("aff'g A, B, and C") attach history to one member only; pending appeals are invisible to both sources.

**Dependencies:** C1
**Files:** `src/taxcite/store.py`, `src/taxcite/ingest/citations.py`, `src/taxcite/cli.py`, `tests/test_citations.py`, `pyproject.toml` (eyecite), `eval/snapshot.py`
**Scope:** M

---

## C4: Treatment flags in answers

**Description:** After synthesis, look up each cited opinion's treatment edges and attach a flag to that citation: `reversed`, `overruled`, `on appeal`, `affirmed`, or `unknown` when the treatment table can't be read. The flag names its source and its check date. The answer text doesn't change. The flags travel in the job record and the SSE `answer` event. "No flag" is shown as "no negative treatment found in <sources>, as of <checked_at>", never as "good law". A check older than 7 days (the weekly refresh the intent doc allows) is marked stale. The scheduled refresh itself is Phase H's.

**Acceptance criteria:**
- [x] **Gate:** G-C03, G-X02 and G-X09 carry a `reversed` flag on their reversed opinion; G-C06 and G-X19 carry none; G-C11 carries `on appeal` if C1's source has it. *Measured 2026-09-27 through the real pipeline (6 runs, $0.005):* *Morehouse* reversed (8th Cir. 2014) on G-C03 and G-X02, *Menard* reversed (7th Cir. 2009) on G-X09; G-C06's cited *Grey* affirmed; G-X19's cited opinions clean (though its answer didn't cite the gold opinion, a retrieval miss); *Patel* reads none with "pending appeals are not tracked", as no source sees it
- [x] Flag precision on every held opinion with a treatment edge, checked against C1's hand-verified records (the golden rows cover only 2 opinions, so this is the broader check): **26/26** non-clean flags match (19 CourtListener, 7 corpus-only); 281 read none
- [x] With the treatment lookup failing, the answer is unchanged and every flag reads `unknown` (and the connection is rolled back, since the answer is published on it next)

**Verification:**
- [x] Tests: flag attachment from fixture rows; fail-open when the lookup raises (6 flag-rule tests in `tests/test_citations.py`, 1 attachment test in `tests/test_jobs.py`; fixture rows, not the live table, because CI restores the pre-C3 snapshot until a new one is published)
- [x] Manual: `POST /queries` with G-X02's question shows *Morehouse* flagged in the SSE `answer` event: `reversed`, by 769 F.3d 616 (ca8 2014), checked 2026-09-26. The answer *text* still says the payments are subject to SE tax, which is wrong for an Iowa client: the flag is the only warning, and acting on treatment is Phase E's

**Built:** `flags()` / `flag()` in `src/taxcite/ingest/citations.py` (merge rules beside the code that writes the table); `jobs.run` attaches `treatments` to the `answer` event. Rules: an overruling stands alone; sources disagreeing about an appeal give `unknown`; else the most serious negative outcome, then `appealed`, then an affirmance; no rows is `unknown`, never "good law"; a check older than 7 days is `stale`. Corpus-only flags are dated by the corpus download (2026-09-22), so they turn stale on 2026-09-29 until Phase H's weekly refresh exists.

**Dependencies:** C3
**Files:** `src/taxcite/generate.py`, `src/taxcite/store.py`, `src/taxcite/api.py`, `tests/`
**Scope:** M

---

## C5: Graph expansion as an ablation rung

**Description:** Add bounded 1–2 hop expansion (a join on `citations`, twice for two hops) to the case-law sub-query as an `eval/retrieval.py` variant, off by default. Measure it on the golden set with ≥5 repeats and report the delta next to C0's ceiling of 0. The point is the honest rung on the ladder, not a gain.

**Acceptance criteria:**
- [x] Case-law Recall@20 with expansion, mean ± sd over ≥5 plan sets, against 0.692; latency added. *Measured 2026-09-27, golden, k=20, 5 plan sets; re-run after C6's key-aware scoring (`eval/results/retrieval-golden-2026-09-27-k20-c5-graph.json`). Under label scoring the arms read 0.815 / 0.777 / 0.777 with the same deltas:*

  | Arm | Case-law Recall@20 | All scored rows | p50 |
  |---|---|---|---|
  | shipped (route + rerank) | **0.777 ± 0.029** | 0.563 ± 0.010 | 1.25 s |
  | + 1 hop | 0.738 ± 0.029 (−3.9) | 0.540 (−2.3) | 1.95 s |
  | + 2 hops | 0.738 ± 0.029 (−3.9) | 0.522 (−4.1) | 1.98 s |

  **Zero gains in any row or plan set; only losses** (1 hop: G-C15 and G-S01 in all 5 sets; 2 hops adds G-X04, G-X06, G-X17). Expansion only displaces: G-C15's gold sat at rank 20, and a statutory row loses its statute to court prose because its plan also held a case-law sub-query. C0's ceiling of 0 holds, and the real effect is negative. The 0.692 in this criterion is pre-C2; the audited baseline is 0.815 ± 0.029 over 5 plan sets (0.833 had come from 3; the two new sets scored 0.808 and 0.769)
- [x] Off by default in the live pipeline (`jobs.run` and `decompose.answer` call `retrieve` with the default `hops=0`)

**Verification:**
- [x] Test: expansion adds only held neighbors within the hop limit, on fixture rows (`tests/test_decompose.py`: held only, 1 vs 2 hops, cited-by direction, co-citation through an unheld opinion, seeds excluded)

**Built:** `neighbors()` and a cached `citation_graph()` in `decompose.py`; `retrieve(..., hops=0)`; a `sections` filter on `search()`; rungs `route+graph1` / `route+graph2` in `eval/retrieval.py`. Planning 2 more plan sets for the 86 golden questions (~$0.05) extended the committed plan cache; the dev entries the CI gate reads are unchanged.

**Dependencies:** C3
**Files:** `src/taxcite/decompose.py` or `src/taxcite/retrieve.py`, `eval/retrieval.py`, `tests/`
**Scope:** S

---

## C6: Page selection

**First, fix the eval's shared-label credit (C2 finding, your call):** gold is matched by page label, but 2,072 labels are shared by several chunks, and G-C24 currently scores a hit from a copy that doesn't state the holding. Credit a gold citation only when the retrieved chunk itself is one the gold means: carry the chunk key on `Hit` and store keys alongside labels for the shared-label gold (G-C18, G-C19, G-C24, G-C14, G-S26, G-X10, G-S10, G-X03, G-T11, G-S28). Re-baseline before measuring anything else; the honest case-law figure is expected near 0.795.

**Description:** Close the real page-selection gap C2 leaves: **G-C10** (*Dirico*: the retriever ranks the petitioner's argument at *20-21 over the holding at *21-23) and **G-C26** (*Gale*: background facts over the reasoning at *26-27), 7.7 points against the audited baseline of 0.815 ± 0.029 (5 plan sets, C5). Two rows can't justify a big mechanism: if the cheapest candidate doesn't move them on dev, record that and stop. Candidates, cheapest first, chosen and tuned on the dev set only:
1. Clean the syllabus chunk: drop the masthead (caption, docket, "Filed …") and expand "P" / "R" to "petitioner" / "respondent".
2. Pull all chunks of an opinion that's already retrieved and rerank them together.

Re-embedding the case corpus costs ~24 min (9,973 chunks at 7/s), and the CI snapshot must be regenerated.

**Acceptance criteria:**
**Done 2026-09-27, part 1 (the eval fix):** `Hit` carries the chunk key; gold can be a label (credits any copy) or a key (credits that chunk only); `eval/retrieval.py` and `eval/validate_pilot.py` accept both. You approved narrowing six rows to the chunk that carries the answer: G-C24 (*15 #3), G-S26 (1.446-1(c)(1) #1), G-X03 and G-X10 (#1), G-T11 (Pub 463 p. 1 #1–#2), G-S28 (Pub 946 p. 59 #3). G-S10, G-C14, G-C18 and G-C19 keep labels: every copy carries the answer. G-C24 and G-S28 are now honest misses (their answer chunk isn't in the top 50 even within its own source), marked `expect_hard` with notes. **Re-baseline, 5 plan sets, k=20 (`eval/results/retrieval-golden-2026-09-27-k20-c6-keyed.json`): case-law 0.777 ± 0.029 (was 0.815; exactly one row, G-C24, in every set), statutory 0.500, compound 0.459 ± 0.012, all 0.563 ± 0.010.** The CI gate's dev check is unchanged at 0.6800 (dev gold has no shared labels).

**Part 2 (page selection) not built, by the brief's own stop rule.** The dev set can't measure it: all 12 dev case-law rows have body-page gold in memorandum opinions, none a summary page or an argument-versus-holding confusion, so neither candidate can be chosen on dev, and tuning on golden is ruled out. The evidence already in hand agrees: within-opinion reranking ranks the holding pages 6th–16th of their own opinion (C0), and summary cleaning targets gold that C2 has since widened with body pages, for a 24-min re-embed and a new snapshot. G-C10 and G-C26 stay as documented misses. **To reopen:** add dev rows whose gold is a holding page competing with argument or background in the same opinion, then measure the two candidates there.

- [x] The mechanism chosen on dev, with the losing candidate's number recorded: neither; dev has no rows that exercise it (above)
- [x] Golden case-law Recall@20 scored once, against the post-audit baseline from C2; no regression over 2 points on the other categories: re-baselined only (0.777 ± 0.029); no mechanism, so no regression
- [x] CI's corpus snapshot regenerated; tier 2's retrieval check re-baselined, if the corpus changed: corpus unchanged; tier 2 re-run, 0.6800 PASS

**Verification:**
- [x] Tests: key-versus-label gold matching (`tests/test_metrics.py`); syllabus cleaning not built, so no fixture tests
- [x] `uv run pytest -q` passes

**Dependencies:** C2
**Files:** `src/taxcite/ingest/caselaw.py` and/or `src/taxcite/retrieve.py`, `tests/test_caselaw.py`, `eval/snapshot.py`
**Scope:** M

---

## C7: Phase C exit report

**Description:** Write `eval/results/phase_c.md` in the shape of `phase_b.md`: C0's ceiling, the edge-extraction scores, treatment flags per golden row, the expansion and page-selection rungs with mean ± sd, failures with examples, and §9.3 recalibration notes. Update the tech doc's Implementation Status.

**Acceptance criteria:**
- [x] Every number traces to a results file or a command listed at the foot of the report. Evidence saved to `eval/results/`: `retrieval-golden-2026-09-27-k20-c5-graph.json`, `…-c6-keyed.json`, `phase-c-treatment-gate-2026-09-27.txt` (re-run, identical to the first), `phase-c-handcheck-citations.txt`, `phase-c-handcheck-treatments.txt`. C0's ceiling reproduces from repo code (command in the report). Three figures carried from C0/C1 were stale and were corrected against the tables (304 citing opinions, 698 opinions with corpus history, 14 held)
- [x] The §9.3 Phase C gate is stated as met or not met, with no reinterpretation: the original recall gate **not met** (−3.9); the revised gate (edges and treatment flags) met, with the date it was revised

**Dependencies:** C4, C5, C6
**Files:** `eval/results/phase_c.md`, `taxcite-technical-documentation.md`
**Scope:** S

---

## ✅ Checkpoint: Phase C complete
- [x] Edges ≥90% / ≥85%; 3/3 reversed rows flagged, 0 false flags
- [x] Tests pass in CI; the faithfulness gate is still green (after you commit and publish the new corpus snapshot). On `corpus-2026-09-27` (2026-09-27): retrieval gate 0.6800 PASS (run 36362575198); faithfulness 0.8715 ± 0.007 over 5 runs PASS (run 36362586552; judge cost $2.27, above the $1.40 recorded in the workflow comment)
- [x] Ready to plan Phase D


---

# TaxCite Phase D — Task List

Plan: `tasks/plan.md` (Phase D, revised after D0). Phase D's gate (§9.3): **≥90% temporal accuracy on the held-out temporal rows** (G-T01–G-T11: 10 of 11), with no more than a 2-point Recall@20 regression on the other categories. **At risk** (D0): G-T03 needs Phase F's sufficiency gate; G-T05 and G-T07 need date arithmetic.

---

## D0: Temporal failure spike

**Description:** Find out what the 11 temporal golden rows actually need before building any of it. The corpus holds one version of each source, so an as-of filter alone can't find text that isn't there. For each row, run today's pipeline and read the answer against the reference answer. Then put the row in the first bucket that fixes it:
1. **Already right:** today's text states the dates (a sunset or start date in the section itself).
2. **Needs the as-of year in synthesis:** the text is retrieved, but the answer applies today's rule to an earlier year.
3. **Needs an effective date from the statutory notes:** the date isn't in the section text (G-T02, G-T10 per their notes).
4. **Needs an earlier version of the text:** which source, and which release point or edition.
5. **Outside every source:** name what would supply it (G-T03's rescheduling).

Then measure the cost of bucket 4. Compare the current USLM release point with one from 2016–2017 by section text hash, and do the same for eCFR at two dates. Count how many sections changed, how many chunks they make, and the embed time at ~7 chunks/s.

**Acceptance criteria:**
- [x] A per-row table: bucket, the evidence (the sentence that decides it, or where it lives), and whether the decomposer's as-of year matches the row's
- [x] Today's baseline: rows answered correctly for their year, and as-of extraction accuracy on all 11 (the wider golden check is deferred to D2, which defines the match rule)
- [x] The versioning cost curve: not needed; no row needs an earlier version
- [x] A decision rule, written down before the numbers: build D4 only if bucket 3 has ≥1 row; build D5 only for a source with a bucket-4 row; if buckets 1–2 alone reach 10/11, say so and shrink the phase
- [x] A decision you confirm, logged in STATUS.md and the engineering log

**Verification:**
- [x] Manual: every number comes from real runs against the corpus, not estimates

**Measured 2026-09-27** (shipped pipeline: route + rerank, k=8 for answers, fresh plans, ~$0.01; answers judged by hand against each row's `answer`; scripts in the session scratchpad):

| Row | as-of: gold → plan | Today | Gold at k=20 | Fixed first by | Evidence |
|---|---|---|---|---|---|
| G-T01 | 2016 and 2026 → none | ✗ applies Pub 17 (2025)'s post-2017 rules to 2016 | 0/2 | **retrieval**, then 2 | §67(h) "Suspension for taxable years beginning after 2017" is in today's text |
| G-T02 | 2023 → 2023 | ✗ "$1,000,000" (neither 2023's figure nor today's) | 0/1 (rank 12) | **retrieval**, then 3 | Note: "shall apply to property placed in service in taxable years beginning after December 31, 2024" (§179, 2025 amendment) |
| G-T03 | 2026 → 2026 | ✗ confident "no deduction" | 0/1 | 5 (+ retrieval) | Scheduling is outside the corpus; the reference answer already says so ✓ |
| G-T04 | 2016 → 2016 | ✗ "not deductible" | 0/2 | **retrieval**, then 2 | §67(a)-(b) + *Gregory* |
| G-T05 | 2026-05 → 2022 | ✗ invents a 6-month extension | 0/2 | **retrieval**, then 1 | Not a temporal failure: §6511/§7503 date arithmetic |
| G-T06 | 2026-09 → 2021 | ✓ (from model memory; nothing cited was retrieved) | 0/2 | **retrieval** | Right but unfaithful |
| G-T07 | 2025 → 2024 | ◐ $2,500, misses the §6651(c)(1) offset | 0/3 | **retrieval**, then 1 | Not temporal |
| G-T08 | 2026 → 2026 | ✗ INSUFFICIENT EVIDENCE | 0/1 | **retrieval**, then 1 | §164(b)(7) states 2026's $40,400 outright |
| G-T09 | none → none | ◐ "50%", no year dependence | 1/2 | retrieval of (n)(2), then 2 | §274(n)(2)(D) "paid or incurred before January 1, 2023" |
| G-T10 | 2024 → 2024 | ◐ right outcome, start date unsupported, no flag | 2/2 | 3 (*corrected in D1's scan: also Pub 17 (2025), p. 3, "qualified tips paid to you in 2025"*) | Note is a cross-reference: "Effective Date of 2025 Amendment note under section 45B" |
| G-T11 | 2025 → 2025 | ✗ gives the Jan 10 machine 100% | 1/2 | 2 | Pub 463 p. 1 states the Jan 20 cutoff; synthesis misapplies it |

- **Today: 1 of 11 correct** (G-T06, and unfaithfully), 3 partial, 7 wrong.
- **As-of extraction: 7/11 exact.** The 4 misses aren't planner errors so much as a definition gap. G-T01 names two years, and the plan holds one. In G-T05–G-T07 the plan gives the *return's tax year* and the gold gives the *event date* (claim, audit, filing). D2 must define which one counts.
- **The binding constraint is retrieval, not time.** Temporal gold-group Recall@20 is **0.200** (4/20). 8 of 11 rows miss the gold statute entirely. The gold is reachable: each row's gold sub-query ranks it 1st–4th within its own source in 17 of 20 groups. The loss comes from the question's plain words (log #44's measured choice) matching IRS publications and regulations over statute.
  | Arm (same plans, k=20) | Temporal Recall@20 |
  |---|---|
  | shipped | 0.200 |
  | **as-of filter on publication edition** (drop editions other than the plan's year) | **0.350** (G-T03, G-T07, G-T08 recover) |
  | statute + regulations only | 0.300 |
  | planner's rewritten sub-queries | 0.250 |
- **Buckets:** retrieval blocks 8 rows. Once retrieved: 1 (answerable from current text) ×4, 2 (year-aware synthesis) ×4, 3 (notes) ×2, **4 (earlier version) ×0**, 5 (outside) ×1.
- **Cost curve: not needed.** No row needs an earlier version. G-T02's reference answer asks for an honest "the 2023 version isn't in the corpus", which the §179 note makes possible.

**Decision rule applied:**
- **D5 is not built.** Bucket 4 has 0 rows.
- **D4 is built** (G-T02, G-T10). It must follow cross-referenced notes: §224's date lives under §45B.
- Buckets 1–2 alone can't reach 10/11, because retrieval blocks 8 rows first. So the phase doesn't shrink. It **gains a retrieval task**.

**Decided 2026-09-27 (you confirmed the plan change):**
1. D3 gives publications valid time from their edition year (measured +15 points on temporal rows).
2. New **D3b: statutory recall on dated questions**, tuned on D1's dev rows. Candidates, cheapest first: a per-source floor inside the statutory route; searching the question *and* the planner's sub-query (union).
3. **The gate stays at 10/11, and D0 says plainly it is at risk.** G-T03 needs the sufficiency gate (Phase F), so it is the one allowed miss. G-T05 and G-T07 need date arithmetic that no temporal mechanism supplies.

**Dependencies:** None (Phase C complete)
**Files:** `tasks/todo.md` (this entry), `STATUS.md`, `docs/engineering-log.md`; spike scripts outside `src/`
**Scope:** S

---

## D1: Dev temporal rows

**Description:** The dev set has no temporal rows (only D24 carries an as-of year), so nothing in Phase D can be tuned without them. C6 stopped at this same gap. Write ≥8 dev rows covering the buckets D0 finds: a sunset date in the text, an amendment effective mid-year, a rule changed between two release points, an ambiguous year, and a retroactive rule. Each row gets a gold `as_of`, gold citations (keyed to the version where it matters) and a reference answer. Same authoring process as B4/B5: Claude drafts from the ingested text, you review every row.

**Acceptance criteria:**
- [x] ≥8 rows, each one tied to a D0 bucket (14 after two validation scans)
- [x] No citation or opinion shared with the golden set (checked against golden, pilot and dev gold)
- [x] `uv run python eval/validate_pilot.py eval/dev.jsonl` passes

**Verification:**
- [x] You review every row

**Validated 2026-09-27 in two scans (below): 14 rows, D26–D39. You approved all 14 (`reviewed: true`), and the G-T10 fix.** All are `scored_from: "D"`, so the CI retrieval gate (which scores only `"B"` rows) is unchanged. The validator passes (0 of 39 need attention). No gold label is shared with the golden or pilot sets.

| Row | D0 bucket / shape | Section | as_of | What it tests |
|---|---|---|---|---|
| D26 | 2, and a year with no publication edition | §163(h)(3) (keyed: part 1 $1M, part 3 (F)) | 2016 | $1,000,000 vs $750,000; the pre-Dec-15-2017 grandfather |
| D27 | 2, mid-year cutoff on two dates (G-T11's shape) | §30D(h), (a)-(c) | 2025 | August vs October 2025 car; acquired after Sept 30, 2025 |
| D28 | 1, and a year with no publication edition | §25D(f)-(h) | 2021 | 26% for 2020–2021 |
| D29 | 1, termination | §25C(h)-(i) | 2026 | placed in service after Dec 31, 2025 |
| D30 | 3, cross-referenced note (G-T10's counterpart) | §225 | 2024 | start date only in a note under §63 |
| D31 | 2, tax year vs event date | §163(h)(4) (keyed part 1) | 2025 | loan incurred March 2024, before the Dec 31, 2024 start |
| D32 | 3, retroactive, and a year with no publication edition | §6050W(e)-(g) | 2023 | $20,000/200 restored "as if included in" ARPA (notes only) |
| D33 | ambiguous year (G-T09's counterpart) | §217(k), (a)-(c) | none | suspension after 2017; the Armed Forces and intelligence-community exceptions |
| D34 | procedural, tax year vs event date (G-T05–G-T07's shape) | §6502(a)-(b) | 2012 | 10 years from a June 3, 2014 assessment |

**Dev now exercises D3b's failure, unlike C6's dev set.** In 8 of 9 rows the question's own words miss the gold, and the gold sub-query reaches it. D31 and D34 are reached by the question itself. Every answer is written from the corpus text plus the USLM notes quoted in D0; no outside fact is used.

**Scan 1, per row (every gold chunk and its neighbours read in full; each answer checked against the text, not memory):**
- **D26:** the answer now states its conditions, itemizing and a qualified residence. The $1,000,000 limit (part 1), the post-2017 $750,000 substitution, and the Dec 15, 2017 grandfather (part 3) are confirmed. Keyed gold is right: parts 1 and 3, not part 2 (the pre-1987 debt rules).
- **D27:** $3,750 + $3,750 per vehicle (§30D(b)), plus the MAGI test on the lesser of this year's and last year's income (§30D(f)(10)), confirm "up to $7,500 … income limits". (h) turns on *acquired*, and the question makes acquisition and placed-in-service the same day, so the gap between them doesn't arise.
- **D28, D29:** confirmed. §25D(g)(2) is 26% for 2020–2021 under both the pre- and post-2022 text. §25C(i) turns on placed in service, so the unstated payment date can't change the answer.
- **D30: the answer was wrong on one point, now fixed.** It said the start date was only in the notes, but Pub 17 (2025), p. 3 lists overtime among "the new deductions" for 2025. The answer now accepts either the evidence or an honest "not in my sources", and must not apply the deduction to 2024.
- **D31:** confirmed. §163(h)(4)(E)(ii)'s refinancing rule only carries forward qualifying debt, so a 2024 loan can't be refinanced into eligibility. Keyed part 1 is right.
- **D32:** confirmed, and the notes now say the exception covers only third party settlement organizations (§6050W(e), (b)(3)).
- **D33:** confirmed. The Armed Forces rule is (g); the gold stays (k) + (a)-(c), with the reason in the notes.
- **D34:** confirmed. No §6503 suspension, because the question excludes one.

**Scan 2, across the set:**
- **Gold too narrow:** D31 widened to Pub 17 (2025), p. 3 (#5, #6), a same-year edition that states "a vehicle you purchased in 2025". Pub 334, p. 5 ("Beginning in 2025") can't decide the loan date and isn't gold. Every other rule was searched for in the publications and regulations: none states it for the row's year.
- **Leakage:** no gold label is shared with golden or pilot (re-checked with the new rows). The topic pairing D38 ↔ golden G-I01 (mileage 2026 vs 2027, no shared gold) is documented on D38.
- **Missing edge cases, now added:**
  | Row | Edge | Why it matters |
  |---|---|---|
  | D35 | Today's text answers a *different* year, and the right year's text is only in the notes (§21 applies 35%; 2023 was 20%) | G-T02's dev twin, and the Phase D exit condition. No dev row had this shape |
  | D36 | Relative year ("this year's return"), same facts as D35 | The planner's prompt has no current date, so it can't resolve "this year" |
  | D37 | Two years in one question, one of them after a sunset and after today; today's text *implies the wrong start year* (§151(d)(5) opens "after December 31, 2017", but (C) began in 2025) | G-T01's shape, plus a literal-reading trap |
  | D38 | A 2025 publication states a 2026 fact (72.5 cents) | An "other editions out" filter drops the only source |
  | D39 | A year with no source at all, where neighbouring years' figures and a historical depreciation table are retrievable | The filter plus an honest refusal; `expect_insufficient` |
- **Validator:** 0 of 39 need attention. D30 and D35 are marked `verified` because their answers quote notes, not the gold chunk.

**Findings for later tasks:**
- **D3, edition filter:** a 2025 edition carries facts about other years: next year's figures (D38), "What's New" statements that are evidence about the year before (D30, and golden G-T10), and historical tables (D39's trap). D0's "drop other editions" simulation is too blunt. D3 must measure D30, D38 and D39 alongside the 0.200 → 0.350 gain.
- **D4:** the USLM *Amendments* notes quote prior text verbatim ("Prior to amendment, text read as follows: …35 percent…"). That is a cheap way to recover earlier versions, worth weighing for D35 and G-T02.
- **D2/D7:** the planner needs today's date to resolve relative years (D36).
- **Golden audit finding (approved and applied 2026-09-27: `answer` and `notes` only, gold unchanged, validator passes 0/115; no eval code reads reference answers, so no score moves):** G-T10's reference answer says the tips deduction's start date "appears only in the statutory notes", but Pub 17 (2025), p. 3 says "qualified tips paid to you in 2025", and D0's run retrieved that page. Suggested fix: accept either the evidence or an honest "not in my sources", the same wording as D30.

**Dependencies:** D0
**Files:** `eval/dev.jsonl`
**Scope:** S

---

## D2: Temporal scorer

**Description:** Add a temporal accuracy mode to the eval. First fix what "as-of" means (D0 found two meanings): the **tax year** whose rules apply. A row whose question turns on an event date (G-T05–G-T07) records both, the tax year for the match and the event date for the answer; that is a golden gold change you review. A row naming two years (G-T01) is scored on its answer alone. Per row: (a) the plan's as-of year matches the row's tax year (exact, no judge); (b) an LLM judge from the other provider grades the answer against the reference answer for that year, using §9.2's 3-point rubric and defect tags. A second, differently prompted judge grades the same answers, and Cohen's κ is reported. A row passes only if (a) holds and (b) is *Correct*. Answers are cached, so a re-score only re-judges.

**Acceptance criteria:**
- [x] One command scores the temporal rows of a set and writes a results file (`eval/temporal.py`)
- [x] ≥3 judge repeats per row on dev, with spread reported; κ between the two judges ≥0.7, or the metric is marked untrusted (κ 0.81–0.93 over three calibration runs)
- [x] Cost per golden run measured (expected well under $1): **~$0.08 estimated** from dev's $0.099 for 14 rows × 3 repeats plus the grounding check; golden is not run until D7, to keep it held out

**Verification:**
- [x] Tests: the as-of match and the pass rule, on fixture plans and fixture verdicts (no API calls): `tests/test_temporal.py`, 10 tests (as-of formats, two-year rows, invented years, pass rule, a hand-computed κ); 196 pass
- [ ] Manual: the judge's verdicts on dev are read by you for at least 5 rows

**Built 2026-09-27:** `eval/temporal.py` reuses the faithfulness harness's answer cache and plan pinning (`pipeline_answer`, `cached_decompose`), the §9.2 rubric and its alternate phrasing (`llm_bench.judge`, log #31), and the claim checker (`extract_claims`, `judge_claims`). The judge is `claude-haiku-4-5` (other provider). The only new logic is `as_of_match`, `passed` and `kappa`.

**Calibration on dev (14 rows, 3 repeats, `eval/results/temporal-dev-2026-09-27.json`):**

| | Value |
|---|---|
| Temporal accuracy | **0.381 ± 0.041** (0.357 / 0.429 / 0.357); judge noise is about half a row |
| Grounded accuracy (diagnostic) | 0.214–0.286: of the correct answers, only those whose every claim is in the retrieved sources (or the question) |
| As-of extraction | 9/13 scored rows (0.692) |
| κ, primary vs alternate judge | 0.888, 0.810, 0.925 over three calibration runs (≥ 0.7) |
| Judge cost | $0.099 per run |

**What calibration changed:**
- **A grounding diagnostic was added, and it isn't in the pass rule.** The reference-answer judge never sees the sources, so a correct answer can come from the model's memory: D35's "20%" cites Pub 17 (2025), p. 34, which doesn't state it, and §21 wasn't retrieved (G-T06 in D0 was the same). Each answer is now also checked claim by claim against its sources, and the question counts as a source, because restating its facts isn't memory. That fix took D32 and D34 from false "ungrounded" to grounded. **Decided 2026-09-27: report grounding, don't gate on it.** §9.3's gate is unchanged, faithfulness keeps its own gate, and the Phase D report shows both figures per row.
- **D28's reference answer was trimmed.** It carried a non-material sentence (§25D(e)(8)), and the judge counted its absence as `missing_condition`. The sentence moved to the row's notes. The same risk may sit in golden reference answers. If D7's per-row table shows `partial` for a non-material omission, audit that row.
- The judge sometimes emits a tag outside the taxonomy (`wrong_conclusion`). It is kept as given, and it doesn't affect the grade.

**Found for later tasks (the planner, not the scorer):**
- **No current date:** D36's "this year" is planned as **2023**, and its answer applies the old 20% schedule.
- **Event date vs tax year:** D31 is planned as 2024 (the loan), not tax year 2025. The planner prompt says "the tax year or date the question is about".
- **Missed years:** D26 ("on their 2016 joint return") and D34 (the "2012 income tax") are planned with no year at all.
- These are prompt changes, tuned on dev in D3/D7. They invalidate the plan cache for affected questions.

**Golden change, approved and applied 2026-09-27 (the as-of rule):** G-T05, G-T06 and G-T07 record an event date in `as_of`. Under D2's rule, `as_of` becomes the tax year and the event date moves to the notes:

| Row | `as_of` now | Proposed | Event date (to notes) |
|---|---|---|---|
| G-T05 | 2026-05 | **2022** (the return) | refund claim, May 2026 |
| G-T06 | 2026-09 | **2021** | audit opened, September 2026 |
| G-T07 | 2025 | **2024** | filed August 30, 2025 |

This changes no gold and no reference answer, only which year the as-of check expects. D0's planner already returned exactly these three years.

**Dependencies:** D0 (D1 to calibrate)
**Files:** `eval/temporal.py` (or a mode in `eval/ragas_eval.py` if it fits), `tests/`
**Scope:** M

---

## ✅ Checkpoint 1 (human review)
- [x] D0's decision confirmed (2026-09-27): D4 built for G-T02 and G-T10; D5 dropped; D3b added; publication valid time in D3
- [x] D1's rows approved (2026-09-27)

---

## D3: Valid-time columns and the as-of filter

**Description:** Add `effective_date` and `superseded_date` to `chunks` (migrated the way `source_revision` was) and to the Qdrant payload, with a payload index. **Publications are dated by edition:** `Pub 17 (2025)` is valid for tax year 2025 only. Statute dates arrive with D4; regulations and case law stay undated. When the plan has an as-of year, filter every sub-query's search to chunks valid in that year. Undated chunks always pass. D0's simulation (drop other editions) moved temporal gold Recall@20 from 0.200 to 0.350; the built filter should reproduce that. Measure approximate versus exact search under the filter on dev (ADR-17 measured a 22.1% loss for approximate search), and ship the one that loses nothing unless it costs >100 ms.

**Acceptance criteria:**
- [x] The filter is off when no as-of year is extracted, and undated chunks always pass
- [x] Temporal gold Recall@20 reproduces D0's 0.350 on the same plans (or the difference is explained): **0.350 exactly** with the exact-year window
- [x] Filtered approximate vs. exact: recall against the exact top-k, and latency, on dev: approximate keeps **99.2%** of the exact dense top 50 (min 96%), and exact costs +3 ms (13 vs 10 ms p50). **Exact ships**
- [ ] Every golden row scored with the filter on: ≤2-point Recall@20 regression per non-temporal category (≥5 plan sets)

**Verification:**
- [x] Tests: the validity window at its edges, on fixture chunks: `test_edition_filter_keeps_undated_chunks_and_nearby_editions` (in-memory Qdrant: undated, same year, older and newer windows, no nearby edition), `test_tax_year_is_one_year_or_none`, `test_the_plans_tax_year_reaches_search_only_when_editions_are_on`
- [x] `uv run pytest -q` passes (205)

**Built 2026-09-27, smaller than planned.** Every publication in the corpus is a 2025 edition, and its year is already in `as_of`. So D3 needed no new Postgres columns and no re-embedding:
- an integer `edition` payload on publication points (written by `index.sync`; the 2,043 existing points were backfilled with `set_payload`), with an integer payload index;
- `retrieve.edition_filter(year, back, forward)`: undated chunks always pass;
- `decompose.tax_year()`: one year or none, so multi-year plans aren't filtered;
- the window is passed only when a filter applies, and dense search is exact when filtering;
- `eval/retrieval.py` arms `route+ed0`, `route+ed-1` and `route+ed±1`, plus `--scored-from D`, which adds the temporal rows.

The statute's valid time arrives with D4, where a column is first needed.

**Measured:**

| Arm | Golden temporal Recall@20 (D0's plans) | Dev temporal Recall@20 (3 plan sets) |
|---|---|---|
| shipped (`route`) | 0.200 | 0.423 |
| ed0 (same-year editions) | **0.350** | 0.500 |
| **ed-1 (same year and the one before)** | 0.250 | **0.577** |
| ed±1 | 0.200 | 0.577 |

- **Window chosen on dev: ed-1.** It keeps D38's 2026 fact from a 2025 edition, and gains D35 and D36. Golden would have chosen ed0: G-T03 and G-T08 (2026) only recover when the 2025 editions are dropped. For a 2026 question a 2025 edition is both the only source (D38) and the text crowding out the statute (G-T03, G-T08). That second half is dilution, which is D3b's job. Recorded, not chosen.
- **Answers disagree with recall.** With ed-1 live, dev temporal accuracy fell from **0.36–0.43 (12 judge repeats) to 0.286** (`temporal-dev-2026-09-27-d3.json`). D30 and D32 went from correct to incorrect, and D31 went from partial to correct. Removing the 2025 editions removed the only plain-English year evidence. D30 then applied today's §225 to 2024. D32 filled with regulations and fell back on a stale memory of the $600 threshold, which the 2025 law retroactively repealed for 2023; Pub 17 (2025) had given the $20,000 / 200 rule. Recall was blind to this because D1's gold doesn't count off-year editions.
- **Decided 2026-09-27 (you agreed): the filter stays off in the live pipeline until D7.** `decompose.EDITIONS = None`, passed at both live call sites (`decompose.answer`, `jobs.run`). D7 re-decides with D3b and D4 in place, on dev answers, not recall.
- **Golden regression, non-temporal categories (ed-1 vs shipped, 5 plan sets, k=20): moved to D7** (you decided, 2026-09-27). The first run was stopped unfinished to free the CPU for D3b. With the filter off in the live pipeline, the check only matters when D7 re-decides the filter, and it is more meaningful there, measured together with D3b and D4.
- Also fixed: `eval/temporal.py` names its results file after a non-default answer cache, because a D3 run had overwritten the calibration file (the log #64 mistake again). The calibration file was regenerated from its cached answers.

**Dependencies:** Checkpoint 1
**Files:** `src/taxcite/chunk.py`, `src/taxcite/store.py`, `src/taxcite/index.py`, `src/taxcite/retrieve.py`, `src/taxcite/decompose.py`, `tests/`
**Scope:** M

---

## D3b: Statute recall on dated questions

**Description:** D0 found that 8 of 11 temporal rows never retrieve their statute. The pipeline searches with the question's own words (log #44), which match plain-English publications and regulations. Each row's legal-vocabulary sub-query ranks the statute 1st–4th, so the statute is reachable. The planner's rewritten sub-queries scored 0.250, below D3's filter alone (0.350). Candidates, cheapest first, chosen on D1's dev rows only:
1. A per-source floor inside the statutory route: reserve slots for `usc` the way `chunks()` reserves one per sub-query.
2. Search the question *and* the planner's sub-query, and merge the two pools before reranking.

If neither moves dev, record the numbers and stop (C6's rule).

**Acceptance criteria:**
- [x] Each candidate's dev temporal and dev statutory Recall@20, ≥3 plan sets; the winner chosen on dev: **statute search + 1 reserved slot**
- [x] Golden scored once with the winner: temporal gold Recall@20 against D3's figure, and ≤2-point regression on every other category (≥5 plan sets): temporal **0.200 → 0.400** (D3's best was 0.350); all B rows 0.563 → 0.602, no category down
- [x] The CI retrieval gate's dev check still passes, and its threshold is re-baselined if the default changed: gate now scores `route+statute1`, floor 0.66 → **0.70** (measured 0.720; `route` reproduced 0.680)

**Verification:**
- [x] Tests: the source floor (or the pool merge) on fixture hits: `test_statute_floor_searches_the_statute_and_keeps_it_through_reranking`
- [ ] `uv run pytest -q` passes

**Built and measured 2026-09-27.** First, a ceiling check. Searching the question's own words within the statute alone reaches **0.679** of dev's statute gold at k=20; the planner's sub-query only lifts that to 0.714. So `retrieve(statute=n)` adds a statute-only search to each statutory sub-query, and `chunks()` reserves n slots for the best-ranked statute chunks. `retrieve(union=True)` pools the sub-query's own text (candidate 2).

| Dev, 38 scored rows, 3 plan sets | All @20 | Statutory | Temporal | Case law | Compound | All @8 |
|---|---|---|---|---|---|---|
| shipped (`route`) | 0.605 | 0.654 | 0.423 | 0.833 | 0.667 | 0.539 |
| **+ statute, floor 1** | **0.724** | **0.808** | **0.615** | 0.833 | 0.667 | **0.605** |
| floor 2 / 3 | 0.724 | 0.808 | 0.615 | 0.833 | 0.667 | 0.605 |
| union | 0.684 (range 0.039) | 0.744 | 0.526 | 0.833 | 0.750 | |
| union + floor 2 | 0.732 ± 0.013 | 0.821 | 0.615 | 0.833 | 0.694 | |

- **Floor size doesn't matter** (1 = 2 = 3 at k=20 and k=8); the gain is getting the statute into the pool. The shipped route pool averaged 17.4 chunks. The union adds plan noise for an unresolved edge. **Chosen: floor 1**, live as `decompose.STATUTE = 1`, for about +250–450 ms at p50.
- **Answers, dev temporal (the D3 lesson):** 0.381 ± 0.041 against a 0.36–0.43 baseline, so neutral within noise. The three rows that moved were traced to synthesis nondeterminism (D31: identical sources, different text) and judge variance (D30), not to D3b. D26 improved through Pub 587. The statute search pulled the wrong sections for it (§221, §121), which is the vocabulary ceiling.
- **Golden, scored once (`retrieval-golden-2026-09-27-k20-d3b.json`, 5 plan sets):** all 0.563 → **0.602** (each plan set up by more than the 0.029 spread), statutory 0.500 → **0.607**, compound 0.459 → 0.470, case law 0.777 unchanged. Golden temporal on D0's plans: **0.200 → 0.400**, recovering G-T03, G-T08 and two of G-T07's groups. That resolves D3's conflict: those were the rows only the exact-year filter could recover, and the statute floor gets them without dropping publications. The ed-1 filter on top adds nothing (0.400). Still missed: G-T01, G-T04, G-T05, G-T06, where the question's words don't reach §67, §6511 or §6501 even within the statute.
- Evidence: `retrieval-dev-d3b-k20.json`, `-k8.json`, `-gate-k10.json`, `temporal-dev-2026-09-27-d3b.json`, `retrieval-golden-2026-09-27-k20-d3b.json`.

**Dependencies:** D1, D3
**Files:** `src/taxcite/decompose.py`, `eval/retrieval.py`, `tests/test_decompose.py`
**Scope:** S–M

---

## D4: Effective dates from statutory notes

**Description:** Built for G-T02 and G-T10 (D0). Read "Effective Date of [year] Amendment" notes from the USLM XML the parser already downloads, and set `effective_date` on the chunks of the subsections each note names. Follow cross-references: §224's note reads "Effective Date of 2025 Amendment note under section 45B". §179's is in place: "shall apply to property placed in service in taxable years beginning after December 31, 2024". A note the parser can't read with confidence leaves the date null (always passes the filter), never a guess. A statute chunk whose date is after the as-of year still passes the filter, flagged for synthesis (D7), because it is the best evidence available.

**Acceptance criteria:**
- [x] A hand-checked sample of 50 parsed dates, stratified by note shape: accuracy ≥90% on dates set, coverage reported (the §3.2 pattern). **Fresh round 3: 48–49/50 (96–98%)**; coverage 1,795 of 2,576 amended chunks (below)
- [x] G-T02's §179(b) and G-T10's §224 chunks get their date (2025 amendment: taxable years beginning after December 31, 2024)

**Verification:**
- [x] Tests: each note shape found in the sample, as fixture XML taken from the real notes: `tests/test_usc_notes.py` (9 tests) on `tests/fixtures/usc_notes.xml` (§§ 179, 224, 45P, 246A, 25D, 23, cut from the release point); 215 pass

**Built 2026-09-27:** `src/taxcite/ingest/usc_notes.py`. For each statute chunk it finds the latest amendment since 2012 that changed that chunk's text, joins it to that law's Effective Date of Amendment note (following "note under section X" references), and keeps the entry itself, which often quotes the replaced text ("substituted “$2,500,000” for “$1,000,000”", "Prior to amendment, text read as follows"). A section added since 2012 uses its own Effective Date note. The result is stored as `chunks.effective` (jsonb) and in the Qdrant payload; `usc.parse` attaches it. The 11,030 existing rows and 1,795 points were backfilled (SQL upsert plus `set_payload`), with no re-embed.

**Hand checks, three fresh samples of 50, stratified by note shape** (quoted law, summary/cross-reference, retroactive, section added). Each link was checked for two things: the amendment is really the latest to that chunk's text, and the rule is that law's.

| Round | Correct | Failure classes found, then fixed |
|---|---|---|
| 1 | 40/50 (80%) | catchline renames treated as text changes; subsections named only in the entry text; a note's general rule used where a paragraph governs the amendment's own subsection; "not applicable to…" read as the rule |
| 2 (fresh) | 40/50 (80%) | subsection-level entries that touched only the heading, intro or concluding text, attributed to every child (fixed with **text evidence**: an entry quoting its new text links only to the chunk containing it); "(4) to (6)" ranges; a rule in subsection (a) of the law applied to an amendment made by (e) |
| 3 (fresh) | **48–49/50 (96–98%)** | one comma-chained exception clause (fixed in the module; unit test); one link not fully verifiable |

The module differs from the spike in two ways. Range chunks hold their subsections whole, and a subparagraph marker may follow a heading ("Inflation adjustment. (A) In general"). Both added links: 20 of the added links were spot-checked, 20/20 right.

**Coverage:** 1,795 of 2,576 statute chunks amended since 2012 (70%) carry a rule. The rest carry nothing, which by design never passes as a guess. Known limit: list rules ("shall apply to— (1) … executed after December 31, 2018", §61 alimony) fall back to the enactment date.

**The rows that motivated it:** §179(b)(1) (G-T02) and §224 (G-T10) get "taxable years beginning after December 31, 2024". §225 (D30) gets the same; §21(a) (D35) gets "after December 31, 2025" plus the 2025 entry; §151(d)(5) (D37) gets "after December 31, 2024". §163(h)(3) part 1 (D26's $1,000,000 rule) correctly gets none, while parts 2 and 3 get 2020 and 2025. §6050W(e) (D32) is marked retroactive.

**Not in D4, and D7's call:** how synthesis uses it (the flag "this text applies from…", and when to quote the replaced text). The CI snapshot must be regenerated to carry the column and payload; that happens once, with D7.

**Dependencies:** D3
**Files:** `src/taxcite/ingest/usc.py`, `tests/test_usc.py`
**Scope:** M

---

## ~~D5: Prior versions of changed sections~~ (dropped after D0)

No temporal row needs an earlier version of the text (D0: bucket 4 had 0 rows). G-T02's reference answer asks for an honest "the 2023 version isn't in the corpus", which D4's note makes possible. **To reopen:** a golden or dev row whose correct answer needs earlier statutory text. Price it then with D0's method: section hashes compared across two release points, with `fetch_usc(release=...)`.

---

## D6: Transaction time: retire, don't delete

**Description:** Add `recorded_at` (backfilled from `fetched_at`) and `retired_at` to `chunks`. The re-ingest sweep sets `retired_at` instead of deleting the row. Retrieval reads only unretired rows, and retired points are still removed from Qdrant. One documented SQL query answers "which text did TaxCite hold for this citation on date Y".

**Acceptance criteria:**
- [x] A re-ingest that drops a paragraph retires it; its text is still in Postgres and absent from search (Postgres: `test_a_dropped_paragraph_is_retired_by_the_sweep`; search: `index.sweep` unchanged, still removes the point)
- [ ] The audit query is in the report, run against a real retired row: **no real retired row exists yet** (`chunk_versions` is empty until a re-ingest changes or drops text: Phase H's refresh, or a re-ingest in D8). Run against test rows meanwhile

**Verification:**
- [x] Tests: sweep retires rather than deletes; retired rows never reach `search`: 3 tests in `tests/test_store.py` (a rewrite is retired, not lost; a dropped paragraph is retired by the sweep; an unchanged re-ingest keeps its `recorded_at` and retires nothing). 218 pass

**Built 2026-09-27, by a different route than planned.** A `retired_at` column on `chunks` would have needed `retired_at IS NULL` in every reader. Instead:
- `chunks` stays "what TaxCite holds now".
- A Postgres trigger (`chunks_retire`) copies every version TaxCite stops holding into `chunk_versions (key, source, citation, text, recorded_at, retired_at)`. That covers a row the sweep deletes, and also **text an amendment rewrites in place**. The same key (`citation#body#part`) survives an amendment, so the planned version would have lost exactly the history ADR-2 is about.
- `chunks.recorded_at` is when the current text was first recorded. The upsert keeps it unless the text changes; a rewrite is retired at its replacement's `recorded_at`, and a dropped row when the sweep ran.
- The audit query is `store.held_at(conn, citation, at)` (`HELD_AT` in `store.py`): the current rows recorded by `at`, plus the retired rows whose window covers `at`.
- No reader changed, and Qdrant is untouched: `index.sweep` still removes retired points.

**Live migration:** 28,747 rows backfilled with `recorded_at = fetched_at`, the trigger installed, `chunk_versions` empty. **Known imprecision:** the statute rows' `recorded_at` is 2026-09-28, because D4's backfill re-saved them hours before this migration. For pre-D6 rows the last fetch is the best record there is.

**Dependencies:** D3 (the same migration)
**Files:** `src/taxcite/store.py`, `src/taxcite/index.py`, `tests/`
**Scope:** S

---

## D7: As-of-aware synthesis

**Description:** Give synthesis the plan's as-of year, and each chunk's valid-time window. The answer states the tax year it answers for. When a statute chunk took effect after that year (D4), the answer says the earlier rule isn't in its sources and doesn't apply today's text or guess (G-T02). D0's four year-reasoning rows are the targets: G-T01, G-T04, G-T09 and G-T11 (Pub 463's January 20 cutoff misapplied). When the question names no year, it answers for current law and says so, naming any change the retrieved text dates. When a retrieved source's validity window doesn't cover the year, the answer says the source may not apply. Prompt changes are tuned on dev only; the faithfulness gate is dispatched on the branch before merging (ADR-22).

**Acceptance criteria:**
- [x] The golden regression check moved from D3: the edition filter (ed-1), with D3b and D4 in place, against shipped, ≤2-point Recall@20 regression per non-temporal category, 5 plan sets, k=20. **Superseded:** the filter lost on dev answers even with D3b and D4 (0.429 vs 0.452) and stays off, so it has nothing to regress. The check that matters instead is the new *planner* against golden retrieval: **met**, all 0.602 → 0.606 (5 plan sets, range 0.012); statutory 0.607 level, case law 0.777 → 0.800, compound 0.470 → 0.462 (−0.8). Cost: p50 1.75 s → 2.99 s, from more sub-queries (2.34 per question vs 2.05) (`retrieval-golden-k20-d7-planner.json`)
- [x] Dev temporal accuracy (D2) before and after, ≥3 repeats: **0.381 ± 0.041 → 0.452 ± 0.041** (as-of extraction 0.692 → 0.846)
- [x] **Gate, scored once:** golden temporal accuracy ≥90% (10/11), per-row table with defect tags: **NOT MET, 0.394 ± 0.052 (4–5 of 11)**; D0's baseline was 1/11 (table below)
- [x] The faithfulness gate stays green (≥0.855): **fixed build 0.882 ± 0.011, refusals 0.125–0.156 (mean 0.135), run 36381406751.** The first run passed (0.866) **at a refusal rate of 0.52–0.57** (Phase C 0.125), caused by rule 6 going to every question. Fixed in `0f2caf7` (the rule and header only when dated): refusals 13/96 locally, dev temporal 0.500. Re-run dispatched (36381406751), PENDING. **Added (you asked, 2026-09-28):** the faithfulness gate now also fails on a mean refusal rate above 0.25 (`--max-refusal-rate`; healthy band 0.125–0.135, broken 0.52–0.57); `test_refusal_rate_gate`; both paths smoke-tested (forced FAIL exits 1). Golden temporal re-scored once after the fix (your option b): **0.152 ± 0.052**, same retrieval, different answers. The scorer caches one answer per row, so its ± misses the generator's own variation

**Verification:**
- [x] Manual: `POST /queries` with G-T02's question doesn't apply $2.5M to 2023. It says the current limit applies from taxable years beginning after 2024, and names the year, in the SSE `answer` event. **Half met (2026-09-28):** `as_of` 2023; the answer names 2023 and doesn't apply $2.5M, but gives "$1,000,000 … reduced above $2,500,000", the pre-2025 *base* amounts from the amendment note's replaced text, not 2023's inflation-adjusted $1,160,000, and doesn't say that figure isn't in its sources

**Built 2026-09-27/28.**
- **Synthesis:** `Hit.effective` from the payload. `generate.effective_note` marks a statute source "Effective: …" when its current text took effect after the question's earliest year, or retroactively, and quotes the amendment entry (often the replaced text). The prompt carries the tax year(s). Rule 6: state the year answered for; text that states rules for particular years governs those years; don't apply later text to an earlier year (use quoted earlier text, or say it's not in the sources); with no year, answer for current law and name the change.
- **Planner:** today's date in the user message, "as_of" defined as the tax year of the return or transaction, not a later event's date; two years kept; a present-tense question with no year is null.
- One tuning iteration on dev after reading answers, then stop: rule 6 gained "text stating rules for particular years governs them" (D28 had refused 2021's 26%, which the schedule states), and the planner gained the present-tense rule.

**Dev (14 rows, 3 judge repeats, `temporal-dev-2026-09-27-d7.json`, `-2026-09-28-d7ed.json`):**

| Arm | Temporal accuracy | Grounded | As-of |
|---|---|---|---|
| D3b live, old planner and synthesis | 0.381 ± 0.041 | 0.21–0.29 | 0.692 |
| **D7** | **0.452 ± 0.041** | 0.21–0.29 | 0.846 |
| D7 + edition filter (ed-1) | 0.429 ± 0.000 | 0.143 | 0.846 |

**The edition filter stays off:** even with D3b's statute slot and D4's dates, it loses D32, whose only source for the retroactively restored $20,000 threshold is the 2025 edition, and it halves grounding. `decompose.EDITIONS = None` is final for Phase D.

**Golden temporal gate, scored once (`temporal-golden-2026-09-28-d7.json`): 0.394 ± 0.052, NOT MET (≥0.90 = 10/11).**

| Row | Grades (3 repeats) | Why |
|---|---|---|
| G-T01 | correct | two years; §67(h) retrieved and read by year |
| G-T02 | incorrect ×2, correct ×1 | gives the pre-2025 base amounts ($1,000,000 / $2,500,000) from the note's replaced text as 2023's figures; 2023's were inflation-adjusted |
| G-T03 | incorrect | outside every source (DEA rescheduling): the sufficiency gate's job (Phase F) |
| G-T04 | partial | §67 reached only in part |
| G-T05 | partial | date arithmetic (§7503 weekend) |
| G-T06 | correct (ungrounded) | from memory; §6501 not retrieved |
| G-T07 | partial / incorrect | misses the §6651(c)(1) offset |
| G-T08 | incorrect | refuses: at k=8 the one statute slot goes to §225/§1, not §164(b)(7). D3b's recovery was at k=20 |
| G-T09 | incorrect / partial | planner put 2026 on an undated question despite the new rule; answers current law without the pre-2023 exception |
| G-T10 | correct | "not applicable for 2024", the D4 date used |
| G-T11 | correct | the January 20 cutoff applied to both machines |

**Findings for the report:**
- **Two of the misses are retrieval at synthesis depth,** not time: G-T08 at k=8, and G-T06 answering right from memory. The recall metrics at k=20 overstate what synthesis sees.
- **Recovering an earlier version from the notes has a trap:** replaced text can be a *base* amount that was inflation-adjusted every year (G-T02). The statute never stated the year's figure; Rev. Procs did, and they aren't in the corpus.
- **The planner's year extraction is unstable at the edges** (gpt-4o-mini): D33, D34 and G-T09 moved between runs even with the rule in the prompt.
- **Synthesis ignores a note sometimes** (D37 applied the senior deduction to 2022 with the note attached).
- The faithfulness gate must be dispatched on a branch with these prompt changes (ADR-22), and it needs the CI snapshot regenerated first, so CI has D4's dates. Both are outward actions, awaiting your go-ahead.

**Dependencies:** D2, D3, D3b, D4
**Files:** `src/taxcite/generate.py`, `src/taxcite/jobs.py`, `tests/`
**Scope:** M

---

## D8: Phase D exit report

**Description:** Write `eval/results/phase_d.md` in the shape of `phase_c.md`: D0's buckets and decision (versioning measured and dropped), D3b's recall rung, the effective-date accuracy, the filter's rung on the ladder with the approximate-versus-exact numbers, temporal accuracy per row, failures with examples, and §9.3 recalibration notes. Update the tech doc's Implementation Status and baselines table.

**Acceptance criteria:**
- [x] Every number traces to a results file or a command at the foot of the report (D0's plans and the D4 hand checks now saved in `eval/results/`; the temporal-recall script re-run: all six arms reproduce). All numbers in: faithfulness 0.882 at refusals 0.135 (run 36381406751); golden retrieval with the new planner 0.606
- [x] The §9.3 Phase D gate is stated as met or not met, with no reinterpretation: **not met, 0.394 ± 0.052 (4–5 of 11)**; tech doc Implementation Status, baselines, §7 and §9.3 updated

**Dependencies:** D7
**Files:** `eval/results/phase_d.md`, `taxcite-technical-documentation.md`
**Scope:** S

---

## ✅ Checkpoint: Phase D complete
- [ ] Temporal accuracy ≥90% (10/11) on the golden temporal rows; ≤2-point regression elsewhere: **not met** (0.394 scored once; 0.152 re-scored after the refusal fix, identical retrieval); no regression elsewhere (0.602 → 0.606)
- [x] Tests and both CI gates green on the new snapshot: tests green on every `phase-d` commit; faithfulness 0.882 at refusals 0.135; retrieval gate re-baselined to route+statute1 at 0.70 (0.720 measured locally; runs in CI on the next PR touching retrieval)
- [x] Ready to plan Phase E: `phase-d` merged (PR #2, `aa9dd82`); retrieval gate 0.7200 in CI

---

# TaxCite Phase E — Task List

Plan: `tasks/plan.md` (Phase E). Test command: `uv run pytest -q`. Every task leaves the repo runnable. Approved 2026-09-28.

---

## E0: Authority spike

**Goal:** decide, before building, whether an authority prior can help (E4 go/no-go), which authority fields E2 stores, and what E3 samples. A diagnosis on golden, as D0 was; nothing is tuned here. No product code changes.

**What's already known (2026-09-28, from the database):**

| | count |
|---|---|
| Indexed chunks | statute 10,768 · regulations 5,609 · opinions 9,973 · publications 2,043 |
| Opinions | 279 memorandum (9,015 chunks) · 28 reported T.C. (958 chunks); all Tax Court, filed 2000+ |
| Temporary regulations (`section` ends in `T`) | 23 sections, 440 chunks |
| `treatments` rows | corpus: affirmed 609, reversed 52, reversed in part 37, vacated 6, overruled 1, unknown 5, … · CourtListener: none 288, affirmed 13, reversed 3, appealed 1, … (rows cover cited opinions, not only the 307 held) |

**Setup, fixed for every part:** golden, the shipped arm `route+statute1`, plans from `eval/results/decompositions-d7.json` (the live D7 planner; 5 plan sets for the 86 scored golden rows), hits from `dc.chunks(d, k)` at **k=8** (what synthesis reads) and k=20 (what the ladder scores). Authority of a hit, for this spike only, by a throwaway classifier on `Hit.source` and the citation: statute · regulation (final / temporary) · T.C. · T.C. Memo. · publication. Levels: statute = regulation > T.C. > Memo. > publication. (Whether statute outranks regulation for ranking is E4's question, not E0's.)

**Part 1: who holds the top, by authority.** Per category, mean ± sd over 5 plan sets: the authority of top-1, and the authority mix of the top 8. For each row, the gold's highest authority level and the rank of its best gold hit.
- **Definitions (per gold group, as `eval/e0_authority.py` computes them):** *inverted at top-1*: top-1 isn't gold and ranks below the row's highest-authority gold, which the pool holds. *Displaced*: the group isn't in the top k, the pool holds it, and the top k holds a non-gold hit of lower authority, the case a prior could fix (E4's ceiling, C0's reachability question). *Outranked*: in the top k, below such a hit. *Not in pool*: no prior can reach it. The pool is every sub-query's search hits before `chunks()` picks k.
- **D32's risk.** For ≥10 inversions (all of them if fewer), read the lower-authority hit that outranks gold: does it state the answer in plain English that the gold doesn't? Tally yes / no / partly, with one line each.

**Part 2: the field inventory.** For each §3.2 field (`authority_type`, `authority_level`, `court`, `jurisdiction`, `precedential_status`, `binding_on`, `publication_status`, `negative_treatment`, `source_revision`): its values in this corpus with counts, where each value comes from (a column, the citation's form, `treatments`, nothing), and whether it's constant. Two things to settle:
- **Which treatment governs an opinion** when corpus and CourtListener rows disagree, or when an opinion has several (Phase C's `generate` merge rule is the starting point; say whether it's enough for ranking).
- **Temporary regulations:** is a `T` section still in force, or superseded by a final one also in the corpus? Check the 23 by hand from eCFR's section text (a `T` regulation usually says when it expires).

**Part 3: conflict rows.** A written definition, then candidates from existing golden and dev rows (Part 1's inversions are the first place to look; Phase C's *Morehouse*/*Menard* rows and the Eleventh Circuit post-remand row are known ones). For each candidate: the controlling source, the competing lower-authority source, and why the higher one controls. Candidates on golden are *not* tuned on; they seed E1's writing.

**Decision rules, written before measuring:**
- **E4 is built** if rows inverted at top-1 or displaced at k=8 are ≥5 golden rows (mean over plan sets) *and* fewer than half of the read inversions are D32-type (the lower source is the better evidence). Otherwise E4 is dropped or narrowed to what the numbers support (e.g. a reversed-opinion demotion alone), and the gate's rerank half is reported as not applicable, with the evidence, as C0 did for graph expansion.
- **E2 stores** a field per chunk only if it has ≥2 values in the corpus; constants are documented in the tech doc.
- **E3's strata** give each varying field ≥30 of the 150 labels.

**Acceptance criteria:**
- [x] Part 1's tables (k=8 and k=20, mean ± sd over 5 plan sets) and the per-row inversion list, saved
- [x] The ceiling (inversions with gold in the pool) and the D32 tally with one line per read row
- [x] Part 2's inventory with counts and sources; the treatment-merge rule and the 23 temporary regulations settled
- [x] Part 3's definition and candidates, each with its controlling source
- [x] The decision, applied as written above: E4 go / narrowed / dropped; E2's fields; E3's strata

**Verification:**
- [x] Every number reproducible from one command (`eval/e0_authority.py`) and its output in `eval/results/phase-e-e0-authority.json`; the hand reads in `phase-e-e0-reads.txt`
- [x] You read the D32 tally and ≥3 candidate conflict rows (Checkpoint 1): E0 confirmed by you, 2026-09-28

**Done 2026-09-28** (`eval/results/phase-e-e0-authority.json`, `phase-e-e0-reads.txt`; 86 rows × 5 plan sets, 27 min, no API calls. The 11 temporal rows have one cached plan set, so they're out of the 5-set run; a 1-set run had 1 inverted and 1 displaced of 11.)

Part 1, k=8, mean ± sd over 5 plan sets:

| category (rows) | top-1: statute / reg / T.C. / Memo. / pub | inverted at top-1 | displaced | outranked | gold groups not in pool |
|---|---|---|---|---|---|
| statutory (28) | 7.0 / 4.0 / 1.0 / 5.0 / 11.0 | **11.0 ± 0** | 6.0 ± 0 | 9.0 ± 0 | 7 / 29 |
| compound (31) | 2.4 / 2.0 / 5.0 / 18.6 / 3.0 | **7.6 ± 0.55** | 8.6 ± 0.55 | 6.4 ± 0.55 | 30.4 / 63 |
| case law (26) | 1.2 / 0 / 8.8 / 16.0 / 0 | 1.0 ± 0 | 0 | 2.0 ± 0 | 7.2 / 26 |
| **all (86)** | 10.6 / 6.0 / 14.8 / 39.6 / 15.0 | **19.6 ± 0.55** | **14.6 ± 0.55** | 17.4 ± 0.55 | **45.6 / 119** |

At k=20: inverted 21.6, displaced 12.6, not in pool 38.6 / 119. The same 24 rows are inverted or displaced in all 5 plan sets (G-X04 in 3): this is structural, not planner noise.

- **The ceiling clears the bar by 4×:** ~20 rows inverted at top-1, ~15 displaced, against 5 required. Statutory and compound only; case law has nothing for a prior to do (1 row).
- **The bigger limit is reach, not order:** 45.6 of 119 gold groups aren't in the pool at k=8 (38.6 at k=20). No prior reaches them. Searching deeper than synthesis reads (search at 20, pick 8) is the lever for those, and it's G-T08's problem too.
- **D32's risk is small here:** of 15 inversions read, the lower source was **better** evidence once (G-S09: Pub 463 works the exact 40%-use case), **equal** 5 times (a memo or publication restating the statute), **partly** 2, **no** 7. One of the "no" is harmful: *Morehouse*, reversed, outranking §1402(a)(1) for an Iowa client (G-X02).

Part 2, the field inventory:

| field | values here | source | per chunk? |
|---|---|---|---|
| `authority_type` | statute 10,768 · regulation 5,609 (440 temporary) · opinion 9,973 · publication 2,043 | `source` + the citation's form | yes |
| `precedential_status` | opinions: 28 reported T.C. (958 chunks) / 279 Memo. (9,015); publications: not binding; regulations: final / temporary / **temporary, expired** | citation form; the regulation's own text | yes |
| `negative_treatment` | held opinions: none 281 · affirmed 20 · affirmed in part 1 · reversed 3 · reversed in part 1 · appealed 1 | `treatments`, merged by Phase C's `flags()` (reused as is: it already records disagreement as "unknown") | yes |
| `source_revision` | statute: release point; **regulations, opinions, publications: empty** (an FR-16 gap) | eCFR date, filing date, edition: all in `as_of` already | yes, filled by E2 |
| `authority_level` | a function of the three above | derived | stored with the profile |
| `court`, `jurisdiction` | U.S. Tax Court; federal | constant | no: documented |
| `binding_on` | depends on the taxpayer's circuit (Golsen) | a client fact | no: Phase G |
| `publication_status` | folded into `precedential_status` | — | no |

- **Temporary regulations:** §7805(e)(2) (in the corpus) sunsets a temporary regulation after 3 years, but only those issued after November 1988; the older ones (§1.274-5T, §1.280F-*T, §1.469-*T) stay in force. **Four state their own expiry, all past:** §1.988-1T and §1.988-2T whole (Dec 6, 2019); parts of §1.446-3T (May 7, 2018) and §1.482-1T (Sept 14, 2018). Expired text is indexed as if current. "A final with the same number exists" (16 of 23) is not evidence of supersession: §1.274-5 and §1.274-5T are different provisions.

Part 3, conflict rows. **Definition:** a question where a retrieved, relevant source of lower authority competes with a higher one that controls the answer: statute or regulation over a publication or opinion restating it; a reported T.C. over a memorandum; a reviewing court's rule over a reversed opinion, for a taxpayer in that circuit. Candidates (golden, not tuned on; they seed E1's dev rows):
- statute vs. publication or opinion: G-S02, G-S07, G-S11, G-S19 (lower is irrelevant); G-S06, G-S08, G-S16, G-S25 (lower restates it); **G-S09 (lower is the better evidence: the row that says "reorder, don't remove")**
- reported T.C. vs. memorandum: G-C04 (120 T.C. No. 15 vs. T.C. Memo. 2010-205)
- reversed opinion vs. the reviewing court: G-X02 (*Morehouse*, Eighth Circuit), G-X09 (*Menard*, Seventh), G-X19
- **A counter-row:** G-C03 asks how the Tax Court decided *Morehouse*; there the reversed opinion *is* the answer. The same opinion must be demoted for G-X02 and kept for G-C03. What decides is the taxpayer's circuit, a client fact.

**Decision (rules as written):**
- **E4 is built.** Inverted or displaced at k=8: ~20 and ~15 rows (≥5 required); D32-type 1 of 15 (< half).
- **E4's candidates change:** a blanket reversed-opinion demotion is **dropped** (G-C03 vs. G-X02: it needs `binding_on`, Phase G); **added:** search deeper than synthesis reads (pool at 20, pick 8), for the 45.6 gold groups out of reach. Expired temporary-regulation text is demoted (or dropped from the index: E2 decides, 4 sections).
- **E2 stores:** `authority_type`, `precedential_status`, `negative_treatment`, `source_revision` (filled for every source), and the derived `authority_level`. `court` and `jurisdiction` documented as constants; `binding_on` deferred.
- **E3's strata (150):** statute 20 · final regulation 20 · temporary regulation 20 (all 4 expired sections in) · reported T.C. 30 · Memo. 30 · publication 15 · opinions with a non-"none" treatment 15 (reversed, reversed in part, appealed, affirmed). Each varying field gets ≥30 labels.

**Dependencies:** none
**Files:** `eval/e0_authority.py` (new, given in chat; a 1-plan-set run verified 2026-09-28: 5.4 min), `eval/results/phase-e-e0-*` (no product code)
**Scope:** S

---

## E1: Authority-conflict rows

**Goal:** the rows E4 is tuned and gated on. Each one names the source that should be top-1 (`controls`) and the lower source competing with it. Dev for tuning, a golden subset held out and scored once, in E4.

**What exists already (E0, and a 1-plan-set dev run: `phase-e-e0-authority-dev.json`, old planner cache):**
- **Golden:** 24 rows inverted or displaced at k=8 in all 5 plan sets. 15 read in E0 (`phase-e-e0-reads.txt`); 9 unread: G-X04, X05, X07, X13, X15, X17, X22, X27, X29.
- **Dev:** 9 inverted rows, all statute or regulation vs. a publication or memo: D08, D14, D16, D18, D19, D21, D23, D26, D27 (`phase-e-e0-reads-dev.txt`, unread). 7 rows already have the controlling source at top-1: D13, D20, D30, D31, D34, D36, D37.
- **Thin kinds:** reported T.C. vs. memo has one golden row (G-C04) and none on dev. Reversed opinions: golden has *Morehouse* (G-C03, G-X02) and *Menard* (G-X09); dev has none. The held opinions with a negative treatment not used by golden: **137 T.C. No. 17** (reversed, 8th Cir. 2013) and **T.C. Memo. 2002-5** (reversed in part, 9th Cir. 2003). 18 of the 28 reported T.C. opinions are unused by golden.

**Changed from the plan's default (for you to confirm):** the golden subset is mostly **existing rows, tagged**, plus new rows only where a kind is thin. The default ("new golden rows") assumed 3–5 existing candidates; E0 found 24. Tagging them is legitimate because E0 only diagnosed them and nothing was tuned on them. **The caveat, stated in E4's report:** they were selected *because* they fail today, so the subset measures gain. The guard rows measure harm.

**The row tag** (added to existing rows, no other field changed; new rows are full rows with `scored_from: "E"`, so the CI gate and every earlier ladder stay unchanged):

```json
"authority": {"kind": "statute_over_lower", "controls": ["26 U.S.C. § 280A(c)(1)"],
              "competes": ["IRS Pub 587 (2025), p. 5#body#4"], "keep": []}
```

- `kind`:
  - `statute_over_lower`: statute or regulation over a publication or opinion
  - `reported_over_memo`: a reported T.C. over a T.C. Memo.
  - `reviewing_court`: a reversed opinion vs. the reviewing court's rule, where the question states the taxpayer's circuit
  - `guard`: the controlling source is already top-1, and E4 must not break it
- `controls`: citations or chunk keys, drawn from the row's gold. Any one at top-1 passes. Where the reviewing court's opinion isn't in the corpus (G-X02's Eighth Circuit), `controls` is the statute, and the circuit's rule reaches the answer only through Phase C's flag.
- `competes`: the lower source or sources seen competing (from E0's runs, or expected for new rows).
- `keep`: sources that must stay in the top 8 because they are better or unique evidence (G-S09's Pub 463). Empty for most rows.

**Target composition:**

| kind | golden (held out) | dev (tuning) |
|---|---|---|
| `statute_over_lower` | the E0 rows that hold up on reading (≈12–15) | the 9 inverted dev rows that hold up, and new rows if fewer than 6 survive |
| `reported_over_memo` | G-C04 + **2 new** | **3 new** (unused T.C. opinions with a memo on the same issue) |
| `reviewing_court` | G-X02, G-X09 (and G-X19 if its reading holds) | **2 new**: 137 T.C. No. 17 for an Eighth Circuit client, T.C. Memo. 2002-5 for a Ninth |
| `guard` | ≥4, incl. **G-C03** (the reversed opinion *is* the answer) and ≥1 with a `keep` source | ≥4 from D13, D20, D30, D31, D34, D36, D37, **plus a counter-pair row**: how the Tax Court decided 137 T.C. No. 17 |
| rows with a `keep` source | G-S09 and any found by reading | ≥2 (found in the dev reads, or new) |

**Method (D1's two scans):**
1. **Read before tagging.** Read the 9 unread golden inversions and the 9 dev inversions, the same way as E0: is the lower source better, equal, partial, or no? `controls` must be the source a practitioner would cite for the answer, not just the higher-level gold. A row whose "conflict" doesn't hold up (the top-1 is also gold, or the question really is about the publication) isn't tagged.
2. **Write the new rows from the ingested text.** For `reported_over_memo`, find a memo that restates or applies the reported opinion's rule, and ask the question in the memo's words. For `reviewing_court`, state the taxpayer's circuit in the question. The reference answer gives the circuit's rule and names the reversed holding.
3. **Scan 1, per row:** every `controls` and `competes` chunk read in full. The answer checked against the text, not memory. `controls` ⊆ gold.
4. **Scan 2, across sets:** no citation shared between golden and dev (checked against pilot too). Every kind is present on dev. Gold widened where a publication states the same rule, because a publication can be gold without being the controlling source.

**Acceptance criteria:**
- [x] Composition as the table above (or the shortfall stated per kind, with the reason): golden 24 + 8, dev 10 + 8; shortfalls in reported-over-memo and dev reviewing-court stated with reasons
- [x] `validate_pilot.py` passes both sets (0/116, 0/42), and it now also checks `authority`: every `controls` entry is in the row's gold, and every `controls`, `competes` and `keep` entry exists in the corpus
- [x] Each tagged row records whether a `controls` source is in the pool at k=20 on a live-planner plan (`auth_in_pool` in E4's baseline, 5 live-planner plan sets, k=8 and k=20). Out-of-reach rows are kept, and counted separately in E4 (they're what deeper search is for)
- [x] No citation shared between sets; golden edits in logged commits you review (`598f338`, `31b195e`, `570b113`; G-C27's untag in `0edc64f`)

**Verification:**
- [x] Manual: you approve every row (Checkpoint 1), including the tags on existing golden rows (approved 2026-09-28)

**Progress 2026-09-28: the 18 unread cases are read; 23 golden + 9 dev tags approved and applied, and D14's answer fixed (approved).** Only the `authority` field changed on tagged rows (and `answer` on D14), checked against HEAD; validator 0/115 and 0/39; 219 tests pass.
- **Verdicts** (in `phase-e-e0-reads.txt` and `phase-e-e0-reads-dev.txt`):
  - golden, 9 new: equal 3, partly 2, no 3, not a conflict 1 (G-X04: top-1 is never below the statute's level)
  - dev, 9: better 1 (D08), equal 1, partly 2, no 5
  - both sets, all 33 read so far: the lower source was the better evidence twice (G-S09, D08), and both become `keep` sources
- **`at: 8` added to the tag.** Three golden compound rows (G-X07, G-X17, G-X27) have an on-point gold opinion at top-1 in 5 of 5 plan sets, and G-S08's top-1 is a regulation at the statute's level. Pushing the statute above an on-point opinion isn't the goal; getting it into the top 8 is. G-X02 stays `at: 1`: its top-1 is the reversed *Morehouse*.
- **Proposed tags, 23 golden + 9 dev** (all `statute_over_lower` unless noted):
  - golden, `at: 1`: G-S02, S04, S06, S07, S09 (keep Pub 463 p. 31), S10, S11, S15, S16, S19, S25, G-X03, X05, X13, X15, X22, X29, G-C04 (`reported_over_memo`), G-X02 (`reviewing_court`)
  - golden, `at: 8`: G-S08, G-X07, X17, X27
  - dev: D08 (keep Pub 527 p. 20), D14, D16, D18, D19, D21, D23, D26, D27
  - Tested on copies: the validator passes both (0 of 115, 0 of 39) and flags every class of bad tag.
- **A data bug:** D14's reference answer starts ",500 of interest" where "$2,500" was lost (shell interpolation of `$2` at authoring, most likely). No other row in golden, dev or pilot has the pattern. Fixed: "$2,500" restored. No code reads reference answers for retrieval, so no score moves.
- **Guards and reads done (2026-09-28, uncommitted for your diff review):**
  - **Guard candidates:** rows whose top-1 is gold in 5 of 5 plan sets (golden 19, dev 16). **Most are exposed:** a gold opinion or publication leads, and a non-gold statute or regulation also sits in the top 8. In golden, 13 of 19: 6 of 7 case-law and 7 of 8 compound are like this; in dev, D24's gold publication is. The competing sources are mostly irrelevant statutes (§408(m), §420(f)(7), §453B(e)(2), §7471) that a flat "statute beats opinion" prior would promote to top-1. D03's is a reversed reported opinion on another topic (*Morehouse*), which a "reported beats memo" prior would put above the gold memo.
  - **Tagged `guard`** (`controls` = all gold; `competes` = the higher-authority non-gold hits in the top 8, plan set 0):
    - golden: G-C03 (the reversed opinion *is* the answer), G-C08, G-C12, G-C17, G-C20, G-X10, G-X28 (exposed), G-S13 (statute leads, the control)
    - dev: D02, D03, D05, D10, D24 (exposed), D13, D34 (statute leads)
  - **G-X09 tagged `reviewing_court`:** a non-gold page of the reversed *Menard* leads with the disguised-dividend reasoning the Seventh Circuit rejected; §162(a)-(b) isn't in the pool at k=8.
  - **G-X19 not tagged:** its top-1, T.C. Memo. 2025-50 at *5, applies the Eleventh Circuit's rule under *Golsen* (*Kroner*): same level as the gold, and correct. It's a `binding_on` row (Phase G), not a level conflict.
  - Validator 0/115, 0/39.
- **What the guards change for E4:** a flat per-level prior is now expected to fail its own guards. The prior has to be scoped: applied among the candidates of a statutory sub-query (routing already types them), or as a margin tie-break, not across the whole merged list. E4's candidates (a)–(c) are measured with that scoping as well as without, and the guard rows are scored alongside the conflict rows.
- **New rows drafted (2026-09-28, `reviewed: false`, `scored_from: "E"`, uncommitted, awaiting your approval):**
  - **Only 4 reported opinions have a memo in the corpus that restates them** (searched by case name; the citations table misses volume/page cites): *Knudsen* 131 T.C. No. 11 (13 memos), *Smalley* 116 T.C. No. 29 (3), *Garnett* 132 T.C. No. 19 (2), *Treece* 158 T.C. No. 6 (1, its own merits memo). All four were drafted from the opinions' text.
  - **Measured before tagging** (case-corpus search of the question, reranked, top 8, no planner): the reported opinion already leads for *Garnett* and *Smalley*, and a non-gold page of *Treece* itself leads for *Treece*. Only *Knudsen* is a real conflict: three memos citing it hold the top 3, and it isn't in the top 8.
  - **Applied:** G-C27 (*Garnett*, `guard`), D40 (*Knudsen*, `reported_over_memo`), D41 (*Smalley*, `guard`), D42 (*Treece*, untagged: same opinion, same level, not an authority conflict; kept as a case-law row). Validator 0/116, 0/42; no gold shared golden/dev; 219 tests.
  - **Shortfalls, with reasons:**
    - `reported_over_memo`: golden has 1 (G-C04), dev has 1 (D40), against 3 each planned. **The kind is rare, not under-sampled:** a reported opinion usually states its own holding better than the memos citing it, and the cross-encoder already prefers it (3 of the 4 checked). The conflict appears when the reported opinion is out of reach (D40) or outranked by a memo on the same facts (G-C04).
    - `reviewing_court` on dev: 0 of 2. The two reversed held opinions golden doesn't use can't be grounded. *Thompson* (137 T.C. No. 17, 8th Cir. 2013): no text in the corpus says what the circuit held. *Banaitis* (T.C. Memo. 2002-5), flagged "reversed in part" (9th Cir. 2003): the Supreme Court reversed the Ninth Circuit in *Commissioner v. Banks*, 543 U.S. 426 (2005), and T.C. Memo. 2025-80 at *11 states the Tax Court's rule from *Banks*. **So Phase C's flag points the wrong way:** the reversal was itself reversed. That's a finding for E3's treatment labels (a treatment chain two levels deep) and Phase H. Golden's G-X02 and G-X09 cover the kind; E4 reports them, and nothing is tuned on it because the blanket demotion was dropped.
    - Dev counter-pair guard: not written (it depended on *Thompson*). G-C03 covers it on golden; dev D03's threat is a reversed opinion, which covers the dev side of the same risk.
- **E1 totals:** golden 24 conflict rows (21 `statute_over_lower`, 1 `reported_over_memo`, 2 `reviewing_court`) + 9 guards; dev 10 conflict rows (9 `statute_over_lower`, 1 `reported_over_memo`) + 8 guards.

**Out of scope:** the expired temporary regulations (§1.988-1T/-2T are foreign currency, outside the Phase B topics; E2 handles them as metadata, not rows); E4's baseline top-1 on these rows (E4's first step, with 5 live-planner plan sets for every tagged row, dev included: dev's B rows have no D7 plans yet, ~$0.05).

**Dependencies:** E0
**Files:** `eval/dev.jsonl`, `eval/golden.jsonl`, `eval/validate_pilot.py`
**Scope:** M

---

## ✅ Checkpoint 1 (human review)
- [x] E0's field list, the conflict-row definition and the go/no-go on E4 confirmed (2026-09-28)
- [x] E1's rows approved (2026-09-28)

---

## E2: Authority profile at ingestion

**Goal:** every chunk carries an authority profile from structured fields only (ADR-13), stored in Postgres and on the Qdrant point, so E4's ranker, E3's hand check and E5's labels all read one value. No re-embedding.

**Three design changes from the plan, found reading the code (for you to confirm):**
1. **The profile goes into the Qdrant payload after all.** The plan said "not in the payload, the reranker runs on `Hit`s". But a `Hit` is built from the payload (`retrieve.search`), as D4's `effective` and D3's `edition` are. Reading Postgres per query instead would add a database round-trip to the hot path. So: payload, as `effective` did.
2. **`negative_treatment` isn't copied onto chunks.** It changes (a pending appeal is decided; Phase H refreshes it), and `ingest.citations.flags()` already reads it live, per opinion, for every answer (Phase C). A copy on 9,973 chunks would go stale and need its own refresh. E4 doesn't rank on it (the blanket demotion was dropped), and E5 labels answers from `flags()` as today. E3 checks treatment labels through `flags()`, the same function answers use.
3. **Wholly expired temporary regulations are excluded, not demoted.** §1.988-1T and §1.988-2T say "the applicability of this section expires on December 6, 2019". They get the existing `excluded` mechanism with a new reason, `expired`, so the next sync removes them from Qdrant, and D6's trigger keeps their text in `chunk_versions`. That's 4 chunks. The two *partly* expired sections (§1.446-3T, §1.482-1T: named paragraphs expired in 2018) stay indexed, labelled `temporary_partly_expired`. Mapping each expiry to its paragraphs isn't worth it for 2 sections outside the Phase B topics.

**The profile** (jsonb column `authority` on `chunks`; the same dict under `authority` in the payload; `Hit.authority`):

```json
{"type": "opinion", "status": "memorandum", "level": 2}
```

| `type` | `status` | `level` | from |
|---|---|---|---|
| `statute` | `enacted` | 4 | `source == "usc"` |
| `regulation` | `final` | 4 | `source == "ecfr"`, section without a `T` suffix |
| `regulation` | `temporary` | 4 | `T` suffix (pre-1988 temporary regulations stay in force; §7805(e)(2)'s 3-year limit doesn't reach them) |
| `regulation` | `temporary_partly_expired` | 4 | `T` suffix and the text says some paragraphs' applicability "expires" on a past date |
| `opinion` | `reported` | 3 | `source == "case"`, citation matches `\d+ T.C. No. \d+` |
| `opinion` | `memorandum` | 2 | citation matches `T.C. Memo. \d{4}-\d+` |
| `publication` | `not_binding` | 1 | `source == "irs_pub"` |
| `unknown` | `unknown` | 0 | anything else: counted and printed, never defaulted (FR-16) |

- Statute and regulation share level 4 on purpose. Which outranks the other for ranking is E4's question, answered on dev, not baked in here.
- `court` ("U.S. Tax Court") and `jurisdiction` ("federal") are constants in this corpus: documented in the tech doc (§3.2, §5.5), not stored. `binding_on` waits for Phase G.

**`source_revision` for every source (the FR-16 gap E0 found):** each ingester sets it from what it already knows. `ecfr`: `"eCFR 2026-09-17"` (the snapshot date); `irs_pub`: `"2025 edition"`; `case`: `"filed 2019-03-04"`; `usc`: unchanged (`"Pub. L. 119-110"`). The backfill fills the existing rows the same way.

**Where it's computed:** one function, `authority(chunk)`, called in `store.save()`, the one write path every ingester already goes through. It's a pure function of `source`, `citation`, `section` and `text`, so the backfill is the same function over existing rows.

**Backfill** (one CLI command, idempotent, no re-embed):
- Postgres: `UPDATE chunks SET authority = …, source_revision = …` per key, batched.
- Qdrant: `set_payload` grouped by distinct profile (about 8 values), so it's a few calls, not 28,000.
- Expired sections: `excluded = 'expired'`, and those points are deleted from Qdrant.
- It prints the count per `type`/`status`, the `unknown` count, and the expired keys.

**Acceptance criteria:**
- [x] Every indexed chunk has a profile, and `unknown` is 0 or each case is explained
- [x] Counts match E0's inventory: statute 10,768; regulations 5,609 (440 temporary, 4 excluded as expired); opinions 9,973 (958 reported, 9,015 memo); publications 2,043
- [x] Re-running the backfill changes nothing, and D6's trigger records no text versions for it (only `authority` and `source_revision` change, not `text`)
- [x] `index.sync` writes `authority` into the payload for new points; `Hit.authority` is filled on search
- [x] Snapshot round-trip on a throwaway database: dump, restore, and `authority` survives (D6's restore lesson)

**Verification:**
- [x] Tests: `authority()` on one fixture chunk per row of the table above, including an unknown; the payload carries `authority` into `Hit` (in-memory Qdrant, as D3's edition test does); the backfill is idempotent
- [x] `uv run pytest -q` passes; the CI retrieval gate is unchanged (no ranking change in E2)

**Built 2026-09-28.**
- **Code:**
  - `chunk.authority()`, `chunk.revision()` and `chunk.expiry()` live in `chunk.py`, the module every ingester and the store already share.
  - `store.save()` computes the profile and the default revision for every write, so no ingester changed; that's lazier than editing three ingesters, with the same result.
  - The eCFR parser excludes a section its own clause ended, dated against the snapshot, not today.
  - `index.sync` writes the payload, `Hit.authority` reads it, and `taxcite authority` runs the backfill.
- **Backfill:** 28,747 rows read, 28,743 updated, 28,389 points given a profile, in about 5 s with no re-embedding. Expired sections §1.988-1T and -2T (4 chunks) were re-saved as `expired` through `store.save`, so their keys changed as a re-ingest's would. The old points were deleted, and D6's trigger kept the 4 old versions. It recorded nothing for the metadata-only updates.
- **Counts, all as E0 predicted:**
  - statute: 10,768
  - regulations: 5,169 final, 413 temporary, 23 temporary_partly_expired (5,605 = 5,609 − 4 expired)
  - opinions: 958 reported, 9,015 memorandum
  - publications: 2,043
  - **unknown: 0**
  - `source_revision` null: 0 in every source
- **Checks:**
  - A second run updates 0 rows.
  - Snapshot round-trip on a throwaway database (created from `template0`: the local `template1` has a collation-version mismatch, left alone): 28,747 rows, all with profile and revision.
  - CI retrieval gate unchanged: 0.7200.
  - 234 tests (15 new, in `test_store.py`, `test_ecfr.py` and `test_index.py`).
- **For E4:** CI restores `corpus-2026-09-28`, which predates E2, so its rows have no profile. The first PR that ranks on authority needs a new snapshot published (your call, as before).

**Dependencies:** E0
**Files:** `src/taxcite/store.py` (column, `authority()`, save), `src/taxcite/index.py` (payload), `src/taxcite/retrieve.py` (`Hit.authority`), `src/taxcite/ingest/{ecfr,caselaw,irs_pubs}.py` (`source_revision`), `src/taxcite/cli.py` (the backfill command), `tests/`
**Scope:** M

---

## E3: Stratified 150-chunk hand check

**Description:** §3.2's validation, made meaningful. Draw 150 chunks stratified by E0's strata, weighted to the fields that vary (opinions by T.C./Memo. and treatment, regulations by final/temporary), not uniformly. Label each field by hand against the source of truth (the opinion's caption, eCFR's section status, the treatment record). Report accuracy per field and overall. D4's rule: if it fails and gets fixed, re-check on a **fresh** sample, never the one it was fixed against.

**Acceptance criteria:**
- [x] ≥95% field-level accuracy overall **and** per varying field, or stated as not met: **not met** (overall 97.4%; regulation status 77.5%, treatment 86.7%)
- [x] The sample, labels and disagreements saved (`eval/results/phase-e-handcheck-authority.txt`)

**Verification:**
- [x] Manual: you spot-check ≥10 labels (done 2026-09-28)

**Sample drawn 2026-09-28** (`eval/e3_sample.py`, seed 20260928; `phase-e-e3-sample.json`, and `phase-e-handcheck-authority.txt` to label):
- **Strata:**

  | stratum | rows | how drawn |
  |---|---|---|
  | statute | 20 | random |
  | final regulation | 20 | random |
  | temporary regulation | 20 | all 4 expired + 4 partly expired + 12 random |
  | reported opinion | 30 | all 28 reported opinions, one chunk each, + 2 |
  | memorandum opinion | 30 | 30 distinct opinions |
  | publication | 15 | random |
  | treatment | 15 | 15 distinct opinions: every held opinion with an adverse or pending record (6), + 9 affirmed |

  Opinion labels belong to the opinion, so those strata take one chunk per opinion.
- **Evidence per row (the source of truth):**
  - regulations: the eCFR heading ("(temporary)") and any expiry clause
  - opinions: the opinion's own text (its citation form and "Filed <date>" line), plus DAWSON's record (`documentType`/`eventCode`, `filingDate`)
  - treatment: the `flags()` record
- **What the evidence showed while drawing:**
  - **20 of 75 sampled opinions lost their caption in PDF extraction** (the text starts after it). Their filing date can only be checked against DAWSON's record, which is where `as_of` came from, so it's circular. Those rows are marked and reported separately, not counted as independent passes.
  - **DAWSON's `documentType` disagrees with our label once in all 307 opinions:** T.C. Memo. 2012-59 is coded "T.C. Opinion" (TCOP) but titled "T.C. Memo. 2012-59". The citation is right; it's in the sample.
  - **Treatment has two known problems in the sample.** *Banaitis* (T.C. Memo. 2002-5) is "reversed in part", but the Supreme Court reversed that reversal (E1). *Gregory* (T.C. Memo. 2021-115) is "appealed; the outcome could not be read", but golden G-C01's notes record it as affirmed by the Eleventh Circuit in 2023. The field may not reach 95% on 15 rows; if so, it's reported, not re-drawn.

**Labelled 2026-09-28 (all 150; tally at the top of `phase-e-handcheck-authority.txt`). Gate NOT MET.**

| field | correct | where it fails |
|---|---|---|
| type | 150/150 | — |
| status | 141/150 (94.0%); **regulations 31/40 (77.5%)**, temporary stratum 11/20 | 9 temporary-regulation rows |
| source_revision | 149/150 | 1 opinion (below); 20 opinion dates checkable only against DAWSON (circular), reported separately |
| treatment | **13/15 (86.7%)** | *Banaitis*, *Gregory* |
| all fields | 453/465 (97.4%) | |

**What's wrong, and why:**
1. **§7805(e)(2) sunsets temporary regulations; E2 only read their own expiry clauses.** A temporary regulation issued after Nov. 20, 1988 expires within 3 years whatever its text says. The issuing Treasury Decision's date is in every section's source note (`cita`). Five sections are affected beyond §1.988-1T/-2T:
   - **§1.469-4T** (May 1989, 126 chunks, superseded by final §1.469-4, which is also in the corpus; passive-activity grouping is a core topic)
   - §1.446-3T and §1.482-1T (2015, 23 chunks, labelled "partly expired": in fact wholly expired)
   - §1.167(a)-13T (1994, 1 chunk) and §1.704-1T (2016, 1 cross-reference stub)

   The 16 sections issued before the cutoff (1984–July 1988) stay in force, and were labelled right.
2. **Treatment:**
   - *Gregory* reads "appealed" though CourtListener's record names a decided appellate opinion (69 F.4th 762, affirmed); `flags()` treats a decision whose outcome it can't parse as pending.
   - *Banaitis* reads "reversed in part", but the Supreme Court reversed that reversal (*Banks*, 2005). Treatment is tracked one appeal deep.
3. **One corrected reissue:** DAWSON lists *Estate of Caan* (161 T.C. No. 6) by its corrected version's date (Nov. 14, 2023); the opinion says "Filed October 18, 2023". It's the only "(Corrected)" title among the 307.

**Fixes (all four approved 2026-09-28 and applied), then a re-check on a fresh sample (D4's rule):**
- (a) `chunk.expiry` also applies §7805(e)(2): a temporary regulation whose first Treasury Decision in `cita` postdates Nov. 20, 1988 and is more than 3 years before the snapshot is `expired`, excluded like §1.988-1T. That's about 151 more chunks out of the index, including all of §1.469-4T. `temporary_partly_expired` then disappears: both sections it described are wholly expired. The alternative, keeping §1.469-4T with a valid-time window for pre-1992 years, is a Phase D mechanism no row needs.
- (b) `flags()`: an appeal with a decided appellate citation and an unparsed outcome reads "decided; outcome not read", not "appealed" (pending). That fixes the *Gregory* class in code.
- (c) *Banaitis*: one hand-entered treatment row (source `manual`, citing *Banks* and T.C. Memo. 2025-80 at *11), or leave it as a documented limitation. It's the only two-level chain known; finding others needs the Phase H refresh.
- (d) *Caan*: when DAWSON's title says "(Corrected)", take the filing date from the opinion's own "Filed" line. One opinion.

**Applied 2026-09-28:**
- (a) `chunk.sunset()` reads the issue date from `cita`. The eCFR parser and the backfill exclude sunsetted sections. **151 chunks left the index** (§1.469-4T 126, §1.482-1T 14, §1.446-3T 9, §1.167(a)-13T 1, §1.704-1T 1); `temporary_partly_expired` is gone. Temporary regulations in force: 285 (all issued 1984–July 1988).
- (b) `flags()`: an appeal CourtListener found but couldn't read is `decided` ("Decided on appeal …; the outcome could not be read"), not `appealed`. *Gregory* now reads so. Old `appealed` rows are read the same way.
- (c) `citations.MANUAL`: a hand-checked record overrides the automated sources. *Banaitis* is `upheld` with *Banks* and its evidence in the note. `load()` writes it on every rebuild.
- (d) The case-law parser takes a corrected reissue's filing date from the opinion's own line. *Caan*'s 55 chunks were re-saved: filed 2023-10-18, "corrected 2023-11-14" in `source_revision`, payload moved, no text versions recorded.
- 10 tests (244 pass).

**Re-check on a fresh sample** (`e3_sample.py --seed 20260929 --exclude` the first; `phase-e-handcheck-authority-20260929.txt`): 146 rows, no chunk from the first sample, no opinion reused in the memo or treatment strata.

| field | correct |
|---|---|
| type | 146/146 |
| status | 146/146 (regulations 40/40; temporary 20/20: 4 expired §1.469-4T, 16 in force) |
| source_revision | 146/146 (17 opinion dates checkable only against DAWSON, reported as circular) |
| treatment | 11/11, affirmances only |

- **Gate: met on the fresh sample, with one caveat.** Every adverse or pending opinion (6) was in the first sample, so no fresh draw can re-test them. The *Banaitis* and *Gregory* fixes are verified by their tests and records, not by the re-check. The first sample's 86.7% stands as that field's measured accuracy before the fix.
- Why only 146: the treatment stratum ran out of fresh opinions (11 affirmed ones were left).

**Validation in two scans (2026-09-28, at your request).**

*Scan 1, row by row, against evidence independent of what produced each label; a census wherever the population is small:*
- **Treatment, census of all 26 opinions with a record** (every row both samples graded, plus the rest), each checked against the appellate opinion's own text in the Phase C cache, or the later Tax Court opinion that says "aff'd":
  - All consistent, including *Visco* (the text ends "We will affirm"; its "reversed" is a footnote about the IRS).
  - Three gaps. *Western Management* is "AFFIRMED in part; REMANDED in part", but the vocabulary has no remand: "affirmed in part" is true, not whole. 119 T.C. No. 5's label drops its circuit (the source reads "93 Fed. Appx. 473 (3d Cir. 2004)"). T.C. Memo. 2007-166's two sources disagree on the page (86 vs 869; the flag shows the right one).
  - *Gregory*'s cached appellate text never states its own disposition. "Affirmed" rests on golden G-C01's notes, written from memory; "decided, outcome not read" is what the evidence supports.
- **Opinion filing dates, census of all 307:** 217 agree with the opinion's own Filed line and 87 have none.
  - **3 disagreed: a miss in fix (d).** DAWSON also writes "CORRECTED Opinion" and "(CORRECTED)", and the parser matched only "(Corrected)". So did my count of corrected reissues, which was case-sensitive.
  - T.C. Memo. 2024-3, 2025-97 and 2026-29 were dated by their correction, 3–4 months late. None was in either sample.
  - Fixed (case-insensitive match, test extended) and re-saved (407 chunks). No UTC/Eastern date shift exists among the 307.
- **Opinion type, census of all 307** (DAWSON document type vs citation form): 1 disagreement, DAWSON's own miscode (T.C. Memo. 2012-59).
- **Temporary regulations, census of all 23 sections** by issue date: the 7 excluded and 16 in force are all right under §7805(e)(2).
- **One of my labels was wrong:** first-sample row 54 (§1.704-1T, 2016) was graded "ok" as a harmless stub, inconsistent with the rule applied to rows 45–53. Now WRONG: first-sample status 140/150, regulations 30/40 (75.0%).

*Scan 2, the procedure and what no stratum could see:*
- ~~**The fixes changed retrieval.** The CI retrieval gate fell 0.7200 → 0.7000 (D11).~~ **Corrected in E4 (2026-09-28): the 0.7000 wasn't the exclusions.** The same code and data read 0.7200 an hour later (`retrieval-dev-2026-09-28-k10-approx-now.json`). Dense search was approximate (HNSW), and its results changed as Qdrant re-optimised the collection after E3's deletions and payload writes. Exact search reads 0.7200 too (`…-k10-exact.json`). The D14/D19/D33 rank shifts from the same session carry the same doubt. What held: no gold or tag points at an excluded chunk, and Postgres and Qdrant agree.
- **No gold or tag points at an excluded chunk** (golden, dev, pilot: validator 0 issues). Postgres and Qdrant agree (28,238), and the history table holds exactly the 155 expired versions.
- **Superseded *final* regulations ("A" suffix) carry the §1.469-4T risk without a sunset:** §1.274-5A (29 chunks, travel substantiation, a core topic), §1.482-1A/-2A/-7A (92) and §1.1402(e)-1A–5A (15). Their scope isn't stated anywhere in the corpus. "Final" is the right label; the ranking risk is open (a decision for you, below).
- **Temporary sections amended after 1988** (§1.274-5T, §1.62-1T, §1.469-1T/-2T/-5T, §1.162-25T, §1.280F-*T): an amendment issued as a temporary rule may have sunset paragraph by paragraph. The corpus can't say which amendments were temporary. **Unresolved,** labelled in force at section level.
- **What the samples can't measure:**
  - "none" treatments (281 opinions) could hide missed appeals; CourtListener's coverage gap is known from Phase C.
  - 87 opinions (28%) carry no Filed line, so their date rests on DAWSON. A corrected reissue whose title doesn't say so would be invisible.
- **Effective sample sizes:** opinion-level fields repeat across chunks. Reported status is really 28 opinions, re-drawn as fresh chunks; the censuses above are the stronger evidence.
- **Cosmetic:** the 23 excluded §1.446-3T/§1.482-1T rows still store `temporary_partly_expired` (unindexed, never read).
- **Standing risks:**
  - The hand-checked *Banaitis* row never goes stale (the Supreme Court's word is final).
  - The grader who designed the fixes also graded the re-check. The censuses reduce that dependence; your spot-check is still owed.

**Decisions (yours, 2026-09-28):**
1. **The "A" sections are labelled `final_prior_version`** (level 4, like every regulation), so E4 can weigh them. That's 136 chunks: §1.274-5A 29, §1.482-1A/-2A/-7A 92, §1.1402(e)-1A–5A 15. My validation notes said 142, which was an arithmetic slip. Applied through `chunk.authority()` and the backfill: 136 rows updated, a second run updates 0. Tested, including "1.263A-1", where the "A" sits inside the section number (246 tests).
2. **The CI gate stays at 0.70.** Labelling is metadata only, so ranking is unchanged at 0.7000. E4 re-baselines on this corpus and a new snapshot.

**Dependencies:** E2
**Files:** `eval/results/`
**Scope:** S

---

## E4: Authority-weighted rerank

**Goal:** make the controlling source win where a lower one outranks it (E1's conflict rows) without breaking the rows that are right today (E1's guards) or costing more than 2 points of Recall@20 in any category (§9.3). Chosen on dev, golden scored once.

**What the code and the corpus fix before any design (2026-09-28):**
- **Routing makes sources disjoint by sub-query kind.** A statutory sub-query searches `usc`/`ecfr`/`irs_pub`; a case-law sub-query searches `case` only. So the statute-over-opinion harm E1's guards show is purely *across* sub-query kinds. "Scoped" can be defined exactly: reorder within one kind's candidates, and leave the cross-kind ordering to the cross-encoder.
- **The cross-encoder's scale:** top-1 score median 0.80 (range −0.46…2.47), adjacent-rank gap in the top 8 median 0.13, 90th percentile 0.53 (golden, 40 rows, plan set 0). A prior's weight is sized against those gaps.
- **Where the order is decided:** `decompose.chunks()`. It takes one floor slot per sub-query, then D3b's statute slot, then fills by cross-encoder score, and **sorts the chosen 8 by score**. Top-1 is the highest score among the chosen, so a candidate changes top-1 only through the score it sorts by.
- **E0's numbers describe the pre-E3 corpus.** E3 removed 155 chunks, and the CI gate moved 0.7200 → 0.7000. The baseline is re-measured here.

**Step 0: plans and the baseline (no code change to ranking).**
- **Plan sets from the live (D7) planner, into `decompositions-d7.json`:**
  - 5 sets for every dev row (dev's B rows only have old-planner plans)
  - 4 more for the 11 temporal golden rows
  - 5 for the rows E1 added (G-C27, D40–D42)
  - About 260 gpt-4o-mini calls, under $0.15. Appended, so the existing plan sets don't change.
- **Authority metrics in `eval/retrieval.py`,** read from each row's `authority` tag:
  - conflict rows: `controls` at target (top-1 for `at: 1`, top 8 for `at: 8`), and whether `controls` is in the pool at all
  - guards: still at top-1
  - `keep` sources: still in the top 8
  - Reported per kind, mean ± sd over 5 plan sets. Plus Recall@20 and Recall@8 per category over all scored rows, regulation recall (Phase A's 12.4 points), G-T08's statute rank, and latency.
- **Baseline on dev and golden,** shipped arm (`route+statute1`), k=8 and k=20. Golden is measured here only as the "before" of a pre-registered comparison; nothing is tuned on it.

**Step 0 done (2026-09-28).**
- **Plans:** 241 new live-planner plans in `decompositions-d7.json` (5 min, $0.047); every scored dev and golden row now has 5 sets, and the existing sets are unchanged (byte-compared).
- **Code:** `eval/retrieval.py` gets `authority_facts()` (tested in `test_metrics.py`), per-category recall as mean ± sd over plan sets, an authority summary, and `--tag`, so same-day arms stop overwriting each other.
- **Results:** `retrieval-{dev,golden}-2026-09-28-k{8,20}-e4-baseline.json`, arm `route+statute1`, scored rows B + D + E.

| | dev k=8 | dev k=20 | golden k=8 | golden k=20 |
|---|---|---|---|---|
| Recall, all scored rows | 0.590 | 0.700 | 0.493 | 0.580 |
| Recall, original B rows (comparable to Phase D) | 0.608 | 0.748 | 0.515 | **0.606** (Phase D: 0.606) |
| conflict rows at target | **0 / 10** | 0 / 10 | **0 / 24** | 1 / 24 |
| conflict rows in the pool | 9 / 10 (not D40) | 9 / 10 | 23 / 24 (not G-X09) | 23 / 24 |
| guards still leading | 8 / 8 | 8 / 8 | **8 / 9** (not G-C27) | 8 / 9 |
| `keep` sources in the top 8 | 1 / 1 | 1 / 1 | 1 / 1 | 1 / 1 |

- **Every conflict row fails today at k=8,** as E1 selected them. Where the controlling source is in the top 8 it is 2nd–8th: G-S10 and G-S25 at 2, D18 at 2. Most golden statute rows have it outside the top 8 entirely, 14 of 24.
- **The planner's variance barely reaches retrieval:** sd is 0 in most categories (0.034 dev statutory, 0.017 golden case law). The search text is the question itself, and the plans differ mainly in routing, which rarely changes. So five plan sets cost little and resolve little; they stay for the gate as pre-registered.
- **E3 didn't move golden** (0.606 on the B rows, as in Phase D). ~~On dev it cost the CI gate 0.02, via D11~~: corrected, see below; the approximate index was drifting.
- **G-C27 isn't a guard in the full pipeline.** Its top-1 is §469(h), the statute *Garnett* interprets, and *Garnett* is 2nd in all 5 plan sets. E1 tagged it from a case-corpus-only search, a proxy that didn't hold. It's neither a conflict (the higher authority leads) nor a guard. **Proposed: untag it, as D42 was untagged in E1, and read the golden guard gate against the 8 guards that lead at baseline (≤ 1 of 8 lost).** Awaiting your decision (a golden edit).

**G-C27 untagged (your decision, 2026-09-28); the golden guard gate reads against the 8 guards that lead at baseline (≤ 1 of 8 lost).**

**Candidates built (2026-09-28):**
- `decompose.weigh()` (prior / tie, flat / scoped, statute-first and prior-version variants), the widened slot in `chunks(authority=…)`, and `search_k` for deeper search.
- 14 arms in `eval/retrieval.py`.
- The cross-encoder's scores are memoised (`lru_cache`, 4,096 pools): deterministic, so arms stop re-scoring the same pools.
- 4 tests, 31 in `test_decompose.py`.

**Stopped before measuring: dense search wasn't reproducible.** An old unit test, `test_dense_finds_the_hobby_loss_factor`, began failing with no code or data change.
- For that query, approximate (HNSW) dense search dropped §1.183-2(b)(3), which exact search ranks 3rd.
- Across 102 dev and golden questions, approximate shares 98.7% of the exact top 50 on average, **88% at worst**, and 99.6% of the top 10. Raising `hnsw_ef` to 256 gives 99.8%. Exact search costs 6 ms a query instead of 4 (vs ~1 s for reranking).
- **The CI gate read 0.7000 and then 0.7200 on identical code and data.** Qdrant re-optimised the collection in between (after E3's deletions and payload writes), and approximate results moved. Exact search reads 0.7200.
- **Consequences:** validation scan 2's "E3 cost the gate 0.02" is withdrawn. The E4 baseline was taken on a drifting index. A/B comparisons between arms need a fixed search.
- **Proposed (awaiting your decision):** exact dense search always (D3 already uses it under a filter). Then re-run the baseline and measure the candidates.

**Exact dense search, then the measurements (2026-09-28, your decision).**
- `retrieve.search` is exact (`55c2b20`); the drift test passes again; the reranker memo is bounded at 1,024 pools.
- CI gate under exact search: **0.7200** (`retrieval-dev-2026-09-28-k10-ci-exact.json`).
- The golden baseline was re-taken under exact search (`…-e4-baseline-exact.json`).

**Dev: every arm, 5 plan sets** (`retrieval-dev-2026-09-28-k{8,20}-e4-arms-exact.json`). Rules 1–3 were applied by a script written before the results were read. Conflict rows at target are out of 10, at k=8:

| arm | guards (of 8) + keep | worst category Recall@20 | at target |
|---|---|---|---|
| shipped | 8, ok | — | 0 |
| **prior 0.5, scoped** | **8, ok** | **+0.000** | **3** |
| prior 0.5, flat | **7** (breaks D05) | +0.000 | 3 |
| prior 1.0, flat / scoped | 5 / 7 | −0.167 / 0 | 3 |
| prior 0.25, flat / scoped | 8 | 0 | 2 |
| prior 0.1; tie 0.25 (either scope) | 8 | 0 | 1 |
| tie 0.1; slot; deep search | 8 | 0 | 0 |

- **Chosen: prior 0.5, scoped.**
  - Moves to top-1: D08, D18, D19, identical in all 5 plan sets.
  - Lifts but doesn't reach top-1: D14 5→2, D23 5→3, D27 7→3, D21 4→3, D16 5→4.
  - Out of reach: D26, D40.
- **Flat breaks exactly what E1's guards predicted:** D05's gold opinion loses first place to §420(f)(7), an off-topic statute.
- **Variants on the choice** (`…-e4-variants.json`), none better:
  - statute above regulation: 3, but D23's controlling regulation falls 3→5
  - "A" regulations demoted: 3, identical (dev has no "A" sections)
  - plus deeper search: 2

  Ties go to the simpler arm, so the choice stands.

**Golden, scored once (2026-09-28)** (`retrieval-golden-2026-09-28-k{8,20}-e4-golden-gate.json`; shipped vs chosen, same process, 5 plan sets):

| pre-registered criterion | threshold | shipped | prior 0.5 scoped | |
|---|---|---|---|---|
| conflict rows at target, of the 23 in the pool | ≥ 12 | 0 | **2.2** (2, 2, 2, 2, 3) | **not met** |
| guards still top-1 | ≥ 7 of 8 | 8 | **8** (every set) | met |
| `keep` source in the top 8 (G-S09) | kept | kept | kept | met |
| Recall@20, worst category change | ≥ −2 pts | — | **+0.000** (case law); statutory **+12.5**, temporal +9.1, compound +2.6 | met |

- **Not met, and not reinterpreted.** Reached target: G-S06 (top-1 in every set) and G-S08 (at 8, 7th), plus one more in one plan set.
- **Moved up without reaching target:** G-S09 8→2, G-C04 4→2, G-S02 out→4, G-S19 8→4, G-S10 8→5, G-X03 out→7.
- **Why golden falls short of dev (3/10), row by row:**
  - (1) **Reach:** 12 of the 23 have the controlling source outside the top 8 under both arms. A reordering of the statutory kind lifts a statute within its kind, but the compound rows' top 8 is shared with opinions.
  - (2) **The scope does what it was built to do:** in compound and reviewing-court rows the lower source that leads is an *opinion* (G-X02's *Morehouse*, G-X07's *Day*), and scoped never reorders across kinds.
  - (3) G-C04's reported opinion rose 4→2, not to 1.
- **What it does do:**
  - golden Recall@20 statutory 0.607 → 0.732: Phase A's 12.4-point publication dilution, restored inside the statutory kind
  - Recall@8 overall 0.493 → 0.529
  - dev CI gate arm 0.720 → **0.740** (nDCG 0.547 → 0.610, MRR 0.553 → 0.635; `…-k10-ci-e4-choice.json`)
  - zero guards broken
- **Latency:** not measurable from these runs. The chosen arm reused the first arm's cached reranker scores, so its p50 is flattering. The prior itself is a sort over the pool (~50 hits).

**Shipped (your decision, 2026-09-28):** `decompose.AUTHORITY` is `chunks()`' default, so `answer()` and the API's jobs path use it; eval arms that pass `None` measure the pre-E4 pipeline. The CI gate scores `route+statute1+prior0.5-scoped` (0.7400 locally; floor 0.70). `eval/e4_choose.py` added (reproduces the choice). ADR-8 revised. **Needed for CI to test it: a new snapshot (yours to publish).** Until then CI restores `corpus-2026-09-28`, whose points carry no profile, so the prior is inert there. ~~Awaiting your decision: ship it or not.~~ The gate's rerank half failed as pre-registered, but the change improves retrieval and breaks nothing. If shipped: a `decompose` constant (like `STATUTE`), `answer()` passes it, and the CI arm switches. **CI would need a new snapshot:** `corpus-2026-09-28` predates E2, and without the profile on the points the prior does nothing.

**Candidates (built behind a `chunks()` argument, off by default; each an `eval/retrieval.py` arm):**
- **(a) Additive prior.** Score + w × (level − 1), with w ∈ {0.1, 0.25, 0.5, 1.0}, bracketing the gap scale above.
- **(b) Margin tie-break.** Within δ ∈ {0.1, 0.25} of each other, the higher level first; otherwise the score decides.
- **(c) Controlling slot.** D3b's statute slot widened to "statute or final regulation", 1 slot.
- **Each of (a) and (b) in two scopes:**
  - *flat*, across the merged list;
  - *scoped*, where the boosted order is computed within each kind's candidates and that kind's original scores are then re-assigned in the new order. That leaves the cross-kind score profile, and so the statute-vs-opinion order, as the cross-encoder had it.
  - Scoped within case law still ranks reported over memo, and D03's guard (a reversed reported opinion over the gold memo) tests exactly that.
- **(d) Deeper search:** search each sub-query at 20 and choose 8, with and without the best of (a)–(c). This is for E0's 45.6 of 119 golden gold groups out of the k=8 pool: no reordering reaches those.
- **Variants on the best candidate:**
  - statute above regulation (the levels are equal today);
  - `final_prior_version` a quarter-level below `final` (E3's 136 "A" chunks);
  - no blanket demotion of reversed opinions (dropped in E0).

**Choosing on dev (rules fixed before measuring):**
1. Break no dev guard (0 of 8 lose top-1) and keep every `keep` source in the top 8.
2. Recall@20 regression ≤ 2 points in every dev category, mean over 5 plan sets.
3. Among those, the most dev conflict rows at target. Ties go to the simpler candidate: slot, then tie-break, then prior; scoped before flat; no deeper search before deeper search.

If no candidate meets rules 1 and 2, E4 ships nothing, and the report says so (as C5 did).

**The golden gate (pre-registered, to confirm with you before any golden run):**
- **Conflict rows:** at least half of the golden conflict rows whose controlling source is in the pool reach their target, up from the baseline. §9.3 says "changes the top-1 result on a curated authority-conflict subset" without a number; this puts one on it.
- **Guards:** at most 1 of the 9 golden guards loses top-1; every `keep` source stays in the top 8 (G-S09).
- **Recall@20:** ≤ 2 points regression in every golden category, 5 plan sets.
- **Reported, not gated:** conflict rows out of the pool (reach); Recall@8; regulation recall; G-T08; latency; which rows changed top-1 and to what.

**Shipping:**
- If the chosen candidate ships live, `decompose` gets it as a constant (like `STATUTE`), and the CI gate's arm follows.
- **The CI gate stays at 0.70** (your decision). It is re-run on a new snapshot that carries E2–E3's metadata and exclusions; publishing that snapshot is your call.

**Acceptance criteria:**
- [x] Plans generated (counts and cost stated); baseline on dev and golden recorded with the authority metrics
- [x] Every candidate measured on dev (5 plan sets), rules 1–3 applied as written, the choice recorded with the table
- [x] Golden gate thresholds confirmed with you before the golden run; golden scored once: **not met on the conflict criterion** (2.2 of 23 vs ≥ 12)
- [x] CI retrieval gate ≥ 0.70 on the shipped arm (or E4 ships nothing): **0.7400** locally on the new arm

**Verification:**
- [x] Tests: each candidate on fixture hits:
  - the prior reorders but never drops a hit;
  - scoped keeps the cross-kind order;
  - the tie-break respects δ;
  - the slot fills only from statute or final regulation;
  - ties are broken deterministically
- [x] `uv run pytest -q` passes

**Dependencies:** E1, E2, E3
**Files:** `src/taxcite/decompose.py` (`chunks()`), `eval/retrieval.py` (arms, authority metrics), `eval/results/decompositions-d7.json` (plans), `.github/workflows/` (if the arm changes), `tests/test_decompose.py`
**Scope:** M

---

## E5: Authority in answers

**Goal:** the answer knows, and shows, how much weight each source carries. Synthesis sees each source's authority, the answer follows the higher one where sources conflict, and every citation in the API response carries an authority label built from structured fields only (FR-8, FR-14, ADR-13). Answer-level effects are measured, with several answers per row, but not gated. Faithfulness and its refusal-rate check stay the standing gates.

**What the code fixes before any design (2026-09-28):**
- **Rule 4 of `RAG_SYSTEM` already ranks authority,** and has since Phase A: "Regulations and statute outrank IRS publications. Where they differ, follow the regulation and say so." E5 extends a rule every question already gets. It isn't a new one.
- **D7's lesson applies:** a prompt rule given to every question changed undated answers (refusals 0.13 → 0.55) while faithfulness still passed. Any rule change here is measured on refusals across all dev rows, not just the rows it targets.
- **Source headers carry no authority today:** `format_sources` writes `[citation] (heading)` plus D7's "Effective:" note. `Hit.authority` (E2) is on every retrieved chunk, so a label needs no lookup.
- **The API's answer event** (`jobs.run`) carries citations as bare strings, with `treatments` beside them (C4). There is no per-citation authority.
- **Answer-level sampling:** synthesis runs at temperature 0, seed 0, so regenerating on one plan gives near-copies. The variance that reaches the answer is the planner's (routing decides which sources are grouped under which part of the question). **So "N samples" means one answer per cached plan set, N = 5,** using the sets E4 step 0 generated. This is Phase D's open handoff ("`--samples N` before the next answer-level gate"), made to measure the variance that exists.

**Step 0: the measurement, then the baseline (no prompt change).**
- **Sampling.** `eval/temporal.py` gets `--rows temporal|authority` and `--samples N`: answer *i* is generated from plan set *i*, cached per (question, plan set) in its own answers file. Its judge path is reused unchanged: §9.2's rubric against the reference answer, κ-checked against the alternate phrasing, plus the grounding check. For `authority` rows the as-of check is skipped, since they have no year.
- **Baseline** on dev's 18 tagged rows (10 conflict, 8 guards), 5 samples each, under E4's shipped retrieval. Measured:
  - graded correct / partial / incorrect
  - the count of the "authority misweighted" defect tag
  - grounded rate
  - refusal rate

  Plus refusals and faithfulness through the standing faithfulness harness, which scores dev's 25 B rows (the gate's own row set, not all 41: corrected when step 0 ran). The 18 tagged rows' refusals come from their 5 samples. About 90 answers and 180 judgements: under $1.

**Candidates (prompt only; retrieval unchanged):**
- **(i) Labels only.** Each source header gains "Authority: …" from the profile, through a fixed map (below). Rule 4 is unchanged.
- **(ii) Labels + rule 4 widened:** "Each source is labelled with its authority. Where sources disagree, the higher authority governs: statute and regulation, then a reported Tax Court opinion, then a memorandum opinion, then an IRS publication. Say which you followed. A lower source may explain the rule in plain words, but cite the higher source for the rule itself."
- There is no year-style conditional variant. Nearly every question's top 8 mixes levels, so "only when levels differ" would be almost every question anyway; that's the measured reason (E0's top-8 mix).

**Choosing on dev (rules fixed before measuring):**
1. Refusal rate at most 0.05 above baseline, on the faithfulness harness's dev rows and on the tagged rows' samples, and ≤ 0.25 (the standing gate's bound).
2. Grounded rate on the 18 tagged rows at most 0.05 below baseline.
3. Among those, the fewest "authority misweighted" tags on the 10 conflict rows, then the most graded correct. Ties go to (i).
- If neither passes rules 1–2, labels ship in the API response only, and the prompt stays as it is.

**Authority in the API response (ships regardless of the prompt choice):**
- The answer event gains `authorities`: {citation: {"type", "status", "level", "label"}}.
  - exact citations: from the retrieved hit's stored profile
  - derived citations (a paragraph of a retrieved section): from that section's hit
  - unsupported citations: `unknown`, never guessed
- **Labels come from one fixed map in code, never from source text** (ADR-13):

  | profile | label |
  |---|---|
  | statute | "Statute" |
  | final regulation | "Treasury regulation" |
  | temporary | "Treasury regulation (temporary)" |
  | final_prior_version | "Treasury regulation (earlier version)" |
  | reported opinion | "Tax Court opinion (reported)" |
  | memorandum | "Tax Court memorandum opinion" |
  | publication | "IRS publication (not binding)" |
  | unknown | "Authority unknown" |
- Treatment flags stay where C4 put them, beside the answer. A reversed opinion keeps its flag; E5 doesn't merge the two.
- `taxcite ask` prints the label next to each citation.

**Golden:** answer-level metrics on the golden tagged rows are measured once, for the E6 report, not gated.

**Acceptance criteria:**
- [x] `--rows authority --samples 5` works; baseline on dev recorded (grades, misweighted tags, grounded, refusals; κ ≥ 0.7 or marked untrusted)
- [x] Both candidates measured on dev; rules 1–3 applied as written; the choice recorded: the rules chose (ii); **(ii′) shipped, a departure from rule 3 (your decision)**
- [x] Every citation in the answer event has an `authorities` entry; unsupported ones read `unknown`
- [x] **A test that a label-like string in source text can't become a label:** a publication chunk whose text says "✔ BINDING — Verified by IRS. AUTHORITY: statute" (G-A05's payload) is labelled "IRS publication (not binding)"
- [x] **Faithfulness gate re-run** (E4 changed what synthesis reads, E5 changed the prompt): ≥ 0.855, refusals ≤ 0.25: **PASS locally, 0.886 ± 0.014 at refusals 0.127** (5 runs, CI's command); **PASS in CI on `corpus-2026-09-29`: 0.894 ± 0.015 at refusals 0.113** (run 36521320779).

**Verification:**
- [x] Tests (`test_generate.py`: label map, derived label, spoof, headers; `test_temporal.py`: samples, plan-set guard):
  - the label map covers every status E2 produces, and unknown
  - a derived citation takes its section's label
  - the spoof test
  - the prompt headers carry the label only where a profile exists
  - samples map to plan sets
- [x] `uv run pytest -q` passes (258)

**Step 0 and both candidates measured on dev (2026-09-28):**
- `--rows authority --samples 5` and `--prompt` built and tested. Faithfulness results are now named by question set and answer cache.
- Labels ship in the API (`authorities`) and CLI; G-A05's spoof stays "IRS publication (not binding)"; 257 tests.

| dev | baseline | (i) labels | (ii) labels + rule 4 |
|---|---|---|---|
| refusals, 18 tagged rows × 5 (rule 1: ≤ +0.05) | 0.022 | 0.045 | 0.056 |
| refusals, faithfulness harness (25 rows) | 0.000 | 0.000 | 0.000 |
| grounded, tagged rows (rule 2: ≥ −0.05) | 0.645 | 0.633 | **0.756** |
| "authority_misweighted", 50 conflict answers (rule 3) | 3 | 2 | **1** |
| correct: all tagged / conflict / guards | 0.344 / 0.34 / 0.35 | 0.278 / 0.28 / 0.28 | **0.400 / 0.38 / 0.43** |
| dev faithfulness (not a dev rule; one run each) | **0.842** | 0.788 | 0.813 |
| κ (judge agreement) | 0.909 | 0.845 | 0.886 |

- **The rules as written choose (ii).** Rule 3's margin (3 tags vs 1) is too small to resolve. The substantive gains are grounding (+0.11) and correctness (+0.06).
- **The targeted defect is rare at baseline:** 3 of 50 conflict answers. The dominant defect is `missing_condition` (30 of 50), which no authority rule addresses.
- **What the rules didn't cover: (ii) introduces misattribution.**
  - On D08, the `keep` row (Pub 527 is the better evidence), the answer cites the publication's plain-English test ("management decisions in a significant and bona fide sense") to 26 U.S.C. § 469(i)(6)(A), which doesn't say it. Faithfulness 0.67 → 0.25.
  - The cause is the clause "cite the higher source for the rule itself". Rule 2's grounding check didn't catch it, because grounding reads the answer's claims against all its sources, not each claim against the source it cites.
  - Dev faithfulness overall: 0.842 → 0.813 (down on D07, D08, D10, D12, D17, D18, D23; up on D02, D05, D06, D25). D18's drop reads as judge noise (near-identical answer).
- ~~**Proposed (awaiting your decision):**~~ Measured (your decision): a candidate (ii′) without that clause, measured on dev by the same rules: "…the higher authority governs… Say which you followed." Plus faithfulness with 3 repeats on the baseline and (ii′), so the ~0.03 differences have a spread next to them. Golden stays untouched. Cost ≈ $1.50.

**(ii′) measured on dev (2026-09-28)** (`temporal-dev-2026-09-28-e5rule4b.json`; faithfulness ×3: `ragas-dev-2026-09-28-ragas-answers-e5rule4b.json`, baseline ×3: `…-e5base3.json`):

| dev | baseline | (i) | (ii) | **(ii′)** |
|---|---|---|---|---|
| refusals, tagged (rule 1: ≤ +0.05) | 0.022 | 0.045 | 0.056 | 0.067 (+0.045, just inside) |
| refusals, faithfulness rows | 0.000 | 0.000 | 0.000 | 0.000 / 0.000 / 0.040 |
| grounded, tagged (rule 2) | 0.645 | 0.633 | 0.756 | **0.789** |
| "authority_misweighted", of 50 (rule 3) | 3 | 2 | **1** | 4 |
| correct: all / conflict / guards | 0.344 / 0.34 / 0.35 | 0.278 | **0.400** / 0.38 / 0.43 | 0.322 / 0.32 / 0.33 |
| dev faithfulness | **0.821 ± 0.015** (×3) | 0.788 (×1) | 0.813 (×1) | **0.835 ± 0.043** (×3) |
| D08 faithfulness (the misattribution row) | 0.57 / 0.67 / 0.80 | 0.80 | **0.25** | 0.67 / 0.67 / 1.00 |
| κ | 0.909 | 0.845 | 0.886 | 0.920 |

- **The pre-registered rules, applied as written to all three candidates, still choose (ii):** it passes rules 1–2 and has the fewest misweighted tags (1). (ii′) passes rules 1–2 too, with 4 tags.
- **Why the rules don't settle it:**
  - Rule 3's counts (1, 2, 3, 4 of 50) are within one row's flip: D23 alone accounts for most.
  - The correctness spread across samples is ~0.05 sd, so (ii)'s 0.400 against (ii′)'s 0.322 is about 1.5 sd.
  - The one difference with a demonstrated mechanism is (ii)'s misattribution. Rule 2's grounding check can't see it, because it doesn't check a claim against the source it cites.
- **Recommendation: (ii′).** It keeps the grounding gain (+0.14, the largest of any arm) without (ii)'s misattribution; faithfulness equals the baseline within noise; and its correctness and misweighted counts are indistinguishable from the others at this sample size. **This departs from the rule as written,** and the report will say so.
- **The alternatives:** (ii) as the rules pick it, knowing it cites publications' words to statutes; or labels in the API only, with the prompt unchanged.

**Shipped (your decision, 2026-09-28): (ii′), recorded as a departure from rule 3.**
- `generate.RAG_SYSTEM` is the pre-E5 prompt with rule 4 replaced by `RULE_4_AUTHORITY_B`; `SOURCE_LABELS` is on; `PRE_E5_SYSTEM` keeps the old prompt.
- The eval arms are rebuilt from it: `pre-e5`, `labels`, `labels+rule4`, `labels+rule4b`, and `shipped`, which leaves the module as is. **The runs before this change used "shipped" to mean the pre-E5 prompt** (the `e5base` files).
- 258 tests, one of them checking that (ii′) ships and `pre-e5` reproduces the old prompt exactly.
- **The departure, in one line:** rule 3 ranked by a count too small to resolve (1 vs 4 misweighted tags of 50), and the arm it picked has a demonstrated misattribution that the grounding rule can't see. The rule would have needed a per-citation support check to see it.
- **For the next pre-registration:** add citation-level support (does the cited source state the claim?) as a rule, not just answer-level grounding.

**Golden faithfulness gate, local, CI's command: PASS (2026-09-28, after your credit top-up)** (`ragas-golden-2026-09-28-pipeline-answers-e5.json`):
- faithfulness 0.873 / 0.885 / 0.891 / 0.873 / 0.907, **mean 0.886 ± 0.014** (Phase D: 0.882 ± 0.011); refusals **0.127** (0.104–0.135; Phase D 0.125–0.156)
- E4's reordered top 8 and E5's labelled prompt cost nothing in faithfulness and don't add refusals. $2.27 judge + $0.36 pipeline.

~~**Golden faithfulness gate, run locally as CI runs it: incomplete, 2 of 5 runs.**~~ (first attempt, below; superseded)
- Command: `ragas_eval.py --repeats 5 --max-cost 5.00 --fail-under 0.855 --max-refusal-rate 0.25 --answers-cache eval/results/pipeline-answers-e5.json`, with CI's plan cache.
- **Run 1: 0.881 at refusals 0.135. Run 2: 0.889 at 0.135.** Both clear 0.855 and 0.25, in line with Phase D's healthy 0.882 at 0.125–0.156.
- **Stopped in run 3** by an Anthropic API error, "credit balance is too low" (the judge is `claude-haiku-4-5`); $1.10 spent. Not a gate verdict.
- To finish: top up the Anthropic credit and re-run the same command. The answers for runs 1–2 and part of run 3 are cached in `pipeline-answers-e5.json` (not committed, like CI's default cache), so only the judge re-runs for those.
- Still open for E6: the workflow's own note asks for the healthy **and** broken bands to be re-measured after any pipeline change. E4 and E5 are both pipeline changes. Your decision.

**Golden answer metrics, measured once for E6 (2026-09-29)** (`temporal-golden-2026-09-29-e5golden{,-pre}.json`): 32 tagged rows × 5 samples, the pre-E5 prompt and (ii′), E4's retrieval in both.

| golden | pre-E5 | (ii′), shipped |
|---|---|---|
| correct, all | 0.356 ± 0.036 | 0.369 ± 0.068 |
| correct: conflict / guards | 0.267 / 0.625 | 0.275 / 0.650 |
| grounded | 0.650 | 0.675 |
| refused | 0.037 | 0.031 |
| "authority_misweighted", of 120 conflict answers | 9 | 12 |
| κ | 0.720 | 0.736 |

- **No measurable effect on golden answer quality:** every difference is inside the sample spread. Dev's grounding gain (+0.14) shrank to +0.025. Dominant defect in both arms: `missing_condition` (58–64 of 120).
- **The misweighting is concentrated in two reviewing-court rows, in both arms:** G-X02 (*Morehouse*, Iowa; 5/5) and G-X09 (*Menard*, Wisconsin; 4–5/5). **Synthesis never sees the appeal outcome:** Phase C put treatment flags beside the answer, not in the prompt, so the model applies a reversed Tax Court holding to a taxpayer in the reversing circuit. An authority label ("Tax Court opinion (reported)") can't carry that.
- **Handed on (open):** give synthesis the treatment flag in the source header ("reversed by 769 F.3d 616 (8th Cir. 2014)"), from `flags()`, like the label. That's structured data again, so ADR-13 holds. For E6 to list; not built here.
- Judge: $1.10 + $1.08.

**Dependencies:** E2, E4 (and your snapshot, for the CI faithfulness run)
**Files:** `src/taxcite/generate.py` (headers, rule 4, the label map), `src/taxcite/jobs.py` (`authorities`), `src/taxcite/cli.py` (`ask` output), `eval/temporal.py` (`--rows`, `--samples`), `tests/`
**Scope:** M

---

## E6: Phase E exit report

**Description:** `eval/results/phase_e.md` in the shape of `phase_d.md`: E0's findings and decision, the metadata accuracy per field, the ladder with the authority rung, the conflict subset row by row, answers with their sample spread, failures with examples, §9.3 recalibration notes. Update the tech doc's Implementation Status, baselines, §7 and §9.3.

**Acceptance criteria:**
- [x] Every number traces to a results file or a command at the foot of the report
- [x] Both §9.3 Phase E gates stated as met or not met, with no reinterpretation

**Drafted 2026-09-29:** `eval/results/phase_e.md` (a new file, handed to you to create); tech doc Implementation Status, baselines, §7 and §9.3 updated. Metadata gate: not met, then met on re-check; conflict criterion: not met; recall regression and guards: met; faithfulness: met locally.

**Dependencies:** E4, E5
**Files:** `eval/results/phase_e.md`, `taxcite-technical-documentation.md`
**Scope:** S

---

## ✅ Checkpoint: Phase E complete
- [ ] Authority metadata ≥95% field-level on the 150-chunk stratified sample: **not met on the first sample** (regulation status 75.0%, treatment 86.7%); met on a fresh 146-row re-check after four fixes (treatment re-checked on affirmances only)
- [ ] Controlling source moves to top-1 on the golden conflict subset; ≤2-point Recall@20 regression per category: conflict **not met** (2.2 of 23 reachable rows vs a pre-registered 12); regression met (none down; statutory +12.5); guards 8/8 kept
- [x] Tests and both CI gates green on a new snapshot: `corpus-2026-09-29`; retrieval 0.7400 (run 36521274499), faithfulness 0.894 ± 0.015 at refusals 0.113 (run 36521320779)

---

# TaxCite Phase F — Task List

Plan: `tasks/plan.md` (Phase F). Test command: `uv run pytest -q`. Every task leaves the repo runnable. Approved 2026-09-29. F2–F5 are briefed in outline; each gets its full brief after F0, as E's did.

---

## F0: Verification spike

**Goal:** before building, find out (a) whether the judge's labels can be trusted, (b) whether a sentence + citation is a good enough claim unit, (c) whether any self-hosted NLI model reaches F1 ≥0.90 against the judge (ADR-4 go/no-go), and (d) how much ADR-15 would suppress. A diagnosis on existing answers; no product code changes.

**Input:** cached golden answers from the shipped pipeline (`eval/results/pipeline-answers-e5.json` or CI's latest), with their retrieved chunks. No new synthesis calls.

**Steps:**
1. **Pairs.** Split each answer into sentences; keep those with a bracket; pair each with its cited chunk(s) (exact, derived → section's chunks, unsupported → auto-fail). Count: sentences per answer, share uncited, share citing ≥2 sources, share of premises over 512 tokens.
2. **Judge labels.** The Haiku judge (`VERDICT_SYSTEM`) labels each pair against its *cited* source only. Also run the existing claim extractor on the same answers, and map its claims back to sentences to see how often one sentence holds more than one claim, and how often they disagree.
3. **Judge check.** You read ~40 pairs, stratified: judge-unsupported over-sampled (G-S10 and G-S14 included). Agreement reported.
4. **NLI candidates.** DeBERTa-v3 base and large (MNLI/FEVER/ANLI checkpoint), HHEM-2.1-open. Windowed premises, best window. Per model: F1 and precision/recall on the "not supported" class, false-accept rate, CPU ms per answer. Pick the threshold on half the pairs and report on the other half, so the number isn't tuned on itself.
5. **Projected suppression.** Under the judge's labels and under the best NLI model: the share of answers suppressed if the unit is (i) the whole answer, (ii) one section per sub-query (approximated by which group each cited chunk came from), (iii) the sentence. Beside it, today's refusal rate (~0.11–0.13).
6. **Abstention today.** On the 11 insufficiency rows plus answerable rows: refusals from rule 3, as the baseline F2 must beat.

**Acceptance:** an `eval/results/f0_*.md` note with the numbers above; a go/no-go on NLI (or the evidence for ADR-4's revision); a recommended sub-answer unit backed by (5). Log entry.

**Files:** one spike script under `eval/` (new file: you create it from my code block); a dev-only `transformers` dependency if an ONNX export isn't available for a candidate.

**Results (2026-09-30).** Script `eval/f0_verify.py`; outputs `eval/results/f0-pairs.json`, `f0-nli-{base,large,hhem}.json`, `f0-report.json`, `f0-judge-check.md`. 305 distinct golden answers (96 rows × 5 cached runs of the shipped pipeline); 42 refused, 263 answer. Judge spend $0.76 (Haiku, one call per answer and unit), after two judge fixes found by reading its failures: the chunk heading is now in the premise (synthesis saw it; an opinion's case name lives only there), and several cited sources are judged together, not each alone.

| | |
|---|---|
| Sentences in answers | 859: **378 cited, 481 uncited** (349 sit before a citation in their paragraph, 132 trail the last one) |
| Cited sentences per answer / LLM claims per answer | 1.44 / 3.95 |
| Supported by their **own** citation (judge) | **0.734** of 372 (+6 citing nothing retrieved). Today's faithfulness, against all 8 chunks: 0.886 |
| Unsupported, by kind (keyword heuristic) | 73 state a rule or holding with an exact citation; 26 apply it to the question |
| "Answer has a failing claim": sentence unit vs today's judge | agree on 177 of 263; 42 fail only today, 44 only here |

NLI against the judge, "not supported" class, sentence unit (threshold fitted on one half of questions, scored on the other, both ways; halves swing 0.36–0.76, so the mean is the number):

| Model | Held-out F1 | Ceiling (fit on all) | CPU s/answer (M4) |
|---|---|---|---|
| DeBERTa-v3 base (MNLI/FEVER/ANLI) | 0.56 | 0.59 | 0.7 |
| DeBERTa-v3 large (+ling, wanli) | 0.51 | 0.59 | 2.1 |
| HHEM-2.1-open | **0.61** | 0.67 | 0.7 |

Span unit: 0.42 / 0.51 / 0.52. **No candidate is near 0.90, even at its in-sample ceiling.** Accept-all would score 0.85 on the "supported" class: why the gate reads the other one.

What ADR-15 would hide (judge labels, answers that weren't already refusals):

| Unit | Whole answer | Section (per sub-query kind) | Answer emptied by sections | Claim |
|---|---|---|---|---|
| sentence | 0.37 | 0.33 | 0.32 | 0.28 |
| span | 0.37 | 0.33 | 0.32 | 0.28 |

If an uncited sentence also fails: 0.92 of answers (sentence unit), 0.53 (span). Today 0.14 of answers refuse already.

Abstention today (all 5 runs): 10 of 11 insufficiency rows refuse 5/5; `G-I06` 0/5; `G-I11` refuses both halves 5/5. Answerable rows refuse in 11 of 425 runs.

**Readings, before the judge check (superseded by it, below):**
1. **The self-hosted NLI verifier is a no-go against the 0.90 gate** (best 0.61). Unless your read shows the judge is wrong, ADR-4 gets a *Revised* note: the runtime verifier is an LLM call, batched per answer (as ADR-10 batches sufficiency). Cost is known: $0.0025 an answer on Haiku.
2. **Verification can't start from today's answers.** A third of answers would be emptied, on top of 14% refusing. The cause is synthesis: a quarter of cited sentences say more than their own citation does, and most sentences carry no citation. F3 has to change what synthesis writes (cite every sentence; one citation says only what its source says) before F4 suppresses anything, and ADR-11's trigger (Haiku synthesis) is measured on dev there.
3. **Span beats sentence as the unit** for coverage (uncited-fail 0.53 vs 0.92), at the same suppression.

**Judge check (2026-09-30, done by Claude at your request, two scans; one careful LLM reader, not a human).** First scan: my verdict on all 40 pairs of `f0-judge-check.md`. The judge agrees on **30 of 40** (F1 on "not supported" 0.74). It says "not supported" wrongly 6 times, "supported" wrongly 4. **HHEM agrees on 30 of 40 too (F1 0.76)**, so F0's NLI "no-go" rested on treating a ~75%-accurate judge as ground truth: *not established*. Second scan: the causes, counted over all 744 judged pairs, not just the 40:

| Edge case | Pairs affected | Example | Fix |
|---|---|---|---|
| Judge never sees the question, so a claim restating the client's facts can't be supported | 22 name the client, 10 judged unsupported | P13 ($60,000 / $40,000 are the client's, not the case's), P35 ("No," answers the question) | give the question, facts "taken as given, not law" |
| A sentence alone loses what it refers to | 133 open with Therefore/This/However…, 34 unsupported | P03 ("Therefore" follows "The Eleventh Circuit has concluded…") | give the answer's earlier text as context, not to be judged |
| A derived citation expanded to every retrieved chunk of its section | 27 pairs, 5 unsupported | P09 (`280A(e)(1)` pulled in (c)(1), (d)(4); judge objected to "irrelevant citations"), P20 (`at *11-12` pulled in `*14`) | map to the chunk that contains it (paragraph prefix, page overlap); whole section only as fallback |
| Pinpoint to the wrong page of a retrieved opinion | **49 of 99** unsupported cite an opinion with other retrieved pages | P01 (Genecure's reasoning is on a neighbouring page), P32 (nexus holding is in the headnote, `*1-2`) | **a policy decision** (below) |
| Judge lenient on partly supported multi-sentence claims | 4 of 20 "supported" in the sample | P14, P22/P40 (drops §183(b)'s exception), P27 (first sentence contradicts Pub 527) | "every assertion must be supported; any unsupported part, qualifier or condition fails it" |
| "Judged together" instruction ignored | P20 | | reworded: "even if some of them say nothing relevant" |
| Splitter breaks at lowercase `sec.` | 4 fragments ("1402(a)(1) and are not excluded…") | P19, P37 | case-insensitive abbreviations |
| Nested / multi-citation brackets | 2 in 305 answers (`[26 U.S.C. § 3121(d)(1), [119 T.C. No. 5, at *7-8]]`) | P11 | **also in `generate.parse_citations`** (same regex): fix in F3 |
| Near-duplicate claims across runs | 372 sentence pairs, 306 distinct; judge flips on 1 of 308 | P02/P21, P22/P40 | report distinct n; split stays by question |
| Judge's "Source N" numbers are its own, not the sheet's order | cosmetic | P03's note | number the sheet the judge's way |

Re-judged the same 40 with the input fixes (question + earlier text + narrowed derived citations), ~$0.10: **V2 35/40 (F1 0.85)**; with the every-part rule, **V2b 36/40 (F1 0.89)**; two of its four remaining disagreements (P24, P35) are ones where a strict reading sides with the judge. Opinion-wide pinpoint (V3b) moves P01, P05, P06, P33 to supported: 33/40 against my cited-page labels, which is the policy difference, not error.

**What this changed (before the re-run below):** F0's headline numbers (0.734 supported; NLI F1 0.51–0.61; ~32% of answers emptied) were measured against the flawed judge and are withdrawn until F0 is re-run with the V2b judge. The NLI verdict and ADR-4's revision wait for that re-run. The finding that stands: uncited sentences (481 of 859) and misattribution are real (P02/P21, P08, P34/P38 are unambiguous).

**Re-run with the fixed judge (2026-09-30; your policy: a claim is checked against every retrieved page of the opinions it cites, the page scored apart).** Judge $1.65 (main pass + page pass); NLI 410 s / 1,212 s / 402 s on the M4 CPU. The splitter fix merged the 4 fragments back (859 → 853 sentences; the two G-C03 check pairs are gone, 38 remain).

| | first run (flawed judge) | re-run |
|---|---|---|
| Cited sentences supported by their citation | 0.734 | **0.860** (spans 0.866); today's all-context faithfulness 0.886 |
| Judge vs my 38 verdicts | 30/40 | **31/38**: single sentences **15/16**, multi-sentence spans 16/22 (lenient on extra assertions) |
| Opinion claims whose cited *page* doesn't support them (passed on another page) | — | **28 of 168** |
| Uncited sentences | 481 of 859 | 475 of 853 (343 sit before a citation) |

NLI against the fixed judge, "not supported" class, sentence unit (held out both ways; ceiling = fitted on all):

| Model | Held-out F1 | Ceiling | False accepts | vs my 38 verdicts | CPU s/answer (both units) |
|---|---|---|---|---|---|
| DeBERTa-v3 base | 0.22 | 0.42 | 0.60 | 24/38 | 1.6 |
| DeBERTa-v3 large | 0.40 | 0.47 | 0.65 | 28/38 | 4.7 |
| HHEM-2.1-open | 0.42 | 0.47 | 0.20 | 24/38 | 1.6 |
| (the judge itself) | — | — | — | 31/38 | — |

Worse than the first run, for two reasons: unsupported claims are now rarer (14%), and each claim is read against every page of its opinion (870 of 981 premises windowed), so a model taking the best window over many finds spurious entailment. **No NLI model is near 0.90 even in-sample, and the judge beats all three against a careful read. The NLI no-go now stands.**

What ADR-15 would hide (fixed judge, answers that weren't already refusals): sentence unit, whole answer 0.22, **section 0.20, answer emptied by its sections 0.18**, claim 0.15. On top of 0.14 refusing today. If an uncited sentence also failed: 0.90 of answers (sentence unit), 0.42 (span).

**Conclusions for Checkpoint 1 (proposed):**
1. **ADR-4 revised:** the runtime verifier is an LLM call, one batched call per answer, as ADR-10 batches sufficiency: ~$0.0023 an answer on Haiku (this run's main pass, per unit). Self-hosted NLI measured and rejected (table above).
2. **The gate needs an independent reference.** If Haiku verifies at runtime, "F1 against the Haiku judge" is circular. Proposed: the verifier is scored against a different model (the audit judge) plus a hand-checked sample, and the audit judge is itself checked on that sample, as done here.
3. **Unit: the sentence, read with the question and the whole answer as context** (15/16 against 16/22 for spans). Uncited sentences are F3's job: synthesis cites every sentence, so the sentence unit covers the answer.
4. **Suppression (~18% of answers emptied) is too high to ship as is:** F3 changes synthesis first (cite every sentence, say only what the cited source says), and ADR-11's trigger (Haiku synthesis) is measured on dev there.

**Can a small model be rescued? (2026-09-30, quick test at your request, sentence unit, no judge cost.)** Tried: two checkers built for this task (MiniCheck RoBERTa-L and DeBERTa-v3-L), reading only the reranker's top 3 windows instead of every page (`--premise top`), and triage (small model decides what it's sure of, the LLM the rest; thresholds fitted on one half, ≤2% unsupported among auto-accepts, scored on the other).

| Model | Held-out F1 | Ceiling | Triage: share decided alone | Unsupported let through (of 52) | CPU s/answer |
|---|---|---|---|---|---|
| MiniCheck-DeBERTa (best) | **0.46** | 0.54 | **0.36** | 3 | 2.45 (top 3: 1.08) |
| MiniCheck-RoBERTa | 0.40 | 0.50 | 0.29 | 6 | 1.55 (top 3: 0.67) |
| HHEM | 0.42 | 0.47 | 0.26 | 3 | 1.56 (top 3: 0.37) |
| DeBERTa-v3 large | 0.40 | 0.47 | 0.28 | 9 | 4.70 (top 3: 1.07) |

Reading the top 3 windows costs ≤0.05 F1 and is 2–4× faster. **Still nowhere near 0.90; triage would save at most a third of LLM calls (~$0.0008 an answer) while letting 3 of 52 unsupported claims through, which ADR-15's zero tolerance forbids.** Not worth it at this volume. Kept as ADR-4's revisit trigger: if privacy (client documents, Phase G) or volume makes the LLM call a problem, fine-tune MiniCheck-DeBERTa on judge-labelled tax pairs, run it on the top 3 windows, and re-measure triage.

---

## F1: Insufficiency rows and entailment pair sets

**Goal:** give F2 a dev set to tune on and F5 a fixed golden audit set, before anything is tuned.
- ≥10 dev insufficiency rows, mirroring golden's kinds (future-year figures, state/foreign law, IRS operations, legislation not yet passed) without sharing a citation with golden. ≥3 of them partial (one answerable half, one not), like `G-I11`. `expect_insufficient` gains a per-part form for partials.
- Entailment pair sets: dev pairs (for F4's threshold) and golden pairs (scored once, F5), from F0's sentence splitter, judge-labelled, frozen as JSON so every NLI run scores the same pairs.
- `validate_pilot.py` checks the new fields. Golden audit rule: logged commits you review.

**Acceptance:** rows approved by you (Checkpoint 1); pair files committed with their counts.

**Changed after F0 (2026-09-30):** the frozen entailment pair sets move to F5. Pairs are made from answers, and F3 changes how synthesis writes them (every sentence cited), so pairs frozen from today's answers would audit a pipeline that no longer exists. F1 is the rows only.

**Done (2026-09-30), `eval/dev.jsonl` D43–D53, approved by you and committed (`a5c2023`):** 11 rows, 3 partial, `scored_from: "F"`, same kinds as golden's 11, no gold shared with golden (checked: golden's gold has no §221, §219, §223, §2503 or Pub 17 p. 76/81).

| Row | Kind (golden sibling) | Question (short) | Why insufficient: checked in the corpus | Trap |
|---|---|---|---|---|
| D43 | future figure (G-I01, G-I02) | 2027 gift tax annual exclusion | no chunk has 2027 with gift/exclusion | — |
| D44 | future figure | 2027 HSA family limit | no chunk has 2027 with health savings | §223(b)(2) base amounts |
| D45 | state (G-I03/04/09) | Pennsylvania tax on 401(k) distributions | no non-opinion chunk gives PA tax rules | — |
| D46 | state | Massachusetts rate on short-term gains | none gives an MA rate | §1222, federal rate chunks |
| D47 | foreign (G-I05) | Germany's tax on a US citizen's German dividends | US federal law only | §245/245A |
| D48 | IRS operations (G-I06) | TAS case-assignment wait | TAS described, no times | §7811, Pub 17/587 TAS text |
| D49 | announced rate (G-I07) | short-term AFR, March 2027 | no 2027 rate; may state §1274(d)'s method | — |
| D50 | future legislation (G-I08) | will Congress repeal §280E? | unknowable; may state current law | Mission Organic pages |
| D51 | **partial** (G-I11) | student loan interest: federal + New Jersey | federal: §221(a)-(c); NJ: no state law | Pub 17 p. 99 names New Jersey (state benefit funds only) |
| D52 | **partial** | alimony paid under a 2020 agreement: federal + California | federal: Pub 17 p. 76 (indirect: §§71, 215 repealed and excluded); CA: none | — |
| D53 | **partial**, future half | traditional IRA limit for 2025 + 2027 | 2025: Pub 17 p. 81 ($7,000); 2027: none | §219(b)(5) still says $5,000 |

Partial rows carry `parts` (`[{part, insufficient, gold}]`); `validate_pilot.py` checks them (each part named and flagged; answerable parts have gold inside the row's gold; at least one of each kind). Golden's G-I11 gained `parts` (your approval; only that field changed, all 116 golden rows validate).

---

## ✅ Checkpoint 1 (human review)
- [x] Judge labels read (~40 pairs, by Claude at your request, two scans); agreement recorded (30/40 before fixes; 15/16 sentences, 16/22 spans after)
- [x] Confirmed by you (2026-09-30): ADR-4 revised (LLM verifier, one call per answer; small models rejected); the gate scored against an independent audit reference; sentence unit with question + whole answer as context; F3 before F4. Sub-answer unit: one section per sub-query (approved with the plan)
- [x] F1's 11 rows approved by you (2026-09-30), and `parts` added to golden G-I11 (`a5c2023`); pair sets moved to F5

---

## F2: Sufficiency gate

**Goal:** before anything is written, decide for each part of the question whether its retrieved sources can answer it, and write nothing for a part that can't (ADR-7, ADR-10, FR-5). F4 hides an unsupported sentence after it's written; F2 keeps it from being written.

**Why (measured, shipped pipeline):**
- **Golden, Phase B onward:** `G-I06` (amended-return processing times) is answered, from nothing, in every run; `G-I11` (federal home office + California) refuses both halves before F3 and, since F3, answers the federal half but writes about California from sources that don't cover it.
- **Dev, F4:** 24% of sentences fail verification and 9 of 126 answers are emptied. Some of that is synthesis writing about a part its sources don't cover; a part skipped up front costs nothing to hide.
- **Refusing is today a sentence the synthesis model chooses to write** (rule 3, now "add the part to not_answerable"). Nothing checks it.

**What changes:**
1. **`sufficiency(question, label, hits, year) -> Verdict`** in `decompose.py` (or a new `sufficiency.py`, handed to you as code if so): one structured-output call per searched sub-query over its reranked chunks (ADR-10). Output: per chunk `supports: bool`, and for the part `sufficient: bool` with `missing` (what the sources lack). It is told the tax year, so "the 2027 limit" isn't answered from 2025 figures (`G-I10`'s and `D53`'s trap). Model: gpt-4o-mini, as ADR-11 set for this call site; Haiku is the measured alternative only if the gate is wrong too often.
2. **Wiring in `decompose.answer`:** after `chunks()`, before synthesis. A part judged insufficient is dropped from the synthesis prompt and shown as "Part N: … INSUFFICIENT EVIDENCE: <missing>". All parts insufficient: **no synthesis call and no verifier call**, an immediate refusal (§9.3 H's 2 s refusal path). Client facts are never gated; an unrouted (fallback) plan is one part.
3. **`checking_sufficiency` stage** in the job stream between `retrieving` and `synthesizing`, with each part's verdict; recorded in the job.
4. **Fail open or closed?** If the gate's call fails, the part goes to synthesis as today, and F4 still verifies every sentence. *Default: fail open* (the gate saves work; the verifier is the guarantee). Recorded, yours to overrule.
5. **Measurement:** `temporal.py --rows every` (answerable and insufficiency rows); the job/`Answer` records each part's verdict so the eval can score the gate itself.

**Lean measurement (your call, 2026-09-30: reuse what exists, re-run only what a change touches):**
1. **Arm A on the 42 answerable rows is F4's shipped run:** `temporal-answers-f4-sentence.json` and its grades. No new run.
2. **Gate-only pass** (`temporal.py --gate-only`): plan, retrieval and the gate's verdicts for all 53 rows × 3 plan sets, no synthesis, no grading (~160 calls, ~$0.08).
3. **Full runs only where the gate can change the answer:** the 11 insufficiency rows (A with `--no-gate`, and G), and any answerable row-sample where the gate rejects a part (G, `--ids`). Every other answerable row-sample is identical in G by construction (same plan, same chunks, synthesis at temperature 0, same verifier), so A's grade stands for it.

**Two arms, on the same plans:**

| Arm | Pipeline |
|---|---|
| **A** | shipped (F3 synthesis + F4 sentence hiding), no gate |
| **G** | A + the gate |

| Metric | Rows | Why |
|---|---|---|
| **Correct refusals**: D43–D50 refused | 8 wholly insufficient rows | the gate's job |
| **Partial rows handled**: D51–D53 answer the answerable part (a cited sentence) *and* flag the other (INSUFFICIENT EVIDENCE or "Not in the sources" for it) | 3 partial rows | `G-I11`'s kind |
| **Wrong refusals**: an answerable row refused | 42 answerable rows | the gate's cost |
| Correct (the §9.2 judge against the reference) | all 53 | answer quality; on insufficiency rows the reference *is* the abstention |
| Sentences hidden, answers emptied (F4's metrics) | answerable rows | whether skipping up front leaves less to hide |
| Gate verdicts against row labels: abstention precision / recall per part | all | §9's abstention metric |
| Cost and latency per answer, and on the refusal path | all | §4.1, §9.3 H |

**Decision rule, fixed before any arm runs:**
0. **Sanity first (F3's and F4's lesson: test each metric on a known-good and a known-bad case before the arms run):** "correct refusal" counts a hand-made refusal of D43 as 1 and a cited answer to it as 0; "partial handled" counts a hand-made D51 answer with a cited federal sentence and a New Jersey INSUFFICIENT EVIDENCE line as handled, and the same answer without the line as not; "wrong refusal" counts a refusal of an answerable row and not a partial answer. If any check fails, the metric is fixed before measuring.
1. **Guard:** G's wrong refusals on the 42 answerable rows exceed A's by more than 0.05 → G is out.
2. **Guard:** G's correctness on the 42 answerable rows is more than 0.05 below A's → G is out. (Both arms are verified, so neither is credited for unsupported content: F4's trap doesn't apply.)
3. **G ships if it improves** correct refusals on D43–D50 **or** partial rows handled on D51–D53 by at least 3 of the 24 (resp. 9) row-samples, without making the other worse.
4. Otherwise A stays, and the finding is the report.

**Acceptance:**
- [ ] `sufficiency()` with tests (one call per part; schema; the year in the prompt; client facts never gated; all insufficient → no synthesis call; fail open)
- [ ] A `G-I11`-shaped test: a two-part plan, one part sufficient and one not → one answered part, one INSUFFICIENT EVIDENCE part, synthesis sees only the first (Phase B's "waiting test" doesn't exist in `tests/`; this adds it)
- [ ] `checking_sufficiency` in the job stream (test for its order and payload)
- [ ] Both arms measured on dev with the metrics above; the rule applied, sanity checks first
- [ ] Log entry

**Files:** `src/taxcite/decompose.py` (or new `sufficiency.py`), `generate.py` (render skipped parts), `jobs.py`, `eval/temporal.py` (`--rows every|insufficiency`, `--gate-only`, `--no-gate`, `--ids`), tests.

**Cost estimate:** gate calls ~$0.0005 a part on gpt-4o-mini. With the lean plan: the gate-only pass ~$0.08, 2 × 33 insufficiency row-samples and the changed answerable ones with synthesis, verification and grading: **about $1** (was ~$5). Golden untouched until F5.

**Out of F2:** rewriting failed sentences (F4's recorded next step); tuning the gate on golden (F5 scores it once).

**Built (2026-09-30):** `decompose.sufficiency()` (one gpt-4o-mini structured call per part, the tax year in the prompt, fails open), `gate()`, `GATE`; `generate.skipped_only()` and `answer_from_groups(skipped=)` (a skipped part is never in the prompt; it shows as INSUFFICIENT EVIDENCE after the answered parts); `jobs.run`'s `checking_sufficiency` stage and the refusal path (no synthesis, no verification); `temporal.py --rows every|insufficiency`, `--gate-only`, `--no-gate`, `--gate-prompt`, `--ids`. Tests: the gate's call and verdict, fail open, empty parts left to synthesis, **the G-I11 test** (the answerable part answered, the other never written), nothing answerable → no synthesis call, the job stream's refusal path. 287 tests.

**Results (2026-09-30), lean plan, ~$0.35 in all.** Gate-only passes over all 53 dev rows × 3 plan sets (~$0.10 each), the shipped pipeline's F4 run as the answerable baseline, and one baseline run on the 11 insufficiency rows.

| | strict gate | lenient gate | no gate (shipped) |
|---|---|---|---|
| Answerable row-samples refused before writing | **33 of 126** | **23 of 126** | (refused after writing: 9 of 126) |
| …of which the shipped pipeline got right, verified | 10 | **7** (D04 ×3, D21 ×3, D38) | — |
| D43–D50 (wholly insufficient) refused | 21 of 24 | 23 of 24 | 13 of 24 |
| D51–D53 (partial): the bad half alone skipped / handled | 8 of 9 | 6 of 9 | 6 of 9 handled |
| Correct on the 11 insufficiency rows | — | — | **0.818** |

**The rule:** guard 1 (wrong refusals on answerable rows no more than 0.05 above A's): G refuses at least 23/126 = 0.18 against 0.07, **so both gate prompts fail it, determined without a full gated run.** A stays: `GATE = False`, the code kept and tested. The gate's wrong refusals are the kind it was meant to avoid: D04's cited opinion holds the answer ("no clear conclusion"), D21's answer *is* that §1031 now covers only real property ("the sources don't cover equipment").

**What the shipped pipeline already does on insufficiency rows:** verified federal context plus a "Not in the sources" note (D45: §402(a) on 401(k) payouts, "Pennsylvania … not in the sources"), graded correct. The remaining misses aren't the gate's to fix: D52's federal half is emptied by the verifier (retrieval/support), and 11 of 24 wholly insufficient row-samples get context rather than a bare refusal, which the judge accepts.

**Decided (2026-09-30, your call): ADR-7/10 revised to "measured, not shipped".** ADR-7 and ADR-10 specify this gate. Measurement says it has no job the verifier doesn't already do, and does it worse. The intent rule is to drop an ADR'd component only on evidence and with your confirmation: revise ADR-7/10 to "measured, not shipped", or keep looking for a gate design.

## F3: Synthesis that cites every sentence, in sections

**Goal:** change what synthesis writes, so that F4's verifier has something to check and zero tolerance doesn't empty a fifth of answers. Measured on dev; golden is not touched until F5.

**Why (F0, golden, shipped pipeline):** 475 of 853 sentences carry no citation, and 132 of them come after the last citation, so they're conclusions nothing backs ("Thus, your client must recognize the full amount as income."). Of cited sentences, 14% say more than the source they cite (G-S14's 40% rate, G-S10's 750 hours). ADR-15 on today's answers would empty ~18% of answers, on top of 14% refusing. Rule 2 of `RAG_SYSTEM` asks only for "every sentence that states a rule" to be cited, so applications and conclusions go uncited by design.

**What changes:**
1. **Rule 2 becomes: every sentence carries a citation, and says only what that source says.** A sentence applying a rule to the client's facts cites the rule it applies; the question's facts need no citation (the verifier takes them as given, F0). A sentence that can't be cited isn't written. Wording is measured, not assumed (arms below).
2. **One section per searched sub-query** (the unit approved with the plan). `answer_from_groups` already groups sources by sub-query; the prompt numbers the parts and asks for one section per part, each self-contained (no conclusion that leans on another section, since F4 may hide one). A question with one searched sub-query gets one section and no heading. Client facts are never a section. `Answer` gains `sections: list[(label, text)]`, parsed from the section markers; `text` stays the whole answer, so the API and CLI keep working.
3. **Citation parsing fixed** (F0 found it): `parse_citations` misses nested brackets (`[26 U.S.C. § 3121(d)(1), [119 T.C. No. 5, at *7-8]]`) and several citations in one bracket (`[A; B]`). One shared `citations(text)` in `generate.py`, used by `parse_citations` and by the verifier's splitter later; unit tests for both shapes.
4. **The measurement tools read any answer cache.** `eval/f0_verify.py` gains `--answers` and `--questions` (today it is fixed to the golden E5 cache), so the same pairing and the fixed judge score dev arms. `eval/temporal.py --rows all` grades every answerable row, not only temporal or authority rows.

**Arms, on dev's 42 answerable rows (D43–D53 excluded: they're F2's), 3 samples each (answer i from plan set i, as E5):**

| Arm | Prompt | Synthesis model |
|---|---|---|
| A | shipped (ii′) | gpt-4o-mini |
| B | + rule 2 rewritten (every sentence cited, only what its source says) | gpt-4o-mini |
| C | B + one section per sub-query | gpt-4o-mini |
| D | C | claude-haiku-4-5 (ADR-11's revisit trigger: "move synthesis to Haiku if Phase F suppresses too much") |

**Metrics, per arm (all on dev):**
- **Citation completeness** = cited sentences ÷ all sentences (F0's splitter; §9.3's F gate is ≥0.85, scored on golden in F5).
- **Cited-source support** = share of cited sentences the fixed judge (F0) finds supported by their own citation (A's golden figure: 0.86).
- **Projected suppression** = share of answers F4 would empty, and of sections it would hide, under the judge's labels.
- **Faithfulness** (`ragas_eval.py`, 3 runs) and **refusal rate**; **correctness** (`temporal.py --rows all --samples 3`, §9.2's judge against the reference answer).
- Cost and latency per answer.

**Decision rule, fixed before any arm runs:**
1. Refusal rate no more than A's + 0.05, and correctness no lower than A's − 0.05 (one sample-noise band, E5). An arm failing either is out.
2. Of the rest, the arm with the lowest projected answers emptied wins, if it beats A by ≥5 points; within 2 points of each other, the cheaper arm.
3. D (Haiku) is taken only if it wins rule 2 by ≥5 points over C, since it's ~7× the synthesis cost. The ADR-11 revision it would trigger is written then.
4. If no arm reaches completeness ≥0.85 on dev, say so plainly: F5's gate is then at risk, reported, not lowered.

**Also measured, not decided on:** how many sentences still trail the last citation; whether sectioning costs correctness on compound rows (reported per category); the wrong-page rate (28 of 168 on golden in F0).

**Acceptance:**
- [ ] Tests for `citations()` (nested, multi-citation, plain) and for section parsing (one section, several, missing markers → one section holding the whole text)
- [ ] All four arms measured on dev with the metrics above, in a results note
- [ ] One arm shipped by the rule (or a recorded departure, as E5's), in `generate.py`
- [ ] Faithfulness CI gate still green locally on golden (CI's command) with the shipped arm
- [ ] Log entry

**Files:** `src/taxcite/generate.py` (rule 2, sections, `citations()`), `src/taxcite/decompose.py` (numbered parts in the synthesis call), tests, `eval/f0_verify.py`, `eval/temporal.py`, `eval/ragas_eval.py` (`--prompt` arms). New files, if any, handed to you as code.

**Cost estimate:** synthesis 4 arms × 42 rows × 3 samples: ~$0.30 on gpt-4o-mini, ~$1.50 for the Haiku arm; judges (support, faithfulness, correctness): ~$4. **About $6 in all.** *Corrected when building (2026-09-30): ~$12. Correctness runs two judges and a grounding check per answer (~$1.5–2.5 an arm), faithfulness makes its own answers per arm, and the support judge runs two passes.*

**Built (2026-09-30), before any arm ran:** `generate.citations()` (nested and packed brackets; `parse_citations` uses it), `split_sections()` and `Answer.sections`, `RULE_2_EVERY`, `SECTIONS_RULE` and the `SECTIONS` switch (numbered parts in `answer_from_groups`; an empty group isn't a part); `ragas_eval --prompt f3-cite|f3-sections` built on the shipped prompt; `--synth-model` in `ragas_eval.py` and `temporal.py` (synthesis only; plans pinned); `temporal.py --rows all`; `f0_verify.py --answers/--questions/--tag` (it now uses `generate.citations`; F0's report reproduces exactly). 4 new tests; 262 pass.

**Risks:** citing every sentence may make answers stiffer or longer (watch length and correctness), or push the model to refuse more (rule 1 catches it). Sections may repeat context across parts (watch length). A sentence can carry a citation and still say more than its source: that's F4's job, and exactly what support measures.

**Results (2026-09-30), dev's 42 answerable rows × 3 samples; ~$8.70 in all.** Files: `eval/results/temporal-dev-2026-09-30-f3{a,b,c,d}.json`, `f0-report-f3-dev-{a,b,c,d}.json`, answer caches `temporal-answers-f3*.json`, `ragas-answers-f3*.json`.

| Arm | Correct (3 samples) | Refused | Faithfulness | Support (cited sentence backed by its source) | Completeness, as registered | Completeness, material sentences only | Answers every sentence cited *and* supported | Answers emptied (registered metric) | Words |
|---|---|---|---|---|---|---|---|---|---|
| A shipped | 0.373 ± 0.014 | 0.095 | 0.839 ± 0.037 | 0.752 | 0.356 | 0.438 | 0.032 | **0.295** | 101 |
| B cite every sentence | 0.310 ± 0.041 | 0.111 | 0.841 ± 0.015 | 0.766 | 0.486 | 0.598 | 0.120 | 0.370 | 106 |
| C B + sections | 0.349 ± 0.036 | 0.079 | 0.841 ± 0.041 | 0.800 | 0.471 | 0.607 | 0.078 | 0.353 | 119 |
| D C on Haiku | 0.405 ± 0.024 | **0.206** | 0.874 ± 0.031 (refusals 0.19) | 0.863 | 0.540 | 0.714 | 0.120 | 0.370 | 165 |

**The rule, applied as written:** (1) B fails the correctness guard (0.310 < 0.373 − 0.05); D fails the refusal guard (0.206 > 0.095 + 0.05). (2) C passes both guards but empties *more* answers than A (0.353 vs 0.295), so no arm beats A: **by the rule, nothing ships; A stays.** (4) No arm reaches completeness 0.85 (best 0.71): **F5's completeness gate is at risk**, reported, not lowered.

**The registered metric has the same blind spot E5's rule 3 had.** "Answers emptied" counts only *cited* sentences that fail; an uncited sentence is never checked, so an arm that cites more exposes more sentences and looks worse. Counting an uncited material sentence as unverified (it can't be shown under ADR-15 either), the share of answers that survive whole is A 3%, B 12%, C 8%, D 12%. Recorded here as a finding, not used to override the rule.

**Measurement correction (post hoc, disclosed):** F0's splitter counted structural lines as uncited sentences: section headings (71 in C), the year statement rule 6 requires ("The year I answer for is 2026.", 59 in C), and markdown titles ("**Conclusion**"). §9's completeness is over *material* claims, so the "material sentences only" column excludes them. It moves every arm up ~0.08–0.17 and changes no ranking.

**What the uncited sentences are (C, D):** applications and arithmetic on the question's facts ("Since your client's gain is $200,000 … she can exclude all $200,000"), and plain restatements of a rule the previous sentence cited. The prompt asks for a citation on each; the models write most, not all.

**Conclusion:** prompting moves completeness from 0.44 to 0.60–0.71 but cannot reach 0.85, and under zero tolerance almost no answer survives whole (≤12%). The lever left is structural: synthesis returns sentences as objects with a required `citations` field (JSON schema), so an uncited sentence can't be written, and the verifier checks every one. Proposed as arm E, measured by the same rule plus the fully-verified share. Decision for you.

**Arm E, structured synthesis (2026-09-30, your go; ~$1.40).** `STRUCTURED` in `generate.py`: JSON items, one sentence each with citations from an enum of the retrieved sources (none can be invented); an uncited item is dropped, an unanswerable part renders as INSUFFICIENT EVIDENCE; an unusable response is a refusal. OpenAI strict structured outputs added to `call_model`. `f0_verify.py`'s report now carries `completeness_material` and `answers_fully_verified` (reproduces the table above exactly). 266 tests.

| Arm | Correct | Refused (as detected) | Pure refusals (no cited sentence) | Completeness, material | Support | **Answers fully verified** | Answers emptied (registered) | Sections hidden | Words |
|---|---|---|---|---|---|---|---|---|---|
| A shipped | 0.373 ± 0.014 | 0.095 | 9 of 126 | 0.438 | 0.752 | 0.032 | 0.295 | 0.342 | 101 |
| C cite + sections | 0.349 ± 0.036 | 0.079 | — | 0.607 | 0.800 | 0.078 | 0.353 | 0.397 | 119 |
| D C on Haiku | 0.405 ± 0.024 | 0.206 | — | 0.714 | 0.863 | 0.120 | 0.370 | 0.387 | 165 |
| **E structured** | 0.341 ± 0.014 | **0.460** | **0 of 126** | **1.000** | 0.716 | **0.414** | 0.569 | 0.565 | 127 |

Faithfulness E: 0.692 ± 0.058, but over only 12–14 of 25 rows (the harness drops "refused" rows), so not comparable.

**The rule, as written:** E fails the refusal guard (0.460 > 0.145). **But every one of E's 58 "refusals" is a full cited answer with an INSUFFICIENT EVIDENCE caveat appended** for a detail the sources lack (D51: "2026 phase-out thresholds are not provided"); `Answer.refused` matches the phrase anywhere. E's pure refusals are 0 against A's 9. With refusals counted as answers with no cited sentence, E passes both guards (correct 0.341 ≥ 0.323) and then loses rule 2 on "answers emptied" (0.569 vs 0.295), the metric already shown blind to uncited sentences. **By the rule as written, nothing ships; the two measurement flaws both work against E.**

**What E shows:**
1. Completeness 1.000 by construction; fully verified answers 41% against ≤12% for every prompt arm.
2. Support falls to 0.716: sentences that other arms left uncited are now cited, and many don't hold (D51: "New Jersey does not conform … [IRS Pub 17 (2025), p. 71]"). The misattribution was always there; E makes it checkable.
3. Under section-level zero tolerance, E would hide 56% of sections. The unit ADR-15 hides is F4's question, raised now: hiding the failing *sentence* keeps ADR-15's promise (no unverified claim shown) and loses far less.
4. The caveat habit is noise for users (46% of answers end in INSUFFICIENT EVIDENCE for a detail).

**Arm E′: E with your two fixes, re-measured (2026-09-30, your decision "adopt E with the two fixes").** (1) A detail missing from an answered part renders as "Not in the sources: …", not INSUFFICIENT EVIDENCE; a part with nothing answered still says INSUFFICIENT EVIDENCE. (2) `Answer.refused` = says INSUFFICIENT EVIDENCE *and cites nothing* (was: the phrase anywhere). `f0_verify` recomputes it from the text, and counts "Not in the sources" / INSUFFICIENT EVIDENCE lines as non-material.

| | A (pre-F3) | E′ (ships) |
|---|---|---|
| Correct (3 samples) | 0.373 ± 0.014 | **0.373 ± 0.037** |
| Refused / pure refusals | 0.095 / 9 of 126 | **0.000 / 0** |
| Completeness, material | 0.438 | **1.000** (12 uncited sentences dropped in 126 answers) |
| Support (cited sentence backed by its source) | 0.752 | **0.769** |
| **Answers fully verified** | 0.032 | **0.523** |
| Sections hidden under section-level zero tolerance | 0.342 | 0.442 |
| Faithfulness, as the CI gate judges (question hidden) | 0.839 ± 0.037 | 0.777 ± 0.028 |
| Faithfulness, question as a source | 0.859 ± 0.007 | **0.864 ± 0.025** |

**The faithfulness drop is the gate's judge, not E.** None of E′'s 73 unsupported claims is a "not in the sources" note; many are the client's own facts, which E now writes out in its application sentences ("The client owned and lived in the house for 3 of the last 5 years"), and the gate's judge never sees the question (F0's blind spot, in the other judge). With the question as a source (`ragas_eval.py --question-as-source`, as `temporal.py`'s grounding check already does), E′ equals A.

**Shipped (2026-09-30): arm E′ is the default** (`STRUCTURED = True`; (ii′) kept as `PRE_F3_SYSTEM` and eval arm `pre-f3`), recorded as a departure from F3's pre-registered rule, whose two metrics both worked against it. Every non-shipped eval arm now sets both F3 switches, so an E5 arm can't run structured by accident. 268 tests.

**Golden faithfulness gate with E′ (2026-09-30, CI's command, 5 runs, ~$6 with the rerun).** As CI judges (question hidden): **0.838 ± 0.006, FAIL** (< 0.855). With the question as a source: **0.869 ± 0.006, PASS**. Refusal rate 0.002 (Phase E's shipped build: 0.113), well inside the 0.25 bound. So on golden, as on dev, E′ fails the gate only through the judge's blind spot. Caveats: (a) the pre-F3 build has not been judged with the question on golden, so "E′ equals pre-F3" is shown on dev only (0.864 vs 0.859); (b) E′ answers the ~11% of rows pre-F3 refused, and those are scored now. The first attempt hung for an hour on a dead connection after the laptop slept; `call_model` now gives both SDKs a 2-minute timeout (`API_TIMEOUT`).

**Decision needed (not taken):** shipping E′ needs the gate's judge to see the question. That changes the gate's definition, so the standing rule (re-measure both bands with ≥5 samples after a pipeline change) is now due; you deferred it "until required" on 2026-09-29.

**Gate decision (2026-09-30, your option 1), bands re-measured as the standing rule requires (~$5.50).** Golden, judge shown the question, 5 runs each: pre-F3 0.920 ± 0.012 (refusing ~12%); shipped E′ **0.869 ± 0.006**; E′ with the grounding rule removed (`--prompt broken`, B9's arm rebuilt) **0.870 ± 0.019**. On the 81 rows pre-F3 answered in every run: pre-F3 0.919, E′ 0.899, broken 0.898; E′ scores 0.707 on the 15 rows pre-F3 refused. So E′ costs ~0.02 faithfulness like-for-like, and **the gate can no longer detect B9's regression: under structured synthesis the grounding rule does almost nothing the structure doesn't.** Done: `faithfulness.yml` runs with `--question-as-source` at 0.855 as a floor; ADR-22 revised; §9.3 row noted. **Moved to F5:** calibrate F4's verifier against a seeded failure (e.g., the verifier off, or `broken`), since it is now the detector.

**F3 acceptance:**
- [x] Tests for `citations()` and section parsing (and structured rendering, the schema, OpenAI strict outputs, the broken arm, refusals): 269 pass
- [x] Four arms (+ E, E′) measured on dev, results above
- [x] One arm shipped: E′, by your decision, a recorded departure from the rule (both of its metrics worked against E)
- [x] Faithfulness gate on golden with the shipped arm, CI's command: 0.869 ± 0.006 with the question shown (the gate's new definition), PASS; refusals 0.002
- [x] Log entries #82, #83 (local; `docs/` is gitignored)

## F4: The verifier, and hiding what fails

**Goal:** after synthesis, check every sentence of the answer against the sources it cites, and never show one that fails (ADR-3, ADR-15). Since F3 this is also the pipeline's regression detector: the weekly faithfulness gate became a floor (ADR-22 revised).

**Decided already (Checkpoint 1, F0, F3):**
- **An LLM verifier, not NLI** (ADR-4 revised): one batched structured-output call per answer, Haiku (the other provider from synthesis, ADR-11). ~$0.0023 an answer, a few seconds.
- **The judge prompt is F0's fixed one** (V2b): the question and the whole answer as context, the question's client facts taken as given, cited sources judged together, every assertion must hold. Measured: 15/16 on single sentences against a careful read.
- **The unit is the sentence,** and since F3 each sentence is a JSON item with its citations, so no splitting is needed: the verifier reads the items directly.
- **A cited opinion counts with every retrieved page of it** (your pinpoint policy); whether the cited page itself holds the claim is recorded apart (`pinpoint`), not hidden.

**What changes:**
1. **`src/taxcite/verify.py` (new file, handed to you as code).** `verify(question, answer) -> list[Verdict]`: one call over all of an answer's sentences, each with its cited chunks (plus the other retrieved pages of a cited opinion); returns supported / not, which source carried it, and a short reason. The prompt moves here from `eval/f0_verify.py`, which then imports it, so the eval and the product judge the same way.
2. **`Answer.items`:** `render()` keeps the (part, sentence, citations) items it rendered from, so the verifier needs no re-parsing.
3. **Hiding** (`apply(answer, verdicts, unit)`): a failed sentence is never shown. What else goes with it is the open question below. A part left with nothing shown says INSUFFICIENT EVIDENCE for that part. The shown text is re-rendered from the surviving items; `Answer` records what was hidden and why (for the eval and the log, not the user).
4. **Fail closed:** if the verifier call fails or returns nothing usable, nothing unverified is shown: the answer becomes "INSUFFICIENT EVIDENCE: the answer could not be verified", and the job record says why.
5. **Wiring:** `decompose.answer` (so every eval measures the verified pipeline; `--no-verify` keeps the unverified arm), and `jobs.run` with a `verifying` SSE stage between `synthesizing` and `answer`; the answer stays buffered until verification ends (ADR-9).

**Decision to make on dev (it revises ADR-15 if S wins): what does one failed sentence take down with it?**

| Arm | Hides | For | Against |
|---|---|---|---|
| **P** (ADR-15 as written) | the whole part (section) | nothing shown can depend on a hidden sentence | on F3's dev answers, ~44% of sections would go |
| **S** | only the failing sentence | keeps ADR-15's promise (no unverified claim shown) and hides ~23% of sentences | a surviving sentence can lose its qualifier ("unless…" hidden), so the shown answer can be verified sentence by sentence and still wrong |

**Measured on the shipped E′ dev answers (126 cached answers, 3 samples × 42 rows; no new synthesis):**
- share of sentences hidden; answers shown whole; answers with at least one part shown; answers emptied;
- **correctness of what is shown** (`temporal.py`'s judge on the verified text): the check that hiding a sentence didn't make an answer wrong;
- hidden sentences the verifier got right: a fresh hand-read sample of ~30 verdicts on E′ answers (F0's sample was on pre-F3 answers), stratified hidden/kept;
- verifier latency and cost per answer.

**Decision rule, fixed before any arm runs (F3's lesson: each metric is first run on a known-good and a known-bad case):**
0. *Sanity, before measuring:* on a hand-made answer with one fabricated sentence (a real citation on a claim its source doesn't make), both arms hide it and keep the rest as defined; on an all-supported answer, neither hides anything. If either fails, the metric or the code is fixed first.
1. An arm whose shown answers are less correct than the unverified E′ answers by more than 0.05 is out.
2. Of the rest, the arm with more answers showing at least one part wins; within 2 points, P (the ADR as written).

**Acceptance:**
- [ ] `verify.py` with tests (batching, fail-closed, one fabricated sentence hidden, opinion pages, the prompt's context), the prompt shared with `f0_verify.py`
- [ ] `verifying` stage in the job stream; tests for its order and for a fail-closed answer
- [ ] Both arms measured on dev with the metrics above; the rule applied; ADR-15 revised if S ships
- [ ] Hand-read sample of ~30 E′ verdicts, agreement recorded
- [ ] Latency and cost per answer recorded (against §9.3 H's 35 s p95)
- [ ] Log entry

**Files:** `src/taxcite/verify.py` (new), `generate.py` (`items`), `decompose.py`, `jobs.py`, `eval/f0_verify.py` (shared prompt), `eval/ragas_eval.py` / `temporal.py` (`--no-verify`), tests.

**Cost estimate:** verifier over 126 cached answers ~$0.30; grading the two arms' shown answers ~$2; a hand sample. **About $3.** Nothing touches golden until F5.

**Out of F4:** the golden audit against an independent model and the verifier's calibration against a seeded failure (both F5); re-pointing a wrong-page citation to the page that holds the claim (recorded, not built).

**Built (2026-09-30):** `verify.py` (new; developed outside the repo, handed to you with its tests): F0's validated prompt, one batched call per answer, cited chunks plus every retrieved page of a cited opinion, a skipped verdict counts as a failure, `apply(unit)`, fail closed (`UNVERIFIED`). `generate.cited_items()` so render and verifier number sentences alike; `Answer.structured / hidden / verdicts / verifier` and the verifier's cost in `cost_usd`. `decompose.VERIFY`; `jobs.run` publishes `verifying` and `hidden_sentences`, and a failed verifier sends a refusal, never the unverified text (test). Eval: `--no-verify`, `--hide`, verdicts cached; `eval/f4_hide.py` (new) shows one verified run three ways on identical verdicts. 278 tests with the new files.

**Results (2026-09-30), dev, 42 rows × 3 samples, one synthesis and one verification per answer, ~$3.40:**

| Arm | Sentences hidden | Answers shown whole | Answers with a part shown | Emptied | Correct | Incorrect | Refused | Grounded | Correct *and* grounded |
|---|---|---|---|---|---|---|---|---|---|
| none (unverified) | 0 of 449 | 126 | 126 | 0 | **0.365** ± 0.037 | 0.143 | 0.000 | 0.571 | 0.238 |
| **S** (the failing sentence) | 109 (24%) | 60 | **117** | 9 | 0.278 ± 0.028 | 0.214 | 0.071 | 0.865 | 0.214 |
| **P** (its whole part) | 250 (56%) | 60 | 62 | 64 | 0.206 ± 0.014 | 0.556 | 0.508 | 0.944 | 0.190 |

Verifier: ~$0.002 and a few seconds an answer. Verdict check (Claude's read, 30 stratified): **27 of 30 agree**; 2 hidden that a careful read keeps (V07, V22: fair paraphrases), 1 kept that should go (V28: "rental income" where the statute says AGI). What it hides is mostly real: wrong section cited (§179D for a §25C credit, §263A(h) for §262, §79 for §72), arithmetic ignoring "or fraction thereof", figures the cited page doesn't give.

**The rule, as written: neither arm ships.** Rule 1 (shown answers no more than 0.05 less correct than unverified, i.e. ≥ 0.315): S 0.278 and P 0.206 both fail. Rule 0's sanity cases passed (tests).

**What the drop is made of (S vs none, 126 answers):** correct → partial 10 (content hidden, answer less complete); partial or correct → incorrect 11, of which **9 are refusals** (every sentence failed; the correctness judge grades INSUFFICIENT EVIDENCE as incorrect); 3 real. Correct-and-grounded barely moves (0.238 → 0.214): most of what verification removes was right only from the model's memory, which the unverified baseline credits. The risk rule 1 targets is real but small: D30 s0 lost its conclusion ("cannot deduct for 2024") and kept only "governed by § 225(a)-(f)".

**Third pre-registered rule in this phase to measure something in tension with its purpose:** rule 1 benchmarks against an unverified answer, so any verifier that removes unsupported-but-correct content fails it by construction. Recorded; the decision is yours.

**Shipped (2026-09-30, your decision): S, the failing sentence only** (`verify.HIDE = "sentence"`), a recorded departure from F4's rule; ADR-15 revised with the numbers above. Recorded next step, not built: rewrite failed sentences once from the verifier's reasons (the D30 risk, and the correctness cost).

**F4 acceptance:**
- [x] `verify.py` with tests (batching, fail closed, one fabricated sentence hidden, opinion pages, the prompt's context, the shipped unit): 9 tests
- [x] `verifying` stage in the job stream; a failed verifier sends a refusal (test)
- [x] Both arms measured on dev; the rule applied (neither passed); S shipped by your decision; ADR-15 revised
- [x] Verdict check: 27 of 30 (Claude's read), `eval/results/f4-verdict-check.md`
- [x] Cost ~$0.002 and a few seconds an answer; the §9.3 H latency figure is F5's (p95 over golden)
- [x] Log entry #84 (local)
- [x] `src/taxcite/verify.py`, `tests/test_verify.py`, `eval/f4_hide.py` created by you; `eval/f0_verify.py` imports the product's prompt (checked identical to F0's); committed `8193fb8`

## F5: Phase F scored on golden

**Goal:** score the finished Phase F pipeline on golden, once, against §9.3's gates as revised: structured synthesis (F3), the verifier hiding failed sentences (F4), no sufficiency gate (F2). Nothing is tuned on golden; every number below is reported as it comes out.

**The gates (§9.3, revised at Checkpoint 1):**

| Gate | Threshold | Scored as |
|---|---|---|
| Citation entailment F1 | ≥ 0.90 | the runtime verifier (Haiku) against an **independent reference** on golden's sentences, "not supported" class, false-accept rate beside it |
| Citation completeness | ≥ 0.85 | material sentences cited ÷ material sentences (`completeness_material`), before hiding and as shown |
| Substantive correctness | tracked, not gated (N < 100) | §9.2's judge on the 40-question subset, two judges, κ reported (≥ 0.7 to be trusted) |

**The independent reference (Checkpoint 1: the verifier can't grade itself):** a different, stronger model judging the same pairs with the same prompt, its price confirmed before the run. Candidate: the current Sonnet. That reference is itself checked on ~40 stratified pairs read by hand (as F0 and F4 did), and F1 is reported against both the reference and the hand-read pairs.

**One golden run, reused for everything (the lean rule):** golden's 104 non-adversarial rows (93 answerable + 11 insufficiency) × 3 plan sets, shipped pipeline, through `temporal.py --rows every`, storing structured items, verdicts and per-answer latency. From that single run:
1. **Entailment:** the verifier's verdicts are already in the cache; only the reference judge runs over the same pairs (and the hand-read sample).
2. **Completeness:** computed from the cached items, no calls.
3. **Correctness:** `temporal.py`'s grades from the same run; the 40-question subset and κ read from them.
4. **The ladder's last rung, "+claim verification":** `f4_hide.py` shows the same answers unverified and verified on identical verdicts; graded once more (the unverified view only).
5. **Abstention (§9):** the 11 `G-I` rows: refusals, partial handling (`G-I11`, now with `parts`), and `G-I06`, answered from nothing in every run since Phase B.
6. **Operations (§9.3 H, first look):** p50/p95 latency and cost per answer, synthesis path and refusal path.

**Seeded failure, the detector's calibration (moved here from F3, since the faithfulness gate became a floor):** take verified golden answers whose sentences all passed and swap citations between sentences (each sentence now cites a source that doesn't make it). The verifier must hide them. Reported: the share caught (recall) on ~100 seeded sentences, and the share of untouched sentences still kept. Only verifier calls, no synthesis.

**CI on the finished pipeline:** push `phase-f`, dispatch the weekly faithfulness workflow (question shown, 0.855 floor) and the retrieval gate; record both runs. Not counted in this brief's cost (CI's own budget, ~$3).

**Pre-registered:** the thresholds above are §9.3's, unchanged. A gate not met is reported as not met, with what it would take, as Phases D and E did. Before the run, each new metric is checked on a hand-made right and wrong case (the seeded-failure scorer, the abstention scorer, completeness on a shown answer).

**Acceptance:**
- [ ] Reference judge chosen, priced, and checked on a hand-read sample
- [ ] Entailment F1 and false-accept rate on golden (against the reference and against the hand-read pairs)
- [ ] Completeness on golden, before hiding and as shown
- [ ] Correctness on the 40-question subset, κ between two judges
- [ ] Abstention on the G-I rows, incl. `G-I06` and `G-I11`
- [ ] "+claim verification" on the ablation ladder
- [ ] Seeded-failure recall
- [ ] Latency p50/p95 and cost per answer
- [ ] CI runs on `phase-f` recorded
- [ ] Results note in `eval/results/` and a log entry

**Cost estimate:** golden run ~312 answers × ~$0.0035 (synthesis + verification) ≈ $1.10; correctness grading ≈ $2.20; the unverified view's grading ≈ $2.20; reference judge over ~1,100 sentence pairs ≈ $2–4 depending on the model's price; seeded failure ≈ $0.30. **About $8–10**, the phase's one golden scoring. Golden is run once; any re-run needs your go.

**Results (2026-10-01), golden, scored once: 108 rows × 3 plan sets, shipped pipeline (F3 structured synthesis, F4 sentence hiding, no gate). ~$8.30, plus ~$1.70 of grades lost when Anthropic credit ran out at row 254 (now checkpointed per row).**

| Gate / metric | Result | Threshold | |
|---|---|---|---|
| **Citation entailment F1** (verifier vs Sonnet 5.5, 298 sentences, plan set 0, "not supported" class) | **0.63** (precision 0.90, recall 0.48, false accepts 0.52) | ≥ 0.90 | **not met** |
| …adjusted by a careful read of 40 disagreements (Sonnet right in 27, the verifier in 13) | **≈ 0.72** (precision ≈ 0.93, recall ≈ 0.59) | ≥ 0.90 | **not met** |
| **Citation completeness**, material sentences | **0.996** before hiding, 0.995 as shown | ≥ 0.85 | **met** |
| Correctness, answerable rows (n = 291) | 0.241 correct, 0.478 partial, 0.282 incorrect; κ between the two judges 0.80 (trusted) | tracked | |
| Seeded misattributions caught (citation moved to another section's retrieved source) | **77 of 102 (0.755)** | — | |
| Abstention, 11 G-I rows × 3 | 9 of 10 wholly insufficient refused 3/3; **`G-I06` answered 3/3** (since Phase B); `G-I10` refused 1, flagged 2; **`G-I11` refused 3/3** (its federal half not answered) | — | |
| Insufficiency rows correct | 0.818 | — | |
| Latency (first answer excluded) | answered p50 8.0 s, p95 11.2 s; refused p50 2.7 s, p95 6.2 s | 35 s / 2 s (H, first pass) | answered met; refusal path not |
| Cost per answer | $0.0039 (planning, synthesis, verification) | — | |

**Ladder, "+claim verification"** (same answers, verifier on vs off): correct 0.247 → 0.241, grounded 0.793 → 0.901, correct *and* grounded 0.253 → 0.275, refused 0.207 → 0.237. On golden, verification costs no measurable correctness (dev, F4: 0.365 → 0.278); 134 of 913 sentences hidden, 9 answers emptied.

**What the verifier misses:** sentences that overstate or over-generalise their source, i.e. a dropped condition or carve-out ("§ 280A disallows" where it limits; § 6013(b)(4)'s extra year for any joint return; "gross income" where § 1402(b) says net earnings; American Eagle coins as collectibles, which § 408(m)(3) excepts; § 469(c)(7) read as "not passive" without material participation). The F0 prompt's "every assertion must hold" rule is in; Haiku applies it loosely.

**A regression signal, not yet confirmed: correctness on golden's 32 authority rows fell from 0.369 (Phase E, ii′, 5 samples) to 0.260 (F5, verified and unverified alike, 3 samples).** Verification isn't the cause (both views 0.260); F3's structured synthesis is the likely one, though on dev it cost nothing (0.373 vs 0.373). Confirming it means running the pre-F3 pipeline on those 32 golden rows (~$1): a diagnosis, not tuning, but golden, so it waits for you.

**F5 regression diagnostic (2026-10-01, your go, $0.59 judge + synthesis):** the Phase E prompt (`--prompt pre-f3 --no-verify`) on golden's 32 authority rows, same pinned plans and judge, 3 samples: **correct 0.365** (structured E′ unverified: 0.260; Phase E's own run, samples 0-2: 0.396). Confirmed: F3's structured synthesis costs ~0.10 correctness on golden, not verification. 20 row-samples lost, 10 won; 15 of the 20 lost became "partial: missing condition", only 3 via refusal. Cause seen in the answers: structured answers almost never state the bottom line (4 of 324 open with Yes/No vs 35 of 96 for the old prompt); they list cited facts per sub-query and leave the conclusion to the reader. Dev missed it (0.373 = 0.373). Results `temporal-golden-2026-10-01-f5-pref3.json`.

**Bottom-line fix (2026-10-01, your go for recommendation A), measured on dev, not shipped:** a required part-0 item, one cited sentence answering the question directly, shown first (`generate.BOTTOM_LINE_RULE`). Dev, 42 answerable rows × 3, verified, gate off: **correct 0.238 vs 0.278** (F4's shipped run), incorrect 0.302 vs 0.214, refused 0.095. The model commits to a Yes/No that is often wrong, and the verifier hid 50 of 126 bottom lines. `BOTTOM_LINE = False`; the golden confirmation run was not made, since dev failed. **Correction (same day):** paired, it lost 14 row-samples and won 9 (sign test p ≈ 0.4): inconclusive, not a measured loss. The bottom line was generated before the evidence (schema order), which F5b's C1 changes. Judge spend $0.96 (one run wasted by the bug below).

**Harness bug found (2026-10-01): every eval run since F2 ran the sufficiency gate,** which ships off. `set_verify()` set `GATE = not no_gate`, so the gate was on unless `--no-gate` was passed; `ragas_eval.py` (which CI runs) never passed it. Affected: all F5 golden figures (the gate refused 67 of 324 answers before they were written, verified and unverified alike), the pre-F3 diagnostic (6 of 96), and this dev run's first pass. Not affected: F2's measurements (gate on purpose, `--no-gate` arm) and everything before F2. Fixed: `set_verify(gate=None)` keeps what ships; `temporal.py --gate/--no-gate`. Dev re-run lean: only the 54 answers the gate touched were regenerated and re-graded (`ungate.py`, scratch), and the 72 untouched kept their grades. **F5's golden correctness, refusal, latency and G-I06/G-I11 figures need the same correction before F6.**

## F5b: answers that conclude and can be checked (plan: `tasks/plan.md`, F5b)

- [x] Step 0.2 guard test: eval switches leave the gate as shipped (fails 3× on the buggy version)
- [x] Step 0.3 `judge(..., why=True)` for diagnostic re-grades (scoring rubric unchanged)
- [x] Step 1 diagnose (free): 37 hidden sentences tagged; retrieval is the largest cause; C6 sibling expansion measured free: dev Recall@8 0.610 → 0.683 (+4/−1 rows); false accepts not concentrated in applications (results in `tasks/plan.md`, F5b)
- [ ] Metric checks on hand-made cases (conclusion shown, correct ∧ grounded)
- [x] R1: C6 siblings + shipped synthesis and verifier on dev ($0.46 judge + ~$0.3 synthesis/verification; 90 of 126 row-samples changed sources and were re-run, 36 kept F4's answers and grades). Paired vs F4, answered (not refused) only: correct ∧ grounded 27 → 25 (lost 8, gained 6, noise); incorrect 18 → 11; ungrounded 17 → 5 (p≈0.01); **refusals 9 → 22** (p<0.01): 12 of the 14 new ones are answers the verifier emptied, e.g. D25 (the right regulation, 1.401(a)(9)-2(a)(2), now retrieved but a neighbour cited), D26 (siblings pushed § 163(h)(3) out of 8th, as predicted), D30 (the start date isn't in the corpus: an honest refusal). Fails criterion 4 alone; R2 adds C3 on R1's retrieval. **Metric flaw found:** the grader marks some refusals "correct" (6 of 22 here; 25 of 77 on F5 golden, partly the insufficiency rows, where that's right); on answerable rows the decision metrics now count answered rows only.
- [x] R2 built (free), off by default: `generate.CONCLUSION` (C1: `conclusion` last in the schema; C4: self-contained items), `verify.RECITE` (C3: one call over every retrieved source for failed sentences only; each swap re-checked by the unchanged F0 prompt, text never rewritten), the conclusion check (C2: follows from the sentences that passed plus the client's facts; shown first as "Short answer:", cited with its basis sentences' citations; no check when nothing passed). The verifier's validated prompt is untouched, so criterion 5 can't move. Part-0 bottom line removed. `temporal.py --conclusion --recite --siblings 6`. 295 tests.
- [x] R2 run on dev (your go; judge $0.80 + pipeline $0.82): siblings 6 + C1–C4. Paired vs F4, answered rows: **correct ∧ grounded 27 → 35** (gained 15, lost 7, p≈0.13); correct 35 → 37; incorrect 18 → 17; refusals 9 → 15 (new: 4 replaced ungrounded answers, 3 are D26's sibling crowd-out, 1 cost a correct grounded answer, D31). Conclusion shown on 83 of 111 answered (75%); 26 rejected by the check, mostly rightly (D13 "entire $200,000" without the cap shown; D18 "10% applies" without the exceptions ruled out), a few strict (D05). 15 sentences re-cited. Ungrounded answers: 16 of 17 for ordinary claims, 1 for its conclusion alone. Pipeline $0.0065 an answer (F4: ~$0.004), p50 8.0 s / p95 13.2 s. Completeness 1.0 by construction (the conclusion carries its basis sentences' citations). Verifier prompt unchanged (criterion 5).
  **Against the pre-registered rules:** 2 (correct ∧ grounded) ✓, 3 (incorrect) ✓, 5 ✓; **1 missed** (75% < 80%: the check rejecting overreaching conclusions, which is its job); **4 missed** (refusals +6; but only 1 replaced a correct grounded answer — "refusals not higher" counts honest refusals of memory answers as a cost, the F3 metric lesson again). Your decision.
- [ ] R3 only if R2 misses one criterion with a clear cause
- [x] **R2 ships (your decision 2026-10-01, a recorded departure from criteria 1 and 4):** `SIBLINGS = 6`, `CONCLUSION = True`, `RECITE = True`; a test pins them. `f5_golden.py --cache --prefix` so F5b's outputs don't overwrite F5's. Seeded and Sonnet-audit steps not re-run (the verifier's prompt is unchanged; F5's sentence-level results stand); conclusions and re-cited sentences read by Claude instead (free).
- [x] **Golden once, shipped pipeline, gate fixed (2026-10-01; judge $2.19 + pipeline ~$2.38).** Replaces F5's gate-contaminated figures. Answerable rows (291 row-samples): correct 0.368; answered and correct 0.364; **answered, correct and grounded 0.333**; incorrect 0.137; partial 0.454; refused 13. By category correct: statutory 0.488, case law 0.481, compound 0.247, temporal 0.121. **The 32 authority rows vs Phase E (samples 0–2): correct 0.396 → 0.469, answered correct ∧ grounded 0.312 → 0.385, grounded 0.635 → 0.875** (F5's "regression" reversed). Completeness 0.994 as shown (met). Short answer shown on 231 of 278 answered (83%). 34 sentences re-cited; 210 of 1,160 hidden; 13 answers emptied. Latency p50 8.3 s / p95 11.8 s; $0.0073 an answer. Insufficiency rows: refused or flagged on G-I01/02/04/05/07/10, G-I11 handled 3/3 (partial row, now answers its federal half), answered: G-I06 3/3, G-I09 3/3, G-I03 2/3, G-I08 1/3 (no gate; F2's measured choice).
  Siblings on golden: 54 gold sources gained across 18 rows, 5 lost across 2 (G-T08: § 164(b)(7)'s $40,400 cap pushed out by its siblings; G-S08). Temporal rows mixed: G-T11 ppc → ccc, G-T08 cic → iii (crowd-out), G-T10 ccc → icp; G-T02 ccc → iii is the grader: F5's identical "$1,000,000" was graded correct.
  **Short answers read by Claude (22, plan set 0):** 10 right, 6 vague but not wrong ("Yes, … meets specific requirements"; "Yes," on non-yes/no questions), **6 wrong or misleading and passed by the check**: G-C21 contradicts itself ("No, … are subject"), G-I06 and G-I09 answer what the sources can't (the check tests "follows from the shown sentences", not "answers this question"), G-T03 overconfident, G-S07 and G-C10 state the wrong condition. Edge case 17, realised.

- [x] **Conclusion check tightened (your go, 2026-10-01; $0.21 checks + $0.38 re-grading, dev replay only, golden not touched again):** the check now also fails a conclusion that answers another question (jurisdiction, year, subject) or contradicts itself or a statement, and reports whether the question is yes/no; a stray leading "Yes,"/"No," is dropped from the display when it isn't ("Short answer: $1,750 is taxable to the employee"). First version also rejected any "Yes" on a non-yes/no question: shown fell 83 → 71 of 111, hiding right answers ("Yes, the 2026 rate is 72.5 cents"), so the display fix replaced that rule. Final, replayed over R2's dev answers (38 changed, re-graded): answered correct ∧ grounded 35 → 36, incorrect 17 → 18, partial 57 → 56 (noise); short answer 83 → 84 of 111; off-question conclusions hidden (D01 "inverts the question", D23). The check isn't deterministic on borderline cases (D16 hidden in one replay, shown in the other). Its effect on golden's six bad short answers is unmeasured (golden used once); F6 reports golden as measured before this change.

## F6: Phase F exit report

`eval/results/phase_f.md`: gate outcomes, what each check caught (with examples: a laundered citation suppressed, `G-I11`'s half answer), what it cost (suppressions, latency), what F got wrong. Tech doc §7/§9.3 and ADRs updated.

**F6 (2026-10-01):** exit report drafted (`eval/results/phase_f.md`, a new file for you to create); tech doc ADR-1, ADR-4, ADR-15 revised and Phase F baselines added; PRD §9 results note. `phase-f` pushed (your go); CI green on the shipped pipeline: tests (run 36937736469); retrieval gate 0.760 ≥ 0.70 (run 36937735731); faithfulness 0.951 ± 0.015 ≥ 0.855 at refusals 0.056 (run 36937738414; $6.24: pipeline $3.58, judge $2.66).

## ✅ Checkpoint: Phase F complete
- [ ] Citation entailment F1 ≥0.90 (NLI vs. LLM-judge, not-supported class): **not met**, 0.63 vs Sonnet 5.5 (≈0.72 adjusted)
- [x] Citation completeness ≥0.85: 0.994 (golden, shipped)
- [x] Substantive correctness tracked (N, κ reported): 291 golden row-samples, κ 0.72
- [x] Tests and both CI gates green on the shipped pipeline
