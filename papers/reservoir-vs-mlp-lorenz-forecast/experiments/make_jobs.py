"""Writes experiments/jobs_main.json: every run of the study, split into two lanes of similar estimated duration.
Groups: main (systems, the true-system reference and the component ablations, seeds 0-4, n_train=5000);
sweep_rho, sweep_size (ESN, seeds 0-2); sweep_ntrain (all systems, seeds 0-2); sweep_steps (MLP, GRU optimiser steps, seeds 0-2).
The tuned default point of every sweep is the group-main run of the same seed and is not run again."""
import json
T = json.load(open("method/tuned.json"))
TASKS = ["lorenz63", "lorenz96"]; S5 = [0, 1, 2, 3, 4]; S3 = [0, 1, 2]
NAME = {"esn": "ESN", "mlp": "MLP delay", "gru": "GRU", "truth": "True system"}
jobs = []


def cost(sysn, task, cfg):
    hp = dict(T.get(f"{sysn}/{task}", {}), **cfg)
    if sysn == "mlp": return 6 + hp["steps"] * 0.0027
    if sysn == "gru": return 8 + hp["steps"] * 0.011
    if sysn == "esn": return 6 + (hp.get("size", 500) / 500) ** 2 * 2
    return 6


def add(group, kind, sysn, task, seed, n=5000, cfg=None, name=None):
    cfg = cfg or {}
    tag = "_".join([group, sysn, task, f"s{seed}", f"n{n}"] + [f"{k}{v}" for k, v in cfg.items()])
    f = f"results/raw/{tag}.json"
    jobs.append(dict(kind=kind, name=name or NAME[sysn], group=group, task=task, seed=seed, config=dict(cfg, n_train=n), file=f,
                     cost=cost(sysn, task, cfg),
                     cmd=["{py}", "method/run.py", "--system", sysn, "--task", task, "--seed", str(seed), "--n_train", str(n),
                          "--config", json.dumps(cfg), "--out", "{out}"]))


for task in TASKS:
    for s in S5:
        add("main", "method", "esn", task, s); add("main", "baseline", "mlp", task, s); add("main", "baseline", "gru", task, s)
        add("main", "sanity", "truth", task, s)
        add("main", "ablation", "esn", task, s, cfg={"sq": 0}, name="ESN without squared features")
        if T[f"gru/{task}"]["noise"] > 0: add("main", "ablation", "gru", task, s, cfg={"noise": 0.0}, name="GRU without input noise")
        if T[f"mlp/{task}"]["noise"] > 0: add("main", "ablation", "mlp", task, s, cfg={"noise": 0.0}, name="MLP without input noise")
    for s in S3:
        for r in [0.1, 0.7, 1.0, 1.4, 2.0]: add("sweep_rho", "ablation", "esn", task, s, cfg={"rho": r})
        for n in [100, 250, 1000, 2000]: add("sweep_size", "ablation", "esn", task, s, cfg={"size": n})
        for n in [500, 2000, 10000]:
            for sysn in ["esn", "mlp", "gru"]: add("sweep_ntrain", "ablation", sysn, task, s, n=n)
        for st in [4000, 8000, 16000, 32000]:
            if st != T[f"mlp/{task}"]["steps"]: add("sweep_steps", "ablation", "mlp", task, s, cfg={"steps": st})
        for st in [3000, 6000, 12000]:
            if st != T[f"gru/{task}"]["steps"]: add("sweep_steps", "ablation", "gru", task, s, cfg={"steps": st})

jobs.sort(key=lambda j: (-(j["group"] == "main"), -j["cost"]))   # main group first, long jobs first inside a group block
lanes, load = [[], []], [0.0, 0.0]
for j in jobs:
    i = 0 if load[0] <= load[1] else 1
    lanes[i].append(j); load[i] += j["cost"]
json.dump(lanes, open("experiments/jobs_main.json", "w"), indent=1)
print(len(jobs), "jobs; estimated lane seconds", [round(x) for x in load])
