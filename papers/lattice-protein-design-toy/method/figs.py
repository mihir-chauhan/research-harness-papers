import json, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
rows = [json.loads(l) for l in open("results/runs.jsonl")]
def vals(group, name, m, cfg=None):
    return np.array([r["metrics"][m] for r in rows if r["group"] == group and r["name"] == name and r["metrics"].get(m) is not None
                     and (cfg is None or r["config"].get("data_frac") == cfg)])
Ks = [1, 10, 100, 1000]
plt.rcParams.update({"font.size": 8})
fig, ax = plt.subplots(figsize=(3.4, 3.3))
for (g, n, lab, c, mk) in [("main", "Conditional AR designer", "Conditional AR", "#1f77b4", "o"), ("main", "Contact heuristic", "Contact heuristic", "#2ca02c", "s"),
                            ("extra_sa_warm", "SA from contact heuristic", "SA, heuristic init", "#9467bd", "^"),
                            ("extra_sa_log", "SA graded objective", "SA graded obj.", "#ff7f0e", "D"),
                            ("extra_sa_log", "SA graded objective, heuristic init", "SA graded, heur. init", "#8c564b", "P"),
                            ("main", "Simulated annealing", "SA (random init)", "#d62728", "v"), ("main", "Random search", "Random search", "#7f7f7f", "x")]:
    mu = np.array([vals(g, n, f"succ_k{k}").mean() for k in Ks]); sd = np.array([vals(g, n, f"succ_k{k}").std(ddof=1) for k in Ks])
    ax.errorbar(Ks, mu, sd, label=lab, color=c, marker=mk, ms=4, capsize=2, lw=1.2)
ax.set_xscale("log"); ax.set_xlabel("oracle calls per design K"); ax.set_ylabel("fraction of test targets designed"); ax.legend(fontsize=5.5, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2); ax.set_ylim(-0.02, 1.02)
fig.tight_layout(); fig.savefig("results/figures/budget_curves.pdf"); plt.close(fig)

fig, axs = plt.subplots(1, 2, figsize=(6.8, 2.4))
fr = [0.1, 0.25, 0.5, 1.0]
for k, c in ((1, "#1f77b4"), (100, "#ff7f0e")):
    pts = [(vals("sweep_data_frac", "Conditional AR designer", f"succ_k{k}", f) if f < 1 else vals("abl_components", "Conditional AR designer", f"succ_k{k}")) for f in fr]
    axs[0].errorbar(fr, [p.mean() for p in pts], [p.std(ddof=1) for p in pts], marker="o", ms=4, capsize=2, color=c, label=f"K={k}")
axs[0].set_xscale("log"); axs[0].set_xlabel("fraction of sequence space scored"); axs[0].set_ylabel("success"); axs[0].legend(fontsize=7); axs[0].set_ylim(0, 1)
names = [("abl_components", "Conditional AR designer", "full"), ("abl_components", "No reversal augmentation", "no aug."), ("abl_components", "Unconditional AR", "uncond.")]
w = 0.35
for j, (k, c) in enumerate(((1, "#1f77b4"), (100, "#ff7f0e"))):
    m = [vals(g, n, f"succ_k{k}") for g, n, _ in names]
    axs[1].bar(np.arange(3) + (j - 0.5) * w, [x.mean() for x in m], w, yerr=[x.std(ddof=1) for x in m], capsize=2, color=c, label=f"K={k}")
axs[1].set_xticks(range(3)); axs[1].set_xticklabels([n[2] for n in names]); axs[1].set_ylabel("success"); axs[1].legend(fontsize=7); axs[1].set_ylim(0, 1)
fig.tight_layout(); fig.savefig("results/figures/ablations.pdf"); plt.close(fig)
