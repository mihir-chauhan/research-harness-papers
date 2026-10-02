"""Builds robust-summary tables and figures from results/runs.jsonl (no numbers typed by hand)."""
import json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
runs = [json.loads(l) for l in open("results/runs.jsonl")]
runs = [r for r in runs if r["kind"] != "sanity" and r.get("status", "ok") == "ok"]
def get(group, name, key, seeds=None):
    v = [r["metrics"][key] for r in runs if r["group"] == group and r["name"] == name and (seeds is None or r["seed"] in seeds)]
    return np.array([np.inf if (x is None or not np.isfinite(x)) else x for x in v])  # NaN/inf = diverged
def med(x): return np.median(x)
def f(x):
    if not np.isfinite(x): return "div."
    return f"{x:.3f}" if x < 100 else f"{x:.0e}"
def f2(x):
    """Compact per-seed format: div. = non-finite; scientific above 100."""
    if not np.isfinite(x): return "div."
    if x >= 100: return f"{x:.0e}".replace("e+0", "e").replace("e+", "e")
    return f"{x:.3f}" if x < 0.1 else f"{x:.2f}"
def byseed(group, name, key, seeds):
    d = {r["seed"]: r["metrics"][key] for r in runs if r["group"] == group and r["name"] == name}
    return np.array([np.inf if (d[s] is None or not np.isfinite(d[s])) else d[s] for s in seeds])
order = ["MLP (flat adjacency)", "MPNN-sum", "MPNN-sum + steps", "MPNN-max", "MPNN-max + steps"]
# Table: medians + failures
rows = []
for n in order:
    c = [f(med(get("main", n, f"mae_sparse_n{k}"))) for k in (8, 16, 32, 64)]
    c += [f(med(get("main", n, f"mae_dense_n{k}"))) for k in (8, 64)] + [f(med(get("main", n, f"rel_{x}_n64"))) for x in ("sparse", "dense")]
    fs = int((get("main", n, "mae_sparse_n64") > 1).sum()); fd = int((get("main", n, "mae_dense_n64") > 1).sum())
    rows.append(f"{n} & " + " & ".join(c) + f" & {fs}/5 & {fd}/5 \\\\")
open("results/tables/robust.tex", "w").write(
    "\\begin{tabular}{lcccccccccc}\\toprule\n System & S8 & S16 & S32 & S64 & D8 & D64 & rS64 & rD64 & fail S64 & fail D64 \\\\\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\\end{tabular}\n")
# Per-seed table (main group): S64, D64 and D8 for every seed (registry values only; no ratio is computed here)
S5 = (0, 1, 2, 3, 4); prow = []
for n in order:
    s64 = byseed("main", n, "mae_sparse_n64", S5); d64 = byseed("main", n, "mae_dense_n64", S5); d8 = byseed("main", n, "mae_dense_n8", S5)
    prow.append(f"{n} & " + " & ".join(f2(x) for x in list(s64) + list(d64) + list(d8)) + " \\\\")
hdr = " & ".join(str(s) for s in S5)
open("results/tables/perseed.tex", "w").write(
    "\\begin{tabular}{l" + "|ccccc" * 3 + "}\\toprule\n & \\multicolumn{5}{c|}{S64 MAE, seed} & \\multicolumn{5}{c|}{D64 MAE, seed} & \\multicolumn{5}{c}{D8 MAE, seed} \\\\\n System & "
    + hdr + " & " + hdr + " & " + hdr + " \\\\\\midrule\n" + "\n".join(prow) + "\n\\bottomrule\\end{tabular}\n")
# Sweep table
sw = ["max", "sum"]; mults = [0.5, 1.0, 2.0, 4.0]
def sweep_vals(sys, m, key):
    if m == 1.0: return get("main", f"MPNN-{sys} + steps", key, seeds=(0, 1, 2))
    name = f"{sys}+steps x{m:g}"; return get("sweep_steps", name, key)
def sweep_seed(sys, m, key):
    if m == 1.0: return byseed("main", f"MPNN-{sys} + steps", key, (0, 1, 2))
    return byseed("sweep_steps", f"{sys}+steps x{m:g}", key, (0, 1, 2))
srows = []
for s in sw:
    for key, lab in (("mae_sparse_n16", "S16"), ("mae_sparse_n64", "S64")):
        vals = np.array([sweep_seed(s, m, key) for m in mults])  # (mult, seed)
        if srows: srows.append("\\midrule")
        srows.append(f"{s}+steps & {lab} & median & " + " & ".join(f2(np.median(v)) for v in vals) + " \\\\")
        for i in range(3): srows.append(f" & & seed {i} & " + " & ".join(f2(v[i]) for v in vals) + " \\\\")
