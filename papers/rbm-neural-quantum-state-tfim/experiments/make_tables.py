"""Builds the paper's tables and figures from results/runs.jsonl (superseded rows dropped).

Two starts per (system, task, seed): group `main` = symmetric start (S), group `main_b` = symmetry-broken start (B).
The reported ("selected") state of a (system, task, seed) is the start with the lower variational energy, i.e. the
lower rel_energy_error (E0 is a constant per task); a diverged start (NaN metrics) loses to a finite one, and the
seed counts as diverged only if both starts diverged. Cells are medians over the seeds with a finite selected state;
a superscript is the number of seeds without one."""
import json, collections, glob, csv
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

rows, segs = [], collections.defaultdict(lambda: [[]])   # segs: per (group, name), runs between supersede events
every = []
for l in open("results/runs.jsonl"):
    r = json.loads(l)
    if r.get("kind") == "control" and r.get("op") == "supersede":
        rows = [x for x in rows if not (x["group"] == r["group"] and x["name"] == r["name"])]
        segs[(r["group"], r["name"])].append([])
    elif r.get("provenance", {}).get("copied_from"):
        continue   # group `selected`: the selected runs listed again by experiments/list_selected.py, not runs of their own
    elif r.get("status") == "ok" and "metrics" in r:
        rows.append(r); segs[(r["group"], r["name"])][-1].append(r); every.append(r)
current = {r["run_id"] for r in rows}
main = {"S": [r for r in rows if r["group"] == "main"], "B": [r for r in rows if r["group"] == "main_b"]}
ORDER = ["Mean-field SGD", "Mean-field SR", "Jastrow SGD", "Jastrow SR", "RBM alpha=1 SGD", "RBM alpha=1 SR",
         "RBM alpha=2 SGD", "RBM alpha=2 SR", "RBM alpha=4 SGD", "RBM alpha=4 SR"]
SHORT = {n: n.replace("Mean-field", "MF").replace("Jastrow", "Jas").replace("RBM alpha=", "RBM$\\alpha{=}$") for n in ORDER}
G10 = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
SEEDS = [0, 1, 2, 3, 4]
def T(n, g): return f"tfim_N{n}_g{g:.2f}"
TASKS = [T(10, g) for g in G10] + [T(n, g) for n in (8, 12) for g in (0.5, 1.0, 1.5)]
def lab(t): return f"{t.split('_')[1][1:]}/{float(t.split('_g')[1]):g}"
IDX = {st: {(r["name"], r["task"], r["seed"]): r["metrics"] for r in main[st]} for st in "SB"}
for st in "SB":
    assert len(IDX[st]) == len(main[st]) == 650, (st, len(main[st]))
def fin(m): return np.isfinite(m["rel_energy_error"])
def selected(name, task, seed):
    """(metrics, start) of the lower-energy start; (None, None) if both starts diverged."""
    c = [(IDX[st][(name, task, seed)], st) for st in "SB"]
    c = [x for x in c if fin(x[0])]
    return min(c, key=lambda x: x[0]["rel_energy_error"]) if c else (None, None)
def sel_vals(name, task, metric):
    v = [selected(name, task, s)[0] for s in SEEDS]
    return np.array([m[metric] for m in v if m is not None], float), sum(1 for m in v if m is None)
def start_vals(name, task, metric, st):
    v = [IDX[st][(name, task, s)] for s in SEEDS]
    return np.array([m[metric] for m in v if fin(m)], float), sum(1 for m in v if not fin(m))
def fmt(x): return ("%.1e" % x).replace("e-0", "e-").replace("e+0", "e+")
def cell(v, d): return (fmt(np.median(v)) if len(v) else "--") + (f"$^{{{d}}}$" if d else "")
def med(name, task, metric="rel_energy_error"): return np.median(sel_vals(name, task, metric)[0])

# sampling-free reference (group exact_opt): lower-energy start of the L-BFGS optimisation
EX = collections.defaultdict(list)
for r in rows:
    if r["group"] == "exact_opt":
        EX[(r["name"], r["task"])].append(r["metrics"])
