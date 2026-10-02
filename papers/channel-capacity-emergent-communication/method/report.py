"""Build paper tables/figures from results/runs.jsonl (main core tasks and the two sweeps, selected by tag)."""
import json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
rows = [json.loads(l) for l in open("results/runs.jsonl")]
rows = [r for r in rows if r["status"] == "ok" and r["group"] == "main"]
df = pd.DataFrame([{**r["metrics"], "name": r["name"], "task": r["task"], "seed": r["seed"],
                    "tag": (r["tags"] or [""])[0]} for r in rows])
CORE = ["V4_L4", "V8_L4", "V16_L8"]
SYS = ["Gumbel-softmax sender-receiver", "REINFORCE sender (reimplemented)", "Random code (reference)", "Oracle compositional code (reference)"]
SHORT = {SYS[0]: "Gumbel", SYS[1]: "REINFORCE", SYS[2]: "Random code", SYS[3]: "Oracle code"}
ms = lambda s: f"{s.mean():.3f} $\\pm$ {s.std(ddof=1):.3f}"

def table(sub, key, cols, labels, path):
    out = ["\\begin{tabular}{l" + "c" * len(cols) + "}", "\\toprule", key[1] + " & " + " & ".join(labels) + " \\\\", "\\midrule"]
    md = ["| " + key[1] + " | " + " | ".join(cols) + " |", "|" + "---|" * (len(cols) + 1)]
    for k, g in sub:
        cells = [ms(g[c]) for c in cols]
        out.append(f"{k.replace('_','\\_')} & " + " & ".join(cells) + " \\\\")
        md.append(f"| {k} | " + " | ".join(c.replace(" $\\pm$ ", " ± ") for c in cells) + " |")
    out += ["\\bottomrule", "\\end{tabular}"]
    open(path + ".tex", "w").write("\n".join(out) + "\n"); open(path + ".md", "w").write("\n".join(md) + "\n")

core = df[df.task.isin(CORE) & (df.tag == "")]
items = []
for t in CORE:
    for s in SYS:
        g = core[(core.task == t) & (core.name == s)]
        items.append((f"{t} {SHORT[s]}", g))
table(items, (0, "Task / system"), ["heldout_acc", "train_acc", "topsim", "gen_gap"], ["held-out", "train", "topsim", "gap"], "results/tables/main_core")
for tag, key in [("sweep_vocab", "V"), ("sweep_length", "L")]:
    sub = df[df.tag == tag]
    order = sorted(sub.task.unique(), key=lambda t: int(t.split("_")[0][1:]) if key == "V" else int(t.split("_")[1][1:]))
    table([(t, sub[sub.task == t]) for t in order], (0, "Task"), ["heldout_acc", "train_acc", "topsim", "n_unique_messages"],
          ["held-out", "train", "topsim", "unique msgs"], f"results/tables/{tag}")
    sub = sub.assign(x=sub.task.map(lambda t: int(t.split("_")[0][1:]) if key == "V" else int(t.split("_")[1][1:])))
    fig, ax = plt.subplots(figsize=(3.4, 2.4))
    for m, lab in [("train_acc", "train acc"), ("heldout_acc", "held-out acc"), ("topsim", "topsim")]:
        g = sub.groupby("x")[m].agg(["mean", "std"])
        ax.errorbar(g.index, g["mean"], yerr=g["std"], marker="o", capsize=2, label=lab)
    ax.set_xlabel("vocabulary size V (L=5)" if key == "V" else "message length L (V=6)"); ax.set_xscale("log", base=2) if key == "V" else None
    ax.legend(fontsize=7); ax.set_ylim(-0.05, 1.05); fig.tight_layout(); fig.savefig(f"results/figures/{tag}_all.pdf"); plt.close(fig)

fig, axs = plt.subplots(1, 2, figsize=(3.4, 2.3))
for ax, m in zip(axs, ["heldout_acc", "topsim"]):
    for i, s in enumerate(SYS):
        g = core[core.name == s].groupby("task")[m].agg(["mean", "std"]).reindex(CORE)
        ax.bar(np.arange(3) + i * 0.2 - 0.3, g["mean"], 0.2, yerr=g["std"], capsize=1.5, label=SHORT[s])
    ax.set_xticks(range(3)); ax.set_xticklabels(["V4L4", "V8L4", "V16L8"], fontsize=6); ax.set_title(m, fontsize=8)
axs[0].legend(fontsize=5); fig.tight_layout(); fig.savefig("results/figures/main_bars.pdf")
