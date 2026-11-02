"""Cross-tenant leakage (Phase G gate: 0 failures). Grows with G2 (documents) and G3 (answers)."""

import json
import uuid

import pytest
from fastapi.testclient import TestClient

from taxcite import api, index, jobs, retrieve, store
from taxcite.generate import Answer
from taxcite.ingest import client_docs
from test_documents import ask, pdf, stub_models  # noqa: F401 (a fixture)

client = TestClient(api.app)


@pytest.fixture(autouse=True)
def clean():
    with store.connect() as conn:
        jobs.create_table(conn)
        conn.execute("DELETE FROM jobs")
        conn.execute(store.TENANTS)
        client_docs.create_tables(conn)
        conn.execute("DELETE FROM tenants WHERE name LIKE 'test-%'")  # their documents cascade
        conn.commit()
        client_docs.sweep(conn, index.client())  # and their points


@pytest.fixture
def stub_pipeline(monkeypatch):
    """No model, no search: isolation lives in the API and retrieval, not the LLM."""
    from taxcite import decompose as dc
    from taxcite import generate

    monkeypatch.setattr(dc, "decompose", lambda q, **k: dc.Decomposition(
        q, [dc.SubQuery("statutory", "home office")], as_of="2026", model="stub"))
    monkeypatch.setattr(dc, "search", lambda *a, **k: [])
    monkeypatch.setattr(generate, "answer_from_groups", lambda q, groups, **k: Answer(
        text="stub", mode="rag", model="stub", citations=[], input_tokens=0, output_tokens=0))


def key(name: str) -> dict:
    with store.connect() as conn:
        k = store.create_tenant(conn, f"test-leak-{name}")
        conn.commit()
    return {"Authorization": f"Bearer {k}"}


def test_every_route_but_health_needs_a_known_key():
    assert client.get("/health").status_code in (200, 503)
    for headers in ({}, {"Authorization": "Bearer not-a-key"}, {"Authorization": "Basic abc"}):
        assert client.post("/queries", json={"question": "x"}, headers=headers).status_code == 401
        assert client.get(f"/queries/{uuid.uuid4()}", headers=headers).status_code == 401
        assert client.get(f"/queries/{uuid.uuid4()}/events", headers=headers).status_code == 401


def test_another_tenants_job_is_indistinguishable_from_no_job(stub_pipeline):
    a, b = key("A"), key("B")
    job = client.post("/queries", json={"question": "CANARY-HENDERSON depreciation"}, headers=a).json()["id"]
    assert client.get(f"/queries/{job}", headers=a).status_code == 200

    for path in (f"/queries/{job}", f"/queries/{job}/events"):
        missing = client.get(path.replace(job, str(uuid.uuid4())), headers=b)
        r = client.get(path, headers=b)
        assert r.status_code == missing.status_code == 404
        assert r.json() == missing.json()  # same body: no "exists but not yours"
        assert "CANARY-HENDERSON" not in r.text


def test_a_malformed_job_id_is_a_404_not_an_error():
    assert client.get("/queries/not-a-uuid", headers=key("A")).status_code == 404


def test_quota_is_per_tenant_and_says_when_it_resets(stub_pipeline, monkeypatch):
    monkeypatch.setattr(api, "QUERIES_PER_DAY", 2)
    a, b = key("A"), key("B")
    for _ in range(2):
        assert client.post("/queries", json={"question": "q"}, headers=a).status_code == 202
    r = client.post("/queries", json={"question": "q"}, headers=a)
    assert r.status_code == 429 and "UTC" in r.json()["detail"]
    assert client.post("/queries", json={"question": "q"}, headers=b).status_code == 202  # B is unaffected


def test_the_global_cap_stops_everyone(stub_pipeline, monkeypatch):
    monkeypatch.setattr(api, "ALL_QUERIES_PER_DAY", 1)
    assert client.post("/queries", json={"question": "q"}, headers=key("A")).status_code == 202
    assert client.post("/queries", json={"question": "q"}, headers=key("B")).status_code == 429


def test_no_client_data_reaches_the_citation_graph(stub_pipeline):
    """ADR-5: graph-traversal reads hold public opinions only, so no tenant filter is needed there."""
    client.post("/queries", json={"question": "CANARY-HENDERSON"}, headers=key("A"))
    with store.connect() as conn:
        for table, cols in (("citations", "citing || cited"), ("treatments", "citation || by_citation")):
            (n,) = conn.execute(f"SELECT count(*) FROM {table} WHERE {cols} LIKE '%%CANARY%%'").fetchone()
            assert n == 0


HENDERSON = "Henderson workpapers. Depreciation schedule: delivery van placed in service 2024, MACRS 5-year, basis 41200."


def test_another_tenants_document_is_never_listed_searched_or_deletable():
    """G-A07's setup: A holds the Henderson workpapers; B can't find, see or remove them, nor tell they exist."""
    a, b = key("A"), key("B")
    with store.connect() as conn:
        a_id, b_id = (store.tenant_for(conn, h["Authorization"].split()[1]) for h in (a, b))
    doc = client.post("/documents", files={"file": ("henderson.pdf", pdf(HENDERSON))}, headers=a).json()["id"]

    assert client.get("/documents", headers=b).json() == {"documents": []}
    assert retrieve.search(HENDERSON, k=10, collection=index.CLIENT_COLLECTION, tenant=b_id) == []
    missing = client.delete(f"/documents/{uuid.uuid4()}", headers=b)
    r = client.delete(f"/documents/{doc}", headers=b)
    assert r.status_code == missing.status_code == 404 and r.json() == missing.json()
    assert client.delete("/documents/not-a-uuid", headers=b).status_code == 404

    assert [d["id"] for d in client.get("/documents", headers=a).json()["documents"]] == [doc]  # still A's
    assert retrieve.search(HENDERSON, k=1, collection=index.CLIENT_COLLECTION, tenant=a_id)[0].citation == "henderson.pdf, p. 1"
    assert client.delete(f"/documents/{doc}", headers=a).status_code == 204
    assert retrieve.search(HENDERSON, k=10, collection=index.CLIENT_COLLECTION, tenant=a_id) == []  # points go too


def test_document_routes_need_a_known_key():
    for headers in ({}, {"Authorization": "Bearer not-a-key"}):
        assert client.post("/documents", files={"file": ("w.pdf", pdf("x"))}, headers=headers).status_code == 401
        assert client.get("/documents", headers=headers).status_code == 401
        assert client.delete(f"/documents/{uuid.uuid4()}", headers=headers).status_code == 401


def test_another_tenants_document_never_reaches_an_answer(stub_models):
    """G-A07: B's prompts are identical with and without A's Henderson workpapers, and never show them."""
    a, b = key("A"), key("B")
    question = "What does the Henderson engagement's depreciation schedule show?"
    before = ask(b, question)["answer"]
    client.post("/documents", files={"file": ("henderson.pdf", pdf(HENDERSON))}, headers=a)
    after = ask(b, question)["answer"]
    assert stub_models["synthesis"][0] == stub_models["synthesis"][1] and stub_models["verify"][0] == stub_models["verify"][1]
    assert {k: v for k, v in before.items() if k != "trace_id"} == {k: v for k, v in after.items() if k != "trace_id"}
    sent = json.dumps(stub_models)
    assert "41200" not in sent and "henderson.pdf" not in sent and "client_document" not in sent

