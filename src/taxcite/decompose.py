"""Split a question into typed sub-queries, and route each to the sources that can answer it.

Phase A searched the whole corpus with the questioner's own words. Growing the corpus
broke that twice (B2, B3): a compound question contains almost none of the vocabulary
its sources use, and 10k chunks of case-law prose bury regulations on any question that
sounds like a dispute (pilot Recall@10 0.667 -> 0.500, log #38). B6 then showed the
bottleneck is first-stage recall, not ranking: 47% of golden gold never reaches the top
25 candidates, so no reranker can save it (ADR-19).

Decomposition attacks both. One structured-output call plans the searches: what kinds of
authority the answer needs, which facts the questioner supplied, and what year it is about.
Each kind is then searched separately, filtered to the corpora that hold it, and the union
is reranked back down to k.

What the plan is used for is narrower than it first looks. B7 measured the model's rewritten
sub-query text against the questioner's own words and the rewriting lost (dev Recall@10 0.542
vs 0.708, log #44), so the searches use the original question and the model is trusted only
for the routing. `retrieve(rewrite=True)` keeps the other arm of that measurement runnable.
"""

import json
from collections.abc import Sequence
from dataclasses import dataclass, field

from taxcite.generate import MODEL, call_model, cost
from taxcite.retrieve import RERANK_MODEL, Hit, rerank, search

# Which sources each kind of sub-query may search. () means never searched; None means
# every source, which is Phase A's behaviour and what the fallback falls back to.
ROUTES: dict[str, tuple[str, ...] | None] = {
    "statutory": ("usc", "ecfr", "irs_pub"),
    "case_law": ("case",),
    "client_fact": (),
    "unrouted": None,
}
MODEL_KINDS = ("statutory", "case_law", "client_fact")  # "unrouted" is ours, not the model's
MAX_SUBQUERIES = 4
SEED = 0  # best-effort determinism; temperature 0 alone re-planned a dev question between runs

SYSTEM = """You plan the searches needed to answer a US federal tax question.

Return JSON only, in this shape:
{"as_of": "2023" or null, "subqueries": [{"kind": "statutory", "query": "..."}]}

"as_of" is the tax year or date the question is about, if it names or implies one.

"kind" is one of:
  "statutory"   - the rule itself: Internal Revenue Code, Treasury regulations, IRS publications.
  "case_law"    - how courts have applied the rule: US Tax Court opinions.
  "client_fact" - a fact about the questioner's client that changes the answer. It is never
                  searched, it is handed to the answer step, so write the fact itself here
                  rather than a search for it.

Rules:
- Write each query in the vocabulary of the source, not of the questioner: "suspension of
  miscellaneous itemized deductions for taxable years after 2017", not "can they deduct this".
- Every sub-query must be one the final answer will cite. Searches compete for a fixed number
  of results, so one that only provides background makes the answer worse, not better.
- Every question needs at least one "statutory" sub-query. Whether it also needs case law is
  one test: **would the answer have to say how a court ruled?**
    * No, if the answer can be stated from the text of the Code, a regulation or an IRS
      publication alone -- a dollar limit, a percentage, a deadline, a definition, an
      election, a mechanical computation. Then do not add a "case_law" sub-query, even when
      the question is phrased as a client's problem, and even when it sounds contentious.
    * Yes, if the rule turns on judgment a court applies to facts: whether an activity is a
      trade or business or engaged in for profit, whether an expense is ordinary and necessary,
      reasonableness, substance over form, whether particular records or facts were adequate --
      or if the question asks in so many words what courts have held.
    * If you genuinely cannot tell, include both: a kind you leave out cannot be recovered later.
- Most questions need one or two sub-queries; never more than four. Do not pad.
- Never invent a section number you are unsure of. Describe the rule instead.

Example 1 (needs both: the rule, and how courts weigh it)
Question: My client breeds horses at a loss and also works full time. Can he deduct the losses?
{"as_of": null,
 "subqueries": [
   {"kind": "statutory", "query": "activity not engaged in for profit deduction limitation"},
   {"kind": "case_law", "query": "horse breeding profit objective nine factors full-time employment"},
   {"kind": "client_fact", "query": "the client works full time outside the activity"}]}

Example 2 (asks what courts have done: case law only)
Question: Are toll and parking receipts on a spreadsheet enough to substantiate travel expenses?
{"as_of": null,
 "subqueries": [
   {"kind": "case_law", "query": "adequacy of taxpayer-prepared records tolls parking substantiation of travel expenses"}]}

Example 3 (a client's problem, but the answer is a figure in the Code: statute only)
Question: My client is 52 and put $8,000 into a traditional IRA this year. How much can they deduct?
{"as_of": null,
 "subqueries": [
   {"kind": "statutory", "query": "deduction limit for contributions to a traditional individual retirement account, catch-up for age 50"},
   {"kind": "client_fact", "query": "the client is 52 and contributed $8,000"}]}

Example 4 (asks what the rule is: statute only)
Question: What is the standard mileage rate a self-employed client can deduct?
{"as_of": null,
 "subqueries": [
   {"kind": "statutory", "query": "standard mileage rate for business use of an automobile"}]}"""


