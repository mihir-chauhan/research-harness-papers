"""Builds the custom tables and figures from results/runs.jsonl (all numbers come from the run registry)."""
import json, collections, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = [json.loads(l) for l in open("results/runs.jsonl") if l.strip()]
R = [r for r in R if r["status"] == "ok"]
TASKS = ["sort_desc", "reverse"]

def vals(group, name, task, key, cond=lambda c: True, seeds=None):
    return [r["metrics"][key] for r in R if r["group"] == group and r["name"] == name and r["task"] == task
            and cond(r["config"]) and (seeds is None or r["seed"] in seeds)]

def ms(v, p=3):
    return f"{np.mean(v):.{p}f} $\\pm$ {np.std(v, ddof=1):.{p}f}"

def write(name, header, rows, align):
    tex = "\\begin{tabular}{" + align + "}\n\\toprule\n" + " & ".join(header) + " \\\\\n\\midrule\n"
    for r in rows:
        tex += " & ".join(r) + " \\\\\n" if r != "mid" else "\\midrule\n"
    tex += "\\bottomrule\n\\end{tabular}\n"
    open(f"results/tables/{name}.tex", "w").write(tex)
    open(f"results/tables/{name}.md", "w").write("\n".join(" | ".join(x for x in r) if r != "mid" else "---" for r in [header] + rows) + "\n")

# ---- rank / parameter table (main group)
systems = ["Head only", "Last block", "From scratch", "Full fine-tuning", "LoRA r=1", "LoRA r=2", "LoRA r=4", "LoRA r=8"]
full_p = vals("main", "Full fine-tuning", "reverse", "trainable_params")[0]
rows = []
for s in systems:
    p = vals("main", s, "reverse", "trainable_params")[0]
    a = [vals("main", s, t, "adapt_acc") for t in TASKS]
    nfail = sum(x < 0.5 for x in a[1]) 
    rows.append([s, f"{int(p)}", f"{100 * p / full_p:.1f}", ms(a[0]), f"{np.min(a[0]):.3f}", ms(a[1]), f"{np.min(a[1]):.3f}", f"{nfail}/5"])
write("tab_rank", ["System", "Params", "\\% full", "sort\\_desc", "min", "reverse", "min", "fail"], rows, "lrrccccr")

# ---- target modules ablation
rows = []
for k in [1, 4]:
    for lab, g, nm in [("all linear", "main", f"LoRA r={k}"), ("q,v only", "abl_targets", f"LoRA r={k} (q,v only)")]:
        p = vals(g, nm, "reverse", "trainable_params")[0]
        a = [vals(g, nm, t, "adapt_acc") for t in TASKS]
        rows.append([str(k), lab, f"{int(p)}", ms(a[0]), ms(a[1])])
write("tab_targets", ["Rank", "Targets", "Params", "sort\\_desc acc", "reverse acc"], rows, "llrcc")

# ---- training-set size sweep (sort_desc), seeds 0-2 for every cell
SD = [0, 1, 2]
names = [("Full fine-tuning", "Full fine-tuning"), ("From scratch", "From scratch"), ("Last block", "Last block"),
         ("LoRA r=1", "LoRA r=1"), ("LoRA r=4", "LoRA r=4"), ("LoRA r=8", "LoRA r=8")]
rows = []
for lab, nm in names:
    rows.append([lab] + [ms(vals("sweep_ntrain", nm, "sort_desc", "adapt_acc", lambda c, n=n: c["n_train"] == n)) for n in (100, 300)]
                + [ms(vals("main", nm, "sort_desc", "adapt_acc", seeds=SD))])
write("tab_ntrain", ["System", "$N$=100", "$N$=300", "$N$=2000"], rows, "lccc")

# ---- lr sweep
lrs = {"Full fine-tuning": [3e-4, 1e-3, 3e-3, 1e-2], "LoRA r=4": [3e-4, 1e-3, 3e-3, 1e-2, 3e-2]}
default = {"Full fine-tuning": 1e-2, "LoRA r=4": 3e-2}
def lr_vals(nm, t, lr, key="adapt_acc"):
    if lr == default[nm]:
        return vals("main", nm, t, key, seeds=SD)
    return vals("sweep_lr", nm, t, key, lambda c: abs(c["lr"] - lr) < 1e-12)
rows = []
for nm in lrs:
    for lr in lrs[nm]:
        rows.append([nm, f"{lr:g}"] + [ms(lr_vals(nm, t, lr)) for t in TASKS] + [ms(lr_vals(nm, "reverse", lr, "pretask_acc"))])
write("tab_lr", ["System", "LR", "sort\\_desc", "reverse", "reverse retention"], rows, "llccc")
fig, ax = plt.subplots(1, 2, figsize=(5.4, 2.1), sharey=True)
for i, t in enumerate(TASKS):
    for nm, c in [("Full fine-tuning", "#1f77b4"), ("LoRA r=4", "#d95f02")]:
        m = [np.mean(lr_vals(nm, t, lr)) for lr in lrs[nm]]; s = [np.std(lr_vals(nm, t, lr), ddof=1) for lr in lrs[nm]]
        ax[i].errorbar(lrs[nm], m, yerr=s, marker="o", ms=3, capsize=2, color=c, label=nm)
    ax[i].set_xscale("log"); ax[i].set_title(t.replace("_", " "), fontsize=8); ax[i].set_xlabel("learning rate", fontsize=8)
    ax[i].tick_params(labelsize=7)
