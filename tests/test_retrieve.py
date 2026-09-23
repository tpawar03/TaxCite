import pytest

from taxcite import index
from taxcite.retrieve import Hit, rerank, search

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


def test_unknown_mode_suffix_is_rejected():
    with pytest.raises(ValueError, match="only '\\+rerank' exists"):
        search("anything", mode="hybrid+magic")


def hit(citation, heading, text):
    return Hit(citation=citation, heading=heading, text=text, score=0.0, section=citation, source="ecfr")


def test_rerank_promotes_the_rule_over_a_chunk_that_only_mentions_it():
    """The cross-encoder's job: an example that quotes a rule is not the rule."""
    example = hit("26 CFR 1.183-2(c)(1)", "Example 1",
                  "A taxpayer inherited a farm of 65 acres from her husband and moved onto the farm.")
    rule = hit("26 CFR 1.183-2(b)(3)", "Relevant factors",
               "The time and effort expended by the taxpayer in carrying on the activity. The fact that "
               "the taxpayer devotes much of his personal time and effort to carrying on an activity may "
               "indicate an intention to derive a profit.")
    ranked = rerank("does the time a taxpayer spends on an activity show a profit motive?", [example, rule], k=2)
    assert [h.citation for h in ranked] == [rule.citation, example.citation]
    assert ranked[0].score > ranked[1].score


def test_rerank_mode_reorders_the_hybrid_candidates():
    q = "does time spent on an activity matter for hobby loss rules?"
    plain = [h.citation for h in search(q, k=10, mode="hybrid")]
    reranked = [h.citation for h in search(q, k=10, mode="hybrid+rerank")]
    assert len(reranked) == 10
    assert plain != reranked
    assert set(reranked) <= set(h.citation for h in search(q, k=25, mode="hybrid"))  # drawn from the candidate pool


def test_source_filter_limits_results():
    assert all(h.source == "ecfr" for h in search("depreciation", k=5, source="ecfr"))
    assert all(h.source == "irs_pub" for h in search("depreciation", k=5, source="irs_pub"))


def test_publications_answer_what_regulations_cannot():
    """No final 280A regulations exist, so the home-office rules live only in Pub 587."""
    hits = search("simplified method home office deduction per square foot", k=10)
    assert any(h.source == "irs_pub" and "587" in h.citation for h in hits)