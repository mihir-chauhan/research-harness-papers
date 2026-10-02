"""Learning-curve figure and per-seed table, both read from results/runs.jsonl (group main)."""
import json, collections
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
R = {}
for l in open("results/runs.jsonl"):
    r = json.loads(l)
    if r["group"] == "main" and r["status"] == "ok":
        R[(r["name"], r["task"], r["seed"])] = r["metrics"]["test_acc"]
names = ["Pixels + LR", "PCA + LR", "Random CNN + probe", "Supervised scratch", "Rotation (reimplemented)", "SimCLR-style probe"]
ns = [("n10", 10), ("n50", 50), ("n200", 200)]
fig, ax = plt.subplots(figsize=(3.4, 2.6))
for nm in names:
    m = [np.mean([R[(nm, t, s)] for s in range(5)]) for t, _ in ns]
    sd = [np.std([R[(nm, t, s)] for s in range(5)], ddof=1) for t, _ in ns]
    ax.errorbar([n for _, n in ns], m, yerr=sd, marker="o", ms=3, capsize=2, lw=1.2, label=nm.replace(" (reimplemented)", ""))
ax.set_xscale("log"); ax.set_xticks([10, 50, 200]); ax.set_xticklabels(["10", "50", "200"])
ax.set_xlabel("labels"); ax.set_ylabel("test accuracy"); ax.legend(fontsize=5.5); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig("results/figures/learning_curves.pdf")
L = [r"\begin{tabular}{lrrrrr}", r"\toprule", r"System & s0 & s1 & s2 & s3 & s4 \\", r"\midrule"]
for nm in ["Supervised scratch", "Random CNN + probe", "SimCLR-style probe"]:
    L.append(nm + " & " + " & ".join(f"{R[(nm,'n10',s)]:.3f}" for s in range(5)) + r" \\")
L += [r"\bottomrule", r"\end{tabular}"]
open("results/tables/perseed_n10.tex", "w").write("\n".join(L) + "\n"); print("\n".join(L))

# sensitivity figure (n50), values from the registry; defaults (tau=0.5, 60 epochs) from group main
S = collections.defaultdict(list)
for l in open("results/runs.jsonl"):
    r = json.loads(l)
    if r["status"] != "ok": continue
    if r["group"] == "sweep_tau": S[("tau", r["config"]["tau"])].append(r["metrics"]["test_acc"])
    if r["group"] == "sweep_epochs": S[("ep", r["config"]["epochs"])].append(r["metrics"]["test_acc"])
    if r["group"] == "main" and r["name"] == "SimCLR-style probe" and r["task"] == "n50":
        S[("tau", 0.5)].append(r["metrics"]["test_acc"]); S[("ep", 60)].append(r["metrics"]["test_acc"])
fig, axs = plt.subplots(1, 2, figsize=(3.4, 1.9))
for ax, k, lab in zip(axs, ["tau", "ep"], [r"temperature $\tau$", "pretraining epochs"]):
    xs = sorted(x for (kk, x) in S if kk == k)
    ax.errorbar(xs, [np.mean(S[(k, x)]) for x in xs], yerr=[np.std(S[(k, x)], ddof=1) for x in xs], marker="o", ms=3, capsize=2)
    ax.set_xlabel(lab, fontsize=7); ax.tick_params(labelsize=6); ax.grid(alpha=.3)
    if k == "ep": ax.set_xscale("log"); ax.minorticks_off(); ax.set_xticks(xs); ax.set_xticklabels([str(x) for x in xs])
axs[0].set_ylabel("test acc. (n50)", fontsize=7)
fig.tight_layout(); fig.savefig("results/figures/sensitivity_n50.pdf")
