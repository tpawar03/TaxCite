"""Answer a question, with and without retrieval.

Two modes, because the §9 ablation ladder needs the bottom rung: `closed_book`
asks the model with no sources (the baseline TaxCite has to beat), `rag` puts
retrieved chunks in the prompt and requires a citation on every claim.

Model choice is deliberate: start on the cheapest and fastest model and upgrade
only if measurement shows a need (T8). Override with TAXCITE_MODEL.
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from taxcite.retrieve import Hit, search

MODEL = os.environ.get("TAXCITE_MODEL", "gpt-4o-mini")
TOP_K = 8
MAX_TOKENS = 4000

# $ per million tokens (input, output), confirmed 2026-09-20.
# Cached-input rates ($0.075 gpt-4o-mini, $0.10 haiku) are omitted deliberately:
# our only stable prefix is the ~200-token system prompt, far below the minimum
# cacheable size, and the retrieved sources differ every query. The cache that
# pays here is the Redis verified-sub-answer cache (§3.4), not prompt caching.
PRICES = {
    "gpt-4o-mini": (0.15, 0.60),
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-sonnet-5": (2.00, 10.00),
    "claude-opus-5": (5.00, 25.00),
}

CITATION_RE = re.compile(r"\[([^\[\]]+)\]")
OPINION_RE = re.compile(r"\d+ T\.C\. No\. \d+|T\.C\. Memo\. \d{4}-\d+")

RAG_SYSTEM = """You answer US federal tax questions for an enrolled agent, using only the sources provided.

Rules:
1. Use ONLY the numbered sources. Do not add rules, dollar amounts or dates from memory.
2. Every sentence that states a rule must end with its citation in square brackets, copied exactly as the source header gives it, e.g. [26 CFR 1.183-2(b)(3)], [26 U.S.C. § 183(d)] or [T.C. Memo. 2026-76, at *12].
3. If the sources do not answer the question, say exactly: INSUFFICIENT EVIDENCE, and explain what is missing. Do not guess.
4. Regulations and statute outrank IRS publications. Where they differ, follow the regulation and say so.
5. Be brief: a practitioner wants the rule and the citation, not an essay."""

CLOSED_BOOK_SYSTEM = """You answer US federal tax questions for an enrolled agent, from your own knowledge.

No sources are provided. Answer as accurately as you can, and cite the section you
believe applies. Be brief."""


@dataclass
class Answer:
    text: str
    mode: str
    model: str
    citations: list[str] = field(default_factory=list)
    derived_citations: list[str] = field(default_factory=list)
    unsupported_citations: list[str] = field(default_factory=list)
    retrieved: list[Hit] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def cost_usd(self) -> float:
        in_rate, out_rate = PRICES.get(self.model, (0.0, 0.0))
        return (self.input_tokens * in_rate + self.output_tokens * out_rate) / 1e6

    @property
    def refused(self) -> bool:
        return "INSUFFICIENT EVIDENCE" in self.text.upper()


def format_sources(hits: list[Hit]) -> str:
    return "\n\n".join(
        f"[{h.citation}] ({h.heading})\n{h.text}" for h in hits
    )


def section_of(citation: str) -> str:
    """The section a citation belongs to, ignoring paragraph depth.

    '26 CFR 1.263(a)-3(k)(1)' -> '1.263(a)-3'   (the dash separates section from paragraphs)
    'IRS Pub 587 (2025), p. 12' -> 'Pub 587'
    '26 U.S.C. § 1400Z-2(a)(1)' -> '1400Z-2'  (statute sections can contain a dash)
    'Chapin v. Commissioner, T.C. Memo. 2026-76, at *12' -> 'T.C. Memo. 2026-76'  (an opinion is its "section")
    """
    if m := OPINION_RE.search(citation):
        return m.group()
    if citation.startswith("26 U.S.C."):
        return citation.removeprefix("26 U.S.C.").strip(" §").split("(")[0]
    body = citation.removeprefix("26 CFR ").strip()
    if body.startswith("IRS Pub"):
        return "Pub " + body.split()[2]
    head, dash, tail = body.partition("-")
    return f"{head}-{tail.split('(')[0]}" if dash else head


def parse_citations(text: str, retrieved: list[Hit]) -> tuple[list[str], list[str], list[str]]:
    """Split the answer's citations three ways: exact, derived, unsupported.

    The three differ in kind, and collapsing them misreads a model's behaviour:

    * exact       — the citation string a source carried, character for character.
    * derived     — a different paragraph of a section that *was* retrieved. Our chunk
                    citations are sometimes ranges ('1.212-1(c)-(d)') or coarser levels,
                    so a model citing '1.212-1(c)' is being more precise, not inventing.
                    Still worth counting separately: the precise paragraph was never
                    verified, so Phase F's claim check has nothing to check it against.
    * unsupported — a section that was never retrieved at all. This is fabrication, and
                    it is the failure the whole system exists to prevent.
    """
    available = {h.citation for h in retrieved}
    sections = {h.section for h in retrieved}
    cited = list(dict.fromkeys(CITATION_RE.findall(text)))

    exact = [c for c in cited if c in available]
    rest = [c for c in cited if c not in available]
    derived = [c for c in rest if section_of(c) in sections]
    unsupported = [c for c in rest if section_of(c) not in sections]
    return exact, derived, unsupported


class MissingCredentials(RuntimeError):
    """Raised instead of the SDK's generic auth error, which does not say what to set."""


