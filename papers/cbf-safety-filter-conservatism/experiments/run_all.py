"""Driver: registers every run through `rh run`. Usage: run_all.py {A|B}  (A: main, grid CT; B: grid DT, dth, abl_select)."""
import subprocess, sys, json, time, os, re
PY = os.environ["PY"]
NM = {"nominal": ("baseline", "Nominal"), "ct": ("baseline", "CT-CBF"), "dt": ("method", "DT-CBF"), "heur": ("baseline", "Braking")}
TASKS = ["double_integrator", "unicycle"]; SEEDS = range(5)
ALPHAS = [0.5, 1, 2, 5, 10]; DTS = [0.01, 0.02, 0.05, 0.1, 0.2]
jobs = []
def add(group, system, task, seed, alpha=2, dt=0.05, dth=1.0, select="critical", ablation=False):
    kind = "ablation" if ablation else NM[system][0]
    cfg = {"alpha": alpha, "dt": dt} if system in ("ct", "dt") else ({"dth": dth} if system == "heur" else {})
    if group == "abl_select": cfg["select"] = select
    jobs.append((group, system, task, seed, kind, cfg, dict(alpha=alpha, dt=dt, dth=dth, select=select)))
which = sys.argv[1]
if which == "A":
    for t in TASKS:
        for s in SEEDS:
            for sy in ["nominal", "ct", "dt", "heur"]: add("main", sy, t, s)
    for t in TASKS:
        for a in ALPHAS:
            for d in DTS:
                for s in SEEDS: add("grid_alpha_dt", "ct", t, s, alpha=a, dt=d, ablation=True)
else:
    for t in TASKS:
        for a in ALPHAS:
            for d in DTS:
                for s in SEEDS: add("grid_alpha_dt", "dt", t, s, alpha=a, dt=d, ablation=True)
    for t in TASKS:
        for th in [0.25, 0.5, 1, 2]:
            for s in SEEDS: add("sweep_dth", "heur", t, s, dth=th, ablation=True)
    for t in TASKS:
        for sy in ["ct", "dt"]:
            for a in [2, 5, 10]:
                for s in SEEDS: add("grid_dt005", sy, t, s, alpha=a, dt=0.005, ablation=True)
    for sy in ["ct", "dt"]:
        for sel in ["nearest", "critical"]:
            for s in SEEDS: add("abl_select", sy, "double_integrator", s, select=sel, ablation=True)
last = 0
for group, system, task, seed, kind, cfg, a in jobs:
    while int(time.time()) == last: time.sleep(0.05)   # unique log file name per run (rh names logs by second)
    last = int(time.time())
    tag = re.sub(r"[^A-Za-z0-9]+", "_", json.dumps(cfg))
    out = f"results/raw/{group}_{system}_{task}_{tag}_{seed}.json"
    cmd = ["nice", "-n", "10", "rh", "run", "--kind", kind, "--name", NM[system][1], "--group", group, "--task", task, "--seed", str(seed),
           "--config", json.dumps(cfg), "--metrics-file", out, "--", PY, "method/run.py", "--system", system, "--task", task, "--seed", str(seed),
           "--alpha", str(a["alpha"]), "--dt", str(a["dt"]), "--dth", str(a["dth"]), "--select", a["select"], "--out", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print("FAIL", cmd, r.stdout[-300:], r.stderr[-300:], flush=True)
print("done", which, len(jobs))
