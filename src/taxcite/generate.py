"""Answer a question, with and without retrieval.

Two modes, because the §9 ablation ladder needs the bottom rung: `closed_book`
asks the model with no sources (the baseline TaxCite has to beat), `rag` puts
retrieved chunks in the prompt and requires a citation on every claim.

Model choice is deliberate: start on the cheapest and fastest model and upgrade
only if measurement shows a need (T8). Override with TAXCITE_MODEL.
"""

import json
import os
import re
from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path

from taxcite.retrieve import Hit, search

MODEL = os.environ.get("TAXCITE_MODEL", "gpt-4o-mini")
# F3: a golden run hung for an hour on one request whose connection had died (the laptop slept); the SDKs' own
# defaults wait ten minutes per attempt. A synthesis or judge call takes seconds, so two minutes is generous.
API_TIMEOUT = 120.0
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
    "claude-sonnet-5-5": (2.00, 10.00),  # F5's reference judge; confirmed 2026-09-30
    "claude-opus-5": (5.00, 25.00),
}

CITATION_RE = re.compile(r"\[([^\[\]]+)\]")
# F0: the model sometimes nests one bracket in another, "[26 U.S.C. § 3121(d)(1), [119 T.C. No. 5, at *7-8]]", and
# CITATION_RE alone then sees only the inner citation
NESTED_RE = re.compile(r"\[([^\[\]]*?),?\s*\[([^\[\]]+)\]\]")
OPINION_RE = re.compile(r"\d+ T\.C\. No\. \d+|T\.C\. Memo\. \d{4}-\d+")
# F3: a section heading as the model writes it: "Part 2: Case law", "**Part 2 – Case law**", "### Part 2. Case law"
PART_RE = re.compile(r"^[ \t]*(?:#+[ \t]*)?\**[ \t]*Part[ \t]+(\d+)[ \t]*[:.\-–—][ \t]*(.*?)[ \t]*\**[ \t]*$", re.M)

RAG_SYSTEM = """You answer US federal tax questions for an enrolled agent, using only the sources provided.

Rules:
1. Use ONLY the numbered sources. Do not add rules, dollar amounts or dates from memory.
2. Every sentence that states a rule must end with its citation in square brackets, copied exactly as the source header gives it, e.g. [26 CFR 1.183-2(b)(3)], [26 U.S.C. § 183(d)] or [T.C. Memo. 2026-76, at *12].
3. If the sources do not answer the question, say exactly: INSUFFICIENT EVIDENCE, and explain what is missing. Do not guess.
4. Regulations and statute outrank IRS publications. Where they differ, follow the regulation and say so.
5. Be brief: a practitioner wants the rule and the citation, not an essay."""

RULE_4 = "4. Regulations and statute outrank IRS publications. Where they differ, follow the regulation and say so."
# E5's candidate (ii): the same rule over every level E2 labels; measured on dev before it replaces RULE_4
RULE_4_AUTHORITY = ("4. Each source is labelled with its authority. Where sources disagree, the higher authority "
                    "governs: statute and regulation, then a reported Tax Court opinion, then a Tax Court memorandum "
                    "opinion, then an IRS publication. Say which you followed. A lower source may explain the rule in "
                    "plain words, but cite the higher source for the rule itself.")
# (ii′), after dev: (ii) without its last sentence. "Cite the higher source for the rule itself" made the model
# cite a publication's own words to the statute (D08: faithfulness 0.67 -> 0.25), a misattribution
RULE_4_AUTHORITY_B = RULE_4_AUTHORITY.removesuffix(" A lower source may explain the rule in plain words, but cite "
                                                   "the higher source for the rule itself.")
assert RULE_4 in RAG_SYSTEM and RULE_4_AUTHORITY_B.endswith("Say which you followed.")
# (ii′) ships (E5, your decision). Dev's pre-registered rule 3 chose (ii) on "authority_misweighted" tags, 1 of 50
# vs (ii′)'s 4, a margin inside one row's flip; (ii) demonstrably cited a publication's words to the statute
# (D08), which its grounding rule couldn't see. (ii′): grounded 0.645 -> 0.789, dev faithfulness 0.835 ± 0.043
# vs 0.821 ± 0.015 before. Recorded as a departure from rule 3.
PRE_E5_SYSTEM = RAG_SYSTEM
RAG_SYSTEM = PRE_E5_SYSTEM.replace(RULE_4, RULE_4_AUTHORITY_B)
PRE_F3_SYSTEM = RAG_SYSTEM  # (ii′), shipped until F3; F3's arms build on it

