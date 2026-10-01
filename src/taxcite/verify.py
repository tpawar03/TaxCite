"""Claim verification (Phase F, F4): every sentence of an answer, against the sources it cites, before it is shown.

ADR-3 adds the check; ADR-4 (revised by F0) makes it one LLM call per answer rather than a self-hosted NLI model,
which reached F1 0.22-0.46 against the 0.90 gate. The prompt is the one F0 checked by hand: 30 of 40 verdicts agreed
with a careful read before three input fixes, 15 of 16 single sentences after. Those fixes are here too: the
verifier sees the question (a client's facts are given, not unsupported) and the whole answer (so "Therefore..."
has something to refer to), cited sources are judged together, and every assertion in a sentence must hold.

A sentence the verifier fails is never shown (ADR-15). `HIDE` decides what goes with it: "sentence", only itself
(shipped, F4), or "part", the part of the answer it belongs to (ADR-15 as first written). On dev, hiding the part
emptied 64 of 126 answers against 9; see HIDE for the numbers and the departure from F4's rule.
If verification itself fails, nothing unverified is shown: the answer becomes a refusal.
"""

import json
import os
from dataclasses import asdict, dataclass, replace

from taxcite.generate import OPINION_RE, Answer, call_model, cited_items, parse_citations, render, section_of

VERIFIER = os.environ.get("TAXCITE_VERIFIER", "claude-haiku-4-5")  # the other provider from synthesis (ADR-11)
# F4 (your decision 2026-09-30), a recorded departure from F4's pre-registered rule, which neither unit passed: shown
# answers at most 0.05 less correct than unverified ones (>= 0.315). Dev: sentence 0.278 with 9 of 126 answers emptied,
# part 0.206 with 64. The bar credits the unverified answer for being right from memory, which verification exists to
# remove: correct *and* grounded moved only 0.238 -> 0.214, and 9 of the new "incorrect" were honest refusals.
HIDE = "sentence"
UNVERIFIED = "INSUFFICIENT EVIDENCE: the answer could not be verified."

SYSTEM = """You check whether each claim is supported by the sources it cites.

You also get the question and the whole answer the claims come from. The question's facts about the client may be taken as given (they are facts, not law); the answer only tells you what a claim refers to. Judge each claim's content against the sources it cites by number, never the others, even if another one supports it. A claim citing several sources is supported if they state it together, even if some of them say nothing relevant. Every assertion in the claim must be supported: a claim with any unsupported part, qualifier or condition is NOT supported.

Return JSON only: {"verdicts": [{"index": 0, "supported": true, "why": "..."}]}, one entry per
claim, in order.

"supported" means the sources state the claim or it follows directly from what they state,
including arithmetic the sources make possible. It does NOT mean the claim is good law, and it
does NOT mean you agree with it: a claim you know to be legally wrong is still supported if the
sources say it. A claim that is true in general but absent from these sources is NOT supported.
Keep "why" under 20 words."""

SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["verdicts"],
    "properties": {"verdicts": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["index", "supported", "why"],
        "properties": {"index": {"type": "integer"}, "supported": {"type": "boolean"}, "why": {"type": "string"}}}}},
}


# F5b C3: a failed sentence may cite the wrong one of the retrieved sources (D24's $15,750 cites p. 3; the chart is
# p. 97). One call names the source that states it, and the swap is re-checked by SYSTEM, unchanged; text is never
# rewritten. C2: the conclusion is an inference, judged against the sentences that passed rather than quoted from a
# source, and shown cited with theirs. Both off until measured.
RECITE = False
RECITE_SYSTEM = """Each claim below failed a check against the source it cited. For each, pick the one source from the list that states the claim fully, every part, qualifier and condition, or null if none does. The question's facts about the client may be taken as given. Never pick a source that states only part of the claim.

Return JSON only: {"recites": [{"index": 0, "source": 3, "why": "..."}]}, one entry per claim. Keep "why" under 15 words."""
RECITE_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["recites"],
    "properties": {"recites": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["index", "source", "why"],
        "properties": {"index": {"type": "integer"}, "source": {"type": ["integer", "null"]}, "why": {"type": "string"}}}}},
}
CONCLUSION_SYSTEM = """You check an answer's conclusion against statements already verified from sources.

The conclusion is supported only if it follows from the numbered statements together with the question's facts about the client. A conclusion that adds a rule, number, date or condition the statements don't contain is NOT supported. A conclusion that ignores a condition or exception the statements make material is NOT supported. Do not use your own knowledge of the law.

Return JSON only: {"follows": true, "basis": [0, 2], "why": "..."}. "basis" lists the statements it follows from. Keep "why" under 20 words."""
CONCLUSION_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["follows", "basis", "why"],
    "properties": {"follows": {"type": "boolean"}, "basis": {"type": "array", "items": {"type": "integer"}},
                   "why": {"type": "string"}},
}


