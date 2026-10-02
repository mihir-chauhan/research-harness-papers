"""Writes the queue of rh run commands (one per line)."""
import json
NAME = {"CE": "CE", "GCE": "GCE", "SCE": "SCE", "BandIgnoreCE": "Band-ignore CE"}
def cmd(kind, name, group, task, seed, system, cfg, extra=""):
    f = f"results/raw/{group}_{system}_{task}_{'_'.join(f'{k}{v}' for k,v in cfg.items())}_s{seed}.json"
    c = json.dumps(cfg)
    return (f"rh run --kind {kind} --name '{name}' --group {group} --task {task} --seed {seed} --config '{c}' "
            f"--metrics-file {f} -- $PY method/run.py --system {system} --task {task} --seed {seed} {extra} --out {f}")
out = []
TASKS = ["none", "boundary_p0.3", "flip_p0.3"]
for s in range(4):
    for t in TASKS:
        for sy in NAME:
            out.append(cmd("method" if sy == "BandIgnoreCE" else "baseline", NAME[sy], "main", t, s, sy, {"n": 500}, "--n 500"))
for s in range(4):
    for n in (100, 2000):
        for t in TASKS:
            out.append(cmd("ablation", f"CE n={n}", "size", t, s, "CE", {"n": n}, f"--n {n}"))
for s in range(3):
    for n in (250, 1000):
        for t in ("none", "flip_p0.3"):
            out.append(cmd("ablation", f"CE n={n}", "size", t, s, "CE", {"n": n}, f"--n {n}"))
    for t in ("flip_p0.1", "flip_p0.2"):
        out.append(cmd("ablation", "CE", "sweep_noise", t, s, "CE", {"n": 500}, "--n 500"))
    for q in (0.3, 0.9):
        out.append(cmd("ablation", f"GCE q={q}", "sweep_gce_q", "flip_p0.3", s, "GCE", {"q": q}, f"--n 500 --q {q}"))
    for st in (200, 1200):
        out.append(cmd("ablation", f"CE steps={st}", "sweep_steps", "flip_p0.3", s, "CE", {"n": 100, "steps": st}, f"--n 100 --steps {st}"))
print("\n".join(out))
