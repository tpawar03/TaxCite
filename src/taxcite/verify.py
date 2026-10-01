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


def verify(question: str, answer: Answer, model: str = VERIFIER) -> tuple[list[Verdict], int, int]:
    """(one verdict per shown sentence, input tokens, output tokens). One call for the whole answer (ADR-10's
    batching). A sentence the verifier skipped is unsupported: silence is not support."""
    items = cited_items(answer.structured["data"])
    if not items:
        return [], 0, 0
    raw, tin, tout = call_model(SYSTEM, prompt(question, answer, items), model, json_schema=SCHEMA)
    try:
        given = {v["index"]: v for v in json.loads(raw)["verdicts"] if isinstance(v, dict) and "index" in v}
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        raise VerificationFailed(f"unusable verifier response: {raw[:120]!r}") from e
    return [Verdict(k, bool(given.get(k, {}).get("supported")), str(given.get(k, {}).get("why", "no verdict returned")))
            for k in range(len(items))], tin, tout


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
    emptied = {items[k]["part"] for k in hide} - {item["part"] for item in kept} - {0}  # a hidden bottom line just goes
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
    except Exception as e:  # noqa: BLE001  any failure, API or parse, must not let an unverified claim through
        return replace(answer, text=UNVERIFIED, citations=[], derived_citations=[], unsupported_citations=[],
                       hidden=[{**item, "failed": False, "why": f"verification failed: {e}"[:200]}
                               for item in cited_items(answer.structured["data"])], verifier=model)
    return replace(apply(answer, verdicts, unit), verifier=model, verify_input_tokens=tin, verify_output_tokens=tout,
                   verdicts=[asdict(v) for v in verdicts])
