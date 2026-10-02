"""Reads results/runs.jsonl and the aggregates written by `rh table` / `rh compare` (run those first).
Writes results/figures/*.pdf, results/tables/{corr,rho_sweep,wd_sweep}.{md,tex}, cmp.tex, sel.tex, and re-typesets
results/tables/{main,abl_sam}.tex from {main,abl_sam}_agg.csv (same means and stds, sharp_rand in units of 1e-3)."""
import json, collections, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import spearmanr
R = [json.loads(l) for l in open("results/runs.jsonl")]
R = [r for r in R if r["group"] in ("main", "sweep_rho", "sweep_wd", "abl_sam")]
df = pd.DataFrame([dict(group=r["group"], name=r["name"], task=r["task"], seed=r["seed"],
                        rho=r["config"].get("rho", 0.0), wd=r["config"].get("wd", 0.0), **r["metrics"]) for r in R])
TASKS = ["digits_n0.0", "digits_n0.2", "digits_n0.4", "spirals_n0.2"]
def save(t, name, prec=3):
    t.to_csv(f"results/tables/{name}.csv")
    open(f"results/tables/{name}.md", "w").write(t.to_string())
    open(f"results/tables/{name}.tex", "w").write(t.to_latex(float_format=lambda x: f"{x:.{prec}f}", escape=True))
# --- sweeps: SAM rows = main SAM + sweep_rho ; SGD+WD rows = main SGD+WD + sweep_wd
sam = df[(df.name == "SAM")]; wdd = df[(df.name == "SGD+WD")]
rs = sam.groupby(["task", "rho"]).test_acc.agg(["mean", "std", "count"]).reset_index()
wsw = wdd.groupby(["task", "wd"]).test_acc.agg(["mean", "std", "count"]).reset_index()
sgd = df[df.name == "SGD"].groupby("task").test_acc.agg(["mean", "std"])
piv = rs.pivot(index="task", columns="rho", values="mean").loc[TASKS]; piv.columns = [f"{c:g}" for c in piv.columns]
piv.insert(0, "SGD", sgd["mean"].loc[TASKS])
save(piv, "rho_sweep", 3); print(piv.round(3)); print(rs["count"].unique())
pw = wsw.pivot(index="task", columns="wd", values="mean").loc[TASKS]; pw.columns = [f"{c:g}" for c in pw.columns]
save(pw, "wd_sweep", 3); print(pw.round(3)); print(wsw["count"].unique())
# --- fig: rho sweep
fig, ax = plt.subplots(1, 4, figsize=(7.2, 2.0), sharey=False)
for a, t in zip(ax, TASKS):
    d = rs[rs.task == t]; a.errorbar(d.rho, d["mean"], d["std"], marker="o", ms=3, lw=1, capsize=2, color="C0", label="SAM")
    a.axhline(sgd["mean"][t], color="C3", ls="--", lw=1, label="SGD")
    w = wdd[(wdd.task == t) & (wdd.group == "main")].test_acc.mean(); a.axhline(w, color="C2", ls=":", lw=1, label="SGD+WD (sel.)")
    a.set_xscale("log"); a.set_title(t.replace("_n", " n"), fontsize=7); a.tick_params(labelsize=6); a.set_xlabel(r"$\rho$", fontsize=7)
ax[0].set_ylabel("test acc", fontsize=7); ax[0].legend(fontsize=5)
plt.tight_layout(); plt.savefig("results/figures/rho_sweep.pdf"); plt.close()
# --- correlations (all evaluation-seed runs)
rows = []
def corr(d, label):
    out = {"subset": label, "n": len(d)}
    for s in ["sharp_rand", "sharp_adv"]:
        for g in ["gap_acc", "gap_loss"]:
            out[f"{s[6:]}-{g[4:]}"] = spearmanr(d[s], d[g])[0]
    rows.append(out)
df["collapsed"] = np.where(df.task.str.startswith("digits"), df.test_acc < 0.15, df.test_acc < 0.55)
print("collapsed runs:", df[df.collapsed].groupby(["task", "name", "rho", "wd"]).size())
corr(df, "all tasks pooled")
corr(df[~df.collapsed], "pooled, collapsed runs removed")
for t in TASKS: corr(df[df.task == t], t)
for t in TASKS: corr(df[(df.task == t) & ~df.collapsed], t + " no collapsed")
corr(df[(df.name == "SAM") & (df.task != "spirals_n0.2")], "SAM-sweep digits pooled")
for t in TASKS[:3]: corr(df[(df.name == "SAM") & (df.task == t)], f"SAM only {t}")
ct = pd.DataFrame(rows).set_index("subset"); ct["n"] = ct["n"].astype(int)
save(ct, "corr", 2); print(ct.round(2))
# --- scatter
fig, ax = plt.subplots(1, 2, figsize=(7.4, 2.5))
cols = dict(zip(TASKS, ["C0", "C1", "C3", "C2"])); mk = {"SGD": "o", "SGD+WD": "s", "SAM": "^", "SAM random direction": "v", "SAM+WD": "D"}
for a, s in zip(ax, ["sharp_adv", "sharp_rand"]):
    for (t, n), d in df.groupby(["task", "name"]):
        a.scatter(d[s], d.gap_acc, s=14, marker=mk[n], color=cols[t], alpha=.7, lw=0)
    a.set_xscale("log"); a.set_xlabel(s.replace("_", " ") + " (loss increase, norm 0.5)", fontsize=8); a.tick_params(labelsize=7)
