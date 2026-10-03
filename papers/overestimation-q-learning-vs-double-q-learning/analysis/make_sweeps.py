"""Aggregate sweep groups from results/runs.jsonl into tables + figures; log the aggregates as run metrics."""
import json, sys, glob, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out_json = sys.argv[1]
rows = [json.loads(l) for l in open("results/runs.jsonl")]
rows = [r for r in rows if r.get("status") == "ok" and r["kind"] != "sanity"]
SYS = {"Q-learning": "q", "Double Q-learning": "double", "Weighted Double Q-learning": "wdq", "Maxmin Q-learning": "maxmin"}
metrics = {}

def vals(group, task, name, metric, cfgkey=None, cfgval=None):
    v = []
    for r in rows:
        if r["group"] == group and r["task"] == task and r["name"] == name:
            if cfgkey is not None and r["config"].get(cfgkey) != cfgval:
                continue
            v.append(r["metrics"][metric])
    return v

def cell(group, task, name, metric, key, val, default_group="main"):
    """mean over seeds; the default setting comes from the main group."""
    if val is None:
        v = vals(default_group, task, name, metric)
    else:
        v = vals(group, task, name, metric, key, val)
    assert len(v) == 5, (group, task, name, metric, key, val, len(v))
    return float(np.mean(v))

def f(x):
    return f"{x:.3f}"

colors = {"Q-learning": "#d95f02", "Double Q-learning": "#1b9e77", "Weighted Double Q-learning": "#7570b3", "Maxmin Q-learning": "#666666"}
fig, axs = plt.subplots(1, 4, figsize=(11, 2.6))
lines = []
sweeps = [("sweep_sigma", "sigma", [0.25, 1.0, 2.0, 4.0], 1.0, r"noise $\sigma$"),
          ("sweep_eps", "epsilon", [0.1, 0.3, 1.0], 0.1, r"exploration $\epsilon$"),
          ("sweep_alpha", "alpha", [0.02, 0.05, 0.1, 0.2], 0.1, r"step size $\alpha$")]
lines.append(r"\begin{tabular}{llrrrrrr}\hline")
lines.append(r"Sweep & value & $\hat V$-bias Q & $\hat V$-bias DQ & $\hat Q$-bias Q & $\hat Q$-bias DQ & subopt Q & subopt DQ \\\hline")
for si, (grp, key, values, default, label) in enumerate(sweeps):
    ser = {"Q-learning": [], "Double Q-learning": []}
    for v in values:
        vv = None if v == default else v
        r = [key if v == values[0] else "", str(v)]
        for met in ["bias_final", "qbias_final", "subopt_all"]:
            for nm in ["Q-learning", "Double Q-learning"]:
                x = cell(grp, "random20", nm, met, key, vv)
                metrics[f"{key}_{str(v).replace('.', 'p')}_{SYS[nm]}_{met}"] = x
                r.append(f(x))
                if met == "bias_final":
                    ser[nm].append(x)
        lines.append(" & ".join(r) + r" \\")
    lines.append(r"\hline")
    ax = axs[si]
    for nm, ys in ser.items():
        ax.plot(range(len(values)), ys, "o-", color=colors[nm], label=nm)
    ax.set_xticks(range(len(values))); ax.set_xticklabels([str(v) for v in values])
    ax.set_xlabel(label); ax.axhline(0, color="k", lw=0.5)
    if si == 0:
        ax.set_ylabel("random20: final start-state\nestimated minus true")
lines[-1] = r"\hline\end{tabular}"
open("results/tables/sweeps_random.tex", "w").write("\n".join(lines) + "\n")

# action sweep (maxbias), all four systems
acts = [2, 5, 10, 25, 100]
L = [r"\begin{tabular}{rrrrrrrrr}\hline",
     r" & \multicolumn{4}{c}{start-state peak bias} & \multicolumn{4}{c}{suboptimal fraction} \\",
     r"$n$ & Q & DQ & WDQ & MM & Q & DQ & WDQ & MM \\\hline"]
ser = {n: [] for n in SYS}
for n in acts:
    vv = None if n == 10 else n
    r = [str(n)]
    for met in ["bias_peak", "subopt_all"]:
        for nm in SYS:
            x = cell("sweep_actions", "maxbias", nm, met, "n_actions", vv)
            metrics[f"actions_{n}_{SYS[nm]}_{met}"] = x
            r.append(f(x))
            if met == "bias_peak":
                ser[nm].append(x)
    L.append(" & ".join(r) + r" \\")
L.append(r"\hline\end{tabular}")
open("results/tables/sweeps_actions.tex", "w").write("\n".join(L) + "\n")
ax = axs[3]
for nm, ys in ser.items():
    ax.plot(range(len(acts)), ys, "o-", color=colors[nm], label=nm)
ax.set_xticks(range(len(acts))); ax.set_xticklabels([str(n) for n in acts])
ax.set_xlabel("maxbias: actions $n$ at state B"); ax.set_ylabel("peak start-state\nestimated minus true")
axs[0].legend(fontsize=6, frameon=False)
fig.tight_layout()
fig.savefig("results/figures/sweeps.pdf")

# learning curves from the per-run curve files (mean over seeds)
fig, axs = plt.subplots(2, 2, figsize=(7.2, 4.6))
for ci, task in enumerate(["maxbias", "random20"]):
    for nm, k in SYS.items():
        for ri, pref in enumerate(["curve", "curvesub"]):
            fs = sorted(glob.glob(f"results/raw/{pref}_main_{task}_{k}_s*.csv"))
            assert len(fs) == 5, (pref, task, k, len(fs))
            arr = np.array([np.loadtxt(x, delimiter=",", skiprows=1, usecols=(0, 1)) for x in fs])
            xs, ys = arr[0, :, 0], arr[:, :, 1].mean(0)
            axs[ri, ci].plot(xs, ys, color=colors[nm], label=nm, lw=1.2)
            if pref == "curve":
                metrics[f"curve_{task}_{k}_ep10"] = float(ys[9])
    axs[0, ci].set_title(task)
    axs[0, ci].axhline(0, color="k", lw=0.5)
    axs[1, ci].set_xlabel("episode")
axs[0, 0].set_ylabel("start-state est. minus true")
axs[1, 0].set_ylabel("fraction suboptimal actions")
axs[0, 1].set_ylim(-4, 0.5)
axs[0, 0].legend(fontsize=6, frameon=False)
fig.tight_layout()
fig.savefig("results/figures/curves_main.pdf")
json.dump(metrics, open(out_json, "w"))
print("config: sweeps from runs.jsonl main/sweep_*; 5 seeds each")
print("metrics:", len(metrics), "values")
