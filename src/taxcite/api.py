import asyncio
import json
import os

import psycopg
import redis
from fastapi import BackgroundTasks, FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from qdrant_client import QdrantClient

from taxcite import jobs, store

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://taxcite:taxcite@localhost:5433/taxcite")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6380/0")

app = FastAPI(title="TaxCite")


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


class Query(BaseModel):
    question: str
    k: int = 8


POLL_SECONDS = 0.5   # fallback cadence when Redis is unavailable
IDLE_TIMEOUT = 0.5   # how long to wait on Redis before re-checking the record


@app.post("/queries", status_code=202)
def post_query(query: Query, background: BackgroundTasks) -> dict:
    """Accept a question and return immediately (ADR-9).

    The pipeline runs 20-30s, longer than free-tier proxies keep a connection open,
    so the client gets an id and watches /queries/{id}/events instead.
    """
    with store.connect() as conn:
        jobs.create_table(conn)
        job_id = jobs.create(conn, query.question)
    background.add_task(_run_job, job_id, query.question, query.k)
    return {"id": job_id, "events": f"/queries/{job_id}/events"}


def _run_job(job_id: str, question: str, k: int) -> None:
    with store.connect() as conn:
        jobs.run(conn, job_id, question, k=k)


@app.get("/queries/{job_id}")
def get_query(job_id: str) -> dict:
    with store.connect() as conn:
        job = jobs.get(conn, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="no such job")
    return job


@app.get("/queries/{job_id}/events")
def stream_events(job_id: str) -> StreamingResponse:
    """Server-sent events for one job.

    Replays whatever the record already holds, then follows along. Because the record
    is written before the notification, a client that connects late or reconnects sees
    every stage exactly once, and a finished job replays its terminal event instead of
    hanging.
    """
    with store.connect() as conn:
        job = jobs.get(conn, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="no such job")

    async def events():
        # Replay what the record already holds, so a late or reconnecting client
        # misses nothing; then follow live events from Redis (ADR-16).
        seen = 0
        with store.connect() as conn:
            current = jobs.get(conn, job_id)
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
                    current = jobs.get(conn, job_id)
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
