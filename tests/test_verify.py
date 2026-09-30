"""Claim verification (F4), tested without spending money: the verifier call is stubbed."""

import json

import pytest

from taxcite import generate, verify
from taxcite.retrieve import Hit

STATUTE = Hit(citation="26 U.S.C. § 221(a)-(c)", heading="Interest on education loans",
              text="(a) ... a deduction ... interest paid ... on any qualified education loan. (b) ... $2,500.",
              score=0.9, section="221", source="usc")
PAGE_9 = Hit(citation="T.C. Memo. 2020-1, at *9", heading="Doe v. Commissioner", text="We hold the loan qualified.",
             score=0.8, section="T.C. Memo. 2020-1", source="case")
PAGE_4 = Hit(citation="T.C. Memo. 2020-1, at *4", heading="Doe v. Commissioner", text="Facts about the loan.",
             score=0.7, section="T.C. Memo. 2020-1", source="case")
PUB = Hit(citation="IRS Pub 17 (2025), p. 99", heading="Publication 17", text="State benefit funds...",
          score=0.6, section="Pub 17", source="irs_pub")
HITS = [STATUTE, PAGE_9, PAGE_4, PUB]
LABELS = ["federal deduction", "New Jersey"]


def structured_answer(sentences, not_answerable=()):
    data = {"tax_year": None, "sentences": sentences, "not_answerable": list(not_answerable)}
    text, _ = generate.render(data, LABELS)
    exact, derived, invented = generate.parse_citations(text, HITS)
    return generate.Answer(text=text, mode="rag", model="gpt-4o-mini", citations=exact, retrieved=HITS,
                           structured={"data": data, "labels": LABELS})


# one supported sentence and one fabricated one in part 1 (a real citation on a claim it doesn't make), one in part 2
ANSWER = structured_answer([
    {"part": 1, "text": "Interest on a qualified education loan is deductible.", "citations": [STATUTE.citation]},
    {"part": 1, "text": "The deduction has no income limit.", "citations": [STATUTE.citation]},
    {"part": 2, "text": "New Jersey allows the same deduction.", "citations": [PUB.citation]},
])


@pytest.fixture
def stub(monkeypatch):
    calls = []

    def fake(system, prompt, model, **kw):
        calls.append({"system": system, "prompt": prompt, "model": model, **kw})
        return calls_reply[0], 300, 40

    calls_reply = [json.dumps({"verdicts": [
        {"index": 0, "supported": True, "why": "states it"},
        {"index": 1, "supported": False, "why": "the source limits it"},
        {"index": 2, "supported": False, "why": "the source is about benefit funds"}]})]
    monkeypatch.setattr(verify, "call_model", fake)
    return calls, calls_reply


def test_a_cited_opinion_is_judged_with_all_its_retrieved_pages_and_a_statute_alone():
    item_case = {"part": 1, "text": "x", "citations": [PAGE_9.citation]}
    item_statute = {"part": 1, "text": "y", "citations": [STATUTE.citation]}
    assert verify.premises(item_case, ANSWER) == [1, 2]  # *9 cited, *4 the same opinion's other page
    assert verify.premises(item_statute, ANSWER) == [0]


def test_one_call_judges_every_sentence_with_the_question_and_the_whole_answer(stub):
    calls, _ = stub
    verdicts, tin, tout = verify.verify("Can she deduct it, and in New Jersey?", ANSWER)
    assert len(calls) == 1 and [v.supported for v in verdicts] == [True, False, False] and (tin, tout) == (300, 40)
    p = calls[0]["prompt"]
    assert p.startswith("Question: Can she deduct it, and in New Jersey?") and ANSWER.text in p
    assert "0. Interest on a qualified education loan is deductible. (cites: Source 1)" in p
    assert "2. New Jersey allows the same deduction. (cites: Source 2)" in p and "Source 2: [IRS Pub 17" in p
    assert calls[0]["model"] == verify.VERIFIER and calls[0]["json_schema"] == verify.SCHEMA
    assert "taken as given" in calls[0]["system"] and "Every assertion" in calls[0]["system"]


