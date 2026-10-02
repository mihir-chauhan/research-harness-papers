"""Figures from results/runs.jsonl and results/raw/curve_*.csv."""
import json, glob, collections, re
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
TASKS = ["perm_dil", "split_cil", "split_til"]
import sys; sys.path.insert(0, "experiments")
from registry import active_runs
runs = active_runs()
def agg(group, name, key, task, metric="average_accuracy"):
    d = collections.defaultdict(list)
    for r in runs:
        if r["group"] == group and r["task"] == task and r["name"] == name:
            d[r["config"][key]].append(r["metrics"][metric])
    ks = sorted(d); return ks, np.array([np.mean(d[k]) for k in ks]), np.array([np.std(d[k], ddof=1) for k in ks])
joint = {t: np.mean([r["metrics"]["average_accuracy"] for r in runs if r["group"] == "main" and r["name"] == "Joint training" and r["task"] == t]) for t in TASKS}
fig, ax = plt.subplots(2, 3, figsize=(7.2, 3.9), sharey="col")
for j, t in enumerate(TASKS):
    for i, (g, nm, key, lab, c) in enumerate([("sweep_buffer", "Experience replay", "buffer", "replay buffer size M", "#1f77b4"), ("sweep_lambda", "EWC", "lam", r"EWC strength $\lambda$", "#d95f02")]):
        ks, m, s = agg(g, nm, key, t); x = np.arange(len(ks))
        a = ax[i, j]
        a.errorbar(x, m, s, marker="o", ms=3, color=c, capsize=2)
        a.axhline(joint[t], ls="--", color="gray", lw=0.8)
        a.set_xticks(x); a.set_xticklabels([f"{k:g}" for k in ks], rotation=45, fontsize=7)
        a.set_xlabel(lab); a.set_ylim(0, 1.02)
        if j == 0: a.set_ylabel("final average accuracy")
        if i == 0: a.set_title(t)
fig.tight_layout(); fig.savefig("results/figures/sweeps_buffer_lambda.pdf")
# per-stage mean accuracy on seen tasks
lab = {"Fine-tuning": "finetune", "EWC": "ewc", "Joint training": "joint", "Experience replay (M=20)": "M20", "Experience replay (M=100)": "M100"}
fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.3), sharey=True)
files = glob.glob("results/raw/curve_main_*.csv")
for r in runs:
    pass
cols = {"Fine-tuning": "k", "EWC": "#d95f02", "Joint training": "gray", "Experience replay (M=20)": "#9ecae1", "Experience replay (M=100)": "#1f77b4"}
for j, t in enumerate(TASKS):
    for nm, c in cols.items():
        dfs = []
        for f in files:
            m = re.match(r"results/raw/curve_main_(.+?)_(.*)_(perm_dil|split_cil|split_til)_(\d+)\.csv", f)
            if m.group(3) == t and m.group(1) == nm.replace(" ", ""):
                dfs.append(pd.read_csv(f))
        d = pd.concat(dfs).groupby("step").value.agg(["mean", "std"])
        ax[j].errorbar(d.index, d["mean"], d["std"], label=nm, color=c, marker="o", ms=3, capsize=2)
    ax[j].set_title(t); ax[j].set_xlabel("tasks learned"); ax[j].set_xticks(range(1, 6))
ax[0].set_ylabel("mean accuracy on seen tasks"); ax[0].legend(fontsize=6)
fig.tight_layout(); fig.savefig("results/figures/curves_main.pdf")

# sweep table: mean +- std over 5 seeds, from the run registry
def cell(g, nm, key, t, k, metric):
    v = [r["metrics"][metric] for r in runs if r["group"] == g and r["name"] == nm and r["task"] == t and r["config"][key] == k]
    assert len(v) == 5
    return f"{np.mean(v):.3f} $\\pm$ {np.std(v, ddof=1):.3f}"
rows = []
hdr = "Setting & " + " & ".join(f"{t.replace('_', chr(92) + '_')} acc" for t in TASKS) + " & " + " & ".join(f"{t.replace('_', chr(92) + '_')} forg" for t in TASKS) + r" \\"
out = [r"\begin{tabular}{lcccccc}", r"\toprule", hdr, r"\midrule"]
for g, nm, key, sym, ks in [("sweep_buffer", "Experience replay", "buffer", "M", [0, 5, 10, 20, 50, 100, 200, 500]), ("sweep_lambda", "EWC", "lam", r"\lambda", [0, 1, 10, 100, 1000, 10000, 100000])]:
    for k in ks:
        out.append(f"${sym}={k}$ & " + " & ".join(cell(g, nm, key, t, k, "average_accuracy") for t in TASKS) + " & " + " & ".join(cell(g, nm, key, t, k, "forgetting") for t in TASKS) + r" \\")
    if sym == "M": out.append(r"\midrule")
out += [r"\bottomrule", r"\end{tabular}"]
open("results/tables/sweep_both.tex", "w").write("\n".join(out) + "\n")
