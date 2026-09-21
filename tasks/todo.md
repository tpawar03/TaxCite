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
