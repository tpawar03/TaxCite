"""The metrics must be right before any number computed with them means anything."""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "eval"))

import pytest
from ragas_eval import Budget, CostCap, Judged, aggregate, judge_claims, parse_json
from retrieval import mrr, ndcg_at_k, recall_at_k, section_of

GOLD = {"A", "B"}


def test_recall_counts_only_gold_hits():
    assert recall_at_k(["A", "B"], GOLD) == 1.0
    assert recall_at_k(["A", "X"], GOLD) == 0.5
    assert recall_at_k(["X", "Y"], GOLD) == 0.0


def test_recall_ignores_duplicates():
    assert recall_at_k(["A", "A", "A"], GOLD) == 0.5


def test_ndcg_rewards_earlier_hits():
    top = ndcg_at_k(["A", "B", "X"], GOLD)
    deep = ndcg_at_k(["X", "A", "B"], GOLD)
    assert top == 1.0
    assert deep < top


def test_ndcg_matches_hand_calculation():
    # one gold at rank 2: DCG = 1/log2(3); ideal for |gold|=2 = 1/log2(2) + 1/log2(3)
    expected = (1 / math.log2(3)) / (1 / math.log2(2) + 1 / math.log2(3))
    assert ndcg_at_k(["X", "A", "Y"], GOLD) == expected


def test_mrr_is_one_over_first_hit_rank():
    assert mrr(["A", "X"], GOLD) == 1.0
    assert mrr(["X", "A"], GOLD) == 0.5
    assert mrr(["X", "Y", "B"], GOLD) == 1 / 3
    assert mrr(["X", "Y"], GOLD) == 0.0


def test_empty_results_score_zero():
    assert recall_at_k([], GOLD) == 0.0
    assert ndcg_at_k([], GOLD) == 0.0
    assert mrr([], GOLD) == 0.0


def test_section_of_strips_paragraph_markers():
    assert section_of("26 CFR 1.183-2(b)(3)") == "1.183-2"
    assert section_of("26 CFR 1.263(a)-3(k)(1)") == "1.263(a)-3"
    assert section_of("26 CFR 1.280F-7(a)(1)") == "1.280F-7"
    assert section_of("26 CFR 1.61-1") == "1.61-1"

# gold groups (log #36): any member of a group satisfies it
GROUPS = [["26 U.S.C. § 183(a)-(d)", "26 CFR 1.183-1(b)(1)"], "26 CFR 1.183-2(b)(3)"]


def test_any_member_satisfies_a_group():
    assert recall_at_k(["26 U.S.C. § 183(a)-(d)", "X"], GROUPS) == 0.5
    assert recall_at_k(["26 CFR 1.183-1(b)(1)", "26 CFR 1.183-2(b)(3)"], GROUPS) == 1.0


def test_a_group_counts_once_even_when_several_members_are_retrieved():
    both = ["26 U.S.C. § 183(a)-(d)", "26 CFR 1.183-1(b)(1)"]
    assert recall_at_k(both, GROUPS) == 0.5
    # the second member adds no gain: DCG is the group's first hit only
    assert ndcg_at_k(both, GROUPS) == 1 / (1 / math.log2(2) + 1 / math.log2(3))


def test_mrr_uses_the_first_satisfied_group():
    assert mrr(["X", "26 CFR 1.183-1(b)(1)"], GROUPS) == 0.5


def test_section_of_understands_every_source():
    assert section_of("IRS Pub 587 (2025), p. 12") == "Pub 587"  # the old eval helper returned the whole string
    assert section_of("26 U.S.C. § 183(d)") == "183"
    assert section_of("T.C. Memo. 2021-115, at *4-5") == "T.C. Memo. 2021-115"


# ---------------------------------------------------------------- faithfulness (B8)

def judged(id, refused=False, supported=()):
    """A row with one claim per entry in `supported`."""
    return Judged(id=id, question="q", refused=refused,
                  claims=[f"claim {i}" for i in range(len(supported))],
                  verdicts=[{"index": i, "supported": v} for i, v in enumerate(supported)])


def test_a_refusal_is_not_scored_as_zero_or_as_one():
    """Averaging refusals in either direction breaks the gate: 0 punishes the behaviour we
    want, 1 lets a system pass by refusing everything."""
    rows = [judged("A", supported=(True, True)), judged("B", refused=True)]
    s = aggregate(rows)
    assert s["faithfulness"] == 1.0          # the refusal is out of the mean entirely
    assert s["scored"] == 1 and s["rows"] == 2
    assert s["refusals"] == 1 and s["refusal_rate"] == 0.5
    assert judged("B", refused=True).faithfulness is None


def test_faithfulness_is_the_supported_ratio():
    assert judged("A", supported=(True, True, True, False)).faithfulness == 0.75
    assert judged("A", supported=(False,)).faithfulness == 0.0


def test_an_answer_with_no_claims_is_reported_not_averaged():
    """An answer the extractor found nothing in would otherwise score 0/0."""
    row = judged("A")
    assert row.faithfulness is None
    s = aggregate([row, judged("B", supported=(True,))])
    assert s["answers_with_no_claim"] == 1
    assert s["scored"] == 1 and s["faithfulness"] == 1.0


def test_aggregate_counts_claims_and_unsupported_claims():
    s = aggregate([judged("A", supported=(True, False)), judged("B", supported=(True,))])
    assert s["claims"] == 3 and s["unsupported_claims"] == 1
    assert s["perfect_rows"] == 1
    assert s["faithfulness"] == pytest.approx((0.5 + 1.0) / 2)


def test_the_cost_cap_stops_a_run():
    budget = Budget(cap=0.001)
    budget.charge("claude-haiku-4-5", 100, 10)          # $0.00015, under the cap
    assert 0 < budget.spent < 0.001
    with pytest.raises(CostCap, match="cap"):
        budget.charge("claude-haiku-4-5", 1_000_000, 0)  # $1.00, over
    assert budget.spent > 0.001                          # the spend is recorded, not rolled back


def test_a_claim_the_judge_skipped_counts_as_unsupported(monkeypatch):
    """Silence is not support: a missing verdict must not quietly become a pass."""
    import ragas_eval
    monkeypatch.setattr(ragas_eval, "call_model",
                        lambda *a, **k: ('{"verdicts": [{"index": 0, "supported": true}]}', 10, 5))
    verdicts = judge_claims(["first", "second"], [{"citation": "c", "text": "t"}],
                            "claude-haiku-4-5", Budget(cap=1.0))
    assert [v["supported"] for v in verdicts] == [True, False]
    assert "no verdict" in verdicts[1]["why"]


def test_judging_no_claims_costs_nothing(monkeypatch):
    import ragas_eval
    monkeypatch.setattr(ragas_eval, "call_model", lambda *a, **k: pytest.fail("should not be called"))
    budget = Budget(cap=1.0)
    assert judge_claims([], [{"citation": "c", "text": "t"}], "claude-haiku-4-5", budget) == []
    assert budget.spent == 0.0


@pytest.mark.parametrize("text", ["not json", "{}", '{"claims": "one string"}', ""])
def test_a_judge_that_returns_junk_does_not_crash_the_run(text):
    assert parse_json(text, "claims", []) == []


def test_json_is_found_inside_chatter():
    """Instruction is not a guarantee; the model sometimes wraps its JSON in prose."""
    assert parse_json('Sure! {"claims": ["a", "b"]} Hope that helps.', "claims", []) == ["a", "b"]
