"""Benettin estimate of the largest Lyapunov exponent. Usage: python method/lyap.py <task> [--out FILE]
Settings: RK4 step h=0.005, total time T=4000 after 200 burn-in samples, separation eps=1e-8 renormalised every 20 steps,
seed 0. The printed values, rounded to 3 decimals, are the constants lib.LYAP."""
import json, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import lib

def lyap(task, T=4000.0, h=0.005, seed=0):
    f = lib.FUN[task]; rng = np.random.default_rng(seed)
    x = lib.integrate(task, lib.init_state(task, rng), 1, burn=200)[0]
    D = len(x); v = rng.normal(size=D); v /= np.linalg.norm(v); eps = 1e-8; s = 0.0
    n = int(T / h); every = 20; xp = x + eps * v
    for i in range(n):
        x = lib.rk4(f, x, h); xp = lib.rk4(f, xp, h)
        if (i + 1) % every == 0:
            d = xp - x; nd = np.linalg.norm(d); s += np.log(nd / eps); xp = x + eps * d / nd
    return s / (n * h)

if __name__ == "__main__":
    task = sys.argv[1]
    print("CONFIG", json.dumps(dict(task=task, T=4000.0, h=0.005, eps=1e-8, renorm_every=20, seed=0)), flush=True)
    lam = float(lyap(task)); res = dict(lyapunov=lam, lyapunov_time=1.0 / lam)
    print("METRICS", json.dumps(res), flush=True)
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.environ.get("RH_METRICS_FILE")
    if out: json.dump(res, open(out, "w"))
