# TaxCite — Phase B exit report

_Phase B: case-law corpus, decomposition, and the eval infrastructure. Completed 2026-09-23._

Phase B's job was to add statute and case law, build a golden set big enough to resolve
differences, decide whether reranking and decomposition earn their place, and put a
standing regression gate in CI. Every number below traces to a file in `eval/results/`
or to a command in this document. Three of the phase's conclusions are negative, and
they are reported as prominently as the positive ones.

## What exists

| | |
|---|---|
| Corpus | 28,747 chunks: 11,030 statute (26 U.S.C., release 119-110), 9,973 Tax Court opinions (307 opinions via DAWSON), 5,662 regulations (26 CFR), 2,082 IRS publication pages |
| Indexed | 28,393 vectors (dense `bge-base-en-v1.5` 768d + BM25 sparse, RRF fusion) |
| Not indexed, each with a recorded reason | 354: 241 repealed, 41 oversized tables, 39 failed PDF pages, 17 renumbered, 12 tables of contents, 4 other |
| Query path | `POST /queries` → `decomposing → retrieving → synthesizing → answer` over SSE |
| Eval sets | golden 115 rows (86 scored in B), dev 25, pilot 20 |
| Tests | 160 |
| CI | 3 tiers, all verified against real runs (ADR-22) |

## The ablation ladder

86 scored golden rows, k=10, mean of three independently planned sets
(`golden-b7b-repeats3-k10.json`).

