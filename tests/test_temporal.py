"""The temporal gate's scoring rules (D2), on fixture values: no API calls."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "eval"))

import pytest
from temporal import as_of_match, kappa, passed


@pytest.mark.parametrize("plan, gold, expected", [
    ("2023", "2023", True),
    ("2026", "2026-05", True),      # month-level gold still compares at the year
    ("2022", "2026-05", False),     # an event date is not the tax year: gold must hold the tax year
    (None, None, True),             # no year asked, none extracted (G-T09's shape)
    (None, "2023", False),
    ("2025", None, False),          # a year invented for an undated question
    ("2016", "2016 and 2026", None),  # two years: a one-year plan can't express it, not scored
    (None, "2022 and 2029", None),
])
def test_as_of_match(plan, gold, expected):
    assert as_of_match(plan, gold) is expected


def test_pass_needs_a_correct_answer_and_no_as_of_miss():
    assert passed(True, "correct")
    assert passed(None, "correct")        # two-year rows pass on the answer alone
    assert not passed(False, "correct")   # right answer, wrong year extracted
    assert not passed(True, "partial")
    assert not passed(True, "unparsed")


def test_kappa_hand_computed():
    a = ["correct", "correct", "partial", "incorrect"]
    assert kappa(a, a) == 1.0
    # observed 2/4; expected (2*2 + 1*1 + 1*1)/16 = 0.375 -> (0.5 - 0.375) / 0.625
    assert kappa(a, ["correct", "partial", "correct", "incorrect"]) == pytest.approx(0.2)
    assert kappa(["correct"] * 3, ["correct"] * 3) == 1.0  # one category, full agreement
