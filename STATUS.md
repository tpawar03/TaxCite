# TaxCite — Status

_Last updated: 2026-09-19_

## Now
**Phase A, T2 (ingest 26 CFR Part 1), step 3: Postgres.** The parser is done and green: `src/taxcite/ingest/ecfr.py` with `tests/test_ecfr.py` (24 passing) over the 9-section fixture. Both first-run bugs are fixed — duplicate citations (now a `part` field; the key is `(citation, part)`) and preamble mis-citation.

Next: the `chunks` table and an idempotent upsert keyed on `(citation, part)`; then embeddings into Qdrant (step 4) and the `taxcite ingest ecfr` CLI (step 5).

Still open: the large-table record is one per section rather than one per table.

Parser now also tags `source` on every chunk, and a test confirms our whole-section citations match eCFR's own `hierarchy_metadata` citation string.

Working mode: Claude writes the code and may edit existing files; new files are handed over as code blocks for the user to create.

## Phase A progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`)
| Task | Status |
|---|---|
| T1 Local stack, package, `/health` | ✅ Done (built by Claude before the collaborative mode was set; walkthrough offered) |
| T2 Ingest eCFR Title 26 | 🔨 In progress (exploration done, parser next) |
| T3 Hybrid search CLI | ⏳ |
| T4 Pilot set + retrieval eval | ⏳ |
| T5 Ingest IRS Publications | ⏳ |
| T6 Embedding benchmark (ADR-18) | ⏳ |
| T6b Qdrant vs. pgvector (ADR-17 trigger) | ⏳ |
| T7 Cited answers + closed-book baseline | ⏳ |
| T8 LLM benchmark (ADR-11) | ⏳ |
| T9 Job record + SSE transport (ADR-9) | ⏳ |
| T10 Phase A exit report | ⏳ |

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

## Environment
- Stack: `docker compose up -d --wait` starts Qdrant (6333), Postgres (**5433**) and Redis (**6380**); 5432 and 6379 are taken locally.
- Tests: `uv run pytest -q` (needs the stack running).
- Knowledge graph: `graphify-out/`; it's stale since the ADR-17 and §11.1 edits.

## Pending housekeeping
- No git commits yet. Commit the docs, plan and T1? (`.DS_Store` and `scratch/` to `.gitignore` first.)
- If a `venv/` folder reappears, delete it and use a fresh terminal tab.
