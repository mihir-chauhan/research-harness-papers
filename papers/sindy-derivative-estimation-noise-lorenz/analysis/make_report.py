"""Tables and figures built only from results/runs.jsonl (ok runs)."""
import json, numpy as np, collections
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

# registry rows; a control row (`rh supersede`) retires all earlier rows of its (group, name)
R, OLD = [], []
for r in (json.loads(l) for l in open("results/runs.jsonl")):
    if r.get("kind") == "control":
        OLD += [x for x in R if x["group"] == r["group"] and x["name"] == r["name"]]
        R = [x for x in R if not (x["group"] == r["group"] and x["name"] == r["name"])]
    elif r["status"] == "ok":
        R.append(r)
TUNED = json.load(open("method/tuned.json"))
TUNED_V1 = json.load(open("method/tuned_v1.json"))   # first tuner version (exact ties -> smallest threshold)
KEY = {"FD-STLSQ": "fd", "SG-STLSQ": "sg", "Spline-STLSQ": "spline", "TV-STLSQ": "tv", "Weak-form STLSQ": "weak"}
LV = ["0", "0.5", "1", "2", "5", "10"]
SYS = ["FD-STLSQ", "SG-STLSQ", "Spline-STLSQ", "TV-STLSQ", "Weak-form STLSQ"]
SHORT = {"FD-STLSQ": "FD", "SG-STLSQ": "SG", "Spline-STLSQ": "Spline", "TV-STLSQ": "TV", "Weak-form STLSQ": "Weak"}


def vals(group, name, lv, metric, cfg=None, rows=None):
    sel = [r for r in (R if rows is None else rows) if r["group"] == group and r["name"] == name
           and r["task"] == f"lorenz_n{lv}" and (cfg is None or r["config"] == cfg)]
    sel.sort(key=lambda r: r["seed"])
    return np.array([r["metrics"][metric] for r in sel])


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def fmt_err(x):
    return f"{x:.4f}" if x >= 1e-3 else f"{x:.1e}".replace("e-0", "e-")


def table(path, header, rows, colspec):
    with open(path, "w") as f:
        f.write("\\begin{tabular}{" + colspec + "}\\toprule\n" + " & ".join(header) + " \\\\\\midrule\n")
        for row in rows:
            f.write(" & ".join(row) + " \\\\\n")
        f.write("\\bottomrule\\end{tabular}\n")


T = "results/tables/"
# 1. support rate and coef_err by system x noise
rows, rows2, rows3, rows4, rows5 = [], [], [], [], []
for s in SYS:
    r1, r2, r3, r4, r5 = [SHORT[s]], [SHORT[s]], [SHORT[s]], [SHORT[s]], [SHORT[s]]
    for lv in LV:
        v = vals("main", s, lv, "support_exact"); assert len(v) == 20
        r1.append(f"{v.mean():.2f}")
        r2.append(fmt_err(vals("main", s, lv, "coef_err").mean()))
        r3.append(fmt_err(vals("main", s, lv, "coef_err_oracle").mean()))
        r5.append(fmt_err(np.median(vals("main", s, lv, "coef_err"))))
        r4.append(f"{vals('main', s, lv, 'false_pos').mean():.2f}/{vals('main', s, lv, 'false_neg').mean():.2f}")
    rows.append(r1); rows2.append(r2); rows3.append(r3); rows4.append(r4); rows5.append(r5)
hdr = ["System"] + [f"{l}\\%" for l in LV]
table(T + "rep_support.tex", hdr, rows, "lrrrrrr")
table(T + "rep_coef.tex", hdr, rows2, "lrrrrrr")
table(T + "rep_coef_med.tex", hdr, rows5, "lrrrrrr")
table(T + "rep_oracle.tex", hdr, rows3, "lrrrrrr")
table(T + "rep_fpfn.tex", ["Noise"] + [r[0] for r in rows4], [[f"{lv}\\%"] + [r[i + 1] for r in rows4] for i, lv in enumerate(LV)], "lrrrrr")  # levels as rows

