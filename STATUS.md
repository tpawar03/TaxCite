# TaxCite — Status

_Last updated: 2026-09-23_

## Now
**Phase B is complete (2026-09-23).** Report: `eval/results/phase_b.md`. 160 tests green, CI running in three verified tiers.

The corpus is 28,747 chunks across statute, case law, regulations and publications (28,393 indexed). Decomposition ships as source routing; the golden set is 115 reviewed rows; faithfulness is measured with a known noise floor and gated weekly at 0.855. Phase B's three most useful results are negative: reranking did not earn the default, the decomposer's query rewriting scored below the questioner's own words, and decomposition helps statutory retrieval rather than the compound questions it was built for. **Phase C's baseline is set: case-law Recall@20 = 0.692, decomposition only.** **Next: Phase C (citation graph) — but see the 8.9% edge-resolution finding before committing to it.**

**Phase A is complete (2026-09-21).** Report: `eval/results/phase_a.md`. 95 tests green.

A reviewer can `POST /queries` a tax question and watch `retrieving → synthesizing → answer` arrive over SSE, ending in a cited answer whose citations are checked against what was actually retrieved. Retrieval's contribution is measured: correctness 0.44 → 0.61, outright-wrong answers to zero, hybrid Recall@10 0.722.

Settled by measurement: ADR-11 (`gpt-4o-mini`), ADR-17 (Qdrant over pgvector), ADR-18 (`bge-base-en-v1.5`), §11.1 (statute source).

