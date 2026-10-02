"""Paired differences between systems of the main group (seeds 0-4), from results/runs.jsonl.
For each scenario and pair: mean difference a-b, its sample std, the 95% t-interval (4 d.o.f.) and the paired
t-test p-value. `rh compare` gives the same p-values but no interval, so the intervals quoted in the paper come from here.
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
SHORT = {"Fine-tuning": "FT", "EWC": "EWC", "Experience replay (M=20)": "ER20", "Experience replay (M=100)": "ER100", "Joint training": "Joint"}
PAPER = {("perm_dil", "ER100", "EWC"), ("perm_dil", "ER20", "EWC"), ("perm_dil", "Joint", "ER100"),
         ("split_cil", "EWC", "FT"), ("split_cil", "ER100", "FT"), ("split_cil", "ER100", "EWC"), ("split_cil", "Joint", "ER100"),
         ("split_til", "Joint", "FT"), ("split_til", "ER100", "FT"), ("split_til", "ER100", "EWC"), ("split_til", "Joint", "EWC"), ("split_til", "Joint", "ER100")}
tex = [r"\begin{tabular}{llccc}", r"\toprule", r"Scenario & Pair ($a-b$) & Diff. & 95\% CI & $p$ \\", r"\midrule"]
def sci(p):
    if p >= 0.001: return f"{p:.3f}"
    m, e = f"{p:.1e}".split("e"); return f"${m}{{\\times}}10^{{{int(e)}}}$"
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
        if (task, SHORT[a], SHORT[b]) in PAPER:
            tex.append(f"{task.replace('_', chr(92) + '_')} & {SHORT[a]} $-$ {SHORT[b]} & {d.mean():.3f} & [{d.mean() - h:.3f}, {d.mean() + h:.3f}] & {sci(p)} \\\\".replace("-0.", "$-$0."))
    if task != "split_til": tex.append(r"\midrule")
if metric == "average_accuracy":
    open("results/tables/paired_main.tex", "w").write("\n".join(tex + [r"\bottomrule", r"\end{tabular}"]) + "\n")