# 2. width sweep (main row for the tuned width 0.6 at both levels)
rows = []
assert TUNED["weak"]["2"]["width"] == TUNED["weak"]["5"]["width"] == 0.6
for w in [0.3, 0.6, 1.0, 1.5, 2.5, 4.0]:
    row = [f"{w}" + ("$^\\dagger$" if w == 0.6 else "")]
    for lv in ["2", "5"]:
        v = vals("main", "Weak-form STLSQ", lv, "support_exact") if w == 0.6 else vals("sweep_width", "Weak-form STLSQ", lv, "support_exact", {"width": w})
        e = vals("main", "Weak-form STLSQ", lv, "coef_err") if w == 0.6 else vals("sweep_width", "Weak-form STLSQ", lv, "coef_err", {"width": w})
        fp = vals("main", "Weak-form STLSQ", lv, "false_pos") if w == 0.6 else vals("sweep_width", "Weak-form STLSQ", lv, "false_pos", {"width": w})
        fn = vals("main", "Weak-form STLSQ", lv, "false_neg") if w == 0.6 else vals("sweep_width", "Weak-form STLSQ", lv, "false_neg", {"width": w})
        assert len(v) == 20, (w, lv, len(v))
        row += [f"{v.mean():.2f}", fmt_err(e.mean()), f"{fp.mean():.2f}/{fn.mean():.2f}"]
    rows.append(row)
table(T + "rep_width.tex", ["Width", "supp.", "coef.err", "FP/FN", "supp.", "coef.err", "FP/FN"], rows, "lrrrrrr")

# 3. exponent p (p=3 is the main row)
rows = []
for p in [2, 3, 4, 6]:
    g, c = ("main", None) if p == 3 else ("abl_p", {"p": p})
    nm = "Weak-form STLSQ"
    v, e = vals(g, nm, "2", "support_exact", c), vals(g, nm, "2", "coef_err", c)
    fp, fn = vals(g, nm, "2", "false_pos", c), vals(g, nm, "2", "false_neg", c)
    assert len(v) == 20
    rows.append([f"{p}" + ("$^\\dagger$" if p == 3 else ""), f"{v.mean():.2f}", fmt_err(e.mean()), f"{fp.mean():.2f}/{fn.mean():.2f}"])
table(T + "rep_p.tex", ["$p$", "supp.", "coef.err", "FP/FN"], rows, "lrrr")

# 4. library state
rows = []
for s, nm2 in [("SG-STLSQ", "SG-STLSQ (smoothed library)"), ("Spline-STLSQ", "Spline-STLSQ (smoothed library)")]:
    for lab, g, nm in [("raw", "main", s), ("smoothed", "abl_libstate", nm2)]:
        row = [SHORT[s], lab]
        for lv in ["2", "5"]:
            v = vals(g, nm, lv, "support_exact"); assert len(v) == 20
            row += [f"{v.mean():.2f}", fmt_err(vals(g, nm, lv, "coef_err").mean())]
        rows.append(row)
table(T + "rep_lib.tex", ["System", "Library state", "supp. 2\\%", "err 2\\%", "supp. 5\\%", "err 5\\%"], rows, "llrrrr")

# figures
colors = dict(zip(SYS, ["#7f7f7f", "#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"]))
mk = dict(zip(SYS, "osv^D"))
x = np.arange(len(LV))
fig, ax = plt.subplots(1, 2, figsize=(5.2, 1.3))   # included at 0.72 textwidth, i.e. at natural size
for i, s in enumerate(SYS):
    ps, lo, hi, me, q1, q3 = [], [], [], [], [], []
    for lv in LV:
        v = vals("main", s, lv, "support_exact"); k = int(v.sum())
        ps.append(k / 20); l, h = wilson(k, 20); lo.append(l); hi.append(h)
        e = vals("main", s, lv, "coef_err"); me.append(np.median(e)); q1.append(np.percentile(e, 25)); q3.append(np.percentile(e, 75))
    xo = x + (i - 2) * 0.06
    ax[0].errorbar(xo, ps, yerr=[np.array(ps) - lo, np.array(hi) - ps], color=colors[s], marker=mk[s], ms=3, lw=0.8, capsize=1.5, label=SHORT[s])
    ax[1].errorbar(xo, me, yerr=[np.array(me) - q1, np.array(q3) - me], color=colors[s], marker=mk[s], ms=3, lw=0.8, capsize=1.5, label=SHORT[s])
