"""Figures and derived tables, read only from results/runs.jsonl."""
import json, numpy as np, collections
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = [json.loads(l) for l in open("results/runs.jsonl")]
R = [r for r in R if r["status"] == "ok" and r["group"] != "tune"]

def get(group, name, metric, cond=lambda c: True, seeds=None):
    v = {r["seed"]: r["metrics"][metric] for r in R if r["group"] == group and r["name"] == name and cond(r["config"])}
    return np.array([v[s] for s in sorted(v) if seeds is None or s in seeds])

COL = {"FNO": "#1f77b4", "DeepONet": "#d95f02", "MLP": "#7570b3", "CNN": "#1b9e77"}
# Fig 1: resolution transfer
fig, ax = plt.subplots(figsize=(3.4, 2.5))
sysn = ["FNO", "DeepONet", "MLP", "CNN"]; w = 0.2
for i, s in enumerate(sysn):
    for j, (m, lab) in enumerate([("rel_l2", "128"), ("rel_l2_256", "256"), ("rel_l2_512", "512")]):
        v = get("main", s, m)
        ax.bar(j + (i - 1.5) * w, v.mean(), w, yerr=v.std(ddof=1), color=COL[s], label=s if j == 0 else None, capsize=1.5, error_kw={"lw": .7})
ax.set_yscale("log"); ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["128 (train)", "256 (zero-shot)", "512 (zero-shot)"], fontsize=7)
ax.set_ylabel("test relative $L_2$", fontsize=8); ax.tick_params(labelsize=7); ax.legend(fontsize=6, ncol=2, frameon=False, loc="upper left")
ax.set_ylim(top=3)
fig.tight_layout(); fig.savefig("results/figures/resolution_transfer.pdf"); plt.close(fig)

# Fig 2: sweeps
fig, axs = plt.subplots(1, 2, figsize=(3.4, 2.3))
S3 = {0, 1, 2}
ms = [4, 8, 16, 32]
vals = [get("sweep_modes", f"FNO modes={m}", "rel_l2") if m != 16 else get("main", "FNO", "rel_l2", seeds=S3) for m in ms]
axs[0].errorbar(ms, [v.mean() for v in vals], [v.std(ddof=1) for v in vals], marker="o", ms=3, color=COL["FNO"], capsize=2, lw=1)
axs[0].set_xscale("log", base=2); axs[0].set_yscale("log"); axs[0].set_xticks(ms); axs[0].set_xticklabels(ms)
axs[0].set_xlabel("Fourier modes", fontsize=8); axs[0].set_ylabel("test relative $L_2$", fontsize=8)
ns = [100, 200, 400]
for s, tag in [("FNO", "FNO n={}"), ("DeepONet", "DeepONet n={}")]:
    vals = [get("sweep_ntrain", tag.format(n), "rel_l2") if n != 400 else get("main", s, "rel_l2", seeds=S3) for n in ns]
    axs[1].errorbar(ns, [v.mean() for v in vals], [v.std(ddof=1) for v in vals], marker="o", ms=3, color=COL[s], label=s, capsize=2, lw=1)
axs[1].set_xscale("log"); axs[1].set_yscale("log"); axs[1].set_xticks(ns); axs[1].set_xticklabels(ns); axs[1].minorticks_off()
axs[1].set_xlabel("training pairs", fontsize=8); axs[1].legend(fontsize=6, frameon=False)
for a in axs: a.tick_params(labelsize=7)
fig.tight_layout(); fig.savefig("results/figures/sweeps.pdf"); plt.close(fig)

def ms_(v): return f"{v.mean():.4f} $\\pm$ {v.std(ddof=1):.4f}"
# Zero-shot ratios and the ablation summary are no longer written here: a ratio or a p-value computed in this script
# cannot be traced by `rh numbers`. The ablation table in paper/sections/ablations.tex is built from \rhval keys
# (`rh agg` statistics and `rh compare --group <sweep> --ref <default>`).

# Main table with readable headers (same registry rows and the same means/stds as `rh table --group main --prec 4`)
with open("results/tables/maintab.tex", "w") as f:
    f.write("\\begin{tabular}{lcccccrr}\n\\toprule\nSystem & test 128 & train 128 & test 256 & test 512 & rs256 & params & time (s) \\\\\n\\midrule\n")
    for s in sysn:
        c = [ms_(get("main", s, m)) for m in ("rel_l2", "train_rel_l2", "rel_l2_256", "rel_l2_512", "rel_l2_256_resamp")]
        npar = get("main", s, "params"); t = get("main", s, "train_s"); assert len(set(npar)) == 1 and len(t) == 5
        f.write(f"{s} & " + " & ".join(c) + f" & {int(npar[0])}" + f" & {t.mean():.1f} $\\pm$ {t.std(ddof=1):.1f} \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")

# Learning-rate tuning table (group tune, seed 100, validation rel. L2; successful runs only)
T = [json.loads(l) for l in open("results/runs.jsonl")]
T = [r for r in T if r["group"] == "tune" and r["status"] == "ok"]
lrs = [3e-4, 1e-3, 3e-3, 1e-2]; lab = ["$3\\!\\times\\!10^{-4}$", "$10^{-3}$", "$3\\!\\times\\!10^{-3}$", "$10^{-2}$"]
with open("results/tables/tune.tex", "w") as f:
    f.write("\\begin{tabular}{lcccc}\n\\toprule\nSystem & " + " & ".join(lab) + " \\\\\n\\midrule\n")
    for s in sysn:
        v = {}
        for r in T:
            if r["name"] == "tune-" + s.lower():
                assert r["config"]["lr"] not in v; v[r["config"]["lr"]] = r["metrics"]["rel_l2_val"]
        best = min(v, key=v.get)
        f.write(f"{s} & " + " & ".join((f"\\textbf{{{v[l]:.4f}}}" if l == best else f"{v[l]:.4f}") for l in lrs) + " \\\\\n")
        print("tune", s, v)
    f.write("\\bottomrule\n\\end{tabular}\n")

# train/test gap
for s in sysn:
    print(s, "train", get("main", s, "train_rel_l2").mean(), "test", get("main", s, "rel_l2").mean())

# H1 table from rh compare output (Welch, FNO vs baseline), plus relative gap to the best baseline
import csv
cmp_ = list(csv.DictReader(open("results/tables/compare_main_rel_l2.csv")))
with open("results/tables/h1.tex", "w") as f:
    f.write("\\begin{tabular}{lrrrr}\n\\toprule\nBaseline & mean & FNO gain & Welch $p$ & Cohen $d$ \\\\\n\\midrule\n")
    for r in cmp_:
        m, ref = float(r["mean"]), float(r["ref_mean"])
        f.write(f"{r['name']} & {m:.4f} & {100*(1-ref/m):.1f}\\% & {float(r['welch_p']):.1e} & {abs(float(r['cohen_d'])):.1f} \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")
