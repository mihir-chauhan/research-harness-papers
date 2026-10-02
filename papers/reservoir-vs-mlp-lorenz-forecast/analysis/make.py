"""(A paired p-value is shown as n/a when the per-seed differences have zero variance.)
Tables, figures and hypothesis numbers from results/runs.jsonl (ok rows that are not superseded).
Sweeps use seeds 0-2; the tuned default point of each sweep is the group-'main' run of the same seed.
Writes results/tables/{main_systems,main_ablation,tests,sweep_*}.tex, results/figures/*.pdf, results/summary.md.
Run after `rh table --group main ...` and `rh compare ...` (see analysis/build.sh), whose outputs it reformats."""
import json, re, sys, numpy as np, pandas as pd, matplotlib
from scipy import stats
matplotlib.use("Agg"); import matplotlib.pyplot as plt

# ---- registry (append-only; a control row retires earlier ok rows of the same group and name)
rows = []
for l in open("results/runs.jsonl"):
    r = json.loads(l)
    if r.get("kind") == "control":
        for p in rows:
            if p["group"] == r["group"] and p["name"] == r["name"] and p["status"] == "ok": p["status"] = "superseded"
        continue
    rows.append(r)
rows = [r for r in rows if r["status"] == "ok" and r["group"] in ("main", "sweep_rho", "sweep_size", "sweep_ntrain", "sweep_steps")]
tuned = json.load(open("method/tuned.json")); KEY = {"ESN": "esn", "MLP delay": "mlp", "GRU": "gru"}
D = pd.DataFrame([dict(group=r["group"], name=r["name"], task=r["task"], seed=r["seed"], cfg=r["config"], **r["metrics"]) for r in rows])
for k in ["rho", "size", "steps"]:   # value of a swept hyperparameter: the override if present, else the tuned/default value
    D[k] = [c.get(k, tuned.get(f"{KEY.get(n)}/{t}", {}).get(k, 500 if k == "size" else None)) for c, n, t in zip(D.cfg, D.name, D.task)]
D["n"] = D.cfg.map(lambda c: c["n_train"])
TASKS = ["lorenz63", "lorenz96"]; TL = {"lorenz63": "L63", "lorenz96": "L96"}; SY = ["ESN", "MLP delay", "GRU"]
main = D[D.group == "main"]; main3 = main[main.seed <= 2]
summ = []


def cell(df, metric):
    x = df[metric].to_numpy(float)
    return (x.mean(), x.std(ddof=1) if len(x) > 1 else 0.0, len(x)) if len(x) else (np.nan, np.nan, 0)


def tab(df, key, vals, names, metric):
    return {(t, s): [cell(df[(df.task == t) & (df.name == s) & (df[key] == v)], metric) for v in vals] for t in TASKS for s in names}


def write(cols, vals, key, fn, prec=2, ratio=False):
    """cols: list of (header, list of (mean, std, n)); one row per swept value."""
    ln = ["\\begin{tabular}{r" + "c" * len(cols) + "}\\toprule", " & ".join([key] + [h for h, _ in cols]) + "\\\\", "\\midrule"]
    for i, v in enumerate(vals):
        ln.append(" & ".join([str(v)] + [("--" if c[i][2] == 0 else f"{c[i][0]:.{prec}f} $\\pm$ {c[i][1]:.{prec}f}") for _, c in cols]) + "\\\\")
    if ratio:
        ln += ["\\midrule", " & ".join(["max/min"] + [(f"{max(x[0] for x in c)/min(x[0] for x in c):.2f}" if "VPT" in h else "") for h, c in cols]) + "\\\\"]
    ln.append("\\bottomrule\\end{tabular}"); open(f"results/tables/{fn}.tex", "w").write("\n".join(ln) + "\n")


def paired(a, b, metric):
    a, b = a.sort_values("seed"), b.sort_values("seed"); assert list(a.seed) == list(b.seed), "seeds differ"
    x, y = a[metric].to_numpy(float), b[metric].to_numpy(float)
    p = float(stats.ttest_rel(x, y).pvalue) if np.std(x - y) > 0 else float("nan")
    return x.mean(), y.mean(), x.mean() - y.mean(), p, len(x)


def fmt_p(p): return "n/a" if (np.isnan(p) or p == 0) else (f"{p:.3f}" if p >= 0.001 else f"{p:.1e}")


