# TaxCite: Phase F exit report

*2026-10-01. Plan: `tasks/plan.md` (Phase F, and F5b's research plan). Tasks: `tasks/todo.md` F0–F6. Every number
here traces to a file in `eval/results/` or a command under [Reproducing](#reproducing).*

Phase F set out to make every claim an answer shows checkable, and to stop the system answering from nothing. The
spec asked for a self-hosted NLI verifier, a pre-synthesis sufficiency gate, and suppression of anything unverified.
What shipped is different in mechanism and the same in promise: **an LLM verifier checks every sentence against the
source it cites before it is shown, structured synthesis makes every sentence citable, and the sufficiency gate was
measured and left off.** Late in the phase a measurement bug was found and fixed, and the answer format was reworked
so answers state a conclusion again. **Of §9.3's gates, completeness is met (0.994) and entailment F1 is not (0.63
against 0.90).** Correctness is tracked: on golden's authority rows, answers are now both more often right and far more
often checkable than in Phase E.

## What exists

| | |
|---|---|
| Structured synthesis | One JSON item per sentence, its citations an enum of the retrieved sources (none can be invented); an uncited item is dropped; a missing detail is "Not in the sources: …"; a part with nothing answered says INSUFFICIENT EVIDENCE (`generate.STRUCTURED`, F3) |
| Claim verifier | One batched Haiku call per answer: each sentence against the sources it cites (all retrieved pages of a cited opinion count), with the question and the answer as context. A failed sentence is hidden; any verifier error shows nothing unverified (`verify.checked`, F4; ADR-4, ADR-15 revised) |
| Re-cite | A failed sentence may move to the retrieved source that states it; the swap is re-checked by the same prompt; text never rewritten (`verify.RECITE`, F5b) |
| Checked conclusion | Written last in the JSON, shown first as "Short answer: …" only if it answers the question asked and follows from the sentences that passed; cited with theirs; a stray "Yes," dropped on non-yes/no questions (`generate.CONCLUSION`, `verify.conclude`, F5b) |
| Sibling expansion | One extra search inside each of the first three statute/regulation sections found, pooled for the reranker (`decompose.SIBLINGS = 6`, F5b; ADR-1 revised) |
| Sufficiency gate | Built, tested, **off** (`decompose.GATE`; ADR-7/10 revised, F2) |
| API / jobs | `verifying` stage; `hidden_sentences` in the payload; refusals skip synthesis and verification |
| Eval | `eval/f0_verify.py` (verifier spike, NLI comparison), `eval/f4_hide.py` (hiding units), `eval/f5_golden.py` (completeness, abstention, seeded failures, reference audit, latency); `temporal.py` flags `--gate/--no-gate`, `--siblings`, `--conclusion`, `--recite`, `--hide`; every paid run saves after each row and resumes |
| CI | Faithfulness judged with the question as a source; a floor at 0.855, not a detector (ADR-22 revised): **0.951 ± 0.015** at refusals 0.056 (run 36937738414; $6.24, about twice Phase E's, since every answer is now verified). Retrieval gate scores the shipped arm with siblings: **0.760** (run 36937735731) |
| Tests | 297 |

## The gates

| criterion | threshold | measured | |
|---|---|---|---|
| Citation entailment F1, "not supported" class, runtime verifier vs an independent reference (§9.3, ADR-4 revised) | ≥ 0.90 | **0.63** vs Sonnet 5.5 (precision 0.90, recall 0.48; 298 golden pairs); ≈0.72 after Claude read the 40 disagreements (reference right in 27) | **not met** |
| Citation completeness: material sentences cited, as shown | ≥ 0.85 | **0.994** (1,181 of 1,188, golden, shipped pipeline) | met |
| Substantive correctness | tracked; N, κ | 291 answerable golden row-samples, two judges, **κ 0.72**: answered correct ∧ grounded 0.333, correct 0.368, incorrect 0.137, partial 0.454, refused 13 | tracked |
| Tests and both CI gates green on the shipped pipeline | green | tests ✓ (run 36937736469); retrieval gate **0.760** ≥ 0.70 (run 36937735731, with siblings); faithfulness **0.951 ± 0.015** ≥ 0.855 at refusals 0.056 ≤ 0.25 (run 36937738414; Phase E 0.894) | met |

The entailment gate is reported as not met and not reinterpreted. The verifier hides the right things (precision 0.90)
and misses about half of what it should hide: its misses drop a condition or an exception ("§ 280A disallows" where
it only limits; American Eagle coins called collectibles). Seeded wrong-source citations: **77 of 102 caught**.

## How the phase went

**F0: the verifier, before building it.** Five self-hosted models (DeBERTa-v3 base/large, HHEM-2.1, MiniCheck RoBERTa-L
and DeBERTa-v3-L) scored held-out F1 0.22–0.46 against 0.90; a rescue (MiniCheck on the top-3 windows, triage) reached
0.46 and leaked 3 of 52 unsupported claims. An LLM judge, after three input fixes found by reading 40 pairs (it needed
the question, the whole answer, and case names), agreed with a careful read on 15 of 16 single sentences. **ADR-4
revised: the runtime verifier is one LLM call per answer** (~$0.002). F0 also found that 475 of 853 golden sentences
cited nothing: a verifier can only check what is cited.

**F1: rows that test refusing.** 11 dev insufficiency rows (3 partly answerable, with a `parts` field); `parts` added to
golden G-I11.

**F3: make every sentence citable.** Prompting reached 0.60–0.71 completeness. Moving the citation into the output's
shape (JSON items, citations from an enum) reached 1.000 on dev with correctness unchanged (0.373). Faithfulness, as
the CI gate judged it, dropped, because its judge never saw the question; judged with the question, the healthy and
broken builds score the same (0.869 vs 0.870), so the gate became a floor, not a detector (ADR-22 revised).

**F4: hide the sentence, not the part.** On dev, hiding the whole part emptied 64 of 126 answers; hiding the sentence,
9. Neither passed F4's bar, which credited unverified answers for being right from memory; the sentence unit shipped
as a recorded departure (ADR-15 revised).

**F2: the gate, measured and left off.** It refused 23–33 of 126 answerable dev row-samples before writing, against 9
for the shipped pipeline after writing and verifying (ADR-7/10 revised).

**F5: golden, and a bug.** Golden scored completeness 0.996 and entailment 0.63, and suggested a correctness regression
on the authority rows (Phase E 0.369 → 0.260). Diagnosing it found the cause in the harness: **every eval run since F2
had the sufficiency gate on**, though it ships off (`set_verify` set `GATE = not no_gate`). 67 of 324 golden answers
were the gate's refusals. Fixed (`gate=None` keeps what ships) and guarded by a test that fails on the old code.

**F5b: answers that conclude and can be checked.** On the golden rows the gate never touched, the old and new formats
scored alike (0.42 vs 0.40); what remained was real: structured answers listed evidence and rarely stated a
conclusion, and the verifier hid true sentences whose source was never retrieved. Reading all 37 hidden sentences of
one dev sample found the largest cause in retrieval (the right section, the wrong subsection), then citations to a
neighbour of the right source. Three fixes, each measured on dev before golden:

| dev, 126 answers, paired | F4 (shipped) | + siblings (R1) | + re-cite, conclusion (R2, final check) |
|---|---|---|---|
| answered, correct ∧ grounded | 27 | 25 | **36** |
| answered, incorrect | 18 | 11 | 18 |
| answered from memory (ungrounded) | 17 | 5 | 17 |
| refused | 9 | 22 | 15 |
| short answer shown | ~3% | — | 76% of answered |

Shipped as a recorded departure from two pre-registered criteria (short answer on 80%; refusals not higher: only 1 of
the 6 extra refusals replaced a correct grounded answer). A first try at a conclusion, written *first* in the JSON,
was noise (lost 14, won 9): the model committed before reasoning.

## Golden, scored once on the shipped pipeline

| | Phase E (32 authority rows) | Phase F |
|---|---|---|
| correct | 0.396 | **0.469** |
| answered correct ∧ grounded | 0.312 | **0.385** |
| grounded (every claim in the sources) | 0.635 | **0.875** |

All answerable rows (291): answered correct ∧ grounded 0.333, correct 0.368 (statutory 0.488, case law 0.481, compound
0.247, temporal 0.121), incorrect 0.137. Short answer on 231 of 278 answered (83%). Of 1,160 sentences written, 210 hidden
and 34 re-cited; 13 answers emptied. Latency p50 8.3 s, p95 11.8 s (answered); cost $0.0073 an answer.
Siblings: 54 gold sources reached the writer's 8 across 18 rows, 5 lost across 2.

**What each check caught, with examples.**
- *A wrong source, re-cited:* D24's "$15,750" cited Pub 17 p. 3 ("has been increased"); the chart is p. 97.
- *An overreaching conclusion, held back:* D13's "she can exclude the entire $200,000" when no shown sentence gave the
  $250,000 cap; D02's "No, an influencer can't deduct streaming" when the sources say "only if primarily personal".
- *A conclusion that answers another question, held back (after the check was tightened):* D01's conclusion inverted
  the question.
- *G-I11's half answer:* answered its federal half and flagged the state half, 3 of 3.

**Insufficiency rows (no gate):** refused or flagged on 6 rows; G-I11 handled 3/3; answered without flagging: G-I06
3/3 (since Phase B), G-I09 3/3, G-I03 2/3, G-I08 1/3.

## What Phase F got wrong

1. **A harness switch that defaulted the wrong way** voided F5's first golden correctness figures and sent the first diagnosis the wrong way. An
   eval override must mean "as shipped" unless asked; the guard test now enforces it.
2. **Pre-registered metrics that measured the wrong thing, four times:** F3's "answers emptied" ignored uncited
   sentences and "refused" counted caveats; F4's bar credited answers right from memory; F5b's "refusals not higher"
   counted honest refusals as losses. Test a metric on known good and bad cases before trusting it.
3. **Calling noise a result:** the first bottom-line test "lost" 0.04 on dev; paired, it was 14 lost against 9 won.
4. **The grader marks some refusals "correct"** (6 of 22 dev refusals in R1); decision metrics now count answered rows.
5. **The conclusion check passed six wrong short answers in 22 read on golden** (a self-contradiction, two answers to
   questions the corpus can't answer, wrong conditions). Tightened afterwards on dev; its effect on golden is
   unmeasured, since golden was used once.

## Open, for later phases

- Entailment F1 0.63: a stronger verifier model or a tuned prompt, against the frozen pairs (ADR-4).
- Crowd-out: siblings can push a gold subsection out of the 8 (G-T08's $40,400 cap); give siblings their own slots.
- Whole sections never retrieved (D15 § 213, D17 § 1211): retrieval, not verification.
- Unanswerable questions still answered: G-I06, G-I09 (the gate that would catch them refuses too much).
- Temporal rows 0.121 correct on golden.

## Reproducing

```bash
uv run python eval/temporal.py --questions eval/golden.jsonl --rows every --samples 3 --answers-cache eval/results/temporal-answers-f5b.json
uv run python eval/f5_golden.py report --cache eval/results/temporal-answers-f5b.json --prefix f5b
uv run python eval/temporal.py --questions eval/dev.jsonl --rows all --samples 3 --answers-cache eval/results/temporal-answers-f5b-r2.json
uv run python eval/retrieval.py --pilot eval/dev.jsonl --mode hybrid --k 8 --decompose route+statute1+prior0.5-scoped+sib6 --repeats 3
uv run python eval/f5_golden.py audit
```

Results: `temporal-golden-2026-10-01-f5b.json`, `f5b-report.json`, `f5-audit.json`, `f5-seeded.json`,
`f5-reference-check.md`, `temporal-dev-2026-10-01-f5b-r1.json`, `-r2.json`, `-r2d.json`,
`retrieval-dev-2026-10-01-k8-f5b-sib6.json`.
