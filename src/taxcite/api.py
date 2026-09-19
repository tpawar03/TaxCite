import os

import psycopg
import redis
from fastapi import FastAPI, Response
from qdrant_client import QdrantClient

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