open("results/tables/sweep_table.tex", "w").write("\\begin{tabular}{lllcccc}\\toprule\n System & Cell & & $\\times$0.5 & $\\times$1 & $\\times$2 & $\\times$4$^\\dagger$ \\\\\\midrule\n" + "\n".join(srows) + "\n\\bottomrule\\end{tabular}\n")
# Aggregation ablation table
arows = []
for lab, g, n in [("sum", "main", "MPNN-sum"), ("mean", "abl_agg", "MPNN-mean"), ("max", "main", "MPNN-max"),
                  ("sum + steps", "main", "MPNN-sum + steps"), ("mean + steps", "abl_agg", "MPNN-mean + steps"), ("max + steps", "main", "MPNN-max + steps")]:
    seeds3 = [r for r in runs if r["group"] == g and r["name"] == n and r["seed"] in (0, 1, 2)]
    def m3(k): return f(np.median([np.inf if not np.isfinite(r["metrics"][k]) else r["metrics"][k] for r in seeds3]))
    def nf(k): return int(sum((not np.isfinite(r["metrics"][k])) or r["metrics"][k] > 1 for r in seeds3))
    arows.append(f"{lab} & {m3('mae_sparse_n8')} & {m3('mae_sparse_n16')} & {m3('mae_sparse_n64')} ({nf('mae_sparse_n64')}/3) & {m3('mae_dense_n64')} ({nf('mae_dense_n64')}/3) \\\\")
open("results/tables/agg_table.tex", "w").write("\\begin{tabular}{lcccc}\\toprule\n Aggregation & S8 & S16 & S64 (fail) & D64 (fail) \\\\\\midrule\n" + "\n".join(arows) + "\n\\bottomrule\\end{tabular}\n")
# Figure 1: MAE vs n
col = dict(zip(order, ["k", "tab:blue", "tab:cyan", "tab:red", "tab:orange"]))
CAP = 1e5
fig, ax = plt.subplots(1, 2, figsize=(5.2, 2.9), sharey=True)
for a, fam, t in zip(ax, ("sparse", "dense"), ("constant degree", "growing degree")):
    for n in order:
        ys = np.array([get("main", n, f"mae_{fam}_n{k}") for k in (8, 16, 32, 64)])
        ys = np.where(np.isfinite(ys) & (ys < CAP), ys, CAP)  # non-finite and >= CAP are drawn at CAP
        a.plot([8, 16, 32, 64], np.median(ys, 1), "-o", color=col[n], label=n, ms=3)
        for i, k in enumerate((8, 16, 32, 64)): a.scatter([k] * ys.shape[1], ys[i], color=col[n], s=7, alpha=.45)
    a.set_xscale("log", base=2); a.set_yscale("log"); a.set_xticks([8, 16, 32, 64]); a.set_xticklabels([8, 16, 32, 64]); a.set_title(t, fontsize=8); a.set_xlabel("test nodes n")
    a.set_ylim(3e-3, 4e5); a.axhline(CAP, color="gray", lw=.5, ls=":"); a.tick_params(labelsize=7)
ax[0].set_ylabel("MAE (median, dots = seeds)", fontsize=8); ax[0].legend(fontsize=6.5, loc="upper left", frameon=False, labelspacing=.2); plt.tight_layout(); plt.savefig("results/figures/mae_vs_n.pdf"); plt.close()
# Figure 2: step multiplier sweep
fig, ax = plt.subplots(1, 2, figsize=(5.2, 2.5))
for a, key in zip(ax, ("mae_sparse_n16", "mae_sparse_n64")):
    for s, c in (("max", "tab:orange"), ("sum", "tab:cyan")):
        ys = np.array([sweep_vals(s, m, key) for m in mults]); assert np.isfinite(ys).all()  # no sparse-family sweep run diverged
        a.plot(mults, np.median(ys, 1), "-o", color=c, label=f"MPNN-{s} + steps", ms=3)
        for i, m in enumerate(mults): a.scatter([m] * ys.shape[1], ys[i], color=c, s=7, alpha=.45)
    a.set_xscale("log", base=2); a.set_yscale("log"); a.set_xticks(mults); a.set_xticklabels(mults); a.set_xlabel("test-time steps / (n-1)", fontsize=8); a.tick_params(labelsize=7); a.set_title({"mae_sparse_n16": "S16 MAE", "mae_sparse_n64": "S64 MAE"}[key], fontsize=8)
ax[0].legend(fontsize=7, frameon=False); plt.tight_layout(); plt.savefig("results/figures/steps_sweep.pdf"); plt.close()
print(open("results/tables/perseed.tex").read()); print(open("results/tables/robust.tex").read()); print(open("results/tables/agg_table.tex").read()); print(open("results/tables/sweep_table.tex").read())