# F3's candidates, measured on dev before either ships. F0: rule 2 asks for a citation only on "every sentence that
# states a rule", so applications and conclusions go uncited (475 of 853 golden sentences), and 14% of cited
# sentences say more than their source. A verifier can only check what is cited.
RULE_2 = ("2. Every sentence that states a rule must end with its citation in square brackets, copied exactly as the "
          "source header gives it, e.g. [26 CFR 1.183-2(b)(3)], [26 U.S.C. § 183(d)] or [T.C. Memo. 2026-76, at *12].")
RULE_2_EVERY = ("2. Every sentence must end with the citation of the source it relies on, in square brackets, copied "
                "exactly as the source header gives it, e.g. [26 CFR 1.183-2(b)(3)], [26 U.S.C. § 183(d)] or "
                "[T.C. Memo. 2026-76, at *12]. That includes a sentence applying a rule to the client's facts: cite the "
                "rule it applies. A sentence says only what its cited source says; if you can't cite a source for it, "
                "leave it out. The client's facts from the question need no citation.")
SECTIONS_RULE = """
7. Parts: the sources come in numbered parts, one per part of the question. Answer each part in its own section, headed "Part N: <what it answers>" on a line of its own, in the parts' order. Each section must stand on its own: use only that part's sources and do not rely on another section's conclusion. If there is only one part, write no heading."""
assert RULE_2 in RAG_SYSTEM
SECTIONS = False  # F3: number the parts and ask for a section per part

# F3 arm E. Prompting reached 0.60-0.71 completeness, never 0.85: the model writes most sentences cited, not all.
# So the citation moves into the output's shape: one JSON item per sentence, its citations chosen from the
# retrieved sources (an enum, so none can be invented), and an item left without one is dropped, not shown.
RULE_3 = ("3. If the sources do not answer the question, say exactly: INSUFFICIENT EVIDENCE, and explain what is "
          "missing. Do not guess.")
RULE_2_STRUCTURED = ("2. Write each sentence as its own item, with the citations of the sources it relies on, chosen "
                     "from the list. That includes a sentence applying a rule to the client's facts: cite the rule it "
                     "applies. A sentence says only what its cited sources say; an item without a citation is not shown.")
RULE_3_STRUCTURED = ("3. If the sources do not answer a part of the question, add that part to not_answerable with what "
                     "is missing. Do not guess.")
STRUCTURED_RULE = """
7. Output: JSON only, in the given shape. "part" is the number of the part a sentence answers (1 if there is one part). One sentence per item. "tax_year" is the year you answer for, or null."""
assert RULE_3 in RAG_SYSTEM
# Arm E ships (F3, your decision 2026-09-30), a recorded departure from F3's pre-registered rule, whose two metrics
# both worked against it: "refused" counted a cited answer with a caveat, and "answers emptied" ignored uncited
# sentences. On dev: completeness 1.000 (0.438 before), answers fully verified 0.523 (0.032), correctness 0.373 (same),
# faithfulness with the question as a source 0.864 ± 0.025 (0.859 ± 0.007).
RAG_SYSTEM = PRE_F3_SYSTEM.replace(RULE_2, RULE_2_STRUCTURED).replace(RULE_3, RULE_3_STRUCTURED)
STRUCTURED = True
# F5b C1: a conclusion, written last so the model reasons before it commits (F5's first try asked for it first: lost
# 14, won 9, noise), shown first once F5b's conclusion check passes it. C4: items that stand on their own.
CONCLUSION_RULE = """
8. Every item must stand on its own: name what it refers to, never "this", "it" or "such" for another item, and never a lead-in like "the following rules:".
9. Last, "conclusion": one sentence answering the question from your items: "Yes, ...", "No, ...", "It depends: ... if ..., ... if ...", or the short answer when the question isn't yes or no. It adds nothing your items don't say. If no item answers the question, leave it empty."""
# F5b (your decision 2026-10-01), a recorded departure from F5b's criteria 1 and 4: dev correct and grounded 27 -> 35, incorrect 18 -> 17, refusals 9 -> 15 (1 cost a correct grounded answer), short answer on 75%.
CONCLUSION = True


