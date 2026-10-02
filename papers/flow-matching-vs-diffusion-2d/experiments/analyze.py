"""Registered tests, derived tables and figures; reads only results/runs.jsonl."""
import json, os, collections, numpy as np
from scipy import stats
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
rows = [json.loads(l) for l in open("results/runs.jsonl")]
os.makedirs("results/analysis", exist_ok=True)  # by-product tables; the paper reports tests through rh compare and \rhval
M = collections.defaultdict(dict)  # (task,name) -> seed -> metrics
for r in rows:
    if r["status"] == "ok" and r["group"] in ("main", "abl_schedule", "abl_reflow"): M[(r["task"], r["name"])][r["seed"]] = r["metrics"]
TASKS = ["eight_gaussians", "two_moons", "checkerboard"]; TN = {"eight_gaussians": "8 Gauss.", "two_moons": "Moons", "checkerboard": "Checker."}
KS = [1, 2, 4, 8, 16, 32, 64, 100]
def vec(t, n, m, seeds=range(5)): return np.array([M[(t, n)][s][m] for s in seeds])
def mean(t, n, m, seeds=range(5)): return vec(t, n, m, seeds).mean()
def paired(t, a, b, m):  # a vs b, a - b
    x, y = vec(t, a, m), vec(t, b, m); r = stats.ttest_rel(x, y); return (x - y).mean(), r.statistic, r.pvalue
FM, DD, RF, HE = "Flow Matching (Euler)", "DDIM", "Reflow-1 (Euler)", "Flow Matching (Heun)"
out = []
def line(*c): out.append(" & ".join(c) + r" \\")
out += [r"\begin{tabular}{llrrrr}", r"\toprule", r"Hyp. & Task & Quantity & Diff./ratio & $t$ & $p$ \\", r"\midrule"]
res = {}
for t in TASKS:
    d, ts, p = paired(t, FM, DD, "sw_k4"); line("H1", TN[t], r"SW@4 FM$-$DDIM", f"{d:.3f}", f"{ts:.2f}", f"{p:.3g}"); res[f"H1_{t}"] = (d, ts, p)
for t in TASKS:
    r4 = mean(t, DD, "sw_k4") / mean(t, FM, "sw_k4"); r100 = mean(t, DD, "sw_k100") / mean(t, FM, "sw_k100")
    line("H2", TN[t], r"SW DDIM/FM, K=4 / K=100", f"{r4:.2f} / {r100:.2f}", "--", "--"); res[f"H2_{t}"] = (r4, r100)
for t in TASKS:
    for m, lab in (("sw_k1", "SW@1"), ("sw_k100", "SW@100")):
        d, ts, p = paired(t, RF, FM, m); line("H3", TN[t], lab + r" Reflow$-$FM", f"{d:.4f}", f"{ts:.2f}", f"{p:.3g}"); res[f"H3_{t}_{m}"] = (d, ts, p)
for t in TASKS:
    for a, b, lab in ((FM, DD, r"straight FM$-$DDIM"), (RF, FM, r"straight Reflow$-$FM")):
        d, ts, p = paired(t, a, b, "straight"); line("H4", TN[t], lab, f"{d:.3f}", f"{ts:.2f}", f"{p:.3g}"); res[f"H4_{t}_{a}"] = (d, ts, p)
out += [r"\bottomrule", r"\end{tabular}"]
open("results/analysis/tests.tex", "w").write("\n".join(out) + "\n")
# exploratory: equal NFE, Heun with K steps (2K evals) vs Euler with 2K steps; paired test on seeds
out = [r"\begin{tabular}{lrrrrrr}", r"\toprule", r"NFE & \multicolumn{2}{c}{8 Gauss.} & \multicolumn{2}{c}{Moons} & \multicolumn{2}{c}{Checker.} \\", r" & Heun & Euler & Heun & Euler & Heun & Euler \\", r"\midrule"]
for K in (1, 2, 4, 8, 16, 32):
    c = [str(2 * K)]
    for t in TASKS: c += [f"{mean(t, HE, f'sw_k{K}'):.3f}", f"{mean(t, FM, f'sw_k{2*K}'):.3f}"]
    line(*c)
out += [r"\bottomrule", r"\end{tabular}"]
open("results/analysis/nfe.tex", "w").write("\n".join(out) + "\n")
# reflow-2 vs reflow-1 and teacher-4 on seeds 0-2 (paired)
out = [r"\begin{tabular}{llrrr}", r"\toprule", r"Task & Comparison (3 seeds) & Diff. SW@1 & Diff. SW@100 & $p$ (SW@1) \\", r"\midrule"]
for t in TASKS:
    for a, lab in (("Reflow-2 (Euler)", "Reflow-2 $-$ Reflow-1"), ("Reflow-1 (teacher 4 steps)", "Teacher-4 $-$ Teacher-100")):
        x1, y1 = vec(t, a, "sw_k1", range(3)), vec(t, RF, "sw_k1", range(3)); x2, y2 = vec(t, a, "sw_k100", range(3)), vec(t, RF, "sw_k100", range(3))
        line(TN[t], lab, f"{(x1-y1).mean():.3f}", f"{(x2-y2).mean():.3f}", f"{stats.ttest_rel(x1, y1).pvalue:.3g}")
