# Graph Report - TaxCite.nosync  (2026-09-18)

## Corpus Check
- Corpus is ~13,795 words - fits in a single context window. You may not need a graph.

## Summary
- 73 nodes · 113 edges · 10 communities (7 shown, 3 thin omitted)
- Extraction: 96% EXTRACTED · 3% INFERRED · 1% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.78)
- Token cost: 91,687 input · 0 output

## Community Hubs (Navigation)
- Query Pipeline & Observability
- Ingestion & Data Sources
- Product Scope & Open Decisions
- Tenancy, Cost & Operations
- Claim Verification & Eval
- Injection & Rendering Safety
- Retrieval Scope Decisions
- Project Package
- FastAPI

## God Nodes (most connected - your core abstractions)
1. `Functional Requirements FR-1..FR-17` - 12 edges
2. `Ingestion Pipeline` - 12 edges
3. `TaxCite PRD` - 10 edges
4. `Query Path (9-step pipeline)` - 10 edges
5. `TaxCite Technical Design Documentation` - 8 edges
6. `Post-Generation NLI Claim Verification` - 7 edges
7. `TaxCite citation-grounded RAG system` - 6 edges
8. `Evidence-Sufficiency Gate` - 6 edges
9. `SSE Progress Stream over Durable Job Record` - 6 edges
10. `Cost Model & <$50/mo Budget Ceiling` - 6 edges

## Surprising Connections (you probably didn't know these)
- `README (empty)` --conceptually_related_to--> `TaxCite citation-grounded RAG system`  [AMBIGUOUS]
  README.md → taxcite-technical-documentation.md
- `TaxCite PRD` --references--> `Eval Harness & Ablation Ladder`  [EXTRACTED]
  taxcite-prd.md → taxcite-technical-documentation.md
- `Renee (Enrolled Agent persona)` --conceptually_related_to--> `TaxCite citation-grounded RAG system`  [EXTRACTED]
  taxcite-prd.md → taxcite-technical-documentation.md
- `Functional Requirements FR-1..FR-17` --references--> `Post-Generation NLI Claim Verification`  [EXTRACTED]
  taxcite-prd.md → taxcite-technical-documentation.md
- `Functional Requirements FR-1..FR-17` --references--> `Evidence-Sufficiency Gate`  [EXTRACTED]
  taxcite-prd.md → taxcite-technical-documentation.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **TaxCite query pipeline stages** — taxcite_technical_documentation_query_decomposition, taxcite_technical_documentation_hybrid_retrieval, taxcite_technical_documentation_citation_graph_traversal, taxcite_technical_documentation_authority_aware_reranking, taxcite_technical_documentation_evidence_sufficiency_gate, taxcite_technical_documentation_synthesis, taxcite_technical_documentation_claim_verification, taxcite_technical_documentation_sse_delivery [EXTRACTED 1.00]
- **Untrusted client-document defense layers** — taxcite_technical_documentation_prompt_injection_defense, taxcite_technical_documentation_sanitized_rendering, taxcite_technical_documentation_pii_redaction, taxcite_technical_documentation_tenant_isolation [INFERRED 0.85]
- **Self-hosted stateful stores operated by one engineer** — taxcite_technical_documentation_qdrant, taxcite_technical_documentation_neo4j, taxcite_technical_documentation_postgres, taxcite_technical_documentation_redis, taxcite_technical_documentation_langfuse [EXTRACTED 1.00]

## Communities (10 total, 3 thin omitted)

### Community 0 - "Query Pipeline & Observability"
Cohesion: 0.23
Nodes (13): Functional Requirements FR-1..FR-17, ADR-16: Live delivery decoupled from tracing, ADR-8: Authority-aware reranking, Authority-Aware Cross-Encoder Reranking, Bounded 1-2 Hop Citation-Graph Traversal, Graph-Store Fail-Open / Case-Law Fail-Closed Resilience, Langfuse, Neo4j (+5 more)

