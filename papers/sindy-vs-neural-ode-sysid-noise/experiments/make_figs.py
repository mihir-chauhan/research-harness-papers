"""Figures and extra tables built only from results/runs.jsonl (mean over seeds, individual seeds as dots)."""
import json, collections, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
rows = [json.loads(l) for l in open("results/runs.jsonl")]
rows = [r for r in rows if r["status"] == "ok" and r["kind"] != "sanity"]
SYS = ["SINDy (STLSQ)", "Neural ODE (MLP)", "DMDc (linear LS)", "True model (oracle)"]
COL = {"SINDy (STLSQ)": "#1b6ca8", "Neural ODE (MLP)": "#d9822b", "DMDc (linear LS)": "#6b8e23", "True model (oracle)": "#777777"}
SHORT = {"SINDy (STLSQ)": "SINDy", "Neural ODE (MLP)": "MLP", "DMDc (linear LS)": "DMDc", "True model (oracle)": "oracle"}

def get(group, name, task, metric, key=None):
    return [r["metrics"][metric] for r in rows if r["group"] == group and r["name"] == name and r["task"] == task]

# ---- Fig: bars over noise per system (log y) ----
def bars(metric, fname, ylabel, logy):
    fig, axs = plt.subplots(1, 2, figsize=(3.5, 1.6), sharey=False)
    noises = ["0.0", "0.02", "0.05", "0.1"]
    for ax, task in zip(axs, ["pendulum", "vdp"]):
        sy = [s for s in SYS if metric != "pred_nrmse" or s != "True model (oracle)"]
        w = 0.8 / len(sy)
        for i, s in enumerate(sy):
            for j, nz in enumerate(noises):
                v = np.array(get("main", s, f"{task}_noise{nz}", metric))
                x = j + (i - (len(sy) - 1) / 2) * w
                ax.bar(x, v.mean(), w * 0.92, color=COL[s], label=SHORT[s] if j == 0 else None)
                ax.scatter(np.full(len(v), x), v, s=2, color="k", zorder=3, lw=0)
        ax.set_xticks(range(4)); ax.set_xticklabels(["0", "0.02", "0.05", "0.1"], fontsize=7); ax.set_xlabel("noise level $\\sigma$", fontsize=8)
        ax.set_title({"pendulum": "pendulum", "vdp": "Van der Pol"}[task], fontsize=8); ax.tick_params(axis="y", labelsize=7)
        if logy: ax.set_yscale("log")
    axs[0].set_ylabel(ylabel, fontsize=8); axs[1].legend(fontsize=6, loc="upper left")
    fig.tight_layout(pad=0.3); fig.savefig(f"results/figures/{fname}.pdf"); plt.close(fig)
bars("pred_nrmse", "bars_main_pred_nrmse", "pred_nrmse (log)", True)
bars("lqr_cost", "bars_main_lqr_cost", "LQR cost (log)", True)

# ---- Fig: data size, median over seeds with min-max band (log axes, explicit plain ticks) ----
from matplotlib.ticker import NullFormatter, NullLocator
NT = [200, 500, 1000, 2000, 5000]
def ntrain_panel(ax, task, metric):
    for s in SYS[:3]:
        med, lo, hi = [], [], []
        for n in NT:
            v = np.array([r["metrics"][metric] for r in rows if r["group"] == f"sweep_ntrain_{task}" and r["name"] == s and r["config"]["ntrain"] == n])
            med.append(np.median(v)); lo.append(v.min()); hi.append(v.max())
        ax.plot(NT, med, "o-", color=COL[s], label=SHORT[s], ms=3); ax.fill_between(NT, lo, hi, color=COL[s], alpha=0.15, lw=0)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xticks(NT); ax.set_xticklabels(["200", "500", "1k", "2k", "5k"], fontsize=7)
    ax.xaxis.set_minor_locator(NullLocator()); ax.xaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(axis="y", labelsize=7); ax.set_xlabel("training transitions $N$", fontsize=8)
def ntrain_fig(metric, fname, ylabel):
    fig, axs = plt.subplots(1, 2, figsize=(3.5, 1.6))
    for ax, task, title in zip(axs, ["pendulum", "vdp"], ["pendulum", "Van der Pol"]):
        ntrain_panel(ax, task, metric); ax.set_title(title, fontsize=8)
    axs[0].set_ylabel(ylabel, fontsize=8); axs[0].legend(fontsize=6)
    fig.tight_layout(pad=0.3); fig.savefig(f"results/figures/{fname}.pdf"); plt.close(fig)
ntrain_fig("pred_nrmse", "ntrain_pred", "pred_nrmse (median)")

