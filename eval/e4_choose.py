"""E4: apply the dev rules as written in tasks/todo.md, before looking at which arm wins.

    uv run python eval/e4_choose.py eval/results/retrieval-dev-2026-09-28-k8-e4-arms-exact.json \
        eval/results/retrieval-dev-2026-09-28-k20-e4-arms-exact.json

1. break no dev guard (all 8 still top-1 in every plan set) and keep every `keep` source in the top 8 (k=8)
2. Recall@20 regression <= 2 points in every dev category (mean over plan sets) vs the shipped arm
3. among those, the most conflict rows at target (k=8, mean over plan sets); ties to the simpler arm:
   slot < tie < prior; scoped < flat; no deep search < deep search
"""
import json
import statistics
import sys

K8 = json.load(open(sys.argv[1]))
K20 = json.load(open(sys.argv[2]))
BASE = "hybrid+route+statute1"


def simplicity(arm: str) -> tuple:
    kind = 0 if "slot" in arm else 1 if "tie" in arm else 2 if "prior" in arm else 3 if "deep" in arm else -1
    return (kind, "flat" in arm, "deep" in arm)


rows = []
for arm in K8["authority"]:
    a = K8["authority"][arm]
    guards_ok = all(v == a["guard_rows"] for v in a["guards_kept"]) and all(v == a["keep_rows"] for v in a["keep_sources_kept"])
    base_cat, cat = K20["recall_per_plan_set_by_category"][BASE], K20["recall_per_plan_set_by_category"][arm]
    worst = min(statistics.mean(cat[c]) - statistics.mean(base_cat[c]) for c in cat)
    at = statistics.mean(a["conflict_at_target"])
    rows.append((arm, guards_ok, worst, at, min(a["guards_kept"]), statistics.mean(K20["recall_per_plan_set"][arm])))

print(f"{'arm':44} {'guards+keep ok':>14} {'worst cat dR@20':>16} {'conflict@target':>16} {'min guards':>11} {'R@20':>7}")
for arm, ok, worst, at, g, r in sorted(rows, key=lambda x: -x[3]):
    print(f"{arm:44} {str(ok):>14} {worst:>+16.3f} {at:>16.2f} {g:>11} {r:>7.3f}")
eligible = [r for r in rows if r[1] and r[2] >= -0.02 and r[0] != BASE]
base_at = next(r[3] for r in rows if r[0] == BASE)
eligible = [r for r in eligible if r[3] > base_at]
if not eligible:
    print("\nNO ARM passes rules 1-2 and beats the shipped arm: E4 ships nothing")
else:
    best = max(r[3] for r in eligible)
    choice = min((r for r in eligible if r[3] == best), key=lambda r: simplicity(r[0]))
    print(f"\nchosen: {choice[0]} (conflict rows at target {choice[3]:.2f} vs {base_at:.2f} shipped; worst category {choice[2]:+.3f})")