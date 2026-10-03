"""Paired (by seed) differences between systems, computed from results/runs.jsonl. Writes flat JSON metrics.
d_<pair>_<metric> = mean over seeds of (A - B); p_<pair>_<metric> = two-sided paired t-test p; w_<pair>_<metric> = #seeds with A > B (Brier: A < B)."""
import json, sys, numpy as np
from scipy import stats
rows = [json.loads(l) for l in open("results/runs.jsonl")]
def get(group, name):
    d = {r["seed"]: r["metrics"] for r in rows if r["group"] == group and r["name"] == name and r["status"] == "ok"}
    assert len(d) == 5, (group, name, len(d)); return d
M = ("main", "GRU-D"), ("main", "GBDT (summary)"), ("main", "LR (summary)"), ("main", "GRU (forward-fill)"), ("main", "GRU (mask+delta)")
P = {  # pair id: (A, B)
 "md_ffill": (("main", "GRU (mask+delta)"), ("main", "GRU (forward-fill)")),
 "grud_ffill": (("main", "GRU-D"), ("main", "GRU (forward-fill)")),
 "grud_md": (("main", "GRU-D"), ("main", "GRU (mask+delta)")),
 "grud_gbdt": (("main", "GRU-D"), ("main", "GBDT (summary)")),
 "grud_lr": (("main", "GRU-D"), ("main", "LR (summary)")),
 "gbdt_lr": (("main", "GBDT (summary)"), ("main", "LR (summary)")),
 "ffill_lr": (("main", "GRU (forward-fill)"), ("main", "LR (summary)")),
 "noin_grud": (("abl_decay", "GRU-D w/o input decay"), ("main", "GRU-D")),
 "nohid_grud": (("abl_decay", "GRU-D w/o hidden decay"), ("main", "GRU-D")),
 "nodecay_grud": (("abl_decay", "GRU-D w/o any decay"), ("main", "GRU-D")),
 "lrnocnt_lr": (("abl_counts", "LR (summary) w/o counts"), ("main", "LR (summary)")),
 "gbnocnt_gb": (("abl_counts", "GBDT (summary) w/o counts"), ("main", "GBDT (summary)")),
}
for h in (12, 24):
    P[f"h{h}_gbdt_grud"] = (("sweep_horizon", f"GBDT (summary) @{h}h"), ("sweep_horizon", f"GRU-D @{h}h"))
    P[f"h{h}_gbdt_lr"] = (("sweep_horizon", f"GBDT (summary) @{h}h"), ("sweep_horizon", f"LR (summary) @{h}h"))
    P[f"h{h}_grud_lr"] = (("sweep_horizon", f"GRU-D @{h}h"), ("sweep_horizon", f"LR (summary) @{h}h"))
    P[f"h{h}_grud_ffill"] = (("sweep_horizon", f"GRU-D @{h}h"), ("sweep_horizon", f"GRU (forward-fill) @{h}h"))
    P[f"h{h}_md_ffill"] = (("sweep_horizon", f"GRU (mask+delta) @{h}h"), ("sweep_horizon", f"GRU (forward-fill) @{h}h"))
out = {}
for k, (A, B) in P.items():
    a, b = get(*A), get(*B)
    for m in ("auroc", "auprc", "brier"):
        x = np.array([a[s][m] for s in range(5)]); y = np.array([b[s][m] for s in range(5)]); d = x - y
        out[f"d_{k}_{m}"] = float(d.mean()); out[f"p_{k}_{m}"] = float(stats.ttest_rel(x, y).pvalue)
        out[f"w_{k}_{m}"] = int((d < 0).sum() if m == "brier" else (d > 0).sum())
print(json.dumps(out, indent=0)); json.dump(out, open(sys.argv[1], "w"))
