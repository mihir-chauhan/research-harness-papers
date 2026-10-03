"""LR sensitivity over the three main peak LRs for systems given warmup=100 (groups abl_warmup_fair + abl_warmup)."""
import argparse, json
ap = argparse.ArgumentParser()
ap.add_argument("--system", required=True); ap.add_argument("--seed", type=int, required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
d = {}
for line in open("results/runs.jsonl"):
    r = json.loads(line)
    if r["name"] != a.system or r["seed"] != a.seed or r["status"] != "ok": continue
    if r["group"] in ("abl_warmup_fair", "abl_warmup"): d[r["config"]["lr"]] = r["metrics"]["val_loss"]
assert len(d) == 3, d
out = {"sens3": max(d.values()) - min(d.values()), "best3": min(d.values())}
print("sens_fair", a.system, a.seed, json.dumps(out)); json.dump(out, open(a.out, "w"))