# ---- sweeps with the default point from main (seeds 0-2)
esn3 = main3[main3.name == "ESN"]
r = pd.concat([D[D.group == "sweep_rho"], esn3]); rv = [0.1, 0.4, 0.7, 1.0, 1.4, 2.0]
Lr, Lrc = tab(r, "rho", rv, ["ESN"], "vpt"), tab(r, "rho", rv, ["ESN"], "clim_ok")
write([(f"{TL[t]} VPT", Lr[(t, "ESN")]) for t in TASKS] + [(f"{TL[t]} clim\\_ok", Lrc[(t, "ESN")]) for t in TASKS], rv, "$\\rho$", "sweep_rho", ratio=True)
for t in TASKS:
    m = [x[0] for x in Lr[(t, "ESN")]]
    summ.append(f"H3 {t}: rho {rv} vpt means {np.round(m, 3).tolist()} ratio best/worst {max(m)/min(m):.2f}; clim_ok {np.round([x[0] for x in Lrc[(t, 'ESN')]], 2).tolist()}")
    for a_, b_ in [(0.1, 0.4)]:
        for met in ["vpt", "clim_ok"]:
            q = paired(r[(r.task == t) & (r.rho == a_)], r[(r.task == t) & (r.rho == b_)], met)
            summ.append(f"   {t} rho {a_} vs {b_} {met}: {q[0]:.3f} vs {q[1]:.3f}, paired p={fmt_p(q[3])} (n={q[4]})")

s = pd.concat([D[D.group == "sweep_size"], esn3]); sv = [100, 250, 500, 1000, 2000]
Ls, Lsc = tab(s, "size", sv, ["ESN"], "vpt"), tab(s, "size", sv, ["ESN"], "clim_ok")
write([(f"{TL[t]} VPT", Ls[(t, "ESN")]) for t in TASKS] + [(f"{TL[t]} clim\\_ok", Lsc[(t, "ESN")]) for t in TASKS], sv, "$N$", "sweep_size")
for t in TASKS:
    summ.append(f"H4 {t}: size {sv} vpt means {np.round([x[0] for x in Ls[(t, 'ESN')]], 3).tolist()}; clim_ok {np.round([x[0] for x in Lsc[(t, 'ESN')]], 2).tolist()}")
    q = paired(s[(s.task == t) & (s["size"] == 1000)], s[(s.task == t) & (s["size"] == 100)], "vpt")
    summ.append(f"   {t} N=1000 vs N=100 vpt: {q[0]:.3f} vs {q[1]:.3f}, paired p={fmt_p(q[3])} (n={q[4]})")

nt = pd.concat([D[D.group == "sweep_ntrain"], main3[main3.name.isin(SY)]]); nv = [500, 2000, 5000, 10000]
Ln, Lnc = tab(nt, "n", nv, SY, "vpt"), tab(nt, "n", nv, SY, "clim_ok")
hdr = lambda L: [(f"{TL[t]} {sy.split()[0]}", L[(t, sy)]) for t in TASKS for sy in SY]
write(hdr(Lnc), nv, "$n_{\\rm train}$", "sweep_ntrain_clim")
tl = ["\\begin{tabular}{r" + "ccccc" * 2 + "}\\toprule", " & ".join(["$n_{\\rm train}$"] + [f"{TL[t]} {x}" for t in TASKS for x in ["ESN", "MLP", "GRU", "$\\Delta$", "$p$"]]) + "\\\\", "\\midrule"]
for i, n in enumerate(nv):
    c = [str(n)]
    for t in TASKS:
        q = paired(nt[(nt.task == t) & (nt.n == n) & (nt.name == "ESN")], nt[(nt.task == t) & (nt.n == n) & (nt.name == "MLP delay")], "vpt")
        c += [f"{Ln[(t, sy)][i][0]:.2f} $\\pm$ {Ln[(t, sy)][i][1]:.2f}" for sy in SY]
        c += [f"{q[2]:+.2f}", fmt_p(q[3])]; summ.append(f"ntrain {t} n={n}: ESN {q[0]:.3f} vs MLP {q[1]:.3f} delta {q[2]:+.3f} paired p={fmt_p(q[3])} (n={q[4]})")
    tl.append(" & ".join(c) + "\\\\")
tl.append("\\bottomrule\\end{tabular}"); open("results/tables/sweep_ntrain.tex", "w").write("\n".join(tl) + "\n")
for t in TASKS:
    for sy in SY:
        m = [x[0] for x in Ln[(t, sy)]]; n80 = next(v for v, x in zip(nv, m) if x >= 0.8 * m[-1])
        summ.append(f"H5 {t} {sy}: n {nv} vpt {np.round(m, 2).tolist()} clim_ok {np.round([x[0] for x in Lnc[(t, sy)]], 2).tolist()} n80={n80}")