**Phase B plan approved (2026-09-21).** Plan: `tasks/plan.md` (Phase B section); tasks: `tasks/todo.md` (B1–B10). **B2 done (2026-09-22).** All of Title 26 is indexed: 10,768 statute chunks, 110 tests green. Pilot hybrid Recall@10 0.722 → 0.667 with the statute, one question (P02), whose statute answer now outranks its gold regulation (log #36). Fixed on the way: a Phase A range-citation bug (84 eCFR chunks, log #33) and an embedding batch size that thrashed swap (log #35). **B3 done (2026-09-22).** 307 Tax Court opinions indexed (9,973 chunks); corpus 28,393 vectors; 120 tests green. Case law cut pilot hybrid Recall@10 0.667 → 0.500: P01's top 10 is all case law. Routing case law out recovers ~0.611 (approx.), which is B7's job (log #38). **B4 done (2026-09-22).** `eval/golden.jsonl` (53 rows: 27 statutory, 26 case law) and `eval/dev.jsonl` (12 rows) reviewed and frozen; baseline hybrid Recall@10 0.491, statutory only 0.333 (`eval/results/golden-b4-baseline-k10.json`). **B5 done (2026-09-22). Golden set complete and frozen:** `eval/golden.jsonl`, 111 reviewed rows. Baseline hybrid Recall@10 0.435 over the 84 rows scored in B (statutory 0.333, case law 0.654, compound 0.350; `eval/results/golden-b5-baseline-k10.json`). **B6 done (2026-09-22).** Cross-encoder rerank is built and measured, and it did **not** earn the default: on the 84 scored golden rows it moves Recall@10 0.435 → 0.452 with nDCG flat at 0.307, for p50 30 ms → 852 ms (ADR-19, log #43). `hybrid+rerank` ships as an ablation rung; `jinaai/jina-reranker-v1-turbo-en` over 25 candidates, chosen on the dev set. The useful number is the ceiling: golden hybrid Recall@25 is 0.530, so 47% of gold never reaches the candidate pool — first-stage recall, not ranking, is the bottleneck, which makes it B7's problem. **B7 done (2026-09-22), with one criterion unmet.** Decomposition ships as **source routing, not query rewriting** (ADR-20): the model supplies the routing, the client facts and the as-of year, and each sub-query searches the *original question* filtered to the corpora its kind allows — the model's rewritten text measured worse than the questioner's own words (dev 0.625 vs 0.708, log #44). Golden (held out) Recall@10 0.435 → 0.476, nDCG 0.307 → 0.330, compound 0.350 → 0.400, p50 28 ms → 1,915 ms. The pipeline now publishes `decomposing → retrieving → synthesizing → answer`. **B7b done (2026-09-22).** The dev set grew 12 → 25 rows so routing *precision* could be measured at all (it was invisible before: every dev row's gold had case law). Two prompt revisions took routing to recall 0.917 / precision 0.917 on dev, and the **pilot dilution criterion is met: 0.500 → 0.611** — with the caveat that pilot shares 3 gold citations with dev, and on the 15 uncontaminated rows it is 0.533 → 0.600. The golden set was audited twice more and grew 111 → 115 rows (log #45). **The headline correction (log #46): B7's golden gain was a single-run reading.** The planner is not deterministic, so `eval/retrieval.py` now caches plans and `--repeats N` scores every arm against N independently planned sets. Over six plan sets routing is **0.440 ± 0.012** against a deterministic hybrid baseline of **0.428** — +0.012, one gold group in 86, with one run of six below baseline. Best arm is `hybrid+rerank+route` at **0.452**. **Checkpoint 3 answered, against the design's own prediction:** decomposition does *not* help the compound questions it was built for (0.349 → 0.366) — it helps **statutory** ones (0.321 → 0.357, 0.429 in the best arm), by keeping case-law prose out of a pool that should hold statute and regulations. **B8 done (2026-09-22).** `eval/ragas_eval.py` implements RAGAS faithfulness in-house — the library resolves to 326 packages against this project's 65 for a two-call metric (ADR-21) — judged by `claude-haiku-4-5`. Over 96 rows × 3 runs: **0.859 / 0.902 / 0.833, mean 0.865, sd 0.035**, $1.56 and 29 minutes. **Abstention is 10/10 insufficiency rows in 3/3 runs**, with 3–7 false refusals per run on top. **The finding that justifies the gate:** two rows score 0.00 in every run with *legally correct* answers — the gold chunk was never retrieved, the model answered from memory and pinned a citation to a chunk that was retrieved but does not say it. Phase A's citation checker scores those as exact and passes them; faithfulness is the only check that sees it. **The problem handed to B9:** run 3 fell below the 0.85 gate with nothing changed, so a per-run gate fails about one unchanged build in three. **B9 in progress (2026-09-23).** The gate is calibrated against the failure it exists to catch, not set at the specified 0.85 (ADR-22, log #48). A deliberately broken synthesis prompt costs only ~0.05 faithfulness against a 0.02–0.03 noise band, so a per-PR gate on the 25-row dev set would give ~12% false failures — it does not work. CI is now three tiers: **pytest on every push**; a **deterministic retrieval check** as the per-PR blocker (no LLM, seconds, two cached runs agree to three decimals); and **faithfulness nightly on golden**, where the same gap is ~4.4σ. Synthesis is pinned to `temperature=0, seed=0` — half the noise, no quality cost, and the right default for a legal tool regardless of CI. Three workflows and `eval/snapshot.py` are written. **Tier 3 is enabled at 0.83** — three sigma below the measured healthy golden mean (0.871, sd 0.013). Getting there found a harness bug worth more than the threshold: `ragas_eval` never used the plan cache, so faithfulness was partly measuring the planner; pinning plans took golden sd 0.035 → 0.013, where temperature 0 alone had achieved nothing (log #49). **Tiers 1 and 2 are verified against real CI (2026-09-23):** `tests` green; the retrieval gate scores 0.6800 on healthy `main` (identical to local) and 0.3400 on PR #1's seeded `PREFETCH` 50→1 regression, which it fails — while `pytest` stays green on that same commit, which is the argument for tier 2 existing. CI found three bugs local testing could not: `index.count` 404'ing on an empty Qdrant, a Qdrant version mismatch that broke the snapshot restore, and `on: release` firing the faithfulness gate when the *corpus* snapshot was published. **Tier 3 proved too — by failing.** Both arms ran on the runner: healthy `main` mean **0.881** (sd 0.010), grounding rule removed mean **0.844** (sd 0.004). The broken build **passed** a gate set at 0.83, because that threshold was three sigma below a locally measured *healthy* mean and sat below where a broken build lands. Corrected to **0.855**, between the two measured bands, which do not overlap (healthy's worst 0.870 beats broken's best 0.849). Two further faults surfaced. The gate step ended in `| tee`, and GitHub runs steps as `bash -e` without `pipefail`, so **the gate could not fail at any threshold** — fixed with `shell: bash`, after which the re-run produced its first red build (broken 0.839 FAIL, healthy 0.862 PASS; logs #50, #51). And pooling six samples per arm put the real separation at 2.1 sigma, not the 4.9 claimed from three — at 5 repeats the gate is 0.2% false-fail / 2.5% false-pass. **Cadence moved from nightly/3 repeats to weekly/5** (log #52): nightly was $48.60/month against a $50 project ceiling, weekly/5 is $11.65 *and* stricter, because frequency buys latency that is worth little here while repeats buy statistical power. **Then: B10 (Phase B exit report).** Scope from §7 — case-law corpus, query decomposition, the 100-question golden set, and RAGAS as a standing CI gate (faithfulness ≥ 0.85). Phase A left three baselines for later phases to beat: the 12.4-point publication dilution (Phase E), the 22% filtered-recall loss under strict filters (Phase D), and a pilot set too small to resolve differences under 5.6 points (§9.1).

Working mode: Claude writes the code and may edit existing files; new files are handed over as code blocks for the user to create.

## Phase B progress (plan: `tasks/plan.md`, tasks: `tasks/todo.md`, Phase B sections)
| Task | Status |
|---|---|
| B1 Topic scope and source spike | ✅ Done (DAWSON; whole Title 26) |
| B2 Ingest 26 U.S.C. | ✅ Done (10,768 chunks; pilot 0.722 → 0.667) |
| B3 Ingest Tax Court opinions | ✅ Done (9,973 chunks; pilot 0.667 → 0.500) |
| B4 Golden set part 1 | ✅ Done (53 rows; baseline 0.491) |
| B5 Golden set part 2 | ✅ Done (111 rows total; baseline 0.435) |
| B6 Cross-encoder rerank | ✅ Done (shelved as a default; earns its place inside B7's routed path) |
| B7 Query decomposition | ✅ Done (source routing, not rewriting) |
| B7b Dev set + routing precision + golden audit | ✅ Done (pilot criterion met; golden gain not established) |
| B8 RAGAS harness | ✅ Done (faithfulness 0.865 ± 0.035; gate not enforceable per-run) |
| B9 CI + RAGAS gate | 🔶 In progress (design calibrated; workflows written; threshold pending) |
| B10 Phase B exit report | ✅ Done (`eval/results/phase_b.md`) |

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
_Interview-ready versions of these, with the trade-offs behind them, are kept in a working log outside the repo. The measurements they cite are all in `eval/results/`._
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
- Cross-encoder reranking on CPU costs ~35 ms per candidate: 25 candidates ≈ 850 ms, 50 ≈ 1.7 s. `BAAI/bge-reranker-base` (1 GB) is 2.8 s and scores worst; size is not the variable that matters (log #43).
- Recall at the candidate depth is the diagnostic for whether reranking can help at all: golden hybrid Recall@10 0.435 vs Recall@25 0.530 (dev: 0.625 vs 0.750, saturating by 25).
- LLM query rewriting is not free upside: gpt-4o-mini's rewritten sub-queries scored *below* the questioner's own words on this corpus (dev 0.625 vs 0.708). Court prose and statute text are close to how practitioners ask (log #44).
- A router's recall and its precision need different test rows. The dev set had case law in every row's gold until B7b added 13 rows that need none; only then was routing precision measurable (it was 0.600).
- **An LLM step gives the eval a noise floor.** `gpt-4o-mini`'s `seed` is best-effort. On 86 golden rows, routing scores 0.440 ± 0.012 (sd, six plan sets); 16% of questions route differently between runs, and the 45% that differ only in wording cannot move a metric because the search text is the question. Use `--repeats 5`+ and read the standard deviation — a range over three samples gave both 0.035 and 0.006 and misled twice. Plans cache to `eval/results/decompositions.json`; a cached run's latency excludes the ~1.2 s planning call.
- The golden set had no publication gold at all until B7b, despite publications being 7% of the corpus and Phase A's 12.4-point publication-dilution baseline.
- **A correct answer can be unfaithful.** When retrieval misses, the model answers from parametric knowledge and cites a chunk that *was* retrieved but does not state the claim. The citation checker passes it (the citation is exact); only faithfulness catches it. Two golden rows do this in every run (log #47).
- `anthropic` 1.7.0 has no `temperature` on `messages.create` — passing it raises TypeError — and it supports schema-enforced JSON through `output_config` (stricter than OpenAI's json_object, and it requires `additionalProperties: false`).
- The faithfulness judge costs ~$0.45 per 96-row run and ~10 minutes; the full 3-run measurement is $1.56 and 29 minutes.
- **Noise, decomposed:** re-judging identical answers moves faithfulness by sd 0.008 (5% of variance); the planner and synthesis sampling hold the other 95%. Synthesis now runs at `temperature=0, seed=0`, which halved the dev spread (0.033 → 0.016) with no measurable quality cost.
- A broken synthesis prompt (grounding rule removed, citations still demanded) costs only ~0.05 faithfulness. The metric is structurally weak here: the retrieved sources are still the right sources, so most claims stay supported even when the model is not reading them.
- An answer cache is invalid the moment the pipeline changes — the temp-1.0 answers were deleted when synthesis was pinned. Same rule as the plan cache.
- CourtListener's search API works unauthenticated (opinion *text* needs a key; the public page does not). Its coverage of unpublished appellate dispositions is incomplete, so "no appellate opinion found" is not "not appealed".
- 91% of the opinions our case corpus cites are not in it (2,540 cited, 227 held), so a citation-graph hop would mostly dangle — Phase C needs the cited opinions ingested first.
- Embedding runs at 7.0 chunks/s (~105 min for Part 1). Parallel workers are *slower* (3.4/s at 4 workers); CoreML is a wash.

## Environment
- Stack: `docker compose up -d --wait` starts Qdrant (6333), Postgres (**5433**) and Redis (**6380**); 5432 and 6379 are taken locally.
- Tests: `uv run pytest -q` (needs the stack running).
- Knowledge graph: `graphify-out/`; refreshed 2026-09-21 but not committed yet.

## Pending housekeeping
- B1–B5 committed and pushed (2026-09-22). B6, B7, B7b, B8 and B9-so-far are done but uncommitted (54+ files). The remote is `github.com/tpawar03/TaxCite`; the new workflows cannot run until this is pushed.
- If a `venv/` folder reappears, delete it and use a fresh terminal tab.
