# TaxCite — Engineering Log

Observations and trade-offs from building TaxCite, written to be retold in interviews. Each entry covers what I saw, what I chose, what it cost, and the questions an interviewer is likely to ask.

**Format:** Context → Observation → Decision → Trade-off → Likely questions. The newest entry goes at the bottom. The formal records are the ADRs in `taxcite-technical-documentation.md` §8; this log captures the reasoning and evidence behind them.

## Index
| # | Topic | Area |
|---|---|---|
| 1 | The spec's chunk size didn't survive contact with the data | Retrieval / data |
| 2 | Chunk at legal paragraph designations, only two levels deep | Retrieval / data |
| 3 | Tables: a few huge ones, many small meaningful ones | Retrieval / data |
| 4 | Italic designations are a different hierarchy level | Parsing |
| 5 | The corpus has gaps that shape the evaluation | Evaluation |
| 6 | The source XML already carries temporal signals | Temporal design |
| 7 | Statute source: the origin for content, the mirror for change detection | Ingestion |
| 8 | Qdrant over pgvector, with a measurable revisit trigger | Architecture |
| 9 | Redis vs. Postgres for live progress events | Architecture |
| 10 | Keep live delivery separate from tracing | Reliability |
| 11 | Stay true to the architecture but defer stores until they have work | Delivery / scope |
| 12 | Vercel is the wrong host for this backend | Deployment |
| 13 | The iCloud bug that silently broke editable installs | Tooling / debugging |
| 14 | Table-of-contents sections would poison retrieval | Retrieval / data |
| 15 | Test fixtures chosen from real edge cases, not invented | Testing |

---

## 1. The spec's chunk size didn't survive contact with the data
- **Context:** the design doc (§3.2) specified section-level chunks of 200–500 tokens, chosen because it "mirrors legal citation granularity."
- **Observation:** measuring 26 CFR Part 1 (3,774 sections) showed a median of ~1,000 words (~1,350 tokens) per section, and **74% of sections over 500 tokens**. The largest was 54,667 words (§1.704-1). The spec's assumption was wrong for most of the corpus.
- **Decision:** explore before designing. Download once, count tags, measure length distributions, then set chunking rules from the data.
- **Trade-off:** about an hour of exploration before writing any parser, in exchange for avoiding a parser built on a false assumption.
- **Likely questions:** *How did you choose chunk size?* *What would you do differently on a new corpus?*

## 2. Chunk at legal paragraph designations, only two levels deep
- **Observation:** 30,195 paragraphs start with a CFR designation, `(a)` → `(1)` → `(i)` → `(A)` → `(`*`1`*`)` → `(`*`i`*`)`, six levels. Legal citations already point at these units (`§1.704-1(b)(2)`).
- **Decision:** split at level 1, and at level 2 only when a level-1 unit is over ~500 tokens. Pack neighbouring units up to ~500 tokens. Each chunk's citation is the paragraph path.
- **Trade-off:** citations are precise to two levels, not six. Going deeper means resolving ambiguous designations (`(i)`, `(v)` and `(x)` are both letters and Roman numerals, told apart only by what came before). Deferred until retrieval evaluation shows deeper citations matter.
- **Edge case found:** one paragraph can open two levels at once (`(a) General rule. (1) …`), so the first split piece is cited `(a)(1)`.
- **Likely questions:** *Why not fixed-size or semantic chunking?* (Citation precision is a product requirement, and the document's own structure gives better boundaries than a token counter.) *How deep would you go and why?*

## 3. Tables: a few huge ones, many small meaningful ones
- **Observation:** 2,532 tables. The 5 largest sections hold ~114k of ~180k table cells (§1.72-9 alone has 50,114), all actuarial lookup tables. The median table has only 21 cells, mostly worked tax calculations inside examples. Removing tables barely changed section length (median 1,058 → 1,024 words).
- **Decision:** flatten tables with ≤100 cells into text rows (keeping 90%+ of tables). Larger tables get no embedding and are recorded with the reason `large_table`.
- **Trade-off:** actuarial tables can't be found by semantic search. That's acceptable because they're lookup data, which a future tool can query by structure. Recording them keeps the gap visible instead of hidden.
- **Likely questions:** *How do you handle tables in RAG?* *What happens when a user asks about an annuity factor?*

## 4. Italic designations are a different hierarchy level
- **Observation:** `(<I>2</I>)` is level 5 (italic number), not level 2. Stripping markup before parsing, the obvious approach, would make it look like `(2)` and cause splits at the wrong places.
- **Decision:** read designations from the raw element (the text before the first child tag). Italic designations never count as split points. A test fixture covers this.
- **Trade-off:** none really; it's a correctness trap. It shows that markup carries meaning, and that normalizing text too early loses information.
- **Likely questions:** *What bugs did you catch before they shipped?*

## 5. The corpus has gaps that shape the evaluation
- **Observation:** eCFR has no §1.280A. The home-office regulations were only proposed, never finalized, and the PRD's headline example is a home-office question.
- **Decision:** answer home-office questions from IRS Pub 587 and the statute, and design the pilot set around what the corpus actually contains.
- **Trade-off:** the headline demo question depends on publications and statute more than on regulations.
- **Likely questions:** *How did you build your eval set?* *How do you handle questions the corpus can't answer?* (That's what the sufficiency gate is for.)

