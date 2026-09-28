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

def test_graph_expansion_reaches_only_held_neighbors_within_the_hop_limit():
    """C5: A cites B and C; C cites D; E cites D; Z is unheld. Hops go either direction."""
    from taxcite.decompose import neighbors
    edges = {("A", "B"), ("A", "C"), ("C", "D"), ("E", "D"), ("A", "Z"), ("F", "Z")}
    held = {"A", "B", "C", "D", "E", "F"}
    assert neighbors(edges, {"A"}, 1, held) == {"B", "C"}            # Z is one hop away but not held
    assert neighbors(edges, {"A"}, 2, held) == {"B", "C", "D", "F"}  # F through unheld Z (co-citation)
    assert neighbors(edges, {"D"}, 1, held) == {"C", "E"}            # cited-by counts as a hop
    assert neighbors(edges, {"A"}, 0, held) == set()                 # off
    assert "A" not in neighbors(edges, {"A", "B"}, 2, held | {"A"})  # seeds are never returned


@pytest.mark.parametrize("as_of, year", [
    ("2023", 2023),
    ("2026-05", 2026),
    ("tax year 2016", 2016),
    (None, None),
    ("", None),
    ("2016 and 2026", None),   # two years: a one-year filter would drop half the answer
    ("2024 through 2024", 2024),
])
def test_tax_year_is_one_year_or_none(as_of, year):
    assert dc.tax_year(as_of) == year


def test_the_plans_tax_year_reaches_search_only_when_editions_are_on(monkeypatch):
    calls = []
    monkeypatch.setattr(dc, "search", lambda q, k, mode, source, **kw: calls.append(kw) or [])
    plan = lambda as_of: dc.Decomposition("q", [dc.SubQuery("statutory", "x")], as_of=as_of)  # noqa: E731
    dc.retrieve(plan("2023"))
    dc.retrieve(plan("2023"), editions=(1, 0))
    dc.retrieve(plan("2016 and 2026"), editions=(1, 0))
    assert calls == [{}, {"year": 2023, "editions": (1, 0)}, {}]


def test_statute_floor_searches_the_statute_and_keeps_it_through_reranking(monkeypatch):
    """D3b: plain-English publications outrank the statute; a statute-only search puts it in the
    pool and the reserved slots keep it there."""
    pubs = [hit(f"IRS Pub 17 (2025), p. {i}", source="irs_pub") for i in range(1, 6)]
    statute = [hit("26 U.S.C. § 67(e)-(h)", source="usc"), hit("26 U.S.C. § 67(a)-(b)", source="usc")]
    calls = []

    def fake_search(q, k, mode, source, **kw):
        calls.append(source)
        return statute if source == "usc" else pubs
    monkeypatch.setattr(dc, "search", fake_search)
    monkeypatch.setattr(dc, "rerank", lambda q, hits, k, name: hits)  # publications first, as measured

    d = dc.retrieve(dc.Decomposition("q", plan(("statutory", "s"), ("case_law", "c"))), k=3, statute=2)
    assert calls == [("usc", "ecfr", "irs_pub"), "usc", ("case",)]   # statutory sub-query only
    kept = [h.citation for h in dc.chunks(d, 3, floor=0)]
    assert {"26 U.S.C. § 67(e)-(h)", "26 U.S.C. § 67(a)-(b)"} <= set(kept) and len(kept) == 3
    off = dc.retrieve(dc.Decomposition("q", plan(("statutory", "s"))), k=3)
    assert not {h.source for h in dc.chunks(off, 3, floor=0)} & {"usc"}   # off: the pool never had it


def scored(citation, score, source, kind, status, lvl):
    return Hit(citation=citation, heading="h", text="t", score=score, section=citation, source=source,
               authority={"type": kind, "status": status, "level": lvl})


