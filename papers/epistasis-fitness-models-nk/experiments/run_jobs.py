"""usage: run_jobs.py jobs.txt -- runs each shell line (2 in parallel, niced) from the workspace root."""
import subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
env = dict(os.environ, OMP_NUM_THREADS="2", MKL_NUM_THREADS="2")
lines = [l for l in open(sys.argv[1]).read().splitlines() if l.strip()]
def go(l):
    r = subprocess.run(["nice", "-n", "10", "bash", "-c", l], env=env)
    if r.returncode: print("FAILED", r.returncode, l[:120], flush=True)
with ThreadPoolExecutor(2) as ex: list(ex.map(go, lines))
print("done", len(lines))
