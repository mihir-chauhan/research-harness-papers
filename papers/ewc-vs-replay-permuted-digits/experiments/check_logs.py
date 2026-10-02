"""Check that every active registry row has its own log file and that the log is the output of that row's command."""
import json, collections, os
import sys; sys.path.insert(0, "experiments")
from registry import active_runs
act = active_runs()
cnt = collections.Counter(r["provenance"]["log"] for r in act)
bad = 0
for r in act:
    lp = r["provenance"]["log"]
    txt = open(lp).read() if os.path.exists(lp) else ""
    tail = r["provenance"]["command"].split("method/run.py", 1)[1].replace("'", "")
    ok = cnt[lp] == 1 and txt.count("# rh run") == 1 and tail in txt.replace("'", "") and txt.count("metrics:") == 1
    if ok:  # the metrics line of the log must equal the registry metrics
        m = json.loads(txt.split("metrics:", 1)[1].splitlines()[0])
        ok = all(abs(m[k] - v) < 1e-12 for k, v in r["metrics"].items())
    bad += not ok
    if not ok: print("BAD", r["group"], r["name"], r["task"], r["seed"], r["config"], lp)
print(f"active rows: {len(act)}; distinct logs: {len(cnt)}; rows without a clean own log: {bad}")
