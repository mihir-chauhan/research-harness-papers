"""Run the queue with two workers (each line is one `rh run ...` shell command)."""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
lines = [l.strip() for l in open(sys.argv[1]) if l.strip()]
def go(l):
    r = subprocess.run(["nice", "-n", "10", "sh", "-c", l], capture_output=True, text=True)
    print(r.stdout[-300:], r.stderr[-300:], flush=True)
with ThreadPoolExecutor(2) as ex:
    list(ex.map(go, lines))
