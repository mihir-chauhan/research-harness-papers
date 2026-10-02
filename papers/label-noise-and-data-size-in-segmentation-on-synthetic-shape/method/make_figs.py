"""Figures drawn only from results/runs.jsonl (ok rows, final-budget runs)."""
import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
rows = [json.loads(l) for l in open("results/runs.jsonl")]
rows = [r for r in rows if r.get("status") == "ok" and r["group"] in ("main", "size") and r["provenance"]["started"] >= "2026-10-02T18:10"]
def get(task, n, name="CE", m="miou"):
    v = [r["metrics"][m] for r in rows if r["task"] == task and ((r["group"] == "main" and r["name"] == name and n == 500 and r["config"]["n"] == 500) or (r["group"] == "size" and r["name"] == f"CE n={n}"))]
    return np.array(v)
Ns = [100, 250, 500, 1000, 2000]
fig, ax = plt.subplots(figsize=(3.4, 2.5))
for t, c in (("none", "#1f77b4"), ("boundary_p0.3", "#2ca02c"), ("flip_p0.3", "#d62728")):
    xs = [n for n in Ns if len(get(t, n))]
    ax.errorbar(xs, [get(t, n).mean() for n in xs], [get(t, n).std(ddof=1) for n in xs], marker="o", ms=3, capsize=2, label=t, color=c)
ax.set_xscale("log"); ax.set_xlabel("training images N"); ax.set_ylabel("test mIoU"); ax.legend(fontsize=7); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig("results/figures/size_curves.pdf")
fig, ax = plt.subplots(figsize=(3.4, 2.5))
cls = ["iou_circle", "iou_square", "iou_triangle"]
for k, (t, c) in enumerate((("none", "#1f77b4"), ("boundary_p0.3", "#2ca02c"), ("flip_p0.3", "#d62728"))):
    m = [get(t, 500, m=q).mean() for q in cls]; s = [get(t, 500, m=q).std(ddof=1) for q in cls]
    ax.bar(np.arange(3) + 0.27 * (k - 1), m, 0.27, yerr=s, capsize=2, color=c, label=t)
ax.set_xticks(range(3)); ax.set_xticklabels(["circle", "square", "triangle"]); ax.set_ylabel("test IoU (CE, N=500)"); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig("results/figures/perclass_ce.pdf")