## 6. The source XML already carries temporal signals
- **Observation:** each section's `CITA` lists every amendment with its Treasury Decision number and date, and some say "Redesignated", meaning the section was renumbered. Paragraph headings also carry date ranges ("Taxable years beginning after December 31, 1970").
- **Decision:** store `CITA` raw now for Phase D to parse. Store both the eCFR as-of date (valid time) and the download time (transaction time) on every chunk. Paragraph-level chunks keep each date-scoped paragraph separate instead of blending two eras into one vector.
- **Trade-off:** two extra columns now, instead of a migration later.
- **Likely questions:** *How do you handle law that changes over time?* *What's bi-temporal and why does it matter here?* *How do you deal with renumbered sections?*

## 7. Statute source: the origin for content, the mirror for change detection
- **Context:** 26 U.S.C. is available from uscode.house.gov (OLRC, the origin) and GovInfo (GPO, a mirror with a REST API).
- **Decision:** fetch content from uscode.house.gov release points, which are tied to specific enacted Public Laws. Use only GovInfo's "modified since" endpoint, once a week, to detect when Title 26 changed.
- **Trade-off:** two sources to integrate instead of one. In return: one hop from the source of truth, versions tied to real law changes (a better fit for bi-temporal than annual editions), and no rate-limited API on the content path. That lesson came from CourtListener cutting its free tier from 5,000/hr to 125/day in May 2026.
- **Likely questions:** *Why not use the API with the nicer interface?* *How do you detect upstream changes?*

## 8. Qdrant over pgvector, with a measurable revisit trigger
- **Context:** the design picked Qdrant (ADR-6) but never said why it beat other vector stores. An interviewer's first question would be "why not pgvector in the Postgres you already run?"
- **Decision (ADR-17):** Qdrant. It's the only option with native dense + sparse hybrid search, filtering applied during the search rather than after it, free self-hosting, and one lightweight container. pgvector is the strongest rival, since it removes a store and keeps text, metadata and vector together.
- **Trade-off:** one more store to run and back up, and metadata copied between Postgres and the Qdrant payload.
- **What makes it defensible:** a **falsifiable revisit trigger** backed by a planned benchmark (T6b). Reopen the decision if pgvector fits the managed-Postgres storage cap and loses no more than 2 points of recall under strict filters.
- **Likely questions:** *Why Qdrant?* *When would you switch?* *What is filtered-search recall loss?*

## 9. Redis vs. Postgres for live progress events
- **Question considered:** could Postgres `LISTEN/NOTIFY` replace Redis pub/sub and remove a store?
- **For Postgres:** one fewer service, and the job-state update and event can be sent in one transaction.
- **Against it:** the plan hosts Postgres on Supabase, whose pooled connections don't support `LISTEN`. Direct connections are limited, and each open SSE stream would hold one. Redis also gives cache expiry for free, which the cost ceiling depends on.
- **Decision:** keep Redis as specified. If Postgres were self-hosted, it would be close to a coin flip.
- **Likely questions:** *Why add Redis?* *How do you push progress to clients?*