| rung | Recall@10 | nDCG@10 | MRR | Section recall | p50 |
|---|---|---|---|---|---|
| hybrid (Phase A's default) | 0.428 | 0.302 | 0.305 | 0.550 | 29 ms |
| + cross-encoder rerank | 0.446 | 0.305 | 0.322 | 0.579 | 844 ms |
| + source routing | 0.442 | 0.311 | 0.321 | 0.578 | 1,382 ms |
| **+ rerank + routing** | **0.452** | **0.315** | **0.325** | **0.609** | 2,195 ms |

By category:

| rung | statutory (28) | case law (26) | compound (31) |
|---|---|---|---|
| hybrid | 0.321 | 0.654 | 0.349 |
| + rerank | 0.321 | **0.731** | 0.333 |
| + routing | 0.357 | 0.641 | 0.366 |
| + rerank + routing | **0.429** | 0.641 | 0.328 |

**Checkpoint 3, answered against the design's own prediction.** Decomposition was built
for compound questions. Compound recall barely moves (0.349 → 0.366, and *down* to 0.328
with reranking). What routing actually helps is **statutory** questions, 0.321 → 0.429,
by keeping 10k chunks of case-law prose out of a pool that should hold statute and
regulations. The mechanism works; the category it was designed for is not the one it helps.

## Phase C's baseline

Graph expansion (§5.3) has to beat this. Decomposition-only, k=20, 26 case-law rows:

| | Recall@20 |
|---|---|
| hybrid | 0.692 |
| **hybrid + routing (decomposition only)** | **0.692** |

Routing adds nothing to case law at k=20 — it is already finding what it can, and the
remaining 30.8% is not in the candidate pool at any depth routing can reach. That is the
gap graph expansion exists to close, and the number it will be measured against.

Overall at k=20: hybrid 0.469 → routing 0.539; statutory 0.357 → 0.500; compound 0.398 → 0.462.

## Faithfulness

Golden set, plans pinned, synthesis at temperature 0, judged by `claude-haiku-4-5`
(the other provider, ADR-11). Six runs per arm across two CI dispatches:

| | runs | mean | sd |
|---|---|---|---|
| healthy | 0.870 / 0.884 / 0.889 / 0.862 / 0.868 / 0.856 | **0.8715** | 0.0127 |
| grounding rule removed | 0.849 / 0.841 / 0.842 / 0.815 / 0.840 / 0.862 | **0.8415** | 0.0154 |

Separation 2.1 pooled sigma, and the bands overlap: broken's best run (0.862) beats
healthy's worst (0.856). The gate survives this because it compares a **mean of five
repeats**, where the standard error is 0.0057 and 0.0069 — at the 0.855 threshold, 0.2%
false failures and 2.5% false passes. It will miss roughly one broken build in forty.

Against §7's specified 0.85: the healthy mean clears it, but a single run does not reliably.
§7's number was a quality target chosen before either band was known; 0.855 is a CI
threshold derived from both. They are different objects and both are now recorded.

## Abstention

| | |
|---|---|
| Unanswerable rows that refused in all 3 runs | **9 of 10** |
| Answerable rows that refused at least once | 10 of 86 (3–7 per run) |

## Failures, with examples

**1. Citation laundering — the phase's most important finding.** `G-S10` and `G-S14`
score 0.00 faithfulness in every run while giving **legally correct answers**. Asked the
real-estate-professional hour threshold, the system answers "more than 750 hours" and cites
`IRS Pub 527 (2025), p. 19`. The gold statute chunk was never retrieved; the model answered
from parametric knowledge and attached a citation to a chunk that *was* retrieved and does
not say it. Phase A's citation checker scores these as **exact** citations and passes them —
it catches invented citations, which it drove to zero, and cannot catch a real citation on
an unsupported claim. Faithfulness is the only check in the system that sees this.

**2. Answers that contradict their own sources.** `G-S03` asks whether a home office
deduction can create a loss. The system answers yes; §280A(c)(5) caps the deduction at
gross income precisely so it cannot. Faithfulness 0.50 — here the legal error and the
unfaithfulness are the same defect.

**3. A citation to the right section but the wrong chunk.** `G-S05` asserts the
"sold to customers in a bona fide transaction" exception citing `1.274-12(c)(2)`. That text
exists in the corpus, but the citation spans **15 chunk parts** and retrieval returned a
different one. The claim is true, the citation is real, and the retrieved context does not
support it.

**4. An unanswerable question that gets answered.** `G-I06` ("How long is the IRS currently
taking to process amended returns?") refuses in **0 of 3 runs**. Nine of the ten
fully-unanswerable rows abstain reliably; this one does not.

**5. Over-refusal on a partial.** `G-I11` asks a federal question and a California question
in one breath. The federal half is answerable (§280A(c)(1) is gold); the system refuses
**both** in all 3 runs. The per-sub-query sufficiency gate (§3.3 step 6) that would drop only
the unsupported half is not built — a Phase C item, now with a test waiting for it.

**6. Retrieval that varies between runs.** `G-C13` retrieved its gold opinion in 1 of 3 runs.
The planner routes 16% of golden questions differently between runs, and different routing
retrieves different evidence.

**7. Statutory retrieval is the weakest category** at 0.321 (hybrid) and 0.429 at best.
47% of golden gold never reaches the top 25 at all (hybrid Recall@25 0.530 against
Recall@10 0.435), which is why reranking alone could not help — B6's finding, and the
reason B7 existed.

## §9.3 recalibration

| what | was | now | why |
|---|---|---|---|
| Faithfulness CI threshold | 0.85, per-PR | **0.855**, weekly | Calibrated between two measured bands rather than set at a quality target. A broken build scores 0.8415 |
| Gate cadence | nightly, 3 repeats | **weekly, 5 repeats** | Nightly is $48.60/month against a $50 project ceiling; weekly at 5 repeats costs $11.65 *and* is stricter. Frequency buys latency, repeats buy statistical power |
| Per-PR blocking | faithfulness | **deterministic retrieval check** | On 25 rows a broken prompt separates at 2.2σ (~12% false failures). The retrieval check needs no LLM, runs in seconds, and two cached runs agree to three decimals |
| Gate's eval set | golden | **dev** for tier 2, golden for tier 3 | A gate firing on every PR is a tuning signal; nightly/weekly bounds the exposure |
| §9.1 category counts | targets | **minimums** | The golden set is 115 rows against a target of 100 |
| Reported spread | single run | **mean and sd over ≥5 plan sets** | Three-sample estimates misled this phase four times |

## What Phase B got wrong

Recorded because the corrections are the phase's real content:

- **Reranking was assumed to help.** It bought +1.7 points for 28× the latency and was
  shelved as a default (ADR-19). It earns its place only inside the routed path.
- **Decomposition was assumed to be query rewriting.** The model's rewritten queries scored
  *below* the questioner's own words (dev 0.542 vs 0.708). What it is good for is routing
  (ADR-20).
- **The eval harness was the noise source, not the model.** `ragas_eval` never used the plan
  cache; pinning plans took golden sd from 0.035 to 0.013.
- **A gate that could not fail.** `| tee` swallowed the exit code under `bash -e`; the
  faithfulness job was green at any threshold against any prompt until `shell: bash` was
  added.
- **Four separate trends read from three samples.** The standing
  rule is now five or more, with a standard deviation rather than a range.

## Reproducing

```bash
uv run python eval/retrieval.py --pilot eval/golden.jsonl --mode hybrid --k 10 \
  --decompose route --decompose route-norerank --repeats 3     # the ladder
uv run python eval/retrieval.py --pilot eval/golden.jsonl --k 20 --decompose route
uv run python eval/ragas_eval.py --repeats 5 --max-cost 5.00 --fail-under 0.855
uv run python eval/validate_pilot.py eval/golden.jsonl