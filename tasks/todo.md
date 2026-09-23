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
- [x] Manual: 3 questions checked. One excellent (profit-motive factors), two mediocre — see log #19 and the subset gap below

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

**Done 2026-09-20.** First numbers (k=10): hybrid Recall 0.812 / nDCG 0.468, dense 0.719 / 0.445, sparse 0.500 / 0.387. Section recall 1.000 vs strict 0.812 = the reranking headroom. Gold verified against regulation text, **not** reviewed by a tax professional (see log #21); validation caught a wrong citation and two incomplete answers.

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

**Done 2026-09-20.** Text comes from pdfminer.six, not pypdf (log #22). Pub 535 is discontinued and its URL returns HTTP 200 with HTML, so downloads are validated by content (log #23); 946 and 527 replace it. **Key result:** adding publications cut hybrid recall on the *same 16 regulation questions* from 0.812 to 0.688, because plain-English guidance outranks binding law — the measured case for Phase E authority-aware reranking (log #24).

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

**Done 2026-09-20.** bge-base beat bge-small on every quality metric (hybrid recall 0.667 vs 0.611, nDCG 0.350 vs 0.259, dense MRR 0.315 vs 0.185) at 3.4x index time (31.6 vs 9.3 min) and 2x storage (24 vs 12 MB). nomic was excluded on latency before any quality measurement (491 ms/query; log #25). Dense scores 0.000 on publication questions for both models — publications match lexically, not semantically.

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

**Done 2026-09-20.** Qdrant 0.667 hybrid recall vs pgvector 0.500; the gap is lexical (BM25 0.444 vs `ts_rank_cd` 0.111), not dense (0.583 vs 0.528) and not filtering (0.779 both). Storage would have fitted a free tier (77 MB, ~386 MB projected). Two findings: the revisit trigger omitted the deciding metric (log #27), and a tie at the k boundary made the eval unreproducible until ties were broken deterministically (log #28).

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
- [x] Manual: P01 in both modes — RAG cited `26 CFR 1.183-2(b)(3)` exactly; closed-book cited the **discontinued** IRS Pub 535 (log #29)

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
- Chunking decisions: level 1 is a section's top provisions (subsections, or paragraphs as in §212), level 2 their children; **lead-ins fold into the first provision they introduce** (log #34); bracketed "[(n) Repealed …]" provisions are dropped; repealed/renumbered/reserved/omitted sections are recorded with `excluded = status`; `sourceCredit` is stored as `cita`; notes are skipped; en-dash section numbers (`1400Z–2`) become hyphens.
- `ecfr.pack` extracted and shared with a citation prefix. **It had a Phase A bug:** range citations lost their end when the last unit had several blocks, affecting 84 of 5,609 eCFR chunks (log #33). Fixed with a regression test, P03 gold relabelled `1.162-4(a)-(c)`, and the eCFR subset re-ingested from the same 2026-09-17 file.
- `source_revision` column added (ALTER, so Phase A's table picks it up); `section_of` handles statute citations, including dashed sections; the synthesis prompt shows a statute citation example; the IRS scraper's User-Agent now points to the right repo.
- Found while testing: `index.sync` held its read transaction open for the whole embedding run, so the `source_revision` ALTER queued behind a running ingest and hung the test suite. `index.sync` now commits after reading, and `create_table` only ALTERs when the column is missing.
- The first eCFR re-ingest ran at 0.45 chunks/s (8.6 GB, 20 GB swap) and was stopped at 56%. Embedding batch 256 → 16: same speed (2.91 vs 2.86/s), 1.5 GB vs 4.5 GB peak (log #35). Re-run at ~3/s.
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

Three more questions lost (P01, P11, P17). **P01's top 10 is all case law**: hobby-loss opinions apply §1.183-2(b)'s factors to real horse breeders, which matches a fact-pattern question better than the regulation. Across the pilot, case law takes 53 of 180 top-10 slots (29%). This is the dilution B7's source routing exists to remove (log #38).

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

**Description:** Create `eval/golden.jsonl`. The schema extends the pilot set's (question, gold citations, reference answer) with `category`, `scored_from` (the phase a row starts being scored in), `as_of` and `expect_insufficient`. Claude drafts 25 statutory-only and 20 case-law-only rows from ingested text; you review every row. **Gold is a list of groups of interchangeable citations** (e.g. `[["26 U.S.C. § 183(a)-(d)", "26 CFR 1.183-1(b)(1)"]]`); a group counts when any member is retrieved (log #36). Update `eval/retrieval.py` to score groups, treating a flat list as one citation per group so the pilot's numbers don't move. Case-law rows can only use the 307 ingested opinions. Extend `eval/validate_pilot.py` to take any set file and check that every gold citation exists in the corpus. Also add ~12 dev rows (case-law and compound) for tuning, in `eval/dev.jsonl`.

**Acceptance criteria:**
- [x] 53 rows in `eval/golden.jsonl` (27 statutory, 26 case law; §9.1's 25/20 kept as minimums at your call); the validator passes
- [x] `eval/retrieval.py` scores gold groups; pilot recall and MRR unchanged (nDCG and section recall corrected, log #39)
- [x] Every row reviewed by you (`reviewed: true`); corrections logged (log #40)
- [x] 12 dev rows in `eval/dev.jsonl`, validated, no gold or opinion shared with the golden set or pilot

**Verification:**
- [x] `uv run python eval/validate_pilot.py eval/golden.jsonl`: 0 of 53 need attention; 4 known-hard; 12 diluted groups

**Done 2026-09-22.** Baseline `eval/results/golden-b4-baseline-k10.json`, hybrid k=10: Recall 0.491 (statutory 0.333, case law 0.654), nDCG 0.324, MRR 0.271. **Frozen:** any change to `eval/golden.jsonl` from here is a logged commit.

**Progress 2026-09-22 (drafted, awaiting your review):**
- 45 golden rows (25 statutory, 20 case-law; 37 natural-language, 8 keyword) and 12 dev rows (6 case-law, 6 compound) in a **new `eval/dev.jsonl`**, not appended to the pilot, so Phase A's pilot numbers stay comparable. Dev rows use opinions the golden set doesn't.
- Written from the gold chunks' text: statute answers from the provision (e.g. §67(h) now suspends miscellaneous itemized deductions permanently, not through 2025); case-law answers from the court's own "Held:" or "we hold" sentences. Gold located by phrase, so every chunk containing a holding (overlap can duplicate it) is in its group.
- Gold groups used where authorities are interchangeable: 5 statute rows carry a regulation alternative; G-C16 accepts two opinions with the same holding; G-C14 and G-C20 accept the syllabus and the discussion page.
- `eval/retrieval.py` scores groups; `section_of` now comes from `generate.py`. **Two Phase A metric bugs found** (log #39): nDCG counted a gold citation once per retrieved chunk (P15 scored 1.232), and section recall never matched publications. Pilot recall and MRR unchanged; ADR-18 carries a caveat.
- `eval/validate_pilot.py` handles groups, prints category counts, and **separates diluted gold from wrong gold**: a group missing from the overall top 50 is re-searched within its own source. 12 statute groups are diluted (found within `usc` only); 2 rows are marked `expect_hard` for vocabulary mismatch (G-S03, G-S21).
- Baseline, hybrid k=10: Recall 0.467 (statutory **0.320**, case law 0.650), nDCG 0.317, MRR 0.268.

**Audit 2026-09-22 (two full passes over every row and its sources, at your request; log #40):**
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
- **Temporal rows expose a Phase D gap:** effective dates live in the statutory notes, which the B2 parser drops, so the corpus can't say that the qualified-tips deduction (§224) starts in 2025 or which §179 limit applied in 2023 (log #41). Those rows are `expect_insufficient`.
- The queued edge cases are in: medical marijuana 2026 (G-T03), hobby expenses after 2017 (G-X01) and in 2016 (G-T04), Morehouse in the Eighth Circuit (G-X02, Phase E).
- Adversarial rows carry `client_doc` and `expected_behavior`: prompt injection, script injection, a fabricated §183(z), a system-prompt exfiltration request, and a forged authority badge with a `javascript:` link.
- Baseline on the 30 compound rows, hybrid k=10: Recall **0.317**, the number decomposition has to beat.

**Audit 2026-09-22 (two passes over every row and its full sources, at your request; log #42):**
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

**Done (2026-09-22).** Results: `eval/results/golden-b6-rerank-k10.json` (+ `.txt`). Decision: ADR-19, log #43.
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

**Done (2026-09-22), with one criterion unmet.** Results: `eval/results/golden-b7-decompose-k10.json`, `golden-b7-ladder-k10.txt`, `dev-b7-ladder-k10.txt`, `pilot-b7-decompose-k10.txt`. Decision: ADR-20, log #44.
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

**Progress (2026-09-23).** Design settled and calibrated (ADR-22, log #48); files written; threshold pending one measurement.
- [x] **Calibrated the gate against the failure it exists to catch.** Dev, judge `claude-haiku-4-5`: healthy 0.823 (sd 0.033), healthy at temp 0 **0.808 (sd 0.016)**, broken prompt 0.762, broken at temp 0 0.759 (sd 0.027). A broken synthesis prompt costs ~0.05 — **2.2 pooled sd**, a 0.011-wide window, ~12% false failures and ~12% false passes. A per-PR faithfulness gate on 25 rows does not work.
- [x] **Noise decomposed by pinning one component at a time:** re-judging identical answers moves sd **0.008** (5% of variance); the planner and synthesis sampling hold the other 95%, and both are pinnable. The unpinnable component is the one that barely matters.
- [x] **Synthesis pinned to `temperature=0, seed=0`** — halves the noise, no measurable quality cost, and the right default for a legal tool independent of CI. Test added.
- [x] **Three workflows written** (`test.yml`, `retrieval-gate.yml`, `faithfulness.yml`) plus `eval/snapshot.py` for corpus freeze/restore, and `--fail-under` on both eval entry points (exit codes verified).
- [x] Tier 2 is the per-PR blocker: `eval/retrieval.py` against the committed plan cache — no LLM, deterministic, `--fail-under 0.66` against the measured dev figure.
- [x] **Tier 3 threshold: 0.83**, three sigma below the measured healthy golden mean (0.871, sd 0.013, plans pinned + temperature 0). Enabled in `faithfulness.yml`. Calibrated against the healthy distribution, since broken-on-golden is not measured yet — the proof run supplies that.
- [x] **Found and fixed a harness bug worth more than the threshold:** `ragas_eval` called `decompose` fresh per row and never used the plan cache, so faithfulness was partly measuring the planner. Pinning plans took golden sd 0.035 → 0.013; temperature 0 alone had moved it only to 0.030, because the planner dominated (16% of golden questions re-route between runs). `decompose.answer()` now accepts a supplied plan (log #49).
- [x] Residual noise characterised: ~0.010 synthesis + 0.008 judge. Irreducible — OpenAI's `temperature=0` with `seed` is best effort, and two runs over identical plans and context still differ.
- [x] **Tier 1 verified:** `tests` green on `03f529c` (run 35899005211). The first run failed and the CI log confirmed the diagnosis exactly — `index.count` 404'd on an empty Qdrant during collection.
- [x] **Tier 2 verified both ways:** healthy `main` 0.6800 PASS (run 35900723401); PR #1 with `PREFETCH` 50→1 scores 0.3400 FAIL (run 35900409247), while `pytest` stays green on that same commit. Corpus restored in CI both times, 28,393 / 28,747 matching local.
- [x] **Three CI-only bugs found and fixed:** the empty-Qdrant 404; a Qdrant version mismatch (workflows pinned v1.12.4, the snapshot is v1.19.1 — the restore 500'd); and `on: release` firing the faithfulness gate when the *corpus* snapshot was published (run 35898818357), now skipped for `corpus-*` tags. `snapshot.py` also now prints Qdrant's response body, which `raise_for_status` was discarding.
- [x] **Tier 3 proof run — and it failed, correctly.** Both arms dispatched on the runner (35901633914 broken, 35901637011 healthy). Healthy `main` 0.870/0.884/0.889 → mean **0.881** sd 0.010. Grounding rule removed → 0.849/0.841/0.842 → mean **0.844** sd 0.004. **The broken build passed a gate set at 0.83**: the threshold was three sigma below a locally measured *healthy* mean and sat below where a broken build actually lands. Threshold corrected to **0.855**, between the two measured bands (~2.5 sigma margin each side); the bands do not overlap, healthy's worst run beats broken's best by 0.021. The contingency comment in the workflow was also backwards ("comes down" → must go up). Log #50, ADR-22.
- [x] Note: B9's criterion says "a *PR* with a broken prompt fails the gate". That wording predates the ADR-22 tiering, under which faithfulness deliberately does not trigger on `pull_request`. The dispatch on a branch is the equivalent proof for a nightly gate.
- [x] PR #1 closed unmerged.
- [ ] **Re-run the proof against 0.855** to see the gate actually go red (~$2.80, 50 min). The arithmetic is already settled by the measured means — 0.844 < 0.855 < 0.881 — so this demonstrates the mechanism rather than discovering anything.
- [ ] Delete `proof/retrieval-regression` and `proof/broken-synthesis-prompt`.

---

## B10: Phase B exit report

**Description:** Write `eval/results/phase_b.md`, in the same shape as `phase_a.md`: the golden-set ablation ladder with per-category numbers, faithfulness with its spread across runs, refusal and abstention rates, failures with examples, and §9.3 recalibration notes. Record the **decomposition-only case-law Recall@20** — the baseline Phase C's gate is measured against. Update the tech doc's Implementation Status.

**Acceptance criteria:**
- [ ] Every number traces to a results file or a reproducible command
- [ ] At least 5 failure examples documented
- [ ] Phase C's case-law Recall@20 baseline stated explicitly

**Verification:**
- [ ] Tech doc Implementation Status updated to say what is built and what is not

**Dependencies:** B9
**Files:** `eval/results/phase_b.md`, `taxcite-technical-documentation.md`
**Scope:** S

---

## ✅ Checkpoint: Phase B complete
- [ ] All tests pass in CI
- [ ] The RAGAS gate is live and green
- [ ] Ready to plan Phase C