ax[0].set_ylabel("exact support rate"); ax[1].set_ylabel("median coef. error")
ax[1].set_yscale("log")
for a in ax:
    a.set_xticks(x); a.set_xticklabels([f"{l}%" for l in LV]); a.set_xlabel("noise level (% of signal std)"); a.grid(alpha=.3)
ax[0].legend(fontsize=6, loc="lower left", labelspacing=0.2, borderpad=0.3); ax[0].set_ylim(-0.05, 1.05)
for a in ax: a.tick_params(labelsize=6.5); a.xaxis.label.set_size(7); a.yaxis.label.set_size(7)
fig.tight_layout(); fig.savefig("results/figures/noise_curves.pdf"); plt.close(fig)

# per-seed oracle error scatter vs noise (boxplot)
fig, ax = plt.subplots(figsize=(3.4, 2.6))
for i, s in enumerate(SYS):
    mo = [np.median(vals("main", s, lv, "coef_err_oracle")) for lv in LV]
    ax.plot(x + (i - 2) * 0.04, mo, color=colors[s], marker=mk[s], ms=4, lw=1, label=SHORT[s])
ax.set_yscale("log"); ax.set_xticks(x); ax.set_xticklabels([f"{l}%" for l in LV]); ax.grid(alpha=.3)
ax.set_xlabel("noise level (% of signal std)", fontsize=8); ax.set_ylabel("median coef. error, true support", fontsize=7.5)
ax.tick_params(labelsize=7); ax.legend(fontsize=6.5)
fig.tight_layout(); fig.savefig("results/figures/oracle_curves.pdf"); plt.close(fig)

# width sweep figure (included at 0.64 columnwidth, i.e. at natural size)
fig, ax = plt.subplots(figsize=(2.25, 1.15))
W = [0.3, 0.6, 1.0, 1.5, 2.5, 4.0]
for lv, c in [("2", "#1f77b4"), ("5", "#d62728")]:
    ys = []
    for w in W:
        v = vals("main", "Weak-form STLSQ", lv, "support_exact") if w == 0.6 else vals("sweep_width", "Weak-form STLSQ", lv, "support_exact", {"width": w})
        ys.append(v.mean())
    ax.plot(W, ys, marker="o", ms=3, lw=1, color=c, label=f"{lv}% noise")
ax.set_xscale("log"); ax.set_xticks(W); ax.set_xticklabels([str(w) for w in W]); ax.minorticks_off()
ax.set_xlabel("test-function width (time units)", fontsize=7); ax.set_ylabel("support rate", fontsize=7); ax.set_ylim(-0.05, 1.08)
ax.grid(alpha=.3); ax.legend(fontsize=6, loc="lower center", bbox_to_anchor=(0.5, 0.98), ncol=2, frameon=False, borderpad=0.1); ax.tick_params(labelsize=6.5)
fig.tight_layout(); fig.savefig("results/figures/width_sweep.pdf"); plt.close(fig)

# significance tables (Welch p from rh compare csv files)
import pandas as pd
def ptab(csv, out, rows_names, higher_better, mark_better):
    d = pd.read_csv(csv)
    rows = []
    for nm in rows_names:
        row = [SHORT[nm]]
        for lv in LV:
            x = d[(d.task == f"lorenz_n{lv}") & (d.name == nm)]
            if len(x) == 0 or np.isnan(x.welch_p.values[0]):
                row.append("--")
            else:
                pv = x.welch_p.values[0]
                # ddagger: the row system has the better mean than the reference (against the hypothesised direction)
                better = (x["mean"].values[0] > x.ref_mean.values[0]) == higher_better and x["mean"].values[0] != x.ref_mean.values[0]
                row.append(("%.3f" % pv) + ("$^*$" if pv < 0.05 else "") + ("$^\\ddagger$" if better == mark_better else ""))
        rows.append(row)
    table(out, hdr, rows, "lrrrrrr")
    return rows
