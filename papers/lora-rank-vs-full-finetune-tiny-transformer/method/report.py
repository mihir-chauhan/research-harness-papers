"""Builds the custom tables and figures from results/runs.jsonl (all numbers come from the run registry).

The .tex tables hold no typed numbers: every cell is a \\rhval{<key>} macro (`rh values --list`), so the paper prints
what the registry recorded. The .md copies hold the same statistics as plain numbers for reading in the repository.
Ratios and paired tests are not computed here: they are the `rh compare` statistics (results/tables/compare_*.csv).
"""
import json, collections, re, numpy as np, matplotlib
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

def slug(s):   # key component, as in rh/numbers.py
    return re.sub(r"[^a-z0-9_.+-]+", "-", str(s).lower()).strip("-") or "x"

def key(group, name, task, metric, cfg=None):
    """Registry key of one (group, system, task, metric) cell; cfg=(param, value) selects one value of a swept setting."""
    at = f"@{slug(cfg[0])}={slug(cfg[1])}" if cfg else ""
    return f"{slug(group)}/{slug(name)}{at}/{slug(task)}/{slug(metric)}"

def rv(k, spec=""):
    return f"\\rhval{{{k}{':' + spec if spec else ''}}}"

def ms_tex(k, p=3):
    return f"{rv(k + '/mean', str(p))} $\\pm$ {rv(k + '/std', str(p))}"

class C(str):
    """A table cell: the plain text goes to the .md copy, `.tex` (an \\rhval macro) to the .tex table."""
    def __new__(cls, text, tex=None):
        c = super().__new__(cls, text); c.tex = text if tex is None else tex
        return c

def write(name, header, rows, align):
    tex = "\\begin{tabular}{" + align + "}\n\\toprule\n" + " & ".join(header) + " \\\\\n\\midrule\n"
    for r in rows:
        tex += " & ".join(getattr(x, "tex", x) for x in r) + " \\\\\n" if r != "mid" else "\\midrule\n"
    tex += "\\bottomrule\n\\end{tabular}\n"
    open(f"results/tables/{name}.tex", "w").write(tex)
    open(f"results/tables/{name}.md", "w").write("\n".join(" | ".join(str(x) for x in r) if r != "mid" else "---" for r in [header] + rows) + "\n")

CMP = {}
def cmp_stat(metric, name, task, stat):
    """A statistic of `rh compare --group main --metric <metric>` (the reference system is the one in the CSV)."""
    import pandas as pd
    if metric not in CMP: CMP[metric] = pd.read_csv(f"results/tables/compare_main_{metric}.csv")
    d = CMP[metric]; r = d[(d.name == name) & (d.task == task)].iloc[0]
    return {"delta": r["delta"], "paired_p": r["paired_p"], "inv_ratio": r["mean"] / r["ref_mean"], "ref": r["ref"]}[stat]

# ---- rank / parameter table (main group)
systems = ["Head only", "Last block", "From scratch", "Full fine-tuning", "LoRA r=1", "LoRA r=2", "LoRA r=4", "LoRA r=8"]
assert cmp_stat("trainable_params", "LoRA r=4", "reverse", "ref") == "Full fine-tuning"   # rh compare --metric trainable_params --ref "Full fine-tuning"
rows = []
for s in systems:
    p = vals("main", s, "reverse", "trainable_params")[0]
    a = [vals("main", s, t, "adapt_acc") for t in TASKS]
    k = [key("main", s, t, "adapt_acc") for t in TASKS]
    nfail = sum(x < 0.5 for x in a[1])
    share = C("100.0") if s == "Full fine-tuning" else C(f"{100 * cmp_stat('trainable_params', s, 'reverse', 'inv_ratio'):.1f}",
                                                         rv(f"cmp/main/{slug(s)}/reverse/trainable_params/inv_ratio", "pct1"))
    rows.append([s, C(f"{int(p)}", rv(key("main", s, "reverse", "trainable_params") + "/mean")), share,
                 C(ms(a[0]), ms_tex(k[0])), C(f"{np.min(a[0]):.3f}", rv(k[0] + "/min", "3")),
                 C(ms(a[1]), ms_tex(k[1])), C(f"{np.min(a[1]):.3f}", rv(k[1] + "/min", "3")), f"{nfail}/5"])
