"""usage: main.py <main|abl|sweep>. Logs every run with `rh run`, two at a time. Configs = tuned hyper-parameters (experiments/select.py)."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); os.makedirs("results/raw", exist_ok=True)
env = {**os.environ, "OMP_NUM_THREADS": "2", "MKL_NUM_THREADS": "2"}
PY = os.environ["PY"]; TASK = "physionet2012_mortality"
CFG = dict(lr={"C": 0.01}, gbdt={"leaves": 32, "l2": 10}, gru_ffill={"hidden": 32, "lr": 0.003}, gru_md={"hidden": 32, "lr": 0.001, "wd": 0.01}, grud={"hidden": 32, "lr": 0.001})
NAME = dict(lr="LR (summary)", gbdt="GBDT (summary)", gru_ffill="GRU (forward-fill)", gru_md="GRU (mask+delta)", grud="GRU-D")
jobs = []  # (kind, name, group, system, seed, tag, extra)
st = sys.argv[1]; S = range(5)
if st == "main":
    for sy in CFG:
        for s in S: jobs.append(("method" if sy == "grud" else "baseline", NAME[sy], "main", sy, s, "main", {}))
elif st == "abl":
    for s in S:
        jobs += [("ablation", "GRU-D w/o input decay", "abl_decay", "grud", s, "noin", {"in_decay": 0}),
                 ("ablation", "GRU-D w/o hidden decay", "abl_decay", "grud", s, "nohid", {"h_decay": 0}),
                 ("ablation", "GRU-D w/o any decay", "abl_decay", "grud", s, "nodecay", {"in_decay": 0, "h_decay": 0}),
                 ("ablation", "LR (summary) w/o counts", "abl_counts", "lr", s, "nocnt", {"counts": 0}),
                 ("ablation", "GBDT (summary) w/o counts", "abl_counts", "gbdt", s, "nocnt", {"counts": 0})]
elif st == "sweep":
    for h in (12, 24):
        for sy in CFG:
            for s in S: jobs.append(("ablation", f"{NAME[sy]} @{h}h", "sweep_horizon", sy, s, f"h{h}", {"horizon": h}))
def run(j):
    kind, nm, grp, sy, s, tag, extra = j
    cfg = json.dumps({**CFG[sy], **extra}); f = f"results/raw/{grp}_{sy}_{tag}_s{s}.json"
    return subprocess.run(["rh", "run", "--kind", kind, "--name", nm, "--group", grp, "--task", TASK, "--seed", str(s), "--config", cfg, "--metrics-file", f, "--",
                           "nice", "-n", "10", PY, "method/run.py", "--system", sy, "--seed", str(s), "--config", cfg, "--out", f], env=env, capture_output=True, text=True).stdout[-300:]
with ThreadPoolExecutor(2) as ex:
    for o in ex.map(run, jobs): print(o.strip().split("\n")[0][:160], flush=True)
