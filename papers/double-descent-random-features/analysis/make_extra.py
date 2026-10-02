"""Derived tables and figures; reads only results/runs.jsonl and results/raw/*.csv written by the runs."""
import json, glob, os
import numpy as np, pandas as pd
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

rows = []
for l in open("results/runs.jsonl"):
    r = json.loads(l)
    if r["status"] != "ok" or r["group"] == "sanity": continue
    d = dict(group=r["group"], name=r["name"], task=r["task"], seed=r["seed"], **r["metrics"])
    if r["group"] == "sweep_lambda": d["lam"] = r["config"]["lam"]
    rows.append(d)
df = pd.DataFrame(rows)
SYN = ["synth_n0", "synth_n0.25", "synth_n0.5", "synth_n1"]; DIG = ["digits_n0", "digits_n0.15", "digits_n0.3", "digits_n0.6"]
TASKS = SYN + DIG
NOISE = {t: float(t.split("_n")[1]) for t in TASKS}
main = df[df.group == "main"]; out = open("results/analysis.md", "w")
def P(*a): print(*a); print(*a, file=out)
def ms(x, p=3): return f"{np.mean(x):.{p}f} $\\pm$ {np.std(x, ddof=1):.{p}f}"
def sh(task): return task.replace("synth_n", "syn ").replace("digits_n", "dig ")
def g(name, task, m, d=main): return d[(d.name == name) & (d.task == task)].sort_values("seed")[m].values
def rv(key, spec=""): return "\\rhval{" + key + (":" + spec if spec else "") + "}"   # paper cells print registry values (rh values), never a number formatted here
def lamkey(L, t, m, st):   # registry key of a fixed-ridge cell: lam=0 is MinNorm, 1e-2 the main FixedRidge, the rest the sweep
    if L == 0: return f"main/minnorm/{t}/{m}/{st}"
    if L == 1e-2: return f"main/fixedridge/{t}/{m}/{st}"
    return f"sweep_lambda/fixedridge-sweep@lam={json.dumps(int(L) if float(L).is_integer() else L)}/{t}/{m}/{st}"
def wr(path, header, body, align):
    with open(path, "w") as f:
        f.write("\\begin{tabular}{" + align + "}\\hline\n" + " & ".join(header) + " \\\\ \\hline\n")
        for b in body: f.write(" & ".join(b) + " \\\\\n")
        f.write("\\hline\\end{tabular}\n")

# --- H1/H2: min-norm peak vs noise
body = []
for t in TASKS:
    pk, lg, bs = g("MinNorm", t, "peak_mse"), g("MinNorm", t, "log10_peak_mse"), g("MinNorm", t, "best_mse")
    k = f"main/minnorm/{t}/"
    body.append([sh(t), rv(k + "peak_pos/median", "2"), rv(k + "log10_peak_mse/mean", "2") + " $\\pm$ " + rv(k + "log10_peak_mse/std", "2"),
                 rv(k + "peak_mse/mean"), rv(k + "peak_mse/median"), rv(k + "best_mse/mean", "3")])
    P("H1/H2", t, "peak_pos all", set(g("MinNorm", t, "peak_pos")), "mean peak", np.mean(pk), "median", np.median(pk))
wr("results/tables/noise_minnorm.tex", ["Task", "pos", "$\\log_{10}$ peak", "mean peak", "median peak", "best"], body, "lccccc")
for ds in (SYN, DIG):
    lo, hi = g("MinNorm", ds[0], "log10_peak_mse"), g("MinNorm", ds[-1], "log10_peak_mse")
    w = stats.wilcoxon(hi, lo, alternative="greater"); tt = stats.ttest_rel(hi, lo)
    P("H2 wilcoxon one-sided hi>lo on log10 peak", ds[0], "p=", w.pvalue, "paired t p=", tt.pvalue, "means", [np.mean(g("MinNorm", t, "peak_mse")) for t in ds])
    P("   raw peak paired wilcoxon", stats.wilcoxon(g("MinNorm", ds[-1], "peak_mse"), g("MinNorm", ds[0], "peak_mse"), alternative="greater").pvalue)

# the Wilcoxon p-values stay in results/analysis.md only: `rh compare` has no cross-task test, so the paper does not print them

# --- H3: sweep over fixed lambda (+ MinNorm as lam=0 and FixedRidge main as 1e-2)
LAMS = [0, 1e-6, 1e-4, 1e-3, 1e-2, 1e-1, 1, 10]
def lamrows(t):
    res = {}
    for L in LAMS:
        if L == 0: d = main[(main.name == "MinNorm") & (main.task == t)]
        elif L == 1e-2: d = main[(main.name == "FixedRidge") & (main.task == t)]
        else: d = df[(df.group == "sweep_lambda") & (df.task == t) & np.isclose(df.lam, L)]
        res[L] = d.sort_values("seed")
    return res