st = pd.concat([D[D.group == "sweep_steps"], main3[main3.name.isin(["MLP delay", "GRU"])]])
stv = {"MLP delay": [4000, 8000, 16000, 32000], "GRU": [3000, 6000, 12000]}
sl = ["\\begin{tabular}{lr" + "cccc" * 2 + "}\\toprule", " & ".join(["System", "steps"] + [f"{TL[t]} {x}" for t in TASKS for x in ["VPT", "$p$", "ESN/sys.", "fit (s)"]]) + "\\\\", "\\midrule"]
for sy in ["MLP delay", "GRU"]:
    Lv, Lf = tab(st, "steps", stv[sy], [sy], "vpt"), tab(st, "steps", stv[sy], [sy], "fit_seconds")
    for i, v in enumerate(stv[sy]):
        c = [sy.split()[0], str(v)]
        for t in TASKS:
            tu = tuned[f"{KEY[sy]}/{t}"]["steps"]; cur = st[(st.task == t) & (st.name == sy) & (st.steps == v)]
            e = paired(esn3[esn3.task == t], cur, "vpt")
            if v == tu: ps = "tuned"
            else:
                q = paired(cur, st[(st.task == t) & (st.name == sy) & (st.steps == tu)], "vpt"); ps = fmt_p(q[3])
            c += [f"{Lv[(t, sy)][i][0]:.2f} $\\pm$ {Lv[(t, sy)][i][1]:.2f}", ps, f"{e[0]/e[1]:.2f}", f"{Lf[(t, sy)][i][0]:.1f}"]
            summ.append(f"steps {t} {sy} steps={v} (tuned {tu}): vpt {e[1]:.3f} p vs tuned {ps}; ESN(seeds 0-2) {e[0]:.3f} ratio ESN/sys {e[0]/e[1]:.2f} (paired p ESN vs sys {fmt_p(e[3])}); fit_s {Lf[(t, sy)][i][0]:.1f}")
        sl.append(" & ".join(c) + "\\\\")
    if sy == "MLP delay": sl.append("\\midrule")
sl.append("\\bottomrule\\end{tabular}"); open("results/tables/sweep_steps.tex", "w").write("\n".join(sl) + "\n")

# ---- main-group ratios, orderings and per-seed extremes
for t in TASKS:
    mt = main[main.task == t]; g = mt.groupby("name")[["vpt", "clim_ok", "clim_w1", "blowup", "fit_seconds"]].mean()
    summ.append(f"main {t}: vpt order {g.loc[SY].vpt.sort_values(ascending=False).round(3).to_dict()}; clim_ok order {g.loc[SY].clim_ok.sort_values(ascending=False).round(3).to_dict()}")
    summ.append(f"   ratios ESN/MLP {g.vpt['ESN']/g.vpt['MLP delay']:.2f} ESN/GRU {g.vpt['ESN']/g.vpt['GRU']:.2f} MLP/ESN {g.vpt['MLP delay']/g.vpt['ESN']:.2f}")
    summ.append(f"   fit_seconds {g.fit_seconds.round(2).to_dict()}")
    summ.append(f"   clim_w1_max over seeds {mt.groupby('name').clim_w1_max.max().round(3).to_dict()}")

# ---- paired tests among main-group systems, from the rh compare CSVs (delta = ref - other)
SHORT = {"MLP delay": "MLP", "ESN without squared features": "ESN no sq.", "GRU without input noise": "GRU no noise", "True system": "truth"}
PAIRS = [("ESN", "MLP delay"), ("ESN", "GRU"), ("ESN", "ESN without squared features"), ("GRU", "GRU without input noise")]
ln = ["\\begin{tabular}{lllrrrrr}\\toprule", " &  &  & \\multicolumn{3}{c}{vpt} & \\multicolumn{2}{c}{clim\\_ok}\\\\", "Task & A & B & A $-$ B & A/B & $p$ & A $-$ B & $p$\\\\", "\\midrule"]
for t in TASKS:
    for a_, b_ in PAIRS:
        c = [TL[t], SHORT.get(a_, a_), SHORT.get(b_, b_)]
        for met in ["vpt", "clim_ok"]:
            x = pd.read_csv(f"results/tables/compare_main_{met}_ref{a_.split()[0]}.csv")
            x = x[(x.task == t) & (x.ref == a_) & (x["name"] == b_)].iloc[0]; d = "n/a" if np.isnan(x.cohen_d) else f"{x.cohen_d:.1f}"
            c += [f"{x.delta:+.2f}"] + ([f"{x.ref_mean / x['mean']:.2f}"] if met == "vpt" else []) + [fmt_p(x.paired_p)]
            summ.append(f"compare {t} {met}: {a_} {x.ref_mean:.3f} vs {b_} {x['mean']:.3f} delta {x.delta:+.3f} paired p={fmt_p(x.paired_p)} welch p={fmt_p(x.welch_p)} d={d}")
        ln.append(" & ".join(c) + "\\\\")
    if t == TASKS[0]: ln.append("\\midrule")
