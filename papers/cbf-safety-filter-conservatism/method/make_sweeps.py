"""Sweep / grid tables (.tex) and figures from results/runs.jsonl (std is the sample std, ddof=1, over seeds)."""
import json, collections
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

rows = [json.loads(l) for l in open("results/runs.jsonl")]
rows = [r for r in rows if r.get("status") == "ok"]
SH = {"CT-CBF": "CT-CBF", "DT-CBF": "DT-CBF", "Braking": "Braking", "Nominal": "Nominal"}
TK = {"double_integrator": "DI", "unicycle": "Uni"}
ALPHAS = [0.5, 1, 2, 5, 10]; DTS = [0.01, 0.02, 0.05, 0.1, 0.2]
A0, DT0 = 2, 0.05


def agg(group, keyf):
    d = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        if r["group"] != group: continue
        k = keyf(r)
        if k is None: continue
        for m, v in r["metrics"].items(): d[k][m].append(v)
    return d


def sd(x): return float(np.std(x, ddof=1))


def table(d, vals, label, fname, cols=("violation_rate", "worst_penetration", "time_to_goal"), fmts=("{:.2f}", "{:.3f}", "{:.2f}")):
    lines = ["\\begin{tabular}{ll" + "c" * len(vals) + "}", "\\hline", "System & Task & " + " & ".join(f"{label}={v}" for v in vals) + " \\\\", "\\hline"]
    for sysn in sorted({k[0] for k in d}):
        for t in ["double_integrator", "unicycle"]:
            if (sysn, t, vals[0]) not in d: continue
            cells = [" / ".join(f.format(np.mean(d[(sysn, t, v)][c])) for c, f in zip(cols, fmts)) for v in vals]
            lines.append(f"{sysn} & {TK[t]} & " + " & ".join(cells) + " \\\\")
    lines += ["\\hline", "\\end{tabular}"]
    open(f"results/tables/{fname}.tex", "w").write("\n".join(lines) + "\n")


def table_t(d, vals, label, fname, cols, fmts):
    keys = [(sysn, t) for sysn in sorted({k[0] for k in d}) for t in ["double_integrator", "unicycle"] if (sysn, t, vals[0]) in d]
    lines = ["\\begin{tabular}{l" + "c" * len(keys) + "}", "\\hline", label + " & " + " & ".join(f"{sysn} ({TK[t]})" for sysn, t in keys) + " \\\\", "\\hline"]
    for v in vals:
        cells = [" / ".join(f.format(np.mean(d[(sysn, t, v)][c])) for c, f in zip(cols, fmts)) for sysn, t in keys]
        lines.append(f"{v} & " + " & ".join(cells) + " \\\\")
    lines += ["\\hline", "\\end{tabular}"]
    open(f"results/tables/{fname}.tex", "w").write("\n".join(lines) + "\n")


def fig(d, xs, xlabel, fname):
    panels = [("barrier_violation_rate", "violation rate"), ("time_to_goal", "time to goal [s]"), ("min_clearance", "min. clearance [m]")]
    f, ax = plt.subplots(2, 3, figsize=(7.2, 3.1))
    for i, t in enumerate(["double_integrator", "unicycle"]):
        for j, (m, yl) in enumerate(panels):
            a = ax[i, j]
            for sysn, c in [("CT-CBF", "#1f77b4"), ("DT-CBF", "#d62728")]:
                mu = np.array([np.mean(d[(sysn, t, x)][m]) for x in xs]); s = np.array([sd(d[(sysn, t, x)][m]) for x in xs])
                a.errorbar(xs, mu, yerr=s, color=c, marker="o", ms=3, capsize=2, label=sysn)
            a.set_xscale("log"); a.grid(alpha=.3); a.tick_params(labelsize=7)
            a.set_ylabel(f"{yl} ({TK[t]})", fontsize=8)
            if i == 1: a.set_xlabel(xlabel, fontsize=8)
    ax[0, 0].legend(fontsize=7)
    plt.tight_layout(); plt.savefig(f"results/figures/{fname}.pdf"); plt.close()


# one-factor slices of the joint grid
G = lambda r: (SH[r["name"]], r["task"], r["config"]["alpha"], r["config"]["dt"])
g = agg("grid_alpha_dt", G)
da = {(k[0], k[1], k[2]): v for k, v in g.items() if k[3] == DT0}
dd = {(k[0], k[1], k[3]): v for k, v in g.items() if k[2] == A0}
SAFE = dict(cols=("barrier_violation_rate", "barrier_penetration"), fmts=("{:.2f}", "{:.3f}"))
CONS = dict(cols=("time_to_goal", "min_clearance"), fmts=("{:.2f}", "{:.2f}"))
table(da, ALPHAS, "$\\alpha$", "sweep_alpha_safe", **SAFE); table_t(da, ALPHAS, "$\\alpha$", "sweep_alpha_cons", **CONS)
table(dd, DTS, "$\\Delta t$", "sweep_dt_safe", **SAFE); table(dd, DTS, "$\\Delta t$", "sweep_dt_cons", **CONS)
fig(da, ALPHAS, "class-K gain $\\alpha$", "sweep_alpha")
fig(dd, DTS, "control period $\\Delta t$ [s]", "sweep_dt")