def test_a_skipped_verdict_is_a_failure_and_an_unusable_response_raises(stub):
    _, reply = stub
    reply[0] = json.dumps({"verdicts": [{"index": 0, "supported": True, "why": "ok"}]})
    assert [v.supported for v in verify.verify("q", ANSWER)[0]] == [True, False, False]  # silence is not support
    reply[0] = "{truncated"
    with pytest.raises(verify.VerificationFailed):
        verify.verify("q", ANSWER)


def test_part_hides_the_whole_part_and_sentence_hides_only_the_failure(stub):
    verdicts, _, _ = verify.verify("q", ANSWER)
    part = verify.apply(ANSWER, verdicts, "part")
    assert part.text == ("Part 1: federal deduction\nINSUFFICIENT EVIDENCE: no statement in this part could be verified "
                         "against its sources.\n\nPart 2: New Jersey\nINSUFFICIENT EVIDENCE: no statement in this part "
                         "could be verified against its sources.")
    assert part.refused and [h["failed"] for h in part.hidden] == [False, True, True]  # the kept one went with its part

    sentence = verify.apply(ANSWER, verdicts, "sentence")
    assert sentence.text == ("Part 1: federal deduction\nInterest on a qualified education loan is deductible "
                             "[26 U.S.C. § 221(a)-(c)].\n\nPart 2: New Jersey\nINSUFFICIENT EVIDENCE: no statement in "
                             "this part could be verified against its sources.")
    assert not sentence.refused and sentence.citations == [STATUTE.citation]
    assert [h["text"] for h in sentence.hidden] == ["The deduction has no income limit.",
                                                    "New Jersey allows the same deduction."]


def test_an_all_supported_answer_is_shown_unchanged(stub):
    _, reply = stub
    reply[0] = json.dumps({"verdicts": [{"index": k, "supported": True, "why": "ok"} for k in range(3)]})
    for unit in ("part", "sentence"):
        shown = verify.apply(ANSWER, verify.verify("q", ANSWER)[0], unit)
        assert shown.text == ANSWER.text and shown.hidden == []


def test_a_note_about_a_missing_detail_survives_when_its_part_is_shown(stub):
    _, reply = stub
    answer = structured_answer([{"part": 1, "text": "Deductible.", "citations": [STATUTE.citation]}],
                               [{"part": 1, "why": "the 2026 thresholds"}])
    reply[0] = json.dumps({"verdicts": [{"index": 0, "supported": True, "why": "ok"}]})
    assert verify.apply(answer, verify.verify("q", answer)[0]).text == \
        "Part 1: federal deduction\nDeductible [26 U.S.C. § 221(a)-(c)]. Not in the sources: the 2026 thresholds"


def test_checked_fails_closed_and_leaves_refusals_alone(stub, monkeypatch):
    def boom(*a, **k):
        raise TimeoutError("verifier timed out")
    monkeypatch.setattr(verify, "call_model", boom)
    shown = verify.checked("q", ANSWER)
    assert shown.text == verify.UNVERIFIED and shown.refused and len(shown.hidden) == 3
    assert "verifier timed out" in shown.hidden[0]["why"]

    refusal = generate.Answer(text="INSUFFICIENT EVIDENCE: nothing here.", mode="rag", model="m")
    assert verify.checked("q", refusal) is refusal  # nothing to verify, no call made


def test_checked_records_the_verifier_and_its_cost(stub):
    shown = verify.checked("q", ANSWER, unit="sentence")
    assert shown.verifier == verify.VERIFIER and shown.verify_input_tokens == 300
    assert shown.cost_usd == pytest.approx(generate.cost("gpt-4o-mini", 0, 0) + generate.cost(verify.VERIFIER, 300, 40))


def test_sentence_hiding_ships():
    """F4, your decision: only the failing sentence is hidden (ADR-15 revised); "part" stays available to the eval."""
    assert verify.HIDE == "sentence"
