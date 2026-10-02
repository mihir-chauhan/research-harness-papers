"""Driver: python experiments/drive.py {tune|select|main|sweeps|abl|derived}. Calls `rh run` once per (system, task, seed).
`derived` logs the statistics of experiments/derive.py (correlations, Holm-adjusted p, per-seed differences), one row each."""
import json, subprocess, sys, os, collections
PY = os.environ["PY"]
TASKS = ["digits_n0.0", "digits_n0.2", "digits_n0.4", "spirals_n0.2"]
RHOS = [0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
WDS = [1e-4, 1e-3, 1e-2, 5e-2]
TUNE_SEEDS = [100, 101, 102]; SEEDS = [0, 1, 2, 3, 4]
SEL = "experiments/selected.json"

def run(kind, name, group, task, seed, system, rho=0.0, wd=0.0):
    tag = f"{group}_{system}_{task}_{seed}_{rho}_{wd}".replace("/", "_")
    f = f"results/raw/{tag}.json"
    cfg = {"system": system, "rho": rho, "wd": wd}
    cmd = ["nice", "-n", "10", "rh", "run", "--kind", kind, "--name", name, "--group", group, "--task", task,
           "--seed", str(seed), "--config", json.dumps(cfg), "--metrics-file", f, "--",
           PY, "method/run.py", "--system", system, "--task", task, "--seed", str(seed),
           "--rho", str(rho), "--wd", str(wd), "--out", f]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print("FAIL", tag, r.stdout[-300:], r.stderr[-300:])

def tune():
    for t in TASKS:
        for s in TUNE_SEEDS:
            for rho in RHOS: run("ablation", "SAM", "tune", t, s, "sam", rho=rho)
            for wd in WDS: run("ablation", "SGD+WD", "tune", t, s, "sgd_wd", wd=wd)

def rows(group):
    for l in open("results/runs.jsonl"):
        r = json.loads(l)
        if r.get("group") == group: yield r

def select():
    acc = collections.defaultdict(list)
    for r in rows("tune"):
        c = r["config"]; key = (r["task"], r["name"], c["rho"] if r["name"] == "SAM" else c["wd"])
        acc[key].append(r["metrics"]["val_acc"])
    sel = {}
    for t in TASKS:
        for name in ["SAM", "SGD+WD"]:
            cand = {k[2]: sum(v) / len(v) for k, v in acc.items() if k[0] == t and k[1] == name}
            sel[f"{t}|{name}"] = max(cand, key=cand.get)
    json.dump(sel, open(SEL, "w"), indent=1); print(sel)

def main():
    sel = json.load(open(SEL))
    for t in TASKS:
        for s in SEEDS:
            run("baseline", "SGD", "main", t, s, "sgd")
            run("baseline", "SGD+WD", "main", t, s, "sgd_wd", wd=sel[f"{t}|SGD+WD"])
            run("method", "SAM", "main", t, s, "sam", rho=sel[f"{t}|SAM"])

def sweeps():
    sel = json.load(open(SEL))
    for t in TASKS:
        for s in SEEDS:
            for rho in RHOS:
                if rho != sel[f"{t}|SAM"]: run("ablation", "SAM", "sweep_rho", t, s, "sam", rho=rho)
            for wd in WDS:
                if wd != sel[f"{t}|SGD+WD"]: run("ablation", "SGD+WD", "sweep_wd", t, s, "sgd_wd", wd=wd)

def abl():
    sel = json.load(open(SEL))
    for t in TASKS:
        for s in SEEDS:
            r, w = sel[f"{t}|SAM"], sel[f"{t}|SGD+WD"]
            run("ablation", "SAM random direction", "abl_sam", t, s, "sam_random", rho=r)
            run("ablation", "SAM+WD", "abl_sam", t, s, "sam_wd", rho=r, wd=w)

PRIMARY = "digits_n0.4"   # registry rows need a task; pooled statistics are filed under the primary task (see the row note)

def derive(name, task, args, pooled=None):
    tag = ("derived_" + name + "_" + task).replace(" ", "_").replace("/", "_")
    f = f"results/raw/{tag}.json"
    cfg = {"analysis": args[0], "args": " ".join(args[1:])}
    note = []
    if pooled:
        cfg["pooled_over"] = pooled
        note = ["--note", f"pooled over {pooled}; the task field is only a placeholder"]
    cmd = ["nice", "-n", "10", "rh", "run", "--kind", "ablation", "--name", name, "--group", "derived", "--task", task,
           "--seed", "0", "--config", json.dumps(cfg), "--metrics-file", f, *note, "--",
           PY, "experiments/derive.py", *args, "--out", f]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout.strip()[:200] if not r.returncode else ("FAIL " + tag + r.stdout[-300:] + r.stderr[-300:]))

def derived():
    thr = ["--collapse-digits", "0.15", "--collapse-spirals", "0.55"]
    for scope, nm in [("all", "corr all"), ("no_collapsed", "corr no-collapsed"), ("sam", "corr SAM")]:
        for t in (TASKS[:3] if scope == "sam" else TASKS):
            derive(nm, t, ["corr", "--scope", scope, "--task", t] + thr)
    derive("corr pooled all", PRIMARY, ["corr", "--scope", "all", "--task", "pooled"] + thr, pooled="all four tasks")
    derive("corr pooled no-collapsed", PRIMARY, ["corr", "--scope", "no_collapsed", "--task", "pooled"] + thr, pooled="all four tasks")
    derive("corr pooled SAM digits", PRIMARY, ["corr", "--scope", "sam", "--task", "pooled"] + thr, pooled="the three digits tasks")
    for t in TASKS:
        for b in ["SGD", "SGD+WD"]:
            derive(f"SAM minus {b}", t, ["paired", "--task", t, "--baseline", b])

if __name__ == "__main__":
    globals()[sys.argv[1]]()
