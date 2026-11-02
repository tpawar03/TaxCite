# G3 step 4: five dev rows with the client's facts in a document (draft, for your review)

*2026-11-02. Not yet in `eval/dev.jsonl`; nothing has run. Plan: `tasks/todo.md` G3 step 4.*

Each row is an existing reviewed dev row with its client facts taken out of the question and put into a synthetic
uploaded document. The question keeps only what a practitioner would type when the facts are on file. Gold citations
and reference answers are the source row's, unchanged: the law didn't move, only where the facts live.

**Departure from the plan:** the plan said "compound dev rows". The six compound rows (D07–D12) carry almost no
client facts: they are rule-plus-case-law questions ("what factors decide…, and how has the Tax Court applied
them?"), so there is nothing to move. These five are the dev rows whose answer turns on the client's numbers, which
is what step 4 measures.

**What is reported per row (tracked, not gated):** *retrieved*: a chunk of the row's document reached synthesis;
*used*: the answer states the document's facts (the figure the answer depends on); *cited*: a sentence cites the
document. Plus the usual dev correctness from the reference answer. Cost: about 5 × $0.008 = $0.04.

| New id | From | Question (facts removed) | Uploaded document (`client_doc`) | Expected |
|---|---|---|---|---|
| D54 | D13 | My client sold her house. Her intake form is uploaded. How much of the gain can she exclude? | `intake-2025.pdf`: "Client intake, 2025. Filing status: single. Residence: owned and lived in as main home for 3 of the last 5 years. Sold this year; gain on sale $200,000." | All $200,000 (§ 121(a); $250,000 cap, § 121(b)(1)) |
| D55 | D15 | My client itemizes. Her medical bills and AGI are in the uploaded organizer. How much of the medical expense is deductible? | `organizer-medical.pdf`: "Tax organizer, medical. Itemizes deductions: yes. Unreimbursed medical and dental expenses paid: $9,000. Adjusted gross income: $100,000." | $1,500 (over 7.5% of AGI, § 213(a)) |
| D56 | D17 | My client's capital loss summary is uploaded. How much of the loss can they use this year, and what happens to the rest? | `schedule-d-summary.pdf`: "Capital gains and losses summary for the year. Net capital loss: $10,000. Capital gains: none." | $3,000 now (§ 1211(b)), $7,000 carried forward (§ 1212(b)) |
| D57 | D18 | My client got the uploaded 1099-R for a 401(k) withdrawal. What extra tax applies? | `1099-R.pdf`: "Form 1099-R. Payer: Acme Corp 401(k) Plan. Gross distribution: $20,000. Taxable amount: $20,000. Distribution code 1 (early distribution, no known exception). Recipient's age at distribution: 45." | 10% additional tax, $2,000 (§ 72(t)(1)), unless a § 72(t)(2) exception applies |
| D58 | D35 | What percentage of my client's 2023 day care expenses did the child and dependent care credit cover? Her 2023 organizer is uploaded. | `organizer-2023.pdf`: "2023 tax organizer. Filing status: single. Adjusted gross income: $60,000. Day care paid for her 6-year-old, so she could work: $3,000." | 20%, $600 (D35's temporal trap kept: not today's 35%) |

**Row fields** (as golden's adversarial rows): `category: "client_document"`, `source_row`, `client_doc` (the text,
uploaded as a one-page text PDF under the file name above), `gold`, `answer` and `as_of` from the source row,
`reviewed: false` until you approve.

**Your call:** approve as written, or change any question or document. One design choice to confirm: each question
says the document is uploaded ("her intake form is uploaded"), which is how a user would ask. Leaving that out makes
the row harder: the decomposition then has no hint that facts exist, and only the question-wide document search would
find them.
