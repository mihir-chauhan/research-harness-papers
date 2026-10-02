"""Step-size pre-check of the full two-scale model: python experiments/precheck_dt.py --task F20_c10 --seed 0 --out m.json

Runs the truth from the same initial conditions with the RK4 step used everywhere (l96.DT_TRUTH) and with half of it,
and compares the mean and variance of X pooled over chains, sectors and a 20-unit window after a 20-unit spin-up.
The trajectories themselves diverge (chaos), so only the statistics are compared.
"""
import argparse, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "method"))
import l96

ap = argparse.ArgumentParser()
ap.add_argument("--task", default="F20_c10"); ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--chains", type=int, default=40); ap.add_argument("--t_len", type=float, default=20.0)
ap.add_argument("--out", required=True)
a = ap.parse_args(); t0 = time.time()
print("config", json.dumps(vars(a)), flush=True)
F, c = {"F20_c10": (20.0, 10.0), "F20_c4": (20.0, 4.0)}[a.task]
m = {}
for tag, dt in [("dt", l96.DT_TRUTH), ("half", l96.DT_TRUTH / 2)]:
    X, _ = l96.simulate_truth(7000 + a.seed, a.chains, 20, a.t_len, F, c, dt=dt)
    m[f"mean_{tag}"] = float(X.mean()); m[f"var_{tag}"] = float(X.var())
m["mean_rel_diff"] = abs(m["mean_dt"] / m["mean_half"] - 1)
m["var_rel_diff"] = abs(m["var_dt"] / m["var_half"] - 1)
m["runtime_s"] = time.time() - t0
json.dump(m, open(a.out, "w")); print("metrics", json.dumps(m), flush=True)
