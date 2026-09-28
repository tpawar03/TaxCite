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
import re
from datetime import date
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field, replace
from functools import cache

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

"as_of" is the tax year whose rules the answer depends on: the year of the return or of the
transaction, not the date of a later event such as filing, a refund claim, an audit or a levy.
Resolve "this year", "last year's return" and the like from today's date, and use today's date
for nothing else: a present-tense question that names no year ("are meals deductible?") is null. If the question asks
about two tax years, give both ("2016 and 2026"). If it names or implies none, null.

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
    statute_floor: int = 0  # set by retrieve (D3b): slots `chunks` reserves for the statute

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
    # today's date resolves a relative year ("this year's return"); without it the model guessed 2023 (D2)
    text, tin, tout = call_model(SYSTEM, f"Today's date: {date.today():%B %d, %Y}\nQuestion: {question}", model,
                                 temperature=0, json_output=True, seed=SEED)
    subs, as_of, fallback = parse(text, question)
    return Decomposition(question=question, subqueries=subs, as_of=as_of, model=model,
                         input_tokens=tin, output_tokens=tout, fallback=fallback)


def neighbors(edges: Iterable[tuple[str, str]], seeds: set[str], hops: int, held: set[str]) -> set[str]:
    """Held opinions within `hops` citation steps of the seeds, in either direction; the seeds themselves
    excluded. A hop may pass through an opinion we don't hold (co-citation), as C0 measured."""
    near: dict[str, set[str]] = {}
    for a, b in edges:
        near.setdefault(a, set()).add(b)
        near.setdefault(b, set()).add(a)
    reached, frontier = set(seeds), set(seeds)
    for _ in range(hops):
        frontier = {n for o in frontier for n in near.get(o, ())} - reached
        reached |= frontier
    return (reached - seeds) & held


@cache
def citation_graph() -> tuple[frozenset, frozenset]:
    """(edges, held opinions), loaded once: 5,278 edges is small enough to walk in memory (ADR-23)."""
    from taxcite import store
    with store.connect() as conn:
        edges = frozenset(conn.execute("SELECT citing, cited FROM citations").fetchall())
        held = frozenset(r[0] for r in conn.execute(
            "SELECT DISTINCT section FROM chunks WHERE source = 'case' AND excluded IS NULL"))
    return edges, held


# D3's edition window, chosen on dev recall: (1, 0), a dated question sees its own year's edition and
# the one before (a 2025 edition states 2026's mileage rate); dev temporal Recall@20 0.423 -> 0.577.
# Off in the live pipeline: on dev *answers* it cost 0.36-0.43 -> 0.29, because removing the 2025
# editions removed the only plain-English year evidence (D30's "new for 2025", D32's retroactive
# $20,000) and synthesis fell back on today's statute and stale memory. D7 re-decides with D3b and D4.
EDITIONS: tuple[int, int] | None = None

# D3b, chosen on dev: each statutory sub-query also searches the statute alone, and one slot is
# reserved for it. Dev Recall@20 0.605 -> 0.724 (statutory 0.654 -> 0.808, temporal 0.423 -> 0.615,
# case law and compound unchanged); floors of 1, 2 and 3 scored the same at k=20 and at k=8.
STATUTE = 1


def tax_year(as_of: str | None) -> int | None:
    """The plan's one tax year, or None: no year, or several ("2016 and 2026"), filter nothing."""
    years = re.findall(r"\b(?:19|20)\d\d\b", as_of or "")
    return int(years[0]) if len(set(years)) == 1 else None


def retrieve(d: Decomposition, k: int = 8, mode: str = "hybrid", route: bool = True,
             rewrite: bool = False, hops: int = 0, editions: tuple[int, int] | None = None,
             statute: int = 0, union: bool = False) -> Decomposition:
    """Search once per sub-query, filtered to the sources its kind allows. Fills `hits` in place.

    The search text is the **original question**, not the model's rewritten sub-query,
    because that is what measured better: on the dev set, routing the question itself to
    each corpus scored Recall@10 0.708 against 0.542 for the rewritten text, and the
    rewrite lost hits the questioner's own words had found (log #44). What the model is
    trusted for is the routing -- which corpora this question needs -- not the wording.
    `rewrite` and `route` exist so the eval can take either half away.

    `hops` > 0 expands each case-law sub-query along the citation graph: one more search, limited to
    the held opinions within that many citation steps of the ones already found, joins its pool, and
    the reranker decides. Off by default: C0 measured its ceiling on the golden set at zero (ADR-1),
    and it stays as an ablation rung so the ladder shows that with a number, not a claim (C5).

    `statute` > 0 adds a statute-only search to each statutory sub-query and has `chunks` reserve
    that many slots for the statute (D3b): the question's plain words find publications first, and
    searched within the statute alone they reach 0.68 of dev's statute gold at k=20. `union` also
    searches the sub-query's own text and pools both (D3b's second candidate).
    """
    seen: dict[tuple, list[Hit]] = {}  # two sub-queries of one kind would repeat a search
    year = tax_year(d.as_of) if editions is not None else None
    dated = {"year": year, "editions": editions} if year is not None else {}  # D3's edition filter
    for s in d.searched:
        key = (s.query if rewrite else d.question, s.sources if route else None)
        if key not in seen:
            seen[key] = search(key[0], k=k, mode=mode, source=key[1], **dated)
        s.hits = seen[key]
        extra = []
        if union and not rewrite:
            extra += search(s.query, k=k, mode=mode, source=key[1], **dated)
        if statute and s.kind == "statutory" and route:
            extra += search(key[0], k=k, mode=mode, source="usc")
        if extra:
            own = {h.key or h.citation for h in s.hits}
            s.hits = list(s.hits)  # the search result may be shared with another sub-query (`seen`)
            for h in extra:
                if (h.key or h.citation) not in own:
                    own.add(h.key or h.citation)
                    s.hits.append(h)
    d.statute_floor = statute
    if hops:
        edges, held = citation_graph()
        for s in (s for s in d.searched if s.kind == "case_law"):
            near = neighbors(edges, {h.section for h in s.hits if h.source == "case"}, hops, held)
            own = {h.citation for h in s.hits}
            if near:
                s.hits = s.hits + [h for h in search(d.question, k=k, mode=mode, source="case", sections=near)
                                   if h.citation not in own]
    return d


