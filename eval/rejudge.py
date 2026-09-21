"""Re-grade stored answers without regenerating them (judging is the cheap half).

    uv run python eval/rejudge.py eval/results/llm_bench-2026-09-21.json

Exists because a judge design can be wrong while the answers are fine: the first
reliability check used a stricter second rubric and produced a false kappa of 0.65
(log #31). Re-judging 72 stored answers cost $0.02; regenerating them would not have
been free, and would have changed the thing being measured.
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from llm_bench import JUDGE_FOR, cost_of, judge  # noqa: E402

load_dotenv()

path = Path(sys.argv[1])
data = json.loads(path.read_text())
pilot = {json.loads(l)["id"]: json.loads(l) for l in open("eval/pilot.jsonl") if l.strip()}

spend = 0.0
for r in data["rows"]:
    if "grade" not in r:
        continue
    q = pilot[r["id"]]
    jm = JUDGE_FOR[r["model"]]
    b = judge(q["question"], q["answer"], r["text"], jm, alt=True)
    spend += cost_of(jm, b["in"], b["out"])
    r["grade2"], r["judge2"] = b["grade"], "alt-phrasing"
    print(f"  {r['model']:<17}{r['mode']:<12}{r['id']}  {r['grade']:<9}| {b['grade']}", flush=True)

data["rejudge_spend"] = spend
path.write_text(json.dumps(data, indent=2))
print(f"\nre-judged {sum('grade' in r for r in data['rows'])} answers for ${spend:.3f}")