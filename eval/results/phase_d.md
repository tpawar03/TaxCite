# TaxCite — Phase D exit report

*2026-09-28. Plan: `tasks/plan.md` (Phase D). Tasks: `tasks/todo.md` D0–D8. Every number here traces to a file in
`eval/results/` or a command under [Reproducing](#reproducing).*

Phase D set out to make answers right for the tax year a question is about. The spec's plan was valid-time
metadata, as-of filtering, and amendment versioning at ingestion. A spike before any building found that
retrieval, not time, blocked most of the temporal rows, and that no row needed an earlier version of the text.
So the phase built less of the spec and more of what the rows needed: the statute's effective dates from its own
notes, a statute slot in retrieval, and year-aware synthesis. **The gate is not met:** 4–5 of 11 temporal rows
are answered correctly for their year, against 10 required. D0's baseline was 1.

## What exists

| | |
|---|---|
| Effective dates | `ingest/usc_notes.py`: 1,795 statute chunks carry the latest amendment since 2012, its effective rule and the amendment entry (often the replaced text), in `chunks.effective` and the Qdrant payload |
| Statute slot | Each statutory sub-query also searches the statute alone; one slot is reserved for it (`decompose.STATUTE = 1`, live) |
| Year-aware synthesis | The tax year in the prompt; statute sources marked "Effective: …" when their text took effect after that year or retroactively; rule 6 (state the year; dated text governs its years; don't apply later text to an earlier year) |
| Planner | Today's date in the prompt; "as_of" is the tax year of the return or transaction, not a later event's date |
| Edition filter | `retrieve(..., editions=)`: publications limited to editions near the tax year; built, measured, **off** |
| Transaction time | A trigger keeps every retired chunk version (dropped rows and in-place rewrites) in `chunk_versions`; `store.held_at(citation, at)` |
| Temporal scorer | `eval/temporal.py`: as-of match + reference-answer judge (κ-checked), with a grounding diagnostic |
| Eval sets | 14 dev temporal rows (D26–D39); golden G-T10's answer and G-T05–07's as-of corrected (approved) |
| CI | Retrieval gate scores the shipped arm (`route+statute1`) at 0.70; snapshot `corpus-2026-09-28` carries D4 and D6 |
| Tests | 219 |

## The gate

| criterion | threshold | measured | |
|---|---|---|---|
| Temporal accuracy, golden G-T01–G-T11 (§9.3) | ≥ 90% (10 of 11) | **0.394 ± 0.052** scored once (4–5 of 11); **0.152 ± 0.052** re-scored once after the refusal fix (1–2 of 11) | **not met** |
| Recall@20 regression on other categories | ≤ 2 points | statute slot: all 0.563 → 0.602, no category down; new planner: 0.602 → 0.606, compound −0.8, the rest level or up | met |
| Effective-date accuracy (added in the plan, the §3.2 pattern) | ≥ 90% on a 50-row hand check | **48–49 / 50** on a fresh third sample | met |
| Faithfulness (standing CI gate) | ≥ 0.855, and now refusals ≤ 0.25 | first D7 build: 0.866 **at a refusal rate of 0.52–0.57** (invalidated); fixed build: **0.882 ± 0.011, refusals 0.125–0.156** (run 36381406751, `0f2caf7`) | met |

The gate is **not met**, and not reinterpreted. One golden row is 9.1 points, so the gate allowed one miss;
Phase D misses six or seven. The reasons, row by row, are below. Most are not about time.

Scoring (D2): a row passes when the plan's as-of year matches the row's tax year (two-year rows are scored by
their answer) and `claude-haiku-4-5` grades the answer *correct* against the reference answer. A second
phrasing of the same rubric gives κ = 0.772 on this run (≥ 0.7 required). The golden set was scored once, at
the end; tuning used the 14 dev rows only.

### A gate that passed while the system refused half its questions

The first D7 build gave the year rule (rule 6) to every question. The faithfulness gate on `phase-d` passed
(0.866 ± 0.018, run 36376696743) while **52–57% of golden answers were refusals**, against 12.5% in Phase C.
Refusals sit outside faithfulness's mean by design, and the workflow reports their rate but checks nothing.
Reproduced locally in CI's configuration: 53/96 refusals; without rule 6 and the year header, 13/96; the statute
slot plays no part (52/96 without it). 40 rows refused only under the rule, nearly all undated case-law and
compound questions. **Fix (`0f2caf7`): the rule and the year header go only to questions with a tax year.**
Refusals 13/96 (0.135). Dev temporal accuracy 0.452 → 0.500 (`temporal-dev-2026-09-28-d7fix.json`).
**And the gate now checks it:** `ragas_eval.py --max-refusal-rate 0.25` in the faithfulness workflow, set between the healthy band (0.125–0.135) and the broken one (0.52–0.57), smoke-tested on both paths.

### The same retrieval, a different score

Re-scored once after the fix, as you chose (option b), golden temporal accuracy fell from **0.394 to 0.152**
(`temporal-golden-2026-09-28-d7fix.json`). The retrieved sources are identical, row for row. The fix changed
only wording that doesn't apply to dated questions, and gpt-4o-mini wrote different answers: G-T01 now gets 2016
wrong, and G-T10 and G-T11 were marked down. The temporal scorer caches one answer per row and repeats only the
judge, so its ± is the judge's noise, not the generator's. On 11 rows, answer-level variation from a small prompt
edit (0.394 vs 0.152; 0.452 vs 0.500 on dev) is larger than any effect D7 set out to measure. **Both D7 accuracy
figures are one sample of a brittle generator, not a measured improvement.** The refusal fix, 53 → 13 of 96, is
far outside that noise.

## D0: what the rows needed, before building

The shipped pipeline on the 11 golden temporal rows, judged by hand against the reference answers
(`phase-d-d0-plans-and-answers.json`):

- **1 of 11 correct**, and that one from memory: nothing G-T06 cited had been retrieved.
- **Retrieval blocked 8 of 11.** Temporal gold Recall@20 was 0.200. Each row's hand-written legal-vocabulary
  sub-query ranked its statute 1st–4th within the statute, so the gold was reachable. The question's own words,
  which the pipeline searches with (log #44), found IRS publications instead.
- Put each row in the first bucket that fixes it: answerable from today's text ×4, needs year-aware synthesis
  ×4, needs a date from the statutory notes ×2, **needs an earlier version of the text ×0**, outside every
  source ×1.
- **Decided before building:** no amendment versioning (D5 dropped), effective dates from the notes (D4), and
  a retrieval task the spec didn't have (D3b).

## The ladder

Retrieval, golden, k=20, hybrid + routing + rerank, 5 plan sets (`retrieval-golden-2026-09-27-k20-d3b.json`):

| rung | all scored (86) | statutory (28) | compound (31) | case law (26) |
|---|---|---|---|---|
| hybrid, no routing | 0.504 | 0.357 | 0.398 | 0.808 |
| routing + rerank (shipped before D3b) | 0.563 | 0.500 | 0.459 | 0.777 |
| **+ statute slot (D3b, shipped)** | **0.602** | **0.607** | **0.470** | 0.777 |
| + new planner (D7) | 0.606 (range 0.012) | 0.607 | 0.462 | 0.800 |

The new planner writes more sub-queries (2.34 per question, from 2.05), which raises p50 retrieval latency from 1.75 s to 2.99 s (`retrieval-golden-k20-d7-planner.json`): inside the 35 s budget, but a cost.

Temporal gold Recall@20, golden, on D0's plans (`phase-d-d0-plans-and-answers.json`; command below):

| rung | Recall@20 |
|---|---|
| shipped before Phase D | 0.200 |
| edition filter, same year only (ed0) | 0.350 |
| edition filter, same year and the one before (ed-1; chosen on dev) | 0.250 |
| edition filter ±1 | 0.200 |
| **statute slot** | **0.400** |
| statute slot + ed-1 | 0.400 |

Answers, dev temporal rows (14), 3 judge repeats over the same cached answers:

| rung | temporal accuracy | grounded | as-of | file |
|---|---|---|---|---|
| before Phase D | 0.36–0.43 (12 repeats) | 0.21–0.29 | 0.692 | `temporal-dev-2026-09-27.json` |
| + edition filter (D3) | 0.286 | 0.143 | 0.692 | `…-27-d3.json` |
| + statute slot (D3b) | 0.381 ± 0.041 | 0.21–0.29 | 0.692 | `…-27-d3b.json` |
| **+ year-aware synthesis and planner (D7)** | **0.452 ± 0.041** | 0.21–0.29 | 0.846 | `…-27-d7.json` |
| D7 + edition filter | 0.429 | 0.143 | 0.846 | `…-28-d7ed.json` |

The edition filter improved recall and made answers worse, twice. Removing the 2025 editions removed the only
plain-English evidence about other years: D32's retroactively restored $20,000 Form 1099-K threshold and
D30's "new for 2025". Recall couldn't see it, because D1's gold counts only same-year editions. It stays off.

## The gate, row by row

Golden, D7 configuration, scored once (`temporal-golden-2026-09-28-d7.json`):

| row | grades (3 repeats) | grounded | what decided it |
|---|---|---|---|
| G-T01 | correct ×3 | yes | two years; §67(h) retrieved and read by year |
| G-T02 | incorrect, correct, incorrect | no | "$1,000,000 for 2023", from the 2025 amendment note's replaced text. That was a base amount, inflation-adjusted to $1,160,000 by a Revenue Procedure the corpus doesn't hold |
| G-T03 | incorrect ×3 | **yes** | applies §280E faithfully; the law changed outside the corpus (April 2026 rescheduling). The sufficiency gate's case (Phase F) |
| G-T04 | partial ×3 | no | §67 reached only in part; `wrong_tax_year` twice |
| G-T05 | partial ×3 | yes | the §7503 weekend rule: date arithmetic |
| G-T06 | correct ×3 | no | right from memory; §6501 not retrieved |
| G-T07 | partial ×3 | no | misses the §6651(c)(1) offset: arithmetic |
| G-T08 | incorrect ×3 | yes | refuses: at k=8 the statute slot goes to §225 and §1, not §164(b)(7). The statute slot's recovery of this row was at k=20 |
| G-T09 | incorrect, incorrect, partial | no | the planner put 2026 on an undated question; answers current law without the pre-2023 restaurant exception |
| G-T10 | correct ×3 | yes | "not applicable for 2024", from D4's date |
| G-T11 | correct ×3 | yes | the January 20 cutoff applied to both machines |

As-of extraction 9/10 scored rows; grounded accuracy 0.273 (3 of 11). Judge cost $0.09.

**Of the misses, one is about time as Phase D defined it (G-T02).** The others are retrieval depth (G-T08),
vocabulary (G-T04, and G-T06 by grounding), arithmetic (G-T05, G-T07), a fact outside the corpus (G-T03), and
the planner (G-T09).

## Effective dates (D4)

Two USLM notes answer "when did this text start to apply": the Amendments note (which provision each law
changed) and the Effective Date of Amendment note (when that law applies). The chunker skipped both.

- **Hand checks on three independent samples of 50,** each excluding every key drawn before
  (`phase-d-handcheck-effective-dates.txt`): 40/50, then 40/50 on new failure classes, then **48–49/50**.
  Re-checking the first sample after fixing it would have reported ~100%.
- **Text evidence did most of the work:** an Amendments entry quotes what it inserted, so a link counts only
  if the chunk contains that text. That decides which of several chunks under one label an amendment touched.
  §163(h)(3) is three chunks: the 2025 amendment touched only (F), in part 3. Part 1, the 1987 $1,000,000
  rule D26 needs, correctly carries no date.
- **Coverage:** 1,795 of 2,576 statute chunks amended since 2012 (70%). The rest carry nothing, never a guess.

## Transaction time (D6)

The plan's `retired_at` column would have kept rows the sweep drops, but not text an amendment rewrites in
place: the key is the citation, so the upsert overwrites it. A `BEFORE UPDATE OR DELETE` trigger now copies
every version TaxCite stops holding into `chunk_versions`, and `store.held_at(citation, at)` answers "what did
TaxCite hold on date Y". No reader of `chunks` changed. **Not yet run against a real retired row:** none exists
until a re-ingest changes or drops text (Phase H).

## Failures, with examples

1. **The replaced-text trap (G-T02).** Recovering an earlier version from the notes gives the statute's text
   as it read, not the year's figure: "$1,000,000" was a base amount, indexed for inflation every year.
   Confident and stale. The fix is a rule, not more data: never state an inflation-indexed base amount as a
   year's figure.
2. **Recall at k=20, answers at k=8 (G-T08).** The statute slot put §164(b)(7) in the top 20; synthesis sees 8,
   and one statute slot went to the wrong section. A retrieval metric at a depth synthesis doesn't use
   overstated this row.
3. **Grounded and wrong (G-T03).** Every claim is supported by §280E as written, and the answer is wrong,
   because the controlling fact changed outside the corpus. This is §5.4's point: support is not
   correctness.
4. **Right from memory (G-T06, D35).** The reference-answer judge can't see the sources. D35's "20%" cited a
   page about qualifying children. D2's grounding diagnostic exists for this, and it halves the dev figure.
5. **A filter that removes the evidence (D32).** The edition filter drops Pub 17 (2025), the only retrieved
   source for a retroactive restoration, and the model falls back on a stale memory ($600).
6. **Reference answers that overstated (D30, G-T10).** "The start date is only in the notes" was wrong:
   Pub 17 (2025) states it. Found by D1's second validation scan; fixed with approval.
7. **The planner's year at the edges.** "This year" is now resolved (D36), but an undated present-tense
   question still drew 2026 in some runs (D33, G-T09), and a levy date stood in for the tax year once (D34),
   despite the prompt rule. gpt-4o-mini is not stable here.

## §9.3 recalibration

| what | was | now | why |
|---|---|---|---|
| Phase D gate | ≥ 90% temporal accuracy | unchanged; **not met** (0.394) | not lowered after the fact |
| How it is scored | "accuracy" | as-of match (tax year) + reference judge, κ ≥ 0.7; grounding reported, not gated | D2; decided with you |
| Amendment versioning | ingest earlier release points | not built | D0: no row needs earlier text; the notes quote replaced text where it matters |
| Effective-date extraction | — | ≥ 90% on a 50-row hand check (met: 48–49/50) | the §3.2 pattern, as Phase C's edges |
| As-of filtering | on when a year is extracted | built, off | lost on answers twice (D3, D7) |
| Transaction time | valid + transaction time columns | a trigger and a history table; an audit query, no retrieval mode | the column design lost in-place rewrites |

**Gate resolution:** 11 rows at 9.1 points each. A gate this coarse passes or fails on one or two rows; §9.1's
10 temporal rows are a minimum, and 14 dev rows were needed just to tune.

## What Phase D got wrong

- **Two results files overwritten by same-day runs** (the D2 calibration file, nearly D3's dev file), the
  Phase C mistake again. `eval/temporal.py` now names files by answer cache; the calibration was regenerated.
- **A recall metric blind to a cost I had designed out.** D1's gold counted only same-year editions, so the
  edition filter's loss of cross-year evidence scored as nothing. Only answers showed it.
- **Two reference answers of mine were wrong** (D30, G-T10), in the same way, found only by searching the
  plain-English sources.
- **The plan's transaction-time design** would have kept deleted rows and lost amended text. Caught while
  building it, not in review.
- **A restore bug nearly shipped:** `pg_dump --table` carried D6's trigger but not its function, so CI's
  restore would have failed. Reproduced on a throwaway database and fixed before the snapshot was published.
- **A statute-search result read at the wrong depth:** D3b's golden recovery of G-T08 was at k=20; the
  answer is built from 8.

## Open problems handed on

| problem | owner |
|---|---|
| Statute at synthesis depth: the statute slot at k=8 (G-T08) | open; measure k and the slot count on dev answers |
| Plain-words vocabulary gap to §67, §6501, §6511 (G-T01, G-T04–G-T06) | open |
| Inflation-indexed base amounts stated as a year's figure (G-T02); Revenue Procedures not in the corpus | open; a synthesis rule first, a source later |
| Facts outside the corpus (G-T03) | Phase F (sufficiency gate) |
| Date arithmetic (G-T05, G-T07) | open |
| Planner year stability (G-T09, D33, D34) | open |
| Transaction-time audit on a real retired row | Phase H (the weekly re-ingest) |
| Edition filter | off; revisit only if several editions per publication are ingested |
| Answer-level metrics on few rows sample one answer per row: a prompt-wording change moved golden temporal 0.394 → 0.152 on identical retrieval | open; `eval/temporal.py --samples N` (several generated answers per row) before the next answer-level gate |

## Reproducing

```bash
uv run pytest -q                                                      # 219 tests
uv run python eval/validate_pilot.py eval/golden.jsonl                # 0 of 115 need attention
uv run python eval/validate_pilot.py eval/dev.jsonl                   # 0 of 39
uv run python eval/temporal.py --questions eval/golden.jsonl --repeats 3 \
  --plan-cache eval/results/decompositions-d7.json \
  --answers-cache eval/results/temporal-answers-d7.json               # the gate: 0.394
uv run python eval/temporal.py --questions eval/dev.jsonl --repeats 3 \
  --plan-cache eval/results/decompositions-d7.json \
  --answers-cache eval/results/temporal-answers-d7.json               # dev D7: 0.452
uv run python eval/temporal.py --questions eval/dev.jsonl --repeats 3 \
  --plan-cache eval/results/decompositions-d7.json \
  --answers-cache eval/results/temporal-answers-d7ed.json --editions 1,0   # D7 + filter: 0.429
uv run python eval/retrieval.py --pilot eval/golden.jsonl --mode hybrid --k 20 --repeats 5 \
  --decompose route --decompose route+statute1                        # the ladder
uv run python eval/retrieval.py --pilot eval/golden.jsonl --mode hybrid --k 20 --repeats 5 \
  --decompose route+statute1 --plan-cache eval/results/decompositions-d7.json   # new planner: 0.606
uv run python eval/retrieval.py --pilot eval/dev.jsonl --mode hybrid --k 10 \
  --decompose route+statute1 --plan-cache eval/results/decompositions.json --fail-under 0.70  # CI: 0.720
uv run python -m taxcite.ingest.usc_notes data/raw/usc26@119-110.xml 179   # effective dates for one section
```

Temporal gold Recall@20 on D0's plans (the second ladder table):

```bash
uv run python - <<'EOF'
import json
from taxcite import decompose as dc
plans = json.load(open("eval/results/phase-d-d0-plans-and-answers.json"))
rows = {json.loads(l)["id"]: json.loads(l) for l in open("eval/golden.jsonl")}
for arm, ed, st in [("shipped", None, 0), ("ed0", (0, 0), 0), ("ed-1", (1, 0), 0), ("ed±1", (1, 1), 0),
                    ("statute1", None, 1), ("statute1+ed-1", (1, 0), 1)]:
    hit = n = 0
    for rid, p in plans.items():
        r = rows[rid]
        d = dc.retrieve(dc.Decomposition(r["question"], [dc.SubQuery(k, q) for k, q in p["subs"]], as_of=p["as_of_plan"]),
                        k=20, editions=ed, statute=st)
        got = {h.key for h in dc.chunks(d, 20)} | {h.citation for h in dc.chunks(d, 20)}
        hit += sum(any(g in got for g in grp) for grp in r["gold"]); n += len(r["gold"])
    print(arm, f"{hit}/{n} = {hit / n:.3f}")
EOF
```

Transaction time, the audit query:

```bash
uv run python -c "from datetime import datetime, timezone; from taxcite import store
with store.connect() as c: print(store.held_at(c, '26 U.S.C. § 179(b)(1)', datetime.now(timezone.utc)))"
```
