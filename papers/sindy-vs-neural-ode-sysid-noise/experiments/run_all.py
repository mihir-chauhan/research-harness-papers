"""Driver: issues every `rh run` of the study. Usage: python experiments/run_all.py <part> (two worker processes at most)."""
import subprocess, sys, json, os
from concurrent.futures import ThreadPoolExecutor
PY = os.environ["PY"]
SEEDS = range(5)
NAMES = {"sindy": ("SINDy (STLSQ)", "method"), "node": ("Neural ODE (MLP)", "baseline"),
         "dmdc": ("DMDc (linear LS)", "baseline"), "oracle": ("True model (oracle)", "baseline")}
jobs = []
def add(group, system, task, seed, noise, n, kind=None, name=None, extra=None, cfg=None):
    nm, k = NAMES[system]
    task_name = f"{task}_noise{noise}"
    f = "results/raw/" + f"{group}__{system}__{name or nm}__{task_name}__{'_'.join(f'{k}{v}' for k,v in (cfg or {}).items())}__{seed}.json".replace(" ", "_").replace("(", "").replace(")", "").replace("/", "-")
    args = f"--system {system} --task {task} --seed {seed} --noise {noise} --ntrain {n} " + (extra or "")
    # lam sweeps carry lambda in the run name so that every run gets its own log file
    c = ["rh", "run", "--kind", kind or k, "--name", name or nm, "--group", group, "--task", task_name, "--seed", str(seed)]
    if cfg: c += ["--config", json.dumps(cfg)]
    c += ["--metrics-file", f, "--", PY, "method/run.py", *args.split(), "--out", f]
    jobs.append(c)
part = sys.argv[1]
for task in ["pendulum", "vdp"]:
    for s in SEEDS:
        if part == "main":
            for noise in [0.0, 0.02, 0.05, 0.1]:
                for sy in NAMES: add("main", sy, task, s, noise, 1000)
        if part == "sweep_ntrain":
            for n in [200, 500, 1000, 2000, 5000]:
                for sy in NAMES: add(f"sweep_ntrain_{task}", sy, task, s, 0.05, n, cfg={"ntrain": n})
        if part == "sweep_noise":   # finer noise sweep, sparse+neural+linear, N=1000
            pass
        if part == "sweep_lam":
            for lam in [0.01, 0.03, 0.1, 0.3, 1.0]:
                add(f"sweep_lam_{task}", "sindy", task, s, 0.05, 1000, kind="ablation", name=f"SINDy lam={lam}", extra=f"--lam {lam}", cfg={"lam": lam})
        if part == "abl_sindy":
            add("abl_sindy", "sindy", task, s, 0.05, 1000)
            add("abl_sindy", "sindy", task, s, 0.05, 1000, kind="ablation", name="SINDy w/o trig library", extra="--trig 0")
            add("abl_sindy", "sindy", task, s, 0.05, 1000, kind="ablation", name="SINDy + SG smoothing", extra="--smooth 1")
            add("abl_sindy", "sindy", task, s, 0.05, 1000, kind="ablation", name="SINDy + SG smoothing, lam 0.3", extra="--smooth 1 --lam 0.3")
def go(c):
    r = subprocess.run(c, capture_output=True, text=True)
    if r.returncode: print("FAIL", " ".join(c), r.stdout[-300:], r.stderr[-300:], flush=True)
with ThreadPoolExecutor(2) as ex: list(ex.map(go, jobs))
print(part, "done", len(jobs))
