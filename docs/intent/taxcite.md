# TaxCite — Confirmed Intent

Confirmed 2026-09-18 via interview. Upstream of the PRD and technical doc (v5), which stay authoritative for *how*.

- **Outcome:** TaxCite built to the technical doc (v5) as specified: the full query path, all five stores (Qdrant, Neo4j, Postgres, Redis, Langfuse), ADR-1..16, and phases A–H with their acceptance gates.
- **User:** Interviewers and engineering reviewers. Renee is the made-up persona that gives the design its realistic constraints, not a real customer.
- **Why now:** A production-grade portfolio piece for upcoming interviews.
- **Success:**
  1. A live URL where a reviewer can ask a compound tax question and get a cited answer that has passed the sufficiency gate and claim verification.
  2. A published eval dashboard showing the ablation ladder, meaning what each mechanism adds, measured against the closed-book and simpler-RAG baselines, with every phase gate met (e.g. RAGAS faithfulness ≥0.85, citation F1 ≥0.90).
- **Constraint:** 3–4 months, and the running cost of the live system under $50/mo. The architecture stays as specified; simplification happens inside components (fewest abstractions, standard library first), never by dropping a store or an ADR.
- **Out of scope:** Real customers or real client data (tenant isolation is proven by the leakage test, not by real use), state tax law, pricing and go-to-market, live token-by-token streaming of answers, and freshness faster than weekly.

Open design choices, to decide in the phase where each comes up: LLM provider/model tiering (ADR-11), embedding model (Phase A), frontend stack, hosting, backup storage.
