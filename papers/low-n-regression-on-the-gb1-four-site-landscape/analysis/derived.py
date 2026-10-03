"""Derived analyses computed from results/runs.jsonl (latest ok row per (group, name, task, seed)).
Writes: flat metrics JSON (--out), LaTeX tables and a learning-curve figure."""
import argparse, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
rows = {}
for l in open("results/runs.jsonl"):
    d = json.loads(l)
    if d.get("status") == "ok" and d.get("kind") in ("method", "baseline", "ablation") and d["group"] in ("main", "sweep_alpha", "abl_logtarget", "abl_cnn"):
        cfg = json.dumps(d.get("config") or {}, sort_keys=True) if d["group"] == "sweep_alpha" else "{}"
        rows[(d["group"], d["name"], d["task"], d["seed"], cfg)] = d["metrics"]
SYS = {"ridge": "One-hot ridge (reimplemented)", "pairwise": "One-hot + pairwise ridge",
       "gp": "GP Hamming kernel (reimplemented)", "cnn": "CNN (reimplemented)"}
LAB = {"ridge": "One-hot ridge", "pairwise": "Pairwise ridge", "gp": "GP", "cnn": "CNN"}
NS = [48, 96, 384, 2000]
def get(group, name, task, metric, cfg="{}"):
    v = [rows[(group, name, task, s, cfg)][metric] for s in range(5) if (group, name, task, s, cfg) in rows]
    assert len(v) == 5, (group, name, task, len(v))
    return np.array(v)

out = {}
# rand vs dbl at fixed Hamming distance of the test variants (difference of seed means; std of per-seed differences)
tex = ["\\begin{tabular}{llrrrr}", "\\toprule", "System & Test HD & N=48 & N=96 & N=384 & N=2000 \\\\", "\\midrule"]
for s in SYS:
    for hd in (3, 4):
        cells = []
        for n in NS:
            r = get("main", SYS[s], f"rand_{n}", f"spearman_hd{hd}"); d = get("main", SYS[s], f"dbl_{n}", f"spearman_hd{hd}")
            out[f"gap_hd{hd}_{s}_{n}"] = float(r.mean() - d.mean())
            cells.append(f"{r.mean()-d.mean():+.3f}")
        tex.append(f"{LAB[s]} & {hd} & " + " & ".join(cells) + " \\\\")
tex += ["\\bottomrule", "\\end{tabular}"]
open("results/tables/gap_hd.tex", "w").write("\n".join(tex) + "\n")

# alpha sweep at rand_384
ALPHAS = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
tex = ["\\begin{tabular}{lrrrrrrrr}", "\\toprule", "System & $10^{-3}$ & $10^{-2}$ & $10^{-1}$ & $1$ & $10$ & $10^2$ & $10^3$ & CV \\\\", "\\midrule"]
for s in ("ridge", "pairwise"):
    nm = "One-hot ridge fixed alpha" if s == "ridge" else "One-hot + pairwise ridge fixed alpha"
    cells = []
    for al in ALPHAS:
        v = get("sweep_alpha", nm, "rand_384", "spearman", json.dumps({"alpha": al}, sort_keys=True))
        out[f"alpha_{s}_{al}_mean"] = float(v.mean()); out[f"alpha_{s}_{al}_std"] = float(v.std(ddof=1))
        cells.append(f"{v.mean():.3f}")
    cv = get("main", SYS[s], "rand_384", "spearman")
    out[f"alpha_{s}_cv_mean"] = float(cv.mean())
    tex.append(f"{LAB[s]} & " + " & ".join(cells) + f" & {cv.mean():.3f} \\\\")
tex += ["\\bottomrule", "\\end{tabular}"]
open("results/tables/alpha_sweep.tex", "w").write("\n".join(tex) + "\n")

# learning curves
fig, ax = plt.subplots(2, 2, figsize=(7, 5), sharex=True)
col = {"ridge": "#1f77b4", "pairwise": "#d62728", "gp": "#2ca02c", "cnn": "#9467bd"}
for j, reg in enumerate(("rand", "dbl")):
    for i, (m, lab) in enumerate((("spearman", "Spearman"), ("top100_recall", "top-100 recall"))):
        for s in SYS:
            mu = [get("main", SYS[s], f"{reg}_{n}", m).mean() for n in NS]
            sd = [get("main", SYS[s], f"{reg}_{n}", m).std(ddof=1) for n in NS]
            ax[i, j].errorbar(NS, mu, yerr=sd, label=LAB[s], color=col[s], marker="o", capsize=2, lw=1.2, ms=3)
        ax[i, j].set_xscale("log"); ax[i, j].set_ylabel(lab); ax[i, j].set_title(f"{reg} training"); ax[i, j].grid(alpha=.3)
for j in range(2): ax[1, j].set_xlabel("N (training variants)")
ax[0, 0].legend(fontsize=7)
plt.tight_layout(); plt.savefig("results/figures/learning_curves.pdf"); plt.close()
# default vs log-target training (rand), both from logged runs
LOGN = {"ridge": ("abl_logtarget", "One-hot ridge log target"), "pairwise": ("abl_logtarget", "One-hot + pairwise ridge log target"),
        "gp": ("abl_logtarget", "GP log target"), "cnn": ("abl_cnn", "CNN log target")}
fig, ax = plt.subplots(figsize=(3.5, 2.6))
for s in SYS:
    ax.errorbar(NS, [get("main", SYS[s], f"rand_{n}", "spearman").mean() for n in NS], color=col[s], marker="o", ms=3, lw=1.2, label=LAB[s])
    g, nm = LOGN[s]
    ax.errorbar(NS, [get(g, nm, f"rand_{n}", "spearman").mean() for n in NS], color=col[s], marker="s", ms=3, lw=1.2, ls="--")
ax.set_xscale("log"); ax.set_xlabel("N (random training variants)"); ax.set_ylabel("Spearman"); ax.grid(alpha=.3)
ax.legend(fontsize=6, title="solid: raw target, dashed: log target", title_fontsize=6)
plt.tight_layout(); plt.savefig("results/figures/logtarget_curves.pdf"); plt.close()
json.dump(out, open(a.out, "w"))
print(json.dumps({k: round(v, 4) for k, v in out.items() if k.startswith("gap_hd3")}))
