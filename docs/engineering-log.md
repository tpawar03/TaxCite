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

## 16. Parallel workers made embedding slower, not faster
- **Context:** Part 1 produces 44,250 chunks (43,919 indexable, averaging 270 tokens). Embedding them locally with `bge-small-en-v1.5` runs at 7.0 chunks/s, about 105 minutes for one pass. T6 re-indexes once per candidate model, so the rate is worth measuring rather than assuming.
- **Observation:** the obvious optimisation, multiprocess workers, made it **worse**: 7.0/s single-process, 4.6/s with auto-parallel, 3.4/s with four workers. Apple's CoreML backend was a wash (8.5/s vs 8.7/s). The ONNX runtime already threads across cores, so extra processes contend for the same cores and add spawn and serialisation overhead.
- **Decision:** keep the defaults; leave `parallel` as an explicit argument rather than a default, with the measured numbers in the docstring so nobody "optimises" it back.
- **Trade-off:** ~105 minutes per full index pass, accepted. The lever that actually helps is indexing a subset during the benchmark loop, not more processes.
- **Interview framing:** measure before optimising, and keep the measurement next to the code so the non-obvious result isn't undone later.
- **Likely questions:** *How did you speed up indexing?* *Why isn't it parallel?*

## 17. The chunker's output is 12× the section count
- **Observation:** 3,774 sections became 44,250 chunks, one per 85 words of regulation. Paragraph-level chunking multiplies the index, and that ripples: index size, embedding time, and how many chunks a query must rerank.
- **Decision:** accept it for Phase A and measure the consequences (T6b covers index size against the managed-Postgres cap, which is exactly where this could bite).
- **Trade-off:** more, smaller chunks make retrieval sharper and citations precise, at the cost of a bigger index and a harder reranking job.
- **Likely questions:** *How big is your index?* *What does chunk granularity cost you?*

## 18. The counts-match check caught silent data loss
- **Context:** T2's acceptance criterion was "Postgres and Qdrant chunk counts match". It looked like box-ticking next to the interesting retrieval work.
- **Observation:** the first real ingest parsed 5,056 chunks and stored 4,902. **154 chunks vanished with no error.** Cause: sections like §1.61-21 (fringe benefits) embed their own outline in an `<EXTRACT>` element, repeating every paragraph heading. The parser read those copies as real paragraphs, which restarted the numbering, so eleven different chunks claimed the citation `1.61-21(a)(1)` and the upsert overwrote them one by one. The unit tests all passed: the nine-section fixture had no in-section outline.
- **Decision:** two fixes, because silent loss of legal text is the worst failure mode here. (1) `EXTRACT` becomes one opaque text block that never contributes paragraph structure, which is also right for quoted statute. (2) `part` is renumbered per citation across the whole section, so a key is unique by construction rather than by assumption.
- **Trade-off:** in-section outlines stay in the index as text (they are short and attached to the paragraph that introduces them) rather than being detected and dropped. Detecting them reliably is a bigger job than it is worth right now.
- **Verification:** zero duplicate keys across all 43,583 chunks of Part 1, plus two regression tests built from the real structure.
- **Interview framing:** the boring invariant found the bug that 40 passing unit tests missed, because it was the only check that compared what went in with what came out. Fixtures show you what you thought of; counts show you what you didn't.
- **Likely questions:** *How do you know your pipeline didn't drop data?* *What did your tests miss and why?*

## 19. Hybrid retrieval is not uniformly better than dense
- **Context:** ADR-6 chose Qdrant's dense+sparse hybrid over a separate lexical engine, on the reasoning that legal text needs literal matching ("§280A", "Form 8829") alongside meaning.
- **Bug found first:** the collection was created with plain sparse vectors, without telling Qdrant they are BM25-style (the IDF modifier). Without it there is no inverse-document-frequency weighting, so words appearing in nearly every regulation ("activity", "taxable", "section") scored like rare ones. Fixed for new collections, and switched on for the existing one in place via `update_collection`, with no re-embedding.
- **Observation, after the fix:** which mode wins depends on the query's shape. On a natural-language question ("does time spent on an activity matter for hobby loss rules?") dense ranked the correct paragraph 3rd while hybrid pushed it to 5th, because BM25 matched common legal vocabulary. On citation-style and term-style queries ("section 183 activity not engaged in for profit", "listed property inclusion amount lease") hybrid matched or beat dense. Swapping RRF for distribution-based fusion did not change the pattern.
- **Decision:** ship all three modes (`sparse`, `dense`, `hybrid`) as the ablation ladder's first rungs and let the 20-question pilot set decide, rather than tuning fusion by eye on one query. This is precisely what the §9 ladder exists to answer.
- **Trade-off:** no tuning now, and a real answer later. The risk is shipping a default (hybrid) that the measurement may overturn.
- **Interview framing:** "hybrid search is better" is a claim, not a fact. It was true for two query shapes and false for a third, on the same corpus and index.
- **Likely questions:** *Why hybrid?* *How do you know it helps?* *What is the IDF modifier and why does BM25 need it?*

