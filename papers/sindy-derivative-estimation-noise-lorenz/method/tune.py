"""Hyperparameter selection on independent tuning trajectories (seeds 1000-1004), per system and noise level.
Selection rule: highest exact-support rate, then lowest median coefficient error, then the largest threshold.
A "tie" in this script therefore means equal support rate AND equal median coefficient error on the five tuning
trajectories; it does not check that the tied configurations return the same models. tie_check.py does that check:
in 17 of the 19 cells with a tie the tied configurations return identical models on all five trajectories; for FD at
5 % noise (thresholds 0.05, 0.1) and spline at 10 % (0.4, 0.6) they do not (results/logs/*tune_diag*.log).
The first version of this script resolved ties by grid order, i.e. by the smallest threshold; its output is kept in
tuned_v1.json and results/logs/tune_v1.log. Run from method/: python tune.py > ../results/logs/tune.log"""
import json, itertools
import numpy as np
from sindy import simulate, problem, stlsq, metrics

LEVELS = ["0", "0.5", "1", "2", "5", "10"]
THR = [0.05, 0.1, 0.2, 0.4, 0.6]
GRIDS = {
    "fd": {},
    "sg": {"window": [11, 21, 41, 81, 161], "order": [3]},
    "spline": {"lam": [1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3]},
    "tv": {"alpha": [1e-5, 1e-4, 1e-3, 1e-2, 1e-1]},
    "weak": {"width": [0.3, 0.6, 1.0, 1.5, 2.5]},
}
TUNE_SEEDS = range(1000, 1005)
out = {}
for system, grid in GRIDS.items():
    out[system] = {}
    keys = list(grid)
    for lv in LEVELS:
        data = [simulate(s, float(lv) / 100) for s in TUNE_SEEDS]
        cands = []
        for vals in itertools.product(*[grid[k] for k in keys]):
            hp = dict(zip(keys, vals))
            probs = [problem(system, t, noisy, hp) for (t, _, noisy) in data]
            for thr in THR:
                r = np.array([[metrics(stlsq(Th, dX, thr), Th, dX)[k] for k in ("support_exact", "coef_err")]
                              for Th, dX in probs])
                # score: support rate, then median error, then the larger threshold (tie = equal rate and equal median)
                cands.append(((r[:, 0].mean(), -np.median(r[:, 1]), thr), {**hp, "thr": thr}))
        best = max(cands, key=lambda c: c[0])
        out[system][lv] = best[1]
        # the log label "exact_ties_thr" is kept so that the script still reproduces results/logs/tune.log; it lists
        # the thresholds with equal support rate and equal median error, which need not give identical models
        ties = [c[1]["thr"] for c in cands if c[0][:2] == best[0][:2]]
        print(system, lv, best[1], "tune_support=%.2f tune_med_err=%.4f" % (best[0][0], -best[0][1]),
              "exact_ties_thr=%s" % ties, flush=True)
        # per-threshold scores at the selected smoothing parameter (support rate / median error)
        row = [c for c in cands if all(c[1][k] == best[1][k] for k in keys)]
        print("   by_thr", " ".join("%g:%.2f/%.4f" % (c[1]["thr"], c[0][0], -c[0][1]) for c in row), flush=True)
json.dump(out, open("tuned.json", "w"), indent=1)
