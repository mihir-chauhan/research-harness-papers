"""Summarise V4_L4 train-accuracy curves (results/raw/curve_*.csv) into results/tables/curve_summary.tex."""
import pandas as pd
rows = []
for sysn, lab in (("gumbel", "Gumbel"), ("reinforce", "REINFORCE")):
    for s in range(3):
        d = pd.read_csv(f"results/raw/curve_{sysn}_V4_L4_s{s}.csv")
        i = d.value.idxmax()
        v = lambda t: d[d.step == t].value.iloc[0]
        rows.append((lab, s, d.value.max(), int(d.step[i]), v(6000), v(19999)))
t = "\\begin{tabular}{llrrrr}\n\\hline\nSystem & Seed & Peak & Peak step & @6000 & @20000\\\\\n\\hline\n"
for r in rows:
    t += f"{r[0]} & {r[1]} & {r[2]:.3f} & {r[3]} & {r[4]:.3f} & {r[5]:.3f}\\\\\n"
t += "\\hline\n\\end{tabular}\n"
open("results/tables/curve_summary.tex", "w").write(t)

# longer-training control table (20000 steps), short names, from the run registry
import json
import numpy as np
rr = [json.loads(l) for l in open("results/runs.jsonl")]
rr = [r for r in rr if r["group"] == "abl_longtrain" and r["status"] == "ok"]
t = "\\begin{tabular}{lrrrr}\n\\hline\nSystem & train & held-out & topsim & msgs\\\\\n\\hline\n"
for key, lab in (("Gumbel", "Gumbel"), ("REINFORCE", "REINFORCE")):
    m = {k: [r["metrics"][k] for r in rr if r["name"].startswith(key)] for k in ("train_acc", "heldout_acc", "topsim", "n_unique_messages")}
    f = lambda k, p: f"{np.mean(m[k]):.{p}f} $\\pm$ {np.std(m[k], ddof=1):.{p}f}"
    t += f"{lab} & {f('train_acc',3)} & {f('heldout_acc',3)} & {f('topsim',3)} & {f('n_unique_messages',1)}\\\\\n"
t += "\\hline\n\\end{tabular}\n"
open("results/tables/longtrain_short.tex", "w").write(t)