def _require_credentials(model: str) -> None:
    """Fail early and specifically. The SDK raises a generic TypeError at request
    time, which does not say which variable to set."""
    if model.startswith("claude"):
        # an `ant auth login` profile is also valid, so a missing env var is not conclusive
        profile = Path.home() / ".config" / "anthropic"
        if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN") or profile.exists():
            return
        raise MissingCredentials(
            f"No Anthropic credentials for model {model!r}. Set ANTHROPIC_API_KEY "
            "(see .env.example), or run `ant auth login` to store a profile."
        )
    if not os.environ.get("OPENAI_API_KEY"):
        raise MissingCredentials(
            f"No OpenAI credentials for model {model!r}. Set OPENAI_API_KEY (see .env.example)."
        )


def call_model(system: str, prompt: str, model: str, temperature: float | None = None) -> tuple[str, int, int]:
    """One completion. Returns (text, input_tokens, output_tokens)."""
    _require_credentials(model)
    if model.startswith("claude"):
        import anthropic

        client = anthropic.Anthropic()
        kwargs = {"temperature": temperature} if temperature is not None else {}
        response = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        text = "".join(b.text for b in response.content if b.type == "text")
        return text, response.usage.input_tokens, response.usage.output_tokens

    from openai import OpenAI

    client = OpenAI()
    kwargs = {"temperature": temperature} if temperature is not None else {}
    response = client.chat.completions.create(
        model=model,
        max_completion_tokens=MAX_TOKENS,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        **kwargs,
    )
    usage = response.usage
    return response.choices[0].message.content or "", usage.prompt_tokens, usage.completion_tokens


def answer_from_hits(question: str, hits: list[Hit], model: str = MODEL) -> Answer:
    """Synthesis only, over chunks already retrieved.

    Split out from `answer` so a caller that reports progress (the SSE worker) can
    emit a stage event between retrieval and synthesis without searching twice.
    """
    return _generate(question, hits, mode="rag", model=model)


def answer(question: str, mode: str = "rag", k: int = TOP_K, model: str = MODEL,
           retrieval_mode: str = "hybrid") -> Answer:
    """Answer a question with retrieval (`rag`) or without it (`closed_book`)."""
    if mode not in ("rag", "closed_book"):
        raise ValueError(f"mode must be 'rag' or 'closed_book', not {mode!r}")
    hits = search(question, k=k, mode=retrieval_mode) if mode == "rag" else []
    return _generate(question, hits, mode=mode, model=model)


def _generate(question: str, hits: list[Hit], mode: str, model: str) -> Answer:
    if mode == "rag":
        prompt = f"Sources:\n\n{format_sources(hits)}\n\nQuestion: {question}"
        system = RAG_SYSTEM
    else:
        prompt = f"Question: {question}"
        system = CLOSED_BOOK_SYSTEM

    text, input_tokens, output_tokens = call_model(system, prompt, model)
    exact, derived, invented = parse_citations(text, hits)
    return Answer(text=text, mode=mode, model=model, citations=exact,
                  derived_citations=derived, unsupported_citations=invented,
                  retrieved=hits, input_tokens=input_tokens, output_tokens=output_tokens)