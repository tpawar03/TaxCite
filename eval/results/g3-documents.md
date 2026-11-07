# G3 step 4: client facts from an uploaded document (dev, tracked not gated)

*2026-11-02. Rows: `eval/dev-documents.jsonl` (D54–D58, approved; their source rows D13, D15, D17, D18, D35). Runner:
`eval/g3_documents.py`. Raw: `eval/results/g3-documents-2026-11-02.jsonl`. Shipped pipeline, one fresh tenant per row.
$0.028 for five rows, plus $0.008 for one diagnostic re-run of D55.*

| Row | Retrieved | Cited | Used | Gold cited | Hidden | Reading |
|---|---|---|---|---|---|---|
| D54 home sale | yes | yes | yes ($200,000) | yes | 1 | **Correct**: all $200,000, § 121(a) and (b)(1), the doc cited for the facts only |
| D55 medical | yes | yes | no | no | 5 | **Not answered**: states the doc's $9,000 and $100,000, nothing else survives. Public retrieval missed § 213 (below) |
| D56 capital loss | yes | yes | yes ($7,000) | no | 3 | **Right figures, wrong support**: every law sentence hidden; the short answer ($3,000 now, $7,000 carried) is shown cited only to the client's document (below) |
| D57 early 401(k) | yes | yes | no ($2,000 unstated) | yes | 0 | **Correct in substance**: 10% additional tax under § 72(t)(1), age 45 and code 1 from the 1099-R; doesn't compute $2,000 |
| D58 day care 2023 | yes | no | no | no | 0 | **Acceptable refusal**: "not provided in the sources" for 2023, which D35's reference accepts; it did not apply today's 35% |

**Retrieval of the document: 5/5. Cited: 4/5** (the fifth refused, correctly). The document path works: the facts were
found, fenced, cited as the client's record, and labelled "Client document".

## Finding 1: taking facts out of the question changes public retrieval (D55)

D15 asked "paid $9,000 of unreimbursed medical bills on $100,000 of AGI"; D55 asks about "her medical bills and AGI".
Its decomposition searched "medical expense deduction limit based on adjusted gross income for itemized deductions",
which reached § 223 and § 220 (HSA and Archer MSA coordination), never § 213. The verifier correctly hid the one rule
sentence that cited § 223(f)(6) ("addresses HSA coordination only"). Not a document bug: the question's own details
were helping retrieval. Decomposition can't see the document's facts, because they are retrieved after it plans.
Recorded; a second decomposition pass over retrieved client facts would be the fix, and isn't in G3's scope.

## Finding 2: a conclusion can state law on a client document's authority (D56)

Every law sentence of D56 failed verification and was hidden. The one kept statement was the document's fact ("net
capital loss of $10,000"), and the conclusion check (Claude Haiku, `verify.conclude`) still passed "$3,000 now, $7,000
carried forward", a rule the statements don't contain, against its own instruction. The conclusion inherits its
citations from the kept statements it rests on, so the $3,000 limit is shown cited to `schedule-d-summary.pdf`: a rule
of law on a client document's authority, the thing rule 10 forbids. The figures happen to be right; the support isn't.

Proposed fix (deterministic, one condition in `verify.checked`): **a conclusion whose citations are all client
documents is dropped**, since documents can establish facts, never the rule. It can only fire when documents are among
the sources, so no measured answer changes. **Added (your decision, 2026-11-02):** `verify.checked`; the test replays D56's shape (conclusion check passes, only a document cited) and fails with the guard off. D56 not re-run live: the guard is deterministic, and under it D56 would show only the document's fact.

## What this does not measure

Correctness here is read by hand from the reference answers, not judged; five rows is a smoke test of the path, not a
rate. The tax year line reads 2026 on D54–D57 (the question names none, so the model used today's date), a known
behaviour from D7, not new to documents.