@dataclass
class SubQuery:
    kind: str
    query: str
    hits: list[Hit] = field(default_factory=list)

    @property
    def sources(self) -> tuple[str, ...] | None:
        return ROUTES[self.kind]

    @property
    def searchable(self) -> bool:
        return self.kind != "client_fact"


@dataclass
class Decomposition:
    question: str
    subqueries: list[SubQuery]
    as_of: str | None = None
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    fallback: str = ""  # set when the model's plan was unusable and we searched as Phase A did

    @property
    def searched(self) -> list[SubQuery]:
        return [s for s in self.subqueries if s.searchable]

    @property
    def facts(self) -> list[str]:
        return [s.query for s in self.subqueries if s.kind == "client_fact"]

    @property
    def cost_usd(self) -> float:
        return cost(self.model, self.input_tokens, self.output_tokens)

    def groups(self, keep: set[str] | None = None) -> list[tuple[str, list[Hit]]]:
        """(sub-query, its chunks) for the synthesis prompt, limited to `keep` if given.

        `keep` is the set of citations that survived reranking: synthesis sees the same k
        chunks the eval scores, still labelled with the sub-query that found them.
        """
        return [(s.query, [h for h in s.hits if keep is None or h.citation in keep])
                for s in self.searched]


def parse(text: str, question: str) -> tuple[list[SubQuery], str | None, str]:
    """(sub-queries, as_of, fallback reason). Never raises.

    A decomposition that cannot be used must degrade to the one search Phase A would
    have run, not fail a query the corpus can answer. JSON mode guarantees valid JSON,
    not a valid plan, so the shape is checked field by field.
    """
    plan = [SubQuery("unrouted", question)]
    try:
        data = json.loads(text)
        raw = data["subqueries"]
    except (json.JSONDecodeError, TypeError, KeyError):
        return plan, None, "unparseable"
    if not isinstance(raw, list):
        return plan, None, "subqueries is not a list"

    as_of = data.get("as_of")
    as_of = str(as_of) if as_of not in (None, "") else None
    subs = [
        SubQuery(s["kind"], str(s["query"]).strip())
        for s in raw
        if isinstance(s, dict) and s.get("kind") in MODEL_KINDS and str(s.get("query", "")).strip()
    ][:MAX_SUBQUERIES]
    if not any(s.searchable for s in subs):  # client facts alone cannot answer anything
        return plan, as_of, "no searchable sub-query"
    return subs, as_of, ""


def decompose(question: str, model: str = MODEL) -> Decomposition:
    """One structured-output call (ADR-11). Temperature 0 and a fixed seed, so a re-run
    of the eval measures the change under test and not a different plan."""
    text, tin, tout = call_model(SYSTEM, f"Question: {question}", model,
                                 temperature=0, json_output=True, seed=SEED)
    subs, as_of, fallback = parse(text, question)
    return Decomposition(question=question, subqueries=subs, as_of=as_of, model=model,
                         input_tokens=tin, output_tokens=tout, fallback=fallback)


