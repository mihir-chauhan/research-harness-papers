"""Job lists of every run group in the paper. Usage (from the project root, after sourcing the environment):
    $PY experiments/jobs.py {tune_lr|sweeps|main} [--dry-run] [--resume]
--dry-run prints the `rh run` commands instead of executing them.
--resume skips jobs that already have an active row in results/runs.jsonl (after an interrupted driver).

tune_lr : Fine-tuning and Joint training at lr in {0.01, 0.05, 0.1}, seeds 100-101 (learning-rate selection).
sweeps  : ER buffer size M and EWC strength lambda, seeds 10-14 (groups sweep_buffer, sweep_lambda).
main    : five systems, seeds 0-4; EWC uses the lambda with the best mean validation accuracy in sweep_lambda.
"""
import sys, shlex
sys.path.insert(0, "experiments")
from drive import TASKS, command, run

LRS = [0.01, 0.05, 0.1]
BUFFERS = [0, 5, 10, 20, 50, 100, 200, 500]
LAMBDAS = [0, 1, 10, 100, 1000, 10000, 100000]
LAMBDA_STAR = {"perm_dil": 10, "split_cil": 1000, "split_til": 1000}  # argmax mean val_average_accuracy, sweep_lambda


def tune_lr():
    jobs = []
    for lr in LRS:
        for name, system in (("Fine-tuning", "finetune"), ("Joint training", "joint")):
            for task in TASKS:
                for seed in (100, 101):
                    jobs.append(("tune_lr", "baseline", f"{name} lr{lr}", task, seed, ["--system", system, "--lr", str(lr)], {"lr": lr}))
    return jobs


def sweeps():
    # config value outermost, so that neighbouring jobs never share a log-file stem (group, name, task, seed)
    jobs = []
    for i in range(max(len(BUFFERS), len(LAMBDAS))):
        for task in TASKS:
            for seed in range(10, 15):
                if i < len(LAMBDAS):
                    jobs.append(("sweep_lambda", "ablation", "EWC", task, seed, ["--system", "ewc", "--lam", str(LAMBDAS[i])], {"lam": LAMBDAS[i]}))
                if i < len(BUFFERS):
                    jobs.append(("sweep_buffer", "ablation", "Experience replay", task, seed, ["--system", "replay", "--buffer", str(BUFFERS[i])], {"buffer": BUFFERS[i]}))
    return jobs


def main():
    jobs = []
    for task in TASKS:
        for seed in range(5):
            lam = LAMBDA_STAR[task]
            jobs += [("main", "baseline", "Fine-tuning", task, seed, ["--system", "finetune"], {}),
                     ("main", "baseline", "EWC", task, seed, ["--system", "ewc", "--lam", str(lam)], {"lam": lam}),
                     ("main", "baseline", "Joint training", task, seed, ["--system", "joint"], {}),
                     ("main", "baseline", "Experience replay (M=20)", task, seed, ["--system", "replay", "--buffer", "20"], {"buffer": 20}),
                     ("main", "method", "Experience replay (M=100)", task, seed, ["--system", "replay", "--buffer", "100"], {"buffer": 100})]
    return jobs


if __name__ == "__main__":
    jobs = {"tune_lr": tune_lr, "sweeps": sweeps, "main": main}[sys.argv[1]]()
    if "--resume" in sys.argv:
        from registry import active_runs
        done = {(r["group"], r["name"], r["task"], r["seed"], tuple(r["config"].items())) for r in active_runs()}
        jobs = [j for j in jobs if (j[0], j[2], j[3], j[4], tuple(j[6].items())) not in done]
        print(len(jobs), "jobs left", flush=True)
    if "--dry-run" in sys.argv:
        for j in jobs:
            print(shlex.join(command(*j)[1]))
    else:
        run(jobs)
