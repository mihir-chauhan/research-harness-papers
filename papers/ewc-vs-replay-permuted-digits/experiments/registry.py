"""Active rows of results/runs.jsonl: status ok and not retired by a later `rh supersede` control row."""
import json
def active_runs(path="results/runs.jsonl"):
    rows = [json.loads(l) for l in open(path)]
    ctrl = [(i, r) for i, r in enumerate(rows) if r.get("kind") == "control"]
    return [r for i, r in enumerate(rows) if r.get("kind") != "control" and r["status"] == "ok"
            and not any(j > i and c["group"] == r["group"] and c["name"] == r["name"] for j, c in ctrl)]
