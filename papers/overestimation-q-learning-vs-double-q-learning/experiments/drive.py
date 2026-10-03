import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
jobs = [l.strip() for l in open(sys.argv[1] if len(sys.argv) > 1 else "experiments/jobs.txt") if l.strip()]
def go(c):
    r = subprocess.run(["bash", "-c", c], capture_output=True, text=True)
    return r.returncode
with ThreadPoolExecutor(2) as ex:
    rcs = list(ex.map(go, jobs))
print("failed:", sum(1 for r in rcs if r))
