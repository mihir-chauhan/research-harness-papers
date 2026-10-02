"""Best DEV selection score (succ_k100 + succ_k1000) of the original and the extended SA grids, per objective."""
import json, os
rows = [json.loads(l) for l in open("results/runs.jsonl")]
out = {}
for obj, g0, g1 in (("bin", "tune_sa", "tune2_sa"), ("log", "tune_sa_log", "tune2_sa_log")):
    for tag, g in (("orig", g0), ("ext", g1)):
        rs = [r for r in rows if r["group"] == g and r.get("status", "ok") == "ok"]
        sc = [(r["metrics"]["succ_k100"] + r["metrics"]["succ_k1000"], r["config"]) for r in rs]
        b = max(sc, key=lambda x: x[0])
        out[f"{obj}_{tag}_n"] = len(rs); out[f"{obj}_{tag}_best_score"] = b[0]
        out[f"{obj}_{tag}_best_T0"] = b[1]["T0"]; out[f"{obj}_{tag}_best_T1"] = b[1]["T1"]
print(json.dumps(out)); json.dump(out, open(os.environ["RH_METRICS_FILE"], "w"))
