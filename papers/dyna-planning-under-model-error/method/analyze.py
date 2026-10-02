"""Sweep tables/figures built only from results/runs.jsonl (ok rows).
The tables hold no numbers: every cell is a \\rhval{<key>} macro that `rh paper build` fills from the registry."""
import json, collections, re
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
rows = [json.loads(l) for l in open("results/runs.jsonl")]
rows = [r for r in rows if r.get("status") == "ok" and r["kind"] != "sanity"]
def slug(s): return re.sub(r"[^a-z0-9_.+-]+", "-", str(s).lower()).strip("-")    # key parts as `rh values --list` prints them
def rv(group, name, task, metric, stat="mean", param=None, prec=1):
    return "\\rhval{%s/%s%s/%s/%s/%s:%d}" % (slug(group), slug(name), "@%s=%s" % (slug(param[0]), slug(param[1])) if param else "", slug(task), slug(metric), stat, prec)
def get(group, name, task, cfgkey, metric, seeds=None):
    d = collections.defaultdict(list)
    for r in rows:
        if r["group"] == group and r["name"] == name and r["task"] == task and (seeds is None or r["seed"] in seeds):
            d[r["config"].get(cfgkey)].append(r["metrics"][metric])
    return d
SYS = ["Dyna-Q", "Dyna-Q+", "Prioritized sweeping"]
NS = [1, 5, 20, 50, 100]
TASKS = ["static", "blocking", "shortcut", "stochastic", "stoch_blocking"]
def ms(x): return float(np.mean(x)), float(np.std(x, ddof=1) / np.sqrt(len(x)))
out = {}
for metric, fname in [("cum_reward", "sweep_n_cum"), ("post_reward", "sweep_n_post")]:
    fig, axs = plt.subplots(1, 5, figsize=(10, 2.1), sharex=True)
    for ax, task in zip(axs, TASKS):
        q = [r["metrics"][metric] for r in rows if r["group"] == "main" and r["name"] == "Q-learning" and r["task"] == task and r["seed"] < 10]
        qm, qs = ms(q)
        ax.axhline(qm, color="k", ls=":", lw=1, label="Q-learning (n=0)")
        for s, c in zip(SYS, ["#1b6ca8", "#d95f02", "#4d9a3c"]):
            d = get("sweep_n", s, task, "n", metric)
            m = [ms(d[n]) for n in NS]
            ax.errorbar(NS, [a for a, _ in m], [b for _, b in m], color=c, marker="o", ms=3, lw=1, capsize=2, label=s)
        ax.set_xscale("log"); ax.set_title(task.replace("_", " "), fontsize=8); ax.tick_params(labelsize=7)
        ax.set_xlabel("planning steps n", fontsize=7)
    axs[0].set_ylabel(metric.replace("_", " "), fontsize=7)
    axs[0].legend(fontsize=5.5)
    fig.tight_layout(); fig.savefig(f"results/figures/{fname}.pdf"); plt.close(fig)
# table: mean cum_reward / post_reward by n for each task
with open("results/tables/sweep_n_tab.tex", "w") as f:
    f.write("\\begin{tabular}{llrrrrrr}\n\\toprule\nTask & System & n=0 & n=1 & n=5 & n=20 & n=50 & n=100 \\\\\n\\midrule\n")
    for task in ["static", "blocking", "shortcut", "stochastic"]:
        for i, s in enumerate(SYS):
            qv = rv("sweep_n", "Q-learning", task, "cum_reward")    # Q-learning runs of seeds 0-9, listed in the sweep_n group
            lab = {"Prioritized sweeping": "PS"}.get(s, s)
            f.write(("\\multirow{3}{*}{%s}" % task.replace("_", " ") if i == 0 else "") + f" & {lab} & " + (("\\multirow{3}{*}{%s} & " % qv) if i == 0 else " & ") + " & ".join(rv("sweep_n", s, task, "cum_reward", param=("n", n)) for n in NS) + " \\\\\n")
        f.write("\\midrule\n" if task != "stochastic" else "")
    f.write("\\bottomrule\n\\end{tabular}\n")
