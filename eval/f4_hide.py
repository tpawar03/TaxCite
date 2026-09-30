"""F4: one verified run, shown three ways, so the hiding unit is decided on identical verdicts.

    uv run python eval/temporal.py --questions eval/dev.jsonl --rows all --samples 3 \\
        --plan-cache eval/results/decompositions-d7.json --answers-cache eval/results/temporal-answers-f4.json
    uv run python eval/f4_hide.py --answers eval/results/temporal-answers-f4.json
    uv run python eval/temporal.py ... --answers-cache eval/results/temporal-answers-f4-{none,part,sentence}.json

The verified run stores each answer's structured items and verdicts (ragas_eval.pipeline_answer). This writes three
answer caches from it: "none" (every item shown, as if unverified), "part" (a failed sentence hides its part, ADR-15
as written) and "sentence" (only the failed sentence goes). temporal.py grades each: a complete cache makes no new
synthesis, so the three differ only in what is shown. Also writes the hiding metrics and a sheet of ~30 verdicts to
read by hand.
"""

import argparse
import json
import random
from pathlib import Path

from taxcite import verify
from taxcite.generate import Answer, cited_items, citations, render, section_of
from taxcite.retrieve import Hit

RESULTS = Path("eval/results")
UNITS = ("none", "part", "sentence")


def base(entry: dict) -> Answer:
    """The cached answer as the verifier saw it: every cited item shown."""
    s = entry["structured"]
    text, _ = render(s["data"], s["labels"])
    hits = [Hit(citation=c["citation"], heading=c.get("heading", ""), text=c["text"], score=0.0,
                section=section_of(c["citation"]), source="") for c in entry["contexts"]]
    return Answer(text=text, mode="rag", model=entry.get("model", ""), retrieved=hits, structured=s,
                  citations=citations(text))


def shown(entry: dict, unit: str) -> dict:
    """The cache entry as `unit` would show it."""
    if not entry.get("structured") or not entry.get("verdicts"):
        return dict(entry)  # a refusal, or nothing to hide
    answer = base(entry)
    if unit != "none":
        answer = verify.apply(answer, [verify.Verdict(**v) for v in entry["verdicts"]], unit)
    return {**entry, "text": answer.text, "refused": answer.refused, "citations": answer.citations,
            "hidden": answer.hidden}


def metrics(cache: dict, unit: str) -> dict:
    entries = [e for runs in cache.values() for e in runs]
    views = [(e, shown(e, unit)) for e in entries]
    live = [(e, v) for e, v in views if not shown(e, "none")["refused"]]
    sentences = sum(len(cited_items(e["structured"]["data"])) for e, _ in live if e.get("structured"))
    return {"answers": len(entries), "answered_unverified": len(live), "sentences": sentences,
            "sentences_hidden": sum(len(v.get("hidden") or []) for _, v in live),
            "answers_shown_whole": sum(not v.get("hidden") for _, v in live),
            "answers_with_a_part_shown": sum(not v["refused"] for _, v in live),
            "answers_emptied": sum(v["refused"] for _, v in live)}


def check_sheet(cache: dict, path: Path, n: int = 30, seed: int = 0) -> None:
    """Half failed, half passed verdicts, one per answer; the verdict under a fold, read the sources first."""
    rng = random.Random(seed)
    pool = []
    for q, runs in cache.items():
        for r, e in enumerate(runs):
            if e.get("structured") and e.get("verdicts"):
                items = cited_items(e["structured"]["data"])
                for v in e["verdicts"]:
                    pool.append((q, r, e, items[v["index"]], v))
    rng.shuffle(pool)
    picked, seen = [], set()
    for want in (False, True):
        for q, r, e, item, v in pool:
            if len([p for p in picked if p[4]["supported"] is want]) == n // 2:
                break
            if v["supported"] is want and (q, r) not in seen:
                picked.append((q, r, e, item, v))
                seen.add((q, r))
    rng.shuffle(picked)
    lines = ["# F4 verdict check", "", "Does the cited source (or another retrieved page of the same opinion) state the "
             "sentence, or does it follow directly (arithmetic included)? The question's client facts count as given. "
             "Write `yes` or `no` after **Your verdict:**.", ""]
    for k, (q, r, e, item, v) in enumerate(picked, 1):
        answer = base(e)
        lines += [f"## V{k:02d}", "", f"**Question:** {q}", "", f"**Sentence:** {item['text']}", ""]
        for i in verify.premises(item, answer):
            h = answer.retrieved[i]
            lines += [f"**Source [{h.citation}]**", "", "> " + h.text[:3000].replace("\n", "\n> "), ""]
        lines += ["**Your verdict:** ", "", f"<details><summary>Verifier</summary>"
                  f"{'supported' if v['supported'] else 'NOT supported'}: {v['why']}</details>", "", "---", ""]
    path.write_text("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", required=True, help="a verified run's answer cache")
    args = ap.parse_args()
    src = Path(args.answers)
    cache = json.loads(src.read_text())
    out = {}
    for unit in UNITS:
        view = {q: [shown(e, unit) for e in runs] for q, runs in cache.items()}
        (src.parent / f"{src.stem}-{unit}.json").write_text(json.dumps(view, indent=1))
        out[unit] = metrics(cache, unit)
        print(f"{unit:<9} {json.dumps(out[unit])}")
    (RESULTS / f"f4-hide-{src.stem}.json").write_text(json.dumps(out, indent=2))
    sheet = RESULTS / "f4-verdict-check.md"
    if not sheet.exists():  # never overwrite verdicts written into it
        check_sheet(cache, sheet)
        print(f"wrote {sheet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
