"""Builds the custom figures and the sensitivity table strictly from results/runs.jsonl."""
import json, collections, numpy as np
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

rows = [json.loads(l) for l in open("results/runs.jsonl")]
rows = [r for r in rows if r["status"] == "ok"]
def get(group, name, task, metric, cfgkey=None, cfgval=None):
    d = {}
    for r in rows:
        if r["group"] == group and r["name"] == name and r["task"] == task:
            if cfgkey is not None and r["config"].get(cfgkey) != cfgval: continue
            d[r["seed"]] = r["metrics"][metric]
    return d
tasks = ["digits_noise20", "digits_noise40", "digits_noise60"]
names = ["Label smoothing", "Mixup", "Small-loss (1 net)"]
short = {"Label smoothing": "LS", "Mixup": "Mixup", "Small-loss (1 net)": "Small-loss"}

# The paired table (differences to CE, p-values) is no longer built here: the paper takes those values
# from the registry comparison (`rh compare --group main --metric test_acc|mem_rate --ref CE`) via \rhval.

# fig 1: test acc and mem_rate vs noise
noise = [0, 20, 40, 60]
sysn = ["CE", "Label smoothing", "Mixup", "Small-loss (1 net)"]
fig, ax = plt.subplots(1, 2, figsize=(7, 2.8))
for n, mk in zip(sysn, "osv^"):
    for k, m in enumerate(["test_acc", "mem_rate"]):
        mu = []; sd = []
        for z in noise:
            v = list(get("main", n, f"digits_noise{z}", m).values()); mu.append(np.mean(v)); sd.append(np.std(v, ddof=1))
        ax[k].errorbar(noise, mu, yerr=sd, marker=mk, label=n, capsize=2, lw=1.2, ms=4)
ax[0].set_ylabel("clean test accuracy"); ax[1].set_ylabel("mem_rate")
for a in ax: a.set_xlabel("symmetric noise rate (%)"); a.set_xticks(noise); a.grid(alpha=.3)
ax[0].legend(fontsize=7); plt.tight_layout(); plt.savefig("results/figures/noise_curves.pdf"); plt.close()

# fig 2: sensitivity sweeps at 40% noise (default setting from main, marked)
fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.7))
specs = [("sweep_mixup_alpha", "Mixup", "mix_alpha", 1.0, "mixup $\\alpha$", True),
         ("sweep_ls_eps", "Label smoothing", "ls_eps", 0.1, "LS $\\epsilon$", True),
         ("sweep_sl_rate", "Small-loss (1 net)", "sl_rate", 0.4, "assumed forget rate", False)]
t = "digits_noise40"
for a, (g, n, key, dflt, lab, logx) in zip(ax, specs):
    pts = collections.defaultdict(list)
    for r in rows:
        if r["group"] == g: pts[r["config"][key]].append(r["metrics"]["test_acc"])
    pts[dflt] = list(get("main", n, t, "test_acc").values())
    xs = sorted(pts); mu = [np.mean(pts[x]) for x in xs]; sd = [np.std(pts[x], ddof=1) for x in xs]
    a.errorbar(xs, mu, yerr=sd, marker="o", ms=4, capsize=2, lw=1.2)
    a.plot([dflt], [np.mean(pts[dflt])], "o", ms=9, mfc="none", mec="k")
    ce = np.mean(list(get("main", "CE", t, "test_acc").values())); a.axhline(ce, ls="--", c="gray", lw=1)
    if logx: a.set_xscale("log"); a.set_xticks(xs); a.set_xticklabels([f"{x:g}" for x in xs], fontsize=6); a.minorticks_off()
    else: a.set_xticks(xs)
    a.set_xlabel(lab); a.grid(alpha=.3)
ax[0].set_ylabel("test acc @ 40% noise"); 
plt.tight_layout(); plt.savefig("results/figures/sweeps.pdf"); plt.close()

# sensitivity table (40% noise); main-setting rows come from group main, others from sweep groups
T = "digits_noise40"
def cell(v): return f"{np.mean(v):.3f}$\\pm${np.std(v, ddof=1):.3f}"
L = [r"\begin{tabular}{llccc}", r"\toprule", r"System & Setting & test\_acc & mem\_rate & mem\_gap \\", r"\midrule"]
def block(label, name, key, dflt, grp, fmt, extra=None):
    pts = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        if r["group"] == grp:
            for m in ("test_acc", "mem_rate", "mem_gap"): pts[r["config"][key]][m].append(r["metrics"][m])
    for m in ("test_acc", "mem_rate", "mem_gap"): pts[dflt][m] = list(get("main", name, T, m).values())
    for v in sorted(pts):
        tag = fmt(v) + (" (main)" if v == dflt else "")
        L.append(f"{label} & {tag} & " + " & ".join(cell(pts[v][m]) for m in ("test_acc", "mem_rate", "mem_gap")) + r" \\")
    L.append(r"\midrule")
block("Mixup", "Mixup", "mix_alpha", 1.0, "sweep_mixup_alpha", lambda v: f"$\\alpha$={v:g}")
block("LS", "Label smoothing", "ls_eps", 0.1, "sweep_ls_eps", lambda v: f"$\\epsilon$={v:g}")
block("Small-loss", "Small-loss (1 net)", "sl_rate", 0.4, "sweep_sl_rate", lambda v: f"rate={v:g}")
nw = {m: [r["metrics"][m] for r in rows if r["group"] == "abl_smallloss"] for m in ("test_acc", "mem_rate", "mem_gap")}
L.append("Small-loss & no warm-up/ramp, rate=0.4 & " + " & ".join(cell(nw[m]) for m in nw) + r" \\")
L += [r"\bottomrule", r"\end{tabular}"]
open("results/tables/sensitivity.tex", "w").write("\n".join(L) + "\n")
open("results/tables/sensitivity.md", "w").write("\n".join(L) + "\n")
print("ok")
