"""Reads results/runs.jsonl; writes compact tables (results/tables/*.tex|md), figures (results/figures/*.pdf) and results/hyp.md."""
import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import stats
rows = []
for l in open("results/runs.jsonl"):
    r = json.loads(l)
    if r["status"] == "ok" and r["kind"] != "sanity":
        rows.append(dict(group=r["group"], name=r["name"], task=r["task"], seed=r["seed"], **r["config"], **r["metrics"]))
df = pd.DataFrame(rows)
main = df[df.group == "main"]; orc = df[df.group == "abl_oracle"]
SYS = ["MLP", "MLP + temperature scaling", "MC dropout", "Deep ensemble (5)"]; SH = ["MLP", "TS", "MCD", "Ens"]
TASKS = ["rot0", "rot10", "rot20", "rot30", "rot45", "rot60", "noise0.25", "noise0.5", "noise0.75", "noise1.0", "rot30_noise0.5"]
TL = {t: t.replace("_", "+").replace("noise", "n").replace("rot", "r") for t in TASKS}
M = main.groupby(["name", "task"]).mean(numeric_only=True)
def two_metric_table(m1, m2, fname, prec=3):
    cols = "l" + "cccc" + "cccc"
    hdr = " & ".join(["Shift"] + [f"{m1.upper() if m1!='accuracy' else 'Acc'} {s}" for s in SH] + [f"{m2.upper() if m2!='accuracy' else 'Acc'} {s}" for s in SH])
    lines = [f"\\begin{{tabular}}{{{cols}}}", "\\toprule", hdr + " \\\\", "\\midrule"]
    md = ["| " + hdr.replace("&", "|") + " |", "|" + "---|" * 9]
    for t in TASKS:
        vals = []
        for m in (m1, m2):
            v = [M.loc[(s, t), m] for s in SYS]
            best = (max if m == "accuracy" else min)(v)
            vals += [(f"\\textbf{{{x:.{prec}f}}}" if x == best else f"{x:.{prec}f}") for x in v]
        lines.append(" & ".join([TL[t]] + vals) + " \\\\")
        md.append("| " + " | ".join([t] + [x.replace("\\textbf{", "**").replace("}", "**") if "textbf" in x else x for x in vals]) + " |")
    lines += ["\\bottomrule", "\\end{tabular}"]
    open(f"results/tables/{fname}.tex", "w").write("\n".join(lines)); open(f"results/tables/{fname}.md", "w").write("\n".join(md))
two_metric_table("ece", "nll", "main_ece_nll"); two_metric_table("accuracy", "brier", "main_acc_brier")

# hypothesis tests
def paired(a, b, metric, task):  # a, b: dataframes
    x = a[a.task == task].sort_values("seed")[metric].values; y = b[b.task == task].sort_values("seed")[metric].values
    d = x - y; p = stats.ttest_rel(x, y).pvalue
    return x.mean(), y.mean(), d.mean(), p
g = lambda n: main[main.name == n]
TS, MLP, MCD, ENS = g(SYS[1]), g(SYS[0]), g(SYS[2]), g(SYS[3])
H = []
for t in ["rot0"]:
    for m in ["nll", "ece"]:
        a, b, d, p = paired(TS, MLP, m, t); H.append(("H1", f"TS-MLP {m}", t, a, b, d, p))
for t in ["rot60", "noise1.0"]:
    ts_id = TS[TS.task == "rot0"].ece.mean(); ts_s = TS[TS.task == t].ece.mean()
    H.append(("H2", "TS ECE shifted vs rot0 (ratio)", t, ts_s, ts_id, ts_s / ts_id, np.nan))
for t in ["rot60", "noise1.0"]:
    for m in ["nll", "brier"]:
        means = {s: main[(main.name == s) & (main.task == t)][m].mean() for s in SYS}
        H.append(("H3", f"{m}: best system", t, means[SYS[3]], min(v for k, v in means.items() if k != SYS[3]), means[SYS[3]] - min(v for k, v in means.items() if k != SYS[3]), np.nan))
for t in ["rot60", "noise1.0"]:
    a, b, d, p = paired(ENS, MCD, "ece", t); H.append(("H4", "Ens-MCD ece", t, a, b, d, p))
for t in ["rot45", "rot60", "noise0.75", "noise1.0"]:
    a, b, d, p = paired(orc, TS, "ece", t); H.append(("H5", "Oracle-TS ece", t, a, b, d, p))
