"""Ablation tables and extra figures; every number is read from results/runs.jsonl.
The tables hold only whole ablation groups (all logged seeds of a system), i.e. registry aggregates;
the main-group systems are reported in the rh-generated main table, not as seed subsets here."""
import json, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = [json.loads(l) for l in open("results/runs.jsonl")]
R = [r for r in R if r["kind"] not in ("sanity", "control") and r["status"] == "ok"]
def rows(group, name, task, seeds=(0, 1, 2)):
    return [r["metrics"] for r in R if r["group"] == group and r["name"] == name and r["task"] == task and r["seed"] in seeds]
def ms(rs, k, p=3):
    v = np.array([r[k] for r in rs]); return f"{v.mean():.{p}f} $\\pm$ {v.std(ddof=1):.{p}f}"
def table(path, spec, cols, head):
    out = ["\\begin{tabular}{l" + "c" * len(cols) + "}", "\\toprule", head + " \\\\", "\\midrule"]
    for label, rs in spec: out.append(label + " & " + " & ".join(ms(rs, k) for k in cols) + " \\\\")
    out += ["\\bottomrule", "\\end{tabular}"]; open(path, "w").write("\n".join(out) + "\n")
T = "F20_c10"
# AR(1) amplitude / memory (ablation group, seeds 0-2)
spec = [("AR(1) $\\sigma\\times0.5$", rows("abl_ar1", "AR(1) sigma x0.5", T)),
        ("AR(1) $\\sigma\\times1.5$", rows("abl_ar1", "AR(1) sigma x1.5", T)),
        ("White noise ($\\phi\\!=\\!0$)", rows("abl_ar1", "AR(1) white (phi=0)", T))]
assert all(len(r) == 3 for _, r in spec)
table("results/tables/ar1_matched.tex", spec, ["valid_time", "var_ratio", "w1_pdf", "spec_err"], "Closure noise & valid\\_time & var\\_ratio & w1\\_pdf & spec\\_err")
# MLP inputs
spec = [("$X_{k-1},X_k,X_{k+1}$", rows("abl_mlpin", "MLP stencil 1", T)),
        ("$X_{k-3..k+3}$", rows("abl_mlpin", "MLP stencil 3", T))]
table("results/tables/mlp_in.tex", spec, ["offline_r2", "valid_time", "mean_err", "w1_pdf", "spec_err"], "MLP input & offline\\_r2 & valid\\_time & mean\\_err & w1\\_pdf & spec\\_err")
# forcing shift (ablation group, seeds 0-2)
out = ["\\begin{tabular}{llccccc}", "\\toprule", "Deploy $F$ & System & valid\\_time & mean\\_err & var\\_err & w1\\_pdf & spec\\_err \\\\", "\\midrule"]
for lab, F in [("18", 18), ("22", 22)]:
    for nm, sh in [("Polynomial (deg 4)", "Polynomial deg 4"), ("MLP (32x2)", "MLP 32x2"), ("AR(1) stochastic", "AR(1) stochastic")]:
        rs = rows("abl_shift", f"{sh}, deploy F={F}", T); assert len(rs) == 3
        out.append(f"{lab} & {nm} & " + " & ".join(ms(rs, k) for k in ["valid_time", "mean_err", "var_err", "w1_pdf", "spec_err"]) + " \\\\")
    out.append("\\midrule")
out[-1] = "\\bottomrule"; out.append("\\end{tabular}"); open("results/tables/shift.tex", "w").write("\n".join(out) + "\n")
# figure: spectrum log-ratio per wavenumber
cols = {"No closure": "#999999", "Polynomial (deg 4)": "#1b6ca8", "MLP (32x2)": "#d98c00", "AR(1) stochastic": "#b2182b"}
fig, ax = plt.subplots(1, 2, figsize=(3.5, 1.9), sharey=True)
for a, t in zip(ax, ["F20_c10", "F20_c4"]):
    for nm, c in cols.items():
        rs = rows("main", nm, t, range(5)); v = np.array([[r[f"logspec_k{k}"] for k in range(1, 5)] for r in rs])
        a.errorbar(np.arange(1, 5), v.mean(0), v.std(0, ddof=1), color=c, marker="o", ms=3, lw=1, capsize=2, label=nm)
    a.axhline(0, color="k", lw=.6); a.set_title(t.replace("_", "\\_") if False else t, fontsize=7); a.set_xlabel("wavenumber $m$", fontsize=7); a.set_xticks(range(1, 5)); a.tick_params(labelsize=6)
