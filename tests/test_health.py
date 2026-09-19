from fastapi.testclient import TestClient

from taxcite import api

client = TestClient(api.app)


def test_all_stores_ok():
    r = client.get("/health")
    assert r.status_code == 200, r.json()
    assert r.json() == {"qdrant": "ok", "postgres": "ok", "redis": "ok"}


def test_down_store_reported(monkeypatch):
    monkeypatch.setattr(api, "REDIS_URL", "redis://localhost:1/0")
    r = client.get("/health")
    assert r.status_code == 503
    assert r.json()["redis"].startswith("error")
    assert r.json()["qdrant"] == "ok"
