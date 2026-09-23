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

## 32. The designed case-law source covers a fifth of the cases that matter
- **Context:** §11.5 names CourtListener as the Tax Court source (bulk CSV for the initial load, the API for weekly updates). B1 measured it before B3 committed to it.
- **Observation:** CourtListener holds 13,876 Tax Court opinions, but only ~20–60 a year since 2000 (2015: 32, 2024: 20), which is about the number of *reported* T.C. opinions. The memorandum opinions, where most hobby-loss, substantiation and home-office disputes are decided, are largely absent. The same `"section 183"` search returns **108** opinions on CourtListener and **560** on DAWSON, the court's own system.
- **The bulk route didn't rescue it:** the opinions dump is 54.6 GB compressed across all courts, and opinion rows carry no court id, so extracting the Tax Court means joining the 5 GB dockets and 2.5 GB clusters files first. That would be ~62 GB downloaded to get the same thin coverage.
- **Trade-off:** DAWSON has the coverage and is the source of record, but no documented API: its web app calls an undocumented host, and opinions are PDFs (pdfminer already handles those, from T5). The choice is between thin, clean coverage and complete coverage behind an interface that could change without notice.
- **Also measured:** all of Title 26 is only ~2.3M tokens (1,900 live sections), about an hour to embed. Scoping the statute to topics, as Phase A did for regulations, would save an hour once and make compound questions fail on sections that simply weren't loaded.
- **Interview framing:** the design doc chose a source by its reputation and API; measuring its *coverage for this court* reversed the choice before any code was written. Spikes are cheap relative to building an ingester against the wrong source.
- **Likely questions:** *Why not CourtListener, which everyone uses?* *How do you handle a source with no stable API?* *Why load the whole statute but only part of the regulations?*

## 33. A range citation bug from Phase A, found by writing a second parser
- **Context:** B2's statute parser reuses eCFR's packing code (`ecfr.pack`), which combines short neighbouring subsections into one chunk cited as a range, `(a)-(c)`.
- **Observation:** §1400Z-1's chunks came out cited `(a)`, `(c)`, `(e)`, as if (b) and (d) were missing. The text was all there; the *citation* was wrong. The range's end was read from the last packed **block**, and when the last subsection runs to several paragraphs, its trailing blocks carry no designation, so the range silently collapsed to its first element.
- **Impact on Phase A:** 84 of 5,609 indexed regulation chunks (1.5%) were cited too narrowly. One pilot gold citation, P03's `1.162-4(a)`, had been labelled against a chunk that actually holds (a)–(c). A model citing (b) from that chunk would have been counted as citing a paragraph it was never shown.
- **Fix:** track the last packed *unit's* designation, not the last block's; one regression test; P03 relabelled to `1.162-4(a)-(c)`; the eCFR subset re-ingested from the same 2026-09-17 file so the fix is the only change.
- **Interview framing:** reusing code across a second input format is a test of the first. The eCFR fixture happened to end every packed range on a one-paragraph unit, so the bug never showed; the statute's structure exposed it on the first run.
- **Likely questions:** *How did Phase A's tests miss it?* *Did it change your Phase A numbers?* (re-measured after the re-ingest.)

## 34. Statute chunks need their chapeau
- **Context:** the statute is written in lead-ins: "there shall be allowed as a deduction all the ordinary and necessary expenses…—" followed by "(1) for the production or collection of income". Title 26 has ~13,500 of them.
- **Observation:** chunked the eCFR way, where a preamble never packs with the units after it, §212's lead-in became a 34-token chunk with no object, and its paragraphs became a list with no verb. Headings of split subsections ("(d) Definitions.") became 12-token chunks. First pass: 2,563 of 12,026 chunks under 50 tokens.
- **Fix:** fold a lead-in into the first provision it introduces. Under-50-token chunks halved (1,243 of 10,768), and the statute went from 12,288 to 11,030 chunks.
- **What it does not fix, stated:** in a long enumeration split at level 2, only the first item carries the chapeau; items like "(22) the nonconventional source production credit…" are still retrieved alone. Packing consecutive level-2 units, or prefixing each with its chapeau, would fix it; left until the golden set can show whether it costs recall.
- **Also:** 150 repealed provisions ("[(24) Repealed. Pub. L. 113–295 …]") are dropped, as eCFR drops `[Reserved]`; 262 repealed/renumbered/reserved/omitted sections are recorded, not indexed.
- **Likely questions:** *Why not just use a fixed token window?* *How did you decide chunk boundaries for legal text?*

