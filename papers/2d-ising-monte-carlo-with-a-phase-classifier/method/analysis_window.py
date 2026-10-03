"""Sensitivity of the collapse to its window |T-Tc| <= w (exponent free), on the curves saved by the main runs."""
import argparse, json, re, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from estimators import collapse
from sampler import TC_EXACT

ap = argparse.ArgumentParser()
ap.add_argument("--system", required=True); ap.add_argument("--seed", type=int, required=True)
ap.add_argument("--window", type=float, required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
print("CONFIG", vars(a))
z = np.load(f"results/raw/main_{re.sub('[^A-Za-z0-9]', '_', a.system)}_s{a.seed}_curves.npz")
tc, nu, cost = collapse(z["T"], {L: z[f"L{L}"] for L in (16, 24, 32)}, window=a.window)
M = {"tc_error_fss": abs(tc - TC_EXACT), "tc_bias_fss": tc - TC_EXACT, "nu_fss": nu, "nu_error_fss": abs(nu - 1.0), "collapse_cost": cost}
print("METRICS", json.dumps(M))
json.dump(M, open(a.out, "w"))
