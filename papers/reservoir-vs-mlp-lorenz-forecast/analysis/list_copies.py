"""Lists existing runs in further groups with `rh log --from-run` (no metric is typed: rh copies the run's metrics, config and
provenance). Run once from the project root after sourcing seed/env.sh; a copy that is already in the registry is skipped.
  sweep_rho, sweep_size, sweep_ntrain, sweep_steps   the default point of each sweep: the main runs of seeds 0-2
  abl_gru                                            GRU and GRU without input noise (main, 5 seeds), for `rh compare --ref GRU`
  nt<N>                                              ESN and MLP at n_train=N (seeds 0-2), for `rh compare --ref ESN`
  st_<system><steps>                                 ESN (tuned) and one baseline at one optimiser budget (seeds 0-2), for `rh compare --ref ESN`
analysis/build.sh then calls rh compare on these groups."""
import sys, json, subprocess
sys.path.insert(0, open("../../harness_path.txt").read().strip())
from rh import registry
from pathlib import Path
rows = [r for r in registry.read_rows(Path("results/runs.jsonl")) if r.get("status") == "ok"]
TASKS = ["lorenz63", "lorenz96"]
tuned = json.load(open("method/tuned.json")); KEY = {"MLP delay": "mlp", "GRU": "gru"}

def find(group, name, task, seed, **cfg):
    m = [r for r in rows if r["group"] == group and r["name"] == name and r["task"] == task and r["seed"] == seed
         and all(r["config"].get(k) == v for k, v in cfg.items())]
    assert len(m) == 1, (group, name, task, seed, cfg, len(m))
    return m[0]

jobs = []   # (source row, target group, note)
S3, S5 = [0, 1, 2], [0, 1, 2, 3, 4]
for t in TASKS:
    for s in S3:
        esn = find("main", "ESN", t, s)
        for g in ["sweep_rho", "sweep_size", "sweep_ntrain"]:
            jobs.append((esn, g, "default point of the sweep (tuned setting): the main run of this seed"))
        for nm in ["MLP delay", "GRU"]:
            m = find("main", nm, t, s)
            jobs.append((m, "sweep_ntrain", "default point of the sweep (n_train=5000): the main run of this seed"))
            jobs.append((m, "sweep_steps", "default point of the sweep (tuned optimiser steps): the main run of this seed"))
        # ESN versus MLP at one training length, for `rh compare --group nt<N> --ref ESN`
        for n in [500, 2000, 5000, 10000]:
            for nm in ["ESN", "MLP delay"]:
                src = find("main", nm, t, s) if n == 5000 else find("sweep_ntrain", nm, t, s, n_train=n)
                jobs.append((src, f"nt{n}", f"ESN and MLP at n_train={n}, listed together for rh compare"))
        # ESN versus a baseline at one optimiser budget, for `rh compare --group st_<sys><steps> --ref ESN`
        for nm, steps in [("MLP delay", [4000, 8000, 16000, 32000]), ("GRU", [3000, 6000, 12000])]:
            for v in steps:
                g = f"st_{KEY[nm]}{v}"
                src = find("main", nm, t, s) if tuned[f"{KEY[nm]}/{t}"]["steps"] == v else find("sweep_steps", nm, t, s, steps=v)
                jobs.append((esn, g, f"ESN (tuned) next to {nm} at {v} optimiser steps, for rh compare"))
                jobs.append((src, g, f"{nm} at {v} optimiser steps, listed next to the ESN for rh compare"))
    for s in S5:   # GRU versus its own ablation, for `rh compare --group abl_gru --ref GRU`
        for nm in ["GRU", "GRU without input noise"]:
            jobs.append((find("main", nm, t, s), "abl_gru", "GRU and its no-noise ablation, listed together for rh compare"))
have = {(r["group"], (r.get("provenance") or {}).get("copied_from")) for r in rows}
jobs = [j for j in jobs if (j[1], j[0]["run_id"]) not in have]
print(len(jobs), "copies to make")
for src, g, note in jobs:
    cmd = ["rh", "log", "--kind", "ablation", "--name", src["name"], "--group", g, "--task", src["task"], "--seed", str(src["seed"]),
           "--from-run", src["run_id"], "--note", note]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print("FAILED", cmd, r.stdout, r.stderr); sys.exit(1)
print("done")
