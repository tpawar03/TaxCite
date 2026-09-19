# Implementation Plan: TaxCite Phase A — Core Retrieval Baseline

## Overview

Phase A (tech doc §7) builds single-hop hybrid retrieval over **eCFR Title 26 + IRS Publications**, for one tenant, with no decomposition. It is measured against a ~20-question pilot set and compared with a closed-book baseline. Phase A also has to **settle three architecture decisions**: the dense embedding model (§3.2), the LLM provider/model tiering (ADR-11), and the SSE-over-durable-job transport (ADR-9, decided but not yet built).

The exit condition is evidence plus a runnable path. A reviewer can `POST /queries` a regulations or IRS-publication question, watch the SSE stage events, and get a cited answer. The pilot-set numbers for closed-book, dense-only and hybrid runs, the embedding benchmark, and the LLM benchmark are all written down.

Source docs: `taxcite-technical-documentation.md` §3, §4, §7, §9, §11, ADR-6/9/11/16 · `docs/intent/taxcite.md`.

## Architecture Decisions (for this phase)

- **Stores used in Phase A: Qdrant, Postgres, Redis.** Neo4j arrives in Phase C with the citation graph and Langfuse with tracing. Both stay in the architecture; they just aren't needed until they have work to do. For ADR-11 benchmarking, cost comes from token counts in the provider responses.
- **Local dev uses one `docker compose`** (Qdrant, Postgres 16, Redis). Supabase and hosting are deployment choices for later phases; the code only sees a `DATABASE_URL`.
- **Hybrid retrieval uses Qdrant's native dense + sparse vectors with its built-in fusion** (ADR-6). Sparse vectors come from `fastembed` (BM25-style), so there's no second engine.
- **Chunking follows §3.2.** Regulations get section-level chunks of 200–500 tokens with no overlap and keep their parent-section metadata. IRS publications use the §3.2 fallback: ~300-token sliding windows with 15% overlap.
- **Package layout:** `src/taxcite/`, with plain modules and no framework layers. Each stage is one function. Where a model is swappable (embedding, LLM), the choice is one config value, not an interface hierarchy.
- **The pilot set is data, not code:** `eval/pilot.jsonl` holds question, gold section citations and a reference answer. The eval scripts are small and live next to it.
- **Transport (ADR-9 + ADR-16):** `POST /queries` inserts a `jobs` row in Postgres and returns the id. A background worker runs the pipeline and publishes stage events to Redis pub/sub. `GET /queries/{id}/events` streams SSE. On reconnect it replays the terminal state from the job row. The answer is sent once, as the terminal event, never streamed token by token.

## Dependency Graph

```
docker compose (Qdrant, Postgres, Redis) + package skeleton
        │
        ├── eCFR T26 ingest ──► hybrid search CLI ──► pilot set + retrieval eval
        │                              │                        │
        │                              ├── IRS pubs ingest ─────┤
        │                              │                        ▼
        │                              │            embedding benchmark (decision)
        │                              ▼                        │
        │                     answer generation + closed-book baseline
        │                              │
        │                              ▼
        │                     ADR-11 LLM benchmark (decision)
        │                              │
        └──────────────────────────────┴──► ADR-9 job + SSE transport ──► Phase A exit report
```

## Task List

Full task details are in `tasks/todo.md`.

### Slice 1 — Retrieval works end to end (regulations)
- [x] T1: Local stack and package skeleton
- [ ] T2: Ingest eCFR Title 26 into Postgres + Qdrant
- [ ] T3: Hybrid search CLI with citations

### Checkpoint 1
- [ ] `taxcite search "…"` returns relevant 26 CFR sections for 3 hand-picked questions

### Slice 2 — Measure retrieval, add publications, pick the embedding model
- [ ] T4: Pilot set (20 questions) and retrieval eval script
- [ ] T5: Ingest IRS Publications
- [ ] T6: Embedding-model benchmark (≥2 candidates) and the decision recorded
- [ ] T6b: ADR-17 revisit trigger — Qdrant vs. pgvector (hybrid recall, filtered-recall loss, latency, size)

### Checkpoint 2 (human review: embedding decision)
- [ ] Recall@10/nDCG@10 recorded for dense-only vs. hybrid across each candidate; model locked
- [ ] ADR-17 confirmed or reopened from the T6b Qdrant-vs-pgvector numbers

### Slice 3 — Answers, baseline, pick the LLM
- [ ] T7: Cited answer generation and closed-book baseline
- [ ] T8: ADR-11 LLM benchmark (quality per dollar) and the decision recorded

### Checkpoint 3 (human review: ADR-11 decision)
- [ ] Pilot scores for closed-book vs. RAG per candidate model; projected monthly cost under $50

### Slice 4 — Delivery
- [ ] T9: ADR-9 job record + SSE transport
- [ ] T10: Phase A exit report

### Checkpoint: Phase A complete
- [ ] All Phase A acceptance items met; ready to plan Phase B

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| The pilot set needs tax-domain judgment to label gold sections | High | Claude drafts questions and gold citations from the ingested text, and the user reviews all 20 before any numbers count. The set stays at 20, per §7. |
| eCFR XML structure is messier than expected (nested paragraphs, tables) | Med | Get T2 working on one Part (§1.1-1 area) first, then scale up. Tables are kept as text in Phase A. |
| Local embedding on a Mac CPU is slow for a full Title 26 re-index per candidate model | Med | Benchmark on a fixed subset (the Parts the pilot questions touch, plus distractors), not the full title. Document the subset. |
| LLM API keys and spend for the benchmark | Med | Cap the benchmark at 20 questions × ≤3 models × 2 modes. The script prints the running cost and stops at a configurable limit. |
| IRS PDF extraction quality (multi-column, tables) | Med | Use `pypdf` text extraction. Pages that come out empty or garbled are marked `extraction_failed` and excluded (§3.2 rule), never silently indexed. |
| No public statute (26 U.S.C.) in Phase A skews compound questions | Low | By design (§7): the pilot set is limited to regulation and publication questions. Statute is ingested in Phase B. |

## Resolved Inputs (2026-09-18)

- **Embedding:** `BAAI/bge-small-en-v1.5` is the primary candidate. §3.2 requires ≥2 candidates, so T6 benchmarks it against one challenger (default `nomic-embed-text-v1.5`, long-context).
- **LLM providers for ADR-11:** Anthropic and OpenAI (keys available). T8 benchmarks the budget tier of each (Claude Haiku 4.5, plus OpenAI's current small model). A pricier model is considered for synthesis only if it fits under $50/mo. The judge model is always from the other provider (§9.2).
- **Statute source (§11.1):** decided. uscode.house.gov release-point XML is the content source, and GovInfo modified-since is used only for weekly change detection. Built in Phase B.
- **Pilot set:** Claude drafts, the user reviews every row (defaulted).
