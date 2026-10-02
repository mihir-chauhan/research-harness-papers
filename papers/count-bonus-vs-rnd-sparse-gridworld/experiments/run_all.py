"""Every registry run of the study, through `rh run` (two processes at a time).

Usage: $PY experiments/run_all.py [pilot|main|abl|sweeps|all|copies]
`copies` runs nothing: it copies the main rows of the penalty-only control and the count (state) bonus into the group
`offset_control` (`rh log --from-run`), so that `rh compare` can test the two against each other.
Each run writes its own metrics file under results/raw/r2/ and is skipped if that file exists.
Sweep cells at the default value (beta 0.1, K 16, clip 5) are the `main` runs and are not repeated.
"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

PY = os.environ["PY"]
TASKS = ["chain_10", "chain_20", "chain_40", "room_2", "room_4", "room_6", "chain_20_tv", "room_4_tv"]
SEEDS = [0, 1, 2, 3, 4]
DEF = {"beta": 0.1, "offset": 1.0, "K": 16, "warmup": 64, "clip": 5.0}
# display name -> (kind, system, overrides of DEF)
MAIN = {
    "Epsilon-greedy Q-learning": ("baseline", "egreedy", {}),
    "Step penalty only (optimistic init)": ("baseline", "offset_only", {}),
    "Count bonus (state), no offset": ("ablation", "count_state", {"offset": 0.0}),
    "Count bonus (state)": ("baseline", "count_state", {}),
    "Count bonus (obs)": ("baseline", "count_obs", {}),
    "RND bonus": ("method", "rnd", {}),
}
ABL = {
    "no bonus normalisation (rnd_nonorm)": ("ablation", "rnd_nonorm", {}),
    "RND, unguarded normaliser (v1)": ("ablation", "rnd", {"warmup": 0, "clip": 0.0}),
    "RND, warm-up only": ("ablation", "rnd", {"clip": 0.0}),
    "RND, clip only": ("ablation", "rnd", {"warmup": 0}),
}


def job(group, name, kind, system, over, task, seed):
    cfg = dict(DEF, **over, system=system)
    tag = "_".join(f"{k}{v}" for k, v in sorted(over.items()))
    slug = name.lower().replace(" ", "-").replace(",", "").replace("(", "").replace(")", "")
    out = f"results/raw/r2/{group}__{slug}__{task}__s{seed}{'__' + tag if tag else ''}.json"
    cmd = ["rh", "run", "--kind", kind, "--name", name, "--group", group, "--task", task, "--seed", str(seed),
           "--config", json.dumps(cfg), "--metrics-file", out, "--",
           "nice", "-n", "10", PY, "method/run.py", "--system", system, "--task", task, "--seed", str(seed), "--out", out,
           "--beta", str(cfg["beta"]), "--offset", str(cfg["offset"]), "--K", str(cfg["K"]),
           "--warmup", str(cfg["warmup"]), "--clip", str(cfg["clip"])]
    return out, cmd


def jobs(which):
    js = []
    if which in ("pilot", "all"):  # seed outside the evaluation seeds: does anything find the reward without the offset?
        for name, system, over in [("Count bonus (state), no offset", "count_state", {"offset": 0.0}),
                                   ("Count bonus (obs), no offset", "count_obs", {"offset": 0.0}),
                                   ("RND bonus, no offset", "rnd", {"offset": 0.0}),
                                   ("RND, unguarded normaliser (v1), no offset", "rnd", {"offset": 0.0, "warmup": 0, "clip": 0.0}),
                                   ("Count bonus (state)", "count_state", {}), ("RND bonus", "rnd", {})]:
            for task in ["chain_40", "room_6"]:
                js.append(job("pilot", name, "sanity", system, over, task, 100))
    if which in ("main", "all"):
        for seed in SEEDS:
            for task in TASKS:
                for name, (kind, system, over) in MAIN.items():
                    js.append(job("main", name, kind, system, over, task, seed))
    if which in ("abl", "all"):  # RND normaliser variants; logged in group main next to the method rows
        for seed in SEEDS:
            for task in TASKS:
                for name, (kind, system, over) in ABL.items():
                    js.append(job("main", name, kind, system, over, task, seed))
    if which in ("sweeps", "all"):
        for seed in SEEDS:
            for beta in [0.03, 0.3, 1.0]:
                js.append(job("sweep_beta", "RND bonus", "method", "rnd", {"beta": beta}, "room_4", seed))
                js.append(job("sweep_beta", "Count bonus (state)", "baseline", "count_state", {"beta": beta}, "room_4", seed))
            for K in [1, 4, 64]:
                js.append(job("sweep_K", "RND bonus", "method", "rnd", {"K": K}, "room_4_tv", seed))
                js.append(job("sweep_K", "Count bonus (obs)", "baseline", "count_obs", {"K": K}, "room_4_tv", seed))
            for clip in [2.0, 20.0]:
                for task in ["chain_20", "room_4"]:
                    js.append(job("sweep_clip", "RND bonus", "method", "rnd", {"clip": clip}, task, seed))
    return js


def go(j):
    out, cmd = j
    if os.path.exists(out):
        return out, "skip"
    r = subprocess.run(cmd, capture_output=True, text=True)
    return out, "ok" if r.returncode == 0 and os.path.exists(out) else "FAILED " + (r.stdout + r.stderr)[-300:]


def copies():
    rows = [json.loads(l) for l in open("results/runs.jsonl")]
    dead = {}  # (group, name) -> line of the last supersede
    for i, r in enumerate(rows):
        if r.get("op") == "supersede": dead[(r["group"], r["name"])] = i
    live = [r for i, r in enumerate(rows) if "op" not in r and r.get("status") == "ok" and i > dead.get((r["group"], r["name"]), -1)]
    have = {(r["name"], r["task"], r["seed"]) for r in live if r["group"] == "offset_control"}
    for r in live:
        if r["group"] == "main" and r["name"] in ("Step penalty only (optimistic init)", "Count bonus (state)") \
                and (r["name"], r["task"], r["seed"]) not in have:
            subprocess.run(["rh", "log", "--kind", r["kind"], "--name", r["name"], "--group", "offset_control", "--task", r["task"],
                            "--seed", str(r["seed"]), "--from-run", r["run_id"]], check=True)


if __name__ == "__main__":
    if sys.argv[1:] == ["copies"]:
        copies(); sys.exit(0)
    js = jobs(sys.argv[1] if len(sys.argv) > 1 else "all")
    os.makedirs("results/raw/r2", exist_ok=True)
    with ThreadPoolExecutor(2) as ex:
        for i, (out, st) in enumerate(ex.map(go, js)):
            print(i + 1, len(js), st, out, flush=True)
