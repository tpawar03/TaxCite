"""Client-document ingestion (G2). Fixtures are built here, not stored: each is a few lines, and the bytes stay
readable in review."""

import io
import json
import shutil

import pytest
from fastapi.testclient import TestClient
from qdrant_client import models

from taxcite import api, index, retrieve, store
from taxcite.ingest import client_docs

client = TestClient(api.app)
qc = index.client()
CANARY = "123-45-6789"  # G-A06's SSN
INTAKE = ("Client intake. Name: Maria Lopez. SSN: 123-45-6789. Business: bakery, Schedule C. "
          "Question: can I deduct my delivery van?")  # G-A06's client_doc, verbatim
W2 = "Form W-2 Wage and Tax Statement 2025. Employer Okafor Bakery LLC. Box 1 wages 48250.00. Box 2 withheld 5120.00"
needs_tesseract = pytest.mark.skipif(not shutil.which("tesseract"), reason="tesseract not installed (brew install tesseract)")


def pdf(*pages: str) -> bytes:
    """A text-layer PDF, one page per string ("" is a page with no text). Offsets are computed, so it's valid."""
    objs = ["<< /Type /Catalog /Pages 2 0 R >>", "", "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    kids = []
    for text in pages:
        stream = f"BT /F1 10 Tf 40 740 Td ({text}) Tj ET"
        objs.append(f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream")
        objs.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> "
                    f"/Contents {len(objs)} 0 R >>")
        kids.append(f"{len(objs)} 0 R")
    objs[1] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(kids)} >>"
    out, offsets = b"%PDF-1.4\n", []
    for n, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += f"{n} 0 obj\n{body}\nendobj\n".encode()
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    out += b"".join(f"{o:010d} 00000 n \n".encode() for o in offsets)
    return out + f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()


def png(text: str) -> bytes:
    """A 'scan': the text drawn large on white, the way a phone photo of a form reads to OCR."""
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGB", (1700, 400), "white")
    ImageDraw.Draw(image).text((40, 150), text, fill="black", font=ImageFont.load_default(size=36))
    out = io.BytesIO()
    image.save(out, "PNG")
    return out.getvalue()


def scanned_pdf(text: str) -> bytes:
    """A PDF whose only page is an image: no text layer, so it needs OCR."""
    import pypdfium2
    from PIL import Image

    doc = pypdfium2.PdfDocument.new()
    page = doc.new_page(612, 792)
    image = pypdfium2.PdfImage.new(doc)
    image.set_bitmap(pypdfium2.PdfBitmap.from_pil(Image.open(io.BytesIO(png(text)))))
    image.set_matrix(pypdfium2.PdfMatrix().scale(580, 136).translate(16, 600))
    page.insert_obj(image)
    page.gen_content()
    out = io.BytesIO()
    doc.save(out)
    return out.getvalue()


def tenant(name: str) -> tuple[str, dict]:
    with store.connect() as conn:
        key = store.create_tenant(conn, f"test-docs-{name}")
        conn.commit()
        return store.tenant_for(conn, key), {"Authorization": f"Bearer {key}"}


def upload(headers: dict, name: str, data: bytes):
    return client.post("/documents", files={"file": (name, data)}, headers=headers)


@pytest.fixture(autouse=True)
def clean():
    with store.connect() as conn:
        client_docs.create_tables(conn)
        conn.execute("DELETE FROM tenants WHERE name LIKE 'test-%'")  # documents and chunks cascade
        conn.commit()
        client_docs.sweep(conn, qc)


def test_a_text_pdf_is_stored_listed_and_searchable_by_its_tenant():
    who, h = tenant("A")
    r = upload(h, "w2.pdf", pdf(W2))
    assert r.status_code == 201, r.text
    doc = r.json()
    assert doc["pages"] == 1 and doc["chunks"] == 1 and doc["failed_pages"] == []
    assert [d["id"] for d in client.get("/documents", headers=h).json()["documents"]] == [doc["id"]]
    hits = retrieve.search("Box 1 wages Okafor Bakery", k=3, collection=index.CLIENT_COLLECTION, tenant=who)
    assert hits[0].citation == "w2.pdf, p. 1" and hits[0].source == "client"


def test_a_page_with_no_text_is_reported_and_never_indexed():
    who, h = tenant("A")
    doc = upload(h, "two.pdf", pdf(W2, "")).json()
    assert doc["pages"] == 2 and doc["failed_pages"] == [{"page": 2, "status": client_docs.FAILED}]
    with store.connect() as conn:
        assert conn.execute("SELECT DISTINCT page FROM client_chunks WHERE document = %s", (doc["id"],)).fetchall() == [(1,)]


