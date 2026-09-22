# TaxCite — Status

_Last updated: 2026-09-21_

## Now
**Phase A is complete (2026-09-21).** Report: `eval/results/phase_a.md`. 95 tests green.

A reviewer can `POST /queries` a tax question and watch `retrieving → synthesizing → answer` arrive over SSE, ending in a cited answer whose citations are checked against what was actually retrieved. Retrieval's contribution is measured: correctness 0.44 → 0.61, outright-wrong answers to zero, hybrid Recall@10 0.722.

Settled by measurement: ADR-11 (`gpt-4o-mini`), ADR-17 (Qdrant over pgvector), ADR-18 (`bge-base-en-v1.5`), §11.1 (statute source).

**Phase B plan approved (2026-09-21).** Plan: `tasks/plan.md` (Phase B section); tasks: `tasks/todo.md` (B1–B10). **B2 done (2026-09-22).** All of Title 26 is indexed: 10,768 statute chunks, 110 tests green. Pilot hybrid Recall@10 0.722 → 0.667 with the statute, one question (P02), whose statute answer now outranks its gold regulation (log #36). Fixed on the way: a Phase A range-citation bug (84 eCFR chunks, log #33) and an embedding batch size that thrashed swap (log #35). **B3 done (2026-09-22).** 307 Tax Court opinions indexed (9,973 chunks); corpus 28,393 vectors; 120 tests green. Case law cut pilot hybrid Recall@10 0.667 → 0.500: P01's top 10 is all case law. Routing case law out recovers ~0.611 (approx.), which is B7's job (log #38). **B4 done (2026-09-22).** `eval/golden.jsonl` (53 rows: 27 statutory, 26 case law) and `eval/dev.jsonl` (12 rows) reviewed and frozen; baseline hybrid Recall@10 0.491, statutory only 0.333 (`eval/results/golden-b4-baseline-k10.json`). **B5 done (2026-09-22). Golden set complete and frozen:** `eval/golden.jsonl`, 111 reviewed rows. Baseline hybrid Recall@10 0.435 over the 84 rows scored in B (statutory 0.333, case law 0.654, compound 0.350; `eval/results/golden-b5-baseline-k10.json`). **Next: B6 (cross-encoder rerank).** Scope from §7 — case-law corpus, query decomposition, the 100-question golden set, and RAGAS as a standing CI gate (faithfulness ≥ 0.85). Phase A left three baselines for later phases to beat: the 12.4-point publication dilution (Phase E), the 22% filtered-recall loss under strict filters (Phase D), and a pilot set too small to resolve differences under 5.6 points (§9.1).

Working mode: Claude writes the code and may edit existing files; new files are handed over as code blocks for the user to create.

## Phase B progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`, Phase B sections)
| Task | Status |
|---|---|
| B1 Topic scope and source spike | ✅ Done (DAWSON; whole Title 26) |
| B2 Ingest 26 U.S.C. | ✅ Done (10,768 chunks; pilot 0.722 → 0.667) |
| B3 Ingest Tax Court opinions | ✅ Done (9,973 chunks; pilot 0.667 → 0.500) |
| B4 Golden set part 1 | ✅ Done (53 rows; baseline 0.491) |
| B5 Golden set part 2 | ✅ Done (111 rows total; baseline 0.435) |
| B6 Cross-encoder rerank | ⬜ Next |
| B7 Query decomposition | ⬜ |
| B8 RAGAS harness | ⬜ |
| B9 CI + RAGAS gate | ⬜ |
| B10 Phase B exit report | ⬜ |

## Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`)
| Task | Status |
|---|---|
| T1 Local stack, package, `/health` | ✅ Done (built by Claude before the collaborative mode was set; walkthrough offered) |
| T2 Ingest eCFR Title 26 | ✅ Done (pilot subset: 4,969 chunks / 4,917 vectors) |
| T3 Hybrid search CLI | ✅ Done (dense / sparse / hybrid) |
| T4 Pilot set + retrieval eval | ✅ Done (hybrid Recall@10 0.812) |
| T5 Ingest IRS Publications | ✅ Done (6 pubs, 2,083 chunks) |
| T6 Embedding benchmark (ADR-18) | ✅ Done (bge-base, +5.6 recall) |
| T6b Qdrant vs. pgvector (ADR-17 trigger) | ✅ Done (ADR-17 confirmed) |
| T7 Cited answers + closed-book baseline | ✅ Done |
| T8 LLM benchmark (ADR-11) | ✅ Done (gpt-4o-mini) |
| T9 Job record + SSE transport (ADR-9) | ✅ Done |
| T10 Phase A exit report | ✅ Done |

## Decisions log
| Date | Decision | Where recorded |
|---|---|---|
| 2026-09-22 | B5 audit: compound rows may not reuse an opinion a case-law-only row tests (except deliberate pairs); reversed opinions become explicit Phase E tests with notes | `tasks/todo.md` B5, log #42 |
| 2026-09-22 | B5: compound/temporal rows carry gold sub-queries (measurement only); insufficiency verified by real search, not text match | `tasks/plan.md`, `tasks/todo.md` B5, log #41 |
| 2026-09-22 | You kept the extra golden rows: §9.1's per-category counts are minimums; golden set frozen after review | `tasks/plan.md`, `tasks/todo.md` B4 |
| 2026-09-22 | B4 audit: §9.1 counts treated as minimums (golden part 1 is 27 + 26); rows carry `notes` for facts outside the corpus (appeals, later law); no gold citation or opinion may appear in both golden and dev/pilot | `tasks/plan.md`, `tasks/todo.md` B4, log #40 |
| 2026-09-22 | B4: dev rows in a new `eval/dev.jsonl` (pilot left untouched); validator distinguishes diluted from wrong gold; nDCG counts each gold group once; ADR-18 nDCG gap marked unreliable | `tasks/todo.md` B4, log #39, tech doc ADR-18 |
| 2026-09-22 | Plan revised from B1–B3 findings (you allowed plan edits when findings require them): case law is the 50 newest per topic with page pin-cites; no empty holding/dicta column; golden-set gold becomes groups of interchangeable citations (log #36); DAWSON API change and orphaned gold labels added as risks | `tasks/plan.md`, `tasks/todo.md` B3–B4 |
| 2026-09-21 | B2: statute chapeaus fold into their first provision; repealed provision stubs dropped; eCFR packing shared via `ecfr.pack`; Phase A range-citation bug fixed, P03 gold relabelled `1.162-4(a)-(c)` | `tasks/todo.md` B2, logs #33-34 |
| 2026-09-21 | B1: case law from DAWSON, not CourtListener (§11.5 revised; 5× coverage, memos included, but no documented API); whole live Title 26 loaded (~60 min once); 8 case-law topics | `tasks/todo.md` B1, log #32, tech doc §11.5 |
| 2026-09-21 | Phase B plan approved with Claude's defaults: cross-encoder rerank in B (B6); RAGAS library, pinned; holding/dicta field added empty, tagged in Phase E; CI corpus from a Qdrant snapshot + Postgres dump release asset; golden set is held out, tuning on the dev set only | `tasks/plan.md` Phase B |
| 2026-09-18 | Project intent: interview piece; architecture kept as specified; live demo + eval dashboard; 3–4 months; <$50/mo | `docs/intent/taxcite.md` |
| 2026-09-18 | Phase A plan approved | `tasks/plan.md` |
| 2026-09-18 | Embedding: `bge-small-en-v1.5` primary, `nomic-embed-text-v1.5` challenger | `tasks/plan.md` |
| 2026-09-18 | LLM candidates: Anthropic + OpenAI budget tier; the judge model comes from the other provider | `tasks/plan.md` |
| 2026-09-18 | Statute source: uscode.house.gov for content, GovInfo for change detection only | Tech doc §11.1 |
| 2026-09-19 | ADR-17: Qdrant over pgvector and others; T6b benchmark as the revisit trigger | Tech doc ADR-17, `tasks/todo.md` T6b |
| 2026-09-19 | Chunking: split at paragraph level 1 → 2, ~500 tokens, keep short sections, skip reserved, flatten tables ≤100 cells, store `CITA` raw, keep as-of date + download time | `tasks/todo.md` T2 |
| 2026-09-19 | Dropped the global `UV_PROJECT_ENVIRONMENT=venv`; project uses `.venv/` | — |
| 2026-09-21 | ADR-11 decided: `gpt-4o-mini` at all three call sites (correct 0.61 vs 0.33, 3x faster, 8x cheaper); revisit trigger moves synthesis to haiku if Phase F suppresses too much for want of citations | Tech doc ADR-11, logs #30-31 |
| 2026-09-21 | Citations are counted three ways — exact / derived (narrower paragraph of a retrieved section) / fabricated — because collapsing them misread haiku as inventing citations | `src/taxcite/generate.py` |
| 2026-09-20 | Start on the cheapest, fastest model (`claude-haiku-4-5`, no reasoning) and upgrade only if measurement shows a need. At persona volume (~200 queries/mo) the pipeline costs ~$3.51/mo, 14x under the ceiling, so cost is not the binding constraint — latency and quality are | `src/taxcite/generate.py`, T8 |
| 2026-09-20 | ADR-17 confirmed by measurement: pgvector's lexical ranking (0.111) is far below Qdrant BM25 (0.444); trigger corrected to include hybrid recall | Tech doc ADR-17, log #27 |
| 2026-09-20 | Retrieval over-fetches and breaks RRF ties by citation, making the eval reproducible | `src/taxcite/retrieve.py`, log #28 |
| 2026-09-20 | ADR-18: dense model is `bge-base-en-v1.5` (768d); nomic excluded on 491 ms query latency | Tech doc ADR-18, logs #25-26 |
| 2026-09-20 | IRS pubs use pdfminer.six (not pypdf); downloads validated by content; Pub 535 replaced by 946 + 527 | `src/taxcite/ingest/irs_pubs.py`, logs #22-23 |
| 2026-09-20 | Hybrid confirmed as default by measurement (Recall@10 0.812 vs dense 0.719); per-style numbers reported, not one aggregate | `eval/results/`, log #20 |
| 2026-09-20 | Search ships three modes (sparse/dense/hybrid) as ablation rungs; hybrid is not uniformly better, so T4's pilot set decides the default | `src/taxcite/retrieve.py`, log #19 |
| 2026-09-19 | Chunks keyed on `chunk.key` (`citation#reason#part`); re-ingest sweeps rows a section no longer produces; one record per oversized table | `src/taxcite/store.py`, `tasks/todo.md` T2 |
| 2026-09-19 | Preamble text (before `(a)`) is its own chunk cited bare; packed units get a range citation `(a)-(c)` | `src/taxcite/ingest/ecfr.py` |
| 2026-09-19 | Skip `[Reserved]` paragraphs; skip table-of-contents sections (`excluded = "toc"`); designation parser reads all leading designations (`(b)(1)`) | `tasks/todo.md` T2, log #14 |

## Findings worth remembering
_Interview-ready versions of these, with trade-offs, are in `docs/engineering-log.md`._
- CourtListener has only ~20–60 Tax Court opinions a year since 2000 (reported T.C. only); DAWSON has 5× more on `"section 183"` (560 vs 108). Its bulk opinions dump is 54.6 GB with no court id on the row (log #32).
- Title 26 release point 119-110: 1,900 live sections, ~2.3M tokens, 56 MB XML parsed in 0.7 s. The whole statute is ~60 min to embed.
- The eCFR API requires compressed responses (406 without them). Part 1 is ~12 MB compressed and takes ~30 s to download; it's cached in `data/raw/`.
- No §1.280A in eCFR (the home-office regulations were never finalized), so home-office questions rely on Pub 587 and the statute.
- `CITA` holds the amendment history, and some sections were renumbered ("Redesignated"). Both matter for Phase D.
- Some paragraph headings carry their own date ranges ("taxable years beginning after Dec 31, 1970"), which Phase D can use.
- Italic designations `(<I>2</I>)` are deep paragraph levels (5–6), not split points.
- `(i)` is ambiguous: a letter in `1.42-1` (after `(h)`), a Roman numeral in `1.704-1T` (after `(b)(1)`). Both are in the fixture.
- 178 table-of-contents sections (~4% of Part 1) are heading lists that would compete with real rule text in search results.
- Part 1 parses to 44,250 chunks (43,919 indexable), averaging 270 tokens; parsing takes ~5 s.
- Sections can embed their own outline in an `<EXTRACT>`; treating it as structure restarted paragraph numbering and silently lost 154 chunks (fixed; log #18).
- Embedding batch size must stay small on CPU: 256 thrashed at 8.6 GB; 16 is as fast at 1.5 GB. bge-base runs ~3 chunks/s (log #35).
- Embedding runs at 7.0 chunks/s (~105 min for Part 1). Parallel workers are *slower* (3.4/s at 4 workers); CoreML is a wash.

## Environment
- Stack: `docker compose up -d --wait` starts Qdrant (6333), Postgres (**5433**) and Redis (**6380**); 5432 and 6379 are taken locally.
- Tests: `uv run pytest -q` (needs the stack running).
- Knowledge graph: `graphify-out/`; refreshed 2026-09-21 but not committed yet.

## Pending housekeeping
- Phase A is committed (`df0703e`). Not committed yet: the `.gitignore` entry for `docs/phase-a-interview-prep.md` and the refreshed `graphify-out/`.
- If a `venv/` folder reappears, delete it and use a fresh terminal tab.
