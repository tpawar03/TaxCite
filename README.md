# TaxCite

A citation-grounded RAG system for compound US federal tax questions: questions that span a statutory rule, a case-law exception and a client's own facts, answered as one synthesized answer where **every claim cites a retrieved source and is checked against it before it is shown**.

> **Status: Phases A–F complete** (merged to `main`, 2026-10-01). Retrieval, case-law treatment flags, tax-year awareness, authority-aware ranking and claim verification are built and measured. Each phase has an exit report in [`eval/results/`](eval/results/); [STATUS.md](STATUS.md) has the full decision log.

## Results

| | Measured | Set |
|---|---|---|
| Retrieval, Recall@20 | **47% → 63%** (plain hybrid → decomposition, cross-encoder and authority-aware reranking) | golden, 98 questions, 5 plan sets |
| Material sentences that cite a source | **44% → 100%** (free-text → structured JSON output) | dev, same 126 answers |
| Fully grounded answers, authority-conflict questions | **64% → 88%** (Phase E → F; retrieval and answer handling also changed) | golden, 32 questions |
| Grounded answers, verifier off → on | **79% → 90%**, correctness unchanged | golden, paired |
| Verifier entailment F1 ("not supported" class) | **0.63** (precision 0.90, recall 0.48) vs a Claude Sonnet 5.5 reference; gate was 0.90, **not met** | golden, 298 pairs |
| CI gates | retrieval Recall@10 **0.760** (floor 0.70); faithfulness **0.951 ± 0.015** (floor 0.855, refusals ≤ 25%) | dev / golden |

Negative results are reported as prominently as positive ones: citation-graph expansion lowered case-law recall and ships off (Phase C), the temporal gate was not met (Phase D), the authority-conflict criterion was not met (Phase E), and five self-hosted NLI verifiers reached only F1 0.22–0.46 (Phase F).

## How it works

| Mechanism | What it does |
|---|---|
| Query decomposition | Splits a compound question into statutory, case-law and client-fact sub-queries, each routed to its sources |
| Hybrid retrieval | Qdrant dense (`bge-base-en-v1.5`) + BM25 sparse, RRF fusion; exact terms like `§280A` must match literally |
| Reranking | Cross-encoder, then an authority prior within each kind of source (statute and regulation over opinion over publication) |
| Neighbouring sections | One extra search inside each of the top statute/regulation sections, so the right subsection reaches the writer |
| Case-law treatment | A citation graph in two Postgres tables flags cited opinions that were later reversed, vacated or appealed |
| Tax-year awareness | Statute effective dates from the code's own notes; dated questions get the year's rule |
| Structured synthesis | One JSON item per sentence, citations chosen from the retrieved sources only, so none can be invented |
| Claim verification | One batched Claude Haiku 4.5 call per answer checks each sentence against its cited source; a failed sentence is hidden |

The eval harness is a deliverable in its own right: an ablation ladder per phase, hand-audited golden and dev sets, κ-checked LLM judges, and CI gates calibrated against deliberately broken builds.

## Limitations

- No deployed demo; it runs locally.
- The dev set was tuned on. Golden was scored once per phase, but golden-set analyses informed what got built, so it is a test set, not a strictly held-out one.
- The verifier misses about half of unsupported sentences (recall 0.48); it caught 77 of 102 seeded wrong citations.
- Correctness on all answerable golden questions is 0.37; compound (0.25) and temporal (0.12) questions are the weakest.

## Repository map

| Path | What's in it |
|---|---|
| [`taxcite-prd.md`](taxcite-prd.md) | Product requirements: users, goals, non-goals, requirements |
| [`taxcite-technical-documentation.md`](taxcite-technical-documentation.md) | Architecture, tech stack, build phases, ADR-1..23, eval methodology, data sourcing |
| [`STATUS.md`](STATUS.md) | Current state, decisions log, findings |
| [`eval/results/`](eval/results/) | Phase A–F exit reports and every measurement behind them |
| [`docs/engineering-log.md`](docs/engineering-log.md) | Observations and trade-offs, one entry per finding |
| [`tasks/`](tasks/) | Plan and task list |
| [`src/taxcite/`](src/taxcite/) | Implementation |
| [`tests/`](tests/) | 297 tests, with fixtures cut from real sources |
| [`graphify-out/`](graphify-out/) | Knowledge graph of the code and docs (`graph.html` is interactive) |

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

All federal, all free: [eCFR](https://www.ecfr.gov/developers/documentation/api/v1) for regulations, [uscode.house.gov](https://uscode.house.gov/download/download.shtml) for statute (with GovInfo used only for change detection), Tax Court opinions via DAWSON with [CourtListener](https://www.courtlistener.com/help/api/) for appeal history, and IRS.gov for publications.

## Notes

Renee, the enrolled agent in the PRD, is a persona used to keep the design honest about real constraints, not a real customer. The system handles no real client data.