ln.append("\\bottomrule\\end{tabular}"); open("results/tables/tests.tex", "w").write("\n".join(ln) + "\n")

# ---- rh table outputs: drop the best/second marks (ties and hidden rows make them misleading), shorten names
for src, dst in [("main_systems_raw", "main_systems"), ("main_ablation_raw", "main_ablation")]:
    try: x = open(f"results/tables/{src}.tex").read()
    except FileNotFoundError: continue
    x = re.sub(r"\\(?:textbf|underline)\{((?:[^{}]|\{[^{}]*\})*)\}", r"\1", x)
    for a_, b_ in [("lorenz63", "L63"), ("lorenz96", "L96"), ("fit\\_seconds", "fit (s)"), ("MLP delay", "MLP (delay)"), ("without squared features", "no squares"), ("without input noise", "no noise")]:
        x = x.replace(a_, b_)
    open(f"results/tables/{dst}.tex", "w").write(x)

# ---- figures
cm = {"ESN": "#1f77b4", "MLP delay": "#d95f02", "GRU": "#2ca02c"}


def fig(name, series, xlab, logx=True, ylab="VPT (Lyapunov times)", legend=True, ticks=None):
    f, ax = plt.subplots(1, 2, figsize=(3.5, 1.7))
    for a, t in zip(ax, TASKS):
        for sy, xs, L in series:
            m = np.array([x[0] for x in L[(t, sy)]]); sd = np.array([x[1] for x in L[(t, sy)]])
            a.errorbar(xs, m, sd, marker="o", ms=3, lw=1, capsize=2, label=sy, color=cm[sy])
        a.set_title({"lorenz63": "Lorenz-63", "lorenz96": "Lorenz-96"}[t], fontsize=7); a.set_xlabel(xlab, fontsize=7); a.tick_params(labelsize=6)
        if logx:
            a.set_xscale("log"); tk = ticks or series[0][1]; a.set_xticks(tk); a.set_xticklabels([f"{v:g}" if v < 1000 else f"{v // 1000:g}k" for v in tk]); a.minorticks_off()
        a.grid(alpha=.3); a.set_ylim(bottom=0)
    ax[0].set_ylabel(ylab, fontsize=7)
    if legend: ax[0].legend(fontsize=5)
    f.tight_layout(); f.savefig(f"results/figures/{name}.pdf"); plt.close(f)


fig("sweep_rho_fig", [("ESN", rv, Lr)], "spectral radius $\\rho$", legend=False, ticks=[0.1, 0.4, 1.0, 2.0])
fig("sweep_size_fig", [("ESN", sv, Ls)], "reservoir size $N$", legend=False)
fig("sweep_ntrain_fig", [(sy, nv, Ln) for sy in SY], "training samples $n_{\\rm train}$")
fig("sweep_steps_fig", [(sy, stv[sy], tab(st, "steps", stv[sy], [sy], "vpt")) for sy in ["MLP delay", "GRU"]], "optimiser steps", ticks=[3000, 6000, 12000, 32000])
f, ax = plt.subplots(1, 2, figsize=(3.5, 1.8))
for a, t in zip(ax, TASKS):
    for i, sy in enumerate(SY):
        x = main[(main.task == t) & (main.name == sy)].vpt.to_numpy()
        a.bar(i, x.mean(), yerr=x.std(ddof=1), color=cm[sy], capsize=2, width=0.65); a.plot([i] * len(x), x, "k.", ms=2)
    a.set_xticks(range(3)); a.set_xticklabels(["ESN", "MLP", "GRU"], fontsize=6); a.tick_params(labelsize=6)
    a.set_title({"lorenz63": "Lorenz-63", "lorenz96": "Lorenz-96"}[t], fontsize=7); a.grid(alpha=.3, axis="y")
ax[0].set_ylabel("VPT (Lyapunov times)", fontsize=7); f.tight_layout(); f.savefig("results/figures/main_vpt_fig.pdf"); plt.close(f)

open("results/summary.md", "w").write("\n".join(summ) + "\n"); print("\n".join(summ))
