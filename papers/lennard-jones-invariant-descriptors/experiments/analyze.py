"""Builds the tables, figures and test statistics of the paper from results/runs.jsonl (ok, non-superseded rows only).

Every p-value is a two-sided Welch t-test over seeds (scipy ttest_ind, equal_var=False), the test registered in
proposal.md and the `welch_p` column of `rh compare`.
"""
import json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

rows = []
for l in open("results/runs.jsonl"):
    r = json.loads(l)
    if r.get("op") == "supersede":  # control row: retire the earlier rows of (group, name)
        rows = [x for x in rows if not (x["group"] == r["group"] and x["name"] == r["name"])]
        continue
    if r["status"] != "ok": continue
    rows.append(dict(group=r["group"], name=r["name"], seed=r["seed"], n=r["config"].get("n_train"),
                     steps=r["config"].get("steps", 3000), wall=r["provenance"]["duration_s"], **r["metrics"]))
d = pd.DataFrame(rows)
tail = d[d.name == "Energy tail (untruncated)"]
d = d[d.group != "sanity"]
order = ["Raw coords KRR", "Raw coords MLP", "Sorted dist KRR", "Sorted dist MLP", "SymFn-sum KRR",
         "SymFn-sum MLP", "SymFn atomwise MLP (BP-style)"]
short = {"Raw coords KRR": "Raw KRR", "Raw coords MLP": "Raw MLP", "Sorted dist KRR": "Sorted KRR", "Sorted dist MLP": "Sorted MLP",
         "SymFn-sum KRR": "SF KRR", "SymFn-sum MLP": "SF MLP", "Mean predictor": "Mean pred.",
         "SymFn atomwise MLP (BP-style)": "SF atomwise MLP", "SymFn-sum KRR radial-only": "SF KRR radial-only",
         "SymFn-sum linear ridge": "SF linear ridge", "SymFn-sum linear ridge radial-only": "SF lin.\\ ridge rad.-only",
         "Sorted dist linear ridge": "Sorted linear ridge"}
ms = lambda x: f"{np.mean(x):.2f}$\\pm${np.std(x, ddof=1):.2f}"
f3 = lambda x: f"{np.mean(x):.3f} $\\pm$ {np.std(x, ddof=1):.3f}"
def welch(a, b): return stats.ttest_ind(a, b, equal_var=False).pvalue
def sci(v):  # 6.2e-05 -> 6.2\cdot10^{-5}
    if v == 0: return "0"
    if 0.01 <= abs(v) < 1000: return f"{v:.3g}"
    m, e = f"{v:.2e}".split("e")
    return f"${m}\\cdot10^{{{int(e)}}}$"
def pfmt(p): return f"{p:.3f}" if p >= 0.001 else sci(p)
def write(name, L): open(f"results/tables/{name}.tex", "w").write("\n".join(L))
out = []

