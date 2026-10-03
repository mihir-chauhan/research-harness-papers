"""Pick the best config per system from tuning runs (mean hold-out AUROC over tuning seeds); ties -> first in file order (smaller model)."""
import json, sys, collections
out = sys.argv[1] if len(sys.argv) > 1 else None
rows = []; sup = set()
for l in open("results/runs.jsonl"):
    r = json.loads(l)
    if r.get("op") == "supersede":  # control row: retire earlier ok rows of (group, name)
        for q in rows:
            if q.get("group") == r["group"] and q.get("name") == r["name"]: q["status"] = "superseded"
    else: rows.append(r)
d = collections.defaultdict(list)
for r in rows:
    if r["group"] in ("tune", "tune2") and r["status"] == "ok": d[(r["name"].replace("tune ", ""), json.dumps(r["config"], sort_keys=True))].append(r["metrics"]["auroc"])
best = {}
for (s, c), v in d.items():
    m = sum(v) / len(v)
    if s not in best or m > best[s][0] + 1e-9: best[s] = (m, c, len(v))
for s, (m, c, n) in sorted(best.items()): print(s, round(m, 4), c, n)
if out:
    res = {}
    for s, (m, c, n) in best.items(): res[f"best_holdout_auroc_{s}"] = m
    json.dump(res, open(out, "w"))
