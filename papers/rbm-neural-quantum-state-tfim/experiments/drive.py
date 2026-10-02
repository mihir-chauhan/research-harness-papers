"""Driver: launches every run through `rh run`.
Usage: [ONLY=<ansatz>] drive.py tune|main|main_b|exact_opt|abl_shift|abl_samples|curves [worker k of n]
main = symmetric start (a_i ~ N(0, 0.01^2)); main_b = symmetry-broken start (a_i = 0.5 + N(0, 0.01^2)), same rates.
ONLY=jastrow restricts a group to one ansatz (used to re-run Jastrow after its parametrisation was fixed)."""
import json, subprocess, sys, os, itertools
GROUP = sys.argv[1]; K, NW = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 1)
SYS = [("Mean-field", "mf", 1), ("Jastrow", "jastrow", 1), ("RBM alpha=1", "rbm", 1),
       ("RBM alpha=2", "rbm", 2), ("RBM alpha=4", "rbm", 4)]
if os.environ.get("ONLY"):
    SYS = [x for x in SYS if x[1] == os.environ["ONLY"]]
FIELD_B = 0.5
OPT = {"sgd": "SGD", "sr": "SR"}
TUNE_TASK = "tfim_N10_g1.00"
TUNE_TASKS = ["tfim_N10_g0.25", "tfim_N10_g1.00", "tfim_N12_g0.50"]  # v2 tuning set (v1 used TUNE_TASK only)
TASKS = ["tfim_N10_g%.2f" % g for g in [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]] + \
        ["tfim_N%d_g%.2f" % (n, g) for n in (8, 12) for g in (0.5, 1.0, 1.5)]
SEEDS = [0, 1, 2, 3, 4]
LR = json.load(open("experiments/lr.json")) if os.path.exists("experiments/lr.json") else {}

def run(kind, name, group, task, seed, ansatz, alpha, opt, extra, cfg, tag):
    out = f"results/raw/{group}_{tag}.json"
    cmd = ["rh", "run", "--kind", kind, "--name", name, "--group", group, "--task", task, "--seed", str(seed),
           "--config", json.dumps(cfg), "--metrics-file", out, "--", sys.executable, "method/run.py",
           "--ansatz", ansatz, "--alpha", str(alpha), "--opt", opt, "--task", task, "--seed", str(seed), "--out", out] + extra
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)

jobs = []
if GROUP == "tune":
    # rate is the outer loop per system so that two runs with the same (name, task, seed) never start in the same
    # second (the harness log name has no rate in it)
    for (n, a, al), o in itertools.product(SYS, OPT):
        for lr, tt, ts in itertools.product([0.003, 0.01, 0.03, 0.1] if o == "sgd" else [0.02, 0.05, 0.1], TUNE_TASKS, [100, 101, 102]):
            jobs.append(("ablation", f"{n} {OPT[o]}", "tune_lr3", tt, ts, a, al, o, ["--lr", str(lr)], {"lr": lr}, f"{a}{al}_{o}_{lr}_{tt}_s{ts}"))
elif GROUP == "main":
    for t, s, (n, a, al), o in itertools.product(TASKS, SEEDS, SYS, OPT):
        lr = LR[f"{a}{al}_{o}"]
        kind = "method" if (a, al, o) == ("rbm", 2, "sr") else "baseline"
        jobs.append((kind, f"{n} {OPT[o]}", "main", t, s, a, al, o, ["--lr", str(lr)], {"lr": lr}, f"{a}{al}_{o}_{t}_s{s}"))
elif GROUP == "main_b":
    for t, s, (n, a, al), o in itertools.product(TASKS, SEEDS, SYS, OPT):
        lr = LR[f"{a}{al}_{o}"]
        kind = "method" if (a, al, o) == ("rbm", 2, "sr") else "baseline"
        jobs.append((kind, f"{n} {OPT[o]}", "main_b", t, s, a, al, o, ["--lr", str(lr), "--field-init", str(FIELD_B)],
                     {"lr": lr, "field_init": FIELD_B}, f"{a}{al}_{o}_{t}_s{s}"))
elif GROUP == "exact_opt":
    # sampling-free reference: L-BFGS on the exactly enumerated energy, both starts, seed 0
    # (RBM alpha=1 and 4 are left out to bound the compute: the enumerated RBM gradient is the slow part)
    for t, (n, a, al), fi in itertools.product(TASKS, [x for x in SYS if x[0] in ("Mean-field", "Jastrow", "RBM alpha=2")], [0.0, FIELD_B]):
        st = "B" if fi else "S"
        jobs.append(("ablation", f"{n} exact-gradient", "exact_opt", t, 0, a, al, "exact", ["--field-init", str(fi)],
                     {"start": st, "field_init": fi}, f"{a}{al}_{st}_{t}"))
elif GROUP == "abl_shift":
    for s, sh in itertools.product(SEEDS, [1e-4, 1e-3, 1e-2, 1e-1, 1.0]):
        jobs.append(("ablation", "RBM alpha=2 SR", "sweep_shift", TUNE_TASK, s, "rbm", 2, "sr", ["--lr", str(LR["rbm2_sr"]), "--shift", str(sh)], {"shift": sh}, f"s{s}_{sh}"))
elif GROUP == "abl_samples":
    for s, m in itertools.product(SEEDS, [32, 64, 128, 256, 512]):
        jobs.append(("ablation", "RBM alpha=2 SR", "sweep_samples", TUNE_TASK, s, "rbm", 2, "sr", ["--lr", str(LR["rbm2_sr"]), "--samples", str(m)], {"samples": m}, f"s{s}_{m}"))
elif GROUP == "curves":
    for s, (n, a, al), o in itertools.product([0, 1, 2], SYS, OPT):
        tag = f"{a}{al}_{o}_s{s}"
        jobs.append(("ablation", f"{n} {OPT[o]}", "curves", TUNE_TASK, s, a, al, o,
                     ["--lr", str(LR[f"{a}{al}_{o}"]), "--curve", f"results/raw/curve_{tag}.csv"], {"lr": LR[f"{a}{al}_{o}"]}, tag))
for i, j in enumerate(jobs):
    if i % NW == K:
        run(*j)