def test_disallowed_oversized_and_overlong_uploads_are_refused(monkeypatch):
    _, h = tenant("A")
    assert upload(h, "notes.txt", b"plain text, not a document").status_code == 415
    assert upload(h, "w2.pdf.exe", b"MZ\x90\x00" + pdf(W2)).status_code == 415  # sniffed, not trusted from the name
    assert upload(h, "broken.pdf", b"%PDF-1.4 not really").status_code == 422
    monkeypatch.setattr(client_docs, "MAX_BYTES", 100)
    r = upload(h, "w2.pdf", pdf(W2))
    assert r.status_code == 413 and "too large" in r.json()["detail"]
    monkeypatch.setattr(client_docs, "MAX_BYTES", 10_000)
    monkeypatch.setattr(client_docs, "MAX_PAGES", 1)
    r = upload(h, "two.pdf", pdf(W2, W2))
    assert r.status_code == 413 and "too many pages" in r.json()["detail"]
    assert client.get("/documents", headers=h).json()["documents"] == []  # nothing refused was stored


def test_uploads_have_a_daily_quota(monkeypatch):
    _, h = tenant("A")
    monkeypatch.setattr(client_docs, "UPLOADS_PER_DAY", 1)
    assert upload(h, "w2.pdf", pdf(W2)).status_code == 201
    r = upload(h, "w2.pdf", pdf(W2))
    assert r.status_code == 429 and "00:00 UTC" in r.json()["detail"]


def test_the_intake_ssn_is_redacted_before_anything_is_stored():
    """G-A06: the canary is in no response, no Postgres row and no Qdrant payload."""
    who, h = tenant("A")
    r = upload(h, f"intake {CANARY}.pdf", pdf(INTAKE))
    assert r.status_code == 201 and CANARY not in r.text
    with store.connect() as conn:
        rows = conn.execute("SELECT c.citation, c.text, d.name FROM client_chunks c JOIN client_documents d "
                            "ON d.id = c.document WHERE c.tenant = %s", (who,)).fetchall()
    points, _ = qc.scroll(index.CLIENT_COLLECTION, scroll_filter=models.Filter(must=[
        models.FieldCondition(key="tenant", match=models.MatchValue(value=who))]), with_payload=True)
    stored = json.dumps([list(r) for r in rows]) + json.dumps([p.payload for p in points])
    assert "[REDACTED SSN]" in stored and "Maria Lopez" in stored and CANARY not in stored


def test_redaction_catches_the_shapes_ocr_and_typing_leave():
    for shape in ("123-45-6789", "123 45 6789", "123456789", "123.45.6789", "123 - 45 - 6789"):
        assert client_docs.redact(f"SSN {shape}.") == "SSN [REDACTED SSN].", shape
    assert client_docs.redact("EIN 12-3456789") == "EIN [REDACTED EIN]"
    kept = "Box 1 48250.00, tax year 2025, call 555-123-4567, ZIP 94110-1234, $1,234,567.89"
    assert client_docs.redact(kept) == kept


def test_client_documents_cant_be_searched_without_a_tenant():
    with pytest.raises(ValueError, match="tenant"):
        retrieve.search("wages", collection=index.CLIENT_COLLECTION)


@needs_tesseract
def test_an_image_and_a_scanned_pdf_are_read_by_ocr():
    who, h = tenant("A")
    for name, data in (("w2.png", png("Box 1 wages 48250 Okafor Bakery")),
                       ("w2-scan.pdf", scanned_pdf("Box 1 wages 48250 Okafor Bakery"))):
        doc = upload(h, name, data).json()
        assert doc["chunks"] == 1 and doc["failed_pages"] == [], (name, doc)
    with store.connect() as conn:
        texts = [t for (t,) in conn.execute("SELECT text FROM client_chunks WHERE tenant = %s", (who,))]
    assert all("Okafor" in t for t in texts) and len(texts) == 2


@needs_tesseract
def test_an_ssn_in_a_scan_is_redacted_too():
    who, h = tenant("A")
    assert upload(h, "intake.png", png(f"SSN {CANARY} Maria Lopez")).status_code == 201
    with store.connect() as conn:
        (text,) = conn.execute("SELECT text FROM client_chunks WHERE tenant = %s", (who,)).fetchone()
    assert "6789" not in text and "Lopez" in text