ax[0].set_ylabel("$\\log_{10}(P_{model}/P_{truth})$", fontsize=7); ax[0].legend(fontsize=5, frameon=False)
plt.tight_layout(); plt.savefig("results/figures/spectrum_ratio.pdf"); plt.close()
# figure: polynomial degree sweep
degs = [1, 2, 3, 4, 5, 6]
def drow(d): return rows("main", "Polynomial (deg 4)", T) if d == 4 else rows("abl_deg", f"Polynomial deg {d}", T)
fig, ax = plt.subplots(1, 3, figsize=(3.5, 1.7))
for a, (k, lab) in zip(ax, [("offline_r2", "offline $R^2$"), ("valid_time", "valid time"), ("spec_err", "spec\\_err")]):
    v = np.array([[r[k] for r in drow(d)] for d in degs]); a.errorbar(degs, v.mean(1), v.std(1, ddof=1), marker="o", ms=3, lw=1, capsize=2, color="#1b6ca8")
    a.set_xlabel("degree", fontsize=7); a.set_title(lab.replace("\\_", "_"), fontsize=7); a.tick_params(labelsize=6)
plt.tight_layout(); plt.savefig("results/figures/degree_sweep.pdf"); plt.close()
print("ok")
# degree table (ablation group, seeds 0-2; degree 4 is the main-group polynomial, see the main table)
spec = [(f"Degree {d}", drow(d)) for d in degs if d != 4]
table("results/tables/degree.tex", spec, ["offline_r2", "valid_time", "mean_err", "w1_pdf", "spec_err"], "Polynomial & offline\\_r2 & valid\\_time & mean\\_err & w1\\_pdf & spec\\_err")
# skill vs climate trade-off over every F20_c10 configuration run at the training forcing (3 matched seeds)
cfgs = [("No closure", "main", "No closure", "#999999"), ("Poly d4", "main", "Polynomial (deg 4)", "#1b6ca8"), ("MLP local", "main", "MLP (32x2)", "#d98c00"),
        ("AR1", "main", "AR(1) stochastic", "#b2182b"), ("AR1 x0.5", "abl_ar1", "AR(1) sigma x0.5", "#b2182b"), ("AR1 x1.5", "abl_ar1", "AR(1) sigma x1.5", "#b2182b"),
        ("white", "abl_ar1", "AR(1) white (phi=0)", "#b2182b"), ("MLP s1", "abl_mlpin", "MLP stencil 1", "#d98c00"), ("MLP s3", "abl_mlpin", "MLP stencil 3", "#d98c00"),
        ] + [(f"Poly d{d}", "abl_deg", f"Polynomial deg {d}", "#1b6ca8") for d in (1, 2, 3, 5, 6)]
OFF = {"Poly d4": (-24, -1), "MLP local": (3, 1), "Poly d5": (3, -6), "Poly d6": (3, 0), "Poly d1": (-22, -1), "white": (3, 1), "AR1": (-12, -7)}  # label offsets (points)
fig, ax = plt.subplots(figsize=(3.5, 2.3))
for lab, g, nm, c in cfgs:
    rs = rows(g, nm, T); x = np.mean([r["valid_time"] for r in rs]); y = np.mean([r["spec_err"] for r in rs])
    ax.scatter(x, y, color=c, s=14); ax.annotate(lab, (x, y), fontsize=5, xytext=OFF.get(lab, (2, 2)), textcoords="offset points")
ax.set_yscale("log"); ax.set_yticks([0.03, 0.05, 0.1, 0.2, 0.4]); ax.set_yticklabels(["0.03", "0.05", "0.1", "0.2", "0.4"]); ax.minorticks_off(); ax.set_xlim(0.3, 1.72); ax.set_xlabel("valid time (higher better)", fontsize=7); ax.set_ylabel("spec\\_err (lower better)".replace("\\", ""), fontsize=7); ax.tick_params(labelsize=6)
plt.tight_layout(); plt.savefig("results/figures/tradeoff.pdf"); plt.close()