out += [r"\bottomrule", r"\end{tabular}"]
open("results/analysis/reflow_paired.tex", "w").write("\n".join(out) + "\n")
# exploratory (not registered) paired tests over the 5 seeds: mean difference (two-sided p) per task
AN = "DDPM ancestral"
def paired2(t, a, ma, b, mb):
    x, y = vec(t, a, ma), vec(t, b, mb); return (x - y).mean(), stats.ttest_rel(x, y).pvalue
def pfmt(p): return f"{p:.3f}" if p >= 0.001 else "$<$0.001"
EX = [(r"SW@100 FM$-$DDIM", FM, "sw_k100", DD, "sw_k100", 3), (r"MMD@4 FM$-$DDIM", FM, "mmd_k4", DD, "mmd_k4", 4),
      (r"MMD@1 FM$-$DDIM", FM, "mmd_k1", DD, "mmd_k1", 3),
      (r"SW@4 Anc.$-$DDIM", AN, "sw_k4", DD, "sw_k4", 3), (r"MMD@4 Anc.$-$DDIM", AN, "mmd_k4", DD, "mmd_k4", 4),
      (r"SW Heun@4$-$Euler@8", HE, "sw_k4", FM, "sw_k8", 3), (r"SW Heun@4$-$DDIM@8", HE, "sw_k4", DD, "sw_k8", 3),
      (r"SW Heun@2$-$Euler@4", HE, "sw_k2", FM, "sw_k4", 3), (r"SW Heun@1$-$Euler@2", HE, "sw_k1", FM, "sw_k2", 3)]
out = [r"\begin{tabular}{lrrr}", r"\toprule", r"Paired difference & 8 Gauss. & Moons & Checker. \\", r"\midrule"]
for lab, a_, ma, b_, mb, pr in EX:
    c = [lab]
    for t in TASKS:
        d, p = paired2(t, a_, ma, b_, mb); c.append(f"{d:.{pr}f} ({pfmt(p)})"); res[f"EX_{lab}_{t}"] = (d, p)
    line(*c)
out += [r"\bottomrule", r"\end{tabular}"]
open("results/analysis/expl.tex", "w").write("\n".join(out) + "\n")
# one compact table for the paper: registered tests, exploratory tests, reflow ablation tests (same numbers as above)
def cell(d, p, pr): return f"{d:.{pr}f} ({pfmt(p)})"
out = [r"\begin{tabular}{llrrr}", r"\toprule", r" & Quantity & 8 Gauss. & Moons & Checker. \\", r"\midrule",
       r"\multicolumn{5}{l}{\emph{Registered tests (5 seeds)}} \\"]
line("H1", r"SW@4 FM$-$DDIM", *[cell(res[f"H1_{t}"][0], res[f"H1_{t}"][2], 3) for t in TASKS])
line("H2", r"SW DDIM/FM, $K{=}4\to100$", *[f"{res[f'H2_{t}'][0]:.2f} $\\to$ {res[f'H2_{t}'][1]:.2f}" for t in TASKS])
line("H3", r"SW@1 Reflow$-$FM", *[cell(res[f"H3_{t}_sw_k1"][0], res[f"H3_{t}_sw_k1"][2], 3) for t in TASKS])
line("H3", r"SW@100 Reflow$-$FM", *[cell(res[f"H3_{t}_sw_k100"][0], res[f"H3_{t}_sw_k100"][2], 4) for t in TASKS])
line("H4", r"straight FM$-$DDIM", *[cell(res[f"H4_{t}_{FM}"][0], res[f"H4_{t}_{FM}"][2], 3) for t in TASKS])
line("H4", r"straight Reflow$-$FM", *[cell(res[f"H4_{t}_{RF}"][0], res[f"H4_{t}_{RF}"][2], 3) for t in TASKS])
out += [r"\midrule", r"\multicolumn{5}{l}{\emph{Exploratory, not registered (5 seeds)}} \\"]
for lab, a_, ma, b_, mb, pr in EX: line("", lab, *[cell(*res[f"EX_{lab}_{t}"], pr) for t in TASKS])
out += [r"\midrule", r"\multicolumn{5}{l}{\emph{Reflow ablations (seeds 0--2)}} \\"]
for a_, lab in (("Reflow-2 (Euler)", "Reflow-2$-$Reflow-1"), ("Reflow-1 (teacher 4 steps)", "Teacher-4$-$Reflow-1")):
    for m, ml in (("sw_k1", "SW@1"), ("sw_k100", "SW@100")):
        c = []
        for t in TASKS:
            x, y = vec(t, a_, m, range(3)), vec(t, RF, m, range(3)); c.append(cell((x - y).mean(), stats.ttest_rel(x, y).pvalue, 4 if m == "sw_k100" and a_.startswith("Reflow-2") else 3))
        line("", f"{ml} {lab}", *c)
