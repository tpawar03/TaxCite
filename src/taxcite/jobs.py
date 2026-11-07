"""Durable job records for the query pipeline (ADR-9).

A query takes 20-30s across several calls, so `POST /queries` returns an id at once
and the work runs in the background. Two things carry progress, deliberately:

* **Postgres is the record.** Every stage is appended to the job row, so a client
  that connects late, reconnects, or misses events entirely can reconstruct the
  whole run. A dropped connection never loses a query that cost real money.
* **Redis pub/sub is the notification** (ADR-16). It makes events arrive promptly;
  it is not the source of truth, so a Redis outage degrades liveness, not results.

The answer itself is never streamed token by token: it is one terminal event, sent
only once synthesis (and later, claim verification) has finished.
"""

import json
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime

import redis

from taxcite import tracing

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6380/0")
CHANNEL = "job:{id}"
TERMINAL = ("answer", "error")

SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS jobs (
        id          uuid PRIMARY KEY,
        question    text NOT NULL,
        status      text NOT NULL,                       -- queued | running | done | error
        stages      jsonb NOT NULL DEFAULT '[]'::jsonb,  -- every event, in order
        created_at  timestamptz NOT NULL DEFAULT now(),
        updated_at  timestamptz NOT NULL DEFAULT now()
    )
    """,
    "CREATE INDEX IF NOT EXISTS jobs_created_idx ON jobs (created_at DESC)",
    # Phase G: every job belongs to a tenant. Rows from before have none and are visible to no one.
    "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS tenant uuid",
    "CREATE INDEX IF NOT EXISTS jobs_tenant_idx ON jobs (tenant, created_at DESC)",
)


@dataclass
class Event:
    event: str
    data: dict

    def sse(self) -> str:
        """One server-sent event. The blank line is the record separator."""
        return f"event: {self.event}\ndata: {json.dumps(self.data)}\n\n"


def client() -> redis.Redis:
    return redis.Redis.from_url(REDIS_URL)


def create_table(conn) -> None:
    for statement in SCHEMA:
        conn.execute(statement)
    conn.commit()


def create(conn, question: str, tenant: str) -> str:
    job_id = str(uuid.uuid4())
    conn.execute("INSERT INTO jobs (id, question, status, tenant) VALUES (%s, %s, 'queued', %s)",
                 (job_id, question, tenant))
    conn.commit()
    return job_id


def count_today(conn, tenant: str | None = None) -> int:
    """Jobs created since midnight UTC: one tenant's, or everyone's (the quotas)."""
    (n,) = conn.execute(
        "SELECT count(*) FROM jobs WHERE created_at >= date_trunc('day', now(), 'UTC') "
        "AND (%(t)s::uuid IS NULL OR tenant = %(t)s::uuid)", {"t": tenant}).fetchone()
    return n


def publish(conn, job_id: str, event: str, data: dict | None = None, rdb: redis.Redis | None = None) -> Event:
    """Append a stage to the record, then notify listeners. Record first: a listener
    that arrives between the two still sees the stage on replay."""
    payload = {"event": event, "data": data or {}, "at": datetime.now().isoformat(timespec="seconds")}
    status = {"answer": "done", "error": "error"}.get(event, "running")
    # The returned length is the stage's sequence number. A listener reads both the
    # record and the live channel, so without it the same stage can be delivered
    # twice when a commit and its notification race.
    (seq,) = conn.execute(
        "UPDATE jobs SET stages = stages || %s::jsonb, status = %s, updated_at = now() "
        "WHERE id = %s RETURNING jsonb_array_length(stages)",
        (json.dumps([payload]), status, job_id),
    ).fetchone()
    conn.commit()
    notify(job_id, payload | {"seq": seq}, rdb)
    return Event(event=event, data=payload["data"])


def notify(job_id: str, payload: dict, rdb: redis.Redis | None = None) -> bool:
    """Best-effort live notification. Redis is the delivery channel, never the record,
    so an outage must cost promptness and nothing else (ADR-16): the stage is already
    committed, and a listener falls back to reading the record."""
    try:
        (rdb or client()).publish(CHANNEL.format(id=job_id), json.dumps(payload))
        return True
    except redis.RedisError:
        return False


def get(conn, job_id: str, tenant: str) -> dict | None:
    """The job, if it exists and is this tenant's. Another tenant's job is None, exactly like a missing one."""
    try:
        uuid.UUID(job_id)
    except ValueError:
        return None
    row = conn.execute(
        "SELECT id, question, status, stages, created_at FROM jobs WHERE id = %s AND tenant = %s", (job_id, tenant)
    ).fetchone()
    if not row:
        return None
    return {"id": str(row[0]), "question": row[1], "status": row[2], "stages": row[3], "created_at": row[4]}


@tracing.traced("query")
def run(conn, job_id: str, question: str, k: int = 8, tenant: str | None = None) -> None:
    """The pipeline, reporting each stage. Phases C-F add their steps here. One run is one trace (G1b)."""
    from taxcite import decompose as dc
    from taxcite.generate import (DOCUMENT_ASKED, NO_DOCUMENT, OPINION_RE, answer_from_groups, authorities,
                                  cited_items, skipped_only)
    from taxcite.ingest.citations import flags

    try:
        rdb = client()
    except redis.RedisError:
        rdb = None  # the pipeline continues without live events
    tracing.annotate({"job.id": job_id, "langfuse.user.id": tenant})
    try:
        publish(conn, job_id, "decomposing", {}, rdb)
        plan = dc.decompose(question)
        # The as-of year is recorded on the job. dc.EDITIONS would limit publications to the
        # editions near it; D3 built that and left it off live until D7 (see decompose.EDITIONS).
        publish(conn, job_id, "retrieving", {
            "k": k,
            "as_of": plan.as_of,
            "subqueries": [{"kind": s.kind, "query": s.query} for s in plan.subqueries],
            "fallback": plan.fallback,
        }, rdb)
        documents = dc.client_hits(plan, tenant) if tenant else []  # G3
        # Checkpoint 2: the plan wants only client facts, the question names an upload, and none is on file. The
        # fallback's public search would answer a question nobody asked (B got substantiation case law).
        only_documents = (plan.fallback == "no searchable sub-query" and not documents
                          and bool(DOCUMENT_ASKED.search(question)))
        hits, groups, skipped, verdicts = [], [], [("The client's uploaded documents", NO_DOCUMENT)], []
        if not only_documents:
            dc.retrieve(plan, k=k, editions=dc.EDITIONS, statute=dc.STATUTE, siblings=dc.SIBLINGS, planned=dc.PLANNED)
            hits = dc.chunks(plan, k)
            groups, skipped = plan.groups({h.citation for h in hits}), []
        if dc.GATE and not only_documents:  # F2: a part its sources can't answer is never written
            groups, skipped, verdicts = dc.gate(question, groups, plan.as_of)
            publish(conn, job_id, "checking_sufficiency", {
                "parts": [{k: v[k] for k in ("part", "sufficient", "missing")} for v in verdicts]}, rdb)
        written = not (skipped and not any(h for _, h in groups))
        if not written:
            result = skipped_only(skipped)  # nothing answerable: no synthesis, nothing to verify
        else:
            publish(conn, job_id, "synthesizing", {"chunks": len(hits), "documents": len(documents)}, rdb)
            result = answer_from_groups(question, groups, facts=plan.facts, as_of=plan.as_of, skipped=skipped,
                                        documents=documents)
        if dc.VERIFY and written:  # F4: nothing is sent until every sentence is checked (ADR-9: the answer stays buffered)
            from taxcite import verify
            publish(conn, job_id, "verifying", {"sentences": len(cited_items(result.structured["data"]))
                                                if result.structured else 0}, rdb)
            result = verify.checked(question, result)
        # Is each cited opinion still good law (C4)? Looked up after synthesis and attached beside the
        # answer, never folded into its text; a failed lookup reads "unknown" and the answer still ships.
        tracing.annotate({"chunks": len(hits), "hidden_sentences": len(result.hidden), "refused": result.refused,
                          "langfuse.observation.output": result.text})  # the trace's output in Langfuse
        opinions = list(dict.fromkeys(m.group() for c in result.citations + result.derived_citations
                                      if (m := OPINION_RE.search(c))))
        publish(conn, job_id, "answer", {
            "treatments": flags(conn, opinions) if opinions else {},
            "text": result.text,
            "citations": result.citations,
            "derived_citations": result.derived_citations,
            "unsupported_citations": result.unsupported_citations,
            # E5: every citation's authority, from E2's stored profile through a fixed label map (ADR-13)
            "authorities": authorities(result),
            "refused": result.refused,
            "hidden_sentences": len(result.hidden),  # F4: failed verification (or went with a failed part)
            "model": result.model,
            "cost_usd": round(result.cost_usd + plan.cost_usd + sum(v["usd"] for v in verdicts), 6),
            "trace_id": tracing.trace_id(),  # None when tracing is off
        }, rdb)
    except Exception as e:  # the job record must show what happened, not just stop
        tracing.annotate({"langfuse.observation.level": "ERROR", "error.type": type(e).__name__})
        publish(conn, job_id, "error", {"type": type(e).__name__, "message": str(e)[:300],
                                        "trace_id": tracing.trace_id()}, rdb)


def replay(job: dict) -> list[Event]:
    return [Event(event=s["event"], data=s["data"]) for s in job["stages"]]


def is_terminal(job: dict) -> bool:
    return job["status"] in ("done", "error")
