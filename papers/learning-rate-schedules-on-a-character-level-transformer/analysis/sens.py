"""Derived LR-sensitivity metrics for one system and seed, from results/runs.jsonl (group main: three main rates plus the two extra rates 3e-4, 3e-2)."""
import argparse, json
ap = argparse.ArgumentParser()
ap.add_argument("--system", required=True); ap.add_argument("--seed", type=int, required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
main, sweep = {}, {}
for line in open("results/runs.jsonl"):
    r = json.loads(line)
    if r["name"] != a.system or r["seed"] != a.seed or r["status"] != "ok" or r["task"] == "sens": continue
    lr = r["config"]["lr"]
    if r["group"] != "main": continue
    if lr in (1e-3, 3e-3, 1e-2): main[lr] = r["metrics"]["val_loss"]
    else: sweep[lr] = r["metrics"]["val_loss"]
allv = {**main, **sweep}
assert len(main) == 3 and len(allv) == 5, (main, sweep)
v3 = list(main.values()); v5 = list(allv.values())
# width of the LR range within 0.05 nats of the best (log10 units, grid points only)
best5 = min(v5)
out = {"sens3": max(v3) - min(v3), "sens5": max(v5) - best5, "best3": min(v3), "best5": best5,
       "n_lr_within_0p05": float(sum(v <= best5 + 0.05 for v in v5)),
       "best_lr_log10": float(__import__("math").log10(min(allv, key=allv.get)))}
print("sens", a.system, a.seed, json.dumps(out))
json.dump(out, open(a.out, "w"))