# ---- Fig: lambda sweep ----
fig, ax = plt.subplots(figsize=(3.4, 2.5)); LAM = [0.01, 0.03, 0.1, 0.3, 1.0]
for task, c in [("pendulum", "#1b6ca8"), ("vdp", "#d9822b")]:
    v = [np.array([r["metrics"]["pred_nrmse"] for r in rows if r["group"] == f"sweep_lam_{task}" and r["config"]["lam"] == l]) for l in LAM]
    ax.plot(LAM, [np.median(x) for x in v], "o-", color=c, label=task, ms=3); ax.fill_between(LAM, [x.min() for x in v], [x.max() for x in v], color=c, alpha=0.15, lw=0)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xticks(LAM); ax.set_xticklabels([str(l) for l in LAM]); ax.xaxis.set_minor_locator(NullLocator()); ax.set_xlabel("threshold $\\lambda$"); ax.set_ylabel("pred_nrmse, median (band: min--max)"); ax.legend(fontsize=6)
fig.tight_layout(); fig.savefig("results/figures/lam_pend.pdf"); plt.close(fig)

# ---- extra tables ----
from scipy import stats
def tex(fname, hdr, lines, cols):
    open(f"results/tables/{fname}.tex", "w").write("\\begin{tabular}{" + cols + "}\\toprule\n" + hdr + " \\\\\\midrule\n" + "\n".join(l if l.startswith("\\midrule") else l + " \\\\" for l in lines) + "\n\\bottomrule\\end{tabular}\n")
def pfmt(p):
    return "$<$0.001" if p < 0.001 else f"{p:.3f}"
def sw(task, name, n, metric):
    rs = sorted([r for r in rows if r["group"] == f"sweep_ntrain_{task}" and r["name"] == name and r["config"]["ntrain"] == n], key=lambda r: r["seed"])
    return np.array([r["metrics"][metric] for r in rs])
S, M, D, O = SYS
# (a) per-seed pred_nrmse on Van der Pol in the two settings where SINDy seeds diverge
L = ["\\multicolumn{8}{l}{\\emph{noise 0.1, 1000 transitions (group main)}}"]
for s in SYS[:3]:
    v = get("main", s, "vdp_noise0.1", "pred_nrmse"); L.append(f"{SHORT[s]} & " + " & ".join(f"{x:.3f}" for x in v) + f" & {np.mean(v):.3f} & {np.median(v):.3f}")
L += ["\\midrule", "\\multicolumn{8}{l}{\\emph{noise 0.05, 200 transitions (group sweep\\_ntrain\\_vdp)}}"]
for s in SYS[:3]:
    v = sw("vdp", s, 200, "pred_nrmse"); L.append(f"{SHORT[s]} & " + " & ".join(f"{x:.3f}" for x in v) + f" & {np.mean(v):.3f} & {np.median(v):.3f}")
tex("vdp_seeds", "System & s0 & s1 & s2 & s3 & s4 & mean & med.", L, "lccccccc")
# (b) paired LQR cost relative to the oracle (identified minus oracle, in percent of oracle), 5 seeds
L = []
for task in ["pendulum", "vdp"]:
    for nz in ["0.0", "0.02", "0.05", "0.1"]:
        o = np.array(get("main", O, f"{task}_noise{nz}", "lqr_cost")); cells = []
        for s in SYS[:3]:
            v = np.array(get("main", s, f"{task}_noise{nz}", "lqr_cost")); d = 100 * (v - o) / o
            cells.append(f"{d.mean():.1f} ({(d > 0).sum()}/5)")
        L.append(f"{task} & {nz} & " + " & ".join(cells))
tex("paired_lqr", "Task & noise & SINDy & MLP & DMDc", L, "llccc")
# (c) noise sweep: medians, median paired gap, seeds in which SINDy is better and paired t-test p
L = []
for task in ["pendulum", "vdp"]:
    for nz in ["0.0", "0.02", "0.05", "0.1"]:
        a, b, c = (np.array(get("main", s, f"{task}_noise{nz}", "pred_nrmse")) for s in SYS[:3])
        L.append(f"{task} & {nz} & {np.median(a):.3f} & {np.median(b):.3f} & {np.median(b - a):.3f} & {(a < b).sum()}/5 ({pfmt(stats.ttest_rel(a, b).pvalue)}) & {(a < c).sum()}/5 ({pfmt(stats.ttest_rel(a, c).pvalue)})")