def level(h: Hit, statute_first: bool = False, demote_prior: bool = False) -> float:
    """A hit's authority level (E2's profile; 0 when it has none), with E4's two variants: the statute a
    half-level above regulations, and an earlier regime's "…A" regulation a quarter-level below final."""
    a = h.authority or {}
    return (a.get("level", 0) + (0.5 if statute_first and a.get("type") == "statute" else 0)
            - (0.25 if demote_prior and a.get("status") == "final_prior_version" else 0))


def weigh(ranked: list[Hit], how: dict) -> list[Hit]:
    """E4's reorderings of the cross-encoder's list by authority. Nothing is dropped.

    `how["rule"]`: "prior" adds w × (level − 1) to the score; "tie" lets a higher level pass a lower one
    whose score is within `delta`. The new order is given the old scores, highest first, so `chunks`'
    final sort by score keeps it. `scoped` does this within each kind of source (statutory: statute,
    regulation, publication; case law: opinions) and hands each kind back its own scores, so the
    cross-kind order the cross-encoder chose, statute against opinion, is untouched (E1's guards).
    """
    lvl = lambda h: level(h, how.get("statute_first", False), how.get("demote_prior", False))  # noqa: E731

    def order(hs: list[Hit]) -> list[Hit]:
        if how["rule"] == "prior":
            return sorted(hs, key=lambda h: (-(h.score + how["w"] * (lvl(h) - 1)), h.citation))
        out, moved = list(hs), True
        while moved:  # terminates: a swap only ever moves a strictly higher level forward
            moved = False
            for i in range(len(out) - 1):
                if out[i].score - out[i + 1].score < how["delta"] and lvl(out[i + 1]) > lvl(out[i]):
                    out[i], out[i + 1], moved = out[i + 1], out[i], True
        return out

    def rescore(hs: list[Hit]) -> list[Hit]:
        return [replace(h, score=s) for h, s in zip(order(hs), sorted((h.score for h in hs), reverse=True))]

    if not how.get("scoped"):
        return rescore(ranked)
    out = [h for kind in ("statutory", "case") for h in rescore([x for x in ranked if ("case" if x.source == "case" else "statutory") == kind])]
    return sorted(out, key=lambda h: (-h.score, h.citation))


def chunks(d: Decomposition, k: int, rerank_model: str = RERANK_MODEL, floor: int = 1,
           authority: dict | None = None) -> list[Hit]:
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

    `authority` (E4, off unless given): {"rule": "prior"|"tie", ...} reorders by `weigh`; {"slot": True}
    lets the statute slots also take a final regulation.
    """
    ranked = rerank(d.question, merge(d.searched, None), 10**6, rerank_model)
    if authority and authority.get("rule"):
        ranked = weigh(ranked, authority)
    slot = ((lambda h: h.source == "usc" or (h.authority or {}).get("status") == "final")
            if authority and authority.get("slot") else (lambda h: h.source == "usc"))
    chosen: dict[str, Hit] = {}
    for s in d.searched:
        own = {h.citation for h in s.hits}
        for h in [x for x in ranked if x.citation in own][:floor]:
            chosen.setdefault(h.citation, h)
    for h in [x for x in ranked if slot(x)][:d.statute_floor]:  # D3b's statute slots (E4: or a final regulation)
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

    d = retrieve(plan or decompose(question, model=model), k=k, mode=mode, route=route, editions=EDITIONS,
                 statute=STATUTE)
    kept = {h.citation for h in chunks(d, k)}
    return d, answer_from_groups(question, d.groups(kept), facts=d.facts, model=model, as_of=d.as_of)