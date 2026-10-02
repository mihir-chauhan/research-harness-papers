"""Fraction of OP lever agents whose initial P(lever 9) exceeds 0.11 (the OP basin threshold), vs trained frac_special.
Reproduces the generator stream of method/run.py (init is the first draw)."""
import sys, json, torch
sys.path.insert(0, "method")
seed, sd, out = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
gen = torch.Generator().manual_seed(1000 * seed + 17)
p = torch.softmax(torch.randn(20, 10, generator=gen) * sd, -1)[:, 9]
res = {"frac_init_above": float((p > 0.11).float().mean())}
print("config:", seed, sd); print("metrics:", json.dumps(res)); json.dump(res, open(out, "w"))
