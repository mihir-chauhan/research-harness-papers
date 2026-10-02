"""Paper version of the main table: results/tables/main.tex (written by `rh table`) -> results/tables/main_paper.tex.
Only the presentation changes (readable headers, plain row labels, tie-aware marks); every number is the string
that `rh table` printed. Marks: bold = every cell whose printed mean equals the best of its scenario and column;
underline = the runner-up value, only when the best is not tied.
"""
import re
HEAD = {r"average\_accuracy": "Avg. accuracy", "forgetting": "Forgetting", r"backward\_transfer": "Backward transfer",
        r"last\_task\_accuracy": "Last-task acc.", "$n$": "Seeds", "Task": "Scenario"}
src = open("results/tables/main.tex").read().splitlines()
strip = lambda c: re.sub(r"\\(textbf|underline)\{(.*)\}", r"\2", c.strip())
out, block, higher = [], [], []
def flush():
    for col in range(2, len(block[0]) - 1):
        vals = [float(r[col].split()[0]) for r in block]
        order = sorted(set(vals), reverse=higher[col - 2])
        for r, v in zip(block, vals):
            if v == order[0]:
                r[col] = r"\textbf{%s}" % r[col]
            elif len(order) > 1 and v == order[1] and vals.count(order[0]) == 1:
                r[col] = r"\underline{%s}" % r[col]
    out.extend(" & ".join(r) + r" \\" for r in block)
    block.clear()
for line in src:
    if line.startswith("Method &"):
        cells = [c.strip() for c in line.rstrip("\\ ").split("&")]
        higher = [r"\uparrow" in c for c in cells[2:-1]]
        new = []
        for c in cells:
            name, arrow = (c.rsplit(" ", 1) + [""])[:2] if "arrow" in c else (c, "")
            new.append((HEAD.get(name, name) + " " + arrow).strip())
        out.append(" & ".join(new) + r" \\")
    elif "&" in line:
        block.append([strip(c) for c in line.rstrip("\\ ").split("&")])
    else:
        if block: flush()
        out.append(line)
text = re.sub(r"(?<![\d.])(?<!\^\{)-(\d)", r"$-$\1", "\n".join(out) + "\n")  # typeset minus signs
open("results/tables/main_paper.tex", "w").write(text)
print(text)

# Two small tables read straight from the run registry (active rows only): learning-rate selection (validation
# accuracy, seeds 100-101) and last-task accuracy of the sweeps (seeds 10-14).
import numpy as np
import sys; sys.path.insert(0, "experiments")
from registry import active_runs
runs = active_runs()
TASKS = ["perm_dil", "split_cil", "split_til"]
tex = lambda t: t.replace("_", r"\_")
def cell(group, name, task, metric, n, key=None, val=None):
    v = [r["metrics"][metric] for r in runs if r["group"] == group and r["name"] == name and r["task"] == task
         and (key is None or r["config"][key] == val)]
    assert len(v) == n, (group, name, task, key, val, len(v))
    return f"{np.mean(v):.3f} $\\pm$ {np.std(v, ddof=1):.3f}"
out = [r"\begin{tabular}{llccc}", r"\toprule", "System & lr & " + " & ".join(tex(t) for t in TASKS) + r" \\", r"\midrule"]
for name in ("Fine-tuning", "Joint training"):
    for lr in (0.01, 0.05, 0.1):
        out.append(f"{name} & {lr} & " + " & ".join(cell("tune_lr", f"{name} lr{lr}", t, "val_average_accuracy", 2) for t in TASKS) + r" \\")
out += [r"\bottomrule", r"\end{tabular}"]
open("results/tables/tune_lr_paper.tex", "w").write("\n".join(out) + "\n")
out = [r"\begin{tabular}{lccc}", r"\toprule", "Setting & " + " & ".join(tex(t) for t in TASKS) + r" \\", r"\midrule"]
for g, nm, key, sym, ks in [("sweep_buffer", "Experience replay", "buffer", "M", [0, 20, 100, 500]),
                            ("sweep_lambda", "EWC", "lam", r"\lambda", [0, 1, 10, 100, 1000, 10000, 100000])]:
    for k in ks:
        out.append(f"${sym}={k}$ & " + " & ".join(cell(g, nm, t, "last_task_accuracy", 5, key, k) for t in TASKS) + r" \\")
    if sym == "M": out.append(r"\midrule")
out += [r"\bottomrule", r"\end{tabular}"]
open("results/tables/sweep_lasttask.tex", "w").write("\n".join(out) + "\n")
print("\n".join(out))
