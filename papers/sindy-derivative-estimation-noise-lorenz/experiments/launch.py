"""Launcher for the revised runs (tuned.json with the largest-threshold tie-break).
Usage: python experiments/launch.py <worker> <n_workers> [group ...]   (runs every job with index % n_workers == worker)
Resumable: a job whose metrics file already has an ok row in results/runs.jsonl is skipped."""
import subprocess, sys, json, os

PY = os.environ["PY"]
SYS = [("weak", "Weak-form STLSQ", "method"), ("fd", "FD-STLSQ", "baseline"), ("sg", "SG-STLSQ", "baseline"),
       ("spline", "Spline-STLSQ", "baseline"), ("tv", "TV-STLSQ", "baseline")]
LV = ["0", "0.5", "1", "2", "5", "10"]
SEEDS = range(20)
THR = "0.05,0.1,0.2,0.4,0.6"
jobs = []  # (group, kind, name, task, seed, config, metrics file, extra args)
for lv in LV:
    for seed in SEEDS:
        for key, name, kind in SYS:
            jobs.append(("main", kind, name, lv, seed, None, f"r2_main_{key}_n{lv}_s{seed}", []))
for lv in ["2", "5"]:
    for w in [0.3, 1.0, 1.5, 2.5, 4.0]:   # tuned width 0.6 is the main run
        for seed in SEEDS:
            c = {"width": w}
            jobs.append(("sweep_width", "ablation", "Weak-form STLSQ", lv, seed, c, f"r2_sweep_width_weak_n{lv}_s{seed}_w{w}",
                         ["--override", json.dumps(c)]))
for p in [2, 4, 6]:                        # p=3 is the main run
    for seed in SEEDS:
        c = {"p": p}
        jobs.append(("abl_p", "ablation", "Weak-form STLSQ", "2", seed, c, f"r2_abl_p_weak_n2_s{seed}_p{p}", ["--override", json.dumps(c)]))
for lv in LV:
    for seed in SEEDS:
        for key, name, _ in SYS:
            jobs.append(("sweep_thr", "ablation", name, lv, seed, {"thr_grid": THR}, f"r2_sweep_thr_{key}_n{lv}_s{seed}", ["--thr-grid", THR]))

done = set()
for line in open("results/runs.jsonl"):
    r = json.loads(line)
    if r.get("status") == "ok":
        done.add(r["provenance"]["command"].split("--out ")[1].split()[0])
worker, n = int(sys.argv[1]), int(sys.argv[2])
groups = sys.argv[3:]
key_of = {name: key for key, name, _ in SYS}
for i, (group, kind, name, lv, seed, cfg, mf, extra) in enumerate(jobs):
    if i % n != worker or (groups and group not in groups):
        continue
    out = f"results/raw/{mf}.json"
    if out in done:
        continue
    cmd = ["rh", "run", "--kind", kind, "--name", name, "--group", group, "--task", f"lorenz_n{lv}", "--seed", str(seed)]
    if cfg:
        cmd += ["--config", json.dumps(cfg)]
    cmd += ["--metrics-file", out, "--", PY, "method/run.py", "--system", key_of[name], "--task", f"lorenz_n{lv}",
            "--seed", str(seed), "--out", out] + extra
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL)
    if r.returncode != 0:
        print("FAILED", group, name, lv, seed, cfg, flush=True)
print("worker", worker, "done", flush=True)
