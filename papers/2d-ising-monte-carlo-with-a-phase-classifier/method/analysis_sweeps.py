"""Per-setting summaries of the two sensitivity sweeps (seeds 0-4); the default setting comes from the main group rows of the same seeds."""
import json, sys
import numpy as np

rows = [json.loads(l) for l in open("results/runs.jsonl")]
rows = [r for r in rows if r["status"] == "ok"]
SEEDS = range(5)
M = {}
for sysn, k in (("MLP", "mlp"), ("CNN", "cnn")):
    for grp, p, default, vals in (("sweep_margin", "margin", 0.3, [0.15, 0.3, 0.45, 0.6]), ("sweep_nsamp", "nsamp", 50, [10, 25, 50]),
                           ("sweep_nsamp_ep", "nsamp_ep", 50, [10, 25, 50])):
        for v in vals:
            if v == default:
                sel = [r for r in rows if r["group"] == "main" and r["name"] == sysn and r["seed"] in SEEDS]
            else:
                sel = [r for r in rows if r["group"] == grp and r["name"] == sysn and r["config"].get(p.replace("_ep", "")) == v]
            assert len(sel) == 5, (sysn, p, v, len(sel))
            tag = f"{k}_{p}{str(v).replace('.', 'p')}"
            for m, short in (("tc_error_l16", "l16"), ("tc_error_l32", "l32"), ("tc_error_fss", "fss"), ("acc_far", "acc")):
                x = np.array([r["metrics"][m] for r in sel])
                M[f"{tag}_{short}_mean"], M[f"{tag}_{short}_std"] = float(x.mean()), float(x.std(ddof=1))
        for v in vals:
            tag = f"{k}_{p}{str(v).replace('.', 'p')}"; d = f"{k}_{p}{str(default).replace('.', 'p')}"
            M[f"{tag}_ratio_l32"] = M[f"{tag}_l32_mean"] / M[f"{d}_l32_mean"]
            M[f"{tag}_ratio_fss"] = M[f"{tag}_fss_mean"] / M[f"{d}_fss_mean"]
print(json.dumps(M, indent=1))
json.dump(M, open(sys.argv[1], "w"))
