"""Paired tests over seeds from the main group of results/runs.jsonl (two-sided Wilcoxon signed-rank).
Writes a flat JSON of statistics; run through `rh run` so that the numbers are logged."""
import json, sys
import numpy as np
from scipy.stats import wilcoxon

out = sys.argv[1]
rows = [json.loads(l) for l in open("results/runs.jsonl")]
allrows = [r for r in rows if r["status"] == "ok"]
rows = [r for r in allrows if r["group"] == "main"]
V = {}
for r in rows:
    V.setdefault(r["name"], {})[r["seed"]] = r["metrics"]
N1 = {}  # collapse with nu fixed to 1 (abl_nu_fixed), same curves
for r in allrows:
    if r["group"] == "abl_nu_fixed":
        N1.setdefault(r["name"], {})[r["seed"]] = r["metrics"]
seeds = sorted(set.intersection(*[set(v) for v in V.values()]))
print("seeds", seeds, "systems", sorted(V))


def get(sys_, m):
    return np.array([V[sys_][s][m] for s in seeds])


def pair(tag, a, ma, b, mb):
    x, y = get(a, ma), get(b, mb)
    d = x - y
    res = {f"{tag}_meandiff": float(d.mean()), f"{tag}_p": float(wilcoxon(x, y).pvalue) if np.any(d != 0) else 1.0,
           f"{tag}_wins": float((d < 0).sum())}  # number of seeds where the first is lower (better)
    return res


M = {"n_paired_seeds": float(len(seeds))}
for s_, k in (("CNN", "cnn"), ("MLP", "mlp")):
    M.update(pair(f"h1_{k}_vs_pca_l32", s_, "tc_error_l32", "PCA", "tc_error_l32"))
    M.update(pair(f"h2_{k}_fss_vs_l32", s_, "tc_error_fss", s_, "tc_error_l32"))
for s_, k in (("PCA", "pca"), ("Confusion (MLP)", "conf"), ("MLP", "mlp"), ("Binder/chi (reference)", "binder")):
    M.update(pair(f"h4_{k}_vs_cnn_fss", s_, "tc_error_fss", "CNN", "tc_error_fss"))
M.update(pair("pca_fss_vs_l32", "PCA", "tc_error_fss", "PCA", "tc_error_l32"))
M.update(pair("binder_fss_vs_l32", "Binder/chi (reference)", "tc_error_fss", "Binder/chi (reference)", "tc_error_l32"))
for L in (16, 24, 32):  # learning by confusion versus the two supervised nets, single-size read-out
    M.update(pair(f"conf_vs_cnn_l{L}", "Confusion (MLP)", f"tc_error_l{L}", "CNN", f"tc_error_l{L}"))
    M.update(pair(f"conf_vs_mlp_l{L}", "Confusion (MLP)", f"tc_error_l{L}", "MLP", f"tc_error_l{L}"))
M.update(pair("cnn_vs_mlp_l32", "CNN", "tc_error_l32", "MLP", "tc_error_l32"))
M.update(pair("cnn_vs_mlp_fss", "CNN", "tc_error_fss", "MLP", "tc_error_fss"))
# nu fixed to 1 versus free exponent, paired over seeds (first minus second; negative = fixing helps)
for s_, k in (("CNN", "cnn"), ("MLP", "mlp"), ("Binder/chi (reference)", "binder"), ("PCA", "pca"), ("Confusion (MLP)", "conf")):
    x = np.array([N1[s_][s]["tc_error_fss"] for s in seeds]); y = get(s_, "tc_error_fss"); d = x - y
    M[f"nu1_{k}_meandiff"] = float(d.mean()); M[f"nu1_{k}_p"] = float(wilcoxon(x, y).pvalue) if np.any(d != 0) else 1.0
    M[f"nu1_{k}_wins"] = float((d < 0).sum())
# bias of the single-size crossing: signed mean and per-size
for s_, k in (("CNN", "cnn"), ("MLP", "mlp")):
    for L in (16, 24, 32):
        M[f"{k}_bias_l{L}_mean"] = float(get(s_, f"tc_bias_l{L}").mean())
    M[f"{k}_bias_fss_mean"] = float(get(s_, "tc_bias_fss").mean())
boot = np.random.default_rng(0).choice(get("CNN", "tc_error_fss"), (2000, len(seeds))).mean(1)
M["cnn_fss_error_ci_lo"], M["cnn_fss_error_ci_hi"] = [float(v) for v in np.percentile(boot, [2.5, 97.5])]
# finite-size drift of the CNN crossing (signed bias L=16 minus L=32)
M["cnn_bias_l16_minus_l32"] = M["cnn_bias_l16_mean"] - M["cnn_bias_l32_mean"]
print(json.dumps(M, indent=1))
json.dump(M, open(out, "w"))