tex("noise_gap", "Task & noise & SINDy & MLP & gap & vs MLP ($p$) & vs DMDc ($p$)", L, "llccccc")
# (d) SINDy ablations: mean +- std of pred_nrmse, mean F1 and terms, and paired comparison with full SINDy
L = []
AB = {S: "full", "SINDy w/o trig library": "no trig", "SINDy + SG smoothing": "SG", "SINDy + SG smoothing, lam 0.3": "SG, $\\lambda{=}0.3$"}
for task, title in [("pendulum", "pendulum"), ("vdp", "Van der Pol")]:
    t = f"{task}_noise0.05"
    base = {m: np.array(get("abl_sindy", S, t, m)) for m in ["pred_nrmse", "lqr_cost"]}
    L.append("\\multicolumn{6}{l}{\\emph{" + title + "}}")
    for nm in AB:
        v = {m: np.array(get("abl_sindy", nm, t, m)) for m in ["pred_nrmse", "lqr_cost", "n_terms"]}
        f1 = [r["metrics"].get("support_f1") for r in rows if r["group"] == "abl_sindy" and r["name"] == nm and r["task"] == t]
        row = f"{AB[nm]} & {v['pred_nrmse'].mean():.3f} $\\pm$ {v['pred_nrmse'].std(ddof=1):.3f} & " + ("--" if f1[0] is None else f"{np.mean(f1):.3f}") + f" & {v['n_terms'].mean():.1f}"
        if nm == S: row += " & -- & --"
        else:
            pp = stats.ttest_rel(v["pred_nrmse"], base["pred_nrmse"]).pvalue; d = v["lqr_cost"] - base["lqr_cost"]
            row += f" & {(v['pred_nrmse'] > base['pred_nrmse']).sum()}/5 ({pfmt(pp)}) & {d.mean():+.3f} ({(d > 0).sum()}/5)"
        L.append(row)
    if task == "pendulum": L.append("\\midrule")
tex("abl_combined", "Variant & pred\\_nrmse & F1 & terms & worse ($p$) & $\\Delta$LQR (worse)", L, "lccccc")
# (e) data-size sweep, rows = size: mean (median) per model, seeds in which SINDy beats the MLP, paired p
for metric, fname in [("pred_nrmse", "ntrain_pred"), ("lqr_cost", "ntrain_lqr")]:
    L = []
    for task in ["pendulum", "vdp"]:
        for n in NT:
            v = [sw(task, s, n, metric) for s in SYS[:3]]
            row = f"{task} & {n} & " + " & ".join(f"{x.mean():.3f} ({np.median(x):.3f})" for x in v)
            if metric == "pred_nrmse": row += f" & {(v[0] < v[1]).sum()}/5 ({pfmt(stats.ttest_rel(v[0], v[1]).pvalue)})"
            L.append(row)
        if task == "pendulum": L.append("\\midrule")
    tex(fname, "Task & $N$ & SINDy & MLP & DMDc" + (" & vs MLP ($p$)" if metric == "pred_nrmse" else ""), L, "llccc" + ("c" if metric == "pred_nrmse" else ""))
# (f) threshold sweep, rows = lambda
L = []
for task in ["pendulum", "vdp"]:
    for l in [0.01, 0.03, 0.1, 0.3, 1.0]:
        rs = [r["metrics"] for r in rows if r["group"] == f"sweep_lam_{task}" and r["config"]["lam"] == l]
        g = lambda m: np.array([x[m] for x in rs])
        L.append(f"{task} & {l} & {g('pred_nrmse').mean():.3f} ({np.median(g('pred_nrmse')):.3f}) & {g('lqr_cost').mean():.3f} & {g('support_f1').mean():.3f} & {g('n_terms').mean():.1f} ({int(g('n_terms').min())})")
    if task == "pendulum": L.append("\\midrule")
tex("lam", "Task & $\\lambda$ & pred\\_nrmse & LQR cost & F1 & terms (min)", L, "llcccc")
# (g) diagnostic of the runs whose LQR cost equals the cap (group diag_lqr, kind sanity)
allrows = [json.loads(l) for l in open("results/runs.jsonl")]
L = []
for r in sorted([r for r in allrows if r["group"] == "diag_lqr" and r["status"] == "ok"], key=lambda r: (r["config"]["ntrain"], r["seed"])):
    m = r["metrics"]
    L.append(f"{r['config']['ntrain']} & {r['seed']} & {'yes' if m['riccati_ok'] else 'no'} & {int(m['n_capped'])}/10 & {m['model_B2']:.3f} & {m['true_B2']:.3f} & {m['true_cl_radius']:.3f}")
tex("diag_lqr", "$N$ & seed & DARE & capped & $\\hat B_2$ & $B_2$ & $\\rho$", L, "llccccc")
print("figs/tables done")