## 35. The batch size that made embedding 4x slower
- **Context:** re-indexing the 5,609-chunk regulation subset was estimated at ~45 minutes (bge-base at ~2 chunks/s). After 2 hours it was 56% done.
- **Observation:** 0.45 chunks/s. The ingest process had grown to 8.6 GB (5.3 GB an hour earlier) and the Mac was holding 20 GB of swap. It was swapping, not computing.
- **Cause:** `index.sync` embedded 256 texts per call. Every text in a batch is padded to the longest one (up to 512 tokens here), so one layer's attention scores for a batch are ~3 GB, and ONNX Runtime keeps the memory it has grabbed. Paragraph-level legal chunks are long, which puts most batches near the worst case.
- **Measured, 128 longest chunks:** batch 16 → 2.91 chunks/s at 1.5 GB peak; batch 128 → 2.86 chunks/s at 4.5 GB. Throughput is flat, because the CPU is saturated either way; only memory changes. Batch size is now 16.
- **Why Phase A didn't notice:** its subset embedded on a quieter machine, and bge-small's hidden size is half of bge-base's. The problem grew with the model and with everything else running on the laptop.
- **Interview framing:** the obvious fix for "embedding is slow" is more parallelism; the measured answer was *less* batching. Big batches help a GPU; on a CPU they only buy memory pressure.
- **Likely questions:** *How did you find it?* (progress per minute in Qdrant, then RSS and swap.) *Why not parallel workers?* (log #16: they were slower too.)

## 36. Adding the statute "cost" a question the statute answers better
- **Context:** B2 indexed all of Title 26 (10,768 chunks) next to the regulation and publication subsets, then re-ran Phase A's 18-question pilot.
- **Observation:** hybrid Recall@10 fell 0.722 → 0.667, which is exactly one question. P02 asks whether anything is deductible for an activity not engaged in for profit. Its gold is the regulation `1.183-1(b)(1)`, which fell from rank 10 to 11; `26 U.S.C. § 183(a)-(d)` now sits at rank 2, and its subsection (b), "Deductions allowable", is the rule itself.
- **Reading:** the pilot was labelled when no statute was indexed, so it cannot credit a statute answer. The metric fell because the answer key is incomplete, not because retrieval got worse. That's the same dilution *mechanism* Phase A measured with publications (more authorities competing for ten slots), but here the newcomer outranks the gold on authority, not on paraphrase.
- **Decision:** leave Phase A's pilot unchanged, so its numbers stay comparable, and report the drop with its cause. B4's golden set labels statute answers from the start.
- **Interview framing:** a metric that drops when you add a better source is measuring its labels. Always check *what* displaced the gold before calling a drop a regression, and with 18 questions, one question is 5.6 points.
- **Likely questions:** *Why didn't you just add the statute to the gold?* (it changes the instrument mid-comparison; recall with two golds needs both.) *How will the golden set avoid this?*

## 37. Ingesting from a source with no documented API
- **Context:** B1 chose DAWSON, the Tax Court's own system, for coverage (560 vs CourtListener's 108 on §183), accepting that it has no documented API.
- **How the interface was found:** the public web app's JavaScript bundle names its endpoints (`/public-api/opinion-search`, a per-document download-URL endpoint) and its enum values (`MOP`, `TCOP`, `customDates`). Watching the browser's network log showed nothing, because the app's requests didn't appear there. A first probe returned nothing because it used the wrong host (`public-api.` rather than `public-api-green.`); a second 400'd on an end date in the future.
- **What the API doesn't do:** rank by relevance. Results come newest first, so "top 50 by relevance" became "50 newest per topic". For broad topics (§162, §6662) that means 2025–2026 opinions only.
- **Defensive choices:** the selection is cached so the corpus doesn't drift as opinions are filed; downloads are checked for a `%PDF` header, not trusted on status 200; a changed response shape raises instead of indexing partial data; requests are spaced and identify the project.
- **A modelling correction:** the plan assumed opinions would be cited by paragraph (`¶14`). They aren't numbered. Courts pin-cite by page (`at *12`), and every page after the first carries a `[*12]` marker, so chunks carry page ranges.
- **Interview framing:** an undocumented API is a dependency you have to own: find it, fence it (cache, validate, fail loudly), and write down what breaks if it changes.
- **Likely questions:** *Is scraping DAWSON allowed?* (public government records, polite rate, identifying User-Agent, no authentication bypassed.) *What happens when they change the API?* *Why the 50 newest?*

## 38. Case law buries the regulation it applies
- **Context:** B3 added 9,973 chunks of Tax Court opinions (307 opinions) to the collection holding regulations, publications and the statute, then re-ran Phase A's pilot.
- **Observation:** hybrid Recall@10 fell 0.667 → 0.500, three more questions. For P01 ("a client has bred horses at a loss for six years; does the time they put in matter?"), all ten results are opinions. Hobby-loss cases walk through §1.183-2(b)'s nine factors *for a specific horse breeder*, so a fact-pattern question matches them better than the rule. Across the pilot, case law took 53 of 180 top-10 slots.
- **Why it's worse than publications were:** publications paraphrase a rule (Phase A's 12.4 points). Opinions paraphrase the rule *and* restate facts like the user's, which is exactly what a natural-language question contains. Keyword questions were untouched (1.000 on hybrid); natural-language ones fell to 0.357.
- **The fix is already in the plan:** decomposition routes a statutory sub-query to `usc + ecfr + irs_pub` and a case-law sub-query to `case`. Dropping case chunks from the top 60 approximates it: ~0.611. B7 now has that recovery as an acceptance criterion.
- **Interview framing:** one index for every authority is simple until the authorities compete. The measured cost of mixing them is the argument for routing, made before routing was built.
- **Likely questions:** *Why not separate collections?* (a payload filter gives the same isolation with one index to snapshot and operate.) *Why not just boost regulations?* (that's Phase E's authority reranking; routing comes first because it's cheaper and precedes reranking in §9's ladder.)

