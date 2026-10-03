import json, collections, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
d = collections.defaultdict(list)
for l in open("results/runs.jsonl"):
    r = json.loads(l)
    if r["group"] in ("main",) and r["status"] == "ok" and r["task"] != "sens": d[(r["name"], r["config"]["lr"])].append(r["metrics"]["val_loss"])
plt.figure(figsize=(3.4, 2.6))
for n, mk in [("Constant", "o"), ("Warmup+Cosine", "s"), ("Step decay", "^"), ("Schedule-free AdamW", "D")]:
    lrs = sorted(k[1] for k in d if k[0] == n)
    plt.errorbar(lrs, [np.mean(d[(n, x)]) for x in lrs], [np.std(d[(n, x)], ddof=1) for x in lrs], marker=mk, ms=4, capsize=2, label=n, lw=1)
plt.xscale("log"); plt.xlabel("peak learning rate"); plt.ylabel("final val loss (nats)"); plt.legend(fontsize=6); plt.grid(alpha=.3); plt.tight_layout()
plt.savefig("results/figures/val_vs_lr.pdf")