body, body2 = [], []
sweep = {t: lamrows(t) for t in TASKS}
for t in TASKS:
    body.append([sh(t)] + [rv(lamkey(L, t, "peak_mse", "mean")) for L in LAMS])
    body2.append([sh(t)] + [f"{sweep[t][L].peak_pos.median():.2f}" for L in LAMS])
    m = [sweep[t][L].peak_mse.mean() for L in LAMS]
    P("H3", t, "mean peak by lam", [round(x, 4) for x in m], "nonincreasing:", all(m[i + 1] <= m[i] for i in range(len(m) - 1)),
      "bump", [round(sweep[t][L].bump_rel.mean(), 4) for L in LAMS], "pos", [sweep[t][L].peak_pos.tolist() for L in LAMS])
hdr = ["Task", "0", "$10^{-6}$", "$10^{-4}$", "$10^{-3}$", "$10^{-2}$", "$10^{-1}$", "1", "10"]
wr("results/tables/sweep_peak.tex", hdr, body, "l" + "c" * 8)
wr("results/tables/sweep_pos.tex", hdr, body2, "l" + "c" * 8)
body = []
for t in TASKS:
    body.append([sh(t)] + [f"{sweep[t][L].bump_rel.mean():.3g}" for L in LAMS])
wr("results/tables/sweep_bump.tex", hdr, body, "l" + "c" * 8)
# also final (large width) error vs lam for context
for t in TASKS: P("sweep final_mse", t, [round(sweep[t][L].final_mse.mean(), 4) for L in LAMS])

# --- H4/H5: bump of tuned systems; ablation
abl = df[df.group == "abl_tuning"]
body = []
for t in TASKS:
    tu, gl, mn = g("TunedRidge", t, "bump_rel"), g("GlobalRidge", t, "bump_rel"), g("MinNorm", t, "bump_rel")
    lo, v5 = g("TunedRidge-LOO", t, "bump_rel", abl), g("TunedRidge-val50", t, "bump_rel", abl)
    p_b = stats.ttest_rel(tu, mn).pvalue; p_l = stats.ttest_rel(g("TunedRidge", t, "log10_peak_mse"), g("MinNorm", t, "log10_peak_mse")).pvalue
    body.append([sh(t), rv(f"main/tunedridge/{t}/bump_rel/mean", "4"), rv(f"main/tunedridge/{t}/bump_rel/max", "4"), rv(f"main/globalridge/{t}/bump_rel/mean", "4"),
                 rv(f"abl_tuning/tunedridge-loo/{t}/bump_rel/mean", "4"), rv(f"abl_tuning/tunedridge-val50/{t}/bump_rel/mean", "4"),
                 rv(f"cmp/main/minnorm/{t}/bump_rel/paired_p", "2"), rv(f"cmp/main/minnorm/{t}/log10_peak_mse/paired_p", "4")])   # p-values: `rh compare` (ref TunedRidge)
    P("H4", t, "tuned bump mean/max", tu.mean(), tu.max(), tu.round(4), "global", gl.mean(), "loo", lo.mean(), lo.max(), "val50", v5.mean(), v5.max(), "p_bump", p_b, "p_logpeak", p_l)
wr("results/tables/h4.tex", ["Task", "Tuned", "Tuned max", "Global", "LOO", "val50", "$p_{bump}$", "$p_{peak}$"], body, "l" + "c" * 7)

body = []
for t in TASKS:
    c = []
    for nm, d in (("TunedRidge", main), ("TunedRidge-val50", abl), ("TunedRidge-LOO", abl)):
        c += [ms(g(nm, t, "bump_rel", d), 3), f"{g(nm, t, 'final_mse', d).mean():.3f}"]
    body.append([sh(t)] + c)
    P("abl final", t, [round(g(nm, t, "final_mse", d).mean(), 4) for nm, d in (("TunedRidge", main), ("TunedRidge-val50", abl), ("TunedRidge-LOO", abl), ("GlobalRidge", main))],
      "peak_mse", [round(g(nm, t, "peak_mse", d).mean(), 4) for nm, d in (("TunedRidge", main), ("TunedRidge-val50", abl), ("TunedRidge-LOO", abl))])
wr("results/tables/abl_tuning_tab.tex", ["Task", "val200 bump", "final", "val50 bump", "final", "LOO bump", "final"], body, "l" + "c" * 6)

