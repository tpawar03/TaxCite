"""G3 step 4: do a client's facts get from an uploaded document into the answer?

Each row of eval/dev-documents.jsonl is a reviewed dev row with its client facts moved out of the question and into a
synthetic document. Per row: a fresh tenant uploads the document as a one-page text PDF, the shipped pipeline answers
the question (jobs.run, as the API runs it), and the tenant is deleted. Reported, tracked not gated:

- retrieved: a chunk of the document reached synthesis
- cited: a shown sentence cites the document
- used: the answer states the row's `fact`, a figure only the document's numbers produce
- gold cited: the answer cites one of the row's public gold citations

Paid (~$0.008 a row). Saves after every row and resumes: a re-run skips rows already answered and retries the
rows that errored; the last result per row counts.
"""

import json
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from taxcite import index, jobs, store
from taxcite.ingest import client_docs

sys.path.insert(0, "tests")
from test_documents import pdf  # noqa: E402 (the same text-PDF writer the tests use)

ROWS = Path("eval/dev-documents.jsonl")
OUT = Path(f"eval/results/g3-documents-{date.today()}.jsonl")


def run(row: dict, conn) -> dict:
    key = store.create_tenant(conn, f"eval-g3-{row['id']}")
    conn.commit()
    who = store.tenant_for(conn, key)
    try:
        client_docs.ingest(conn, index.client(), who, row["client_doc_name"], pdf(row["client_doc"]))
        jobs.create_table(conn)
        job_id = jobs.create(conn, client_docs.redact(row["question"]), who)
        jobs.run(conn, job_id, client_docs.redact(row["question"]), tenant=who)
        stages = {s["event"]: s["data"] for s in jobs.get(conn, job_id, who)["stages"]}
    finally:
        conn.rollback()
        conn.execute("DELETE FROM tenants WHERE id = %s", (who,))  # its document and chunks cascade
        conn.commit()
        client_docs.sweep(conn, index.client())
    answer = stages.get("answer") or {}
    cites = answer.get("citations", []) + answer.get("derived_citations", [])
    gold = {c for group in row["gold"] for c in group}
    return {"id": row["id"], "source_row": row["source_row"], "error": stages.get("error"),
            "retrieved": stages.get("synthesizing", {}).get("documents", 0) > 0,
            "cited": any(c.startswith(row["client_doc_name"]) for c in cites),
            "used": row["fact"] in answer.get("text", ""),
            "gold_cited": bool(gold & set(cites)),
            "refused": answer.get("refused"), "hidden_sentences": answer.get("hidden_sentences"),
            "cost_usd": answer.get("cost_usd"), "trace_id": answer.get("trace_id"),
            "text": answer.get("text"), "citations": cites, "reference": row["answer"]}


def main() -> None:
    load_dotenv(".env")  # the repo's, from the working directory
    previous = [json.loads(line) for line in OUT.read_text().splitlines()] if OUT.exists() else []
    done = {r["id"] for r in previous if not r["error"]}
    rows = [json.loads(line) for line in ROWS.read_text().splitlines()]
    with store.connect() as conn:
        for row in rows:
            if row["id"] in done:
                continue
            result = run(row, conn)
            with OUT.open("a") as f:
                f.write(json.dumps(result) + "\n")
            print(row["id"], {k: result[k] for k in ("retrieved", "cited", "used", "gold_cited", "refused", "cost_usd")})
    results = list({r["id"]: r for r in map(json.loads, OUT.read_text().splitlines())}.values())
    print({k: f"{sum(bool(r[k]) for r in results)}/{len(results)}" for k in ("retrieved", "cited", "used", "gold_cited")},
          f"${sum(r['cost_usd'] or 0 for r in results):.4f}")


if __name__ == "__main__":
    main()