class VerificationFailed(RuntimeError):
    """The verifier's response was unusable. The caller shows nothing unverified."""


@dataclass
class Verdict:
    index: int
    supported: bool
    why: str


def premises(item: dict, answer: Answer) -> list[int]:
    """Indexes into `answer.retrieved` a sentence is judged against: the chunks it cites, and every other retrieved
    page of an opinion it cites (your pinpoint policy, F0: a wrong page is not a wrong source)."""
    hits = answer.retrieved
    cited = [i for i, h in enumerate(hits) if h.citation in item["citations"]]
    opinions = {section_of(hits[i].citation) for i in cited if OPINION_RE.search(hits[i].citation)}
    pages = [i for i, h in enumerate(hits) if OPINION_RE.search(h.citation) and section_of(h.citation) in opinions]
    return list(dict.fromkeys(cited + pages))


def prompt(question: str, answer: Answer, items: list[dict]) -> str:
    used = sorted({i for item in items for i in premises(item, answer)})
    num = {i: n + 1 for n, i in enumerate(used)}
    sources = "\n\n".join(f"Source {num[i]}: [{answer.retrieved[i].citation}] ({answer.retrieved[i].heading})\n"
                          f"{answer.retrieved[i].text}" for i in used)
    claims = "\n".join(f"{k}. {item['text']} (cites: {', '.join(f'Source {num[i]}' for i in premises(item, answer))})"
                       for k, item in enumerate(items))
    return (f"Question: {question}\n\nThe answer (context only; judge the numbered claims):\n{answer.text}\n\n"
            f"Sources:\n\n{sources}\n\nClaims:\n{claims}")


def _json(system: str, prompt: str, model: str, schema: dict) -> tuple[dict, int, int]:
    raw, tin, tout = call_model(system, prompt, model, json_schema=schema)
    try:
        return json.loads(raw), tin, tout
    except (json.JSONDecodeError, TypeError) as e:
        raise VerificationFailed(f"unusable verifier response: {raw[:120]!r}") from e


def verify(question: str, answer: Answer, model: str = VERIFIER,
           items: list[dict] | None = None) -> tuple[list[Verdict], int, int]:
    """(one verdict per shown sentence, input tokens, output tokens). One call for the whole answer (ADR-10's
    batching). A sentence the verifier skipped is unsupported: silence is not support."""
    items = cited_items(answer.structured["data"]) if items is None else items
    if not items:
        return [], 0, 0
    raw, tin, tout = call_model(SYSTEM, prompt(question, answer, items), model, json_schema=SCHEMA)
    try:
        given = {v["index"]: v for v in json.loads(raw)["verdicts"] if isinstance(v, dict) and "index" in v}
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        raise VerificationFailed(f"unusable verifier response: {raw[:120]!r}") from e
    return [Verdict(k, bool(given.get(k, {}).get("supported")), str(given.get(k, {}).get("why", "no verdict returned")))
            for k in range(len(items))], tin, tout


def recite(question: str, answer: Answer, items: list[dict], failed: list[int],
           model: str = VERIFIER) -> tuple[dict[int, str], int, int]:
    """{item index: the retrieved citation that states it} for failed items, from one call over every retrieved
    source. A pick that is out of range or already cited is ignored; the caller re-checks every swap."""
    hits = answer.retrieved
    sources = "\n\n".join(f"Source {n + 1}: [{h.citation}] ({h.heading})\n{h.text}" for n, h in enumerate(hits))
    claims = "\n".join(f"{n}. {items[k]['text']} (cited: {', '.join(items[k]['citations'])})" for n, k in enumerate(failed))
    data, tin, tout = _json(RECITE_SYSTEM, f"Question: {question}\n\nSources:\n\n{sources}\n\nClaims:\n{claims}",
                            model, RECITE_SCHEMA)
    picks = {}
    for r in data.get("recites") or []:
        n, src = r.get("index"), r.get("source")
        if isinstance(n, int) and 0 <= n < len(failed) and isinstance(src, int) and 1 <= src <= len(hits):
            if hits[src - 1].citation not in items[failed[n]]["citations"]:
                picks[failed[n]] = hits[src - 1].citation
    return picks, tin, tout


def conclude(question: str, conclusion: str, kept: list[dict], model: str = VERIFIER) -> tuple[list[str] | None, str, int, int]:
    """(citations to show the conclusion with, or None if it doesn't follow; why; tokens). Its citations are those of
    the passed sentences it rests on, so it is shown cited and can't outlive a hidden premise."""
    statements = "\n".join(f"{n}. {item['text']}" for n, item in enumerate(kept))
    data, tin, tout = _json(CONCLUSION_SYSTEM, f"Question: {question}\n\nVerified statements:\n{statements}\n\n"
                                               f"Conclusion: {conclusion}", model, CONCLUSION_SCHEMA)
    basis = [n for n in data.get("basis") or [] if isinstance(n, int) and 0 <= n < len(kept)]
    if not data.get("follows") or not basis:
        return None, str(data.get("why", "")), tin, tout
    return list(dict.fromkeys(c for n in basis for c in kept[n]["citations"])), str(data.get("why", "")), tin, tout


