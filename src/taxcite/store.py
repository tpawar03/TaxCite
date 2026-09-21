"""Postgres storage for chunks.

One table, created on demand. Writes are idempotent: re-ingesting the same
source updates rows in place and removes rows that no longer exist upstream.
"""

import os
from datetime import datetime, timezone

import psycopg

from taxcite.chunk import Chunk

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://taxcite:taxcite@localhost:5433/taxcite")

SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS chunks (
        key        text PRIMARY KEY,
        source     text NOT NULL,
        citation   text NOT NULL,
        part       int  NOT NULL,
        section    text NOT NULL,
        heading    text NOT NULL,
        text       text NOT NULL,
        tokens     int  NOT NULL,
        cita       text,
        as_of      date NOT NULL,
        fetched_at timestamptz NOT NULL,
        excluded   text
    )
    """,
    "CREATE INDEX IF NOT EXISTS chunks_section_idx ON chunks (section)",
    "CREATE INDEX IF NOT EXISTS chunks_source_idx ON chunks (source)",
)

UPSERT = """
    INSERT INTO chunks (key, source, citation, part, section, heading, text, tokens, cita, as_of, fetched_at, excluded)
    VALUES (%(key)s, %(source)s, %(citation)s, %(part)s, %(section)s, %(heading)s, %(text)s, %(tokens)s,
            %(cita)s, %(as_of)s, %(fetched_at)s, %(excluded)s)
    ON CONFLICT (key) DO UPDATE SET
        heading = EXCLUDED.heading, text = EXCLUDED.text, tokens = EXCLUDED.tokens,
        cita = EXCLUDED.cita, as_of = EXCLUDED.as_of, fetched_at = EXCLUDED.fetched_at,
        excluded = EXCLUDED.excluded
"""


def connect(url: str | None = None) -> psycopg.Connection:
    return psycopg.connect(url or DATABASE_URL)


def create_table(conn: psycopg.Connection) -> None:
    for statement in SCHEMA:
        conn.execute(statement)


def save(conn: psycopg.Connection, chunks: list[Chunk], fetched_at: datetime | None = None) -> int:
    """Upsert chunks, then drop rows of the same sections that are no longer produced.

    The sweep matters because law changes: without it, a paragraph that upstream
    deleted or renumbered would linger and keep being retrieved.
    """
    if not chunks:
        return 0
    stamp = fetched_at or datetime.now(timezone.utc)
    rows = [{**vars(c), "key": c.key, "fetched_at": stamp} for c in chunks]
    with conn.cursor() as cur:
        cur.executemany(UPSERT, rows)
        cur.execute(
            "DELETE FROM chunks WHERE source = %s AND section = ANY(%s) AND key <> ALL(%s)",
            (chunks[0].source, list({c.section for c in chunks}), [c.key for c in chunks]),
        )
    conn.commit()
    return len(rows)


def count(conn: psycopg.Connection, source: str | None = None, indexable_only: bool = False) -> int:
    # the cast is required: Postgres cannot infer a bare parameter's type in "IS NULL"
    sql = "SELECT count(*) FROM chunks WHERE (%(source)s::text IS NULL OR source = %(source)s)"
    if indexable_only:
        sql += " AND excluded IS NULL"
    return conn.execute(sql, {"source": source}).fetchone()[0]