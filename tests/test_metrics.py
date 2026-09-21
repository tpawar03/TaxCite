"""The metrics must be right before any number computed with them means anything."""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "eval"))

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