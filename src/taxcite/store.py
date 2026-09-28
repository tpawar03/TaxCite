"""Postgres storage for chunks.

One table, created on demand. Writes are idempotent: re-ingesting the same
source updates rows in place and removes rows that no longer exist upstream.
"""

import os
from datetime import datetime, timezone

import psycopg
from psycopg.types.json import Jsonb

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
    # The citation graph is two tables, not a graph store (ADR-23): nothing traverses it, it is looked up.
    """
    CREATE TABLE IF NOT EXISTS citations (
        citing text NOT NULL,
        cited  text NOT NULL,
        PRIMARY KEY (citing, cited)
    )
    """,
    "CREATE INDEX IF NOT EXISTS citations_cited_idx ON citations (cited)",
    # One row per opinion, source and appeal. recorded_at is when we first learned it; checked_at is the
    # last look, kept separately because treatments go stale (a pending appeal is decided next month).
    """
    CREATE TABLE IF NOT EXISTS treatments (
        citation    text NOT NULL,
        kind        text NOT NULL,
        by_citation text NOT NULL DEFAULT '',
        source      text NOT NULL,
        recorded_at timestamptz NOT NULL DEFAULT now(),
        checked_at  timestamptz NOT NULL,
        PRIMARY KEY (citation, source, by_citation)
    )
    """,
    # Transaction time (ADR-2, D6): chunks holds what TaxCite holds now; every version it stopped
    # holding -- a paragraph upstream dropped, or text an amendment rewrote -- is kept here, from
    # when it was recorded to when it was retired. A trigger does it, so no reader of chunks changes.
    """
    CREATE TABLE IF NOT EXISTS chunk_versions (
        key         text NOT NULL,
        source      text NOT NULL,
        citation    text NOT NULL,
        text        text NOT NULL,
        recorded_at timestamptz,
        retired_at  timestamptz NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS chunk_versions_citation_idx ON chunk_versions (citation)",
)

# A rewrite is retired when its replacement was recorded; a dropped row, when the sweep ran.
RETIRE = (
    """
    CREATE OR REPLACE FUNCTION retire_chunk() RETURNS trigger AS $$
    BEGIN
        IF TG_OP = 'DELETE' OR OLD.text IS DISTINCT FROM NEW.text THEN
            INSERT INTO chunk_versions (key, source, citation, text, recorded_at, retired_at)
            VALUES (OLD.key, OLD.source, OLD.citation, OLD.text, OLD.recorded_at,
                    CASE WHEN TG_OP = 'UPDATE' THEN NEW.recorded_at ELSE now() END);
        END IF;
        RETURN COALESCE(NEW, OLD);
    END $$ LANGUAGE plpgsql
    """,
    "CREATE OR REPLACE TRIGGER chunks_retire BEFORE UPDATE OR DELETE ON chunks "
    "FOR EACH ROW EXECUTE FUNCTION retire_chunk()",
)

# Which text did TaxCite hold for a citation at a moment? The audit question ADR-2 asks, not a retrieval mode.
HELD_AT = """
    SELECT key, text FROM chunks WHERE citation = %(citation)s AND recorded_at <= %(at)s
    UNION ALL
    SELECT key, text FROM chunk_versions
    WHERE citation = %(citation)s AND recorded_at <= %(at)s AND retired_at > %(at)s
    ORDER BY key
"""

UPSERT = """
    INSERT INTO chunks (key, source, citation, part, section, heading, text, tokens, cita, as_of, fetched_at,
                        excluded, source_revision, effective, recorded_at)
    VALUES (%(key)s, %(source)s, %(citation)s, %(part)s, %(section)s, %(heading)s, %(text)s, %(tokens)s,
            %(cita)s, %(as_of)s, %(fetched_at)s, %(excluded)s, %(source_revision)s, %(effective)s, %(fetched_at)s)
    ON CONFLICT (key) DO UPDATE SET
        heading = EXCLUDED.heading, text = EXCLUDED.text, tokens = EXCLUDED.tokens,
        cita = EXCLUDED.cita, as_of = EXCLUDED.as_of, fetched_at = EXCLUDED.fetched_at,
        excluded = EXCLUDED.excluded, source_revision = EXCLUDED.source_revision, effective = EXCLUDED.effective,
        recorded_at = CASE WHEN chunks.text IS DISTINCT FROM EXCLUDED.text
                           THEN EXCLUDED.recorded_at ELSE chunks.recorded_at END
"""


def connect(url: str | None = None) -> psycopg.Connection:
    return psycopg.connect(url or DATABASE_URL)


def create_table(conn: psycopg.Connection) -> None:
    for statement in SCHEMA:
        conn.execute(statement)
    # Added in Phase B, so Phase A's table needs the column. Checked first because
    # ALTER takes an exclusive lock even with IF NOT EXISTS, and would queue behind
    # any long-running reader (an ingest embedding for an hour).
    for column, kind in (("source_revision", "text"), ("effective", "jsonb"), ("recorded_at", "timestamptz")):
        has_column = conn.execute(
            "SELECT 1 FROM information_schema.columns WHERE table_name = 'chunks' AND column_name = %s", (column,)
        ).fetchone()
        if not has_column:
            conn.execute(f"ALTER TABLE chunks ADD COLUMN {column} {kind}")
            if column == "recorded_at":  # D6: rows from before transaction time; the last fetch is the best record
                conn.execute("UPDATE chunks SET recorded_at = fetched_at")
    for statement in RETIRE:
        conn.execute(statement)


def save(conn: psycopg.Connection, chunks: list[Chunk], fetched_at: datetime | None = None) -> int:
    """Upsert chunks, then drop rows of the same sections that are no longer produced.

    The sweep matters because law changes: without it, a paragraph that upstream
    deleted or renumbered would linger and keep being retrieved.
    """
    if not chunks:
        return 0
    stamp = fetched_at or datetime.now(timezone.utc)
    rows = [{**vars(c), "key": c.key, "fetched_at": stamp, "effective": c.effective and Jsonb(c.effective)}
            for c in chunks]
    with conn.cursor() as cur:
        cur.executemany(UPSERT, rows)
        cur.execute(
            "DELETE FROM chunks WHERE source = %s AND section = ANY(%s) AND key <> ALL(%s)",
            (chunks[0].source, list({c.section for c in chunks}), [c.key for c in chunks]),
        )
    conn.commit()
    return len(rows)


def held_at(conn: psycopg.Connection, citation: str, at: datetime) -> list[tuple[str, str]]:
    """(key, text) TaxCite held for `citation` at `at`, current or since retired (D6)."""
    return conn.execute(HELD_AT, {"citation": citation, "at": at}).fetchall()


def count(conn: psycopg.Connection, source: str | None = None, indexable_only: bool = False) -> int:
    # the cast is required: Postgres cannot infer a bare parameter's type in "IS NULL"
    sql = "SELECT count(*) FROM chunks WHERE (%(source)s::text IS NULL OR source = %(source)s)"
    if indexable_only:
        sql += " AND excluded IS NULL"
    return conn.execute(sql, {"source": source}).fetchone()[0]