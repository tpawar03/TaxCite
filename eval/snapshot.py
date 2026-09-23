"""Freeze the corpus so CI can retrieve against it without a 90-minute ingest.

The corpus is 28,393 vectors across four sources and takes about an hour to embed. CI needs
the same corpus every run, byte for byte: a gate whose index differs from the one the
threshold was calibrated on is measuring the wrong thing.

    uv run python eval/snapshot.py create --out dist/          # after any ingest
    uv run python eval/snapshot.py restore --from dist/        # in CI, or on a fresh machine

Publishing is one line outside this script, so it stays a local tool:

    gh release create corpus-$(date +%F) dist/* --notes "28,393 vectors, 4 sources"
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

import httpx

from taxcite.index import COLLECTION, client

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://taxcite:taxcite@localhost:5433/taxcite")
DUMP = "chunks.sql"
SNAPSHOT = "qdrant-chunks.snapshot"


def create(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    qc = client()
    described = qc.create_snapshot(collection_name=COLLECTION, wait=True)
    if described is None:
        print("qdrant refused to snapshot", file=sys.stderr)
        return 1
    url = f"{QDRANT_URL}/collections/{COLLECTION}/snapshots/{described.name}"
    with httpx.stream("GET", url, timeout=600) as r:
        r.raise_for_status()
        with open(out / SNAPSHOT, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    qc.delete_snapshot(collection_name=COLLECTION, snapshot_name=described.name)

    # only the chunks table: jobs are per-run state, not corpus
    subprocess.run(["pg_dump", "--no-owner", "--table=chunks", "--file", str(out / DUMP), DATABASE_URL],
                   check=True)
    for name in (SNAPSHOT, DUMP):
        print(f"  {out / name}  {(out / name).stat().st_size / 1e6:.1f} MB")
    return 0


def restore(src: Path) -> int:
    # uploaded, not recovered from a path: in CI the Qdrant container cannot see the runner's disk
    with open(src / SNAPSHOT, "rb") as f:
        r = httpx.post(f"{QDRANT_URL}/collections/{COLLECTION}/snapshots/upload?priority=snapshot",
                       files={"snapshot": (SNAPSHOT, f, "application/octet-stream")}, timeout=900)
    r.raise_for_status()
    subprocess.run(["psql", "--quiet", "--set", "ON_ERROR_STOP=1", "-f", str(src / DUMP), DATABASE_URL],
                   check=True)

    from taxcite import store
    points = client().count(COLLECTION).count
    with store.connect() as conn:
        rows = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
    print(f"restored {points} vectors, {rows} chunk rows")
    return 0 if points and rows else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create", help="snapshot the live corpus")
    c.add_argument("--out", type=Path, default=Path("dist"))
    r = sub.add_parser("restore", help="load a snapshot into an empty stack")
    r.add_argument("--from", dest="src", type=Path, default=Path("dist"))
    args = ap.parse_args()
    return create(args.out) if args.cmd == "create" else restore(args.src)


if __name__ == "__main__":
    raise SystemExit(main())