Hd = pd.DataFrame(H, columns=["hyp", "quantity", "task", "A", "B", "A-B", "paired_p"])
Hd.to_csv("results/tables/hyp.csv", index=False)
lines = ["\\begin{tabular}{llcccc}", "\\toprule", "Hyp. & Quantity & Shift & A & B & A$-$B / ratio, $p$ \\\\", "\\midrule"]
for r in H:
    last = f"{r[5]:.3f}" + (f", $p$={r[6]:.3f}" if not np.isnan(r[6]) else "")
    lines.append(f"{r[0]} & {r[1]} & {TL[r[2]]} & {r[3]:.3f} & {r[4]:.3f} & {last} \\\\")
lines += ["\\bottomrule", "\\end{tabular}"]
open("results/tables/hyp.tex", "w").write("\n".join(lines).replace("{TS-MLP", "{TS--MLP"))
open("results/tables/hyp.md", "w").write(Hd.round(4).to_string(index=False))

# per-seed nuance: oracle vs TS at rot0 must be identical
a = orc[orc.task == "rot0"].sort_values("seed").ece.values; b = TS[TS.task == "rot0"].sort_values("seed").ece.values
print("oracle==TS at rot0:", np.allclose(a, b))

# temperature table
Tm = pd.DataFrame({"TS T (ID-fit)": TS.groupby("task").temperature.mean(), "Oracle T": orc.groupby("task").temperature.mean(),
                   "Oracle T min": orc.groupby("task").temperature.min(), "Oracle T max": orc.groupby("task").temperature.max()}).loc[TASKS]
print(Tm.round(2).to_string())
# oracle table: ECE and NLL of TS vs oracle TS
lines = ["\\begin{tabular}{lcccccc}", "\\toprule", "Shift & ECE TS & ECE Orc & NLL TS & NLL Orc & $T$ TS & $T$ Orc \\\\", "\\midrule"]
for t in TASKS:
    lines.append(" & ".join([TL[t]] + [f"{x:.3f}" for x in (TS[TS.task == t].ece.mean(), orc[orc.task == t].ece.mean(), TS[TS.task == t].nll.mean(), orc[orc.task == t].nll.mean(), TS[TS.task == t].temperature.mean(), orc[orc.task == t].temperature.mean())]) + " \\\\")
lines += ["\\bottomrule", "\\end{tabular}"]
open("results/tables/oracle_cmp.tex", "w").write("\n".join(lines)); 

# TS vs MLP per shift
lines = ["\\begin{tabular}{lccccccc}", "\\toprule", "Shift & ECE MLP & ECE TS & $\\Delta$ECE\\% & $p$ & NLL MLP & NLL TS & $p$ \\\\", "\\midrule"]
for t in TASKS:
    _, _, _, pe = paired(TS, MLP, "ece", t); _, _, _, pn = paired(TS, MLP, "nll", t)
    e1, e2 = MLP[MLP.task == t].ece.mean(), TS[TS.task == t].ece.mean(); n1, n2 = MLP[MLP.task == t].nll.mean(), TS[TS.task == t].nll.mean()
    lines.append(f"{TL[t]} & {e1:.3f} & {e2:.3f} & {100*(e2-e1)/e1:.0f} & {pe:.3f} & {n1:.3f} & {n2:.3f} & {pn:.3f} \\\\")
