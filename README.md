# TaxCite

A citation-grounded RAG system for compound US federal tax questions: questions that span a statutory rule, a case-law exception and a client's own facts, answered as one synthesized answer where **every claim carries a citation that has been verified against its source**.

> **Status: Phase A, in progress.** The design is complete (PRD + technical documentation, 18 ADRs); implementation is at the ingestion stage. Nothing here claims to be a working system yet — see [STATUS.md](STATUS.md) for exactly where it stands.

## What makes it different from "vector search plus an LLM"

| Mechanism | What it does |
|---|---|
| Query decomposition | Splits a compound question into statutory, case-law and client-fact sub-queries |
| Hybrid retrieval | Qdrant dense + sparse vectors; exact terms like `§280A` must match literally ([ADR-6](taxcite-technical-documentation.md), [ADR-17](taxcite-technical-documentation.md)) |
| Citation-graph expansion | Bounded 1–2 hop traversal of the case-law citation graph |
| Bi-temporal validity | Every chunk carries valid time *and* transaction time, so a 2023 question gets 2023's rules |
| Authority-aware reranking | Statute, regulation, binding opinion and non-precedential guidance are weighted, not treated alike |
| Evidence-sufficiency gate | Refuses to answer a sub-question when the retrieved evidence is too thin, *before* generating |
| Post-generation claim verification | A self-hosted NLI model checks each claim against its cited source; any sub-answer with an unverified claim is suppressed in full |

The eval harness is a deliverable in its own right: an ablation ladder measuring what each mechanism contributes, rather than one aggregate score.

## Repository map

| Path | What's in it |
|---|---|
| [`taxcite-prd.md`](taxcite-prd.md) | Product requirements: users, goals, non-goals, requirements |
| [`taxcite-technical-documentation.md`](taxcite-technical-documentation.md) | Architecture, tech stack, build phases, ADR-1..18, eval methodology, data sourcing |
| [`STATUS.md`](STATUS.md) | Current state, decisions log, findings |
| [`docs/engineering-log.md`](docs/engineering-log.md) | Observations and trade-offs, with the measurements behind them |
| [`docs/intent/taxcite.md`](docs/intent/taxcite.md) | Confirmed intent: what "done" means |
| [`tasks/`](tasks/) | Phase A plan and task list |
| [`src/taxcite/`](src/taxcite/) | Implementation |
| [`tests/`](tests/) | Tests, with fixtures cut from real 26 CFR sections |
| [`graphify-out/`](graphify-out/) | Knowledge graph of the docs (`graph.html` is interactive) |

## Running it

Requires Python 3.12+, [uv](https://docs.astral.sh/uv/) and Docker.

```bash
docker compose up -d --wait    # Qdrant, Postgres, Redis
uv sync
uv run pytest -q
uv run uvicorn taxcite.api:app # http://localhost:8000/health
```

Postgres is published on host port 5433 and Redis on 6380, to avoid clashing with local installs. Copy `.env.example` to `.env` to override.

## Data sources

All federal, all free: [eCFR](https://www.ecfr.gov/developers/documentation/api/v1) for regulations, [uscode.house.gov](https://uscode.house.gov/download/download.shtml) for statute (with GovInfo used only for change detection), [CourtListener](https://www.courtlistener.com/help/api/) bulk data for case law, and IRS.gov for publications and guidance.

## Notes

Renee, the enrolled agent in the PRD, is a persona used to keep the design honest about real constraints, not a real customer. The system handles no real client data.
