"""Client documents (G2): a tenant's own uploads, searchable by that tenant only.

Kept apart from the public corpus on purpose (ADR-5, G0): their own tables and their own Qdrant collection, so
neither the index rebuild (`index.py` reads `chunks`) nor CI's published snapshot of the public collection can
ever carry them. Everything is checked and cleaned before anything is stored: the type is sniffed from the bytes,
size and pages are capped, text is extracted (OCR for scanned pages when tesseract is installed), and SSN- and
EIN-shaped strings are redacted.
"""

import io
import re
import shutil
import subprocess
import uuid

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from qdrant_client import models

from taxcite import index, retrieve, store
from taxcite.chunk import authority, estimate_tokens
from taxcite.ingest.irs_pubs import OVERLAP, TARGET_TOKENS, windows

# First guesses (plan G), in one place: FR-17 left the size open.
MAX_BYTES = 10 * 1024 * 1024
MAX_PAGES = 50
UPLOADS_PER_DAY = 20
FAILED = "extraction failed — excluded from retrieval"
MAGIC = {b"%PDF-": "pdf", b"\x89PNG\r\n\x1a\n": "png", b"\xff\xd8\xff": "jpeg", b"II*\x00": "tiff", b"MM\x00*": "tiff"}

SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS client_documents (
        id           uuid PRIMARY KEY,
        tenant       uuid NOT NULL REFERENCES tenants (id) ON DELETE CASCADE,
        name         text NOT NULL,
        kind         text NOT NULL,
        pages        int  NOT NULL,
        failed_pages int[] NOT NULL DEFAULT '{}',  -- never indexed; reported to the uploader
        created_at   timestamptz NOT NULL DEFAULT now()
    )
    """,
    "CREATE INDEX IF NOT EXISTS client_documents_tenant_idx ON client_documents (tenant, created_at DESC)",
    """
    CREATE TABLE IF NOT EXISTS client_chunks (
        key      text PRIMARY KEY,
        tenant   uuid NOT NULL,
        document uuid NOT NULL REFERENCES client_documents (id) ON DELETE CASCADE,
        page     int  NOT NULL,
        citation text NOT NULL,
        text     text NOT NULL,
        tokens   int  NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS client_chunks_document_idx ON client_chunks (document)",
)

# SSNs and ITINs share a shape. OCR and typing leave the separators as dashes, spaces, dots or nothing, so all are
# matched, but both separators or neither: one would also match a ZIP+4 (94110-1234). An EIN needs its separator,
# since nine bare digits are already redacted as an SSN.
SSN = re.compile(r"(?<!\d)\d{3}(?:[\s.-]{1,3}\d{2}[\s.-]{1,3}|\d{2})\d{4}(?!\d)")
EIN = re.compile(r"(?<!\d)\d{2}[\s-]{1,3}\d{7}(?!\d)")
# G4 (J15, J16): nine digits with a space in every gap ("3 8 1 - 6 2 - 5 5 0 7"), or nine spelled ones; ZIP+4 and
# phone numbers have unspaced digit pairs, so neither matches
SSN_SPACED = re.compile(r"(?<!\d)(?<!\d )\d(?:(?: [-.] | [-.]| )\d){8}(?![ .-]*\d)")
DIGIT = r"(?:zero|oh|one|two|three|four|five|six|seven|eight|nine)"
SSN_WORDS = re.compile(rf"\b{DIGIT}(?:[\s,.-]+{DIGIT}){{8}}\b", re.I)


class Rejected(ValueError):
    """An upload refused, with the HTTP status that says why."""

    def __init__(self, status: int, detail: str):
        super().__init__(detail)
        self.status = status


def redact(text: str) -> str:
    """Runs on every upload and every question, before anything is stored, searched, sent or traced (§3.4)."""
    for pattern in (SSN, SSN_SPACED, SSN_WORDS):
        text = pattern.sub("[REDACTED SSN]", text)
    return EIN.sub("[REDACTED EIN]", text)


def create_tables(conn) -> None:
    conn.execute(store.TENANTS)
    for statement in SCHEMA:
        conn.execute(statement)
    conn.commit()


def create_collection(qc) -> None:
    if qc.collection_exists(index.CLIENT_COLLECTION):
        return
    index.create_collection(qc, index.CLIENT_COLLECTION)
    # is_tenant: Qdrant stores each tenant's points together, so a filtered search reads only that tenant's
    qc.create_payload_index(index.CLIENT_COLLECTION, "tenant",
                            models.KeywordIndexParams(type=models.KeywordIndexType.KEYWORD, is_tenant=True))
    qc.create_payload_index(index.CLIENT_COLLECTION, "document", models.PayloadSchemaType.KEYWORD)


def kind(data: bytes) -> str:
    for magic, name in MAGIC.items():
        if data.startswith(magic):
            return name
    raise Rejected(415, "unsupported file type: upload a PDF, PNG, JPEG or TIFF")


def ocr(image) -> str:
    """Tesseract's text for one page image; "" when tesseract isn't installed, so the page fails (plan G)."""
    if not shutil.which("tesseract"):
        return ""
    png = io.BytesIO()
    image.save(png, "PNG")
    return subprocess.run(["tesseract", "stdin", "stdout"], input=png.getvalue(), capture_output=True,
                          timeout=120).stdout.decode(errors="replace")


def _pages(n: int) -> None:
    if n > MAX_PAGES:
        raise Rejected(413, f"too many pages: {n} (the limit is {MAX_PAGES})")