lines += ["\\bottomrule", "\\end{tabular}"]
open("results/tables/ts_vs_mlp.tex", "w").write("\n".join(lines))
# dropout decomposition table (abl_dropdet)
dd_ = df[df.group == "abl_dropdet"]
if len(dd_):
    DD = dd_.groupby("task").mean(numeric_only=True)
    lines = ["\\begin{tabular}{lcccccccc}", "\\toprule", "Shift & Acc MLP & Acc Det & Acc MCD & ECE MLP & ECE Det & ECE MCD & NLL Det & NLL MCD \\\\", "\\midrule"]
    for t in TASKS:
        v = [M.loc[(SYS[0], t), "accuracy"], DD.loc[t, "accuracy"], M.loc[(SYS[2], t), "accuracy"], M.loc[(SYS[0], t), "ece"], DD.loc[t, "ece"], M.loc[(SYS[2], t), "ece"], DD.loc[t, "nll"], M.loc[(SYS[2], t), "nll"]]
        lines.append(" & ".join([TL[t]] + [f"{x:.3f}" for x in v]) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    open("results/tables/dropdet.tex", "w").write("\n".join(lines))
    DDs = dd_.set_index(["task", "seed"]).sort_index()
    for t in ["rot0", "rot30", "rot60", "noise1.0"]:
        for nm, ref in [("MCD", MCD), ("MLP", MLP)]:
            x = DDs.loc[t].ece.values; y = ref[ref.task == t].sort_values("seed").ece.values
            print("Det-dropout ECE vs", nm, t, round(x.mean(), 4), round(y.mean(), 4), "p=", round(stats.ttest_rel(x, y).pvalue, 4))
# Figures
col = dict(zip(SYS, ["#555555", "#1b6ca8", "#d9822b", "#2a9d5c"])); mk = dict(zip(SYS, ["o", "s", "^", "D"]))
fam = {"rotation (degrees)": (["rot0", "rot10", "rot20", "rot30", "rot45", "rot60"], [0, 10, 20, 30, 45, 60]),
       "noise sigma": (["rot0", "noise0.25", "noise0.5", "noise0.75", "noise1.0"], [0, .25, .5, .75, 1.0])}
fig, ax = plt.subplots(2, 2, figsize=(7, 4.6))
for i, (m, lab) in enumerate([("ece", "ECE"), ("nll", "NLL")]):
    for j, (fn, (ts, xs)) in enumerate(fam.items()):
        for s, sh in zip(SYS, SH):
            sd = [main[(main.name == s) & (main.task == t)][m].std() for t in ts]; mu = [M.loc[(s, t), m] for t in ts]
            ax[i, j].errorbar(xs, mu, yerr=sd, color=col[s], marker=mk[s], ms=4, lw=1.2, capsize=2, label=sh)
        ax[i, j].set_xlabel(fn); ax[i, j].set_ylabel(lab); ax[i, j].grid(alpha=.3)
ax[0, 0].legend(fontsize=7); fig.tight_layout(); fig.savefig("results/figures/shift_curves.pdf"); plt.close(fig)
fig, ax = plt.subplots(1, 3, figsize=(7, 2.4))
for s, sh in zip(SYS, SH):
    d = M.loc[s].loc[TASKS]; ax[0].scatter(d.accuracy, d.conf, color=col[s], marker=mk[s], s=18, label=sh)
ax[0].plot([0, 1], [0, 1], "k--", lw=.8); ax[0].set_xlabel("accuracy"); ax[0].set_ylabel("mean confidence"); ax[0].legend(fontsize=6)
for k, (fn, (ts, xs)) in enumerate(fam.items()):
    ax[k + 1].errorbar(xs, [TS[TS.task == t].temperature.mean() for t in ts], yerr=[TS[TS.task == t].temperature.std() for t in ts], marker="s", color="#1b6ca8", label="ID-fit T", capsize=2)
    ax[k + 1].errorbar(xs, [orc[orc.task == t].temperature.mean() for t in ts], yerr=[orc[orc.task == t].temperature.std() for t in ts], marker="o", color="#c0392b", label="oracle T", capsize=2)
    ax[k + 1].set_yscale("log"); ax[k + 1].set_xlabel(fn); ax[k + 1].set_ylabel("temperature"); ax[k + 1].grid(alpha=.3)
ax[1].legend(fontsize=6); fig.tight_layout(); fig.savefig("results/figures/conf_temp.pdf"); plt.close(fig)
# sweeps
fig, ax = plt.subplots(2, 3, figsize=(7, 3.8))
for r, (grp, par, lab) in enumerate([("sweep_members", "members", "ensemble size M"), ("sweep_dropout", "p", "dropout rate p")]):
    d = df[df.group == grp]
    for c, (m, ml) in enumerate([("ece", "ECE"), ("nll", "NLL"), ("accuracy", "accuracy")]):
        for t, cc in zip(["rot0", "rot30", "noise0.5"], ["#555", "#1b6ca8", "#d9822b"]):
            dd = d[d.task == t].groupby(par)[m].agg(["mean", "std"])
            ax[r, c].errorbar(dd.index, dd["mean"], yerr=dd["std"], marker="o", ms=3, color=cc, capsize=2, label=t)
        ax[r, c].set_xlabel(lab); ax[r, c].set_ylabel(ml); ax[r, c].grid(alpha=.3)
ax[0, 0].legend(fontsize=6); fig.tight_layout(); fig.savefig("results/figures/sweeps.pdf"); plt.close(fig)
# sweep table (wide)
lines = ["\\begin{tabular}{llcccccc}", "\\toprule", "Sweep & Value & ECE r0 & NLL r0 & ECE r30 & NLL r30 & ECE n0.5 & NLL n0.5 \\\\", "\\midrule"]
for grp, par, nm in [("sweep_members", "members", "M"), ("sweep_dropout", "p", "$p$")]:
    d = df[df.group == grp].groupby([par, "task"])[["ece", "nll"]].mean()
    for v in sorted(df[df.group == grp][par].unique()):
        lines.append(f"{nm} & {v:g} & " + " & ".join(f"{d.loc[(v, t), m]:.3f}" for t in ["rot0", "rot30", "noise0.5"] for m in ("ece", "nll")) + " \\\\")
    lines.append("\\midrule")
lines[-1] = "\\bottomrule"; lines.append("\\end{tabular}")
open("results/tables/sweeps.tex", "w").write("\n".join(lines))
print(Hd.round(4).to_string())