## 20. The measured ablation overturned what one query suggested
- **Context:** while building search I compared modes by eye on a single question and concluded hybrid was worse than dense: it pushed the correct paragraph from rank 3 to rank 5 (log #19).
- **Observation, on 16 pilot questions:** hybrid is clearly best.

  | mode | Recall@10 | nDCG@10 | MRR | Section recall | natural-language | keyword |
  |---|---|---|---|---|---|---|
  | sparse | 0.500 | 0.387 | 0.216 | 1.000 | 0.333 | 1.000 |
  | dense | 0.719 | 0.445 | 0.301 | 0.938 | 0.708 | 0.750 |
  | hybrid | **0.812** | **0.468** | 0.246 | 1.000 | 0.750 | 1.000 |

- **What the split by query style shows:** sparse is perfect on keyword-style questions and poor on natural-language ones (0.33); dense is the mirror image and more even. Hybrid inherits the better half of each. That is the actual argument for hybrid retrieval, and it only appears when the questions are split by style.
- **The most useful number is the gap:** section recall is 1.000 while strict recall is 0.812. Retrieval nearly always finds the right *section* and sometimes returns the wrong *paragraph* of it. That gap is the budget available to reranking (Phase E), quantified before the work starts.
- **Dense keeps the best MRR (0.301)** despite worse recall: it ranks its correct hit higher, while hybrid finds more correct chunks slightly lower down. Fusion trades precision at rank 1 for coverage.
- **Decision:** hybrid stays the default; the per-style numbers go in the eval dashboard rather than one aggregate score.
- **Interview framing:** I formed a hypothesis from one query, wrote it down, then the measurement contradicted it. The eval set exists precisely because intuitions about retrieval are unreliable.
- **Likely questions:** *Did hybrid help?* *By how much, and on what kind of query?* *What is your reranking budget?*

## 21. Gold sets need validating before they can validate anything
- **Context:** the pilot set is the yardstick for every retrieval number in Phase A, and the user is not a tax professional, so "these answers look right" was not available as a check.
- **Decision:** two safeguards. (1) Every reference answer is a paraphrase of one specific paragraph, so checking it is reading comprehension rather than tax expertise: the claim sits beside the regulation text and either matches or does not. (2) A validator (`eval/validate_pilot.py`) runs before any scoring and checks each gold citation exists in the corpus, is not an excluded chunk, shares vocabulary with its answer, and is reachable by retrieval at all.
- **What it caught:** a wrong gold citation (the accounting-method consent rule is §1.446-1(e)(2), not (e)(1), which is about *adopting* a method), an answer missing the >50% business-use condition for section 179, and a gold citation that was too generic (a roof replacement is a *restoration* under 1.263(a)-3(k)(1), not just the general rule in (d)).
- **Trade-off:** three questions have gold that retrieval cannot currently reach. They are kept and marked `expect_hard`, so the validator reports them as expected rather than hiding them, and the scorer still counts them as failures.
- **Stated limitation:** the gold set was verified against the regulation text, not reviewed by a tax professional. That belongs next to any published number, exactly as §9.2 discloses the limits of AI-judged correctness.
- **Likely questions:** *How do you know your eval set is right?* *What happens when your gold data is wrong?*

## 22. Choosing a PDF library by measuring it on the real document
- **Context:** IRS publications are two-column PDFs. The obvious library, pypdf, is already a common default.
- **Observation, on real pages of Pub 587:** pypdf's default mode read the columns in the right order but broke words apart ("Y ou do not meet the requirements"), 41 artifacts on one page. Its layout mode fixed the words but **interleaved the two columns**, producing sentences like "You do not meet the requirements of the exclusive use is not a trade or business". pdfminer.six produced zero broken words and correct column order, in 1.9s for 35 pages.
- **Decision:** pdfminer.six; pypdf and fontTools removed from the dependencies.
- **Trade-off:** pdfminer is slower per page than pypdf, which does not matter for a weekly ingest.
- **Interview framing:** the failure mode that matters (silently garbled sentences) is invisible unless you read the extracted text. Both pypdf modes "worked" in the sense of returning text.
- **Likely questions:** *How do you extract text from PDFs?* *How did you pick the library?*

## 23. A discontinued publication returns HTTP 200 with an HTML page
- **Observation:** IRS Publication 535 (Business Expenses) was discontinued after 2022. Its URL, `irs.gov/pub/irs-pdf/p535.pdf`, still responds **200 OK** and redirects to a human-readable "Guide to business expense resources" page. The ingest saved 114 KB of HTML as `p535.pdf` and only failed later, inside the PDF parser.
- **Decision:** verify the content, not the status code: a download whose first bytes are not `%PDF-` is deleted and reported with a message naming the likely cause. Pub 535 was replaced with 946 (How To Depreciate Property) and 527 (Residential Rental Property), which match the pilot topics.
- **Trade-off:** one magic-byte check, in exchange for never silently indexing a web page as if it were tax guidance.
- **Interview framing:** upstream sources change under you, and a 200 is not proof you got what you asked for. This is the same class of problem as CourtListener's rate-limit change (§11.7), and both are why the ingest validates rather than assumes.
- **Likely questions:** *What happens when a source disappears?* *How do you detect bad ingests?*

## 24. Adding a second corpus made retrieval worse, and that is the argument for authority-aware ranking
- **Context:** Phase A's ablation had regulations only. Adding 2,083 chunks of IRS publications should, intuitively, only help: more of the corpus a tax preparer actually uses.
- **Observation:** on the **same 16 regulation questions**, hybrid recall fell from **0.812 to 0.688** (-12.4 points). Three questions went from a hit to a complete miss. The gold regulation for the constructive-receipt question fell to rank 10; for travel substantiation, to rank 18.
- **Why:** publications are written in the same plain English as the question. Pub 334 says "you can't cash or deposit the check until the following year"; the regulation says "credited to his account, set apart for him, or otherwise made available". Semantic similarity rewards the paraphrase, so explanatory guidance outranks binding law.
- **Decision:** keep both corpora and do not tune the ranking by hand. This is the precise failure that ADR-8 (authority-aware reranking, Phase E) exists to fix, and it now has a measured baseline to beat: restore the 12.4 points without losing the publication answers.
- **Nuance worth stating:** the publication hit at rank 1 is not *wrong* for a preparer, it is just not *authority*. The product requirement is a cited answer that stands up, so the ranking has to know statute outranks regulation outranks publication, rather than treating relevance as one number.
- **Interview framing:** more data is not automatically better retrieval. Mixing authority levels in one flat index dilutes precision, and measuring before and after is the only way to see it.
- **Likely questions:** *Why authority-aware reranking?* *What happened when you added a second source?* *How will you know reranking worked?*

## 25. Screen candidates for viability before measuring their quality
- **Context:** ADR-18 needed an embedding model chosen by measurement. The obvious shortlist put a long-context model (`nomic-embed-text-v1.5`, 8192 tokens) against the small default.
- **Observation:** nomic embeds at **0.2 chunks/s** on this CPU — 8.6 hours for one pass of a 7,652-chunk corpus — and **491 ms per query embed**. The quantised variant was no faster, so the cost is the model, not the precision. With three sub-queries per question that is ~1.5s of embedding before retrieval even starts, against a 35s end-to-end budget, for a context window the corpus never uses (chunks cap at ~500 tokens).
- **Decision:** exclude it on latency and write the reason into the benchmark file, so the exclusion reads as a decision rather than an oversight. Benchmark quality only among candidates that could actually be deployed.
- **Trade-off:** a model that might score better never got a quality score. That is the right order: quality on an unusable model is a number you can't act on.
- **Result of the actual comparison:** bge-base beat bge-small on every quality metric (hybrid recall 0.667 vs 0.611, nDCG 0.350 vs 0.259, dense MRR 0.315 vs 0.185) at 3.4x the index time and 2x the storage. Chosen, because the ranking gains land where synthesis reads.
- **Likely questions:** *How did you choose your embedding model?* *Why not the model with the best benchmark scores?*

## 26. The benchmark died because of software that had nothing to do with the project
- **Observation:** the first benchmark run failed 80% of the way through the second index build with a bare `"timed out"` from the Qdrant client. The cause was not the code: 17 containers from an unrelated demo stack were running on the same machine, holding load average between 6 and 12, and a bulk upsert of 768-dimension vectors exceeded the client's short default timeout. An earlier test failure in the same period had the same root cause and passed when re-run alone.
- **Decision:** raise the client timeout to 120s and retry upserts with backoff, rather than treating a slow host as a fatal error. Then stop the unrelated containers and re-run for timing numbers worth recording.
- **Trade-off:** retries can mask a genuinely failing store. Acceptable here because the sweep and the Postgres/Qdrant count check would catch a partial index.
- **Interview framing:** "self-hosted on one box" means sharing that box. The failure surfaced as a one-word error 20 minutes into a job, which is the kind of thing that makes benchmarks quietly unreproducible — and it is why the numbers in ADR-18 were re-measured on a quiet machine rather than salvaged from the first run.
- **Likely questions:** *How do you make benchmarks reproducible?* *What did you do when infrastructure failed mid-run?*

## 27. ADR-17 confirmed, but the revisit trigger I wrote was mis-specified
- **Context:** ADR-17 chose Qdrant over pgvector by reasoning, and set a falsifiable revisit trigger: reopen if the corpus fits a managed-Postgres free tier and pgvector's filtered recall is within 2 points.
- **Measured (T6b, identical bge-base vectors copied into both stores, 18 pilot questions):**

  | store | hybrid recall | dense only | lexical only | filtered recall | p50 | p95 | storage |
  |---|---|---|---|---|---|---|---|
  | Qdrant | **0.667** | 0.583 | 0.444 (BM25) | 0.779 | 14 ms | 61 ms | 24 MB vectors |
  | pgvector | 0.500 | 0.528 | 0.111 (`ts_rank_cd`) | 0.779 | 52 ms | 130 ms | 77 MB total |

- **Both of my trigger's conditions passed.** Storage: 77 MB now, ~386 MB projected with case law, inside a 500 MB free tier. Filtered recall: **identical**, which disproves the assumption I wrote the trigger around — that pgvector's post-filtering would lose recall. At this corpus size it does not.
- **The deciding number was not in the trigger.** pgvector's hybrid recall is 16.7 points lower, and isolating the halves shows why: dense is close (0.528 vs 0.583), but Postgres full-text ranking is not BM25 and scores **0.111 against 0.444** on the same queries. ADR-6 chose hybrid retrieval precisely because legal text needs literal matching, so a store that cannot rank lexically defeats the design.
- **Decision:** ADR-17 confirmed, Qdrant stays; the trigger gains the condition it should have had (hybrid recall within 2 points), and the benchmark script prints all three conditions with pass/fail so the verdict cannot be read off one number.
- **Interview framing:** a falsifiable trigger is better than an unexamined decision, but writing one is itself a design act that can be wrong. Mine tested the hypothesis I happened to have (filtering) instead of the property that mattered (lexical ranking), and the measurement is what exposed that.
- **Likely questions:** *Why not pgvector?* *What would change your mind?* *Has a decision of yours survived contact with data?*

## 28. One tied score made the eval unreproducible
- **Observation:** the same data and code gave hybrid recall of 0.722 on one run and 0.667 on the next. Dense was stable every time; query vectors were byte-identical across processes; individual queries repeated within a process were stable. Exactly one question flipped, P02, whose gold chunk sat at **rank 10 of 10**, tied at score 0.1429 with another chunk. Whichever of the two the store kept when it cut at k decided whether the question counted as a hit.
- **Decision:** over-fetch 20 extra results and break ties by citation before truncating to k, so the cut happens in our code and is deterministic. Five consecutive runs then produced identical numbers, and a regression test pins it.
- **What this says about the numbers already reported:** with 18 questions, one question is 5.6 points, so differences smaller than that are noise. The bge-base vs bge-small *hybrid* gap was exactly 5.6 points — within jitter. That decision stands on the deterministic dense metrics instead (recall +8.3, nDCG +12.3, MRR +13.0), and ADR-18 now says so.
- **Interview framing:** an eval that is not reproducible cannot support a decision, and the failure looked like model quality rather than a tie-breaking bug. It also sets the floor on what the pilot set can resolve, which is the concrete argument for the 100-question golden set in Phase B.
- **Likely questions:** *How do you know a 5-point improvement is real?* *How many eval questions do you need?*

## 29. The closed-book baseline cited a publication that no longer exists
- **Context:** T7 added answer generation in two modes so the §9 ablation ladder has its bottom rung: `closed_book` (no sources) against `rag` (retrieved chunks, citation required per claim).
- **First real run, same question** ("does time and effort matter for hobby loss?"), gpt-4o-mini:
  - **RAG:** cited `26 CFR 1.183-2(b)(3)` — the exact paragraph, copied character-for-character from the source header, nothing invented, 102 output tokens, $0.0004. It also surfaced a detail from the rule text that a summary would drop: limited time does not imply lack of profit motive *if competent people are employed to run the activity*.
  - **Closed-book:** listed the factors roughly correctly, cited "Reg. §1.183-2" at section level, and told the reader to "refer to **IRS Publication 535**" — the publication T5 found was **discontinued after 2022**, whose URL now serves an HTML redirect page (log #23).
- **Why it matters:** the PRD's premise is that an unretrieved LLM "hallucinates section numbers and expiration dates". This is that failure in our own system, on the first question asked, and it is the *plausible* kind: a real publication number, for the right topic, that stopped existing three years ago. A preparer would have to go looking before discovering it is gone.
- **What the comparison gives us:** paragraph-level citation versus section-level; verifiable against an indexed corpus versus not; and a live citation versus a dead one. That is a sharper argument than a groundedness percentage, because it is one question a reviewer can check themselves in a minute.
- **Design note:** the citation checker already separates cited-and-present from cited-but-absent (`unsupported_citations`), so a fabricated citation is measurable now, before Phase F's NLI verification exists.
- **Likely questions:** *What does retrieval actually buy you?* *Can you show a hallucination your system prevents?*

## 30. Retrieval measured on the full pilot set, and the two models fail differently
- **Setup (T8):** 20 pilot questions x 2 models x {closed_book, rag}, graded on §9.2's 3-point rubric by a judge from the *other* provider. Total spend $0.18.

  | model | mode | correct | partial | wrong | gold cited | exact cites | derived | fabricated | p50 | $/query |
  |---|---|---|---|---|---|---|---|---|---|---|
  | gpt-4o-mini | closed_book | 0.44 | 0.50 | 0.06 | 0.00 | 0 | 0 | 0 | 1.5s | $0.0001 |
  | gpt-4o-mini | **rag** | **0.61** | 0.39 | **0.00** | 0.33 | 18 | 5 | 1 | 1.1s | $0.0005 |
  | claude-haiku-4-5 | closed_book | 0.28 | 0.67 | 0.06 | 0.00 | 0 | 0 | 0 | 3.6s | $0.0013 |
  | claude-haiku-4-5 | rag | 0.33 | 0.61 | 0.06 | **0.50** | 32 | 26 | **0** | 3.0s | $0.0043 |

- **Retrieval helps both**, which is the ladder's core claim measured rather than asserted: gpt-4o-mini goes 0.44 -> 0.61 correct and its outright-wrong answers fall to zero.
- **The models fail in different directions.** gpt-4o-mini scores higher on the rubric but cites sparsely (18 exact, 1 fabricated). claude-haiku scores lower but cites heavily (32 exact, 26 derived), fabricates **nothing**, and lands on the gold citation for 50% of questions against gpt's 33%. For a product whose thesis is verifiable citations, "grades worse, cites better" is not obviously the worse model — which is why ADR-11 waits for the answer-level ablation rather than picking on the rubric column alone.
- **Abstention appears before the sufficiency gate exists.** On the two questions the corpus cannot answer, closed-book both models answered anyway (0/2 refusals); with retrieval, gpt refused 1/2 and haiku refused 2/2. Prompt instructions alone produce some of the behaviour Phase F will enforce structurally.
- **Likely questions:** *What did retrieval buy?* *Which model did you pick and why?* *How do you compare models that fail differently?*

## 31. My reliability check measured two standards and called it noise
- **Context:** §9.2 requires two AI judges agreeing at Cohen's kappa >= 0.70 before a correctness metric is reported as trustworthy, with the second judge being "a different model, or the same model at a different temperature/prompt phrasing".
- **What I did wrong:** I gave the second judge a *stricter* rubric ("any missing material condition is at most partial"). That is a second standard, not a second reading of the same one. Kappa came out at **0.65** — below the threshold — and 9 of 13 disagreements were `correct -> partial`, exactly the direction a stricter prompt forces.
- **Fix:** same rubric, neutrally reworded. Kappa went **0.65 -> 0.81**, raw agreement 0.82 -> 0.90, and the two judges' grade distributions converged (30/39/3 vs 30/40/2). Both judges clear the bar individually (haiku 0.84, gpt-4o-mini 0.78).
- **A constraint found on the way:** temperature would have been the cleaner knob, but current Anthropic models removed sampling parameters entirely (`temperature` is rejected by the SDK), so varying it would only have worked on one provider and made the two reliability checks non-comparable. Paraphrasing keeps the method identical across providers.
- **Cost of the fix: $0.02.** Answers were stored, so only the judging was re-run — worth designing eval artifacts for from the start.
- **Interview framing:** a failed threshold is not automatically a finding about the system; it can be a finding about the instrument. The tell was the *direction* of the disagreements, not their number.
- **Likely questions:** *How do you know your LLM judge is reliable?* *What is Cohen's kappa and why not raw agreement?* (raw was 0.82 when kappa was 0.65: chance agreement alone was 0.48, because grades cluster on "partial".)