REF = ["Mean-field", "Jastrow", "RBM alpha=2"]
with open("results/tables/t_energy.tex", "w") as f:
    def npar(n):   # parameter count at N=10 (identical over starts, seeds and N=10 tasks)
        c = {int(IDX[st][(n, T(10, g), sd)]["n_params"]) for st in "SB" for sd in SEEDS for g in G10}
        assert len(c) == 1
        return c.pop()
    f.write("\\begin{tabular}{lr" + "r" * len(TASKS) + "}\\toprule\n")
    f.write("System & $P_{10}$ & " + " & ".join(lab(t) for t in TASKS) + " \\\\\\midrule\n")
    for n in ORDER:
        f.write(SHORT[n] + f" & {npar(n)} & " + " & ".join(cell(*sel_vals(n, t, "rel_energy_error")) for t in TASKS) + " \\\\\n")
    f.write("\\midrule\n")
    for n in REF:
        for t in TASKS:
            assert len(EX[(f"{n} exact-gradient", t)]) == 2
        best = [min(EX[(f"{n} exact-gradient", t)], key=lambda m: m["rel_energy_error"]) for t in TASKS]
        f.write(SHORT[n + " SR"][:-3] + f" L-BFGS & {npar(n + ' SR')} & " + " & ".join(fmt(m["rel_energy_error"]) for m in best) + " \\\\\n")
    f.write("\\bottomrule\\end{tabular}\n")
MZ = ["Mean-field SR", "Jastrow SR", "RBM alpha=2 SGD", "RBM alpha=2 SR"]
with open("results/tables/t_n10_mz.tex", "w") as f:
    f.write("\\begin{tabular}{rrrrr}\\toprule\n$\\Gamma$ & MF-SR & Jas-SR & R2-SGD & R2-SR \\\\\\midrule\n")
    for g in G10:
        f.write(f"{g:g} & " + " & ".join(cell(*sel_vals(n, T(10, g), "mz_error")) for n in MZ) + " \\\\\n")
    f.write("\\bottomrule\\end{tabular}\n")

# per-start medians (the start ablation): one row per (system, start)
with open("results/tables/t_start.tex", "w") as f:
    f.write("\\begin{tabular}{ll" + "r" * len(TASKS) + "}\\toprule\n")
    f.write("System & start & " + " & ".join(lab(t) for t in TASKS) + " \\\\\\midrule\n")
    for n in [x for x in ORDER if x.endswith("SR")]:
        for st in "SB":
            f.write((SHORT[n] if st == "S" else "") + f" & {st} & " +
                    " & ".join(cell(*start_vals(n, t, "rel_energy_error", st)) for t in TASKS) + " \\\\\n")
    f.write("\\bottomrule\\end{tabular}\n")

# registered tests for H1/H2 on the selected states: per-seed paired wins of RBM alpha=2 SR against each reference
# (a seed where RBM alpha=2 SR has no finite state is a loss), ratio of per-task means over finite seeds, and a
# two-sided paired t-test on the seeds where both systems are finite (as `rh compare` does per start)
from scipy.stats import ttest_rel
refs = ["Mean-field SR", "Jastrow SR", "RBM alpha=2 SGD", "RBM alpha=4 SR"]
M = "RBM alpha=2 SR"
def ratio(x):
    return ("%.0f" % x) if x >= 10 else ("%.2f" % x)
def pfmt(p):
    return "--" if not np.isfinite(p) else ("$<$0.001" if p < 0.001 else "%.3f" % p)