def retrieve(d: Decomposition, k: int = 8, mode: str = "hybrid", route: bool = True,
             rewrite: bool = False) -> Decomposition:
    """Search once per sub-query, filtered to the sources its kind allows. Fills `hits` in place.

    The search text is the **original question**, not the model's rewritten sub-query,
    because that is what measured better: on the dev set, routing the question itself to
    each corpus scored Recall@10 0.708 against 0.542 for the rewritten text, and the
    rewrite lost hits the questioner's own words had found (log #44). What the model is
    trusted for is the routing -- which corpora this question needs -- not the wording.
    `rewrite` and `route` exist so the eval can take either half away.
    """
    seen: dict[tuple, list[Hit]] = {}  # two sub-queries of one kind would repeat a search
    for s in d.searched:
        key = (s.query if rewrite else d.question, s.sources if route else None)
        if key not in seen:
            seen[key] = search(key[0], k=k, mode=mode, source=key[1])
        s.hits = seen[key]
    return d


def chunks(d: Decomposition, k: int, rerank_model: str = RERANK_MODEL, floor: int = 1) -> list[Hit]:
    """The k chunks synthesis sees: every sub-query's hits, ordered by the cross-encoder.

    B6 shelved reranking because 47% of golden gold never reached the candidate pool, so
    there was nothing for it to reorder (ADR-19). Routing is what fills the pool; the
    reranker is what turns the union back into a ranked list of k, since fused scores from
    differently-filtered searches are not comparable with each other.

    `floor` reserves that many slots for each sub-query before the rest are filled by score.
    Routing gets a corpus into the pool; without a floor the reranker can still take it back
    out. On a question asking in so many words for the Code, the regulation and the case law,
    the cross-encoder filled all ten slots with court prose and both statutory sub-queries
    reached synthesis empty. A floor of 1 fixes that and is neutral on every dev metric
    (identical Recall/nDCG/MRR at floors 0-3), so it buys answer composition for nothing.
    """
    ranked = rerank(d.question, merge(d.searched, None), 10**6, rerank_model)
    chosen: dict[str, Hit] = {}
    for s in d.searched:
        own = {h.citation for h in s.hits}
        for h in [x for x in ranked if x.citation in own][:floor]:
            chosen.setdefault(h.citation, h)
    for h in ranked:  # the rest by cross-encoder score
        if len(chosen) >= k:
            break
        chosen.setdefault(h.citation, h)
    return sorted(chosen.values(), key=lambda h: -h.score)[:k]


def merge(subqueries: Sequence[SubQuery], k: int | None) -> list[Hit]:
    """One ranked list of k, round-robin across sub-queries, first occurrence wins.

    Round-robin rather than by score: fused scores from differently-filtered searches are
    not comparable, and a compound question needs every part represented at the top of the
    context, not the loudest part filling it.

    `k` None keeps every hit: each sub-query holds its own depth and synthesis sees more
    chunks. That is a different trade (context and tokens) from the same k split n ways,
    so the eval reports both.
    """
    out: dict[str, Hit] = {}
    for rank in range(max((len(s.hits) for s in subqueries), default=0)):
        for s in subqueries:
            if rank < len(s.hits):
                out.setdefault(s.hits[rank].citation, s.hits[rank])
                if len(out) == k:
                    return list(out.values())
    return list(out.values())


def answer(question: str, k: int = 8, mode: str = "hybrid", model: str = MODEL,
           route: bool = True, plan: Decomposition | None = None) -> tuple[Decomposition, "object"]:
    """Decompose, retrieve per sub-query, synthesize over the grouped sources.

    `plan` supplies the decomposition instead of making a fresh one. An eval needs that: the
    planner is not deterministic, and on the golden set 16% of questions get routed differently
    between runs, which moved faithfulness by sd 0.030 until this was wired up (log #49).
    """
    from taxcite.generate import answer_from_groups

    d = retrieve(plan or decompose(question, model=model), k=k, mode=mode, route=route)
    kept = {h.citation for h in chunks(d, k)}
    return d, answer_from_groups(question, d.groups(kept), facts=d.facts, model=model)