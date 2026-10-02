"""Merge the tuning results (experiments/tuning_<task>_<system>_<stage>[<steps>].json) into method/tuned.json:
ESN from stage A; MLP and GRU from the best stage-B cell over all step values."""
import glob, json
out = {}
for task in ["lorenz63", "lorenz96"]:
    for sysn, stage in [("esn", "A"), ("mlp", "B"), ("gru", "B")]:
        rows = [r for f in sorted(glob.glob(f"experiments/tuning_{task}_{sysn}_{stage}*.json")) for r in json.load(open(f))["grid"]]
        best = max(rows, key=lambda r: r["val_vpt"]); out[f"{sysn}/{task}"] = best["cfg"]
        print(sysn, task, len(rows), "cells; best", best)
json.dump(out, open("method/tuned.json", "w"), indent=1)