def page_texts(data: bytes, kind: str) -> list[str]:
    """One text per page: the text layer where there is one, OCR where there isn't."""
    if kind != "pdf":
        from PIL import Image

        image = Image.open(io.BytesIO(data))
        _pages(getattr(image, "n_frames", 1))  # a TIFF can hold many pages
        texts = []
        for frame in range(getattr(image, "n_frames", 1)):
            image.seek(frame)
            texts.append(ocr(image.convert("RGB")))
        return texts
    import pypdfium2

    pdf = pypdfium2.PdfDocument(data)
    _pages(len(pdf))
    texts = ["\n".join(el.get_text() for el in page if isinstance(el, LTTextContainer))
             for page in extract_pages(io.BytesIO(data))]
    return [text if text.split() else ocr(pdf[n].render(scale=300 / 72).to_pil()) for n, text in enumerate(texts)]


def uploads_today(conn, tenant: str) -> int:
    (n,) = conn.execute("SELECT count(*) FROM client_documents WHERE tenant = %s "
                        "AND created_at >= date_trunc('day', now(), 'UTC')", (tenant,)).fetchone()
    return n


def ingest(conn, qc, tenant: str, name: str, data: bytes) -> dict:
    """Check, extract, redact, chunk, embed and store one upload. Nothing is stored if any step fails."""
    if len(data) > MAX_BYTES:
        raise Rejected(413, f"file too large: the limit is {MAX_BYTES // (1024 * 1024)} MB")
    file_kind = kind(data)
    create_tables(conn)
    if uploads_today(conn, tenant) >= UPLOADS_PER_DAY:
        raise Rejected(429, "daily upload limit reached; resets at 00:00 UTC")
    try:
        texts = page_texts(data, file_kind)
    except Rejected:
        raise
    except Exception as e:  # a damaged or disguised file: the type matched, the contents didn't parse
        raise Rejected(422, f"could not read the {file_kind.upper()} ({type(e).__name__})") from e

    name = redact(name)[:200]  # a file name is user text too
    doc = str(uuid.uuid4())
    size = int(TARGET_TOKENS / 1.3)  # windows are counted in words, as for publications
    failed = [n for n, text in enumerate(texts, 1) if not text.split()]
    rows = [{"key": f"{doc}:{n}:{i}", "tenant": tenant, "document": doc, "page": n,
             "citation": f"{name}, p. {n}", "text": " ".join(words), "tokens": estimate_tokens(" ".join(words))}
            for n, text in enumerate(texts, 1) if text.split()
            for i, words in enumerate(windows(redact(text).split(), size, OVERLAP))]

    conn.execute("INSERT INTO client_documents (id, tenant, name, kind, pages, failed_pages) "
                 "VALUES (%s, %s, %s, %s, %s, %s)", (doc, tenant, name, file_kind, len(texts), failed))
    with conn.cursor() as cur:
        cur.executemany("INSERT INTO client_chunks (key, tenant, document, page, citation, text, tokens) VALUES "
                        "(%(key)s, %(tenant)s, %(document)s, %(page)s, %(citation)s, %(text)s, %(tokens)s)", rows)
    if rows:  # Qdrant before the commit: if it fails, the transaction rolls back and nothing half-exists
        create_collection(qc)
        dense, sparse = retrieve._models()
        bodies = [r["text"] for r in rows]
        index.upsert_with_retry(qc, index.CLIENT_COLLECTION, [
            models.PointStruct(
                id=index.point_id(r["key"]),
                vector={"dense": d.tolist(),
                        "sparse": models.SparseVector(indices=s.indices.tolist(), values=s.values.tolist())},
                payload={"tenant": tenant, "document": doc, "key": r["key"], "citation": r["citation"],
                         "heading": name, "section": doc, "source": "client", "page": r["page"], "text": r["text"],
                         "authority": authority("client", r["citation"], doc)})
            for r, d, s in zip(rows, dense.embed(bodies), sparse.embed(bodies))])
    conn.commit()
    return {"id": doc, "name": name, "kind": file_kind, "pages": len(texts), "chunks": len(rows),
            "failed_pages": [{"page": n, "status": FAILED} for n in failed]}


def documents(conn, tenant: str) -> list[dict]:
    """The tenant's own documents, newest first."""
    create_tables(conn)
    rows = conn.execute("SELECT id, name, kind, pages, failed_pages, created_at FROM client_documents "
                        "WHERE tenant = %s ORDER BY created_at DESC", (tenant,)).fetchall()
    return [{"id": str(r[0]), "name": r[1], "kind": r[2], "pages": r[3], "failed_pages": r[4], "created_at": r[5]}
            for r in rows]


def delete(conn, qc, tenant: str, doc: str) -> bool:
    """Remove a document, its chunks and its points. False for a missing id and for another tenant's, alike."""
    try:
        uuid.UUID(doc)
    except ValueError:
        return False
    create_tables(conn)
    found = conn.execute("DELETE FROM client_documents WHERE id = %s AND tenant = %s RETURNING id",
                         (doc, tenant)).fetchone()  # client_chunks go with it (ON DELETE CASCADE)
    if found and qc.collection_exists(index.CLIENT_COLLECTION):
        qc.delete(index.CLIENT_COLLECTION, points_selector=models.FilterSelector(filter=models.Filter(must=[
            models.FieldCondition(key="tenant", match=models.MatchValue(value=tenant)),
            models.FieldCondition(key="document", match=models.MatchValue(value=doc))])))
    conn.commit()
    return bool(found)


def sweep(conn, qc) -> None:
    """Remove the points of tenants that no longer exist: Postgres cascades a tenant's deletion, Qdrant can't."""
    if not qc.collection_exists(index.CLIENT_COLLECTION):
        return
    live = [str(r[0]) for r in conn.execute("SELECT id FROM tenants")]
    gone = models.Filter(must_not=[models.FieldCondition(key="tenant", match=models.MatchAny(any=live))]) if live \
        else models.Filter()
    qc.delete(index.CLIENT_COLLECTION, points_selector=models.FilterSelector(filter=gone))

