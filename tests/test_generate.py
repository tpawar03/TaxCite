"""Answer generation, tested without spending money: the model call is stubbed."""

import pytest

from taxcite import generate
from taxcite.retrieve import Hit

HITS = [
    Hit(citation="26 CFR 1.183-2(b)(3)", heading="§ 1.183-2 Activity not engaged in for profit defined.",
        text="(3) The time and effort expended by the taxpayer...", score=0.9,
        section="1.183-2", source="ecfr"),
    Hit(citation="IRS Pub 587 (2025), p. 12", heading="Publication 587 Business Use of Your Home",
        text="the prescribed rate (maximum $5 per square foot)", score=0.8,
        section="Pub 587", source="irs_pub"),
]


@pytest.fixture
def stub(monkeypatch):
    """Replace the model call; record what it was asked."""
    calls = {}

    def fake(system, prompt, model):
        calls.update(system=system, prompt=prompt, model=model)
        return calls.get("reply", "stub answer"), 100, 20

    monkeypatch.setattr(generate, "call_model", fake)
    return calls


def test_rag_puts_retrieved_sources_in_the_prompt(stub, monkeypatch):
    monkeypatch.setattr(generate, "search", lambda *a, **k: HITS)
    a = generate.answer("does time and effort matter?", mode="rag")
    assert "26 CFR 1.183-2(b)(3)" in stub["prompt"]
    assert "time and effort expended" in stub["prompt"]
    assert a.retrieved == HITS


def test_closed_book_does_not_retrieve(stub, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("closed_book must not call search")

    monkeypatch.setattr(generate, "search", boom)
    a = generate.answer("anything", mode="closed_book")
    assert a.retrieved == []
    assert "Sources" not in stub["prompt"]


def test_citations_are_matched_against_retrieved_sources(stub, monkeypatch):
    monkeypatch.setattr(generate, "search", lambda *a, **k: HITS)
    stub["reply"] = ("Time and effort is a factor [26 CFR 1.183-2(b)(3)]. "
                     "The cap is $1,500 [IRS Pub 587 (2025), p. 12].")
    a = generate.answer("q", mode="rag")
    assert a.citations == ["26 CFR 1.183-2(b)(3)", "IRS Pub 587 (2025), p. 12"]
    assert a.unsupported_citations == []


def test_a_narrower_paragraph_of_a_retrieved_section_counts_as_derived(stub, monkeypatch):
    """Chunk citations are sometimes ranges; citing one paragraph inside is precision, not invention."""
    hits = HITS + [Hit(citation="26 CFR 1.212-1(c)-(d)", heading="§ 1.212-1 Nontrade expenses.",
                       text="(c) ...", score=0.5, section="1.212-1", source="ecfr")]
    monkeypatch.setattr(generate, "search", lambda *a, **k: hits)
    stub["reply"] = "See [26 CFR 1.212-1(c)] and [26 CFR 1.183-2(b)(3)]."
    a = generate.answer("q", mode="rag")
    assert a.citations == ["26 CFR 1.183-2(b)(3)"]
    assert a.derived_citations == ["26 CFR 1.212-1(c)"]
    assert a.unsupported_citations == []


def test_section_of_ignores_paragraph_depth():
    assert generate.section_of("26 CFR 1.263(a)-3(k)(1)") == "1.263(a)-3"
    assert generate.section_of("26 CFR 1.212-1(c)-(d)") == "1.212-1"
    assert generate.section_of("IRS Pub 587 (2025), p. 12") == "Pub 587"
    assert generate.section_of("26 U.S.C. § 183(d)") == "183"
    assert generate.section_of("26 U.S.C. § 1400Z-2(a)(1)") == "1400Z-2"  # the dash is part of the section
    assert generate.section_of("26 U.S.C. §280A") == "280A"
    assert generate.section_of("T.C. Memo. 2026-76, at *12-13") == "T.C. Memo. 2026-76"
    assert generate.section_of("Read v. Commissioner, 114 T.C. No. 2, at *5") == "114 T.C. No. 2"


def test_invented_citations_are_flagged(stub, monkeypatch):
    """A citation not among the sources is the failure mode this system exists to prevent."""
    monkeypatch.setattr(generate, "search", lambda *a, **k: HITS)
    stub["reply"] = "The rule is clear [26 CFR 1.999-9(z)] and also here [26 CFR 1.183-2(b)(3)]."
    a = generate.answer("q", mode="rag")
    assert a.unsupported_citations == ["26 CFR 1.999-9(z)"]  # a section never retrieved
    assert a.citations == ["26 CFR 1.183-2(b)(3)"]
    assert a.derived_citations == []


def test_refusal_is_detected(stub, monkeypatch):
    monkeypatch.setattr(generate, "search", lambda *a, **k: HITS)
    stub["reply"] = "INSUFFICIENT EVIDENCE: the sources do not cover state conformity."
    assert generate.answer("q", mode="rag").refused


def test_cost_uses_the_model_price(stub, monkeypatch):
    monkeypatch.setattr(generate, "search", lambda *a, **k: HITS)
    a = generate.answer("q", mode="rag", model="claude-haiku-4-5")
    # 100 input tokens at $1/MTok + 20 output at $5/MTok
    assert a.cost_usd == pytest.approx((100 * 1.0 + 20 * 5.0) / 1e6)


def test_unknown_model_costs_zero_rather_than_guessing(stub, monkeypatch):
    monkeypatch.setattr(generate, "search", lambda *a, **k: HITS)
    assert generate.answer("q", mode="rag", model="mystery-model").cost_usd == 0.0


def test_unknown_mode_is_rejected():
    with pytest.raises(ValueError, match="mode must be"):
        generate.answer("q", mode="telepathy")


def test_duplicate_citations_are_listed_once(stub, monkeypatch):
    monkeypatch.setattr(generate, "search", lambda *a, **k: HITS)
    stub["reply"] = "A [26 CFR 1.183-2(b)(3)]. B [26 CFR 1.183-2(b)(3)]."
    assert generate.answer("q", mode="rag").citations == ["26 CFR 1.183-2(b)(3)"]


def test_missing_anthropic_credentials_say_what_to_set(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    monkeypatch.setattr(generate.Path, "home", classmethod(lambda cls: tmp_path))
    with pytest.raises(generate.MissingCredentials, match="ANTHROPIC_API_KEY"):
        generate.call_model("sys", "prompt", "claude-haiku-4-5")


def test_a_cli_profile_counts_as_credentials(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    (tmp_path / ".config" / "anthropic").mkdir(parents=True)
    monkeypatch.setattr(generate.Path, "home", classmethod(lambda cls: tmp_path))
    generate._require_credentials("claude-haiku-4-5")  # must not raise


def test_missing_openai_key_says_what_to_set(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(generate.MissingCredentials, match="OPENAI_API_KEY"):
        generate.call_model("sys", "prompt", "gpt-5-mini")