with open("results/tables/t_wins.tex", "w") as f:
    f.write("\\begin{tabular}{lrrrr|rrr|rrr|r}\\toprule\n & \\multicolumn{4}{c|}{seeds won by R2-SR against} & \\multicolumn{3}{c|}{mean $\\epsilon_E$ ratio to R2-SR} & \\multicolumn{3}{c|}{paired $t$-test $p$} & \\\\\n"
            "$N/\\Gamma$ & MF-SR & Jas-SR & R2-SGD & R4-SR & MF-SR & Jas-SR & R2-SGD & MF-SR & Jas-SR & R2-SGD & $n$ \\\\\\midrule\n")
    tot = collections.Counter()
    for t in TASKS:
        cells, rat, ps = [], [], []
        A = {s: selected(M, t, s)[0] for s in SEEDS}
        for rf in refs:
            B = {s: selected(rf, t, s)[0] for s in SEEDS}
            w = sum(int(A[s] is not None and (B[s] is None or A[s]["rel_energy_error"] < B[s]["rel_energy_error"])) for s in SEEDS)
            tot[rf] += w; cells.append(f"{w}/5")
            if rf != "RBM alpha=4 SR":
                rat.append(ratio(sel_vals(rf, t, "rel_energy_error")[0].mean() / sel_vals(M, t, "rel_energy_error")[0].mean()))
                both = [s for s in SEEDS if A[s] is not None and B[s] is not None]
                ps.append(pfmt(ttest_rel([A[s]["rel_energy_error"] for s in both], [B[s]["rel_energy_error"] for s in both]).pvalue if len(both) >= 3 else np.nan))
        f.write(f"{lab(t)} & " + " & ".join(cells + rat + ps) + f" & {sum(1 for s in SEEDS if A[s] is not None)} \\\\\n")
    f.write("\\midrule Total /65 & " + " & ".join(str(tot[r]) for r in refs) + " & & & & & & & \\\\\n\\bottomrule\\end{tabular}\n")

# hidden-density detail at Gamma=1 (H3, H5): selected states, SR
with open("results/tables/t_alpha.tex", "w") as f:
    f.write("\\begin{tabular}{rrrrrr}\\toprule\n$N$ & $\\alpha$ & mean & median & min & max \\\\\\midrule\n")
    for N in (8, 10, 12):
        for al in (1, 2, 4):
            v, d = sel_vals(f"RBM alpha={al} SR", T(N, 1.0), "rel_energy_error")
            assert len(v) == 5
            f.write(f"{N} & {al} & {fmt(v.mean())} & {fmt(np.median(v))} & {fmt(v.min())} & {fmt(v.max())} \\\\\n")
    f.write("\\bottomrule\\end{tabular}\n")

# which start is selected, and the infidelity of the selected state (N=10 sweep, SR systems and Jastrow SGD)
with open("results/tables/t_select.tex", "w") as f:
    GS = [0.25, 0.5, 0.75, 1.0]
    f.write("\\begin{tabular}{l" + "r" * len(GS) + "}\\toprule\nSystem & " + " & ".join(f"{g:g}" for g in GS) + " \\\\\\midrule\n")
    for n in ["Mean-field SR", "Jastrow SR", "RBM alpha=1 SR", "RBM alpha=2 SR", "RBM alpha=4 SR", "RBM alpha=2 SGD"]:
        cells = []
        for g in GS:
            nb = sum(1 for s in SEEDS if selected(n, T(10, g), s)[1] == "B")
            v, d = sel_vals(n, T(10, g), "infidelity")
            cells.append(f"{fmt(np.median(v))} ({nb})")
        f.write(SHORT[n] + " & " + " & ".join(cells) + " \\\\\n")
    f.write("\\bottomrule\\end{tabular}\n")

# figures from registry values
fig, axs = plt.subplots(2, 1, figsize=(3.45, 2.9), sharex=True)
for ax, metric, yl, pl in zip(axs, ["rel_energy_error", "mz_error"], ["rel. energy error", "$|M_z|$ error"], "ab"):
    for i, n in enumerate(ORDER):
        y = [np.median(sel_vals(n, T(10, g), metric)[0]) for g in G10]
        ax.plot(G10, y, marker="o", ms=2.5, lw=1, color=f"C{i // 2}", ls="-" if "SR" in n else "--", label=n.replace("alpha=", "$\\alpha$=").replace("Mean-field", "MF"))
    ax.set_yscale("log"); ax.axvline(1.0, color="gray", lw=0.5); ax.set_ylabel(yl, fontsize=7); ax.tick_params(labelsize=7)
    ax.set_title(f"({pl})", fontsize=8, loc="left", pad=2)