write("tab_rank", ["System", "Params", "\\% full", "sort\\_desc", "min", "reverse", "min", "fail"], rows, "lrrccccr")

# ---- target modules ablation
rows = []
for k in [1, 4]:
    for lab, g, nm in [("all linear", "main", f"LoRA r={k}"), ("q,v only", "abl_targets", f"LoRA r={k} (q,v only)")]:
        p = vals(g, nm, "reverse", "trainable_params")[0]
        a = [vals(g, nm, t, "adapt_acc") for t in TASKS]
        rows.append([str(k), lab, C(f"{int(p)}", rv(key(g, nm, "reverse", "trainable_params") + "/mean"))]
                    + [C(ms(a[i]), ms_tex(key(g, nm, t, "adapt_acc"))) for i, t in enumerate(TASKS)])
write("tab_targets", ["Rank", "Targets", "Params", "sort\\_desc acc", "reverse acc"], rows, "llrcc")

# ---- training-set size sweep (sort_desc), seeds 0-2; the N=2000 runs are the main group (five seeds, Table main)
SD = [0, 1, 2]
names = [("Full fine-tuning", "Full fine-tuning"), ("From scratch", "From scratch"), ("Last block", "Last block"),
         ("LoRA r=1", "LoRA r=1"), ("LoRA r=4", "LoRA r=4"), ("LoRA r=8", "LoRA r=8")]
rows = []
for lab, nm in names:
    rows.append([lab] + [C(ms(vals("sweep_ntrain", nm, "sort_desc", "adapt_acc", lambda c, n=n: c["n_train"] == n)),
                           ms_tex(key("sweep_ntrain", nm, "sort_desc", "adapt_acc", ("n_train", n)))) for n in (100, 300)])
write("tab_ntrain", ["System", "$N$=100", "$N$=300"], rows, "lcc")

# ---- lr sweep
lrs = {"Full fine-tuning": [3e-4, 1e-3, 3e-3, 1e-2], "LoRA r=4": [3e-4, 1e-3, 3e-3, 1e-2, 3e-2]}
default = {"Full fine-tuning": 1e-2, "LoRA r=4": 3e-2}
def lr_vals(nm, t, lr, key="adapt_acc"):
    if lr == default[nm]:
        return vals("main", nm, t, key, seeds=SD)
    return vals("sweep_lr", nm, t, key, lambda c: abs(c["lr"] - lr) < 1e-12)
rows = []   # table: the swept rates only (group sweep_lr); the default rate of each system is the main group (Table main)
for nm in lrs:
    for lr in lrs[nm]:
        if lr == default[nm]: continue
        rows.append([nm, f"{lr:g}"] + [C(ms(lr_vals(nm, t, lr)), ms_tex(key("sweep_lr", nm, t, "adapt_acc", ("lr", lr)))) for t in TASKS]
                    + [C(ms(lr_vals(nm, "reverse", lr, "pretask_acc")), ms_tex(key("sweep_lr", nm, "reverse", "pretask_acc", ("lr", lr))))])
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

# ---- paired tests over seeds: the statistics of `rh compare --group main --metric <metric>` (reference LoRA r=4)
rows = []
for b, metric in [("Full fine-tuning", "adapt_acc"), ("Last block", "adapt_acc"), ("From scratch", "adapt_acc"), ("Full fine-tuning", "pretask_acc")]:
    for t in TASKS:
        a = cmp_stat(metric, b, t, "ref")
        d, p = cmp_stat(metric, b, t, "delta"), cmp_stat(metric, b, t, "paired_p")
        k = f"cmp/main/{slug(b)}/{slug(t)}/{slug(metric)}"
        rows.append([a, b, metric.replace("_", "\\_"), t.replace("_", "\\_"), C(f"{d:.4f}", rv(k + "/delta", "4")),
                     C("n/a" if np.isnan(p) else f"{p:.4g}", rv(k + "/paired_p"))])
write("tab_tests", ["A", "B", "metric", "task", "mean A$-$B", "paired $p$"], rows, "lllllr")
