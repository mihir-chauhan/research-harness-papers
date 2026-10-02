"""Paired (same seed = same test targets) differences between systems logged in different groups; two-sided paired t-test."""
import json, os, numpy as np
from scipy import stats
rows = [json.loads(l) for l in open("results/runs.jsonl")]
def get(g, n, m):
    d = {r["seed"]: r["metrics"][m] for r in rows if r["group"] == g and r["name"] == n}
    return d
AR = ("main", "Conditional AR designer")
OTH = {"salog": ("extra_sa_log", "SA graded objective"), "salogw": ("extra_sa_log", "SA graded objective, heuristic init"),
       "sawarm": ("extra_sa_warm", "SA from contact heuristic"), "heur": ("main", "Contact heuristic")}
out = {}
for tag, (g, n) in OTH.items():
    for k in (1, 10, 100, 1000):
        a = get(*AR, f"succ_k{k}"); b = get(g, n, f"succ_k{k}")
        seeds = sorted(set(a) & set(b)); x = np.array([a[s] for s in seeds]); y = np.array([b[s] for s in seeds])
        out[f"ar_vs_{tag}_k{k}_delta"] = float((x - y).mean())
        out[f"ar_vs_{tag}_k{k}_p"] = float(stats.ttest_rel(x, y).pvalue) if np.any(x != y) else 1.0
        out[f"ar_vs_{tag}_k{k}_n"] = len(seeds)
print(json.dumps(out, indent=0))
json.dump(out, open(os.environ["RH_METRICS_FILE"], "w"))