axs[1].set_xlabel("$\\Gamma$ ($N$=10)", fontsize=7)
h, l = axs[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=3, fontsize=6, frameon=False)
fig.tight_layout(rect=(0, 0.17, 1, 1)); fig.savefig("results/figures/gamma_sweep.pdf"); plt.close(fig)

# sweeps (RBM alpha=2 SR, N=10, Gamma=1, 5 seeds, symmetric start): median over non-diverged seeds, divergence count
with open("results/tables/t_sweeps.tex", "w") as f:
    f.write("\\begin{tabular}{lrrrr}\\toprule\nsetting & $\\epsilon_E$ & $\\epsilon_{M_z}$ & $1{-}F$ & div. \\\\\\midrule\n")
    for group, param, label, xs in [("sweep_shift", "shift", "$\\epsilon$", [1e-4, 1e-3, 1e-2, 1e-1, 1.0]),
                                    ("sweep_samples", "samples", "$M$", [32, 64, 128, 256, 512])]:
        rs = [r for r in rows if r["group"] == group]
        for x in xs:
            sel = [r["metrics"] for r in rs if r["config"][param] == x]
            assert len(sel) == 5
            ok = [m for m in sel if fin(m)]
            c = [fmt(np.median([m[k] for m in ok])) if ok else "--" for k in ("rel_energy_error", "mz_error", "infidelity")]
            f.write(f"{label}$\\,{{=}}\\,${x:g} & " + " & ".join(c) + f" & {len(sel) - len(ok)}/5 \\\\\n")
        if group == "sweep_shift": f.write("\\midrule\n")
    f.write("\\bottomrule\\end{tabular}\n")
# training curves (registry `curves` group, symmetric start, seed-median per system), N=10 Gamma=1
fig, ax = plt.subplots(figsize=(2.7, 1.9))
for key in ["mf1-sr", "jastrow1-sr", "rbm1-sr", "rbm2-sr", "rbm4-sr", "rbm2-sgd"]:
    cur = []
    for fn in sorted(glob.glob(f"results/raw/curve_{key.split('-')[0]}_{key.split('-')[1]}_s*.csv")):
        cur.append([float(r["value"]) for r in csv.DictReader(open(fn))])
    cur = np.array(cur)
    lbl = key.replace("rbm", "RBM$\\alpha$=").replace("mf1", "MF").replace("jastrow1", "Jastrow").replace("-sr", " SR").replace("-sgd", " SGD")
    ax.plot(np.nanmedian(np.abs(cur), axis=0), label=lbl, lw=0.8, ls="--" if "sgd" in key else "-")
ax.set_yscale("log"); ax.set_xlabel("iteration", fontsize=6.5); ax.set_ylabel("MC $|\\epsilon_E|$", fontsize=6.5); ax.tick_params(labelsize=6)
fig.legend(loc="lower center", ncol=3, fontsize=5.5, frameon=False)
fig.tight_layout(rect=(0, 0.14, 1, 1)); fig.savefig("results/figures/curves.pdf"); plt.close(fig)

# checks and cost: variational bound, MC-vs-exact energy, run counts and run time from the registry
def minutes(rs): return sum(r["provenance"]["duration_s"] for r in rs) / 60
def wall(rs):
    """Minutes during which at least one run was executing (union of the run intervals)."""
    from datetime import datetime
    iv = sorted((datetime.fromisoformat(r["provenance"]["started"]).timestamp(), r["provenance"]["duration_s"]) for r in rs)
    tot, end = 0.0, -1.0
    for s, d in iv:
        s0 = max(s, end)
        if s + d > s0: tot += s + d - s0; end = s + d
    return tot / 60