def answer_schema(citations_allowed: list[str], conclusion: bool = False) -> dict:
    """The JSON schema for arm E: strict, so every field is required and nothing else is allowed. Citations are an
    enum of the retrieved sources' citations: a structured answer cannot cite something it was not given. Fields are
    generated in order, so F5b's conclusion comes last."""
    obj = lambda props: {"type": "object", "additionalProperties": False,  # noqa: E731
                         "required": list(props), "properties": props}
    return obj({
        "tax_year": {"type": ["string", "null"]},
        "sentences": {"type": "array", "items": obj({
            "part": {"type": "integer"}, "text": {"type": "string"},
            "citations": {"type": "array", "items": {"type": "string", "enum": citations_allowed}}})},
        "not_answerable": {"type": "array", "items": obj({"part": {"type": "integer"}, "why": {"type": "string"}})},
        **({"conclusion": {"type": "string"}} if conclusion else {}),
    })


def cited_items(data: dict) -> list[dict]:
    """The sentences a structured answer can show, in order: text and at least one citation. `render` shows exactly
    these and the verifier (F4) numbers exactly these, so a verdict's index always names the sentence it judged."""
    out = []
    for s in data.get("sentences") or []:
        text, cites = str(s.get("text", "")).strip(), list(dict.fromkeys(c for c in s.get("citations") or [] if c))
        if text and cites:
            out.append({"part": s.get("part"), "text": text, "citations": cites})
    return out


def render(data: dict, labels: list[str]) -> tuple[str, int]:
    """(answer text, sentences dropped) from arm E's JSON. Each sentence ends with its citations, as rule 2 always
    asked; a sentence with none is dropped and counted. A part with nothing answered says INSUFFICIENT EVIDENCE; a
    detail missing from a part that is answered is a note, "Not in the sources: ..." (F3: as INSUFFICIENT EVIDENCE it
    ended 46% of answers)."""
    parts = {n: [] for n in range(1, len(labels) + 1)}
    shown = cited_items(data)
    dropped = sum(bool(str(s.get("text", "")).strip()) for s in data.get("sentences") or []) - len(shown)
    for s in shown:
        body = s["text"].rstrip(".").rstrip()
        parts[s["part"] if s["part"] in parts else 1].append(f"{body} {', '.join(f'[{c}]' for c in s['citations'])}.")
    answered = {n for n, lines in parts.items() if lines}
    for m in data.get("not_answerable") or []:
        n = m.get("part") if m.get("part") in parts else 1
        why = str(m.get("why", "")).strip()
        parts[n].append(f"Not in the sources: {why}" if n in answered else f"INSUFFICIENT EVIDENCE: {why}")
    blocks = []
    for n, lines in parts.items():
        if lines:
            head = f"Part {n}: {labels[n - 1]}\n" if len(labels) > 1 else ""
            blocks.append(head + " ".join(lines))
    year = f"Tax year: {data['tax_year']}\n\n" if data.get("tax_year") else ""
    return year + "\n\n".join(blocks), dropped

# E5: what an authority profile is called, wherever it's shown. One fixed map, fed only by E2's structured
# profile, never by what a source's text says about itself (ADR-13, FR-14): a document can't promote itself.
LABELS = {
    ("statute", "enacted"): "Statute",
    ("regulation", "final"): "Treasury regulation",
    ("regulation", "temporary"): "Treasury regulation (temporary)",
    ("regulation", "temporary_partly_expired"): "Treasury regulation (temporary)",
    ("regulation", "final_prior_version"): "Treasury regulation (earlier version)",
    ("opinion", "reported"): "Tax Court opinion (reported)",
    ("opinion", "memorandum"): "Tax Court memorandum opinion",
    ("publication", "not_binding"): "IRS publication (not binding)",
}
UNKNOWN_AUTHORITY = {"type": "unknown", "status": "unknown", "level": 0}
SOURCE_LABELS = True  # E5: each source's header carries its authority label (on with (ii′))


def authority_label(profile: dict | None) -> str:
    p = profile or {}
    return LABELS.get((p.get("type"), p.get("status")), "Authority unknown")


def authorities(answer: "Answer") -> dict[str, dict]:
    """Each cited source's authority and label, for the API (E5): an exact citation from its retrieved chunk, a
    derived one (another paragraph of a retrieved section) from that section's chunk, anything else unknown."""
    exact = {h.citation: h for h in answer.retrieved}
    section: dict[str, Hit] = {}
    for h in answer.retrieved:
        section.setdefault(section_of(h.citation), h)
    found = {c: exact.get(c) or section.get(section_of(c)) for c in answer.citations + answer.derived_citations}
    found |= {c: None for c in answer.unsupported_citations}
    return {c: {**((h.authority if h else None) or UNKNOWN_AUTHORITY), "label": authority_label(h.authority if h else None)}
            for c, h in found.items()}


