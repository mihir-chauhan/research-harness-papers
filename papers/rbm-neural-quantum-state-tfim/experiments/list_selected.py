"""Lists the selected state of every (system, task, seed) in registry group `selected`.

The selected state is defined in PROTOCOL.md: of the two starts (group `main` = start S, group `main_b` = start B)
the one with the lower relative energy error; a diverged start (NaN metrics) loses to a finite one. This script
runs no experiment and writes no metric: each selected run is listed again with `rh log --from-run <run_id>`, which
copies its metrics, config and provenance from the registry. With the group in place, `rh compare --group selected`
gives the registered tests on the selected states and `\\rhval{selected/...}` their aggregates.
Usage: list_selected.py (idempotent: a (system, task, seed) that is already listed is skipped)."""
import json, math, subprocess

rows = []
for l in open("results/runs.jsonl"):
    r = json.loads(l)
    if r.get("kind") == "control" and r.get("op") == "supersede":
        rows = [x for x in rows if not (x["group"] == r["group"] and x["name"] == r["name"])]
    elif r.get("status") == "ok" and "metrics" in r:
        rows.append(r)
START = {"main": "S", "main_b": "B"}
cand, done = {}, set()
for r in rows:
    key = (r["name"], r["task"], r["seed"])
    if r["group"] in START and math.isfinite(r["metrics"]["rel_energy_error"]):
        cand.setdefault(key, []).append(r)
    elif r["group"] == "selected":
        done.add(key)
assert len(cand) == 650, len(cand)
n = 0
for key in sorted(cand):
    if key in done:
        continue
    r = min(cand[key], key=lambda x: x["metrics"]["rel_energy_error"])
    subprocess.run(["rh", "log", "--from-run", r["run_id"], "--kind", r["kind"], "--name", r["name"], "--group", "selected",
                    "--task", r["task"], "--seed", str(r["seed"]), "--tag", "selected-copy", "--note", f"start {START[r['group']]}"],
                   check=True, stdout=subprocess.DEVNULL)
    n += 1
print(f"listed {n} selected states ({len(done)} were already listed)")
