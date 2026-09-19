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
- [ ] `uv run taxcite ingest ecfr --part 1` loads Part 1; Postgres (non-excluded rows) and Qdrant chunk counts match
- [ ] Every chunk has a paragraph-level citation and is ≤ ~500 estimated tokens, except single paragraphs that can't be split further
- [ ] Running ingest again does not create duplicates

**Verification:**
- [ ] `uv run pytest -q` — parser test on a saved eCFR XML fixture (one section, one oversized section)
- [ ] Manual: spot-check 3 chunks against ecfr.gov

**Dependencies:** T1
**Files:** `src/taxcite/ingest/ecfr.py`, `src/taxcite/store.py`, `src/taxcite/cli.py`, `tests/fixtures/ecfr_sample.xml`, `tests/test_ecfr.py`
**Scope:** M

---

## T3: Hybrid search CLI with citations

**Description:** Add a `search(query, k, mode)` function: embed the query dense + sparse, run a Qdrant hybrid query with fusion, and return chunks with their citations. `mode` is `dense | hybrid` for the later ablation. Expose it as `taxcite search`.

**Acceptance criteria:**
- [ ] `taxcite search "who may deduct home office expenses" -k 10` prints ranked citations and snippets
- [ ] `--mode dense` and `--mode hybrid` both work and return different rankings on at least one query

**Verification:**
- [ ] `uv run pytest -q` — a search test over a small fixture collection returns the known relevant section in the top 3
- [ ] Manual: 3 hand-picked questions return a sensible top 5

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
- [ ] 20 approved rows, with a mix of regulation-only, publication-only and questions that need both
- [ ] `uv run python eval/retrieval.py --mode dense|hybrid` writes a results JSON and prints a table
- [ ] The metric functions are checked with asserts on a toy example

**Verification:**
- [ ] `uv run pytest -q` (metric self-check)
- [ ] Manual: the user signs off on the pilot set

**Dependencies:** T3 (T5 is needed before the publication questions can be scored)
**Files:** `eval/pilot.jsonl`, `eval/retrieval.py`, `tests/test_metrics.py`
**Scope:** M

---

## T5: Ingest IRS Publications

**Description:** Download a fixed list of IRS pubs relevant to the pilot set (e.g. 587, 463, 17, 334, 535) from irs.gov/pub, using a rate-limited client with an identifying user-agent that respects robots.txt. Extract text with `pypdf` and chunk it into ~300-token windows with 15% overlap, cited as `IRS Pub N (YYYY), p. X`. Pages that fail extraction are marked `extraction_failed` and excluded.

**Acceptance criteria:**
- [ ] `taxcite ingest irs-pubs` loads the configured pubs; each chunk has a page-level citation
- [ ] Empty or garbled pages are recorded as `extraction_failed`, not indexed
- [ ] Retrieval eval re-runs with the publication questions now scorable

**Verification:**
- [ ] `uv run pytest -q` — chunker overlap test and extraction-failure test (fixture PDF)
- [ ] Manual: 2 pub chunks spot-checked against the PDF

**Dependencies:** T2 (reuses the store); can run in parallel with T3/T4
**Files:** `src/taxcite/ingest/irs_pubs.py`, `tests/test_irs_pubs.py`, `tests/fixtures/pub_sample.pdf`
**Scope:** S

---

## T6: Embedding-model benchmark and decision

**Description:** Re-index a fixed benchmark subset (the Parts and pubs the pilot set touches, plus distractors) once per candidate model, with ≥2 candidates: `bge-small-en-v1.5` vs. `nomic-embed-text-v1.5`. Run T4's eval for dense and hybrid with each model. Write the results into §3.2 of the tech doc as a new ADR entry (ADR-18: embedding model).

**Acceptance criteria:**
- [ ] A results table: model × mode → Recall@10, nDCG@10, MRR, plus index time
- [ ] The decision is recorded with its rationale; `EMBED_MODEL` config is set to the winner

**Verification:**
- [ ] Manual: the user approves the choice (Checkpoint 2)

**Dependencies:** T4, T5
**Files:** `eval/embed_bench.py`, `taxcite-technical-documentation.md`, `eval/results/embed_bench.md`
**Scope:** S

---

## T6b: ADR-17 revisit trigger — Qdrant vs. pgvector

**Description:** Load the same benchmark subset, with the same winning embeddings from T6, into pgvector. Switch the compose image to `pgvector/pgvector:pg16`, which is Postgres 16 with the extension, and store the vectors in a separate `bench_chunks` table so app tables are untouched. Hybrid search on the pgvector side uses `sparsevec` or Postgres full-text search, with RRF fusion in SQL. Compare the two stores on (1) pilot-set Recall@10/nDCG@10 for hybrid search, (2) filtered-recall loss: for each pilot question, run approximate search with a strict filter (a single CFR Part or a single IRS pub) and measure recall@10 against an exact brute-force search under the same filter, (3) p95 query latency, and (4) on-disk index size, projected to the full Phase A–C corpus against the Supabase free-tier storage cap. Record the numbers in ADR-17 and apply its revisit rule.

**Acceptance criteria:**
- [ ] A results table: store × {hybrid Recall@10, nDCG@10, filtered-recall loss, p95 latency, index size, projected corpus size}
- [ ] The ADR-17 outcome is recorded: confirmed (Qdrant stays) or reopened (pgvector fits under the cap AND filtered recall is within 2 points)
- [ ] App tables and the Qdrant collection are unchanged by the benchmark

**Verification:**
- [ ] `uv run pytest -q` still passes (the image switch doesn't break `/health`)
- [ ] Manual: the user reviews the ADR-17 outcome (Checkpoint 2)

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
- [ ] `taxcite ask "…" --mode rag` prints an answer with inline citations that all refer to retrieved chunks
- [ ] `--mode closed_book` works through the same code path, with no retrieval
- [ ] Token counts and cost are returned for each call

**Verification:**
- [ ] `uv run pytest -q` — a citation-parsing test (answer text → cited ids ⊆ retrieved ids) with a stubbed LLM response
- [ ] Manual: 3 pilot questions in both modes

**Dependencies:** T3 (T6 is preferred first so the final embedding model is used)
**Files:** `src/taxcite/generate.py`, `src/taxcite/llm.py`, `src/taxcite/cli.py`, `tests/test_generate.py`
**Scope:** M

---

## T8: ADR-11 LLM benchmark and decision

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
- [ ] The report exists and every number in it traces to a file in `eval/results/`
- [ ] At least 3 failure examples are documented (§9 publishes failures, not just successes)

**Verification:**
- [ ] Manual: user review

**Dependencies:** T6, T8, T9
**Files:** `eval/results/phase_a.md`, `taxcite-technical-documentation.md`
**Scope:** S

---

## ✅ Checkpoint: Phase A complete
- [ ] All tests pass
- [ ] A reviewer can POST a question and receive a cited answer over SSE
- [ ] ADR-9 built; ADR-11 and the embedding model decided
- [ ] Ready to plan Phase B
