"""Derived analysis over logged runs: per-data-fraction means (sweep + full-data reference) -> metrics json + csv."""
import json, os, sys, numpy as np
rows = [json.loads(l) for l in open("results/runs.jsonl")]
def get(group, pred):
    return [r for r in rows if r.get("group") == group and r.get("status", "ok") == "ok" and pred(r)]
by = {}
for fr in (0.1, 0.25, 0.5):
    by[fr] = get("sweep_data_frac", lambda r, fr=fr: r["config"].get("data_frac") == fr)
by[1.0] = get("abl_components", lambda r: r["name"] == "Conditional AR designer")
out = {}; csv = ["data_frac,seed,succ_k1,succ_k100,train_pairs,test_nll"]
for fr, rs in by.items():
    tag = str(fr).replace(".", "p")
    for m in ("succ_k1", "succ_k100", "train_pairs", "test_nll"):
        v = np.array([r["metrics"][m] for r in rs], float)
        out[f"frac{tag}_{m}_mean"] = float(v.mean()); out[f"frac{tag}_{m}_std"] = float(v.std(ddof=1))
    out[f"frac{tag}_n"] = len(rs)
    for r in rs:
        csv.append(",".join(map(str, [fr, r["seed"]] + [r["metrics"][m] for m in ("succ_k1", "succ_k100", "train_pairs", "test_nll")])))
os.makedirs("results/raw", exist_ok=True)
open("results/raw/frac_sweep.csv", "w").write("\n".join(csv) + "\n")
print(json.dumps(out))
json.dump(out, open(os.environ["RH_METRICS_FILE"], "w"))