# --- digits accuracy
body = []
for t in DIG:
    body.append([sh(t)] + [f"{g(n, t, m).mean():.3f}" for n in ("MinNorm", "TunedRidge") for m in ("acc_thresh", "acc_final", "acc_best")])
wr("results/tables/acc.tex", ["Task", "Min thr", "Min 25", "Min best", "Tun thr", "Tun 25", "Tun best"], body, "l" + "c" * 6)
P("acc", body)

# --- lambda chosen
for t in TASKS:
    tu = main[(main.name == "TunedRidge") & (main.task == t)]
    P("lam tuned", t, "thr", tu.log10_lam_thresh.mean(), "final", tu.log10_lam_final.mean())

# --- figures
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
C = {"MinNorm": "#C0392B", "FixedRidge": "#E69F00", "GlobalRidge": "#0072B2", "TunedRidge": "#009E73"}
def curves(pattern_fn, seeds=range(5)):
    return np.array([pd.read_csv(pattern_fn(s)).value.values for s in seeds]), pd.read_csv(pattern_fn(0)).step.values
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.5))
for a, t in zip(ax, ["synth_n0.5", "digits_n0.3"]):
    for nm in C:
        M, x = curves(lambda s: f"results/raw/curve_main_{nm}_{t}_s{s}.csv")
        a.plot(x, M.mean(0), "-o", ms=2.5, lw=1.2, color=C[nm], label=nm)
    a.axvline(1, color="gray", ls=":", lw=0.8); a.set_xscale("log"); a.set_yscale("log")
    a.set_xlabel("features / samples (N/n)"); a.set_title(t.replace("_n", ", noise sd "), fontsize=8)
ax[0].set_ylabel("test MSE (mean of 5 seeds)"); ax[0].legend(frameon=False, fontsize=7)
plt.tight_layout(); plt.savefig("results/figures/fig_curves.pdf"); plt.close()

fig, ax = plt.subplots(1, 2, figsize=(3.4, 2.4), sharey=True)
for a, ds, nm_ in zip(ax, (SYN, DIG), ("synthetic", "digits")):
    for nm in ("MinNorm", "TunedRidge"):
        v = np.array([g(nm, t, "log10_peak_mse") for t in ds]); x = [NOISE[t] for t in ds]
        a.errorbar(x, v.mean(1), v.std(1, ddof=1), marker="o", ms=3, lw=1.2, capsize=2, color=C[nm], label=nm)
    a.set_title(nm_, fontsize=8); a.set_xlabel("label-noise sd")
ax[0].set_ylabel("$\\log_{10}$ peak test MSE"); ax[0].legend(frameon=False, fontsize=7)
plt.tight_layout(); plt.savefig("results/figures/fig_noise.pdf"); plt.close()

fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.3))
xs = np.arange(len(LAMS))
for t in TASKS:
    ls = "-" if t.startswith("synth") else "--"; col = plt.cm.viridis(0.85 * (NOISE[t] / (1.0 if t.startswith('synth') else 0.6)))
    ax[0].plot(xs, [np.log10(sweep[t][L].peak_mse.mean()) for L in LAMS], ls, color=col, lw=1, label=t)
    ax[1].plot(xs, [sweep[t][L].peak_pos.median() for L in LAMS], ls, color=col, lw=1)
for a in ax:
    a.set_xticks(xs); a.set_xticklabels(["0", "-6", "-4", "-3", "-2", "-1", "0", "1"]); a.set_xlabel("$\\log_{10}\\lambda$ (0 = ridgeless)")
ax[0].set_ylabel("$\\log_{10}$ mean peak MSE"); ax[1].set_ylabel("median peak N/n"); ax[1].set_yscale("log")
ax[0].legend(frameon=False, fontsize=6, ncol=2)
plt.tight_layout(); plt.savefig("results/figures/fig_sweep.pdf"); plt.close()

fig, ax = plt.subplots(1, 2, figsize=(3.4, 2.4), sharey=True)
for a, ds, nm_ in zip(ax, (SYN, DIG), ("synthetic", "digits")):
    for k, t in enumerate(ds):
        M, x = curves(lambda s: f"results/raw/lam_main_TunedRidge_{t}_s{s}.csv")
        a.plot(x, M.mean(0), "-", lw=1.2, color=plt.cm.viridis(k / 3), label=f"sd {NOISE[t]:g}")
    a.set_xscale("log"); a.set_xlabel("N/n"); a.set_title(nm_, fontsize=8); a.legend(frameon=False, fontsize=6)
ax[0].set_ylabel("selected $\\log_{10}\\lambda$ (val.)")
plt.tight_layout(); plt.savefig("results/figures/fig_lam.pdf"); plt.close()
