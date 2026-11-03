# Checkpoint 2 demo: one question per tenant (G3)

*2026-11-02. Through the running API (`uvicorn … --env-file .env`, tracing on). Two temporary tenants, deleted after;
their keys were never printed. Raw events: `eval/results/g3-demo-2026-11-02.json`. Traces: A `036d8068dd8c268e48cf4e4fff13fc97`,
B `d31fe402c0bf6bb811e3af7c15d8d6ea` (Langfuse). Cost $0.019.*

## Tenant A: own documents, compound question

Uploaded `w2-2025.pdf` (Maria Lopez, Okafor Bakery, Box 1 $48,250) and `intake-memo.pdf` (full-time employee; weekend
cake business on Schedule C since 2023; losses each year; separate account, no business plan, no change after losses;
"enjoys baking as a hobby"; **SSN 123-45-6789**). Both one page, one chunk, no failed pages.

> My client Maria Lopez works full time and runs a weekend cake business that has lost money every year since 2023. Can
> she deduct those losses against her wages, and how has the Tax Court treated side businesses like this? Her W-2 and
> intake memo are uploaded.

Shown (3 of 6 sentences hidden by verification, $0.010):

> Short answer: It depends: Maria Lopez may be limited in deducting her cake business losses against her wages due to
> the nature of her business and its consistent losses [intake-memo.pdf, p. 1], [IRS Pub 334 (2025), p. 43].
> Maria Lopez has reported net losses … for 2023, 2024, and 2025 [intake-memo.pdf, p. 1]. Under IRS rules, a taxpayer can
> usually deduct business losses … but there are limitations if the activity is not engaged in for profit [IRS Pub 334
> (2025), p. 43]. Maria Lopez has a separate bank account …, but she does not have a written business plan and has not
> changed her pricing or methods … [intake-memo.pdf, p. 1].

| Exit-condition part | Result |
|---|---|
| Cites its own document | **yes**: `intake-memo.pdf, p. 1`, for facts only |
| Labelled "client document" from structured fields | **yes**: "Client document"; Pub 334 "IRS publication (not binding)" |
| SSN never appears | **yes**: not in any event or answer (and redacted before storage, G2) |
| Cites the statute and an opinion | **no**: neither reached synthesis (finding 1) |

## Tenant B: asks about A's client by name

> What does Maria Lopez's intake memo say about her cake business losses?

`GET /documents` for B: empty. Client search: 0 documents (B has none). Shown ($0.009):

> The Tax Court has held that vague and general testimony about business expenses is insufficient … [T.C. Memo. 2021-50,
> at *11-12]. Taxpayers must provide adequate records … under section 274(d) [T.C. Memo. 2021-50, at *11-12].

| Exit-condition part | Result |
|---|---|
| Nothing reveals A's document exists | **yes**: no fact from the memo, no name of A's file, B's prompts held no client document |
| B gets "no such document" | **no**: B gets an off-topic answer about substantiation (finding 2) |

## Finding 1: A's question never retrieved § 183 (shipped retrieval, not documents)

The plan was right: a statutory sub-query "activity not engaged in for profit deduction limitation" and a case-law one.
But `dc.retrieve` searches with the **original question**, by design (log #44: Recall@10 0.708 vs 0.542 for the
rewritten text on dev). This question's words ("lost money every year", "deduct those losses against her wages") pull
§ 461(l) excess business losses and § 461(j) farm losses, not § 183, which has "profit" and "hobby" in it. Searching the
sub-query's own text puts § 1.183-2(a) and § 183(a)-(d) first. The same miss happens with the document sentence removed
from the question, so it isn't G3's. The verifier did its job: the three sentences on the for-profit test and the
court's factors cited sources that don't state them and were hidden.

## Finding 2: a question about a document the tenant doesn't have gets a legal answer, not "no such document"

Nothing in the pipeline knows a question is *about* an uploaded document. B's plan fell back to one unrouted search,
which found substantiation case law, and synthesis answered that. Nothing leaked, but the exit condition asks for
"no such document". Adding a "say no such document" rule to every prompt would break the property that a tenant without
documents gets the prompts measured before G3; the alternatives are a rule shown only when the question names a
document (a heuristic) or accepting the answer as is (it reveals nothing).

**Added (your decision, 2026-11-02): the guarded rule, then a note in code.** A question naming an upload
(`generate.DOCUMENT_ASKED`: "upload(ed)", "attached", "intake", "organizer", "workpaper", "memo" but not "T.C. Memo.";
matches only G-A01..G-A07 among the golden and dev questions) first got a prompt rule (rule 11: "no such document is on
file", don't answer from other sources). Re-run live ($0.008): **gpt-4o-mini ignored it**: it wrote "Maria Lopez's
intake memo indicates that she reported losses" cited to a cookie-business opinion (the verifier hid it) and no
not_answerable entry. So with no documents on file the note is now added in code, as a skipped part, and the prompts
stay the ones measured before G3; rule 11 is sent only to a tenant who has documents. Re-run ($0.009,
`g3-demo-2026-11-02-rule.json`, `B_code_note`):

> Part 2: The client's uploaded documents
> INSUFFICIENT EVIDENCE: no such document is on file.

after a Part 1 still answering substantiation law from T.C. Memo. 2021-50 (2 sentences hidden). Nothing of A's is
revealed. **B gets "no such document": yes**, alongside the off-topic part. Dropping that part too (when the question
asks only what a document says) would need deciding which questions are document-only: not done.

Tenant A re-run with the rule present ($0.012): still no statute (finding 1 stands); cited both documents and
T.C. Memo. 2025-80; 5 sentences hidden.

## For your review

Leakage harness: green (322 tests). Open: finding 1 (retrieval) and whether B's off-topic part should go.
