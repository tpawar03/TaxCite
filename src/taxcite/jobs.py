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


def create(conn, question: str) -> str:
    job_id = str(uuid.uuid4())
    conn.execute("INSERT INTO jobs (id, question, status) VALUES (%s, %s, 'queued')", (job_id, question))
    conn.commit()
    return job_id


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


def get(conn, job_id: str) -> dict | None:
    row = conn.execute(
        "SELECT id, question, status, stages, created_at FROM jobs WHERE id = %s", (job_id,)
    ).fetchone()
    if not row:
        return None
    return {"id": str(row[0]), "question": row[1], "status": row[2], "stages": row[3], "created_at": row[4]}


def run(conn, job_id: str, question: str, k: int = 8) -> None:
    """The pipeline, reporting each stage. Phases C-F add their steps here."""
    from taxcite import decompose as dc
    from taxcite.generate import OPINION_RE, answer_from_groups, authorities
    from taxcite.ingest.citations import flags

    try:
        rdb = client()
    except redis.RedisError:
        rdb = None  # the pipeline continues without live events
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
        dc.retrieve(plan, k=k, editions=dc.EDITIONS, statute=dc.STATUTE)
        hits = dc.chunks(plan, k)
        publish(conn, job_id, "synthesizing", {"chunks": len(hits)}, rdb)
        result = answer_from_groups(question, plan.groups({h.citation for h in hits}), facts=plan.facts,
                                    as_of=plan.as_of)
        # Is each cited opinion still good law (C4)? Looked up after synthesis and attached beside the
        # answer, never folded into its text; a failed lookup reads "unknown" and the answer still ships.
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
            "model": result.model,
            "cost_usd": round(result.cost_usd + plan.cost_usd, 6),
        }, rdb)
    except Exception as e:  # the job record must show what happened, not just stop
        publish(conn, job_id, "error", {"type": type(e).__name__, "message": str(e)[:300]}, rdb)


def replay(job: dict) -> list[Event]:
    return [Event(event=s["event"], data=s["data"]) for s in job["stages"]]


def is_terminal(job: dict) -> bool:
    return job["status"] in ("done", "error")
