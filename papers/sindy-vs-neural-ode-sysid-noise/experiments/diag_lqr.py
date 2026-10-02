"""Diagnostic for runs whose lqr_cost equals the cap (1000): refits the same model with method/run.py (same seed, data,
settings) and reports whether the Riccati solve succeeded and how many of the 10 LQR episodes hit the cost cap.
Usage: python experiments/diag_lqr.py --system node --task pendulum --seed 0 --noise 0.05 --ntrain 200 --out f.json
"""
import argparse, json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "method"))
import run as R

ap = argparse.ArgumentParser()
ap.add_argument("--system", required=True); ap.add_argument("--task", required=True)
ap.add_argument("--seed", type=int, default=0); ap.add_argument("--noise", type=float, default=0.05)
ap.add_argument("--ntrain", type=int, default=1000); ap.add_argument("--out", required=True)
a = ap.parse_args()
print("config", vars(a))
sysd = R.SYS[a.task]
rng = np.random.RandomState(1000 * a.seed + 7)                 # same data stream as method/run.py
X, U = R.gen_data(sysd, a.ntrain // R.L, rng)
Xn = X + a.noise * X.reshape(-1, 2).std(0) * rng.standard_normal(X.shape)
if a.system == "node": f, _, _ = R.fit_node(Xn, U, a.seed)
else: f, _, _ = R.fit_sindy(Xn, U, a.task, 0.05, True, False)
Ad, Bd = R.linearise(f)
K, P = R.lqr(Ad, Bd, sysd["Q"], sysd["R"])
At, Bt = R.linearise(lambda x, u: sysd["f"](x, np.asarray(u)))
out = {"riccati_ok": float(K is not None)}
if K is not None:
    ics = np.random.RandomState(555 + a.seed).uniform(-sysd["cl_ic"], sysd["cl_ic"], (10, 2))
    r = [R.episode_cost(sysd, lambda x: -(K @ x)[0], x0, 80) for x0 in ics]
    out["lqr_cost"] = float(np.mean([c for c, _ in r]))
    out["n_capped"] = float(sum(c >= R.JCAP for c, _ in r))
    # spectral radius of the true linearised closed loop under the gain designed on the identified model
    out["true_cl_radius"] = float(np.abs(np.linalg.eigvals(At - Bt @ K)).max())
    out["model_B2"] = float(Bd[1, 0]); out["true_B2"] = float(Bt[1, 0])
json.dump(out, open(a.out, "w")); print(out)