def with_conclusion(text: str, conclusion: str, cites: list[str]) -> str:
    """The conclusion first ("Short answer: ..."), after the tax-year line if there is one."""
    line = f"Short answer: {conclusion.strip().rstrip('.')} {', '.join(f'[{c}]' for c in cites)}."
    year, sep, rest = text.partition("\n\n") if text.startswith("Tax year:") else ("", "", text)
    return f"{year}{sep}{line}\n\n{rest}"


def apply(answer: Answer, verdicts: list[Verdict], unit: str = HIDE) -> Answer:
    """The answer as shown: failed sentences hidden, and with `unit="part"` the rest of their part too. A part left
    with nothing shown says INSUFFICIENT EVIDENCE; the text is re-rendered from what survives."""
    if unit not in ("part", "sentence"):
        raise ValueError(f"unit must be 'part' or 'sentence', not {unit!r}")
    data, labels = answer.structured["data"], answer.structured["labels"]
    items = cited_items(data)
    failed = {v.index for v in verdicts if not v.supported}
    failed_parts = {items[k]["part"] for k in failed}
    hide = {k for k, item in enumerate(items) if k in failed or (unit == "part" and item["part"] in failed_parts)}
    kept = [item for k, item in enumerate(items) if k not in hide]
    emptied = {items[k]["part"] for k in hide} - {item["part"] for item in kept}
    notes = [m for m in data.get("not_answerable") or [] if m.get("part") not in emptied]
    notes += [{"part": p, "why": "no statement in this part could be verified against its sources."} for p in sorted(emptied, key=str)]
    text, _ = render({**data, "sentences": kept, "not_answerable": notes}, labels)
    exact, derived, invented = parse_citations(text, answer.retrieved)
    why = {v.index: v.why for v in verdicts}
    return replace(answer, text=text, citations=exact, derived_citations=derived, unsupported_citations=invented,
                   hidden=[{**items[k], "failed": k in failed, "why": why.get(k, "")} for k in sorted(hide)])


def checked(question: str, answer: Answer, unit: str = HIDE, model: str = VERIFIER) -> Answer:
    """Verify, then hide. Fails closed: any error in verification shows nothing unverified."""
    if answer.structured is None or answer.refused:
        return answer  # nothing was rendered from items (a refusal, or an unusable synthesis response)
    try:
        verdicts, tin, tout = verify(question, answer, model)
        items = cited_items(answer.structured["data"])
        failed = [v.index for v in verdicts if not v.supported]
        if RECITE and failed:  # C3: swap to the retrieved source that states it, then re-check the swap as usual
            picks, i2, o2 = recite(question, answer, items, failed, model)
            swapped = [{**items[k], "citations": [picks[k]], "recited_from": items[k]["citations"]} for k in picks]
            again, i3, o3 = verify(question, answer, model, swapped) if swapped else ([], 0, 0)
            tin, tout = tin + i2 + i3, tout + o2 + o3
            for k, v in zip(picks, again):
                if v.supported:
                    items[k] = swapped[list(picks).index(k)]
                    verdicts[k] = Verdict(k, True, f"re-cited: {v.why}")
            answer = replace(answer, structured={**answer.structured,
                                                 "data": {**answer.structured["data"], "sentences": items}})
        shown = apply(answer, verdicts, unit)
        conclusion = str(answer.structured["data"].get("conclusion") or "").strip()
        kept = [item for v, item in zip(verdicts, items) if v.supported]
        extra = {}
        if conclusion and kept and not shown.refused:  # C2
            cites, why, i4, o4 = conclude(question, conclusion, kept, model)
            tin, tout = tin + i4, tout + o4
            extra = {"conclusion": {"text": conclusion, "shown": cites is not None, "citations": cites or [], "why": why}}
            if cites:
                text = with_conclusion(shown.text, conclusion, cites)
                exact, derived, invented = parse_citations(text, answer.retrieved)
                shown = replace(shown, text=text, citations=exact, derived_citations=derived, unsupported_citations=invented)
    except Exception as e:  # noqa: BLE001  any failure, API or parse, must not let an unverified claim through
        return replace(answer, text=UNVERIFIED, citations=[], derived_citations=[], unsupported_citations=[],
                       hidden=[{**item, "failed": False, "why": f"verification failed: {e}"[:200]}
                               for item in cited_items(answer.structured["data"])], verifier=model)
    return replace(shown, verifier=model, verify_input_tokens=tin, verify_output_tokens=tout,
                   verdicts=[asdict(v) for v in verdicts], **extra)