ax[0].set_ylabel("gap_acc", fontsize=8)
from matplotlib.lines import Line2D
h = [Line2D([], [], marker="o", ls="", color=c, label=t.replace("_n", " n"), ms=4) for t, c in cols.items()] + \
    [Line2D([], [], marker=m, ls="", color="gray", label=n, ms=4) for n, m in mk.items()]
ax[1].legend(handles=h, fontsize=6, loc="center left", bbox_to_anchor=(1.02, 0.5), ncol=1)
plt.tight_layout(); plt.savefig("results/figures/sharp_gap.pdf"); plt.close()
# --- paired comparison table (from rh compare csv) and selected hyper-parameters
c = pd.read_csv("results/tables/compare_main_test_acc.csv")
# Holm step-down adjustment of the 8 paired p-values (not a registered test; reported next to the uncorrected ones)
o = np.argsort(c.paired_p.values); m = len(o); adj = np.empty(m); run = 0.0
for k, i in enumerate(o):
    run = max(run, min(1.0, (m - k) * c.paired_p.values[i])); adj[i] = run
c["holm"] = adj
c = c[["task", "name", "delta", "welch_p", "paired_p", "holm"]]
c.columns = ["task", "vs", "diff", "Welch p", "paired p", "Holm p"]
c = c.set_index(["task", "vs"])
open("results/tables/cmp.tex", "w").write(c.to_latex(float_format=lambda x: f"{x:.3g}" if abs(x) < 0.01 else f"{x:.3f}", escape=True))
sel = json.load(open("experiments/selected.json"))
st = pd.DataFrame({t: {"SAM rho": sel[f"{t}|SAM"], "SGD+WD wd": sel[f"{t}|SGD+WD"]} for t in TASKS}).T
open("results/tables/sel.tex", "w").write(st.to_latex(float_format=lambda x: f"{x:g}", escape=True))
# --- main and ablation tables: typeset the rh-table aggregates with per-column precision (sharp_rand x 1e3)
COLS = [("test_acc", "test\\_acc", 1, 3), ("gap_acc", "gap\\_acc", 1, 3), ("memorised", "memorised", 1, 3),
        ("sharp_adv", "sharp\\_adv", 1, 4), ("sharp_rand", "sharp\\_rand ($\\times10^{-3}$)", 1e3, 3),
        ("weight_norm", "weight\\_norm", 1, 2)]
def typeset(group, order):
    a = pd.read_csv(f"results/tables/{group}_agg.csv").set_index(["task", "name", "metric"])
    L = ["\\begin{tabular}{ll" + "c" * len(COLS) + "}", "\\toprule",
         "Method & Task & " + " & ".join(h for _, h, _, _ in COLS) + " \\\\"]
    md = ["| Method | Task | " + " | ".join(k + (" (x1e-3)" if sc != 1 else "") for k, _, sc, _ in COLS) + " |", "|---" * (len(COLS) + 2) + "|"]
    for t in TASKS:
        L.append("\\midrule")
        for n in order:
            cells = [f"{a.loc[(t, n, k), 'mean'] * sc:.{pr}f} $\\pm$ {a.loc[(t, n, k), 'std'] * sc:.{pr}f}" for k, _, sc, pr in COLS]
            L.append(f"{n} & {t} & ".replace("_", "\\_") + " & ".join(cells) + " \\\\")
            md.append(f"| {n} | {t} | " + " | ".join(x.replace(" $\\pm$ ", " ± ") for x in cells) + " |")
    L += ["\\bottomrule", "\\end{tabular}"]
    open(f"results/tables/{group}.tex", "w").write("\n".join(L) + "\n")
    open(f"results/tables/{group}_fmt.md", "w").write("\n".join(md) + "\n"); print("\n".join(md))
typeset("main", ["SGD", "SGD+WD", "SAM"])
typeset("abl_sam", ["SAM random direction", "SAM+WD"])
