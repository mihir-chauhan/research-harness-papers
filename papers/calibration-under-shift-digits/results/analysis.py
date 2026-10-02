"""Reads results/runs.jsonl; writes the paper's tables (results/tables/*.tex) and figures (results/figures/*.pdf).
The tables contain no numbers: every cell is a \\rhval{<key>} macro that `rh paper build` fills from the registry
(means, and the statistics of `rh compare`, whose CSVs in results/tables/ are read here only to pick a print format).
The markdown copies (main_ece_nll.md, main_acc_brier.md) hold the means for reading outside the paper."""
import json, re, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
rows = []
for l in open("results/runs.jsonl"):
    r = json.loads(l)
    if r["status"] == "ok" and r["kind"] != "sanity":
        rows.append(dict(group=r["group"], name=r["name"], task=r["task"], seed=r["seed"], **r["config"], **r["metrics"]))
df = pd.DataFrame(rows)
# abl_oracle and abl_dropdet also list main-group runs again (rh log --from-run, for rh compare): select by system name
main = df[df.group == "main"]; orc = df[(df.group == "abl_oracle") & (df.name == "TS oracle (shifted val)")]
SYS = ["MLP", "MLP + temperature scaling", "MC dropout", "Deep ensemble (5)"]; SH = ["MLP", "TS", "MCD", "Ens"]
TASKS = ["rot0", "rot10", "rot20", "rot30", "rot45", "rot60", "noise0.25", "noise0.5", "noise0.75", "noise1.0", "rot30_noise0.5"]
TL = {t: t.replace("_", "+").replace("noise", "n").replace("rot", "r") for t in TASKS}
g = lambda n: main[main.name == n]
TS, MLP, MCD, ENS = g(SYS[1]), g(SYS[0]), g(SYS[2]), g(SYS[3])
M = main.groupby(["name", "task"]).mean(numeric_only=True)
slug = lambda x: re.sub(r"[^a-z0-9_.+-]+", "-", str(x).lower()).strip("-") or "x"   # as rh.numbers.slug
def val(group, name, task, metric, stat="mean", spec="3"):   # a recorded aggregate, printed by \rhval
    return f"\\rhval{{{slug(group)}/{slug(name)}/{slug(task)}/{slug(metric)}/{stat}:{spec}}}"
ORC, DET, ENSN, MCDN, TSN, MLPN = "TS oracle (shifted val)", "Dropout-trained MLP, deterministic", SYS[3], SYS[2], SYS[1], SYS[0]
CMP = {(g, m): pd.read_csv(f"results/tables/compare_{g}_{m}.csv") for g, m in
       [("main", "ece"), ("main", "nll"), ("main", "brier"), ("abl_oracle", "ece"), ("abl_oracle", "nll"), ("abl_dropdet", "ece")]}
REF = {"main": MCDN, "abl_oracle": TSN, "abl_dropdet": DET}   # the reference system of each `rh compare` call
def cmp(group, other, task, metric, stat, spec="3"):   # a statistic of `rh compare --group <group> --metric <metric> --ref REF[group]`
    c = CMP[(group, metric)]; assert set(c.ref) == {REF[group]} and len(c[(c.name == other) & (c.task == task)]) == 1
    return f"\\rhval{{cmp/{slug(group)}/{slug(other)}/{slug(task)}/{slug(metric)}/{stat}:{spec}}}"
def pval(group, other, task, metric, dec=3):   # `dec` decimals; scientific notation when that would print as zero
    c = CMP[(group, metric)]; p = float(c[(c.name == other) & (c.task == task)].paired_p.iloc[0])
    return cmp(group, other, task, metric, "paired_p", str(dec) if p >= 0.5 * 10 ** -dec else "sci1")
def write(fname, lines):
    open(f"results/tables/{fname}.tex", "w").write("\n".join(lines + ["\\bottomrule", "\\end{tabular}"]) + "\n")

