"""Run a list of (group, kind, name, task, seed, system args, config) jobs through `rh run`; 2 workers.

`rh run` names its log <YYYYmmdd-HHMMSS>_<group>_<name>_<task>_s<seed>.log, without the config value,
so two jobs that differ only in config must not start in the same second. Jobs sharing that stem are
therefore serialised here (one lock per stem, plus a pause), which keeps one log file per registry row.
"""
import subprocess, sys, json, os, time, threading, collections
from concurrent.futures import ThreadPoolExecutor
PY = os.environ["PY"]
TASKS = ["perm_dil", "split_cil", "split_til"]
_locks = collections.defaultdict(threading.Lock)
def command(g, kind, name, task, seed, sysargs, cfg):
    tag = f"{g}_{name.replace(' ','')}_{'_'.join(str(v) for v in cfg.values())}_{task}_{seed}"
    mf = f"results/raw/{tag}.json"
    cmd = ["nice", "-n", "10", "rh", "run", "--kind", kind, "--name", name, "--group", g, "--task", task, "--seed", str(seed),
           "--config", json.dumps(cfg), "--metrics-file", mf, "--", PY, "method/run.py", *sysargs, "--task", task,
           "--seed", str(seed), "--out", mf]
    if g == "main":
        cmd += ["--curve", f"results/raw/curve_{tag}.csv"]
    return tag, cmd
def job(g, kind, name, task, seed, sysargs, cfg):
    tag, cmd = command(g, kind, name, task, seed, sysargs, cfg)
    with _locks[(g, name, task, seed)]:
        r = subprocess.run(cmd, capture_output=True, text=True)
        time.sleep(2.1)  # the next job with the same log stem gets a later timestamp
    if r.returncode: print("FAIL", tag, r.stdout[-300:], r.stderr[-300:], flush=True)
def run(jobs):
    with ThreadPoolExecutor(2) as ex: list(ex.map(lambda j: job(*j), jobs))
