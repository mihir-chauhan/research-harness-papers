"""Descriptive statistics of the hourly-binned cohort (no model)."""
import json, sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
X, M, S, y, icu, names = data.load()
r = {"obs_density": float(M.mean()), "mortality": float(y.mean()), "deaths": int(y.sum()), "n_stays": int(len(y)),
     "obs_per_stay_mean": float(M.sum((1, 2)).mean()), "obs_per_stay_median": float(np.median(M.sum((1, 2)))),
     "height_missing": float(np.isnan(S[:, 2]).mean()), "weight_missing": float(np.isnan(S[:, 3]).mean())}
for c in (1, 2, 3, 4): r[f"icu{c}_n"] = int((icu == c).sum()); r[f"icu{c}_mortality"] = float(y[icu == c].mean())
# informative missingness: AUROC of the total observation count alone (no values)
from sklearn.metrics import roc_auc_score
r["auroc_total_count_only"] = float(roc_auc_score(y, M.sum((1, 2))))
r["frac_vars_ever_observed_mean"] = float((M.sum(1) > 0).mean())
json.dump(r, open(sys.argv[1], "w")); print(json.dumps(r, indent=1))