### Community 1 - "Ingestion & Data Sources"
Cohesion: 0.19
Nodes (13): ADR-2: Bi-temporal fact validity, Bi-Temporal Fact Validity (valid time + transaction time), Harvard Caselaw Access Project, CourtListener, CourtListener Rate-Limit Change (May 2026), eCFR API, eyecite, GovInfo API (+5 more)

### Community 2 - "Product Scope & Open Decisions"
Cohesion: 0.27
Nodes (11): README (empty), TaxCite PRD, Open Questions (embedding, LLM provider, frontend, backup storage, market scope), Renee (Enrolled Agent persona), ADR-11: LLM provider/model tiering pending, TaxCite Technical Design Documentation, Embedding Model Choice (pending, Phase A), k6 (+3 more)

### Community 3 - "Tenancy, Cost & Operations"
Cohesion: 0.20
Nodes (11): Goals G1-G6 (research time, seat displacement, groundedness, gates, cost, leakage), Non-Functional Requirements (latency, reliability, cost, security), ADR-10: Batch sufficiency gate per sub-query, ADR-12: Backup & DR for stateful stores, ADR-5: Shared corpus + per-tenant namespace, Backup & Disaster Recovery, Cost Model & <$50/mo Budget Ceiling, Postgres (+3 more)

### Community 4 - "Claim Verification & Eval"
Cohesion: 0.24
Nodes (10): ADR-15: Zero-tolerance claim suppression, ADR-3: Post-generation claim verification, ADR-4: Self-hosted NLI, not LLM-as-judge, in production, ADR-7: Sufficiency gate before synthesis, Post-Generation NLI Claim Verification, Eval Harness & Ablation Ladder, Evidence-Sufficiency Gate, 100-Question Golden Set (+2 more)

### Community 5 - "Injection & Rendering Safety"
Cohesion: 0.40
Nodes (6): ADR-13: Render-boundary sanitized rendering, ADR-14: Model-boundary prompt-injection defense, GitHub Actions, Playwright, Model-Boundary Prompt-Injection Defense, Sanitized Rendering Contract

### Community 6 - "Retrieval Scope Decisions"
Cohesion: 0.40
Nodes (5): Non-Goals (no full GraphRAG, no BM25 engine, no token streaming, federal only), ADR-1: Decomposition + bounded citation-graph traversal, ADR-6: Qdrant hybrid, not Meilisearch, ADR-9: SSE over durable job record, Meilisearch (replaced)

## Ambiguous Edges - Review These
- `README (empty)` → `TaxCite citation-grounded RAG system`  [AMBIGUOUS]
  README.md · relation: conceptually_related_to

## Knowledge Gaps
- **12 isolated node(s):** `taxcite-nosync`, `README (empty)`, `100-Question Golden Set`, `FastAPI`, `RAGAS` (+7 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 22 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `README (empty)` and `TaxCite citation-grounded RAG system`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Functional Requirements FR-1..FR-17` connect `Query Pipeline & Observability` to `Ingestion & Data Sources`, `Product Scope & Open Decisions`, `Tenancy, Cost & Operations`, `Claim Verification & Eval`, `Injection & Rendering Safety`?**
  _High betweenness centrality (0.294) - this node is a cross-community bridge._
- **Why does `Ingestion Pipeline` connect `Ingestion & Data Sources` to `Query Pipeline & Observability`, `Product Scope & Open Decisions`, `Tenancy, Cost & Operations`?**
  _High betweenness centrality (0.204) - this node is a cross-community bridge._
- **Why does `TaxCite PRD` connect `Product Scope & Open Decisions` to `Query Pipeline & Observability`, `Tenancy, Cost & Operations`, `Claim Verification & Eval`, `Retrieval Scope Decisions`?**
  _High betweenness centrality (0.200) - this node is a cross-community bridge._
- **What connects `taxcite-nosync`, `README (empty)`, `100-Question Golden Set` to the rest of the system?**
  _12 weakly-connected nodes found - possible documentation gaps or missing edges._