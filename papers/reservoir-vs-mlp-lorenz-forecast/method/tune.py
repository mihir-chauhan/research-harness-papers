"""Validation grid for one (system, task, stage) on a separate trajectory (seed 100, 10 initial conditions, n_train=5000).
Selection criterion: mean valid prediction time. Usage: python method/tune.py <task> <system> <stage> [<steps>] [--out FILE]
(<steps> restricts stage B to one optimiser-step value so that every tuning run stays under the 6-minute limit.)
Stages: esn/A is the full ESN grid. For mlp and gru, stage A is the model grid at the default optimiser setting and stage B
the optimiser grid (steps x learning rate) at the stage-A optimum, read from experiments/tuning_<task>_<system>_A.json.
Writes experiments/tuning_<task>_<system>_<stage>[<steps>].json (every grid cell with its validation VPT and fit time)."""
import itertools, json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, lib

task, sysn, stage = sys.argv[1], sys.argv[2], sys.argv[3]
GRIDS = {
    ("esn", "A"): dict(rho=[0.4, 0.9, 1.4], sigma=[0.1, 0.3, 1.0], ridge=[1e-8, 1e-6, 1e-4]),
    ("mlp", "A"): dict(delays=[1, 2, 4], noise=[0.0, 0.01, 0.03]),
    ("mlp", "B"): dict(steps=[4000, 8000, 16000], lr=[1e-3, 2e-3, 5e-3]),
    ("gru", "A"): dict(noise=[0.0, 0.01, 0.03, 0.1, 0.3]),
    ("gru", "B"): dict(steps=[3000, 6000], lr=[1e-3, 3e-3, 1e-2]),
}
base = {}
sub = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4].isdigit() else ""
if stage == "B":
    if sub: GRIDS[(sysn, stage)]["steps"] = [int(sub)]
    base = json.load(open(f"experiments/tuning_{task}_{sysn}_A.json"))["best"]["cfg"]
print("CONFIG", json.dumps(dict(task=task, system=sysn, stage=stage, base=base, grid=GRIDS[(sysn, stage)])), flush=True)
d = lib.make_data(task, 100, 5000)
d["test"] = d["test"][:10]
g = GRIDS[(sysn, stage)]; rows = []
for vals in itertools.product(*g.values()):
    cfg = dict(base, **dict(zip(g.keys(), vals))); t = time.time()
    m = lib.build(sysn, lib.DIM[task], 100, **cfg).fit(d["train"]); v = float(lib.valid_time(m, d, task).mean())
    rows.append(dict(cfg=cfg, val_vpt=v, fit_seconds=round(time.time() - t, 2))); print("GRID", json.dumps(rows[-1]), flush=True)
best = max(rows, key=lambda r: r["val_vpt"])
json.dump(dict(best=best, grid=rows), open(f"experiments/tuning_{task}_{sysn}_{stage}{sub}.json", "w"), indent=1)
res = dict(val_vpt_best=best["val_vpt"], n_configs=len(rows), **{f"best_{k}": v for k, v in best["cfg"].items()})
print("METRICS", json.dumps(res), flush=True)
out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.environ.get("RH_METRICS_FILE")
if out: json.dump(res, open(out, "w"))
