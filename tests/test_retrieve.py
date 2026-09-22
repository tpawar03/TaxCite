import pytest

from taxcite import index
from taxcite.retrieve import search

pytestmark = pytest.mark.skipif(
    index.count(index.client(), "ecfr") == 0, reason="needs an ingested corpus"
)


def test_dense_finds_the_hobby_loss_factor():
    hits = search("time and effort expended by the taxpayer", k=10, mode="dense")
    assert any(h.citation == "26 CFR 1.183-2(b)(3)" for h in hits)


def test_sparse_matches_literal_terms():
    hits = search("inclusion amount listed property", k=10, mode="sparse")
    assert any(h.section.startswith("1.280F") for h in hits)


def test_hybrid_returns_k_hits_with_payload():
    # pinned to one source: since B3, case law outranks regulations on this query
    hits = search("hobby loss factors", k=5, mode="hybrid", source="ecfr")
    assert len(hits) == 5
    h = hits[0]
    assert h.citation.startswith("26 CFR ")
    assert h.text and h.heading and h.source == "ecfr"
    assert 0 <= h.score


def test_modes_can_disagree():
    q = "does time spent on an activity matter for hobby loss rules?"
    assert [h.citation for h in search(q, k=5, mode="dense")] != [h.citation for h in search(q, k=5, mode="sparse")]


def test_results_are_reproducible():
    """RRF ties used to break differently per process, moving a chunk across the k cut-off."""
    q = "If an activity is not engaged in for profit, can the client deduct anything at all for it?"
    runs = [[h.citation for h in search(q, k=12, mode="hybrid")] for _ in range(3)]
    assert runs[0] == runs[1] == runs[2]
    scores = [h.score for h in search(q, k=12, mode="hybrid")]
    assert scores == sorted(scores, reverse=True)


def test_unknown_mode_is_rejected():
    with pytest.raises(ValueError, match="mode must be"):
        search("anything", mode="magic")


def test_source_filter_limits_results():
    assert all(h.source == "ecfr" for h in search("depreciation", k=5, source="ecfr"))
    assert all(h.source == "irs_pub" for h in search("depreciation", k=5, source="irs_pub"))


def test_publications_answer_what_regulations_cannot():
    """No final 280A regulations exist, so the home-office rules live only in Pub 587."""
    hits = search("simplified method home office deduction per square foot", k=10)
    assert any(h.source == "irs_pub" and "587" in h.citation for h in hits)