pa = ptab(T + "compare_main_support_exact.csv", T + "rep_p_supp.tex", SYS[:4], True, True)     # mark: baseline better than weak
pb = ptab(T + "compare_main_coef_err.csv", T + "rep_p_err.tex", SYS[:4], False, True)
pc = ptab(T + "h2_fd_ref_coef_err.csv", T + "rep_p_h2.tex", SYS[1:4], False, False)     # mark: smoother worse than FD
with open(T + "rep_p_all.tex", "w") as f:     # the three blocks in one tabular (same cells as the three files above)
    f.write("\\begin{tabular}{lrrrrrr}\\toprule\n" + " & ".join(hdr) + " \\\\\n")
    for lab, blk in [("(a) support rate, weak form vs.", pa), ("(b) coefficient error, weak form vs.", pb),
                     ("(c) coefficient error, FD vs.", pc)]:
        f.write("\\midrule\\multicolumn{7}{l}{%s} \\\\\n" % lab)
        for row in blk:
            f.write(" & ".join(row) + " \\\\\n")
    f.write("\\bottomrule\\end{tabular}\n")

# threshold grid on the test seeds (diagnostic): one sweep_thr run per system x level x seed evaluates all thresholds
THRS = ["0.05", "0.1", "0.2", "0.4", "0.6"]
for nm in SYS:           # consistency: the grid run at the tuned threshold equals the main run, and at the
    for lv in LV:        # first-version threshold it equals the superseded main run of the first tuner version
        for met in ("support_exact", "coef_err", "false_pos", "false_neg"):
            t2, t1 = "%g" % TUNED[KEY[nm]][lv]["thr"], "%g" % TUNED_V1[KEY[nm]][lv]["thr"]
            assert np.array_equal(vals("sweep_thr", nm, lv, f"{met}_t{t2}"), vals("main", nm, lv, met)), (nm, lv, met)
            assert np.array_equal(vals("sweep_thr", nm, lv, f"{met}_t{t1}"), vals("main", nm, lv, met, rows=OLD)), (nm, lv, met)


def mark(cell, key, lv, thr):
    """shaded: tuned threshold (main runs); underline: threshold picked by the first tuner version."""
    if TUNED_V1[key][lv]["thr"] == float(thr):
        cell = "\\underline{%s}" % cell
    if TUNED[key][lv]["thr"] == float(thr):
        cell = "\\colorbox{black!15}{%s}" % cell
    return cell


def thr_table(path, levels, metric, fmt):
    with open(path, "w") as f:
        f.write("\\begin{tabular}{l" + "|rrrrr" * len(levels) + "}\\toprule\n")
        f.write(" & " + " & ".join("\\multicolumn{5}{c}{%s\\%% noise}" % lv for lv in levels) + " \\\\\n")
        f.write("$\\lambda$ & " + " & ".join(THRS * len(levels)) + " \\\\\\midrule\n")
        for nm in SYS:
            row = [SHORT[nm]]
            for lv in levels:
                for thr in THRS:
                    v = vals("sweep_thr", nm, lv, f"{metric}_t{thr}"); assert len(v) == 20
                    row.append(mark(fmt(v.mean()), KEY[nm], lv, thr))
            f.write(" & ".join(row) + " \\\\\n")
        f.write("\\bottomrule\\end{tabular}\n")


