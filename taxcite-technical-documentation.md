# TaxCite — Technical Design Documentation

*A citation-grounded RAG system for small tax/accounting practices*

---

## Implementation Status

This document describes the target design. **Phase A is built and measured** (report: `eval/results/phase_a.md`, 2026-09-21): 7,652 chunks of 26 CFR and IRS publications indexed, single-hop hybrid retrieval at Recall@10 **0.722**, cited answers served over the ADR-9 job/SSE transport, 95 tests. Retrieval's contribution is measured rather than asserted — answer correctness rises 0.44 → 0.61 and outright-wrong answers fall to zero — and three deferred decisions are now settled by measurement: ADR-11 (LLM), ADR-17 (vector store), ADR-18 (embedding model).

The remaining mechanisms below (decomposition, graph expansion, temporal filtering, authority-aware reranking, claim verification) are **not yet built**. §7 (Build Phases) and §9 (Eval Harness) exist to produce that evidence, not just to organize the architecture. Phase A also produced a baseline each later phase must beat: adding IRS publications cost 12.4 points of regulation recall (the case for Phase E), approximate search loses ~22% of exact results under a strict filter (a risk for Phase D), and the pilot set cannot resolve differences below ~5.6 points (the case for §9.1's 100-question golden set).

Each phase in §7 now carries an explicit, numeric acceptance threshold (e.g., a minimum Recall@20 delta, a minimum extraction precision — consolidated in §9.3) rather than only a qualitative direction to "measure the delta." These are first-pass engineering targets to be recalibrated once real data exists, not final commitments.

---

## Revision Notes

**v1 additions** (folded into the baseline single-mechanism design): citation-graph traversal alongside query decomposition, temporal fact validity, post-generation claim verification, and the eval harness treated as a standalone publishable artifact.

**v2 corrections** (from external technical review):
- Replaced valid-time-only "bi-temporal" fields with a genuinely bi-temporal model — added transaction-time fields (`recorded_at`, `retired_at`) alongside the existing valid-time fields (`effective_date`, `superseded_date`), so the system can distinguish "what was the rule on date X" from "what did TaxCite believe the rule was on date Y" (source corrections, delayed ingestion, retroactive legislation).
- Relabeled Meilisearch's role from "BM25 layer" to "lexical retrieval layer" (it uses a proprietary multi-criteria ranking system, not BM25), and replaced it with Qdrant's native sparse+dense hybrid retrieval — see ADR-6.
- Added authority-aware retrieval (§5.5) — tax sources carry different legal weight, and the design previously had no way to represent that in reranking.
- Moved the evidence-sufficiency gate to run after reranking and before synthesis, not after — see ADR-7.
- Split "answer quality" into three explicit eval dimensions (citation entailment, citation completeness, substantive correctness) since NLI entailment proves support, not correctness — see §5.4 and §9.
- Softened the 17–33% hallucination-rate framing from a "floor to beat" to an external reference point, and added a closed-book baseline to the eval comparison set.

**v3 corrections** (from a structured MAANG-style interview review — this revision):
- Decided the answer-delivery transport as a core architecture decision (SSE + durable job record) instead of leaving it implicit in "response returned" — see ADR-9, folded into §3.1/§3.3 and moved into Phase A.
- Replaced the per-candidate evidence-sufficiency design (up to `top_k × 3` LLM calls) with a single batched, structured-output call per sub-query — see ADR-10.
- Named the previously-unspecified LLM provider/model decision explicitly as open, rather than leaving it implicit — see ADR-11.
- Added a backup/disaster-recovery decision for the two stateful non-vector stores (Postgres, Neo4j) — see ADR-12.
- Closed the render-boundary gap where untrusted client-document content could re-enter as forged UI elements — see ADR-13.
- Added an explicit cost model and budget-governance section (§4.1), since "free tier" was previously a constraint with no supporting math.
- Specified chunking token targets/overlap per document type and flagged the embedding-model choice as an open, empirically-resolved decision (§3.2).
- Attached quantified precision/recall/accuracy targets and sample sizes to citation-graph and authority-metadata extraction, previously qualitative-only risks (§3.2, §9.3, §10).
- Defined the golden-set composition and the substantive-correctness labeling protocol, including an inter-rater reliability threshold (§9.1, §9.2) — previously "a small expert-labeled subset" with no further detail.
- Added production SLOs and alerting, distinct from the quality/ablation dashboard, and made PII-redaction ordering a tested CI invariant rather than an assumption (§3.4).

**v4 corrections** (resolving open decisions from PRD review):
- Fixed the monthly compute/API budget ceiling at <$50/mo (§4.1), narrowing ADR-11 accordingly.
- Replaced the human-labeling substantive-correctness protocol with an LLM-as-judge protocol, given no budget for manual review — including a judge-model-vs-generation-model separation, inter-judge reliability in place of inter-rater reliability, and an explicit correlated-error limitation (§9.2).
- Replaced inline flagging of unentailed claims with zero-tolerance suppression — any sub-answer containing a failed claim is suppressed entirely, never shown with a caveat (ADR-15).
- Decoupled live SSE delivery from Langfuse tracing, routing progress events through Redis instead, so an observability-tool outage can't degrade the live product (ADR-16).
- Filled in ADR-14 (model-boundary prompt-injection defense), which §6 and ADR-13 had referenced but which was never actually written out in §8.
- Added an explicit upload threat model — file-type allowlist, reject-on-mismatch, and an OCR/parsing-failure policy — for the previously unaddressed client-document upload path (§3.2).
- Clarified RAGAS-in-CI as a standing regression gate on all future retrieval/prompt/reranking/verification changes, not a one-time Phase B checkpoint (§7).
- Extended Redis caching to full verified sub-answers as the primary lever for staying under the cost ceiling (§3.4).
- Scoped Phase H's load-testing target to the actual persona's realistic query volume rather than an undefined "realistic concurrency" (§7).

**v5 corrections** (data-sourcing research):
- Added §11, a full data-sourcing reference with access method, cost, and current constraints for every ingestion source.
- Corrected a gap in the original design: eCFR only covers regulations (26 CFR), not the statute itself (26 U.S.C.) — added GovInfo/uscode.house.gov as the missing statute source (§11.1).
- Flagged that CourtListener's free-tier API access was cut from 5,000 requests/hour to 125/day as of May 2026, and revised the ingestion strategy accordingly: bulk CSV files for the initial load, the rate-limited API only for weekly incremental updates (§11.7).
- Added GovInfo's USCOURTS collection as a free, rate-limit-independent supplement to CourtListener for Circuit Court opinions, and Harvard's Caselaw Access Project as a historical-backfill source (§11.6).
- Named eyecite and Juriscraper (Free Law Project, open source) as the actual tools behind what was previously the vague placeholder "pattern-based citation parsing" (§3.2, §11.8, §4).

---

## 1. Business Framing

**Persona:** Renee, an Enrolled Agent running a 3-person tax prep and advisory practice serving roughly 400 individual and small-business clients.

**Problem:** Renee routinely needs to answer questions that require combining a general statutory rule (IRC/Treasury regs), an exception or clarification from Tax Court precedent, and a specific client's own numbers — e.g., "Can this client deduct home-office expenses under the simplified method given their business-use percentage, and does that conflict with the vehicle mileage they also claimed?" Keyword search across separate PDFs of the code, regs, and pubs doesn't synthesize that interaction. Renee either does the cross-referencing manually (25–40 minutes per nontrivial question) or pays for a mid-market research seat (CCH AnswerConnect/Checkpoint, ~$100–250/mo) that isn't built for a 3-person firm's workflow and never touches her actual client files.

A citation-grounded RAG system that retrieves across statute, precedent, and the client's own uploaded documents is the only option that's fast, cited, and personalized — a general LLM without retrieval hallucinates section numbers and expiration dates, a documented failure mode in existing legal-research AI tools that's worth tracking against, even if not treated as a strict pass/fail bar (see below).

**Success metrics:**
- Cut average per-question research time from ~30 minutes to under 5.
- Eliminate 80%+ of Renee's paid research-seat usage.
- Measure and publish an end-to-end groundedness rate on the golden set. Published hallucination rates for existing legal-AI research tools (17–33% in one Stanford study) are used as an **external reference point**, not a directly comparable baseline — different products, question distributions, and labeling methodologies mean the number isn't apples-to-apples. The primary comparison is against TaxCite's own closed-book and simpler-RAG baselines on the same held-out set (see §9).

---

## 2. Technical Pitch

TaxCite ingests federal tax statute/regulation text, U.S. Tax Court and relevant Circuit Court opinions, IRS publications, and per-tenant client documents. A compound tax question is split into a statutory sub-query, a case-law precedent sub-query, and a client-fact-extraction sub-query (query decomposition). Each sub-query is retrieved with hybrid (dense + lexical) search and a cross-encoder reranker.

For the case-law sub-query specifically, retrieval doesn't stop at vector similarity: seed opinions returned by hybrid search are expanded through a bounded citation-graph traversal (cites / distinguished-by / overruled-by / amends), surfacing precedent that a similarity-only search would miss.

Every retrieved fact — statutory and case-law — carries both a validity window (when the rule applied in the real world) and a record-history window (when TaxCite itself recorded or retired that fact), and an authority profile (statute vs. regulation vs. binding opinion vs. nonprecedential IRS publication). Reranking uses authority as an explicit signal, not just semantic similarity, so a highly relevant but low-authority source doesn't silently outrank a controlling one.

Before generation, an evidence-sufficiency check runs on the reranked candidates: any sub-query without enough supporting evidence is marked insufficient and excluded from what gets synthesized, rather than generated over and only checked afterward. The synthesis step then produces one cited answer over the sub-answers that passed. After synthesis, a separate claim-verification pass checks whether each generated claim is actually entailed by its cited source — a distinct check from whether retrieval had enough evidence to begin with, and one that proves support, not legal correctness (§5.4).

---

## 3. System Architecture

### 3.1 High-level data flow

```
                         ┌─────────────────────────────┐
                         │      Ingestion Sources       │
                         │ eCFR API · GovInfo/USC 26 ·  │
                         │ CourtListener · IRS.gov ·    │
                         │ client uploads (§11)         │
                         └──────────────┬───────────────┘
                                        │
                         ┌──────────────▼───────────────┐
                         │   Format-specific parsers     │
                         │ statute/XML · OCR · tables    │
                         └──────────────┬───────────────┘
                                        │
              ┌───────────┬─────────────┼─────────────┬───────────┐
              ▼           ▼             ▼              ▼           
     ┌────────────┐ ┌───────────┐ ┌───────────┐ ┌──────────────┐
     │ Chunker +   │ │ Citation-  │ │ Temporal   │ │ Authority     │
     │ embed       │ │ graph edge │ │ metadata   │ │ metadata      │
     │ (dense +    │ │ extraction │ │ tagging    │ │ tagging       │
     │ sparse)     │ │            │ │ (valid +   │ │ (type/level/  │
     │             │ │            │ │ record time)│ │ jurisdiction) │
     └──────┬──────┘ └─────┬──────┘ └─────┬──────┘ └───────┬──────┘
            ▼              ▼              ▼                ▼
     ┌─────────────┐ ┌────────────┐ ┌──────────────────────────┐
     │ Qdrant       │ │ Neo4j      │ │ Postgres                  │
     │ dense+sparse │ │ opinion/   │ │ metadata, temporal        │
     │ hybrid,      │ │ statute    │ │ validity + record-time    │
     │ shared + per-│ │ node/edge  │ │ windows, authority profile,│
     │ tenant       │ │ store      │ │ citations                 │
     └─────────────┘ └────────────┘ └──────────────────────────┘

Query path (client-facing transport per ADR-9):
POST /queries returns a job id immediately; the client opens
GET /queries/{id}/events (SSE) and receives one progress event per
stage below, terminating in an answer, refusal, or insufficient-
evidence event. Steps 1–8 run inside a single backend job; delivery
is decoupled from computation, and the final answer is buffered —
never token-streamed — until claim verification completes.

API gateway → auth/tenant resolver → query decomposer (LLM)              [event: decomposing]
   → parallel hybrid retrieval per sub-query, as-of + authority filtered [event: retrieving]
   → case-law sub-query additionally expands via graph traversal (1–2 hops)
   → cross-encoder rerank, authority-weighted                           [event: reranking]
   → evidence-sufficiency gate: ONE batched, structured-output call
     per sub-query over its full candidate set (ADR-10) — not one
     call per candidate — runs BEFORE synthesis                         [event: checking_sufficiency]
   → synthesis LLM call, only over sub-answers that passed the gate,
     with per-claim citation requirement; buffered, not token-streamed,
     until claim verification completes (ADR-9)                          [event: synthesizing]
   → claim-verification pass: decompose answer into atomic claims,
     check each against its cited source via NLI entailment model        [event: verifying]
   → terminal event: answer + trace ID, with authority annotations
     and all citation content rendered per the sanitized-rendering
     contract (ADR-13). Any sub-answer containing an unverified claim
     was already suppressed before this point (ADR-15) — nothing
     unverified ever reaches this event.
```

### 3.2 Ingestion pipeline

- Scheduled + event-driven pulls from eCFR API (regulations), GovInfo/uscode.house.gov (statute text — see correction in §11.1), CourtListener (case law), and IRS.gov (guidance and publications, scraped — no API exists). Full source-by-source access methods, costs, and current constraints are in §11.
- Format-specific parsers: statute/XML parser, OCR for scanned Tax Court memos, table extractor for rate schedules.
- **Chunker (per-document-type, token targets):**
  - *Statute:* section-level chunks (mirrors legal citation granularity), 200–500 tokens, no overlap — section boundaries are already semantically complete units. Parent-section metadata is retained so a chunk can be expanded to full-section context at generation time.
  - *Case law:* holding/dicta-tagged paragraph-level chunks, 150–400 tokens, one-paragraph overlap between adjacent chunks within the same opinion, to preserve cross-paragraph pronoun/reference resolution.
  - *Client documents:* form-field-level chunks (one chunk per extracted form line item or table row) where the source is structurally bounded; free-text portions (OCR'd memos, cover letters) fall back to ~300-token sliding-window chunks with 15% overlap.
- **Upload threat model (client documents):** accepted file types are allowlisted (PDF plus common scanned-image formats); anything else is rejected outright with a clear error rather than best-effort parsed. If OCR or table extraction fails on an accepted file, the affected content is marked "extraction failed — excluded from retrieval" rather than silently indexed as if it were reliable source text. Maximum upload size is `[DECISION NEEDED: specific size limit]` — arbitrary until real client-file sizes are observed in Phase G.
- **Embedding model:** `[DECISION NEEDED: specific dense embedding model]`. Phase A benchmarks at least two candidates — a general-purpose open-weights model and a legal/long-context-tuned alternative — on Recall@10/nDCG@10 against the Phase A pilot question set before locking in a choice. The sparse side uses Qdrant's built-in sparse retrieval, already decided by ADR-6; no separate decision is needed there.
- Citation-extraction step over case-law text to identify `CITES`, `DISTINGUISHES`, `OVERRULES`, and `AMENDS` relationships (eyecite for pattern-based citation parsing — see §11.8 — plus an LLM pass for ambiguous cases), writing nodes and edges into the graph store. **Validation:** a hand-labeled sample of 200 citation edges, stratified across the four relationship types, is scored for precision/recall by type. Target: precision ≥90%, recall ≥85% per type before graph-expanded candidates are allowed into reranking (Phase C gate; see §9.3).
- **Temporal tagging (bi-temporal):** every chunk gets `effective_date` / `superseded_date` / `superseded_by` (valid time — when the rule applied) *and* `recorded_at` / `retired_at` (transaction time — when TaxCite's own record was created or retired). Amendments create a new versioned node rather than overwriting the prior one; source corrections or delayed ingestion are now representable without confusing them with a change in the underlying law.
- **Authority tagging:** each chunk gets `authority_type` (statute / regulation / opinion / IRS publication / other guidance), `authority_level`, `court`, `jurisdiction`, `precedential_status`, `binding_on`, `publication_status`, `negative_treatment` (flagged if later overruled/questioned), and `source_revision`. Sourced from CourtListener court/jurisdiction metadata and IRS's own published-guidance status where available; gaps are logged and surfaced as "authority unknown," never silently defaulted to a safe level. **Validation:** a hand-labeled sample of 150 chunks against CourtListener/IRS source-of-truth fields, target ≥95% field-level accuracy before authority-aware reranking is enabled in production (Phase E gate; see §9.3).
- Embedding worker pool → Qdrant (dense + sparse hybrid, shared public-corpus collection + per-tenant namespace for client docs) + Postgres for metadata/citations/validity/authority.

### 3.3 Query path

1. API gateway → auth/tenant resolver.
2. Query decomposer (LLM call) splits the question into statutory, case-law, and client-fact sub-queries, and extracts a target "as-of" date (the relevant tax year) from the client-fact sub-query, defaulting to the current year.
3. Parallel hybrid (dense + lexical) retrieval per sub-query, filtered by the as-of date against each chunk's valid-time window.
4. Case-law sub-query only: seed results expand via a bounded (1–2 hop) traversal of the citation graph.
5. Cross-encoder reranks the combined vector + graph-expanded candidate set, using authority metadata (authority_level, precedential_status, jurisdiction) as an explicit boost/demote signal alongside semantic score — not semantic relevance alone.
6. **Evidence-sufficiency gate**, run here — after reranking, before synthesis. Implemented as a single batched, structured-output call per sub-query over that sub-query's full candidate set (ADR-10), not one call per candidate. The model returns a per-candidate support judgment plus a sub-query-level sufficiency verdict in one structured response. Any sub-query whose retrieved evidence falls below threshold is marked "insufficient evidence" and excluded from what gets generated.
7. Synthesis LLM call produces one answer, generated only over the sub-answers that passed the sufficiency gate, with a citation attached to every claim. The answer is buffered and not released to the client until step 8 completes (ADR-9).
8. Claim-verification pass: the synthesized answer is decomposed into atomic claims; each is checked against its cited source chunk using a self-hosted NLI/entailment model, producing a per-claim groundedness label (entailed / neutral / contradicted). Any sub-answer containing at least one non-entailed claim is suppressed in full and treated as insufficient evidence for that portion of the question (ADR-15) — no unverified claim is ever shown to the user, even with a caveat. This proves the claims that do survive are *supported*, not that the surviving answer is the legally *correct* one — see §5.4.
9. Terminal SSE event: response returned with trace ID, citations, and authority annotations for whatever survived step 8. All citation and source-derived text is rendered under the sanitized-rendering contract (ADR-13) — never as raw HTML.

### 3.4 Cross-cutting concerns

- Async ingestion queue (citation-graph extraction, temporal tagging, and authority tagging run as separate queue consumers so a slow pass doesn't block core indexing).
- Full-span tracing across all query-path steps via Langfuse (self-hosted), wrapped in a `@traced_node` decorator. Live progress events for the client (ADR-9) publish separately via Redis pub/sub, not sourced from Langfuse spans directly (ADR-16) — the same step instrumentation feeds both, but a Langfuse outage now degrades the eval dashboard's latency numbers, not the answer a user is waiting on.
- Structured logs with PII redaction on client-doc fields. **Redaction ordering is a tested invariant, not an assumption:** redaction runs in request preprocessing, before any span is emitted — never as a post-hoc filter on stored traces. A CI integration test plants a canary PII-shaped string (e.g., a synthetic SSN pattern) in a test client document and asserts it never appears in raw form in exported Langfuse spans; this gates any change touching the ingestion or tracing code paths.
- Redis serves three roles: caching repeated statute lookups and common as-of/tax-year query results; caching full verified sub-answers keyed by (sub-query text, candidate set, as-of date) so a repeated or near-repeated question doesn't re-run the paid LLM pipeline — the primary lever for staying under the §4.1 cost ceiling; and carrying live SSE progress events (ADR-16). Cache hit rate is expected to collapse toward near-zero for roughly a day after each weekly reindex before recovering — this is treated as an expected, non-alerting pattern (excluded from the latency SLO below during the reindex window), not a regression.
- **Production SLOs and alerting.** Distinct from the §9 eval-quality dashboard, which tracks correctness/ablation over time and updates per-release, this is a live-health view built on the same Grafana instance already used for Loki (§4), with alert rules over the existing Langfuse/Loki telemetry:
  - p95 end-to-end latency ≤35s on the synthesis path, ≤2s on the refusal path (first-pass targets, recalibrated against Phase H's k6 numbers).
  - Error rate <1% over a rolling 5-minute window.
  - Neo4j / Qdrant / Redis health-check failures — paired with the fail-open behavior in ADR-1/§10, an alert fires even when the system degrades gracefully, since graceful degradation should be visible to the operator, not just to the user.
  - Alerts route to `[DECISION NEEDED: Slack webhook vs. email vs. PagerDuty — Slack via Grafana Alerting's free-tier webhook integration is the default absent other constraints]`.
- **Render-boundary content handling (closes the gap identified in ADR-13).** Every piece of source-derived text reaching the client — synthesized answer text, citation excerpts, and any text pulled from client-uploaded documents — is rendered as sanitized/escaped content only, never as raw HTML. Citation chips, authority badges, and similar UI elements are populated exclusively from structured ingestion-pipeline fields (`authority_type`, `court`, etc.), never from arbitrary source text, so a string crafted inside an uploaded PDF cannot forge a UI element. See ADR-13 for the CI enforcement mechanism.
- **Cost tracking.** Cost-per-span (already captured by Langfuse) is rolled up into cost-per-query and monthly burn, surfaced on both the eval dashboard (§9) and the ops dashboard above — see §4.1 for the budget model.

---

## 4. Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Vector + lexical retrieval | **Qdrant, native dense + sparse hybrid (self-hosted)** | replaces a separate Meilisearch instance — see ADR-6; dense embedding model `[DECISION NEEDED — see §3.2/Phase A benchmark]` |
| Graph store | Neo4j Community (self-hosted) | citation graph (opinions, statute sections, edges) |
| Metadata/relational | Postgres (Supabase free tier) | citations, temporal validity + record-time windows, authority profiles |
| API | FastAPI | unchanged |
| Frontend / rendering client | `[DECISION NEEDED: framework]` | thin client; delivery protocol per ADR-9 (SSE); must satisfy the sanitized-rendering contract in ADR-13 regardless of framework chosen |
| Cache/queue | Redis (self-hosted) | extended for as-of query caching |
| Tracing | Langfuse (self-hosted) | spans for graph expansion, sufficiency gate, and verification; doubles as SSE event source (ADR-9) |
| Logging | Grafana Loki + Promtail (self-hosted) | unchanged; redaction-ordering enforced as a CI invariant (§3.4) |
| Alerting | Grafana Alerting (same Grafana instance as Logging) | routes to `[DECISION NEEDED: Slack/PagerDuty/email]` on SLO breach — see §3.4 |
| Claim verification | Self-hosted NLI/entailment model (e.g., a DeBERTa-v3-based NLI checkpoint) | production per-query check — see ADR-4 |
| Citation extraction / court & guidance scraping | eyecite + Juriscraper (Free Law Project, open source) | replaces the original placeholder "pattern-based citation parsing" — see §11.8 |
| LLM provider (decomposition / sufficiency / synthesis) | `[DECISION NEEDED — see ADR-11]` | resolved empirically in Phase A alongside the embedding-model choice; now constrained by a confirmed <$50/mo ceiling (§4.1) |
| Offline eval | RAGAS + LLM-as-judge | extended — see §9 (golden-set composition, correctness-grading protocol, per-phase gates) |
| CI/CD | GitHub Actions | extended with the injection-corpus gate (prompt path + render path, ADR-13) |
| Hosting | Railway/Render free tier or a free VPS | unchanged |
| Backup / DR | `pg_dump` (Postgres) + `neo4j-admin database dump` (Neo4j) + Qdrant snapshot API | target store `[DECISION NEEDED: object storage provider — free-tier candidates: Cloudflare R2, Backblaze B2]`, 14-day retention, quarterly restore drill — see ADR-12 |
| Load testing | k6 | unchanged |
| IaC | Terraform | unchanged |

### 4.1 Cost Model & Budget Governance

Cost was previously the least-specified constraint in this document despite "free tier" being load-bearing throughout §4. This section makes the model explicit.

**Per-query cost drivers (post-ADR-10):**
- Decomposition: 1 small-model LLM call.
- Retrieval + rerank: no LLM cost — embedding and cross-encoder inference only, self-hosted.
- Sufficiency gate: 1 batched structured-output call per sub-query — 3 sub-queries (statutory, case-law, client-fact) → 3 calls, down from as many as `top_k × 3` under the original per-candidate design (ADR-10).
- Synthesis: 1 long-context LLM call.
- Claim verification: self-hosted NLI model, near-zero marginal cost (ADR-4).

Worst case is now on the order of 5 LLM API calls per query (1 decompose + 3 sufficiency + 1 synthesis), down from as many as `2 + top_k × 3`.

**Budget ceiling: <$50/mo, confirmed as a hard constraint.** This is tighter than the low-tens-of-cents-per-query framing above can comfortably support at any real query volume once a hosted frontier-tier model is in the mix — at ~5 LLM calls per query, a few dozen daily queries against premium per-token pricing would burn through $50/mo quickly. This constraint directly narrows ADR-11: it points toward either a self-hosted open-weights model (no marginal per-call cost, but GPU/hosting burden on an already free-tier-constrained single-engineer project) or a budget-tier hosted model reserved for the cheap calls (decomposition, sufficiency), with anything pricier used sparingly if at all for synthesis. The cache extension above (caching full verified sub-answers, not just statute lookups) is the primary lever for staying under this ceiling as real usage grows, since repeated or near-repeated questions shouldn't re-run the full paid pipeline.

**Cost tracking:** cost-per-span is already captured by the existing Langfuse tracing (§3.4); aggregate cost-per-query and monthly burn are added as tracked metrics on both the eval dashboard (§9) and the ops dashboard (§3.4), reusing existing infrastructure rather than standing up a separate system.

---

## 5. Multi-Hop and Correctness Mechanisms

### 5.1 Query decomposition (baseline)

A compound tax question is split into statutory, case-law, and client-fact sub-queries so each can be retrieved with the right corpus and technique, rather than one undifferentiated similarity search.

### 5.2 Citation-graph traversal for case law

Tax Court and Circuit Court opinions cite, distinguish, and overrule each other; a pure hierarchical decomposition misses this. Hybrid search returns seed case-law candidates, and a bounded 1–2 hop graph traversal expands that set along `CITES`, `DISTINGUISHES`, `OVERRULES`, and `AMENDS` edges before reranking — without the infrastructure cost of full GraphRAG-style global summarization (Leiden clustering, global/local search modes), which this corpus doesn't need.

### 5.3 Bi-temporal fact validity

Every fact now carries two independent time dimensions:
- **Valid time** (`effective_date`, `superseded_date`, `superseded_by`): when the rule applied in the real world.
- **Transaction time** (`recorded_at`, `retired_at`): when TaxCite's own record of that fact was created or retired.

This distinction matters beyond "what was the rule in 2022" — it also lets the system answer "what did TaxCite believe the rule was on a given date," which is the relevant question when a source is corrected after the fact, ingestion is delayed, or legislation is applied retroactively. The query decomposer extracts a target tax year and filters retrieval by the valid-time window; transaction-time fields are used for audit and for reconstructing what the system would have answered at a prior point in time, not for routine query filtering.

### 5.4 Post-generation claim verification

The evidence-sufficiency gate (step 6, implemented as a batched call per ADR-10) and claim verification (step 8) catch different failure modes: insufficient evidence at retrieval time versus a generated claim the cited source doesn't actually support. Neither catches a third failure mode: **a claim can be entailed by its cited source and still be the wrong answer** — the source may have lower authority than another retrieved passage, apply to a different jurisdiction, have been superseded, omit a controlling exception, or support the words without supporting their application to the client's specific facts. NLI-based claim verification proves *support*, not *correctness*. §9 tracks these as three separate metrics rather than collapsing them into one "groundedness" number.

### 5.5 Authority-aware retrieval

Tax sources don't carry equal legal weight — a statute, a Treasury regulation, a binding Tax Court opinion, and a nonprecedential IRS publication are not interchangeable, even when they're all semantically relevant to the same question. Every chunk is tagged at ingestion with `authority_type`, `authority_level`, `court`, `jurisdiction`, `precedential_status`, `binding_on`, `publication_status`, `negative_treatment`, and `source_revision` (validated per §3.2 at ≥95% field-level accuracy). This is used two ways: as an explicit reranking signal (boosting higher-authority sources rather than relying on semantic similarity to surface them correctly), and in answer presentation (surfacing the authority level of each citation to the user, so a lower-authority source used for context is visibly distinguishable from the controlling one).

---

## 6. Requirement → Implementation Mapping

| Requirement | Implementation |
|---|---|
| Business problem | §1 — time-to-answer + paid-seat displacement, with an external (not directly comparable) hallucination-rate reference point |
| 500K+ multi-modal, multi-hop | Statute + Tax Court/Circuit opinions (CourtListener) + scanned pre-2000s memos + client doc scans |
| Multi-hop mechanism | Named: query decomposition + bounded citation-graph traversal for the case-law hop |
| Temporal correctness | Bi-temporal fact validity — valid time (effective/superseded) + transaction time (recorded/retired), as-of filtered retrieval |
| Authority correctness | Authority-aware reranking and presentation (§5.5), validated against a 95%-accuracy hand-labeled sample (§3.2) |
| Answer correctness | Evidence-sufficiency gate (pre-synthesis, batched per ADR-10) + post-generation claim-verification pass (NLI entailment); correctness tracked separately from entailment in eval (§9) |
| Eval | RAGAS recall@k/faithfulness + 100-question stratified golden set (§9.1) + CI gate + published ablation report with three-tier correctness metrics + substantive-correctness grading protocol (§9.2) |
| Observability | Langfuse span tracing across all query-path steps, cost/latency per span, plus production SLO alerting distinct from the quality dashboard (§3.4) |
| Logging | Structured JSON logs via Loki, PII redaction on client-doc fields, redaction-ordering enforced as a tested CI invariant (§3.4) |
| Cost governance | Per-query cost model, sufficiency-gate call batching (ADR-10), budget ceiling framework (§4.1) — `[DECISION NEEDED]` on the final number |
| Answer delivery / serving | SSE progress transport + durable job record (ADR-9), decided in Phase A, not discovered post hoc |
| Render-boundary security | Sanitized-rendering contract, structured-field-only UI population, injection corpus gated on the render path (ADR-13) |
| Backup / disaster recovery | Nightly Postgres/Neo4j dumps + Qdrant snapshots, quarterly restore drill (ADR-12) |
| System design | Async ingestion queue, API gateway, Redis cache, Terraform IaC, per-tenant vector namespace, graph store |
| Multi-user | Tenant-scoped auth, per-tenant quotas, cross-tenant filter enforced at query layer, 0-tolerance leakage test (Phase G) |
| Free-tier infra | Full stack in §4, all self-hostable or free-tier where a provider is chosen; LLM provider choice (ADR-11) is the one line item not yet pinned to free tier |
| Security | Prompt-injection defense on untrusted client-uploaded PDFs (ADR-14), extended to the render boundary (ADR-13); secrets via env/vault, never in code |
| Resilience | Circuit breaker on case-law retrieval → fallback to statute-only answer with explicit caveat; graph-expansion step fails open to vector-only results if Neo4j is unavailable; failures are alerted, not just absorbed (§3.4) |
| Data freshness | Weekly incremental reindex on IRB updates; amendments versioned, not overwritten |
| Extraction validation | Citation-graph and authority-metadata extraction each validated against a quantified hand-labeled sample with a precision/recall or accuracy target (§3.2, §9.3) |
| CI/CD | GitHub Actions: unit tests + RAGAS gate + injection-corpus gate (prompt path + render path) + deploy |
| Load testing | k6, real p50/p95 latency numbers across all query-path spans, measured against first-pass SLO targets (§3.4, Phase H) |
| Docs/ADRs | §8 — 13 ADRs total after this revision |

---

## 7. Build Phases

No calendar estimates — this is a dependency order.

**Phase A — Core retrieval baseline.** eCFR Title 26 + IRS pubs only, single-hop hybrid (Qdrant dense + sparse) retrieval, no decomposition, single-tenant, manual eval on a small (~20-question) pilot set. Includes a closed-book (no-retrieval) baseline for later comparison. **Also decided here, not deferred:** ADR-9 (SSE progress transport + durable job record) and ADR-11 (LLM provider/model choice for decomposition, sufficiency-gate, and synthesis calls), benchmarked alongside ≥2 candidate embedding models on Recall@10/nDCG@10 against the pilot set. These are core-architecture decisions, not delivery-layer afterthoughts.

**Phase B — Decomposition + eval infrastructure.** Add Tax Court/case-law corpus, implement query decomposition, build the 100-question golden set (stratified per §9.1), wire RAGAS into CI as a **standing** regression gate on every future PR touching retrieval, prompts, reranking, or verification models — not a one-time Phase B checkbox — **build fails if faithfulness drops below 0.85 on the golden set.**

**Phase C — Citation graph.** Stand up Neo4j, run citation-extraction over the case-law corpus, add bounded graph-expansion into case-law retrieval. **Gate (both required before the graph is treated as load-bearing):** Recall@20 on case-law sub-queries improves by ≥5 points over the decomposition-only baseline, AND edge-extraction precision ≥90% / recall ≥85% on a 200-edge hand-labeled sample (§3.2).

**Phase D — Temporal validity.** Add valid-time and transaction-time metadata to statute and case-law chunks, implement as-of filtering, add amendment-versioning to ingestion. **Gate:** ≥90% accuracy on a held-out set of retroactive/amended-rule questions.

**Phase E — Authority-aware retrieval.** Add authority metadata at ingestion, incorporate into reranking, add authority annotations to answer presentation. **Gate:** authority metadata ≥95% field-level accuracy on a 150-chunk hand-labeled sample (§3.2); reranking must change the top-1 result on a curated authority-conflict subset without a >2-point Recall@20 regression elsewhere.

**Phase F — Evidence sufficiency + claim verification.** Move the sufficiency check to run pre-synthesis, implemented as a single batched structured-output call per sub-query (ADR-10), not one call per candidate. Stand up the self-hosted NLI model; add the post-generation verification pass, with zero-tolerance suppression of any sub-answer containing a failed claim (ADR-15). **Gate:** entailment F1 ≥0.90 (NLI vs. LLM-as-judge audit per ADR-4), completeness ≥0.85. Begin substantive-correctness grading via the LLM-judge protocol (§9.2); this metric is tracked, not gated, until ≥100 AI-judge-graded examples exist.

**Phase G — Multi-tenant + hardening.** Per-tenant client-document ingestion, auth/authz, quotas. **Gate:** cross-tenant leakage test — 0 tolerated failures. Extend the injection test corpus with render-path assertions (ADR-13); both prompt-path and render-path suites must pass 100% before any real client document is ingested.

**Phase H — Resilience + load.** Circuit breakers/fallbacks (including graph-store fail-open), incremental reindexing, load testing at realistic concurrency (k6). "Realistic" is scoped to the actual persona — a 3-person practice generating on the order of dozens of questions per week, not multi-tenant market-scale load — so k6 targets a generous multiple of that (e.g., a handful of concurrent queries), not large-scale concurrent-user assumptions; revisit this scoping if the target-market open question resolves toward a wider audience. **Targets:** p95 ≤35s on the synthesis path, ≤2s on the refusal path (first-pass, recalibrate against real k6 data); error rate <1%; cost-per-query measured against the confirmed <$50/mo ceiling (§4.1) once ADR-11's specific model is resolved. Implement ADR-12 (backup/DR + quarterly restore drill) and stand up the production alerting in §3.4. Full docs and ADRs.

---

## 8. Architectural Decision Records

**ADR-1: Decomposition + bounded citation-graph traversal, not decomposition alone or full GraphRAG.**
*Decision:* Layer a bounded 1–2 hop citation-graph expansion onto the case-law sub-query, backed by self-hosted Neo4j, rather than full GraphRAG community detection.
*Trade-off:* An added datastore and hop-limit tuning, against real gains on multi-hop legal reasoning that decomposition alone misses.

**ADR-2: Bi-temporal fact validity — valid time and transaction time both tracked.**
*Context:* The original design tracked only valid-time fields (effective/superseded dates) and was mislabeled "bi-temporal." A genuinely bi-temporal model also needs transaction time — when the system recorded or retired a version, independent of when the rule itself applied.
*Decision:* Track both dimensions: `effective_date`/`superseded_date`/`superseded_by` (valid time) and `recorded_at`/`retired_at` (transaction time).
*Trade-off:* Extra metadata and two independent filtering dimensions, against the ability to correctly answer both "what was the rule on date X" and "what did the system believe on date Y" — relevant whenever a source is corrected, ingestion is delayed, or legislation is retroactive.

**ADR-3: Post-generation claim verification, not retrieval-confidence gating alone.**
*Decision:* Add a claim-decomposition + NLI-entailment pass over the synthesized answer, independent of the evidence-sufficiency gate.
*Trade-off:* Added latency/cost per query, against a directly measurable, publishable entailment rate. Note this proves support, not legal correctness (§5.4) — it's one of three tracked correctness metrics, not a stand-in for all of them.

**ADR-4: Self-hosted NLI model, not LLM-as-judge, for the production verification pass.**
*Decision:* Use a specialized, self-hosted NLI/entailment model for the per-query verification pass; reserve LLM-as-judge for the offline eval harness.
*Trade-off:* Cheaper and faster than a per-claim LLM call, but less nuanced on ambiguous entailment cases; mitigated by periodically auditing the NLI verifier's error rate against LLM-as-judge offline (target F1 ≥0.90, §9.3).

**ADR-5: Shared corpus + per-tenant namespace, not fully siloed indices.**
*Decision:* One statute/case-law index and citation graph serve all tenants; isolation enforced at the query-filter layer.
*Trade-off:* A small blast-radius risk (a misconfigured filter) against large storage/compute savings — compensating control: an integration test asserting the cross-tenant filter fires on every query, including graph-traversal queries (0-tolerance gate, Phase G).

**ADR-6: Qdrant native sparse+dense hybrid retrieval, not a separate Meilisearch instance.**
*Context:* The original stack labeled Meilisearch as "the BM25 layer." Meilisearch uses a proprietary multi-criteria ranking system, not BM25 — the label was simply wrong, and keeping an extra datastore around a mislabeled component wasn't justified.
*Decision:* Use Qdrant's native sparse+dense hybrid support (fusion of sparse lexical vectors and dense embeddings in one collection) instead of a separate lexical search engine.
*Trade-off:* Loses Meilisearch's typo-tolerance/faceting conveniences, but removes a datastore from the operational surface and fixes the terminology problem directly. If a later stage needs true BM25 scoring specifically, revisit with a dedicated engine (Elasticsearch/OpenSearch) rather than mislabeling a different ranking system as BM25.

**ADR-7: Evidence-sufficiency gate runs before synthesis, not after.**
*Context:* The original design ran the confidence check after synthesis — meaning generation happened over evidence that might then be discarded, and the model could produce unsupported text before insufficiency was flagged.
*Decision:* Move the gate to run after reranking, before synthesis; synthesis runs only over sub-answers that passed.
*Trade-off:* Requires synthesis to handle partial input gracefully (some sub-answers present, others marked insufficient), in exchange for not generating — and then having to retract — unsupported content.

**ADR-8: Authority-aware reranking, not purely semantic reranking.**
*Context:* The original cross-encoder rerank scored candidates on semantic relevance alone; a highly relevant but nonprecedential IRS publication could outrank a controlling statute or binding opinion.
*Decision:* Attach authority metadata to every chunk at ingestion and use it as an explicit reranking signal alongside semantic score, and surface authority level in the UI rather than leaving it implicit in ranking order.
*Trade-off:* Requires reliable authority metadata at ingestion, itself a source of extraction error (§10), in exchange for behaving like a domain-aware legal tool rather than generic semantic search over legal-flavored text.

**ADR-9: Answer delivery transport — SSE progress stream over a durable job record.**
*Status:* Decided.
*Context:* The query path is a long-running, multi-stage pipeline (15–30s estimated p50 pre-optimization) with several terminal outcomes (answer, scope refusal, insufficient evidence) that must remain visible, not buried in a payload the user reads after the fact. This was previously left implicit ("response returned") and only surfaced as a gap in a later review pass — a mistake this revision corrects by deciding it here, in the core architecture, not the delivery layer.
*Options considered:* (A) synchronous request/response — simplest, but a worker is pinned for the full pipeline duration, free-tier proxy idle timeouts (commonly 30–60s) sit right on top of worst-case latency, and a dropped connection loses a query that cost several LLM calls. (B) SSE progress stream — `POST /queries` returns immediately, client opens `GET /queries/{id}/events`; the existing `@traced_node` span emitter (§3.4) becomes the event source essentially for free. (C) async job + polling — durable, but polling granularity fights against per-stage progress and wastes requests against a ~25s job.
*Decision:* SSE for progress, backed by a durable job record so a dropped connection doesn't lose the underlying job. The synthesized answer is buffered and released only after claim verification completes — never token-streamed — so an unverified claim is never shown to a credentialed preparer before it's checked.
*Trade-off:* Medium implementation complexity and a reconnect story to build, against making degradation, refusal, and abstention first-class visible events instead of fields on a payload the user reads after 25 seconds of silence.

**ADR-10: Batch the evidence-sufficiency gate into one call per sub-query.**
*Status:* Decided.
*Context:* The original per-candidate design issued one LLM call per retrieved candidate per sub-query for a sufficiency judgment — up to `top_k × 3` calls per query, the single most expensive and slowest step in the pipeline.
*Decision:* Replace this with one structured-output (JSON-schema-constrained) call per sub-query, presenting all of that sub-query's top-k reranked candidates together and requiring the model to return both a per-candidate support judgment (preserving per-candidate granularity in the output schema) and a sub-query-level sufficiency verdict, in a single round trip.
*Trade-off:* A single call judging many candidates together risks anchoring/averaging across them versus fully independent per-candidate calls — mitigated by requiring the per-candidate field in the structured output rather than only an aggregate verdict, and monitored via the same entailment/completeness eval in §9. In exchange: call count per query drops from as many as `top_k × 3` to 3 (one per sub-query), directly addressing both the cost model (§4.1) and the step-8 latency identified as a critical path item.

**ADR-11: LLM provider and model tiering — gpt-4o-mini, with a measured revisit trigger.**
*Status:* Decided (2026-09-21), from the T8 benchmark on the pilot set.
*Context:* §3.3's decomposition, sufficiency-gate and synthesis calls have different cost/latency/quality needs, and §4.1 fixes a <$50/mo ceiling. The ceiling turned out **not** to be the binding constraint: at the persona's volume (dozens of questions per week, ~200/mo) the whole pipeline costs ~$0.10/mo on gpt-4o-mini and ~$0.86/mo on claude-haiku-4-5. §4.1's "a few dozen daily queries" premise only bites above ~500 queries/mo. The decision therefore rests on answer quality and citation behaviour, not price.
*Measured (20 pilot questions x 2 models x {closed_book, rag}, §9.2 rubric, judge from the other provider, $0.18 total):*

| model | mode | correct | wrong | gold cited | exact cites | fabricated | refused when it should | p50 | $/query |
|---|---|---|---|---|---|---|---|---|---|
| gpt-4o-mini | closed_book | 0.44 | 0.06 | 0.00 | 0 | 0 | 0/2 | 1.5s | $0.0001 |
| **gpt-4o-mini** | **rag** | **0.61** | **0.00** | 0.33 | 18 | 1 | 1/2 | **1.1s** | $0.0005 |
| claude-haiku-4-5 | closed_book | 0.28 | 0.06 | 0.00 | 0 | 0 | 0/2 | 3.6s | $0.0013 |
| claude-haiku-4-5 | rag | 0.33 | 0.06 | **0.50** | 32 | **0** | **2/2** | 3.0s | $0.0043 |

*Judge reliability:* Cohen's kappa **0.81** across 72 graded answers (§9.2 requires >=0.70), two judges applying the same rubric in different wording. See log #31 for why the first attempt produced a false 0.65.
*Decision:* `gpt-4o-mini` at all three call sites for now. It is materially more correct (0.61 vs 0.33), never outright wrong under RAG, ~3x faster and ~8x cheaper.
*The trade-off this accepts, stated plainly:* the two models fail in opposite directions. Haiku grades worse but cites better — it found the gold citation on 50% of questions against gpt's 33%, fabricated nothing where gpt fabricated one, and refused both unanswerable questions where gpt refused one. For a product whose thesis is verifiable citation, that is the uncomfortable half of the result.
*Why the trade is acceptable now:* Phase F's NLI verifier (ADR-4) checks claims mechanically and suppresses unverified ones (ADR-15), which is a stronger guarantee than a model's citing habits. Sparse citing costs recall against that gate; fabrication would cost trust.
*Revisit trigger:* if Phase F's suppression rate is high **because synthesis cited too little or too loosely**, move synthesis to `claude-haiku-4-5` and keep gpt-4o-mini for decomposition and the sufficiency gate — the tiering this ADR was always meant to allow. Re-run `eval/llm_bench.py` to re-test.
*Also settled here:* the §9.2 judge must come from the other provider, so claude-haiku-4-5 grades gpt-4o-mini's answers. Reasoning/thinking is off everywhere for now: it is affordable (~$1-4/mo at persona volume) but unproven here, and synthesis is the only call site where it plausibly helps.

**ADR-12: Backup and disaster recovery for stateful non-vector stores.**
*Status:* Decided, pending storage-provider choice.
*Context:* A single engineer operates five self-hosted stateful/near-stateful services (Qdrant, Neo4j, Postgres, Redis, Langfuse) on free-tier infra. None had a stated backup or recovery plan.
*Decision:* Nightly `pg_dump` (Postgres) and `neo4j-admin database dump` (Neo4j), plus Qdrant's built-in snapshot API on the same cadence, written to `[DECISION NEEDED: object storage provider — free-tier candidates: Cloudflare R2, Backblaze B2]`, retained 14 days. A quarterly restore drill into a scratch environment confirms dumps are actually restorable, not just produced.
*Trade-off:* Modest storage cost and a recurring operational task, against not losing the citation graph or client data to a single host failure — a real risk given the solo-operator, multi-datastore setup (§10).

**ADR-13: Render-boundary content handling — sanitized rendering only, structured fields for UI elements.**
*Status:* Decided.
*Context:* Model-boundary prompt-injection defense (ADR-14, below) stops adversarial content from manipulating the model itself. It does not stop tainted text from re-entering at the render boundary: if source-derived text (including text extracted from an untrusted client PDF) is ever rendered as raw HTML, a crafted document could forge citation chips or authority badges in the browser even if the model was never fooled.
*Decision:* All model-generated and source-derived text reaching the client is rendered as sanitized/escaped text only — never via a "render trusted HTML" pathway. Citation chips, authority badges, and similar UI elements are populated exclusively from structured ingestion-pipeline fields (`authority_type`, `court`, `precedential_status`, etc.), never from arbitrary source text, so a forged string inside a client document cannot produce a fake UI element. The prompt-injection test corpus (ADR-14) is extended with a render-path suite: known XSS/HTML-injection payloads planted inside synthetic client documents must not execute and must not alter chip/badge rendering, verified via a headless-browser CI check (e.g., Playwright) asserting DOM output against an allowlist. This gates any deploy touching ingestion or rendering code, and both suites (prompt-path, render-path) must pass 100% before real client documents are ingested (Phase G).
*Trade-off:* Additional CI surface and a frontend-framework decision (`[DECISION NEEDED]`, §4) that has to satisfy this contract, against closing an attack path that would otherwise let a malicious client upload forge trust signals directly in the UI.

**ADR-14: Model-boundary prompt-injection defense for untrusted client documents.**
*Status:* Decided.
*Context:* Client-uploaded documents are untrusted input that ultimately reaches LLM calls (retrieved chunks included in the synthesis context). A malicious or compromised upload could contain text crafted to manipulate the model — instruction-override attempts, role-play jailbreaks, or requests to exfiltrate another tenant's data.
*Decision:* Retrieved client-document content is always inserted into prompts as clearly delimited, labeled data — never as free-floating text the model could mistake for instructions — and the system prompt explicitly directs the model to treat all retrieved content as reference material only, regardless of what it says. A dedicated injection test corpus (synthetic client documents carrying known injection payloads) runs in CI; the pipeline must correctly ignore every payload (100% pass) before real client documents are ingested — the same Phase G gate that governs the render-path suite in ADR-13.
*Trade-off:* Legitimate client content that reads as instructional ("please note the following applies") needs careful prompt-boundary design to avoid false-positive suppression, in exchange for not letting an uploaded document hijack model behavior or exfiltrate cross-tenant data.

**ADR-15: Zero-tolerance claim display — suppress, never flag-and-show.**
*Status:* Decided.
*Context:* The original design (v3 of this document) flagged unentailed claims inline as a middle ground — showing the generated text with a caveat rather than hiding it. Stakeholder decision: no unverified claim should ever reach the user, even flagged.
*Decision:* Any sub-answer containing at least one claim that fails verification (neutral or contradicted, §3.3 step 8) is suppressed in its entirety and treated as if it had failed the evidence-sufficiency gate — excluded from the final answer, not shown with a warning. This is a single-failing-claim trigger, not a percentage threshold.
*Trade-off:* More sub-answers will be suppressed than under a flagging or partial-threshold approach — some queries that would have gotten a mostly-useful, partially-flagged answer will instead get an "insufficient evidence" outcome for that portion. In exchange, there is no partially-trusted content in front of the user, and no standing UI disclaimer is needed to compensate for one, since nothing unverified is ever displayed.

**ADR-16: Live-delivery transport decoupled from tracing.**
*Status:* Decided.
*Context:* The original SSE design (ADR-9) sourced live progress events directly from Langfuse span emission — a convenient single mechanism, but one that coupled the product's live delivery to an observability tool's uptime. A Langfuse outage would have degraded the actual answer stream, not just the quality dashboards.
*Decision:* Live progress events publish to Redis pub/sub (already in the stack); the same step instrumentation continues to emit to Langfuse independently, for offline trace analysis only.
*Trade-off:* One more integration point per pipeline step (publish to both channels) in exchange for separating failure domains — Langfuse going down now degrades observability, not the response the user is waiting on.

**ADR-17: Vector store — Qdrant, not pgvector or another vector database.**
*Status:* Decided (2026-09-19). Evidence pending: Phase A task T6b benchmarks Qdrant against pgvector on the same data (hybrid recall, filtered-recall loss, p95 latency, projected storage) and applies the revisit trigger below.
*Context:* ADR-6 settled Qdrant vs. a separate lexical engine (Meilisearch) but never recorded why Qdrant beat other vector stores. The retrieval layer has four requirements: (1) dense + sparse hybrid retrieval with fusion in a single query (ADR-6); (2) filtering applied during the vector search on valid-time windows (ADR-2, Phase D), tenant namespace (ADR-5, Phase G) and authority fields (Phase E), without losing recall under strict filters; (3) self-hostable at zero license cost within the <$50/mo ceiling (§4.1); (4) operable by one engineer (§10).
*Options considered:*
- (A) **Qdrant.** Native dense + sparse vectors in one collection with server-side fusion. Filters are applied during the approximate-nearest-neighbour graph search rather than after it. Runs as a single lightweight container with a snapshot API (ADR-12). Meets all four requirements.
- (B) **pgvector in the existing Postgres.** The strongest alternative: it removes a store entirely and keeps chunk text, metadata and vector in one row, so they cannot drift apart. It loses on three points. Hybrid search needs hand-written fusion SQL over pgvector plus Postgres full-text search or `sparsevec`. Its approximate indexes filter after the search, so strict filters (a single tax year, a single tenant) can silently return fewer than k results unless index tuning or iterative scans are added. And vectors for the full corpus would share, and likely exceed, the small storage cap of the managed free-tier Postgres (Supabase, §4).
- (C) **Weaviate.** Built-in hybrid search with true BM25, which fixes the terminology problem ADR-6 raised, plus good filtering. It is heavier to run than Qdrant and adds no capability TaxCite needs; ADR-6 already scoped lexical matching to sparse vectors, not BM25 specifically.
- (D) **Pinecone.** Supports sparse + dense, but it is managed-only and paid beyond a limited free tier, so it fails requirement (3) and removes the self-hosted, inspectable stack.
- (E) **Milvus.** Capable, but a production deployment needs several supporting services, which fails requirement (4).
- (F) **Elasticsearch / OpenSearch.** True BM25 plus vector search, but memory-hungry, and explicitly a non-goal (PRD §4) unless literal BM25 scoring is later shown to be needed.
- (G) **Chroma / LanceDB.** Light and embedded, but hybrid fusion and filtered search are less mature for this workload.
*Decision:* Qdrant, self-hosted. It is the only option that meets all four requirements without extra code (B), extra services (E, F) or recurring cost (D).
*Trade-off:* One more stateful store to operate and back up (ADR-12), and chunk metadata is split across Postgres (source of truth) and the Qdrant payload (a filter copy). The copy can drift, so ingestion writes both from one code path and re-running ingest is idempotent.

*Revisit trigger, as first written:* reopen if the corpus fits managed Postgres and pgvector's filtered recall is within 2 points of Qdrant's. **That trigger was mis-specified** — it omitted overall retrieval quality, and both of its conditions passed. The condition that decided the outcome had to be added after measuring: hybrid recall within 2 points.

*Measured 2026-09-20 (T6b, `eval/store_bench.py`), same bge-base vectors in both stores, 18 pilot questions, k=10:*

| store | hybrid Recall@10 | dense only | lexical only | filtered recall (approx vs exact) | p50 | p95 | storage |
|---|---|---|---|---|---|---|---|
| **Qdrant** | **0.667** | 0.583 | 0.444 (BM25) | 0.779 | 14 ms | 61 ms | 24 MB vectors |
| pgvector | 0.500 | 0.528 | 0.111 (`ts_rank_cd`) | 0.779 | 52 ms | 130 ms | 77 MB table + indexes |

*Outcome: CONFIRMED — Qdrant stays.* Storage passes (77 MB now, ~386 MB projected with case law, inside a 500 MB free tier) and filtered recall is **identical**, disproving the assumption that pgvector's post-filtering would lose recall at this corpus size. The decisive gap is lexical: Postgres full-text ranking is not BM25 and has no comparable inverse-document-frequency weighting, scoring 0.111 against Qdrant's 0.444 on the same queries. Since ADR-6 chose hybrid retrieval precisely because legal text needs literal matching (`§280A`, `Form 8829`), a store that cannot rank lexically defeats the design.

*What would change this:* a Postgres BM25 extension (ParadeDB `pg_search`) closing the lexical gap, or a future where the lexical half stops mattering. Neither is available on a managed free tier today. Re-run `eval/store_bench.py` to re-test.

*Noted for Phase D:* approximate search returned only **77.9% of the exact top-10 under a strict single-section filter, in both stores**. Phase D filters by tax year, which is the same shape, so as-of filtering will need exact search or a raised `ef_search` rather than default ANN parameters.

**ADR-18: Dense embedding model — BAAI/bge-base-en-v1.5.**
*Status:* Decided (2026-09-20), from measurement on the Phase A pilot set.
*Context:* §3.2 left the dense model open and required benchmarking at least two candidates on the pilot set before locking one in. Candidates had to be self-hostable at zero marginal cost (§4.1) and fast enough that three sub-query embeddings fit inside the 35s end-to-end budget (ADR-9).
*Viability screen, before any quality measurement:* `nomic-embed-text-v1.5` embeds at 0.2 chunks/s on this CPU (8.6 hours for the 7,652-chunk corpus) and takes **491 ms per query embed**; its quantised variant is no faster. At three sub-queries per question that is ~1.5s of embedding before retrieval starts, for an 8192-token context the corpus never uses (chunks cap at ~500 tokens). Excluded on latency, not quality. `thenlper/gte-base` errors inside fastembed 0.8 and was not pursued.
*Measured on 18 pilot questions, full 7,652-chunk corpus (both sources), k=10:*

| model | mode | Recall@10 | nDCG@10 | MRR | Section recall | regulation | publication | query ms |
|---|---|---|---|---|---|---|---|---|
| bge-small-en-v1.5 (384d) | dense | 0.500 | 0.278 | 0.185 | 0.667 | 0.562 | 0.000 | 24 |
| bge-small-en-v1.5 | hybrid | 0.611 | 0.259 | 0.131 | 0.722 | 0.625 | 0.500 | 18 |
| **bge-base-en-v1.5 (768d)** | dense | 0.583 | 0.401 | 0.315 | 0.667 | 0.656 | 0.000 | 54 |
| **bge-base-en-v1.5** | **hybrid** | **0.667** | **0.350** | 0.181 | **0.778** | **0.688** | 0.500 | 31 |

*Decision:* `BAAI/bge-base-en-v1.5`, 768 dimensions.
*Rationale:* the ranking gains exceed the recall gains — nDCG +9 points and dense MRR +13 — which matters because synthesis only sees the top few chunks. It also recovers about half of the 12.4-point regulation-recall loss that adding IRS publications caused (log #24): 0.625 → 0.688.
*Trade-off:* the index build goes from 9.3 to 31.6 minutes (3.4x) and dense vectors from 12 MB to 24 MB; query embedding goes from 18 ms to 31 ms, negligible against a 35s budget. The real cost is slower iteration: any change that forces a re-index now costs half an hour.
*Measurement caveat (found after this decision, see log #28):* with 18 pilot questions one question is worth 5.6 points, and a tie at the k boundary made hybrid numbers vary by exactly that much between runs until ties were broken deterministically. The hybrid recall gap between these two models (+5.6) is therefore at the resolution limit of this set; **the decision rests on the deterministic dense metrics** (recall +8.3, nDCG +12.3, MRR +13.0), which were stable across runs. The 100-question golden set in §9.1 is what raises this resolution.
*Noted for later:* dense retrieval scores **0.000** on publication questions for both models, while hybrid scores 0.500. Publications are matched lexically, not semantically — further support for ADR-6's hybrid design, and a caution against treating dense-only numbers as representative.
*Revisit trigger:* if a re-index ever blocks iteration, or if Phase E reranking closes the regulation gap on its own, re-run `eval/embed_bench.py` — bge-small remains a 3.4x cheaper fallback at a measured cost of ~5.6 points of hybrid recall.

---

## 9. The Eval Harness as a Standalone Deliverable

Published as its own artifact, not just internal QA:

- A public dashboard tracking retrieval and generation quality over time, comparing: **closed-book (no retrieval) → dense-only → hybrid (dense+sparse) → hybrid+reranked → +decomposition → +graph expansion → +temporal filtering → +authority-aware reranking → +claim verification.** Each stage isolated so the report shows what each mechanism actually contributes, not just the final system's aggregate score.
- Metrics reported separately, not collapsed into one number:

| Area | Metrics |
|---|---|
| Retrieval | Recall@k, nDCG@k, MRR |
| Citation entailment | Does the source support the claim? (NLI precision/recall/F1, false-accept rate) |
| Citation completeness | Are all material claims cited? |
| Substantive correctness | Is the conclusion correct given the relevant authorities and facts? — graded by an LLM judge on a 40-question subset (protocol: §9.2) |
| Graph extraction | Edge precision/recall by relationship type |
| Temporal behavior | Accuracy on historical and retroactive-rule questions, both valid-time and transaction-time queries |
| Authority weighting | Cases where authority-aware reranking changed the top result vs. semantic-only |
| Abstention | Precision/recall of "insufficient evidence" decisions |
| Security | Cross-tenant leakage and prompt-injection test results (prompt path + render path, ADR-13) |
| Operations | p50/p95 latency, throughput, error rate, cost per query (§4.1) |

- A held-out test set that isn't repeatedly tuned against.
- The measured groundedness rate reported against the external Stanford-study reference point (17–33%), explicitly labeled as a reference rather than a directly comparable baseline, given differing products, question distributions, and labeling methodology.
- The NLI verifier's own periodic audit results against LLM-as-judge (per ADR-4).

Failure analysis is published alongside successes: e.g., graph expansion pulling in an irrelevant later case, the system selecting the wrong tax year, the NLI model accepting an overgeneralized claim, authority weighting changing an answer, a correct abstention, or a citation that's relevant but doesn't fully support the conclusion.

### 9.1 Golden set composition

100 questions, stratified so no single question type dominates the aggregate score:

| Category | Count |
|---|---|
| Statutory-only | 25 |
| Case-law-only | 20 |
| Compound (multi-hop: statute + case law + client facts) | 30 |
| Temporal edge case (retroactive rule, amended return, ambiguous as-of year) | 10 |
| Expected insufficiency (should trigger the sufficiency gate) | 10 |
| Adversarial / injection (malicious client-doc content) | 5 |
| **Total** | **100** |

The adversarial/injection subset is scored against the render-boundary contract (ADR-13) and the prompt-injection defense, not against answer-quality metrics.

### 9.2 Substantive-correctness grading protocol

Substantive correctness (§5.4, §10) is the hardest metric to produce, and this project has no budget for manual labeling. Protocol, revised accordingly:

- **Sample:** the same 40 questions, drawn proportionally from the compound, statutory-only, and case-law-only categories (adversarial and expected-insufficiency questions aren't scored for legal correctness).
- **Rubric:** unchanged — 3-point scale per answer (*Correct* / *Partially correct* / *Incorrect* — misses a material exception, conflates jurisdiction, or omits a conflicting claim, e.g. the home-office/mileage interaction from §1's own example) plus a defect tag from a fixed taxonomy: wrong section cited, superseded rule applied, wrong tax year, authority misweighted, hallucinated fact not in any source.
- **Grader:** an LLM-as-judge call applies the rubric to each sampled answer, replacing human review entirely. The judge model must differ from whatever model performs synthesis (ADR-11) — grading a model's output with the same model risks the judge sharing the generator's blind spots rather than catching them.
- **Reliability, without a second human:** the rubric is applied twice per answer — once by the primary judge, once by a second, differently-configured judge (a different model, or the same model at a different temperature/prompt phrasing) — and agreement between the two AI graders is measured the same way inter-rater reliability would be (Cohen's κ ≥0.7 required before the metric is reported as trustworthy). Disagreements are logged as low-confidence gradings, not adjudicated by a human.
- **Known limitation, stated explicitly, not glossed over:** an AI judge grading AI-generated answers carries correlated-error risk — it can share the generator's knowledge gaps, especially on exactly the failure modes this metric exists to catch (superseded rules, wrong jurisdiction, authority misweighting). This makes the metric weaker evidence of real-world legal correctness than genuine independent expert review would provide, and that gap should be disclosed anywhere this metric is reported, not presented as equivalent to human-validated correctness.
- **Optional, zero-cost calibration:** if Renee notices the AI judge get something wrong during ordinary use, logging that correction is free signal worth capturing — but it's opportunistic, not a scheduled reviewing task, and isn't required for the metric to function.

### 9.3 Acceptance thresholds by build phase (consolidated)

| Phase | Metric | Threshold |
|---|---|---|
| B | RAGAS faithfulness (CI gate) | ≥0.85 |
| C | Case-law Recall@20 delta over decomposition-only | ≥5 points |
| C | Citation-edge extraction precision / recall (N=200 edges) | ≥90% / ≥85% |
| D | Temporal-filtering accuracy (held-out retroactive/amended set) | ≥90% |
| E | Authority-metadata accuracy (N=150 chunks) | ≥95% |
| E | Recall@20 regression from authority-aware rerank | ≤2 points |
| F | Citation entailment F1 (NLI vs. LLM-judge audit) | ≥0.90 |
| F | Citation completeness | ≥0.85 |
| F | Substantive correctness | tracked, not gated, until N≥100 AI-judge-graded examples exist (§9.2) |
| G | Cross-tenant leakage failures | 0 |
| G | Injection corpus pass rate (prompt path + render path) | 100% |
| H | p95 latency — synthesis path / refusal path | ≤35s / ≤2s (first-pass) |
| H | Error rate (rolling 5-min window) | <1% |

All thresholds above are first-pass engineering targets set before any real measurement exists, per the Implementation Status note — they exist to be recalibrated against Phase A–H's actual data, not treated as final commitments.

---

## 10. Risks, Limitations, and Open Questions

- **Design vs. implementation gap.** This document specifies a target architecture; none of it is evidence of correctness until a scoped vertical slice is built and measured (§7, §9). §9.3 now attaches numeric acceptance thresholds to that promise; they are first-pass targets to be recalibrated, not commitments.
- **Citation extraction accuracy.** Mis-extracted graph edges would pollute graph-expanded retrieval; validated against a 200-edge hand-labeled sample with explicit precision/recall targets before graph results are trusted in reranking (§3.2, §9.3, Phase C gate).
- **Authority metadata accuracy.** Authority tagging depends on source metadata (CourtListener court/jurisdiction fields, IRS publication status) that may be incomplete or inconsistent; validated against a 150-chunk hand-labeled sample at a ≥95% accuracy target (§3.2, §9.3); gaps are logged and surfaced as "authority unknown," never silently defaulted to a safe level.
- **As-of resolution ambiguity.** Not every question cleanly implies a single tax year (e.g., a multi-year amended-return sequence). The decomposer's as-of extraction needs explicit fallback behavior — surfacing the assumed year to the user rather than silently picking one.
- **NLI model domain fit.** A general-purpose NLI checkpoint may not transfer cleanly to dense statutory/legal language; the periodic LLM-as-judge audit (ADR-4) is meant to catch this, and is now tied to a concrete F1 ≥0.90 target (§9.3) rather than an open-ended "should be validated."
- **Entailment ≠ correctness.** Even with claim verification passing, an answer can still be substantively wrong (§5.4). The correctness metric in §9 is now graded by an LLM judge rather than a human expert (§9.2, revised from the original human-labeling protocol) and is deliberately tracked, not gated, until enough gradings exist. This trades away the original plan's expert-validation strength: an AI judge shares correlated-error risk with the generator on exactly the failure modes this metric exists to catch, so the metric should be reported with that caveat attached, not treated as equivalent to human-validated correctness.
- **Graph store availability.** A second stateful datastore beyond the vector store; the fail-open behavior (vector-only case-law retrieval if Neo4j is unavailable) needs to be tested, not just designed, and is now paired with an alert (§3.4) so degraded-but-working states are visible to the operator, not just silently absorbed.
- **Gate interactions — resolved.** A sub-answer that passes sufficiency but later fails claim verification is suppressed entirely (ADR-15), not shown with a caveat. The residual risk is coverage, not safety: this suppresses more sub-answers than a flagging or threshold-based approach would, so real usage should track how often "insufficient evidence" outcomes fire in practice — if too high, evidence-sufficiency thresholds (step 6) may need retuning rather than loosening the suppression rule itself.
- **Cost/provider risk.** The <$50/mo ceiling is now fixed (§4.1), but the specific provider/model is not (ADR-11); a provider switch after Phase A could still invalidate downstream per-query cost assumptions, and the ceiling itself may prove too tight for a frontier-tier model at real usage volume, forcing a self-hosted fallback with its own operational cost.
- **Upload threat handling.** A file-type allowlist and an explicit OCR/parsing-failure policy are now specified (§3.2), closing the previously unaddressed threat model for the client-upload path; the exact size limit remains `[DECISION NEEDED]`.
- **Single-engineer operational bus factor.** Five self-hosted stateful/near-stateful services (Qdrant, Neo4j, Postgres, Redis, Langfuse) run solo on free-tier infra. ADR-12's backup/restore drill mitigates data loss but not availability during the operator's own downtime — worth naming explicitly rather than assuming free-tier hosting implies free-tier operational risk too.
- **Render-boundary residual risk.** ADR-13's sanitized-rendering contract and the extended injection corpus (§9.1, Phase G) close the specific forged-citation-chip attack identified in review, but sanitization correctness is necessary, not sufficient, against novel encoding tricks — the render-path corpus should be re-run adversarially on a recurring cadence, not just once at Phase G.

---

## 11. Data Sourcing Reference

This section replaces the informal source list previously scattered across §3.1/§3.2 with the specific access method, cost, and current constraints for each data source, based on a source-availability review conducted in September 2026.

### 11.1 Statute — 26 U.S.C. (Internal Revenue Code)

**Correction:** the original ingestion list implied eCFR covered both statute and regulation text. eCFR is a CFR-only source (regulations); it does not carry the U.S. Code itself. TaxCite's authority model (§5.5) explicitly treats statute and regulation as separate authority tiers, so this needed its own source — one that was missing entirely from the original design.

| Source | Access | Cost | Notes |
|---|---|---|---|
| GovInfo API (USCODE collection) | REST API, free `api.data.gov` key | Free | Official GPO source; returns metadata + HTML/PDF/XML per package/granule, not clean per-citation JSON — requires a parser |
| uscode.house.gov (Office of Law Revision Counsel) | Bulk XML download | Free | The authoritative source Congress itself publishes from |
| Cornell Legal Information Institute (LII) | Bulk XML / scrape | Free | Common practical mirror, more consistently structured than the raw government XML |

**Decision (Phase A, 2026-09-18): uscode.house.gov is the content source; GovInfo is used only for change detection.**

| | uscode.house.gov (OLRC) | GovInfo (GPO) |
|---|---|---|
| Relationship to source | The origin: OLRC edits and publishes the Code | A repackaged mirror of OLRC's output |
| Format | USLM XML (canonical), plus XHTML/PCC/PDF | Same USLM XML inside package/granule metadata |
| Point-in-time versioning | Release points tied to specific enacted Public Laws, with a Prior Release Points archive | Annual editions only (e.g. `USCODE-2023-title26`) |
| Access | Static download (whole title as a zip) | REST API with an `api.data.gov` key, 1,000 req/hr |
| Change detection | None; the Currency page must be polled | "Packages modified since date" endpoint |

*Rationale:* TaxCite needs one title (26 U.S.C.) re-indexed weekly, not live per-citation lookups, so GovInfo's granule-level query API adds little. Three things decided it. uscode.house.gov keeps ingestion one hop from the source of truth. Its release points line up with enacted-law changes, which fits the bi-temporal model (ADR-2) better than annual snapshots. And it removes a rate-limited API dependency; §11.7 is the reason that matters.
*Mechanism:* once a week, query GovInfo's modified-since-date endpoint filtered to `USCODE` (far below 1,000/hr). Fetch fresh Title 26 USLM XML from uscode.house.gov only when Title 26 is flagged as changed. Each release point's Public Law identifier is recorded as the version's `source_revision`. Statute ingestion is built in Phase B.

### 11.2 Regulations — 26 CFR (Treasury Regulations)

| Source | Access | Cost | Notes |
|---|---|---|---|
| eCFR.gov API | REST API, **no key required** | Free | No change from the original design — no key, daily updates, and it already tracks point-in-time section history, which maps directly onto the bi-temporal model in ADR-2. This remains the strongest single data source in the whole pipeline. |

### 11.3 IRS Guidance — Revenue Rulings, Revenue Procedures, Notices, Announcements (Internal Revenue Bulletin)

No structured API exists. The IRS publishes the weekly Bulletin as HTML at predictable URLs (`irs.gov/irb/YYYY-WW_IRB`) and individual guidance documents as their own pages/PDFs.

**Access method: scraped**, not pulled from an API — the one ingestion source in this pipeline that genuinely requires it, rather than a documented API going unused. These are U.S. government works (no copyright barrier), but there's still no structured feed. A rate-limited scraper respecting `robots.txt`, with a clear identifying user-agent, is the standard approach; Juriscraper (§11.8) is a reasonable base to extend for this rather than writing a bespoke scraper.

### 11.4 IRS Publications

Plain PDFs at `irs.gov/pub`. Same situation as §11.3 — no API, scrape/download directly.

### 11.5 U.S. Tax Court Opinions

| Source | Access | Cost | Notes |
|---|---|---|---|
| CourtListener REST API v4 | REST API | Free tier: **125 req/day, 50/hr, 5/min** (tightened May 2026 — see §11.7) | Aggregates Tax Court opinions with everything else; at this rate, bulk-loading years of history through the live API is impractically slow |
| CourtListener bulk data files | Quarterly CSV dump | Free | **Use this for initial bulk ingestion** — sidesteps the daily rate limit; use the REST API only for weekly incremental pulls afterward |
| ustaxcourt.gov / DAWSON | Web UI only, no public API | Free (.gov) | The official source of record. No bulk endpoint; scraping this directly is the fallback if CourtListener coverage or rate limits become a blocker |

### 11.6 Circuit Court / Other Federal Opinions

| Source | Access | Cost | Notes |
|---|---|---|---|
| CourtListener | Same as §11.5 | Same tightened limits | Primary source — roughly 9M decisions across 2,000+ courts |
| GovInfo USCOURTS collection | REST API, free `api.data.gov` key | Free | Official U.S. Courts opinions, 130+ courts back to 2004 — a genuinely free supplement that reduces dependence on CourtListener's tightened limits |
| Harvard Caselaw Access Project (CAP) | Static bulk download only (its live search API was sunset in 2024) | Free, CC0-licensed | Useful for **historical backfill** — digitization runs through roughly 2018, so it won't carry recent opinions, but it's an unrestricted bulk source for older precedent |

**Not recommended:** Justia and Google Scholar both host case law but restrict automated scraping in their terms of service. Given the sources above are cleaner and explicitly open, there's no reason to take on that risk.

### 11.7 CourtListener Rate-Limit Change — Architecture Impact

As of May 2026, CourtListener's free-tier REST API access dropped from 5,000 requests/hour to 125/day, 50/hour, 5/minute (EDU memberships remain free with higher limits, if that ever applies to this project). This postdates the original ADR-1/ADR-6 design and changes the practical ingestion strategy:

- **Initial bulk load (Phase B/C):** use CourtListener's quarterly bulk CSV files, not the REST API — the free-tier daily cap makes an API-driven full historical load impractical.
- **Weekly incremental reindex (§7, ongoing):** the REST API's free tier is adequate for this — a week's worth of new opinions is a small fraction of the daily cap.
- **Supplement, don't solely rely on CourtListener:** GovInfo's USCOURTS collection (§11.6) is a free, rate-limit-independent backup for Circuit Court opinions specifically, and is worth ingesting alongside CourtListener rather than as a pure fallback, since it reduces exposure to any future CourtListener policy change.

### 11.8 Citation-Extraction and Scraping Tooling

Two open-source Free Law Project libraries directly implement mechanisms §3.2 previously described only in the abstract ("pattern-based citation parsing"):

- **eyecite** (`pip install eyecite`, BSD license) — extracts and resolves case citations, `id.`/`supra` references, and statutory citations from raw text; the same library CourtListener itself uses internally. Replaces a from-scratch citation parser for the `CITES`/`DISTINGUISHES`/`OVERRULES`/`AMENDS` extraction step in §3.2.
- **Juriscraper** (open source, Free Law Project) — the scraper framework CourtListener runs to pull opinions directly from court and agency websites. A reasonable base for the IRS Bulletin/Publications scraper in §11.3, and for scraping DAWSON directly if that becomes necessary (§11.5).