out += [r"\bottomrule", r"\end{tabular}"]
open("results/analysis/tests_all.tex", "w").write("\n".join(out) + "\n")
json.dump({k: list(map(float, v)) for k, v in res.items()}, open("results/tests.json", "w"), indent=1)
# figures
col = {DD: "tab:red", "DDPM ancestral": "tab:orange", FM: "tab:blue", HE: "tab:cyan", RF: "tab:green"}
fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.7), sharey=True)
for a, t in zip(ax, TASKS):
    for n in (DD, "DDPM ancestral", FM, HE, RF):
        mu = np.array([mean(t, n, f"sw_k{k}") for k in KS]); sd = np.array([vec(t, n, f"sw_k{k}").std(ddof=1) for k in KS])
        a.errorbar(KS, mu, sd, label=n.replace(" (Euler)", ""), color=col[n], marker="o", ms=2.5, lw=1, capsize=1.5)
    a.axhline(mean(t, "Real data (floor)", "sw_k1"), color="k", ls=":", lw=1, label="real-data floor")
    a.set_xscale("log"); a.set_yscale("log"); a.set_title(TN[t], fontsize=8); a.set_xlabel("sampling steps K", fontsize=7); a.tick_params(labelsize=6)
ax[0].set_ylabel("sliced $W_1$", fontsize=7)
h, l = ax[0].get_legend_handles_labels(); fig.legend(h, l, loc="lower center", ncol=6, fontsize=6)
plt.tight_layout(rect=(0, 0.08, 1, 1)); plt.savefig("results/figures/sw_vs_steps.pdf"); plt.close()
fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.3), sharey=True)
for a, t in zip(ax, TASKS):
    for n in (DD, "DDPM ancestral", FM, HE, RF):
        mu = np.array([mean(t, n, f"mmd_k{k}") for k in KS]); a.plot(KS, mu, label=n.replace(" (Euler)", ""), color=col[n], marker="o", ms=2.5, lw=1)
    a.axhline(mean(t, "Real data (floor)", "mmd_k1"), color="k", ls=":", lw=1)
    a.set_xscale("log"); a.set_yscale("log"); a.set_title(TN[t], fontsize=8); a.set_xlabel("sampling steps K", fontsize=7); a.tick_params(labelsize=6)
ax[0].set_ylabel("MMD$^2$", fontsize=7)
plt.tight_layout(); plt.savefig("results/figures/mmd_vs_steps.pdf"); plt.close()
# ablation figure, single-column size
fig, ax = plt.subplots(1, 2, figsize=(3.5, 2.75))
LS = ("-", "--", ":")
SCH = ((DD, "tab:red", "DDIM, linear (main)"), ("DDIM (cosine)", "tab:purple", "DDIM, cosine"), ("DDIM (cosine, start at ab>=4e-5)", "tab:pink", r"DDIM, cosine, start $\bar\alpha\geq4\!\times\!10^{-5}$"))
RFL = ((FM, "tab:blue", "FM (Euler)"), (RF, "tab:green", "Reflow-1"), ("Reflow-1 (teacher 4 steps)", "tab:olive", "Reflow-1, 4-step teacher"), ("Reflow-2 (Euler)", "tab:brown", "Reflow-2"))
for a, grp in zip(ax, (SCH, RFL)):
    for t, ls in zip(TASKS, LS):
        for n, c, lab in grp: a.plot(KS, [mean(t, n, f"sw_k{k}", range(3)) for k in KS], color=c, ls=ls, lw=1)
    for n, c, lab in grp: a.plot([], [], color=c, label=lab)
    a.set_xscale("log"); a.set_yscale("log"); a.set_xlabel("sampling steps K", fontsize=7); a.tick_params(labelsize=6)
for t, ls in zip(TASKS, LS): ax[1].plot([], [], color="gray", ls=ls, label=TN[t])
ax[0].legend(fontsize=5.5, loc="upper center", bbox_to_anchor=(0.5, -0.24), frameon=False)
ax[1].legend(fontsize=5.5, loc="upper center", bbox_to_anchor=(0.5, -0.24), frameon=False, ncol=2, columnspacing=0.8, handlelength=1.5)
ax[0].set_ylabel("sliced $W_1$ (seeds 0-2)", fontsize=7); ax[0].set_title("diffusion schedule", fontsize=7); ax[1].set_title("flow / reflow variants", fontsize=7)
plt.tight_layout(pad=0.3, w_pad=0.8); plt.savefig("results/figures/ablations.pdf", bbox_inches="tight", pad_inches=0.02); plt.close()
print(open("results/analysis/tests_all.tex").read()); print(open("results/analysis/tests.tex").read()); print(open("results/analysis/expl.tex").read()); print(open("results/analysis/nfe.tex").read()); print(open("results/analysis/reflow_paired.tex").read())
