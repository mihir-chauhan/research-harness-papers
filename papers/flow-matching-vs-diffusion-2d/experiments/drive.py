"""Driver: launches every run through `rh run`. Usage: drive.py PART  (A, B, C)"""
import subprocess, sys, json, os
part = sys.argv[1]
TASKS = ["eight_gaussians", "two_moons", "checkerboard"]
# (system flag, display name, kind, group, extra args, seeds)
A = [("fm_euler", "Flow Matching (Euler)", "method", "main", [], range(5)),
     ("fm_heun", "Flow Matching (Heun)", "baseline", "main", [], range(5)),
     ("reflow", "Reflow-1 (Euler)", "method", "main", [], range(5))]
B = [("ddim", "DDIM", "baseline", "main", [], range(5)),
     ("ddpm_anc", "DDPM ancestral", "baseline", "main", [], range(5)),
     ("real", "Real data (floor)", "sanity", "main", [], range(5))]
C = [("ddim", "DDIM (cosine)", "ablation", "abl_schedule", ["--sched", "cosine"], range(3)),
     ("ddim", "DDIM (cosine, start at ab>=4e-5)", "ablation", "abl_schedule", ["--sched", "cosine", "--start_ab", "4e-5"], range(3)),
     ("reflow", "Reflow-1 (teacher 4 steps)", "ablation", "abl_reflow", ["--teacher_steps", "4"], range(3)),
     ("reflow", "Reflow-2 (Euler)", "ablation", "abl_reflow", ["--rounds", "2"], range(3))]
runs = {"A": A, "B": B, "C": C}[part]
for seed in range(5):
    for task in TASKS:
        for sysf, name, kind, group, extra, seeds in runs:
            if seed not in seeds: continue
            tag = f"{group}_{sysf}{''.join(e.strip('-') for e in extra)}_{task}_s{seed}"
            mf = f"results/raw/{tag}.json"
            if os.path.exists(mf): continue
            cfg = {"extra": " ".join(extra)} if extra else {}
            cmd = ["rh", "run", "--kind", kind, "--name", name, "--group", group, "--task", task, "--seed", str(seed),
                   "--metrics-file", mf]
            if cfg: cmd += ["--config", json.dumps(cfg)]
            cmd += ["--", sys.executable if False else os.environ["PY"], "method/run.py", "--system", sysf, "--task", task,
                    "--seed", str(seed), "--out", mf] + extra
            r = subprocess.run(cmd, capture_output=True, text=True)
            print(tag, r.returncode, r.stdout[-150:].replace("\n", " "), r.stderr[-300:], flush=True)