f2 = lambda x: "%.2f" % x
thr_table(T + "rep_thr_a.tex", ["0", "0.5", "1"], "support_exact", f2)
thr_table(T + "rep_thr_b.tex", ["2", "5", "10"], "support_exact", f2)
thr_table(T + "rep_thr_err_a.tex", ["1", "2"], "coef_err", fmt_err)
thr_table(T + "rep_thr_err_b.tex", ["5", "10"], "coef_err", fmt_err)
thr_table(T + "rep_thr_err_5.tex", ["5"], "coef_err", fmt_err)
thr_table(T + "rep_thr_fp_b.tex", ["2", "5", "10"], "false_pos", f2)
thr_table(T + "rep_thr_fn_b.tex", ["2", "5", "10"], "false_neg", f2)
# full grid as csv
with open(T + "thr_grid.csv", "w") as f:
    f.write("system,noise_pct,thr,tuned,tuned_v1,support_exact,coef_err,false_pos,false_neg\n")
    for nm in SYS:
        for lv in LV:
            for thr in THRS:
                m = [vals("sweep_thr", nm, lv, f"{k}_t{thr}").mean() for k in ("support_exact", "coef_err", "false_pos", "false_neg")]
                f.write(f"{SHORT[nm]},{lv},{thr},{int(TUNED[KEY[nm]][lv]['thr'] == float(thr))},{int(TUNED_V1[KEY[nm]][lv]['thr'] == float(thr))},"
                        + ",".join("%.6g" % x for x in m) + "\n")

# tuned thresholds (revised; first version in parentheses when different), levels as rows; last row: mean runtime
# per trial over the 120 main runs of the system
rows, rows_rt, rt_row = [], [], ["s/trial"]
for lv in LV:
    row = [f"{lv}\\%"]
    for nm in SYS:
        a, b = TUNED[KEY[nm]][lv]["thr"], TUNED_V1[KEY[nm]][lv]["thr"]
        row.append("%g" % a + ("" if a == b else " (%g)" % b))
    rows.append(row)
for nm in SYS:
    rt = np.concatenate([vals("main", nm, lv, "runtime_s") for lv in LV]); assert len(rt) == 120
    rt_row.append("%.2f" % rt.mean()); rows_rt.append([SHORT[nm], "%.2f" % rt.mean()])
rows[-1][-1] += " \\\\\\midrule\n" + " & ".join(rt_row)
table(T + "rep_tuned_thr.tex", ["Noise"] + [SHORT[nm] for nm in SYS], rows, "lrrrrr")
table(T + "rep_rt.tex", ["System", "mean s/trial"], rows_rt, "lr")

# tie diagnostic of the tuner (one registered run per noise level on the tuning seeds, method/tie_check.py): the tie cells in which
# the tied thresholds do not return identical models on the five tuning trajectories
td = {r["task"].split("_n")[1]: r["metrics"] for r in R if r["group"] == "tune_diag"}
assert sorted(td) == sorted(LV)                      # one run per noise level, five cells each
tot = lambda k: sum(int(td[lv][k]) for lv in LV)
assert (tot("cells"), tot("cells_with_tie"), tot("tie_cells_identical_models"), tot("tie_cells_differing_models"),
        tot("tie_cells_other_smoothing"), tot("mean_rule_changes")) == (30, 19, 17, 2, 0, 0)
rows = []
for lv in LV:
    tm = td[lv]
    for k in [k for k in tm if k.endswith("_traj_differ")]:
        key = k[:-len("_traj_differ")]
        thr = sorted((float(m.split("_t")[-1]), tm[m]) for m in tm if m.startswith(f"{key}_mean_err_t"))
        sel = TUNED[key][lv]["thr"]
        assert sel == max(t for t, _ in thr) and min(thr, key=lambda x: x[1])[0] == sel   # both rules select it
        rows.append([f"{SHORT[[n for n in KEY if KEY[n] == key][0]]}, {lv}\\%", " / ".join("%g" % t for t, _ in thr),
                     "%d of 5" % tm[k], " / ".join("%.4f" % e for _, e in thr)])
assert [r[0] for r in rows] == ["FD, 5\\%", "Spline, 10\\%"] and [r[2] for r in rows] == ["3 of 5", "1 of 5"]
table(T + "rep_ties.tex", ["Cell", "tied $\\lambda$", "differ", "mean tuning error"], rows, "llrr")
print("ok")