E4_POOL = [scored("IRS Pub 587 (2025), p. 5", 1.00, "irs_pub", "publication", "not_binding", 1),
           scored("T.C. Memo. 2020-1, at *3", 0.90, "case", "opinion", "memorandum", 2),
           scored("26 U.S.C. § 280A(c)(1)", 0.80, "usc", "statute", "enacted", 4),
           scored("26 U.S.C. § 420(f)(7)", 0.20, "usc", "statute", "enacted", 4),
           scored("140 T.C. No. 16, at *1-2", 0.10, "case", "opinion", "reported", 3)]


def test_weigh_reorders_by_authority_and_drops_nothing():
    """E4 (a): the prior lifts the statute over the publication; every hit survives, scores re-assigned."""
    out = dc.weigh(E4_POOL, {"rule": "prior", "w": 0.25})   # statute 0.80 + 0.75, memo 0.90 + 0.25, publication 1.00
    assert [h.citation for h in out][:3] == ["26 U.S.C. § 280A(c)(1)", "T.C. Memo. 2020-1, at *3", "IRS Pub 587 (2025), p. 5"]
    assert sorted(h.citation for h in out) == sorted(h.citation for h in E4_POOL)
    assert [h.score for h in out] == sorted((h.score for h in E4_POOL), reverse=True)
    assert out == dc.weigh(E4_POOL, {"rule": "prior", "w": 0.25})          # deterministic


def test_scoped_weighing_leaves_the_statute_against_opinion_order_alone():
    """E1's guards: reorder within a kind of source, never a statute over an opinion across kinds."""
    out = dc.weigh(E4_POOL, {"rule": "prior", "w": 1.0, "scoped": True})
    kinds = ["case" if h.source == "case" else "statutory" for h in out]
    assert kinds == ["case" if h.source == "case" else "statutory" for h in E4_POOL]   # same kind at each rank
    assert out[0].citation == "26 U.S.C. § 280A(c)(1)"             # statute over publication, within statutory
    assert [h.citation for h in out if h.source == "case"] == ["140 T.C. No. 16, at *1-2", "T.C. Memo. 2020-1, at *3"]
    flat = dc.weigh(E4_POOL, {"rule": "prior", "w": 1.0})
    assert flat[1].citation == "26 U.S.C. § 420(f)(7)"               # flat: an off-topic statute jumps the opinion


def test_tie_rule_moves_a_higher_level_only_within_delta():
    """A source passes a neighbour only if their scores are within delta: at 0.15 the memo passes the
    publication (0.10 apart), and the statute, 0.20 below the publication, can't pass it."""
    out = dc.weigh(E4_POOL, {"rule": "tie", "delta": 0.15})
    assert [h.citation for h in out][:3] == ["T.C. Memo. 2020-1, at *3", "IRS Pub 587 (2025), p. 5", "26 U.S.C. § 280A(c)(1)"]
    wide = dc.weigh(E4_POOL, {"rule": "tie", "delta": 0.25})
    assert [h.citation for h in wide][:3] == ["26 U.S.C. § 280A(c)(1)", "T.C. Memo. 2020-1, at *3", "IRS Pub 587 (2025), p. 5"]
    assert dc.weigh(E4_POOL, {"rule": "tie", "delta": 0.05}) == [*E4_POOL]    # no neighbour within 0.05


def test_the_widened_slot_takes_a_final_regulation_but_not_a_temporary_one(monkeypatch):
    monkeypatch.setattr(dc, "rerank", lambda q, hits, k, name: hits)
    pubs = [scored(f"IRS Pub 17 (2025), p. {i}", 1 - i / 10, "irs_pub", "publication", "not_binding", 1) for i in range(1, 4)]
    temp = scored("26 CFR 1.274-5T(c)(1)", 0.05, "ecfr", "regulation", "temporary", 4)
    final = scored("26 CFR 1.274-2(a)", 0.01, "ecfr", "regulation", "final", 4)
    s = dc.SubQuery("statutory", "s"); s.hits = pubs + [temp, final]
    d = dc.Decomposition("q", [s]); d.statute_floor = 1
    assert final.citation not in {h.citation for h in dc.chunks(d, 3, floor=0)}
    kept = {h.citation for h in dc.chunks(d, 3, floor=0, authority={"slot": True})}
    assert final.citation in kept and temp.citation not in kept
