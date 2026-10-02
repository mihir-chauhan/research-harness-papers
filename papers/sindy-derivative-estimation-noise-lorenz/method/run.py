"""Entry point: one (system, noise level, seed) trial. Writes a flat JSON of metrics."""
import argparse, json, time, os
from sindy import simulate, fit, metrics, problem, stlsq

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--system", required=True, choices=["fd", "sg", "spline", "tv", "weak"])
ap.add_argument("--task", required=True)           # lorenz_n<percent>, e.g. lorenz_n2
ap.add_argument("--seed", type=int, required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--override", default="{}")        # JSON overriding tuned hyperparameters (ablations/sweeps)
ap.add_argument("--thr-grid", default="")         # diagnostic: comma-separated thresholds, all on one regression problem
a = ap.parse_args()

level_pct = a.task.split("_n")[1]
tuned = json.load(open(os.path.join(HERE, "tuned.json")))[a.system][level_pct]
cfg = {**tuned, **json.loads(a.override)}
if a.thr_grid:
    cfg["thr"] = a.thr_grid                         # the tuned threshold is replaced by the whole grid
print("config", json.dumps({"system": a.system, "task": a.task, "seed": a.seed, **cfg}))
t0 = time.time()
t, clean, noisy = simulate(a.seed, float(level_pct) / 100)
if a.thr_grid:
    # same regression problem as the main run (tuned smoothing parameter); only the STLSQ threshold varies
    Th, dX = problem(a.system, t, noisy, cfg)
    m = {}
    for thr in a.thr_grid.split(","):
        r = metrics(stlsq(Th, dX, float(thr)), Th, dX)
        m.update({f"{k}_t{thr}": r[k] for k in ("support_exact", "coef_err", "false_pos", "false_neg")})
else:
    Xi, Th, dX = fit(a.system, t, noisy, cfg)
    m = metrics(Xi, Th, dX)
m["runtime_s"] = time.time() - t0
print("metrics", json.dumps(m))
json.dump(m, open(a.out, "w"))
