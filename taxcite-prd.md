# TaxCite — Product Requirements Document

**Status:** Design-stage. Architecture, eval methodology, and phase gates are fully specified; implementation has not yet begun (see §11, Milestones).
**Source of technical detail:** `taxcite-technical-documentation.md` (v5). This PRD summarizes and scopes that document for a mixed engineering/product/review audience; where the two disagree, the technical documentation is authoritative.

---

## 1. Overview

TaxCite is a citation-grounded Retrieval-Augmented Generation (RAG) system that answers compound tax questions by combining federal statute and regulation text, U.S. Tax Court/Circuit Court precedent, IRS publications, and a practice's own client documents into a single synthesized, cited answer. It exists because small tax and accounting practices currently either burn 25–40 minutes per nontrivial question manually cross-referencing separate PDFs, or pay for a mid-market legal research seat that's priced and built for larger firms and never touches their client files. TaxCite targets that gap: fast, cited, personalized answers, with explicit handling of legal authority, time-sensitivity, and evidentiary sufficiency rather than a generic semantic-search-plus-LLM wrapper.

---

## 2. Problem Statement

**Who:** Renee, an Enrolled Agent running a 3-person tax prep and advisory practice serving roughly 400 individual and small-business clients. [OPEN QUESTION: the source documentation names Renee as the sole persona and doesn't define a broader target market or customer segment — is TaxCite scoped as a single-practice tool, a portfolio/interview artifact, or an early design for a wider small-practice product?]

**What gap:** Renee routinely needs answers that combine a general statutory rule, an exception or clarification from case law, and a specific client's own facts — e.g., whether a client's home-office deduction under the simplified method conflicts with vehicle mileage they also claimed. Keyword search across separate statute/regulation/publication PDFs doesn't synthesize that interaction. Her two current options are manual cross-referencing (25–40 minutes per question) or a paid research seat (CCH AnswerConnect/Checkpoint-class, ~$100–250/mo) that is not built for a 3-person firm's workflow and has no access to her client files.

**Why now / why RAG:** A general LLM without retrieval hallucinates section numbers and expiration dates — a documented failure mode in existing legal-research AI tools. Grounding generation in retrieved, authority-ranked, time-validated sources with post-generation verification is the only approach in scope that is simultaneously fast, cited, and personalized to client facts.

---

## 3. Goals

| # | Goal | Metric / Target |
|---|---|---|
| G1 | Cut per-question research time | ~30 min → <5 min (field measurement; instrumentation not yet defined — see §12) |
| G2 | Displace paid research-seat usage | ≥80% reduction in Renee's use of the ~$100–250/mo paid seat |
| G3 | Publish a credible groundedness rate | Measured against TaxCite's own closed-book and simpler-RAG baselines on a held-out set; the external 17–33% Stanford hallucination-rate figure is used only as a non-comparable reference point, never a pass/fail bar |
| G4 | Pass all phase-gated offline quality thresholds before advancing | e.g., RAGAS faithfulness ≥0.85 (Phase B), citation entailment F1 ≥0.90 and completeness ≥0.85 (Phase F) — full table in §9 |
| G5 | Operate within a defined per-query cost ceiling | Confirmed at <$50/mo total (§8); narrows the LLM provider decision (ADR-11) to self-hosted or budget-tier options |
| G6 | Zero cross-tenant data leakage | 0 tolerated failures on the automated leakage test (hard gate, Phase G) |

---

## 4. Non-Goals

- **Full GraphRAG-style community detection** (e.g., Leiden clustering, global/local summarization). TaxCite uses only bounded 1–2 hop citation-graph traversal, deliberately scoped smaller than full GraphRAG.
- **A dedicated BM25 lexical engine** (Elasticsearch/OpenSearch). Qdrant's native sparse+dense hybrid retrieval is used instead; a separate lexical engine is out of scope unless a future need for literal BM25 scoring is demonstrated.
- **Real-time token streaming of the generated answer.** The synthesized answer is buffered until claim verification completes and delivered as a single terminal event; only stage-progress updates stream live. This is a deliberate safety decision, not a missing feature.
- **Full elimination of the paid research seat.** The goal is ≥80% displacement (G2), not full replacement.
- **Sub-weekly content freshness.** Ingestion runs on a weekly incremental reindex; near-real-time legal-update tracking is out of scope.
- **State tax law and state courts.** All ingestion sources (eCFR, CourtListener federal opinions, IRS.gov) are federal only.
- **Fully siloed per-tenant infrastructure.** Tenants share one statute/case-law corpus and citation graph; isolation is enforced at the query-filter layer, not via separate infrastructure per tenant.
- **Broader commercialization strategy.** Pricing, multi-firm rollout, and marketing are not addressed in the source documentation and are out of scope for this PRD.

---

## 5. Users & Use Cases

| User | Description |
|---|---|
| Primary — Renee | Enrolled Agent; owner/operator, 3-person tax prep and advisory practice; ~400 individual/small-business clients |
| Secondary — practice staff | [OPEN QUESTION: not specified in source documentation beyond Renee as the named persona — do other staff at the practice query the system or upload client documents independently?] |
| Eval/quality dashboard audience | [OPEN QUESTION: source documentation doesn't specify whether the published eval dashboard (§9) is aimed at Renee, at engineers/reviewers, or is a public portfolio artifact — this materially affects its design] |

**Core user stories:**

1. As Renee, I want to ask a compound question spanning statute, case law, and a specific client's facts, so I get one synthesized, cited answer instead of manually cross-referencing multiple sources.
2. As Renee, I want the system to explicitly decline to answer (or a portion of a question) when evidence is insufficient, rather than guess, so I'm not handed a confidently wrong answer.
3. As Renee, I want every citation labeled with its authority level (statute / regulation / binding opinion / nonprecedential guidance), so I know how much weight to give it.
4. As Renee, I want the system to apply the correct tax year's rules and tell me when it had to assume a year, so retroactive or amended rules aren't silently conflated with current law.
5. As Renee, I want assurance that my practice's client documents are isolated from any other tenant's data.
6. As a reviewer/interviewer, I want to see measured, ablated evidence of what each retrieval mechanism contributes, not just a final aggregate score.

---

## 6. System Architecture

**Ingestion (batch + event-driven):**
eCFR API, CourtListener bulk API, IRS.gov, and client uploads feed format-specific parsers (statute XML parser, OCR for scanned memos, table extraction for rate schedules). Parsed content fans out into four parallel processing paths — chunking + embedding, citation-graph edge extraction, bi-temporal tagging, and authority tagging — which converge into three stores: **Qdrant** (hybrid dense+sparse vector index, shared corpus + per-tenant namespace), **Neo4j** (citation graph), and **Postgres** (metadata, temporal validity, authority profiles, citations).

**Query path (compute is synchronous; delivery is streamed):**
1. Auth/tenant resolution
2. Query decomposition (LLM) into statutory / case-law / client-fact sub-queries, plus an extracted "as-of" tax year
3. Parallel hybrid retrieval per sub-query, filtered by the as-of date against each chunk's valid-time window
4. Citation-graph expansion for the case-law sub-query only (bounded 1–2 hops)
5. Authority-weighted cross-encoder reranking of the combined candidate set
6. Evidence-sufficiency gate — one batched, structured-output call per sub-query, run before synthesis
7. Synthesis — one cited answer over sub-answers that passed the gate; buffered, not token-streamed
8. Claim verification — self-hosted NLI model checks each atomic claim; any sub-answer with a failed claim is suppressed entirely, never shown with a caveat (ADR-15)
9. Terminal response — citations, authority annotations, trace ID, sanitized rendering; live progress events are delivered via Redis, decoupled from Langfuse tracing (ADR-16)

**Delivery:** the client opens an SSE connection immediately on query submission and receives one progress event per stage above, ending in a terminal answer / refusal / insufficient-evidence event, backed by a durable job record so a dropped connection doesn't lose the underlying job.

**Tech stack:**

| Component | Choice |
|---|---|
| Vector + lexical retrieval | Qdrant (self-hosted, native dense+sparse hybrid) |
| Graph store | Neo4j Community (self-hosted) |
| Metadata/relational | Postgres (Supabase free tier) |
| API | FastAPI |
| Cache/queue | Redis (self-hosted) |
| Tracing/observability | Langfuse (self-hosted), decoupled from live delivery — SSE events publish via Redis instead (ADR-16) |
| Logging | Grafana Loki + Promtail |
| Alerting | Grafana Alerting |
| Claim verification | Self-hosted NLI/entailment model (e.g., DeBERTa-v3-based) |
| Offline eval | RAGAS + LLM-as-judge |
| CI/CD | GitHub Actions |
| Hosting | Railway/Render free tier or a free VPS |
| Load testing | k6 |
| IaC | Terraform |
| Embedding model | [OPEN QUESTION — resolved empirically in Phase A] |
| LLM provider (decomposition/sufficiency/synthesis) | [OPEN QUESTION — see §12], now constrained by a confirmed <$50/mo ceiling |
| Frontend/rendering client | [OPEN QUESTION — see §12] |
| Backup object storage | [OPEN QUESTION — see §12] |

---

## 7. Functional Requirements

| ID | Requirement | Reference |
|---|---|---|
| FR-1 | The system must decompose a compound tax question into statutory, case-law, and client-fact sub-queries, plus an as-of tax year. | Query path step 2 |
| FR-2 | The system must retrieve each sub-query via hybrid (dense + sparse) search, filtered by the as-of date against each chunk's valid-time window. | Query path step 3 |
| FR-3 | For case-law sub-queries, the system must expand seed results via bounded 1–2 hop citation-graph traversal (CITES / DISTINGUISHES / OVERRULES / AMENDS). | Query path step 4; ADR-1 |
| FR-4 | The system must rerank the combined candidate set using a cross-encoder with authority metadata as an explicit boost/demote signal, not semantic score alone. | Query path step 5; ADR-8 |
| FR-5 | The system must run an evidence-sufficiency check per sub-query before synthesis, excluding sub-queries below threshold, implemented as one batched structured-output call per sub-query. | Query path step 6; ADR-7, ADR-10 |
| FR-6 | The system must generate one synthesized answer, with a citation attached to every claim, generated only over sub-answers that passed the sufficiency gate. | Query path step 7 |
| FR-7 | The system must run post-generation claim verification on every atomic claim; any sub-answer containing an unentailed or contradicted claim must be suppressed entirely and treated as insufficient evidence — no unverified claim is ever shown to the user, even flagged. | Query path step 8; ADR-3, ADR-4, ADR-15 |
| FR-8 | The system must surface the authority level of every citation shown to the user. | §5.5 |
| FR-9 | The system must surface the assumed/inferred tax year when it is not explicitly stated by the user. | §5.3, §10 |
| FR-10 | Every response must include a trace ID. | §3.4 |
| FR-11 | The system must enforce per-tenant isolation of client documents, verified by an automated test asserting the cross-tenant filter fires on every query, including graph-traversal queries. | ADR-5 |
| FR-12 | The system must stream per-stage progress via SSE and buffer the final answer until claim verification completes; the answer must never be token-streamed before verification. | ADR-9 |
| FR-13 | The system must fail open to vector-only case-law retrieval if Neo4j is unavailable, and fail closed to a statute-only answer with an explicit caveat if case-law retrieval fails outright. | §6 (Resilience) |
| FR-14 | All source-derived and model-generated text must be sanitized at render time; citation chips and authority badges must be populated only from structured ingestion fields, never from arbitrary source text. | ADR-13 |
| FR-15 | PII in client-document fields must be redacted before any trace span is emitted, not after. | §3.4 |
| FR-16 | Citation-extraction and authority-metadata gaps encountered during ingestion must be logged and surfaced, never silently defaulted. | §3.2 |
| FR-17 | Client-document uploads must be restricted to an allowlist of file types; unsupported types are rejected with a clear error. OCR/parsing failures must exclude the affected content from retrieval rather than silently indexing it. | §3.2 |

---

## 8. Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| Latency | p95 end-to-end, synthesis path | ≤35s (first-pass target, recalibrated against Phase H load-test data) |
| Latency | p95 end-to-end, refusal path | ≤2s |
| Reliability | Error rate | <1% over a rolling 5-minute window |
| Reliability | Cross-tenant data leakage | 0 tolerated failures (hard gate) |
| Reliability | Neo4j / Qdrant / Redis health-check failures | Alerted, not silently absorbed, even when the system degrades gracefully |
| Data freshness | Public corpus reindex | Weekly incremental |
| Data durability | Backup | Nightly Postgres/Neo4j dumps + Qdrant snapshots, 14-day retention, quarterly restore drill |
| Cost | Per-query LLM call count | ~5 calls worst case (1 decompose + 3 sufficiency + 1 synthesis), down from as many as `2 + top_k × 3` pre-optimization |
| Cost | Per-query budget | Confirmed ceiling: <$50/mo total; narrows the LLM provider decision to self-hosted or budget-tier options (ADR-11) |
| Security | Prompt-injection defense | Must pass 100% on the injection test corpus (prompt path) before deploy |
| Security | Render-boundary defense | Must pass 100% on the injection test corpus (render path, headless-browser CI check) before any real client document is ingested |
| Infrastructure | Self-hosted / free-tier | Full stack in §6, except LLM provider (not yet chosen) |
| Scalability | Tenancy model | Single-tenant through Phase F; multi-tenant with per-tenant namespace and shared corpus from Phase G |

---

## 9. Evaluation & Success Metrics

**Offline evaluation** is built around a 100-question golden set, stratified as:

| Category | Count |
|---|---|
| Statutory-only | 25 |
| Case-law-only | 20 |
| Compound (multi-hop) | 30 |
| Temporal edge case | 10 |
| Expected insufficiency | 10 |
| Adversarial / injection | 5 |

Quality is tracked via an **ablation ladder** — closed-book → dense-only → hybrid → +reranking → +decomposition → +graph expansion → +temporal filtering → +authority-aware reranking → +claim verification — so each mechanism's contribution is isolated, not just the final aggregate score. Metrics are reported separately (retrieval Recall@k/nDCG/MRR; citation entailment; citation completeness; substantive correctness; graph-extraction precision/recall; temporal accuracy; authority-weighting impact; abstention precision/recall; security test results; latency/cost/error rate), never collapsed into one number.

**Substantive correctness** — the hardest metric — is scored on a 40-question subset by an LLM-as-judge (not human reviewers — no manual-labeling budget), using the same 3-point rubric (Correct / Partially correct / Incorrect) plus a defect taxonomy. The judge model must differ from the generation model; reliability is established by running two independently-configured judges and measuring their agreement (Cohen's κ ≥0.7), the same bar originally set for human inter-rater reliability. This is a known trade-off, not a silent substitution: an AI judge can share the generator's blind spots on exactly the failure modes this metric exists to catch, so it's weaker evidence of correctness than human expert review would be — flagged explicitly in §10.

**Phase-gated acceptance thresholds:**

| Phase | Metric | Threshold |
|---|---|---|
| B | RAGAS faithfulness (CI gate) | ≥0.85 |
| C | Case-law Recall@20 delta over decomposition-only | ≥5 points |
| C | Citation-edge extraction precision / recall (N=200) | ≥90% / ≥85% |
| D | Temporal-filtering accuracy | ≥90% |
| E | Authority-metadata accuracy (N=150) | ≥95% |
| E | Recall@20 regression from authority rerank | ≤2 points |
| F | Citation entailment F1 | ≥0.90 |
| F | Citation completeness | ≥0.85 |
| F | Substantive correctness | Tracked, not gated, until ≥100 AI-judge-graded examples exist |
| G | Cross-tenant leakage failures | 0 |
| G | Injection corpus pass rate (prompt + render path) | 100% |
| H | p95 latency (synthesis / refusal) | ≤35s / ≤2s |
| H | Error rate | <1% |

All thresholds are first-pass engineering targets, to be recalibrated against real measured data, not final commitments.

**Business-level success** (G1–G2 in §3) requires field measurement of actual research time and seat-usage displacement. [OPEN QUESTION: no instrumentation plan for these business-level metrics exists in the source documentation — only the technical quality metrics above are defined.]

---

## 10. Guardrails & Risks

**Implemented guardrails:**
- Fail-closed evidence-sufficiency gating runs *before* synthesis, so ungrounded content is never generated and then retracted (ADR-7).
- Post-generation NLI claim verification suppresses any sub-answer containing a failed claim entirely, rather than showing it with a caveat (ADR-3, ADR-4, ADR-15).
- Per-tenant isolation enforced at the query-filter layer, with a compensating automated leakage test (ADR-5).
- Prompt-injection defenses cover both the prompt boundary (ADR-14) and the render boundary (ADR-13) — untrusted client-document content cannot manipulate the model or forge UI elements.
- PII redaction is enforced as a tested invariant (runs before span emission, not after), not an assumption.
- Fail-open/fail-closed behavior is explicit and tested: vector-only fallback if the graph store is down, statute-only-with-caveat if case-law retrieval fails outright.

**Known risks and limitations:**

| Risk | Mitigation |
|---|---|
| This is a design document, not yet evidence of a working system | Numeric acceptance gates (§9) exist specifically to produce that evidence |
| Citation-graph extraction errors could pollute retrieval | Validated against a 200-edge hand-labeled sample, gated at ≥90%/≥85% precision/recall before trusted (Phase C) |
| Authority-metadata errors could misweight ranking | Validated against a 150-chunk hand-labeled sample, gated at ≥95% accuracy (Phase E); gaps are logged, never silently defaulted |
| As-of (tax year) resolution can be ambiguous | Assumed year is always surfaced to the user, never silently picked |
| A general-purpose NLI model may not transfer cleanly to legal language | Periodic audit against LLM-as-judge, gated at F1 ≥0.90 |
| Entailment does not imply correctness — a claim can be supported yet legally wrong | Tracked as a separate metric (§9), now graded by an LLM judge rather than a human expert — weaker evidence of correctness than human review, disclosed explicitly rather than presented as equivalent |
| Neo4j is a second stateful dependency | Fail-open behavior, tested, plus an alert so degraded-but-working states are visible |
| Sufficiency and verification gates could disagree in edge cases | Resolved: a sub-answer failing verification after passing sufficiency is suppressed entirely (ADR-15). Residual risk is coverage (more "insufficient evidence" outcomes), not safety |
| LLM provider/model is still unresolved | Cost ceiling itself is now fixed at <$50/mo (§8); provider choice remains open and resolved empirically in Phase A (see §12) |
| Client-document uploads had no defined threat model | Addressed: file-type allowlist and OCR/parsing-failure policy now specified (FR-17); exact size limit remains open (see §12) |
| Single engineer operates five self-hosted stateful services | Backup/restore drill (quarterly) mitigates data loss; does not mitigate availability during operator downtime |
| Sanitized rendering closes the known forged-citation attack but not all novel encoding tricks | Render-path injection corpus should be re-run adversarially on a recurring cadence, not just once |

---

## 11. Milestones / Phasing

| Phase | Ships | Exit gate |
|---|---|---|
| A — Core retrieval baseline | Federal statute + IRS pubs, single-hop hybrid retrieval, single-tenant. Delivery transport (SSE) and LLM provider/embedding model decided here. | Closed-book baseline established; provider/embedding choices locked |
| B — Decomposition + eval infra | Case-law corpus, query decomposition, 100-question golden set, RAGAS in CI | Faithfulness ≥0.85 |
| C — Citation graph | Neo4j, citation extraction, bounded graph expansion | Recall@20 delta ≥5 pts AND edge precision/recall ≥90%/85% |
| D — Temporal validity | Bi-temporal metadata, as-of filtering, amendment versioning | Temporal accuracy ≥90% |
| E — Authority-aware retrieval | Authority metadata, authority-weighted reranking | Authority accuracy ≥95%; Recall@20 regression ≤2 pts |
| F — Sufficiency + verification | Batched sufficiency gate, self-hosted NLI verification with zero-tolerance suppression (ADR-15), LLM-judge correctness grading begins | Entailment F1 ≥0.90, completeness ≥0.85 |
| G — Multi-tenant + hardening | Per-tenant ingestion, auth/quotas, render-path injection defense | 0 leakage failures; 100% injection-corpus pass |
| H — Resilience + load | Circuit breakers, backup/DR, production alerting, k6 load test scoped to realistic single-practice query volume | p95 ≤35s/≤2s, error rate <1% |

---

## 12. Open Questions

1. **Embedding model** — not chosen; resolved empirically in Phase A against Recall@10/nDCG@10.
2. **LLM provider/model tiering** (decomposition, sufficiency gate, synthesis) — proposed but undecided (ADR-11); now constrained by the confirmed <$50/mo ceiling; resolved in Phase A.
3. **Frontend/rendering framework** — not specified anywhere in the source documentation.
4. **Backup object storage provider** — candidates named (Cloudflare R2, Backblaze B2) but not chosen.
5. **Alert destination** (Slack/PagerDuty/email) — Slack proposed as default, not confirmed.
6. **Maximum client-document upload size** — file-type policy is now defined (FR-17), but the specific size limit is not.
7. **Target market scope** — is TaxCite intended solely for Renee's practice, or as a template for a broader small-practice product? Not addressed in source documentation.
8. **Eval/quality dashboard audience** — Renee, engineering reviewers, or a public portfolio artifact? This affects the dashboard's design and isn't resolved.
9. **Business-metric instrumentation** — no plan exists for measuring the field-level outcomes in G1 (research time) and G2 (seat displacement); only technical quality metrics are instrumented.
