"""Derived statistics the paper reports, computed from results/runs.jsonl and logged through `rh run`
(one invocation = one registry row in group `derived`), so that no derived number is typed by hand.

  derive.py corr   --scope {all,no_collapsed,sam} --task <task|pooled> --out f.json
      Spearman correlation of the two sharpness measures with the two gaps over the evaluation-seed runs
      (groups main, sweep_rho, sweep_wd, abl_sam). Metrics: n_runs, rand_acc, rand_loss, adv_acc, adv_loss.
      scope sam = SAM runs only (pooled: the three digits tasks).
  derive.py paired --task <task> --baseline {SGD,SGD+WD} --out f.json
      SAM minus baseline on test_acc in group main: the per-seed differences (diff_seed<k>) and the Holm
      step-down adjustment of the paired t-test p-value over the 8 (task, baseline) comparisons (holm_p).
Deterministic: reads the registry only (rows of group `derived` are ignored)."""
import argparse, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr, ttest_rel

TASKS = ["digits_n0.0", "digits_n0.2", "digits_n0.4", "spirals_n0.2"]
EVAL_GROUPS = ("main", "sweep_rho", "sweep_wd", "abl_sam")

def load():
    R = [json.loads(l) for l in open("results/runs.jsonl")]
    R = [r for r in R if r.get("status") == "ok" and r["group"] in EVAL_GROUPS]
    return pd.DataFrame([dict(group=r["group"], name=r["name"], task=r["task"], seed=r["seed"], **r["metrics"]) for r in R])

def corr(a):
    df = load()
    df["collapsed"] = np.where(df.task.str.startswith("digits"), df.test_acc < a.collapse_digits, df.test_acc < a.collapse_spirals)
    if a.scope == "no_collapsed": df = df[~df.collapsed]
    if a.scope == "sam": df = df[(df.name == "SAM") & (df.task != "spirals_n0.2")]
    if a.task != "pooled": df = df[df.task == a.task]
    out = {"n_runs": len(df)}
    for s in ["sharp_rand", "sharp_adv"]:
        for g in ["gap_acc", "gap_loss"]:
            out[f"{s[6:]}_{g[4:]}"] = float(spearmanr(df[s], df[g])[0])
    return out

def paired(a):
    df = load(); df = df[df.group == "main"]
    def diffs(task, base):
        s = df[(df.task == task) & (df.name == "SAM")].sort_values("seed")
        b = df[(df.task == task) & (df.name == base)].sort_values("seed")
        assert list(s.seed) == list(b.seed)
        return list(s.seed), s.test_acc.to_numpy(float), b.test_acc.to_numpy(float)
    cells = [(t, b) for t in TASKS for b in ("SGD", "SGD+WD")]
    p = np.array([ttest_rel(*diffs(t, b)[1:]).pvalue for t, b in cells])
    o = np.argsort(p); m = len(o); adj = np.empty(m); run = 0.0      # Holm step-down
    for k, i in enumerate(o):
        run = max(run, min(1.0, (m - k) * p[i])); adj[i] = run
    seeds, sv, bv = diffs(a.task, a.baseline)
    out = {"holm_p": float(adj[cells.index((a.task, a.baseline))])}
    out.update({f"diff_seed{s}": float(x) for s, x in zip(seeds, sv - bv)})
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="what", required=True)
    c = sub.add_parser("corr"); c.add_argument("--scope", required=True, choices=["all", "no_collapsed", "sam"])
    c.add_argument("--task", required=True); c.add_argument("--collapse-digits", type=float, default=0.15)
    c.add_argument("--collapse-spirals", type=float, default=0.55); c.add_argument("--out", required=True)
    q = sub.add_parser("paired"); q.add_argument("--task", required=True)
    q.add_argument("--baseline", required=True, choices=["SGD", "SGD+WD"]); q.add_argument("--out", required=True)
    a = ap.parse_args()
    res = corr(a) if a.what == "corr" else paired(a)
    print("final", json.dumps(res), flush=True)
    json.dump(res, open(a.out, "w"))
