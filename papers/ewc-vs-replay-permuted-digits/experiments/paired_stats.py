"""Paired differences between systems of the main group (seeds 0-4), from results/runs.jsonl.
For each scenario and pair: mean difference a-b, its sample std, the 95% t-interval (4 d.o.f.) and the paired
t-test p-value. Auxiliary analysis only: the paper quotes no number from this script. Its differences and p-values
are the \rhval{cmp/...} values that `rh compare` records with Experience replay (M=100) as reference.
Usage: $PY experiments/paired_stats.py [metric] > results/tables/paired_main_<metric>.txt
"""
import json, sys, itertools
import numpy as np
from scipy import stats
metric = sys.argv[1] if len(sys.argv) > 1 else "average_accuracy"
SYSTEMS = ["Fine-tuning", "EWC", "Experience replay (M=20)", "Experience replay (M=100)", "Joint training"]
sys.path.insert(0, "experiments")
from registry import active_runs
rows = [r for r in active_runs() if r["group"] == "main"]
print(f"metric: {metric}; paired over seeds 0-4; difference = a - b")
print(f"{'scenario':10s} {'a':26s} {'b':26s} {'mean_a':>7s} {'mean_b':>7s} {'diff':>7s} {'sd':>6s} {'ci95_lo':>8s} {'ci95_hi':>8s} {'paired_p':>9s}")
for task in ["perm_dil", "split_cil", "split_til"]:
    v = {s: {r["seed"]: r["metrics"][metric] for r in rows if r["task"] == task and r["name"] == s} for s in SYSTEMS}
    for b, a in itertools.combinations(SYSTEMS, 2):
        seeds = sorted(v[a]); assert seeds == sorted(v[b]) == [0, 1, 2, 3, 4]
        xa, xb = np.array([v[a][s] for s in seeds]), np.array([v[b][s] for s in seeds])
        d = xa - xb; n = len(d); sd = d.std(ddof=1)
        h = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
        p = stats.ttest_rel(xa, xb).pvalue
        print(f"{task:10s} {a:26s} {b:26s} {xa.mean():7.3f} {xb.mean():7.3f} {d.mean():7.3f} {sd:6.3f} {d.mean() - h:8.3f} {d.mean() + h:8.3f} {p:9.2e}")
