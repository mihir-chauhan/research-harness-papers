"""Emit the shell job list for all groups (one `rh run` command per line)."""
import json
NAMES = {"q": "Q-learning", "double": "Double Q-learning", "wdq": "Weighted Double Q-learning",
         "maxmin": "Maxmin Q-learning", "double_both": "Double Q-learning (both tables)"}
SEEDS = range(5)
jobs = []

def job(group, kind, system, task, seed, extra=None, tag=""):
    extra = extra or {}
    flags = " ".join(f"--{k} {v}" for k, v in extra.items())
    f = f"results/raw/{group}_{task}_{system}{tag}_s{seed}.json"
    cfg = json.dumps(extra) if extra else ""
    cfgarg = f"--config '{cfg}' " if cfg else ""
    curve = f"--curve results/raw/curve_{group}_{task}_{system}_s{seed}.csv" if group == "main" else ""
    jobs.append(f"rh run --kind {kind} --name \"{NAMES[system]}\" --group {group} --task {task} --seed {seed} {cfgarg}"
                f"--metrics-file {f} -- nice -n 10 $PY method/run.py --system {system} --task {task} --seed {seed} {flags} {curve} --out {f}")

for task in ["maxbias", "random20"]:
    for sy in ["q", "double", "wdq", "maxmin"]:
        for s in SEEDS:
            job("main", "method" if sy == "double" else "baseline", sy, task, s)
for task in ["maxbias", "random20"]:
    for s in SEEDS:
        job("abl_double", "ablation", "double_both", task, s)
for sy in ["q", "double", "wdq", "maxmin"]:
    for s in SEEDS:
        job("abl_warm", "ablation", sy, "random20", s, {"init": "true"})
for v in [0.25, 2, 4]:
    for sy in ["q", "double"]:
        for s in SEEDS:
            job("sweep_sigma", "ablation", sy, "random20", s, {"sigma": v}, f"_{v}")
for v in [0.3, 1.0]:
    for sy in ["q", "double"]:
        for s in SEEDS:
            job("sweep_eps", "ablation", sy, "random20", s, {"epsilon": v}, f"_{v}")
for v in [0.02, 0.05, 0.2]:
    for sy in ["q", "double"]:
        for s in SEEDS:
            job("sweep_alpha", "ablation", sy, "random20", s, {"alpha": v}, f"_{v}")
for v in [2, 5, 25, 100]:
    for sy in ["q", "double", "wdq", "maxmin"]:
        for s in SEEDS:
            job("sweep_actions", "ablation", sy, "maxbias", s, {"n_actions": v}, f"_{v}")
import sys
if len(sys.argv) > 1 and sys.argv[1] == "extra":
    jobs = []
    for sy in ["q", "double", "wdq", "maxmin"]:
        for s in SEEDS:
            job("abl_warm", "ablation", sy, "maxbias", s, {"init": "true"})
print("\n".join(jobs))
