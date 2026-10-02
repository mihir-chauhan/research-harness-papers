"""Sanity check for the E <= E_CAP truncation: distribution of the LJ energy of the two configuration
kinds *before* truncation, with the generator of method/run.py.

Usage: python method/energy_tail.py --seed S --m 4000 --out file.json
"""
import argparse, json
import numpy as np
import run as R

ap = argparse.ArgumentParser()
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--m", type=int, default=4000)
ap.add_argument("--out", required=True)
a = ap.parse_args()
print("config:", json.dumps(vars(a)), flush=True)
lib = R.minima_library()
rng = np.random.default_rng(5000 + a.seed)
E = {0: [], 1: []}
for i in range(a.m):
    n = int(rng.integers(R.NMIN, R.NMAX + 1))
    if i % 2 == 0:
        base = lib[n][int(rng.integers(len(lib[n])))]
        x = base @ R.random_rotation(rng).T + rng.uniform(0.02, 0.12) * rng.normal(size=(n, 3))
    else:
        x = R.random_cluster(n, rng)
    E[i % 2].append(R.lj_energy(x))
p, r = np.array(E[0]), np.array(E[1])
out = {"n_samples": a.m,
       "perturbed_max_energy": float(p.max()), "perturbed_q99_energy": float(np.quantile(p, 0.99)),
       "perturbed_frac_above_cap": float((p > R.E_CAP).mean()),
       "random_max_energy": float(r.max()), "random_q99_energy": float(np.quantile(r, 0.99)),
       "random_frac_above_cap": float((r > R.E_CAP).mean()),
       "lowest_minimum_energy_n13": float(min(R.lj_energy(x) for x in lib[13]))}
out.update({f"n_minima_size{n}": len(v) for n, v in lib.items()})  # size of the minima library per cluster size
print(json.dumps(out, indent=1))
json.dump(out, open(a.out, "w"))
