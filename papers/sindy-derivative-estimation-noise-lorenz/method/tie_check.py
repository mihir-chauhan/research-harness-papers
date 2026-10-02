"""Diagnostic of the tuner's ties (tuning seeds 1000-1004 only; no test data).
tune.py calls two configurations tied when they have the same exact-support rate and the same median coefficient
error on the five tuning trajectories. This script repeats the grid of tune.py and reports, for every
system x noise level, the configurations tied with the selected one: (a) on how many of the five trajectories each
tied configuration returns a model different from the selected one, (b) its mean coefficient error, and (c) which
configuration a mean-error tie-break (largest threshold only if the mean is equal too) would select.
Usage (project root): python method/tie_check.py --task lorenz_n<pct> --out <flat metrics json>   (one noise level, all
five systems); the per-cell records go to results/raw/tie_check_cells_n<pct>.json and the printed lines are the log."""
import argparse, json, itertools, os, time
import numpy as np
from sindy import simulate, problem, stlsq, metrics

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--task", required=True)           # lorenz_n<percent>: the noise level whose five cells are checked
ap.add_argument("--out", required=True)
a = ap.parse_args()
t0 = time.time()
LEVELS = [a.task.split("_n")[1]]

THR = [0.05, 0.1, 0.2, 0.4, 0.6]
GRIDS = {   # same grids as tune.py
    "fd": {},
    "sg": {"window": [11, 21, 41, 81, 161], "order": [3]},
    "spline": {"lam": [1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3]},
    "tv": {"alpha": [1e-5, 1e-4, 1e-3, 1e-2, 1e-1]},
    "weak": {"width": [0.3, 0.6, 1.0, 1.5, 2.5]},
}
TUNE_SEEDS = range(1000, 1005)
TUNED = json.load(open(os.path.join(HERE, "tuned.json")))
print("config", json.dumps({"task": a.task, "levels": LEVELS, "thr": THR, "grids": GRIDS, "tune_seeds": list(TUNE_SEEDS)}))
out = []
for system, grid in GRIDS.items():
    keys = list(grid)
    for lv in LEVELS:
        data = [simulate(s, float(lv) / 100) for s in TUNE_SEEDS]
        cands = []
        for vals in itertools.product(*[grid[k] for k in keys]):
            hp = dict(zip(keys, vals))
            probs = [problem(system, t, noisy, hp) for (t, _, noisy) in data]
            for thr in THR:
                Xis = [stlsq(Th, dX, thr) for Th, dX in probs]
                r = np.array([[metrics(Xi, Th, dX)[k] for k in ("support_exact", "coef_err")]
                              for Xi, (Th, dX) in zip(Xis, probs)])
                cands.append({"score": (r[:, 0].mean(), -np.median(r[:, 1]), thr), "cfg": {**hp, "thr": thr},
                              "Xi": Xis, "err": r[:, 1]})
        best = max(cands, key=lambda c: c["score"])
        assert best["cfg"] == TUNED[system][lv], (system, lv, best["cfg"])     # reproduces tune.py
        tied = [c for c in cands if c["score"][:2] == best["score"][:2]]
        same_hp = all(all(c["cfg"][k] == best["cfg"][k] for k in keys) for c in tied)
        # (a) trajectories on which a tied configuration returns a model different from the selected one
        ndiff = [sum(not np.array_equal(a, b) for a, b in zip(c["Xi"], best["Xi"])) for c in tied]
        # (c) mean-error tie-break
        alt = max(tied, key=lambda c: (-c["err"].mean(), c["cfg"]["thr"]))
        rec = {"system": system, "level": lv, "selected_thr": best["cfg"]["thr"], "n_tied": len(tied),
               "tied_thr": [c["cfg"]["thr"] for c in tied], "tied_same_smoothing": bool(same_hp),
               "n_traj_differ": ndiff, "identical_models": bool(max(ndiff) == 0),
               "tied_mean_err": [float(c["err"].mean()) for c in tied],
               "mean_rule_thr": alt["cfg"]["thr"], "mean_rule_same_cfg": bool(alt["cfg"] == best["cfg"])}
        out.append(rec)
        print(system, lv, "selected", best["cfg"], "tied_thr=%s" % rec["tied_thr"], "same_smoothing=%s" % same_hp,
              "traj_differ=%s" % ndiff, "identical=%s" % rec["identical_models"],
              "mean_err=[%s]" % " ".join("%.4f" % e for e in rec["tied_mean_err"]),
              "mean_rule_thr=%g" % rec["mean_rule_thr"], flush=True)
        for c, nd in zip(tied, ndiff):
            if nd:
                print("   thr %g vs selected %g per-trajectory coef_err:" % (c["cfg"]["thr"], best["cfg"]["thr"]),
                      " ".join("%.4f/%.4f" % (a, b) for a, b in zip(c["err"], best["err"])), flush=True)
multi = [r for r in out if r["n_tied"] > 1]
differ = [r for r in multi if not r["identical_models"]]
# flat metrics: counts over the five cells of the level, and for each tie cell with differing models the number of trajectories
# (of 5) on which a tied threshold differs from the selected one and the mean tuning error of each tied threshold
m = {"cells": len(out), "cells_with_tie": len(multi),
     "tie_cells_identical_models": sum(r["identical_models"] for r in multi),
     "tie_cells_differing_models": len(differ),
     "tie_cells_other_smoothing": sum(not r["tied_same_smoothing"] for r in multi),
     "mean_rule_changes": sum(not r["mean_rule_same_cfg"] for r in out)}
for r in differ:
    key = r["system"]
    m[f"{key}_traj_differ"] = max(r["n_traj_differ"])
    for thr, e in zip(r["tied_thr"], r["tied_mean_err"]):
        m[f"{key}_mean_err_t{thr:g}"] = e
m["runtime_s"] = time.time() - t0
print("metrics", json.dumps(m))
json.dump(m, open(a.out, "w"))
json.dump({"summary": m, "cells": out}, open(os.path.join(HERE, "..", "results", "raw", f"tie_check_cells_n{LEVELS[0]}.json"), "w"), indent=1)
