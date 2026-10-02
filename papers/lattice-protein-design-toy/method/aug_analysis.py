"""Paired augmentation analysis: aug vs no-aug (60 epochs) and vs step-matched no-aug (120 epochs), per data fraction."""
import json, os, numpy as np
from scipy import stats
rows = [json.loads(l) for l in open("results/runs.jsonl")]
def get(group, pred):
    return {r["seed"]: r["metrics"] for r in rows if r.get("group") == group and r.get("status", "ok") == "ok" and pred(r)}
out = {}
for fr in (0.1, 0.25, 0.5, 1.0):
    tag = str(fr).replace(".", "p")
    if fr < 1.0:
        a = get("abl_aug_frac", lambda r: r["name"] == "Conditional AR designer" and r["config"]["data_frac"] == fr)
        n0 = get("abl_aug_frac", lambda r: r["name"] == "No reversal augmentation" and r["config"]["data_frac"] == fr)
    else:  # full data: reuse the main ablation rows (distinct-pair counts are not logged there)
        a = get("abl_components", lambda r: r["name"] == "Conditional AR designer")
        n0 = get("abl_components", lambda r: r["name"] == "No reversal augmentation")
    n1 = get("abl_aug_steps", lambda r: r["config"]["data_frac"] == fr)
    seeds = sorted(set(a) & set(n0) & set(n1)); assert len(seeds) == 5, (fr, seeds)
    for name, base in (("noaug60", n0), ("noaug120", n1)):
        for m in ("succ_k1", "succ_k100", "test_nll"):
            d = np.array([a[s][m] - base[s][m] for s in seeds])
            out[f"f{tag}_{name}_{m}_delta"] = float(d.mean())
            out[f"f{tag}_{name}_{m}_p"] = float(stats.ttest_rel([a[s][m] for s in seeds], [base[s][m] for s in seeds]).pvalue)
    for m in ("succ_k1", "succ_k100"):
        out[f"f{tag}_noaug120_{m}_mean"] = float(np.mean([n1[s][m] for s in seeds]))
    if fr < 1.0:
        out[f"f{tag}_aug_train_pairs"] = float(np.mean([a[s]["train_pairs"] for s in seeds]))
        out[f"f{tag}_aug_distinct_pairs"] = float(np.mean([a[s]["distinct_pairs"] for s in seeds]))
        out[f"f{tag}_noaug_train_pairs"] = float(np.mean([n0[s]["train_pairs"] for s in seeds]))
    else:
        out[f"f{tag}_aug_distinct_pairs"] = float(np.mean([n1[s]["distinct_pairs"] for s in seeds]))  # = distinct pairs with augmentation: identical data to noaug
        out[f"f{tag}_aug_train_pairs"] = float(np.mean([a[s]["train_pairs"] for s in seeds]))
        out[f"f{tag}_noaug_train_pairs"] = float(np.mean([n1[s]["train_pairs"] for s in seeds]))
print(json.dumps(out, indent=1))
json.dump(out, open(os.environ["RH_METRICS_FILE"], "w"))