# ---- learning curve table
lc = d[d.group.isin(["main", "sweep_ntrain"])]
sizes = [50, 150, 500, 1500]
L = ["\\begin{tabular}{l" + "c" * len(sizes) + "}", "\\toprule", "System & " + " & ".join(f"$n$={s}" for s in sizes) + " \\\\", "\\midrule"]
for nm in ["Mean predictor"] + order:
    L.append(short[nm] + " & " + " & ".join(ms(lc[(lc.name == nm) & (lc.n == s)].energy_mae) for s in sizes) + " \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
write("lcurve", L)

# ---- registered Welch tests per training size (H1, H3, H4) and the raw-vs-mean-predictor reference
pairs = [("H1", "Sorted dist KRR", "Raw coords KRR"), ("H1", "SymFn-sum KRR", "Raw coords KRR"),
         ("H1", "Sorted dist MLP", "Raw coords MLP"), ("H1", "SymFn-sum MLP", "Raw coords MLP"),
         ("H3", "SymFn-sum KRR", "Sorted dist KRR"), ("--", "SymFn-sum KRR", "Sorted dist MLP"),
         ("H4", "Raw coords KRR", "Raw coords MLP"), ("H4", "Sorted dist KRR", "Sorted dist MLP"), ("H4", "SymFn-sum KRR", "SymFn-sum MLP"),
         ("ref.", "Raw coords KRR", "Mean predictor"), ("ref.", "Raw coords MLP", "Mean predictor")]
L = ["\\begin{tabular}{llcccc}", "\\toprule", " & A vs.\\ B & " + " & ".join(f"$n$={s}" for s in sizes) + " \\\\", "\\midrule"]
for h, a, b in pairs:
    cells = []
    for s in sizes:
        x, y = lc[(lc.name == a) & (lc.n == s)].energy_mae, lc[(lc.name == b) & (lc.n == s)].energy_mae
        p = welch(x, y)
        cells.append(("A " if x.mean() < y.mean() else "B ") + (f"{p:.3f}" if p >= 0.001 else "$<$0.001"))
        out.append(f"{h} n={s}: {a} {x.mean():.3f} (n={len(x)}) vs {b} {y.mean():.3f} (n={len(y)}), Welch p={p:.3g}")
    L.append(f"{h} & {short[a]} vs.\\ {short[b]} & " + " & ".join(cells) + " \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
write("tests", L)

# ---- ablation table (full models restricted to the seeds of the variant)
mm = d[d.group == "main"]
def grp(g, nm): return d[(d.group == g) & (d.name == nm)]
abl = [("SymFn-sum KRR (full)", grp("main", "SymFn-sum KRR"), None),
       ("\\ \\ radial-only", grp("abl_sf", "SymFn-sum KRR radial-only"), "SymFn-sum KRR"),
       ("\\ \\ linear ridge (no kernel)", grp("abl_linear", "SymFn-sum linear ridge"), "SymFn-sum KRR"),
       ("\\ \\ linear ridge, radial-only", grp("abl_linear", "SymFn-sum linear ridge radial-only"), "SymFn-sum KRR"),
       ("Sorted dist KRR (full)", grp("main", "Sorted dist KRR"), None),
       ("\\ \\ linear ridge (no kernel)", grp("abl_linear", "Sorted dist linear ridge"), "Sorted dist KRR"),
       ("SymFn-sum MLP (full)", mm[(mm.name == "SymFn-sum MLP") & (mm.seed <= 2)], None),
       ("\\ \\ radial-only", grp("abl_sf", "SymFn-sum MLP radial-only"), "SymFn-sum MLP"),
       ("Raw coords MLP", mm[(mm.name == "Raw coords MLP") & (mm.seed <= 2)], None),
       ("\\ \\ + rot/perm aug.", grp("abl_aug", "Raw coords MLP + rot/perm aug"), "Raw coords MLP")]
L = ["\\begin{tabular}{lcccc}", "\\toprule", "Variant & seeds & MAE & inv.\\ defect & $p$ vs.\\ full \\\\", "\\midrule"]
for nm, x, ref in abl:
    p = ""
    if ref is not None:
        full = mm[(mm.name == ref) & mm.seed.isin(x.seed)]
        pv = welch(x.energy_mae, full.energy_mae); p = pfmt(pv)
        out.append(f"ablation {nm.strip(chr(92) + ' ')} of {ref}: {x.energy_mae.mean():.3f} vs full {full.energy_mae.mean():.3f} ({len(x)} seeds), Welch p={pv:.3g}")
    L.append(f"{nm} & {len(x)} & {f3(x.energy_mae)} & {sci(np.mean(x.inv_defect))} & {p} \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
write("abl", L)

# ---- steps sensitivity (seeds 0-2)
L = ["\\begin{tabular}{lccc}", "\\toprule", "System & 1000 steps & 3000 steps & 12000 steps \\\\", "\\midrule"]
for nm in ["Sorted dist MLP", "SymFn-sum MLP"]:
    cells, v = [], {}
    for st in (1000, 3000, 12000):
        x = d[(d.name == nm) & (d.n == 500) & (d.seed <= 2) & (d.steps == st) & d.group.isin(["main", "sweep_steps"])]
        v[st] = x.energy_mae; cells.append(ms(x.energy_mae))
    L.append(nm + " & " + " & ".join(cells) + " \\\\")
    L.append("\\ \\ $p$ vs.\\ 3000 steps & " + pfmt(welch(v[1000], v[3000])) + " & & " + pfmt(welch(v[12000], v[3000])) + " \\\\")
    out.append(f"steps {nm}: 1000 vs 3000 p={welch(v[1000], v[3000]):.3g}; 12000 vs 3000 p={welch(v[12000], v[3000]):.3g}")
L += ["\\bottomrule", "\\end{tabular}"]
write("steps", L)

# ---- KRR grid sensitivity (n=500, 5 seeds); "wide" = the main-group runs
L = ["\\begin{tabular}{lccc}", "\\toprule", "System & narrow & mid & wide (main) \\\\", "\\midrule"]
for nm in ["SymFn-sum KRR", "Sorted dist KRR"]:
    v = {g: grp("sweep_krrgrid", f"{nm} ({g} grid)") for g in ("narrow", "mid")}; v["wide"] = grp("main", nm)
    L.append(short[nm] + " & " + " & ".join(f3(v[g].energy_mae) for g in ("narrow", "mid", "wide")) + " \\\\")
    L.append("\\ \\ inv.\\ defect & " + " & ".join(sci(v[g].inv_defect.mean()) for g in ("narrow", "mid", "wide")) + " \\\\")
    L.append("\\ \\ $\\gamma$ at edge / $\\lambda$ at floor & " + " & ".join(f"{int(v[g].hp_gamma_at_edge.sum())}/{len(v[g])}, {int(v[g].hp_lambda_at_edge.sum())}/{len(v[g])}" for g in ("narrow", "mid", "wide")) + " \\\\")
    for g in ("narrow", "mid"):
        out.append(f"grid {nm}: {g} {v[g].energy_mae.mean():.3f} vs wide {v['wide'].energy_mae.mean():.3f}, Welch p={welch(v[g].energy_mae, v['wide'].energy_mae):.3g}")
    w = v["wide"]
out.append("grid narrow SymFn-sum KRR vs narrow Sorted dist KRR: Welch p=%.3g" % welch(grp("sweep_krrgrid", "SymFn-sum KRR (narrow grid)").energy_mae, grp("sweep_krrgrid", "Sorted dist KRR (narrow grid)").energy_mae))
L += ["\\bottomrule", "\\end{tabular}"]
write("grid", L)

# ---- selected KRR hyperparameters, all runs with the wide grid
def lg(v): return f"{np.log10(v):.1f}".replace("-0.0", "0.0").replace(".0", "")
def rng_(x): return f"$10^{{{lg(x.min())}}}$" if x.min() == x.max() else f"$10^{{{lg(x.min())}}}$--$10^{{{lg(x.max())}}}$"
L = ["\\begin{tabular}{llcccc}", "\\toprule", "System & $n$ & $\\gamma$ & $\\lambda$ & $\\gamma$ edge & $\\lambda$ floor \\\\", "\\midrule"]
rawk = lc[lc.name == "Raw coords KRR"]
hp = [("Raw coords KRR", rawk, "all")]
hp += [(nm, lc[(lc.name == nm) & (lc.n == s)], s) for nm in ("Sorted dist KRR", "SymFn-sum KRR") for s in sizes]
hp += [("SymFn-sum KRR radial-only", grp("abl_sf", "SymFn-sum KRR radial-only"), 500)]
hp += [(nm, grp("abl_linear", nm), 500) for nm in ("SymFn-sum linear ridge", "SymFn-sum linear ridge radial-only", "Sorted dist linear ridge")]
for nm, x, s in hp:
    lin = "linear" in nm
    L.append(f"{short[nm]} & {s} & " + ("--" if lin else rng_(x.hp_gamma)) + f" & {rng_(x.hp_lambda)} & "
             + ("--" if lin else f"{int(x.hp_gamma_at_edge.sum())}/{len(x)}") + f" & {int(x.hp_lambda_at_edge.sum())}/{len(x)} \\\\")
    out.append(f"hp {nm} n={s}: gamma {sorted(set(x.hp_gamma)) if not lin else '-'} lambda {sorted(set(x.hp_lambda))} gamma_at_edge {0 if lin else int(x.hp_gamma_at_edge.sum())}/{len(x)} lambda_at_floor {int(x.hp_lambda_at_edge.sum())}/{len(x)}")
L += ["\\bottomrule", "\\end{tabular}"]
write("hp", L)

# ---- figures
cols = plt.cm.tab10(np.arange(7))
fig, ax = plt.subplots(figsize=(3.4, 2.9))
g = lc[lc.name == "Mean predictor"].groupby("n").energy_mae.mean()
ax.plot(g.index, g.values, color="0.45", ls=":", lw=1, label="Mean predictor")
for c, nm in zip(cols, order):
    g = lc[lc.name == nm].groupby("n").energy_mae
    m, s = g.mean(), g.std()
    ax.errorbar(m.index, m.values, yerr=s.values, marker="o" if "KRR" in nm else "s", ls="-" if "KRR" in nm else "--",
                color=c, label=nm, ms=3, lw=1, capsize=1.5)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("training configurations $n$"); ax.set_ylabel("test energy MAE ($\\epsilon$)")
ax.grid(alpha=.3)
fig.legend(fontsize=6, ncol=2, loc="lower center", frameon=False)  # below the axes, so that no curve is covered
fig.tight_layout(rect=(0, 0.22, 1, 1)); fig.savefig("results/figures/lcurve.pdf")
names = ["Mean predictor"] + order
fig, ax = plt.subplots(figsize=(3.4, 2.3)); w = .38; x = np.arange(len(names))
for k, (met, lab) in enumerate([("energy_mae", "clean test"), ("mae_rot_perm", "rotated + permuted test")]):
    g = [mm[mm.name == n][met] for n in names]
    ax.bar(x + (k - .5) * w, [v.mean() for v in g], w, yerr=[v.std(ddof=1) for v in g], label=lab, capsize=1)
ax.set_yscale("log"); ax.set_xticks(x); ax.set_xticklabels(["Mean", "Raw KRR", "Raw MLP", "Sort KRR", "Sort MLP", "SF KRR", "SF MLP", "SF atom"], rotation=45, ha="right", fontsize=6)
ax.set_ylabel("test energy MAE ($\\epsilon$)"); ax.legend(fontsize=6); fig.tight_layout(); fig.savefig("results/figures/invariance.pdf")

# ---- main table with short column names (same numbers as `rh table --group main`)
L = ["\\begin{tabular}{lccccccc}", "\\toprule", "System & MAE & MAE/atom & perturbed & random & rot+perm & inv.\\ defect & max over seeds \\\\", "\\midrule"]
for nm in names:
    x = mm[mm.name == nm]
    L.append(f"{nm} & {f3(x.energy_mae)} & {f3(x.energy_mae_per_atom)} & {f3(x.mae_perturbed)} & {f3(x.mae_random)} & {f3(x.mae_rot_perm)} & {sci(np.mean(x.inv_defect))} & {sci(np.max(x.inv_defect))} \\\\")
    out.append(f"main {nm}: MAE {x.energy_mae.mean():.3f}; rot+perm/clean ratio {np.mean(x.mae_rot_perm / x.energy_mae):.3f}; inv_defect mean {x.inv_defect.mean():.3g}, per-seed max {x.inv_defect.max():.3g}"
               + (f", per-sample max {x.inv_defect_max.max():.3g}" if "inv_defect_max" in x and x.inv_defect_max.notna().all() else ""))
L += ["\\bottomrule", "\\end{tabular}"]
write("maintab", L)

# ---- registry facts quoted in the setup section
inv = d[~d.name.str.startswith("Raw") & (d.name != "Mean predictor")]
out.append(f"invariant systems, all groups: largest per-seed inv_defect {inv.inv_defect.max():.3g} ({inv.loc[inv.inv_defect.idxmax(), 'name']}, n={inv.loc[inv.inv_defect.idxmax(), 'n']}); largest per-sample defect (runs that log it) {inv.inv_defect_max.max():.3g}")
kind = lambda nm: "mean" if nm == "Mean predictor" else "atomwise" if "atomwise" in nm else "MLP" if "MLP" in nm else "KRR/ridge"
for k, x in d.groupby(d.name.map(kind)):
    out.append(f"runtime {k}: in-run {x.runtime_s.min():.1f}-{x.runtime_s.max():.1f} s, median {x.runtime_s.median():.1f} s, wall (rh) max {x.wall.max():.1f} s, {len(x)} runs")
out.append(f"total wall-clock of all ok non-superseded runs: {d.wall.sum() / 60:.1f} min over {len(d)} runs")
out.append(f"test energy std: {d.test_energy_std.min():.2f}-{d.test_energy_std.max():.2f}")
if len(tail):
    t = tail.iloc[0]
    out.append(f"untruncated energies ({int(t.n_samples)} samples): perturbed max {t.perturbed_max_energy:.4g}, q99 {t.perturbed_q99_energy:.4g}, frac>50 {t.perturbed_frac_above_cap:.3f}; random max {t.random_max_energy:.4g}, q99 {t.random_q99_energy:.4g}, frac>50 {t.random_frac_above_cap:.3f}")
    write("tail", ["\\begin{tabular}{lccc}", "\\toprule", "Kind & max $E$ & 99\\% quantile & fraction $E>50$ \\\\", "\\midrule",
                   f"perturbed minima & {t.perturbed_max_energy:.0f} & {t.perturbed_q99_energy:.1f} & {t.perturbed_frac_above_cap:.3f} \\\\",
                   f"random & {t.random_max_energy:.1f} & {t.random_q99_energy:.1f} & {t.random_frac_above_cap:.3f} \\\\", "\\bottomrule", "\\end{tabular}"])
open("results/analysis_stats.txt", "w").write("\n".join(out) + "\n"); print("\n".join(out))
