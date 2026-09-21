# TaxCite — Status

_Last updated: 2026-09-19_

## Now
**Phase A is complete (2026-09-21).** Report: `eval/results/phase_a.md`. 95 tests green.

A reviewer can `POST /queries` a tax question and watch `retrieving → synthesizing → answer` arrive over SSE, ending in a cited answer whose citations are checked against what was actually retrieved. Retrieval's contribution is measured: correctness 0.44 → 0.61, outright-wrong answers to zero, hybrid Recall@10 0.722.

Settled by measurement: ADR-11 (`gpt-4o-mini`), ADR-17 (Qdrant over pgvector), ADR-18 (`bge-base-en-v1.5`), §11.1 (statute source).

**Next: plan Phase B** — case-law corpus, query decomposition, the 100-question golden set, and RAGAS as a standing CI gate (faithfulness ≥ 0.85). Phase A left three baselines for later phases to beat: the 12.4-point publication dilution (Phase E), the 22% filtered-recall loss under strict filters (Phase D), and a pilot set too small to resolve differences under 5.6 points (§9.1).

Working mode: Claude writes the code and may edit existing files; new files are handed over as code blocks for the user to create.

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
- The eCFR API requires compressed responses (406 without them). Part 1 is ~12 MB compressed and takes ~30 s to download; it's cached in `data/raw/`.
- No §1.280A in eCFR (the home-office regulations were never finalized), so home-office questions rely on Pub 587 and the statute.
- `CITA` holds the amendment history, and some sections were renumbered ("Redesignated"). Both matter for Phase D.
- Some paragraph headings carry their own date ranges ("taxable years beginning after Dec 31, 1970"), which Phase D can use.
- Italic designations `(<I>2</I>)` are deep paragraph levels (5–6), not split points.
- `(i)` is ambiguous: a letter in `1.42-1` (after `(h)`), a Roman numeral in `1.704-1T` (after `(b)(1)`). Both are in the fixture.
- 178 table-of-contents sections (~4% of Part 1) are heading lists that would compete with real rule text in search results.
- Part 1 parses to 44,250 chunks (43,919 indexable), averaging 270 tokens; parsing takes ~5 s.
- Sections can embed their own outline in an `<EXTRACT>`; treating it as structure restarted paragraph numbering and silently lost 154 chunks (fixed; log #18).
- Embedding runs at 7.0 chunks/s (~105 min for Part 1). Parallel workers are *slower* (3.4/s at 4 workers); CoreML is a wash.

## Environment
- Stack: `docker compose up -d --wait` starts Qdrant (6333), Postgres (**5433**) and Redis (**6380**); 5432 and 6379 are taken locally.
- Tests: `uv run pytest -q` (needs the stack running).
- Knowledge graph: `graphify-out/`; it's stale since the ADR-17 and §11.1 edits.

## Pending housekeeping
- No git commits yet. Commit the docs, plan and T1? (`.DS_Store` and `scratch/` to `.gitignore` first.)
- If a `venv/` folder reappears, delete it and use a fresh terminal tab.
