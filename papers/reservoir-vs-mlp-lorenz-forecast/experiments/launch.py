"""Job driver: runs a list of `rh run` jobs with at most two processes at a time (two sequential lanes).
usage: python experiments/launch.py <jobs.json>   where jobs.json = [[lane-0 jobs], [lane-1 jobs]] and a job is
{"kind","name","group","task","seed","config":{...},"file":"results/raw/x.json","cmd":[...]}  ("{out}" in cmd -> file)."""
import json, os, subprocess, sys, threading, time
lanes = json.load(open(sys.argv[1])); PY = os.environ["PY"]
def lane(jobs, i):
    for j in jobs:
        cmd = [c.replace("{out}", j["file"]).replace("{py}", PY) for c in j["cmd"]]
        full = ["nice", "-n", "10", "rh", "run", "--kind", j["kind"], "--name", j["name"], "--group", j["group"], "--task", j["task"],
                "--seed", str(j["seed"]), "--config", json.dumps(j["config"]), "--timeout", "360", "--metrics-file", j["file"], "--"] + cmd
        t = time.time(); r = subprocess.run(full, capture_output=True, text=True)
        print(f"lane{i} {time.time()-t:6.1f}s rc={r.returncode} {(r.stdout.strip().splitlines() or [''])[-1][:230]}", flush=True)
        if r.returncode: print(r.stderr[-500:], flush=True)
th = [threading.Thread(target=lane, args=(l, i)) for i, l in enumerate(lanes)]
t0 = time.time(); [t.start() for t in th]; [t.join() for t in th]; print("ALL DONE", round(time.time() - t0), "s")