GM = [("barrier_violation_rate", "{:.3f}"), ("barrier_penetration", "{:.3f}"), ("min_clearance", "{:.2f}")]
# joint grid: per cell "violation rate / worst penetration [m] / min clearance [m]" (barrier level; means over seeds;
# unicycle clearance is the axle-to-raw-radius minimum clearance, which has the 0.15 m look-ahead buffer)
lines = ["\\begin{tabular}{lllccccc}", "\\hline", "Task & Filter & $\\alpha$ & " + " & ".join(f"$\\Delta t$={v}" for v in DTS) + " \\\\", "\\hline"]
for t, tl in [("double_integrator", "DI"), ("unicycle", "Uni")]:
    for sysn in ["CT-CBF", "DT-CBF"]:
        for a in ALPHAS:
            cells = [" / ".join(f.format(np.mean(g[(sysn, t, a, d)][m])) for m, f in GM) for d in DTS]
            lines.append(f"{tl} & {sysn} & {a} & " + " & ".join(cells) + " \\\\")
        lines.append("\\hline")
lines.append("\\end{tabular}")
open("results/tables/grid_violation.tex", "w").write("\n".join(lines) + "\n")

# any-time vs sample-instant violations (barrier level, tolerance 1e-9 m): "any / at samples"
g5 = agg("grid_dt005", lambda r: (SH[r["name"]], r["task"], r["config"]["alpha"], r["config"]["dt"]))
D6 = [0.005] + DTS
lines = ["\\begin{tabular}{lllcccccc}", "\\hline", "Task & Filter & $\\alpha$ & " + " & ".join(f"$\\Delta t$={v}" for v in D6) + " \\\\", "\\hline"]
for t, tl in [("double_integrator", "DI"), ("unicycle", "Uni")]:
    for sysn in ["CT-CBF", "DT-CBF"]:
        if (t, sysn) == ("unicycle", "CT-CBF"): continue   # zero except dt=0.2, where both rates coincide (stated in the caption)
        for a in [2, 5, 10]:
            cells = []
            for d in D6:
                m = g5[(sysn, t, a, d)] if d == 0.005 else g[(sysn, t, a, d)]
                cells.append(f"{np.mean(m['barrier_violation_rate']):.3f} / {np.mean(m['sample_violation_rate']):.3f}")
            lines.append(f"{tl} & {sysn} & {a} & " + " & ".join(cells) + " \\\\")
        lines.append("\\hline")
lines.append("\\end{tabular}")
open("results/tables/sample_vs_between.tex", "w").write("\n".join(lines) + "\n")

# heatmaps of violation rate
f, ax = plt.subplots(2, 2, figsize=(6.0, 3.9))
for i, t in enumerate(["double_integrator", "unicycle"]):
    for j, sysn in enumerate(["CT-CBF", "DT-CBF"]):
        M = np.array([[np.mean(g[(sysn, t, a, d)]["barrier_violation_rate"]) for d in DTS] for a in ALPHAS])
        im = ax[i, j].imshow(M, origin="lower", vmin=0, vmax=1, cmap="viridis_r")
        for (r_, c_), v in np.ndenumerate(M): ax[i, j].text(c_, r_, f"{v:.2f}", ha="center", va="center", fontsize=6, color="w" if v > .5 else "k")
        ax[i, j].set_xticks(range(len(DTS)), [str(x) for x in DTS], fontsize=7); ax[i, j].set_yticks(range(len(ALPHAS)), [str(x) for x in ALPHAS], fontsize=7)
        ax[i, j].set_title(f"{sysn} ({TK[t]})", fontsize=8); ax[i, j].set_xlabel("$\\Delta t$ [s]", fontsize=8); ax[i, j].set_ylabel("$\\alpha$", fontsize=8)
plt.tight_layout(); plt.savefig("results/figures/grid_violation.pdf"); plt.close()

# braking threshold and obstacle selection
table_t(agg("sweep_dth", lambda r: (SH[r["name"]], r["task"], r["config"]["dth"])), [0.25, 0.5, 1, 2], "$d_{th}$", "sweep_dth",
        cols=("barrier_violation_rate", "barrier_penetration", "success_rate", "time_to_goal"), fmts=("{:.2f}", "{:.3f}", "{:.3f}", "{:.2f}"))
table(agg("abl_select", lambda r: (SH[r["name"]], r["task"], r["config"]["select"])), ["nearest", "critical"], "sel", "abl_select")