# Only for a question with a tax year (D7). Given to every question it made the model refuse 40 of 96
# golden rows that name no year, faithfulness's refusal rate going 0.13 -> 0.55; the gate itself still
# passed, because refusals are outside its mean.
YEAR_RULE = """
6. Tax year: the question header names the tax year it is about. Start the answer by stating the year you answer for. A source marked "Effective:" had its current text take effect later than that year, or retroactively. Where that text itself states the rule for particular years (a schedule, "before January 1, 2022, 26 percent", "taxable years beginning after 2017"), those statements govern the years they name. Otherwise do not apply it to an earlier year: use the earlier text if the note quotes it, or say the rule for that year is not in the sources."""

CLOSED_BOOK_SYSTEM = """You answer US federal tax questions for an enrolled agent, from your own knowledge.

No sources are provided. Answer as accurately as you can, and cite the section you
believe applies. Be brief."""


def cost(model: str, input_tokens: int, output_tokens: int) -> float:
    in_rate, out_rate = PRICES.get(model, (0.0, 0.0))
    return (input_tokens * in_rate + output_tokens * out_rate) / 1e6


@dataclass
class Answer:
    text: str
    mode: str
    model: str
    citations: list[str] = field(default_factory=list)
    derived_citations: list[str] = field(default_factory=list)
    unsupported_citations: list[str] = field(default_factory=list)
    dropped_sentences: int = 0  # arm E: sentences the model wrote without a citation, not shown
    structured: dict | None = None  # arm E: {"data": the model's JSON, "labels": part labels}, for the verifier (F4)
    hidden: list[dict] = field(default_factory=list)  # F4: sentences the verifier failed, never shown (eval, logs)
    verdicts: list[dict] = field(default_factory=list)  # F4: one per shown sentence, so the eval can re-hide by unit
    sufficiency: list[dict] = field(default_factory=list)  # F2: the gate's verdict for each part, before synthesis
    gate_usd: float = 0.0
    verify_input_tokens: int = 0
    verify_output_tokens: int = 0
    verifier: str = ""
    conclusion: dict | None = None  # F5b: {"text", "shown", "citations", "why"} from the conclusion check
    retrieved: list[Hit] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def cost_usd(self) -> float:
        return (cost(self.model, self.input_tokens, self.output_tokens)
                + cost(self.verifier, self.verify_input_tokens, self.verify_output_tokens) + self.gate_usd)

    @property
    def refused(self) -> bool:
        """Says INSUFFICIENT EVIDENCE and cites nothing. F3: a cited answer that flags one missing detail, or answers
        one part of a two-part question, is an answer, not a refusal (arm E's 58 "refusals" were all cited answers)."""
        cited = self.citations or self.derived_citations or self.unsupported_citations
        return "INSUFFICIENT EVIDENCE" in self.text.upper() and not cited

    @property
    def sections(self) -> list[tuple[str, str]]:
        return split_sections(self.text)


def split_sections(text: str) -> list[tuple[str, str]]:
    """(label, text) per "Part N: ..." section (F3), the unit ADR-15 hides. No headings: one section, the whole
    answer. Text before the first heading is its own unlabelled section, so nothing escapes a section's check."""
    marks = list(PART_RE.finditer(text))
    if not marks:
        return [("", text.strip())]
    out = [("", text[:marks[0].start()].strip())] if text[:marks[0].start()].strip() else []
    for m, nxt in zip(marks, marks[1:] + [None]):
        out.append((f"Part {m.group(1)}: {m.group(2)}".rstrip(": "), text[m.end():nxt.start() if nxt else None].strip()))
    return out


def effective_note(h: Hit, year: int | None) -> str:
    """D7: flag statute text whose latest amendment took effect after the question's year, or
    retroactively, with the Amendments entry, which often quotes the replaced text."""
    e = h.effective
    if not e or year is None:
        return ""
    starts = re.search(r"\d{4}", e.get("date") or "")
    if not e.get("retroactive") and not (starts and int(starts.group()) >= year):
        return ""
    return f"\nEffective: the current text was enacted in {e['year']} and {e['rule']}. Amendment: {e['amendment'][:400]}"


