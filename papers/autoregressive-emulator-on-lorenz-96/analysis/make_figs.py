"""Figures from results/raw lead-curve CSVs (written by the runs) and results/runs.jsonl."""
import glob, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 8, "axes.grid": True, "grid.alpha": .25})
DT = 0.05
SYS = [("persistence", "Persistence", "#999999", ":"), ("climatology", "Climatology", "#444444", "--"),
       ("linear", "Linear stencil", "#8c6d31", "-."), ("K1", "CNN K=1", "#1f77b4", "-"),
       ("K4", "CNN K=4", "#d62728", "-"), ("K8", "CNN K=8", "#2ca02c", "-")]
fig, ax = plt.subplots(1, 2, figsize=(7, 2.6))
for tag, lab, c, ls in SYS:
    for j, kind in enumerate(["rmse", "acc"]):
        fs = sorted(glob.glob(f"results/raw/leadcurve_{kind}_main_{tag}_s*.csv"))
        if not fs: continue
        a = np.stack([pd.read_csv(f).value.values for f in fs])
        x = np.arange(a.shape[1]) * DT
        ax[j].plot(x, a.mean(0), c=c, ls=ls, label=lab, lw=1.3)
        ax[j].fill_between(x, a.min(0), a.max(0), color=c, alpha=.15, lw=0)
ax[0].set_xlabel("lead time (model time units)"); ax[0].set_ylabel("RMSE"); ax[0].set_yscale("log")
ax[1].axhline(.6, c="k", lw=.5); ax[1].set_xlabel("lead time (model time units)"); ax[1].set_ylabel("ACC")
ax[0].legend(frameon=False, fontsize=6.5)
plt.tight_layout(); plt.savefig("results/figures/lead_curves.pdf"); plt.close()

rows = [json.loads(l) for l in open("results/runs.jsonl")]
df = pd.DataFrame([{**r["metrics"], "name": r["name"], "group": r["group"], "seed": r["seed"]} for r in rows if r["status"] == "ok"])
def k_of(n): return int(n.split("K=")[1].split()[0])
sel = df[df.name.str.startswith("CNN K=") & ~df.name.str.contains("noise|ntrain")]
fig, ax = plt.subplots(1, 3, figsize=(7, 2.3))
for a, (m, lab) in zip(ax, [("rmse_1step", "1-step RMSE"), ("rmse_t20", "RMSE at lead 2.0"), ("acc_leadtime", "ACC lead time (>0.6)")]):
    sel2 = sel.assign(K=sel.name.map(k_of))
    for s, g in sel2.groupby("seed"):
        g = g.sort_values("K"); a.plot(g.K, g[m], c="#bbbbbb", lw=.7, marker=".", ms=3)
    g = sel2.groupby("K")[m].mean(); a.plot(g.index, g.values, c="#d62728", marker="o", ms=4, lw=1.5)
    a.set_xscale("log", base=2); a.set_xticks([1, 2, 4, 8]); a.set_xticklabels(["1", "2", "4", "8"])
    a.set_xlabel("training rollout K"); a.set_ylabel(lab)
plt.tight_layout(); plt.savefig("results/figures/sweep_K_panels.pdf"); plt.close()
print("figures written")
