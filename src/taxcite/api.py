import asyncio
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import psycopg
import redis
from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from qdrant_client import QdrantClient

from taxcite import jobs, store, tracing

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://taxcite:taxcite@localhost:5433/taxcite")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6380/0")


@asynccontextmanager
async def lifespan(app):
    # G1b: tracing is on when the Langfuse keys are set. At startup, not import: tests build their TestClient
    # without `with`, so the lifespan never runs and no test sends a span to Langfuse.
    tracing.setup()
    yield


app = FastAPI(title="TaxCite", lifespan=lifespan)


def _check(probe) -> str:
    try:
        probe()
        return "ok"
    except Exception as e:
        return f"error: {type(e).__name__}"


@app.get("/health")
def health(response: Response) -> dict[str, str]:
    status = {
        "qdrant": _check(lambda: QdrantClient(url=QDRANT_URL, timeout=2).get_collections()),
        "postgres": _check(lambda: psycopg.connect(DATABASE_URL, connect_timeout=2).close()),
        "redis": _check(lambda: redis.Redis.from_url(REDIS_URL, socket_timeout=2).ping()),
    }
    if any(v != "ok" for v in status.values()):
        response.status_code = 503
    return status


def tenant(authorization: str | None = Header(None)) -> str:
    """Every route but /health belongs to a tenant, resolved from its API key (Phase G)."""
    scheme, _, key = (authorization or "").partition(" ")
    if scheme.lower() == "bearer" and key:
        with store.connect() as conn:
            if found := store.tenant_for(conn, key.strip()):
                return found
    raise HTTPException(status_code=401, detail="missing or unknown API key",
                        headers={"WWW-Authenticate": "Bearer"})


class Query(BaseModel):
    question: str
    k: int = 8


POLL_SECONDS = 0.5   # fallback cadence when Redis is unavailable
IDLE_TIMEOUT = 0.5   # how long to wait on Redis before re-checking the record
# Daily quotas, reset at midnight UTC. First guesses (plan G): the global cap keeps a busy day inside the
# <$50/mo budget at ~$0.0073 an answer with room for retries and eval traffic.
QUERIES_PER_DAY = 50
ALL_QUERIES_PER_DAY = 200


def _over_quota(conn, who: str) -> None:
    if jobs.count_today(conn, who) >= QUERIES_PER_DAY or jobs.count_today(conn) >= ALL_QUERIES_PER_DAY:
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).date()
        raise HTTPException(status_code=429, detail=f"daily question limit reached; resets {tomorrow} 00:00 UTC")


@app.post("/queries", status_code=202)
def post_query(query: Query, background: BackgroundTasks, who: str = Depends(tenant)) -> dict:
    """Accept a question and return immediately (ADR-9).

    The pipeline runs 20-30s, longer than free-tier proxies keep a connection open,
    so the client gets an id and watches /queries/{id}/events instead.
    """
    with store.connect() as conn:
        jobs.create_table(conn)
        _over_quota(conn, who)
        job_id = jobs.create(conn, query.question, who)
    background.add_task(_run_job, job_id, query.question, query.k, who)
    return {"id": job_id, "events": f"/queries/{job_id}/events"}


def _run_job(job_id: str, question: str, k: int, tenant: str) -> None:
    with store.connect() as conn:
        jobs.run(conn, job_id, question, k=k, tenant=tenant)


@app.get("/queries/{job_id}")
def get_query(job_id: str, who: str = Depends(tenant)) -> dict:
    with store.connect() as conn:
        job = jobs.get(conn, job_id, who)
    if job is None:
        raise HTTPException(status_code=404, detail="no such job")
    return job


@app.get("/queries/{job_id}/events")
def stream_events(job_id: str, who: str = Depends(tenant)) -> StreamingResponse:
    """Server-sent events for one job.

    Replays whatever the record already holds, then follows along. Because the record
    is written before the notification, a client that connects late or reconnects sees
    every stage exactly once, and a finished job replays its terminal event instead of
    hanging.
    """
    with store.connect() as conn:
        job = jobs.get(conn, job_id, who)
    if job is None:
        raise HTTPException(status_code=404, detail="no such job")

    async def events():
        # Replay what the record already holds, so a late or reconnecting client
        # misses nothing; then follow live events from Redis (ADR-16).
        seen = 0
        with store.connect() as conn:
            current = jobs.get(conn, job_id, who)
        for event in jobs.replay(current)[seen:]:
            yield event.sse()
        seen = len(current["stages"])
        if jobs.is_terminal(current):
            return

        pubsub = None
        try:
            import redis.asyncio as aioredis

            rdb = aioredis.from_url(jobs.REDIS_URL)
            pubsub = rdb.pubsub()
            await pubsub.subscribe(jobs.CHANNEL.format(id=job_id))
        except Exception:
            pubsub = None  # Redis down: fall back to the record (ADR-16's failure domain)

        try:
            while True:
                if pubsub is not None:
                    message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=IDLE_TIMEOUT)
                    if message:
                        payload = json.loads(message["data"])
                        if payload.get("seq", 0) <= seen:
                            continue  # already sent from the record; see jobs.publish
                        yield jobs.Event(event=payload["event"], data=payload["data"]).sse()
                        seen = payload.get("seq", seen + 1)
                        if payload["event"] in jobs.TERMINAL:
                            return
                        continue
                else:
                    await asyncio.sleep(POLL_SECONDS)

                # Redis was quiet (or absent): the record decides whether we are done.
                with store.connect() as conn:
                    current = jobs.get(conn, job_id, who)
                for event in jobs.replay(current)[seen:]:
                    yield event.sse()
                seen = len(current["stages"])
                if jobs.is_terminal(current):
                    return
        finally:
            if pubsub is not None:
                await pubsub.aclose()

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
