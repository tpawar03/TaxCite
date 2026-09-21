# TaxCite — Phase A exit report

_Phase A: core retrieval baseline. Completed 2026-09-21._

Phase A's job was to build single-hop hybrid retrieval over federal regulations and
IRS publications, measure it against a pilot set, and settle the architecture
decisions §7 deferred. Every number below is reproducible from `eval/` against the
running stack; nothing here is estimated.

## What exists

| | |
|---|---|
| Corpus | 5,662 chunks of 26 CFR (21 topic-scoped section families) + 2,082 chunks of 6 IRS publications |
| Indexed | 7,652 vectors in Qdrant (dense `bge-base-en-v1.5` 768d + BM25 sparse) |
| Not indexed, recorded with a reason | 41 oversized tables, 39 failed PDF pages, 12 tables of contents |
| Query path | `POST /queries` → durable job record → SSE stage events → one buffered answer |
| Tests | 95 |

## The ablation ladder so far

18 pilot questions with gold citations, k=10, reproducible across runs.

| rung | Recall@10 | nDCG@10 | MRR | Section recall |
|---|---|---|---|---|
| sparse (BM25 only) | 0.444 | 0.232 | 0.120 | 0.722 |
| dense only | 0.583 | 0.401 | **0.315** | 0.667 |
| **hybrid (dense + sparse, RRF)** | **0.722** | 0.385 | 0.214 | **0.778** |

Answer quality, same questions, graded on §9.2's rubric by a judge from the other
provider (Cohen's κ = 0.81, above §9.2's 0.70 threshold):

| model | mode | correct | outright wrong | gold citation found | fabricated citations |
|---|---|---|---|---|---|
| gpt-4o-mini | closed-book | 0.44 | 0.06 | 0.00 | 0 |
| **gpt-4o-mini** | **RAG** | **0.61** | **0.00** | 0.33 | 1 |
| claude-haiku-4-5 | closed-book | 0.28 | 0.06 | 0.00 | 0 |
| claude-haiku-4-5 | RAG | 0.33 | 0.06 | **0.50** | **0** |

**Retrieval's contribution, measured:** +0.17 correctness on gpt-4o-mini, and outright
wrong answers fall to zero.

## Decisions settled, with the evidence

| Decision | Outcome | Deciding measurement |
|---|---|---|
| ADR-11 LLM | `gpt-4o-mini` at all call sites | correct 0.61 vs 0.33; 3× faster; 8× cheaper. Cost was **not** the constraint: ~$0.10/mo at persona volume against a $50 ceiling |
| ADR-17 vector store | Qdrant confirmed over pgvector | lexical ranking 0.444 (BM25) vs 0.111 (`ts_rank_cd`); filtered recall identical; storage would have fitted |
| ADR-18 embedding model | `bge-base-en-v1.5` (768d) | +8.3 recall, +12.3 nDCG, +13.0 MRR over `bge-small` on deterministic dense metrics, at 3.4× index time |
| §11.1 statute source | uscode.house.gov for content; GovInfo for change detection | decided on release-point granularity and rate-limit independence; ingestion is Phase B |

## Known failures, with examples

**1. Retrieval finds the section but not the paragraph.** Section recall is 0.778
against strict recall 0.722, and the gap is concentrated: P05 returns the *examples*
of the de minimis safe harbor (`1.263(a)-1(f)(7)`) rather than the rule
(`1.263(a)-1(f)(1)`). Illustrative text out-competes the rule it illustrates.

**2. A plausible near-miss on leased cars.** P09 asks about a leased business car;
retrieval returns `1.280F-7(b)`, which covers listed property **other than** passenger
automobiles. The correct paragraph is `(a)`. Wrong, and wrong in a way that reads right.

**3. Adding publications made regulation retrieval worse.** On the same 16 regulation
questions, hybrid recall fell 0.812 → 0.688 when IRS publications were added, because
publications paraphrase the question's own wording. The constructive-receipt regulation
fell to rank 10; travel substantiation to rank 18. This is the measured case for Phase E.

**4. The closed-book baseline cited a dead publication.** Asked about hobby-loss factors
with no sources, the model recommended **IRS Publication 535** — discontinued after 2022.
Plausible number, right topic, gone. That is the failure mode the product exists to prevent.

**5. Answers omit material conditions.** Every "partial" grade in the benchmark carried
the same defect tag: `missing_condition`, 39 of 39. Answers are rarely wrong; they are
incomplete in a specific, repeatable way.

## Recalibration notes for §9.3

Phase A's thresholds were set before any data existed. What the measurements suggest:

- **Phase B RAGAS faithfulness ≥ 0.85** — plausible but untested here; no RAGAS run yet.
- **Phase C case-law Recall@20 delta ≥ 5 points** — reasonable, but note the pilot set
  cannot resolve differences below ~5.6 points (one question of 18). The 100-question
  golden set is what makes a 5-point gate meaningful.
- **Phase E authority reranking** now has a concrete baseline to beat: restore the 12.4
  points that publications cost, without losing publication answers.
- **Phase F citation entailment F1 ≥ 0.90** — untested, but note `missing_condition`
  dominates defects, so a completeness metric may bind before entailment does.
- **New, unplanned finding:** approximate search returns only **77.9%** of the exact
  top-10 under a strict single-section filter, in **both** Qdrant and pgvector. Phase D's
  as-of filtering is exactly this shape and will need exact search or a raised `ef_search`.

## What Phase A did not do

- No statute (26 U.S.C.), no case law, no citation graph, no temporal filtering, no
  authority metadata, no sufficiency gate, no claim verification, no multi-tenancy.
- The corpus is **topic-scoped**: 21 section families of Part 1, not all 43,583 chunks.
- The gold set was verified against the regulation text, **not reviewed by a tax
  professional**. This limitation belongs next to any published number.
- 18 questions is a small instrument: one question is 5.6 points.