## 39. Building the golden set exposed two metric bugs and one validator blind spot
- **nDCG above 1.** Phase A's nDCG summed a gain for every retrieved chunk whose citation was gold. Multi-part chunks share a citation, so one gold paragraph retrieved three times scored three times: P15 came out at **1.232**, which nDCG can't be. Now each gold group earns gain once, at its first hit. Pilot hybrid nDCG 0.304 → 0.247; recall and MRR unchanged. The embedding benchmark used the same function, so **ADR-18's +12.3 nDCG gap is unreliable**; the decision stands on recall (+8.3) and MRR (+13.0), which weren't affected.
- **Section recall that could never match a publication.** The eval had its own regulation-only `section_of`, which returned "IRS Pub 587 (2025), p. 12" whole while chunks store "Pub 587". Replaced by the shared helper that handles all four sources; pilot hybrid section recall 0.667 → 0.778.
- **"Wrong gold" vs "crowded-out gold".** The validator flagged 16 of 45 new rows as unreachable. Re-searching each group within its own source split them: 12 were findable there (dilution, which routing should fix), 2 were vocabulary mismatches worth keeping as known-hard ("FICA" vs "for purposes of this chapter"), and 2 had gold that was too narrow: the court's discussion page, or a second opinion with the same holding, answered just as well. None needed the question reworded, which would have tuned the held-out set to today's retriever.
- **Baseline:** hybrid Recall@10 0.467 on the 45 rows, but **0.320 on statutory questions** against 0.650 on case law. A 25-question statutory stratum makes the dilution visible in a way the 18-question pilot couldn't.
- **Interview framing:** every new instrument audits the old ones. The golden set's first job was to find the bugs in the measuring tools, before measuring anything.
- **Likely questions:** *How do you know your metrics are right?* (hand-computed tests, plus impossible values as a smoke alarm.) *How did you avoid teaching to the test when the validator complained?*

## 40. Auditing a golden set: what two careful passes found
- **Context:** before the golden set was frozen, every row was re-read twice against the full text of its sources, and every external fact an answer depended on was checked on the web.
- **Answers that were true but incomplete.** Eleven statute answers dropped a condition the provision states: §6662(d)'s substantial-understatement threshold is 5%, not 10%, for anyone claiming the §199A deduction; §280A(c)(5)'s disallowed home-office excess carries forward; §179's limit phases down above $4,000,000. Phase A's defect taxonomy was already 39-of-39 `missing_condition`, and the reference answers had the same failure. A grader comparing against an incomplete key would reward incomplete answers.
- **Questions whose answer changes with facts they didn't state.** "My client works from a spare bedroom" has a different answer for an employee (§67(h) suspends the deduction entirely), so the statute question was really two questions. Fixed by saying "self-employed".
- **Law that moved after the source.** State-licensed medical marijuana became Schedule III on 2026-04-28, outside §280E. A reference answer written from the statute text alone was wrong, and nothing in the corpus could reveal that. It's the clearest example yet of why Phase D (temporal validity) and an insufficiency path exist.
- **Precedent that was reversed.** The Tax Court's Morehouse holding was reversed by the Eighth Circuit in 2014; the corpus holds only the Tax Court opinion. This row becomes Phase E's first negative-treatment test.
- **Leakage between dev and golden.** Five dev rows shared statute gold with golden rows. Tuning retrieval on the dev set would have lifted the golden score without the system generalising. Rule now enforced by script: no citation and no opinion in more than one set.
- **Coverage.** The first draft over-sampled published opinions on niche issues (IRA conduits, offers in compromise) and had no case-law row on hobby loss, home office, substantiation or constructive receipt. Eight rows added. §9.1's counts are now minimums.
- **Interview framing:** a golden set is a legal-research product in its own right. Its answer key needs the same conditions, currency and authority checks the system is supposed to perform, or the eval grades the system against its author's mistakes.
- **Likely questions:** *How do you keep an eval set current as law changes?* (`notes` per row, B5 temporal rows, Phase D.) *How did you prevent dev/test leakage?*

## 41. Writing questions a system should fail, and proving they fail for the right reason
- **Compound questions can't be checked the simple way.** "My client restores vintage bikes as a hobby…" contains none of the words in §67(h) or in Gregory, so a single search reaches almost none of the gold, which is exactly why decomposition exists. Each compound row now carries gold sub-queries (source plus legal-vocabulary query); all 45 gold groups are reachable that way. That proves the gold is findable, and it hands B7 a held-out measure of decomposition quality. Baseline without decomposition: Recall@10 0.317.
- **"Not in the corpus" is a claim that needs proof.** Two draft insufficiency questions (the 2026 mileage rate, the 2026 Social Security wage base) were answerable: Pub 334's "What's New for 2026" gives 72.5 cents *a* mile and $184,500, and a text probe for "cents per mile" had missed them. Every insufficiency row is now verified by running the real search and reading the results. Several are traps where search returns authoritative-looking but irrelevant chunks, like federal New York *Liberty Zone* rules for a New York conformity question.
- **Effective dates live where the parser doesn't look.** USLM keeps amendment and effective-date information in statutory notes, which B2 skips. So the corpus holds the qualified-tips deduction's end date (in the text) but not its start date (in the notes), and §179's current $2.5M limit with no sign of when it began. Temporal rows now test exactly that; Phase D's versioning is the fix, and ingesting notes selectively is an option to weigh there.
- **Interview framing:** an eval set earns trust by including questions the system must refuse, and by proving that refusal is correct. An insufficiency row that the corpus can actually answer rewards the system for ignoring its sources.
- **Likely questions:** *How do you test abstention?* *How do you evaluate a decomposer without tuning on the test set?* (gold sub-queries are read by the validator and the scorer, never by the tuning loop.)