ax[0].set_ylabel("exact-match accuracy", fontsize=8); ax[0].legend(fontsize=6)
plt.tight_layout(); plt.savefig("results/figures/lr_sweep.pdf"); plt.close()

# ---- accuracy vs trainable parameters (main)
fig, ax = plt.subplots(1, 2, figsize=(5.4, 2.4))
for i, t in enumerate(TASKS):
    for s in systems:
        if s == "From scratch": continue
        p = vals("main", s, t, "trainable_params")[0]; a = vals("main", s, t, "adapt_acc")
        mk = "s" if s.startswith("LoRA") is False else "o"
        ax[i].scatter([p] * len(a), a, s=8, alpha=0.6, marker=mk, color="#d95f02" if s.startswith("LoRA") else "#1f77b4")
        off = {"Full fine-tuning": -0.2, "Last block": -0.2, "Head only": 0.1, "LoRA r=1": 0.1 if t == "sort_desc" else -0.2}.get(s, 0.08)
        lab = {"Full fine-tuning": "full", "Last block": "last blk", "Head only": "head"}.get(s, s.replace("LoRA ", ""))
        ax[i].text(p, (0.9 if t == "sort_desc" and off > 0 and s.startswith("LoRA") else np.mean(a)) + off if False else min(np.mean(a), 1.0) + off, lab, fontsize=6, ha="center")
    ax[i].set_xscale("log"); ax[i].set_title(t.replace("_", " "), fontsize=8); ax[i].set_xlabel("trainable parameters", fontsize=8)
    ax[i].tick_params(labelsize=7); ax[i].set_ylim(-0.1, 1.15)
ax[0].set_ylabel("exact-match accuracy (per seed)", fontsize=8)
plt.tight_layout(); plt.savefig("results/figures/acc_vs_params.pdf"); plt.close()
print("ok")

# ---- adaptation / retention curves (sort_desc, seeds 0-2) from results/raw/curve_*.csv
import glob, pandas as pd
d = pd.concat([pd.read_csv(f) for f in glob.glob("results/raw/curve_*.csv")])
d["sys"] = d.name.str.replace(r" \(.*\)", "", regex=True); d["kind"] = d.name.str.extract(r"\((.*)\)")[0]
fig, ax = plt.subplots(1, 2, figsize=(5.4, 2.1), sharey=True)
for j, (kind, title) in enumerate([("target", "sort desc (target task)"), ("sort_asc retention", "sort asc (pretraining task)")]):
    for sy, lab in [("full", "full FT"), ("lora-r1", "LoRA r=1"), ("lora-r4", "LoRA r=4"), ("lastblock", "last block")]:
        g = d[(d.sys == sy) & (d.kind == kind)].groupby("step").value
        ax[j].plot(g.mean().index, g.mean().values, label=lab, lw=1.2)
        ax[j].fill_between(g.mean().index, g.min().values, g.max().values, alpha=0.15)
    ax[j].set_title(title, fontsize=8); ax[j].set_xlabel("adaptation step", fontsize=8); ax[j].tick_params(labelsize=7)
ax[0].set_ylabel("exact match (500 test seqs)", fontsize=8); ax[0].legend(fontsize=6, loc="lower right")
plt.tight_layout(); plt.savefig("results/figures/curves_custom.pdf"); plt.close()
# first step at which target accuracy >= 0.9 (mean curve)
for sy in ["full", "lora-r1", "lora-r4", "lastblock"]:
    g = d[(d.sys == sy) & (d.kind == "target")].groupby("step").value.mean()
    print(sy, "first step with mean target acc >= 0.9:", g[g >= 0.9].index.min())

# ---- paired tests over seeds (same as `rh compare`: scipy paired t-test on per-seed values)
from scipy import stats
def seedvec(name, task, key="adapt_acc"):
    d = {r["seed"]: r["metrics"][key] for r in R if r["group"] == "main" and r["name"] == name and r["task"] == task}
    return np.array([d[s] for s in sorted(d)])
rows = []
for a, b, key in [("LoRA r=4", "Full fine-tuning", "adapt_acc"), ("LoRA r=4", "Last block", "adapt_acc"), ("LoRA r=1", "LoRA r=8", "adapt_acc"),
                  ("LoRA r=4", "From scratch", "adapt_acc"), ("LoRA r=4", "Full fine-tuning", "pretask_acc")]:
    for t in TASKS:
        x, y = seedvec(a, t, key), seedvec(b, t, key)
        p = stats.ttest_rel(x, y).pvalue
        rows.append([a, b, key.replace("_", "\\_"), t.replace("_", "\\_"), f"{np.mean(x) - np.mean(y):+.4f}", "n/a" if np.isnan(p) else f"{p:.3g}"])
write("tab_tests", ["A", "B", "metric", "task", "mean A$-$B", "paired $p$"], rows, "lllllr")