## 10. Keep live delivery separate from tracing
- **Design (ADR-16):** pipeline steps report to Redis for the user's live progress and, separately, to Langfuse for traces. Originally, live events were read out of Langfuse.
- **Trade-off:** two writes per step, in exchange for independent failures. A Langfuse outage costs dashboard data, never the answer the user is waiting on.
- **Likely questions:** *How do you stop observability tooling from becoming a production dependency?*

## 11. Stay true to the architecture but defer stores until they have work
- **Decision:** the architecture stays as specified (five stores), but Phase A runs only Qdrant, Postgres and Redis. Neo4j arrives with the citation graph (Phase C) and Langfuse with tracing. For the Phase A LLM benchmark, cost comes from provider token counts.
- **Trade-off:** the full stack isn't running on day one, but nothing idle gets operated or debugged.
- **Likely questions:** *How did you sequence a system this big as a solo engineer?*

## 12. Vercel is the wrong host for this backend
- **Observation:** a query runs 20–30 seconds across several LLM calls, needs a background worker that outlives the request, holds an SSE stream open, and depends on self-hosted stores and an NLI model.
- **Decision:** serverless (Vercel) is at most for the thin frontend. The backend goes on an always-on host.
- **Trade-off:** more operations work than serverless.
- **Likely questions:** *Why not serverless?*

## 13. The iCloud bug that silently broke editable installs
- **Symptom (in earlier projects):** the virtualenv looked healthy, but `import <own package>` failed with no helpful error. Third-party packages still imported fine.
- **Root cause:** two harmless-looking macOS behaviours combined. iCloud Desktop sync sets the `UF_HIDDEN` flag on dot-prefixed paths, recursively inside `.venv/`. CPython 3.13+ silently skips hidden `.pth` files. Editable installs work entirely through a `.pth` file, so the package showed as installed but was never added to the import path.
- **Fix:** found with `ls -lO` (it shows file flags). The immediate fix was `chflags -R nohidden`. The lasting fix is keeping projects outside iCloud sync (`*.nosync` folders), which TaxCite does, so it uses a normal `.venv`.
- **Trade-off:** a global `venv/` naming workaround worked but became unnecessary cruft once projects moved to a non-synced folder, so it was removed.
- **Likely questions:** *Tell me about a hard bug.* (Silent failure, two independent causes, confirmed with evidence, fixed at the root instead of re-applying a workaround.)

## 14. Table-of-contents sections would poison retrieval
- **Observation:** 178 sections of Part 1 (~158,000 words, about 4% of the corpus) are "Table of contents" listings: nothing but the headings of other sections. Embedded, a block of 40 topic headings is a weak match for almost any query on those topics, so it competes with the rule text that actually answers the question, on every query.
- **Decision:** skip them at ingestion, recorded with `excluded = "toc"` rather than silently dropped. The test is the heading text, not the `-0` section number, because `1.954-0` is "Introduction" and is real content.
- **Trade-off:** the system can't answer "what topics does §1.641(c) cover?" from a TOC chunk. That's a navigation question, not a research question, and the parent-section metadata on each chunk can answer it structurally.
- **Interview framing:** near-duplicate, high-surface-area documents hurt retrieval quality even when they're accurate. Finding them takes looking at the corpus, not just the metrics.
- **Likely questions:** *How do you decide what not to index?* *How do you stop boilerplate from crowding out content?*

## 15. Test fixtures chosen from real edge cases, not invented
- **Context:** the chunker needed a test fixture. The easy path is to hand-write a small, tidy XML sample.
- **Observation:** scanning the real corpus for the hard cases turned up edge cases no invented fixture would have contained: a section whose `N` is a *range* (`1.30C-1 - 1.30C-2`), paragraph-level `[Reserved]` cross-reference stubs, designation ranges (`(a)-(g)`, `(d) through (e)`), compact two-level designations (`(b)(1)`), and the two opposite readings of `(i)`: a letter in `1.42-1` (right after `(h)`) and a Roman numeral in `1.704-1T` (right after `(b)(1)`).
- **Decision:** build the fixture from 9 real sections (58 KB), each chosen because it breaks a specific naive assumption.
- **Trade-off:** a bigger, messier fixture than a hand-written one, and it has to be regenerated if the source format changes. In exchange, every test failure corresponds to a real document that exists.
- **Likely questions:** *How do you test a parser?* *How do you find edge cases?* (Query the corpus for them: for each assumption, search for a document that violates it.)
