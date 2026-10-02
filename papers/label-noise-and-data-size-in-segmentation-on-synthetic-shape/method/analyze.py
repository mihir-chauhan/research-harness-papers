"""Derived statistics from results/runs.jsonl (registered tests H1-H3, size/noise curves, per-class IoU). Writes flat JSON."""
import json, sys
import numpy as np
from scipy import stats

rows = [json.loads(l) for l in open("results/runs.jsonl")]
CUTOFF = "2026-10-02T18:10"  # earlier rows are superseded pilots (300/450 steps)
rows = [r for r in rows if r.get("status") == "ok" and r["group"] in ("main", "size", "sweep_noise") and r["provenance"]["started"] >= CUTOFF]
CE = {}  # (task, n) -> {seed: metrics}
for r in rows:
    if r["group"] == "main" and r["name"] != "CE":
        continue
    if r["group"] == "sweep_noise" or r["name"].startswith("CE"):
        CE.setdefault((r["task"], r["config"]["n"]), {})[r["seed"]] = r["metrics"]


def vals(task, n, m="miou", seeds=None):
    d = CE[(task, n)]
    ks = sorted(d) if seeds is None else seeds
    return np.array([d[s][m] for s in ks])


def welch(a, b):
    t, p = stats.ttest_ind(a, b, equal_var=False)
    return float(t), float(p)


out = {}
for n in (100, 250, 500, 1000, 2000):
    for t in ("none", "boundary_p0.3", "flip_p0.3"):
        if (t, n) in CE:
            v = vals(t, n)
            k = f"{t.replace('.', '')}_n{n}"
            out[f"ce_miou_{k}"] = float(v.mean()); out[f"ce_miou_sd_{k}"] = float(v.std(ddof=1))
# per-class IoU for CE, clean, by N and flip_p0.3
for n in (100, 500, 2000):
    for t in ("none", "flip_p0.3"):
        for c in ("circle", "square", "triangle", "bg"):
            out[f"ce_iou_{c}_{t.replace('.', '')}_n{n}"] = float(vals(t, n, f"iou_{c}").mean())
# H1
a, b = vals("none", 2000), vals("none", 100)
out["h1_diff"] = float(a.mean() - b.mean()); out["h1_t"], out["h1_p"] = welch(a, b)
# H2
a, b = vals("boundary_p0.3", 500), vals("flip_p0.3", 500)
out["h2_diff"] = float(a.mean() - b.mean()); out["h2_t"], out["h2_p"] = welch(a, b)
c = vals("none", 500)
out["drop_boundary_n500"] = float(c.mean() - a.mean()); out["drop_flip_n500"] = float(c.mean() - b.mean())
out["h2_boundary_vs_clean_p"] = welch(a, c)[1]
# H3 (per-seed drops, seeds 0-4 at both N)
for t in ("flip_p0.3", "boundary_p0.3"):
    d = {n: vals("none", n) - vals(t, n) for n in (100, 2000)}
    tag = t.replace(".", "")
    out[f"drop_{tag}_n100"] = float(d[100].mean()); out[f"drop_{tag}_n2000"] = float(d[2000].mean())
    out[f"h3_{tag}_diff"] = float(d[100].mean() - d[2000].mean())
    out[f"h3_{tag}_t"], out[f"h3_{tag}_p"] = welch(d[100], d[2000])
# drop at all N for flip (seeds 0-2 common)
for n in (100, 250, 500, 1000, 2000):
    d = vals("none", n, seeds=[0, 1, 2]) - vals("flip_p0.3", n, seeds=[0, 1, 2])
    out[f"drop_flip_s012_n{n}"] = float(d.mean())
# noise-level sweep (CE, N=500)
for p in (0.1, 0.2, 0.3):
    t = f"flip_p{p}"
    v = vals(t, 500, seeds=[0, 1, 2])
    out[f"lvl_flip_{str(p).replace('.', '')}"] = float(v.mean()); out[f"lvl_flip_sd_{str(p).replace('.', '')}"] = float(v.std(ddof=1))
out["lvl_boundary_03_s012"] = float(vals("boundary_p0.3", 500, seeds=[0, 1, 2]).mean())
out["lvl_clean_s012"] = float(vals("none", 500, seeds=[0, 1, 2]).mean())
# memorisation gap: agreement with noisy labels minus agreement with clean labels (CE, flip_p0.3)
for n in (100, 500, 2000):
    out[f"fit_noisy_flip_n{n}"] = float(vals("flip_p0.3", n, "train_fit_noisy").mean())
    out[f"fit_clean_flip_n{n}"] = float(vals("flip_p0.3", n, "train_fit_clean").mean())
if len(sys.argv) > 1:
    json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out, indent=1))