def format_sources(hits: list[Hit], year: int | None = None) -> str:
    label = lambda h: f"\nAuthority: {authority_label(h.authority)}" if SOURCE_LABELS and h.authority else ""  # noqa: E731
    return "\n\n".join(
        f"[{h.citation}] ({h.heading}){label(h)}{effective_note(h, year)}\n{h.text}" for h in hits
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


def citations(text: str) -> list[str]:
    """Every bracketed citation, once each, in order: nested brackets flattened, "[A; B]" split (F0)."""
    flat = NESTED_RE.sub(r"[\1], [\2]", text)
    return list(dict.fromkeys(c.strip() for b in CITATION_RE.findall(flat) for c in b.split(";") if c.strip()))


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
    cited = citations(text)

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


def call_model(system: str, prompt: str, model: str, temperature: float | None = None,
               json_output: bool = False, seed: int | None = None,
               json_schema: dict | None = None, effort: str | None = None) -> tuple[str, int, int]:
    """One completion. Returns (text, input_tokens, output_tokens).

    The two providers expose different controls, and this function does not pretend
    otherwise:

    * `temperature` and `seed` are OpenAI only. `anthropic` 1.7.0 dropped `temperature`
      from `messages.create` entirely, so passing it raises a TypeError -- it is ignored
      for claude models rather than faked, and a caller that needs determinism from a
      claude model cannot get it this way.
    * `json_output` is OpenAI's loose JSON mode: valid JSON, no guaranteed shape.
    * `json_schema` is Anthropic's `output_config` format, which is stricter -- the
      response conforms to the schema. For OpenAI models it is sent as strict structured outputs
      (F3), which also require every property to be listed in `required`. Worth using wherever the shape matters, but parse
      defensively anyway: a refusal or a truncated response still is not your object.

    `seed` is OpenAI's best-effort determinism, and best-effort is the operative word:
    the same golden configuration still scored 0.457 / 0.422 / 0.434 across three runs
    (log #46), which is why the evals cache what the model produced.
    """
    _require_credentials(model)
    if model.startswith("claude"):
        import anthropic

        client = anthropic.Anthropic(timeout=API_TIMEOUT)
        kwargs = {}
        if json_schema is not None:
            kwargs["output_config"] = {"format": {"type": "json_schema", "schema": json_schema}}
        if effort:  # F5: Sonnet 5.5 thinks by default; a judge needs little of it, and output is billed at 5x input
            kwargs.setdefault("output_config", {})["effort"] = effort
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

    client = OpenAI(timeout=API_TIMEOUT)
    kwargs = {"temperature": temperature} if temperature is not None else {}
    if json_output:
        kwargs["response_format"] = {"type": "json_object"}
    if json_schema is not None:  # F3 arm E: OpenAI's strict structured outputs, the counterpart of output_config
        kwargs["response_format"] = {"type": "json_schema",
                                     "json_schema": {"name": "answer", "strict": True, "schema": json_schema}}
    if seed is not None:
        kwargs["seed"] = seed
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


def skipped_only(skipped: Sequence[tuple[str, str]], model: str = MODEL) -> Answer:
    """F2: every part judged insufficient before synthesis. A refusal with what each part lacks, and no model call:
    nothing is written, so nothing needs verifying (§9.3 H's refusal path)."""
    labels = [label for label, _ in skipped]
    text, _ = render({"tax_year": None, "sentences": [],
                      "not_answerable": [{"part": n, "why": why} for n, (_, why) in enumerate(skipped, 1)]}, labels)
    return Answer(text=text, mode="rag", model=model)


def answer_from_groups(question: str, groups: Sequence[tuple[str, list[Hit]]],
                       facts: Sequence[str] = (), model: str = MODEL, as_of: str | None = None,
                       skipped: Sequence[tuple[str, str]] = ()) -> Answer:
    """Synthesis over sources grouped by the sub-query that retrieved them (B7).

    The grouping is in the prompt deliberately: a compound question needs the model to
    see which part of the question each source answers, rather than one flat pile it
    has to re-sort. Client facts are labelled as facts, not sources, because rule 2
    requires a citation for every rule and a client's own statement is not one.

    Takes plain data rather than a Decomposition, so `decompose` depends on this
    module and not the other way round.

    `skipped` (F2): (label, what's missing) for parts the sufficiency gate rejected. They never reach the prompt
    (ADR-7: nothing is generated over insufficient evidence) and are shown after the answered parts.
    """
    years = sorted(set(re.findall(r"\b(?:19|20)\d\d\b", as_of or "")))
    year = int(years[0]) if years else None  # the earliest year named: the one later text can't govern
    groups = [(label, hits) for label, hits in groups if hits]
    blocks = [f"## Part {n}: {label}\n\n{format_sources(hits, year)}" if SECTIONS or STRUCTURED else
              f"## Sources for: {label}\n\n{format_sources(hits, year)}" for n, (label, hits) in enumerate(groups, 1)]
    if facts:
        blocks.append("## Client facts, supplied by the questioner (not sources; never cite these)\n"
                      + "\n".join(f"- {f}" for f in facts))
    hits = list({h.citation: h for _, group in groups for h in group}.values())
    header = f"Tax year(s) the question is about: {' and '.join(years)}\n" if years else ""
    prompt = "Sources:\n\n" + "\n\n".join(blocks) + f"\n\n{header}Question: {question}"
    if STRUCTURED and hits:
        return _generate_structured(hits, [label for label, _ in groups], model, prompt,
                                    RAG_SYSTEM + (YEAR_RULE if years else "") + STRUCTURED_RULE
                                    + (CONCLUSION_RULE if CONCLUSION else ""), skipped)
    system = RAG_SYSTEM + (YEAR_RULE if years else "") + (SECTIONS_RULE if SECTIONS else "")
    result = _generate(question, hits, mode="rag", model=model, prompt=prompt, system=system)
    if skipped:  # the unstructured arms: the skipped parts as plain lines after the answer
        result = replace(result, text=result.text + "".join(f"\n\n{label}: INSUFFICIENT EVIDENCE: {why}"
                                                            for label, why in skipped))
    return result


def _generate_structured(hits: list[Hit], labels: list[str], model: str, prompt: str, system: str,
                         skipped: Sequence[tuple[str, str]] = ()) -> Answer:
    """Arm E: the answer as JSON items, rendered to the same cited text every other arm writes, so the API, the CLI
    and the verifier read it unchanged. An unusable response is a refusal, never raw JSON in front of a user."""
    schema = answer_schema(sorted({h.citation for h in hits}), conclusion=CONCLUSION)
    raw, input_tokens, output_tokens = call_model(system, prompt, model, temperature=0, seed=0, json_schema=schema)
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        data = None
    if isinstance(data, dict) and skipped:  # F2: the gate's rejected parts follow the answered ones
        data = {**data, "not_answerable": list(data.get("not_answerable") or [])
                + [{"part": len(labels) + n, "why": why} for n, (_, why) in enumerate(skipped, 1)]}
        labels = labels + [label for label, _ in skipped]
    text, dropped = render(data, labels) if isinstance(data, dict) else ("", 0)
    if not text.strip():
        text = "INSUFFICIENT EVIDENCE: no sentence of the answer could be tied to a source."
    exact, derived, invented = parse_citations(text, hits)
    return Answer(text=text, mode="rag", model=model, citations=exact, derived_citations=derived,
                  unsupported_citations=invented, retrieved=hits, input_tokens=input_tokens,
                  output_tokens=output_tokens, dropped_sentences=dropped,
                  structured={"data": data, "labels": labels} if isinstance(data, dict) else None)


def answer(question: str, mode: str = "rag", k: int = TOP_K, model: str = MODEL,
           retrieval_mode: str = "hybrid") -> Answer:
    """Answer a question with retrieval (`rag`) or without it (`closed_book`)."""
    if mode not in ("rag", "closed_book"):
        raise ValueError(f"mode must be 'rag' or 'closed_book', not {mode!r}")
    hits = search(question, k=k, mode=retrieval_mode) if mode == "rag" else []
    return _generate(question, hits, mode=mode, model=model)


def _generate(question: str, hits: list[Hit], mode: str, model: str, prompt: str | None = None,
              system: str | None = None) -> Answer:
    if mode == "rag":
        prompt = prompt or f"Sources:\n\n{format_sources(hits)}\n\nQuestion: {question}"
        system = system or RAG_SYSTEM
    else:
        prompt = f"Question: {question}"
        system = CLOSED_BOOK_SYSTEM

    # Synthesis is pinned, not sampled. A legal-research tool that answers the same question
    # two ways on two asks is hard to defend, and the sampling was also the larger half of the
    # eval's noise: pinning it halved the faithfulness spread (sd 0.033 -> 0.016) with no
    # measurable quality cost (0.823 -> 0.808, inside the band). Both are ignored for claude
    # models, which expose neither knob.
    text, input_tokens, output_tokens = call_model(system, prompt, model, temperature=0, seed=0)
    exact, derived, invented = parse_citations(text, hits)
    return Answer(text=text, mode=mode, model=model, citations=exact,
                  derived_citations=derived, unsupported_citations=invented,
                  retrieved=hits, input_tokens=input_tokens, output_tokens=output_tokens)