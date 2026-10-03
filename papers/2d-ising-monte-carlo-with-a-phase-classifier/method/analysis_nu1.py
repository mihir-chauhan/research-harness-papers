"""Ablation of the collapse: Tc fitted with the exponent fixed to the exact nu = 1 (curves saved by the main runs)."""
import argparse, json, re, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from estimators import collapse
from sampler import TC_EXACT

ap = argparse.ArgumentParser()
ap.add_argument("--system", required=True); ap.add_argument("--seed", type=int, required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
print("CONFIG", vars(a))
f = f"results/raw/main_{re.sub('[^A-Za-z0-9]', '_', a.system)}_s{a.seed}_curves.npz"
z = np.load(f)
T = z["T"]
curves = {L: z[f"L{L}"] for L in (16, 24, 32)}
tc, nu, cost = collapse(T, curves, nu_grid=np.array([1.0]))
M = {"tc_error_fss": abs(tc - TC_EXACT), "tc_bias_fss": tc - TC_EXACT, "collapse_cost": cost}
print("METRICS", json.dumps(M))
json.dump(M, open(a.out, "w"))