def two_metric_table(m1, m2, fname, prec=3):
    cols = "l" + "cccc" + "cccc"
    hdr = " & ".join(["Shift"] + [f"{m1.upper() if m1!='accuracy' else 'Acc'} {s}" for s in SH] + [f"{m2.upper() if m2!='accuracy' else 'Acc'} {s}" for s in SH])
    lines = [f"\\begin{{tabular}}{{{cols}}}", "\\toprule", hdr + " \\\\", "\\midrule"]
    md = ["| " + hdr.replace("&", "|") + " |", "|" + "---|" * 9]
    for t in TASKS:
        vals, mdv = [], []
        for m in (m1, m2):
            v = [M.loc[(s, t), m] for s in SYS]
            best = (max if m == "accuracy" else min)(v)
            vals += [(f"\\textbf{{{val('main', s, t, m)}}}" if x == best else val("main", s, t, m)) for s, x in zip(SYS, v)]
            mdv += [(f"**{x:.{prec}f}**" if x == best else f"{x:.{prec}f}") for x in v]
        lines.append(" & ".join([TL[t]] + vals) + " \\\\")
        md.append("| " + " | ".join([t] + mdv) + " |")
    write(fname, lines); open(f"results/tables/{fname}.md", "w").write("\n".join(md))
two_metric_table("ece", "nll", "main_ece_nll"); two_metric_table("accuracy", "brier", "main_acc_brier")

# registered hypothesis tests: means, and the differences and paired p-values of `rh compare`
lines = ["\\begin{tabular}{lllcccc}", "\\toprule", "Hyp. & Quantity (A $-$ B) & Shift & A & B & A$-$B & $p$ \\\\", "\\midrule"]
for m in ["nll", "ece"]:
    lines.append(f"H1 & {m.upper()}: TS $-$ MLP & r0 & {val('main', TSN, 'rot0', m)} & {val('main', MLPN, 'rot0', m)} & {cmp('abl_oracle', MLPN, 'rot0', m, 'delta')} & {pval('abl_oracle', MLPN, 'rot0', m)} \\\\")
for t in ["rot60", "noise1.0"]:
    lines.append(f"H2 & TS ECE: shifted (A), r0 (B) & {TL[t]} & {val('main', TSN, t, 'ece')} & {val('main', TSN, 'rot0', 'ece')} & -- & -- \\\\")
for t in ["rot60", "noise1.0"]:
    for m in ["nll", "brier"]:
        assert min(SYS, key=lambda s: M.loc[(s, t), m]) == MCDN   # the best system other than the ensemble is MC dropout
        lines.append(f"H3 & {m.upper() if m == 'nll' else 'Brier'}: MCD $-$ Ens & {TL[t]} & {val('main', MCDN, t, m)} & {val('main', ENSN, t, m)} & {cmp('main', ENSN, t, m, 'delta')} & -- \\\\")
for t in ["rot60", "noise1.0"]:
    lines.append(f"H4 & ECE: MCD $-$ Ens & {TL[t]} & {val('main', MCDN, t, 'ece')} & {val('main', ENSN, t, 'ece')} & {cmp('main', ENSN, t, 'ece', 'delta')} & {pval('main', ENSN, t, 'ece')} \\\\")
for t in ["rot45", "rot60", "noise0.75", "noise1.0"]:
    lines.append(f"H5 & ECE: TS $-$ Oracle & {TL[t]} & {val('main', TSN, t, 'ece')} & {val('abl_oracle', ORC, t, 'ece')} & {cmp('abl_oracle', ORC, t, 'ece', 'delta')} & {pval('abl_oracle', ORC, t, 'ece')} \\\\")
write("hyp", lines)

# per-seed nuance: oracle vs TS at rot0 must be identical
a = orc[orc.task == "rot0"].sort_values("seed").ece.values; b = TS[TS.task == "rot0"].sort_values("seed").ece.values
print("oracle==TS at rot0:", np.allclose(a, b))

