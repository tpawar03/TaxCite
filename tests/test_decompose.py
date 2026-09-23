"""Decomposition: parsing a plan, routing it, and degrading when the plan is unusable."""

import pytest

from taxcite import decompose as dc
from taxcite.retrieve import Hit


def hit(citation, heading="h", text="t", source="ecfr"):
    return Hit(citation=citation, heading=heading, text=text, score=1.0, section=citation, source=source)


def plan(*pairs):
    return [dc.SubQuery(kind, query) for kind, query in pairs]


def test_parse_reads_kinds_queries_and_as_of():
    subs, as_of, fallback = dc.parse(
        '{"as_of": 2023, "subqueries": ['
        '{"kind": "statutory", "query": "hobby loss deduction limit"},'
        '{"kind": "case_law", "query": "profit objective nine factors"},'
        '{"kind": "client_fact", "query": "the client works full time"}]}', "q")
    assert [(s.kind, s.query) for s in subs] == [
        ("statutory", "hobby loss deduction limit"),
        ("case_law", "profit objective nine factors"),
        ("client_fact", "the client works full time"),
    ]
    assert as_of == "2023"  # the golden set stores as_of as a string ("2016 and 2026")
    assert fallback == ""
    assert [s.query for s in subs if not s.searchable] == ["the client works full time"]


@pytest.mark.parametrize("text", ["not json at all", "{}", '{"subqueries": "hobby loss"}',
                                  '{"subqueries": []}', '{"subqueries": [{"kind": "vibes", "query": "x"}]}',
                                  '{"subqueries": [{"kind": "client_fact", "query": "he is retired"}]}'])
def test_an_unusable_plan_falls_back_to_one_unrouted_search(text):
    """Phase A's path is the floor: a bad plan must not fail a question the corpus can answer."""
    subs, _, fallback = dc.parse(text, "can my client deduct this?")
    assert [(s.kind, s.query) for s in subs] == [("unrouted", "can my client deduct this?")]
    assert subs[0].sources is None  # no filter: every source, exactly as Phase A searched
    assert fallback


def test_more_than_four_subqueries_are_cut():
    text = '{"subqueries": [%s]}' % ",".join(
        '{"kind": "statutory", "query": "q%d"}' % i for i in range(7))
    subs, _, _ = dc.parse(text, "q")
    assert len(subs) == dc.MAX_SUBQUERIES


def test_routing_sends_the_question_itself_to_each_kind_of_corpus(monkeypatch):
    """The model is trusted for the routing, not the wording: rewritten text measured worse."""
    seen = []
    monkeypatch.setattr(dc, "search", lambda q, k, mode, source: seen.append((q, source)) or [])
    d = dc.Decomposition("the question", plan(("statutory", "s"), ("case_law", "c"), ("client_fact", "f")))
    dc.retrieve(d, k=5)
    assert seen == [("the question", ("usc", "ecfr", "irs_pub")),
                    ("the question", ("case",))]  # the client fact is never searched


def test_rewrite_searches_the_models_text_instead(monkeypatch):
    seen = []
    monkeypatch.setattr(dc, "search", lambda q, k, mode, source: seen.append(q) or [])
    dc.retrieve(dc.Decomposition("the question", plan(("statutory", "s"), ("case_law", "c"))),
                k=5, rewrite=True)
    assert seen == ["s", "c"]


def test_two_subqueries_of_one_kind_do_not_repeat_the_search(monkeypatch):
    calls = []
    monkeypatch.setattr(dc, "search", lambda q, k, mode, source: calls.append(q) or [])
    d = dc.Decomposition("the question", plan(("statutory", "a"), ("statutory", "b")))
    dc.retrieve(d, k=5)
    assert len(calls) == 1
    assert d.subqueries[0].hits is d.subqueries[1].hits


def test_routing_can_be_turned_off_for_the_ablation(monkeypatch):
    seen = []
    monkeypatch.setattr(dc, "search", lambda q, k, mode, source: seen.append(source) or [])
    dc.retrieve(dc.Decomposition("q", plan(("statutory", "s"), ("case_law", "c"))), k=5, route=False)
    assert seen == [None]  # same question, no filter: one search, shared by both sub-queries


def test_groups_keep_only_the_chunks_that_survived_reranking():
    a, b = plan(("statutory", "s"), ("case_law", "c"))
    a.hits = [hit("A1"), hit("A2")]
    b.hits = [hit("B1", source="case")]
    d = dc.Decomposition("q", [a, b, dc.SubQuery("client_fact", "the client is retired")])
    assert d.groups({"A1", "B1"}) == [("s", [a.hits[0]]), ("c", b.hits)]
    assert d.facts == ["the client is retired"]


def test_merge_interleaves_by_rank_and_drops_duplicates():
    a, b = plan(("statutory", "s"), ("case_law", "c"))
    a.hits = [hit("A1"), hit("A2"), hit("A3")]
    b.hits = [hit("B1"), hit("A2"), hit("B3")]  # A2 found by both, at rank 1 of each
    # rank 0: A1, B1 | rank 1: A2, then b's A2 is already in | rank 2: A3, B3
    assert [h.citation for h in dc.merge([a, b], k=10)] == ["A1", "B1", "A2", "A3", "B3"]
    assert [h.citation for h in dc.merge([a, b], k=3)] == ["A1", "B1", "A2"]


def test_merge_survives_a_subquery_that_found_nothing():
    a, b = plan(("statutory", "s"), ("case_law", "c"))
    a.hits = [hit("A1")]
    assert [h.citation for h in dc.merge([a, b], k=5)] == ["A1"]
    assert dc.merge([], k=5) == []


def test_chunks_reserves_a_slot_for_every_subquery():
    """Routing gets a corpus into the pool; the floor stops the reranker taking it back out."""
    stat, case = plan(("statutory", "s"), ("case_law", "c"))
    stat.hits = [hit("26 CFR 1.183-1(c)(1)", "Deductions allowable",
                     "Deductions for an activity not engaged in for profit are allowed only to the "
                     "extent of the gross income derived from the activity.")]
    case.hits = [hit(f"T.C. Memo. 2020-{i}, at *{i}", "Smith v. Commissioner",
                     "The taxpayer bred horses at a loss for many years. Weighing the nine factors, "
                     "the court found no actual and honest profit objective.", source="case")
                 for i in range(1, 13)]
    d = dc.Decomposition("did the horse breeding activity have a profit objective?", [stat, case])
    assert stat.hits[0].citation not in {h.citation for h in dc.chunks(d, 10, floor=0)}
    assert stat.hits[0].citation in {h.citation for h in dc.chunks(d, 10)}
    assert len(dc.chunks(d, 10)) == 10


def test_decompose_makes_one_call_and_asks_for_json(monkeypatch):
    calls = []
    monkeypatch.setattr(dc, "call_model", lambda system, prompt, model, **kw: calls.append((prompt, kw)) or (
        '{"as_of": null, "subqueries": [{"kind": "statutory", "query": "rewritten"}]}', 100, 20))
    d = dc.decompose("can my client deduct this?", model="gpt-4o-mini")
    assert len(calls) == 1
    assert calls[0][1] == {"temperature": 0, "json_output": True, "seed": dc.SEED}
    assert [s.query for s in d.searched] == ["rewritten"]
    assert d.cost_usd > 0 and d.fallback == ""