def ndiv(rs): return sum(1 for r in rs if not fin(r["metrics"]))
with open("results/tables/t_check.tex", "w") as f:
    allm = main["S"] + main["B"]
    finm = [r for r in allm if fin(r["metrics"])]
    f.write("\\begin{tabular}{lr}\\toprule\nQuantity & value \\\\\\midrule\n")
    # v1 and v2 are the superseded first and second segments of the registry (single start S)
    old = []
    for i in (0, 1):
        chunk = [r for n in ORDER for r in segs[("main", n)][i]]
        assert len(chunk) == 650
        old.append(ndiv(chunk))
    f.write(f"diverged of 650 main runs, v1 / v2 (start S) & {old[0]} / {old[1]} \\\\\n")
    both = sum(1 for n in ORDER for t in TASKS for s in SEEDS if selected(n, t, s)[0] is None)
    f.write(f"diverged of 650, final: start S / B / both & {ndiv(main['S'])} / {ndiv(main['B'])} / {both} \\\\\n")
    f.write(f"of these, RBM$\\alpha{{=}}$2 / 4 SR, start S (of 65) & "
            f"{ndiv([r for r in main['S'] if r['name'] == 'RBM alpha=2 SR'])} / {ndiv([r for r in main['S'] if r['name'] == 'RBM alpha=4 SR'])} \\\\\n")
    big = lambda rs: sum(1 for r in rs if fin(r["metrics"]) and r["metrics"]["rel_energy_error"] > 0.1)
    nsel = sum(1 for n in ORDER for t in TASKS for s in SEEDS if selected(n, t, s)[0] is not None and selected(n, t, s)[0]["rel_energy_error"] > 0.1)
    f.write(f"$\\epsilon_E>0.1$: start S / B / selected & {big(main['S'])} / {big(main['B'])} / {nsel} \\\\\n")
    f.write(f"min $\\epsilon_E$ over the finite main runs & {fmt(min(r['metrics']['rel_energy_error'] for r in finm))} \\\\\n")
    d = [abs(r["metrics"]["mc_energy_error"] - r["metrics"]["rel_energy_error"]) for r in finm if r["name"] == M]
    f.write(f"median $|\\epsilon_E^{{MC}}-\\epsilon_E|$, RBM$\\alpha{{=}}$2 SR & {fmt(np.median(d))} \\\\\n")
    tune = [r for r in rows if r["group"] == "tune_lr3"]
    per = collections.Counter(r["name"] for r in tune)
    sg = {per[n] for n in ORDER if n.endswith("SGD")}; sr = {per[n] for n in ORDER if n.endswith("SR")}
    assert len(sg) == 1 and len(sr) == 1
    f.write(f"tuning runs per SGD / SR system & {sg.pop()} / {sr.pop()} \\\\\n")
    exr = [m for v in EX.values() for m in v]
    f.write(f"L-BFGS runs / stopped at iteration cap & {len(exr)} / {sum(1 for m in exr if m['lbfgs_iters'] >= 1000)} \\\\\n")
    rep_ = [r for r in rows if r["group"] not in ("sanity", "tune_lr", "tune_lr2")]
    # run counts are the registry's own counts (\rhval), one per reported group
    cnt = lambda *gs: " / ".join("\\rhval{count/%s/runs}" % g for g in gs)
    assert [sum(1 for r in rep_ if r["group"] == g) for g in ("main", "main_b", "exact_opt", "tune_lr3", "sweep_shift", "sweep_samples", "curves")] == [650, 650, 78, 315, 25, 25, 30]
    f.write(f"runs: start S / B / L-BFGS & {cnt('main', 'main_b', 'exact_opt')} \\\\\n")
    f.write(f"runs: tuning / shift / samples / curves & {cnt('tune_lr3', 'sweep_shift', 'sweep_samples', 'curves')} \\\\\n")
    f.write(f"summed run time (min): reported / all & {minutes(rep_):.0f} / {minutes(every):.0f} \\\\\n")
    f.write(f"wall-clock with a run executing (min) & {wall(every):.0f} \\\\\n")
    f.write(f"longest single run (s) & {max(r['provenance']['duration_s'] for r in every):.0f} \\\\\n")
    f.write("\\bottomrule\\end{tabular}\n")
for t in ["t_energy", "t_start", "t_wins", "t_alpha", "t_select", "t_n10_mz", "t_sweeps", "t_check"]:
    print("==", t); print(open(f"results/tables/{t}.tex").read())
