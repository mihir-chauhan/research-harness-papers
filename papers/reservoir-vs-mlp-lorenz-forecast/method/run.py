"""Entrypoint: python method/run.py --system esn|mlp|gru|truth --task lorenz63|lorenz96 --seed S [--n_train N] [--config JSON] --out FILE
Hyperparameters come from method/tuned.json (chosen on a separate validation trajectory, seed 100); --config overrides."""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, torch
import lib

ap = argparse.ArgumentParser()
ap.add_argument("--system", required=True); ap.add_argument("--task", required=True)
ap.add_argument("--seed", type=int, default=0); ap.add_argument("--n_train", type=int, default=5000)
ap.add_argument("--config", default="{}"); ap.add_argument("--out", required=True)
ap.add_argument("--no_tuned", action="store_true")
a = ap.parse_args()

cfg = {}
tp = os.path.join(os.path.dirname(__file__), "tuned.json")
if os.path.exists(tp) and not a.no_tuned:
    cfg.update(json.load(open(tp)).get(f"{a.system}/{a.task}", {}))
cfg.update(json.loads(a.config))
print("CONFIG", json.dumps(dict(system=a.system, task=a.task, seed=a.seed, n_train=a.n_train, hp=cfg)), flush=True)

np.random.seed(a.seed); torch.manual_seed(a.seed)
d = lib.make_data(a.task, a.seed, a.n_train)
t0 = time.time()
m = lib.build(a.system, lib.DIM[a.task], a.seed, **cfg)
if a.system == "truth": m.task, m.mu, m.sd = a.task, d["mu"], d["sd"]
m.fit(d["train"])
t_fit = time.time() - t0
v = lib.valid_time(m, d, a.task)
c = lib.climate(m, d, a.task)
res = dict(vpt=float(v.mean()), vpt_median=float(np.median(v)), vpt_min=float(v.min()), **c, fit_seconds=t_fit)
print("METRICS", json.dumps(res), flush=True)
json.dump(res, open(a.out, "w"))