# oracle table: ECE, NLL and temperature of TS vs oracle TS
lines = ["\\begin{tabular}{lcccccc}", "\\toprule", "Shift & ECE TS & ECE Orc & NLL TS & NLL Orc & $T$ TS & $T$ Orc \\\\", "\\midrule"]
for t in TASKS:
    lines.append(" & ".join([TL[t]] + [val(g, n, t, m) for m in ("ece", "nll", "temperature") for g, n in (("main", TSN), ("abl_oracle", ORC))]) + " \\\\")
write("oracle_cmp", lines)

# TS vs MLP per shift (rh compare --group abl_oracle --ref TS: delta = TS - MLP, rel_delta = delta / MLP)
lines = ["\\begin{tabular}{lccccccc}", "\\toprule", "Shift & ECE MLP & ECE TS & $\\Delta$ECE\\% & $p$ & NLL MLP & NLL TS & $p$ \\\\", "\\midrule"]
for t in TASKS:
    lines.append(" & ".join([TL[t], val("main", MLPN, t, "ece"), val("main", TSN, t, "ece"), cmp("abl_oracle", MLPN, t, "ece", "rel_delta", "pct0"),
                             pval("abl_oracle", MLPN, t, "ece"), val("main", MLPN, t, "nll"), val("main", TSN, t, "nll"), pval("abl_oracle", MLPN, t, "nll")]) + " \\\\")
write("ts_vs_mlp", lines)

# MC dropout vs deep ensemble per shift (rh compare --group main --ref "MC dropout": delta = MCD - Ens)
lines = ["\\begin{tabular}{lcccccc}", "\\toprule", "Shift & $\\Delta$ECE & $p$ & $\\Delta$NLL & $p$ & $\\Delta$Brier & $p$ \\\\", "\\midrule"]
for t in TASKS:
    lines.append(" & ".join([TL[t]] + [x for m in ("ece", "nll", "brier") for x in (cmp("main", ENSN, t, m, "delta"), pval("main", ENSN, t, m, 4))]) + " \\\\")
write("mcd_vs_ens", lines)

# dropout decomposition table (abl_dropdet)
lines = ["\\begin{tabular}{lcccccccc}", "\\toprule", "Shift & Acc MLP & Acc Det & Acc MCD & ECE MLP & ECE Det & ECE MCD & NLL Det & NLL MCD \\\\", "\\midrule"]
for t in TASKS:
    v = [val("main", MLPN, t, "accuracy"), val("abl_dropdet", DET, t, "accuracy"), val("main", MCDN, t, "accuracy"), val("main", MLPN, t, "ece"),
         val("abl_dropdet", DET, t, "ece"), val("main", MCDN, t, "ece"), val("abl_dropdet", DET, t, "nll"), val("main", MCDN, t, "nll")]
    lines.append(" & ".join([TL[t]] + v) + " \\\\")
write("dropdet", lines)
# sweep table (wide)
lines = ["\\begin{tabular}{llcccccc}", "\\toprule", "Sweep & Value & ECE r0 & NLL r0 & ECE r30 & NLL r30 & ECE n0.5 & NLL n0.5 \\\\", "\\midrule"]
for grp, par, nm, sysn in [("sweep_members", "members", "M", "Deep ensemble"), ("sweep_dropout", "p", "$p$", "MC dropout")]:
    for v in sorted(df[df.group == grp][par].unique()):
        pv = slug(json.dumps(int(v) if float(v).is_integer() else float(v)))
        lines.append(f"{nm} & {v:g} & " + " & ".join(f"\\rhval{{{grp}/{slug(sysn)}@{par}={pv}/{slug(t)}/{m}/mean:3}}" for t in ["rot0", "rot30", "noise0.5"] for m in ("ece", "nll")) + " \\\\")
    lines.append("\\midrule")
write("sweeps", lines[:-1])
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
