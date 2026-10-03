"""Figures read only from results/runs.jsonl."""
import json, collections, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
rows = [json.loads(l) for l in open("results/runs.jsonl")]
rows = [r for r in rows if r.get("status") == "ok"]
SYS = ["MSE-MLP", "GMM head", "DDPM head"]; COL = {"MSE-MLP": "#c0392b", "GMM head": "#2874a6", "DDPM head": "#229954"}
# Fig 1: success vs start jitter (0.01 point = main bimodal50 rows)
d = collections.defaultdict(list)
for r in rows:
    if r["group"] == "sweep_jitter":
        s = r["name"].split(" (")[0]; j = r["config"]["jit"]; d[(s, j)].append(r["metrics"]["success"])
    if r["group"] == "main" and r["task"] == "bimodal50":
        d[(r["name"], 0.01)].append(r["metrics"]["success"])
fig, ax = plt.subplots(figsize=(3.4, 2.4))
js = sorted({k[1] for k in d}); x = np.arange(len(js))
for s in SYS:
    m = [np.mean(d[(s, j)]) for j in js]; sd = [np.std(d[(s, j)]) for j in js]
    ax.errorbar(x, m, yerr=sd, marker="o", ms=3, capsize=2, label=s, color=COL[s])
ax.set_xticks(x); ax.set_xticklabels([str(j) for j in js]); ax.set_xlabel("start jitter half-width"); ax.set_ylabel("success rate")
ax.legend(fontsize=7); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig("results/figures/jitter_success.pdf")
# Fig 2: mode shares on bimodal80 and bimodal50 (upper_frac per seed)
fig, axs = plt.subplots(1, 2, figsize=(3.4, 2.2), sharey=True)
for ax, t, tgt in zip(axs, ["bimodal50", "bimodal80"], [.5, .8]):
    for i, s in enumerate(SYS):
        v = [r["metrics"]["upper_frac"] for r in rows if r["group"] == "main" and r["task"] == t and r["name"] == s]
        ax.scatter(np.full(len(v), i) + np.linspace(-.15, .15, len(v)), v, s=8, color=COL[s])
    ax.axhline(tgt, ls="--", c="k", lw=.8); ax.set_title(t, fontsize=8); ax.set_xticks(range(3)); ax.set_xticklabels(["MSE", "GMM", "DDPM"], fontsize=7)
axs[0].set_ylabel("upper-mode share of successes"); fig.tight_layout(); fig.savefig("results/figures/mode_share.pdf")
