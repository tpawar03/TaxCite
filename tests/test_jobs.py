"""Job record and SSE transport (ADR-9), with the pipeline stubbed."""

import json

import pytest
from fastapi.testclient import TestClient

from taxcite import api, jobs, store
from taxcite.generate import Answer

client = TestClient(api.app)

STAGES = ["decomposing", "retrieving", "synthesizing", "answer"]


@pytest.fixture(autouse=True)
def clean():
    with store.connect() as conn:
        jobs.create_table(conn)
        conn.execute("DELETE FROM jobs")
        conn.commit()
    yield


@pytest.fixture
def stub_pipeline(monkeypatch):
    """No decomposition, no retrieval, no LLM: this test is about the transport."""
    from taxcite import decompose as dc
    from taxcite import generate

    monkeypatch.setattr(dc, "decompose", lambda q, **k: dc.Decomposition(
        q, [dc.SubQuery("statutory", "hobby loss deduction limit")], as_of="2026", model="stub"))
    monkeypatch.setattr(dc, "search", lambda *a, **k: [])
    monkeypatch.setattr(generate, "answer_from_groups", lambda q, groups, **k: Answer(
        text="Yes [26 CFR 1.183-2(b)(3)].", mode="rag", model="stub",
        citations=["26 CFR 1.183-2(b)(3)"], input_tokens=10, output_tokens=5))


def sse_events(body: str) -> list[tuple[str, dict]]:
    out = []
    for block in body.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in block.splitlines())
        out.append((lines["event"], json.loads(lines["data"])))
    return out


def test_post_returns_an_id_immediately(stub_pipeline):
    r = client.post("/queries", json={"question": "does time and effort matter?"})
    assert r.status_code == 202
    body = r.json()
    assert body["events"].endswith("/events")
    assert client.get(f"/queries/{body['id']}").status_code == 200


def test_events_arrive_in_pipeline_order_and_end_with_the_answer(stub_pipeline):
    job_id = client.post("/queries", json={"question": "q"}).json()["id"]
    events = sse_events(client.get(f"/queries/{job_id}/events").text)
    assert [name for name, _ in events] == STAGES
    assert events[-1][1]["citations"] == ["26 CFR 1.183-2(b)(3)"]


def test_the_retrieving_stage_records_the_plan_and_the_as_of_year(stub_pipeline):
    """Phase D filters on as_of; B7 only records it, so the record already shows what it would use."""
    job_id = client.post("/queries", json={"question": "q"}).json()["id"]
    events = dict(sse_events(client.get(f"/queries/{job_id}/events").text))
    assert events["retrieving"]["as_of"] == "2026"
    assert events["retrieving"]["subqueries"] == [
        {"kind": "statutory", "query": "hobby loss deduction limit"}]


def test_a_late_client_still_sees_every_stage(stub_pipeline):
    """The record is written before the notification, so nothing is missed on reconnect."""
    job_id = client.post("/queries", json={"question": "q"}).json()["id"]
    client.get(f"/queries/{job_id}/events")  # run to completion
    again = sse_events(client.get(f"/queries/{job_id}/events").text)
    assert [name for name, _ in again] == STAGES


def test_unknown_job_is_404():
    assert client.get("/queries/3f0e4c8a-0000-4000-8000-000000000000/events").status_code == 404
    assert client.get("/queries/3f0e4c8a-0000-4000-8000-000000000000").status_code == 404


def test_a_failing_pipeline_is_recorded_not_swallowed(monkeypatch):
    from taxcite import decompose as dc

    def boom(*a, **k):
        raise RuntimeError("qdrant is down")

    monkeypatch.setattr(dc, "decompose", boom)
    job_id = client.post("/queries", json={"question": "q"}).json()["id"]
    events = sse_events(client.get(f"/queries/{job_id}/events").text)
    assert events[-1][0] == "error"
    assert events[-1][1]["type"] == "RuntimeError"
    with store.connect() as conn:
        assert jobs.get(conn, job_id)["status"] == "error"


def test_the_answer_is_one_event_not_a_token_stream(stub_pipeline):
    """ADR-9: nothing unverified reaches the user, so the answer is buffered."""
    job_id = client.post("/queries", json={"question": "q"}).json()["id"]
    events = sse_events(client.get(f"/queries/{job_id}/events").text)
    assert sum(1 for name, _ in events if name == "answer") == 1
    assert events[-1][1]["text"] == "Yes [26 CFR 1.183-2(b)(3)]."


def test_live_events_arrive_over_redis_while_the_job_runs():
    """ADR-16: Redis carries progress; the record is the source of truth behind it."""
    import threading
    import time

    with store.connect() as conn:
        job_id = jobs.create(conn, "slow question")

    def worker():
        time.sleep(0.2)
        with store.connect() as conn:
            jobs.publish(conn, job_id, "retrieving", {"k": 8})
            time.sleep(0.1)
            jobs.publish(conn, job_id, "answer", {"text": "done", "citations": []})

    thread = threading.Thread(target=worker)
    thread.start()
    events = sse_events(client.get(f"/queries/{job_id}/events").text)
    thread.join()
    assert [name for name, _ in events] == ["retrieving", "answer"]


def test_the_stream_survives_redis_being_down(monkeypatch, stub_pipeline):
    """A Redis outage must degrade liveness, not correctness (ADR-16)."""
    monkeypatch.setattr(jobs, "REDIS_URL", "redis://localhost:1/0")
    job_id = client.post("/queries", json={"question": "q"}).json()["id"]
    events = sse_events(client.get(f"/queries/{job_id}/events").text)
    assert [name for name, _ in events] == STAGES


def test_a_stage_is_never_delivered_twice(stub_pipeline):
    """The record and the live channel can race; sequence numbers settle it."""
    job_id = client.post("/queries", json={"question": "q"}).json()["id"]
    names = [name for name, _ in sse_events(client.get(f"/queries/{job_id}/events").text)]
    assert names == sorted(set(names), key=names.index)  # no repeats
    assert len(names) == len(set(names))