with open("results/tables/sweep_n_post_tab.tex", "w") as f:
    f.write("\\begin{tabular}{llrrrrrr}\n\\toprule\nTask & System & n=0 & n=1 & n=5 & n=20 & n=50 & n=100 \\\\\n\\midrule\n")
    for task in ["blocking", "shortcut", "stoch_blocking"]:
        for i, s in enumerate(SYS):
            qv = rv("sweep_n", "Q-learning", task, "post_reward")    # Q-learning runs of seeds 0-9, listed in the sweep_n group
            lab = {"Prioritized sweeping": "PS"}.get(s, s)
            f.write(("\\multirow{3}{*}{%s}" % task.replace("_", " ") if i == 0 else "") + f" & {lab} & " + (("\\multirow{3}{*}{%s} & " % qv) if i == 0 else " & ") + " & ".join(rv("sweep_n", s, task, "post_reward", param=("n", n)) for n in NS) + " \\\\\n")
        f.write("\\midrule\n" if task != "stoch_blocking" else "")
    f.write("\\bottomrule\n\\end{tabular}\n")
# kappa sweep figure
fig, axs = plt.subplots(1, 3, figsize=(5, 1.9))
for ax, task, m in zip(axs, ["blocking", "shortcut", "stochastic"], ["post_reward", "post_reward", "cum_reward"]):
    d = get("sweep_kappa", "Dyna-Q+", task, "kappa", m); ks = sorted(d)
    mm = [ms(d[k]) for k in ks]
    ax.errorbar(range(len(ks)), [a for a, _ in mm], [b for _, b in mm], marker="o", ms=3, capsize=2, color="#d95f02")
    ax.set_xticks(range(len(ks))); ax.set_xticklabels([f"{k:g}" for k in ks], fontsize=6)
    ax.set_title(f"{task}: {m.replace('_',' ')}", fontsize=7); ax.set_xlabel("kappa", fontsize=7); ax.tick_params(labelsize=6)
fig.tight_layout(); fig.savefig("results/figures/sweep_kappa_fig.pdf")
print("ok")
# kappa table: Dyna-Q+ (n=10) mean over seeds 0-9; the last column is Dyna-Q on the same seeds (main runs listed in the sweep_kappa group)
with open("results/tables/sweep_kappa_tab.tex", "w") as f:
    f.write("\\begin{tabular}{lrrrrr}\n\\toprule\nTask (metric) & $10^{-4}$ & $10^{-3}$ & $10^{-2}$ & $3{\\cdot}10^{-2}$ & Dyna-Q \\\\\n\\midrule\n")
    for task, m in [("blocking", "post_reward"), ("shortcut", "post_reward"), ("static", "cum_reward"), ("stochastic", "cum_reward")]:
        cells = [rv("sweep_kappa", "Dyna-Q+", task, m, param=("kappa", k)) for k in (0.0001, 0.001, 0.01, 0.03)] + [rv("sweep_kappa", "Dyna-Q", task, m)]
        f.write(f"{task.replace('_',' ')} ({m.split('_')[0]}) & " + " & ".join(cells) + " \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")
# compact ablation table: post_reward mean (std), 20 seeds, n=10
with open("results/tables/abl_compact.tex", "w") as f:
    f.write("\\begin{tabular}{lccccc}\n\\toprule\nVariant & blocking & shortcut & static & stoch. & stoch.\\,blk \\\\\n\\midrule\n")
    for v in ["Dyna-Q+", "Dyna-Q+ w/o bonus", "Dyna-Q+ w/o untried", "Dyna-Q+ w/o both"]:
        cells = []
        for task in TASKS_ORDER if False else ["blocking", "shortcut", "static", "stochastic", "stoch_blocking"]:
            cells.append(rv("abl_dynaq_plus", v, task, "post_reward") + " (" + rv("abl_dynaq_plus", v, task, "post_reward", "std") + ")")
        f.write(v.replace("w/o", "w/o ") .replace("w/o  ", "w/o ") + " & " + " & ".join(cells) + " \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")