## 42. Second audit: categories that measured the same thing, and precedent that didn't stand
- **Two categories, one test.** 22 of 30 compound rows used an opinion already tested by a case-law-only row, usually the very same chunk with client facts added. A retrieval hit on one nearly guaranteed a hit on the other, so the compound score would have partly re-reported the case-law score. 18 rows were rebuilt on opinions the golden set doesn't otherwise use; the 4 remaining overlaps are deliberate and documented. Rule now: a compound row's case-law gold may not repeat a case-law-only row's opinion.
- **Reversals hide in plain sight.** Carter's §6751(b) timing holding was reversed by the Eleventh Circuit, and the chunk in the corpus is the post-remand opinion accepting the approval as timely; the draft answer had read the earlier holding and got the law backwards. Menard's reasonable-compensation holding was reversed by the Seventh Circuit in 2009. With Morehouse from B4, the golden set now has three explicit negative-treatment rows. Phase E's authority metadata will need appellate history, which no ingested source provides today.
- **Answers that turned on an unstated fact.** Dirico's lease income was passive only because the lessee used the towers in a *rental* activity; had the company used them in its own trade or business, the self-rental rule would make the income nonpassive. The draft question omitted that fact, so its "correct" answer was only sometimes correct.
- **The long tail of "the source also says".** Nine answers dropped a rule stated in the same or an adjacent provision: reconstruction after a casualty, the for-hire exclusion from "passenger automobile", §162(f), the hotel-portion exception, no reasonable-cause defence for charitable gross overvaluations, the §7503 weekend rule (April 18, 2026 is a Saturday), and others. These are exactly the `missing_condition` defects Phase A found in model answers.
- **Coverage filled:** a retroactive rule (§9.1 names it; the draft had none), a question answerable in one half only (the per-sub-query sufficiency gate's job), and a PII canary for §3.4's redaction invariant.
- **Interview framing:** auditing an eval set is legal research with a checklist: every conclusion needs its conditions, its currency, its appellate history and its independence from the rest of the set. Each missed check produces a test that grades the system against the author's error.
- **Likely questions:** *How do you handle precedent that was later reversed?* *How do you stop eval categories from being correlated?*

## 43. A reranker that worked, on a candidate pool that didn't contain the answer
- **The obvious upgrade bought 1.7 points for 28x the latency.** Cross-encoder reranking is in the design (§5.2) and in every RAG tutorial, so B6 built it and measured it rather than switching it on. On the 84 scored golden rows it moved Recall@10 from 0.435 to 0.452, nDCG stayed at 0.307, and p50 query latency went from 30 ms to 852 ms. Hybrid stays the default (ADR-19); `hybrid+rerank` ships as its own ablation rung.
- **The average hid churn in both directions.** Reranking rescued four questions and lost three. It demoted gold that hybrid had ranked first: G-S12 fell from rank 1 to 10, G-S19 fell out of the top 10 entirely. A near-flat mean over 84 questions is not a small effect, it is a large effect with no net sign — worth knowing before shipping it as a default.
- **The number that explains the result is the ceiling, not the delta.** Hybrid Recall@25 on the golden set is 0.530 against Recall@10 of 0.435. Of the 9.5 points of headroom inside the pool the reranker recovered 1.7 (18%); the remaining 47% of gold is not in the top 25 at all, where no reranker can reach it. First-stage recall is the bottleneck, which is B7's job. Measuring recall at the candidate depth turned "the reranker underperformed" into "the reranker was handed the wrong pool".
- **A bigger model was the worst model.** The 1 GB `BAAI/bge-reranker-base` scored 0.542 on the dev set at 2.8 s a query, below every small model tested and below plain hybrid on nDCG. `jinaai/jina-reranker-v1-turbo-en` (0.15 GB) won at 878 ms.
- **Half the candidates, none of the cost.** Dev-set hybrid Recall@25 and Recall@50 are both 0.750, so the pool is 25: the second 25 candidates doubled latency and could not contain an answer the first 25 missed. Sizing the pool by where recall saturates, not by a round number, is free latency.
- **Interview framing:** the value of an ablation rung is that it can come back negative. A component that is in the architecture diagram and in the literature still has to earn the default path on this corpus, and the diagnostic ("is the answer even in the pool?") matters more than the delta.
- **Likely questions:** *When does reranking help?* (When first-stage recall at the candidate depth is well above recall at k.) *How would you know a reranker is worth its latency?*

## 44. The decomposer's best idea was not its words
- **The rewriting was the liability; the routing was the win.** B7's decomposer does two jobs: it rewrites a question into source vocabulary, and it types each sub-query so retrieval can be filtered to the corpora that hold that kind. Measured separately on the dev set at k=10, the rewritten text scored Recall 0.417 and the questioner's own words, routed the same way, scored 0.667; giving each sub-query its own depth took the original to 0.833 and the rewrite to 0.625. Combining them ("question + rewrite") landed in between. The shipped path searches the original question and uses the model only for the routing.
- **Why the rewrite loses is visible per question.** On a substantiation question the user's words put the gold opinion at rank 2 and the rewrite, which said the same thing in cleaner legal English, missed it entirely. The chunks are court prose and statute text; a question phrased like the documents it is looking for is already a good query, and paraphrasing throws away the rare terms BM25 depends on. The hand-written `gold_subqueries` in the golden set do work, so this is not "rewriting cannot help" — it is "gpt-4o-mini's rewriting does not beat the question".
- **Routing recall and routing precision are different problems, and only one of them is easy.** Two prompts were measured. A precision-oriented one ("a question about what courts held needs only case law") misrouted genuine case-law questions to the statute and dropped dev case-law recall from 0.833 to 0.333. A recall-oriented one ("when unsure, include both") gets a case-law sub-query onto 56 of 56 golden rows whose gold needs one — and onto 23 of the 28 rows that do not, a routing precision of 0.709.
- **That is why the pilot dilution is still there.** B3's case-law ingest cut pilot Recall@10 from 0.667 to 0.500, and B7's acceptance criterion was to recover it. Routing as shipped scores 0.500 — no recovery — because it adds a case-law sub-query to 16 of 18 pilot questions that never needed one. An oracle that routes those questions to statute and regulations only scores **0.667**, and 0.694 with reranking: the mechanism recovers the dilution and then some, and the gap is entirely the model's routing precision.
- **The tuning set cannot see the failure.** Every one of the 12 dev rows has case law in its gold, so a decomposer that asks for case law on every question scores perfectly on dev routing and the false-positive rate is invisible. The dev set was built to hold out the golden set, and it does; it was not built to measure a classifier's precision, and it cannot.
- **Reranking can undo routing.** Routing guarantees a corpus reaches the candidate pool, not the final k. On a question that asks in so many words for the Code, the regulation and the case law, the cross-encoder filled all 10 slots with court prose and the statutory groups contributed nothing to synthesis. A reserved floor per sub-query is the obvious fix and is not measurable on the current dev set either.
- **Correction (B7b, log #46): the golden-set numbers in this entry were read off single runs and the run-to-run spread is larger than the effect.** The claim that routing moved golden Recall@10 from 0.435 to 0.476 does not survive repetition. The dev and pilot findings in this entry stand as directional; the golden one does not.
- **Interview framing:** decomposition is usually sold as one idea. Measuring its halves separately showed one half paying for the other, and an oracle on the failing metric separated "the design does not work" from "the classifier is not accurate enough yet" — different problems with different fixes.
- **Likely questions:** *How do you know your query rewriting helps?* *How do you tune a router without touching the held-out set?*

## 45. A third audit of a set two audits had already passed
- **The rule that was only half-applied.** B5 forbade a compound row from reusing a case-law row's opinion, because a hit on one would nearly guarantee a hit on the other. Nobody applied the same test to statute. Thirteen gold groups turn out to be identical across two or more rows -- section 183(a)-(d) in three rows, 162(a)-(b) in three, 3121(d) in three -- touching 29 of the 84 scored rows. The statutory and compound category scores were never independent, and the write-up's claim that the four remaining opinion overlaps were "deliberate and documented" was wrong: there were five, and three carried no note.
- **Two gaps that only show up when you measure the set against itself.** Exactly one scored row needed more than two kinds of source, and none needed statute, regulation and case law as three separate gold groups -- the architecture's headline capability, untested. And **no scored row had publication gold at all**, though publications are 7% of the corpus and Phase A measured a 12.4-point publication-dilution penalty that later phases are supposed to beat. Reading 111 rows one by one does not surface either; a histogram of gold sources surfaces both in a second.
- **The check that stopped me writing a false fact.** Two prior audits found reversed precedent by recall. This time I checked the appellate record itself on CourtListener, and the case I was most confident about was the one I had backwards: I was about to note that the Ninth Circuit reversed Schwab. It affirmed -- "We agree with the tax court on both determinations, and we affirm." No new reversals turned up; three opinions gained positive history instead. Recall was good enough to find the famous reversals in B4 and B5 and not good enough to be trusted on the next one.
- **Absence of evidence.** CourtListener's coverage of unpublished appellate dispositions is incomplete, so "no appellate opinion found" is not "not appealed". The audit records the query, not a conclusion.
- **The eval sets leak into each other in a direction nobody ruled on.** The B4 rule protected the golden set: no gold citation in both golden and dev/pilot. It said nothing about dev and pilot, which share three gold citations. That matters because B7's dilution criterion is reported on the pilot and tuned on dev: the headline 0.500 -> 0.611 becomes 0.533 -> 0.600 on the 15 pilot rows that share nothing with the tuning set. The conclusion survives; the headline is flattered by about four points, and one shared row (P01) supplies roughly 40% of the gain.
- **A validator that assumed the shape of the attack.** Every adversarial row was required to carry a client document, so a row where the injection arrives in the user's own message -- the trusted channel -- could not be expressed. The rule now demands an explicit decision instead of a non-empty document.
- **Interview framing:** an eval set is not "done" when it passes review, it is done for the questions asked so far. The third audit found more than the second because it asked structural questions of the set as a dataset (which rows share a target, which source kinds are never tested, which sets overlap) rather than legal questions of each row.
- **Likely questions:** *How do you know your eval set is not measuring the same thing twice?* *What is your process for verifying case law is still good?*

## 46. The A/B that was measuring the weather
- **Three runs of one configuration: 0.457, 0.422, 0.434.** (Refined below: over six plan sets the standard deviation is 0.012, and the range over any three is an unstable way to say so.) B7 chose a decomposition prompt on the dev set and reported the result on the golden set. Asked to separate the prompt change from a reranking change, I re-ran the shipped configuration and got a different number from the one recorded an hour earlier — so I ran it three times. The spread is 0.035 Recall@10, about 3 gold groups out of 86, and 9 to 11 of the 86 questions are planned differently on each run. `gpt-4o-mini` at temperature 0 with `seed` set is not deterministic; OpenAI documents the seed as best effort, and this is what best effort looks like at eval scale.
- **What that invalidates.** "The precision-tuned prompt cost the golden set 0.476 → 0.440" was noise read as signal; the controlled comparison puts the two prompts 0.006 apart. The "±0.006 run-to-run spread" I had quoted came from two runs that happened to land close together.
- **What repeating it properly showed.** With `--repeats` in the harness, six independent plan sets put routing at mean 0.4398, sd 0.0117, against a deterministic baseline of 0.428 — an effect of **+0.012 Recall@10, one gold group in 86**, with one run of six below the baseline. So the honest verdict is not "indistinguishable from no change" (my first correction, itself drawn from three samples) but "small, probably real, and unresolvable by any single run". Two wrong headlines came from the same habit: quoting a range over three samples. Five or more samples and a standard deviation, or say nothing.
- **The noise has an address.** Of 86 golden questions planned three times, 14 (16%) are routed differently and 39 (45%) differ only in wording. The wording differences cannot move a metric, because ADR-20 searches the original question and uses the model only for routing — so the entire noise floor is those 14 questions. Dropping the query rewriting bought reproducibility on top of the recall it bought, which I had not thought to claim.
- **What survives.** Everything measured against a fixed plan set or with no LLM in the loop: the floor is exactly neutral (identical metrics at floor 0 and 1 under both prompts), the reranker's own numbers, the source-span and leakage audits, and the oracle showing perfect routing recovers the pilot dilution. Ablations whose arms each called the planner afresh have to be re-read as suggestive.
- **The fix is caching, not more runs.** `eval/retrieval.py` now stores each question's plan in `eval/results/decompositions.json` and reuses it across runs and arms, so a comparison varies only the thing under test; two runs from one cached plan set now agree exactly. B8's RAGAS harness already specified per-run caching — the retrieval eval needed it first and did not have it. One side effect worth remembering when reading the tables: a cached run's p50 excludes the ~1.2 s planning call, so latency must be taken from an uncached run.
- **The tell I should have caught earlier.** The same configuration had already produced 0.470 and 0.476 in two different sessions and I wrote that off as rounding. Two samples cannot show you a spread; the discipline is to repeat a configuration before comparing configurations, and to do it before the numbers go into a document.
- **Interview framing:** the first question to ask of an A/B result is not "is the difference big?" but "is it bigger than the same thing measured twice?" A pipeline with a generative step in it has a noise floor, and nobody tells you what it is.
- **Likely questions:** *How do you make an LLM pipeline's eval reproducible?* *How would you know if your improvement was real?*

## 47. Faithfulness catches what the citation checker is built to miss
- **Two rows scored 0.00 in all three runs, and both answers are legally correct.** Asked how many hours make someone a real estate professional, the system answered "more than 750 hours" and cited IRS Pub 527 p. 19. Asked the accuracy-related penalty rate, it answered "20 percent, 40 percent for undisclosed noneconomic substance transactions" and cited Pub 17 p. 22. Both answers are right. Neither cited page says any of it: the gold statute chunk was not retrieved either time, and the model answered from what it already knew, then attached a citation to a chunk that *was* retrieved.
- **Phase A's citation checker passes both.** It splits citations into exact, derived and fabricated, and these are exact — the cited chunk genuinely came back from retrieval. The check was built to catch invented citations and it drove them to zero; it cannot see a real citation attached to a claim the source does not make. Call it citation laundering. Faithfulness is the only measurement in the system that sees it, which is the concrete argument for the B9 gate that I did not have before.
- **A 0.85 gate cannot be enforced on a single run.** Three runs of the unchanged pipeline scored 0.859, 0.902 and 0.833 — mean 0.865, sd 0.035. Run 3 is *below* the gate. Shipped as specified, CI would fail roughly one build in three with nothing changed, which is the fastest way to teach a team to ignore a gate. The noise traces back to log #46: a different plan means different chunks, which means different claims and different refusals.
- **Abstention is the strongest result in the run.** All 10 insufficiency rows refused in all 3 runs, 30 for 30. The refusal *rate* of 13-18% is higher than those rows alone explain because 3 to 7 answerable rows refuse per run — one consistently (G-C02), one twice, eight once. False refusals are a retrieval problem wearing an honesty costume: the sufficiency gate is right to refuse when the chunks are thin, and the chunks are thin because the plan changed.
- **The judge was checked before its numbers were used.** Five low-scoring rows read against the actual retrieved text: right in all five, including one where I expected it to be wrong. On G-S05 it rejected a bona fide-transaction exception that *is* in the corpus — but the citation `1.274-12(c)(2)` covers 15 separate chunk parts and retrieval returned a different one, so the claim genuinely was not in the context the model saw. A metric this strict only survives if you check it against the source, not against your memory of the source.
- **Not RAGAS the library.** `ragas` 0.4.3 resolves to 326 packages against this project's 65, for a metric that is two model calls, in a gate B9 has to install on every PR. The metric here is RAGAS's own definition, with the judge on Anthropic per ADR-11. Building it also surfaced two things about the SDK: `anthropic` 1.7.0 has no `temperature` on `messages.create` at all, and it offers schema-enforced JSON output, which is stricter than OpenAI's json_object and now guarantees the judge's shape.
- **Interview framing:** the useful question about an eval metric is not "what did it score" but "what failure does it see that nothing else sees". Faithfulness earned its place the moment it flagged two answers that were correct, cited and unsupported.
- **Likely questions:** *Why not just check the citations?* *How do you set a CI threshold on a noisy metric?*

## 48. Calibrating a gate against the failure it exists to catch
- **The threshold in the spec was never tested against a failure.** §7 said the build fails below 0.85 faithfulness. That number was chosen before anyone knew what a healthy build scores or what a broken one scores, which makes it a quality aspiration wearing a CI threshold's clothes. So B9 measured both: a healthy pipeline, and one with the grounding rule deleted from the synthesis prompt.
- **A broken prompt is worth about 0.05 faithfulness, and the noise is 0.02-0.03.** On the 25 rows affordable per PR: healthy 0.808 (sd 0.016 with synthesis pinned), broken 0.759 (sd 0.027). That is 2.2 pooled sd, a separating window 0.011 wide, and roughly 12% false failures with 12% false passes. The gate I had recommended putting on the dev set does not work, and the measurement said so before it shipped rather than after.
- **Why the broken prompt costs so little is the interesting part.** Told to answer from its own knowledge with the sources as "background", the model still mostly says things the retrieved sources support -- because they are the right sources. Removing the grounding rule changes where the answer comes from more than what it says. A metric that scores claims against context is structurally weak at detecting that, which is worth knowing before betting a build gate on it.
- **The broken arm is noisier than the healthy one** (sd 0.027 vs 0.016). Running on parametric knowledge is less repeatable than reading from a page, so the distribution you most need to be tight is the loose one.
- **Pinning, measured one component at a time.** Re-judging identical answers moves the score by sd 0.008 -- 5% of the variance. The other 95% lives in the planner and in synthesis sampling. The only component that cannot be pinned is the one that hardly matters, which is a pleasant way for an error budget to be arranged. Synthesis now runs at temperature 0: half the noise, no measurable quality cost, and a legal tool should not answer the same question two ways.
- **Where that leaves CI.** Three tiers (ADR-22): pytest on every push; a deterministic retrieval check on PRs, which needs no LLM, runs in seconds and cannot flake because two cached runs agree to three decimals; and faithfulness nightly on the golden set, where 96 rows turn the same 0.05 gap into about 4.4 sd. Per-PR blocking stays cheap and certain; the expensive, noisy, genuinely-different check runs where its sample size is affordable.
- **Interview framing:** a CI threshold should be derived from the distance between a good build and a bad one, not from the score you are currently getting. Measuring both distributions turned "0.85, as specified" into a design with a defensible number and an honest statement of what it cannot catch.
- **Likely questions:** *How did you pick that threshold?* *What regression would your gate miss?*

## 49. The eval harness had the bug, not the model
- **Pinning the planner halved the noise; pinning temperature alone did nothing.** Golden faithfulness scored sd 0.035 with nothing pinned, sd 0.030 with synthesis at temperature 0, and sd 0.013 once decompositions came from the shared plan cache. The reason temperature looked useless on golden is that the planner drowned it: 16% of golden questions route differently between runs, against 8% on dev, which is why the same change halved the dev spread and moved golden not at all.
- **`ragas_eval` was calling `decompose` fresh on every row.** The retrieval eval had a plan cache; the faithfulness eval never used it. So the metric intended to gate CI was measuring the planner's mood as much as the pipeline's quality, and every faithfulness number before this — including B8's headline 0.865 ± 0.035 — carries that extra variance. Not wrong, but noisier than it needed to be, and the fix is four lines.
- **Some noise is irreducible and it is worth knowing which.** With plans pinned and `temperature=0, seed=0`, two runs over identical context still produced different answers on 2 of 3 smoke rows. OpenAI's determinism is best effort in the same way its seed is. Residual sd 0.013 against a judge floor of 0.008 leaves about 0.010 of synthesis variation that no amount of configuration removes.
- **A threshold calibrated against the healthy distribution, not a hoped-for broken one.** 0.83 is three sigma below the pinned healthy mean of 0.871: a regression gate that says "do not fall 3 sigma below the established baseline". That framing needs no assumption about what a broken build scores, which matters because the only broken measurement is on a different question set.
- **I wrote predictions down before the run and needed to.** sd ≤ 0.010 meant block at 0.80; 0.010-0.020 meant marginal; > 0.020 meant report-only forever. It landed at 0.013 — marginal — and pre-registering stopped me reading that as the clean result I wanted. Three times this session I had called a trend from two samples (logs #46, #47, and the two golden runs that sat 0.003 apart before the third landed 0.05 away). Writing the bands down first is the cheapest guard against the fourth.
- **Interview framing:** before concluding that a metric is too noisy to gate, check whether the harness is adding the noise. Two of the three sources here were the eval's own doing, and only one was the model's.
- **Likely questions:** *How do you make an LLM eval reproducible?* *What is left when you have pinned everything you can?*

## 50. The proof run failed, which is what proof runs are for
- **A broken build passed the gate.** The grounding rule was deleted from the synthesis prompt, the nightly faithfulness job ran against it on the runner, and it went green at 0.844 against a threshold of 0.83. The regression the gate exists to catch walked straight through it.
- **The threshold was calibrated against one band instead of two.** 0.83 came from three sigma below a healthy mean measured on a laptop. Nothing about that construction knows where a broken build lands, and a broken build lands at 0.844 — above the line. The fix is not a better sigma multiple; it is measuring both distributions and putting the line between them. 0.855 now sits in the window with ~2.5 sigma on each side.
- **The extrapolation I had refused to make, I made anyway.** ADR-22 said in writing that the dev gap must not be assumed to transfer to golden — and then the threshold was derived from a healthy-only calculation that implicitly assumed exactly that. The dev gap was 0.05; the golden gap is 0.037. Writing down the right principle is not the same as following it.
- **The metric is in better shape than the threshold was.** Healthy 0.881 (sd 0.010) against broken 0.844 (sd 0.004), bands that do not overlap — healthy's worst run beats broken's best by 0.021, about 4.9 pooled sigma. Pinning plans and temperature is what bought that: the same comparison on the unpinned pipeline would have been swamped by sd 0.035.
- **The contingency was written backwards.** The workflow comment said that if the proof did not go red, the threshold "comes down". A broken build passing means the gate is too permissive and the number must go up. An error in the recovery plan is worse than an error in the plan, because nobody re-reads the recovery plan until it is needed.
- **Worth noting what did work:** the whole path ran end to end on the runner for the first time — corpus restore from a release asset, both API keys, three repeats, cost cap, artifact upload — and the two arms differed by one line of prompt and nothing else. The experiment was sound; the number it was tested against was not.
- **Interview framing:** a gate that has never been shown to fail is not a gate. This one cost $2.80 and fifty minutes to disprove, and it would otherwise have sat green through exactly the regression it was built for.
- **Likely questions:** *How do you know your alert threshold works?* *What is the difference between calibrating on a baseline and calibrating on a failure?*

## 51. The gate could not have failed
- **`| tee` silently disarmed the faithfulness gate.** GitHub Actions runs `run:` steps as `bash -e {0}`, with no `pipefail`, so a pipeline's exit status is its last command's. `ragas_eval --fail-under` exits 1 on a breach, `tee` exits 0, and the step goes green. Through the entire first proof run the gate was structurally incapable of turning red — at any threshold, against any prompt.
- **Which means the proof proved less than I reported.** Log #50 said a broken build "passed a gate set at 0.83". True about the score, and the threshold really was misplaced — but the gate would have gone green even with the threshold correct. Two independent faults, and fixing the visible one left the invisible one in place.
- **The contrast was sitting there.** Tier 2 failed honestly on its seeded regression; tier 3 passed on a sabotaged prompt. The difference between those two steps is a pipe. I read the tier-3 pass as a threshold problem and stopped looking, because a plausible explanation arrived before a complete one.
- **The fix is `shell: bash`**, which runs `-eo pipefail`. A step whose only job is to fail loudly should not end in a pipe at all, and every gating step in these workflows is now either pipe-free or explicitly pipefail.
- **Found by asking whether a run was necessary.** The re-run looked like a formality — the arithmetic was settled, 0.844 < 0.855 < 0.881 — and I had been ready to skip it. What made it necessary was that nobody had ever seen this gate go red, and a code path that has only ever run in one direction is untested in the other.
- **Interview framing:** "the check passed" and "the check ran" are different claims, and CI makes them easy to confuse. A gate needs a red build in its history before its green builds mean anything.
- **Likely questions:** *How do you know your CI check can fail?* *What is the difference between a test that passes and a test that runs?*
