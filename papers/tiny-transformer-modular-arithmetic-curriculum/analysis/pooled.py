"""Pooled 7-seed check at the main cell (seeds 0-4 from group main, 5-6 from group curves) and the Fig. 2 curves."""
import json, numpy as np, csv
from scipy import stats
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = [json.loads(l) for l in open("results/runs.jsonl")]
R = [r for r in R if r["status"] == "ok" and r["task"] == "wd1_f0.5" and r["group"] in ("main", "curves")]
SYS = ["Uniform sampling", "Operand-size curriculum", "Anti-curriculum"]
def get(s, m, groups):
    d = {r["seed"]: r["metrics"][m] for r in R if r["name"] == s and r["group"] in groups}
    return [d[k] for k in sorted(d)]
def row(s, g):
    v = get(s, "steps_to_95", g); rc = get(s, "reached", g)
    return v, f"{np.mean(v):.0f} $\\pm$ {np.std(v, ddof=1):.0f} & {int(round(sum(rc)))}/{len(v)}"
with open("results/tables/pooled7.tex", "w") as fh:
    fh.write("\\begin{tabular}{lcccc}\n\\toprule\n & \\multicolumn{2}{c}{seeds 0--4 (registered)} & \\multicolumn{2}{c}{seeds 5--6 only} \\\\\nSystem & steps\\_to\\_95 & reached & steps\\_to\\_95 & reached \\\\\n\\midrule\n")
    for s in SYS:
        fh.write(f"{s} & {row(s,('main',))[1]} & {row(s,('curves',))[1]} \\\\\n")
    fh.write("\\midrule\n & \\multicolumn{2}{c}{pooled, 7 seeds (post hoc)} & Welch $p$ & paired $p$ \\\\\n\\midrule\n")
    u = get(SYS[0], "steps_to_95", ("main", "curves")); c = get(SYS[1], "steps_to_95", ("main", "curves"))
    for s in SYS:
        v, txt = row(s, ("main", "curves"))
        if s == SYS[0]: ps = " & "
        elif s == SYS[1]:
            ps = f"{stats.ttest_ind(c, u, equal_var=False).pvalue:.2f} & {stats.ttest_rel(c, u).pvalue:.2f}"
        else:
            ps = f"{stats.ttest_ind(v, u, equal_var=False).pvalue:.2f} & {stats.ttest_rel(v, u).pvalue:.2f}"
        fh.write(f"{s} & {txt} & {ps} \\\\\n")
    fh.write("\\bottomrule\n\\end{tabular}\n")
print(open("results/tables/pooled7.tex").read())
col = {"uniform": "#4c78a8", "curriculum": "#e45756", "anticurriculum": "#72b7b2"}
lab = {"uniform": "Uniform sampling", "curriculum": "Operand-size curriculum", "anticurriculum": "Anti-curriculum"}
fig, ax = plt.subplots(figsize=(3.4, 2.4))
for k in col:
    runs = []
    for sd in (5, 6):
        rr = list(csv.DictReader(open(f"results/raw/curve_{k}_s{sd}.csv"))); runs.append({int(float(x["step"])): float(x["value"]) for x in rr})
    steps = sorted(set().union(*[r.keys() for r in runs]))
    mean = [np.mean([r[s] for r in runs if s in r]) for s in steps]
    lo = [min(r[s] for r in runs if s in r) for s in steps]; hi = [max(r[s] for r in runs if s in r) for s in steps]
    ax.plot(steps, mean, c=col[k], label=lab[k], lw=1); ax.fill_between(steps, lo, hi, color=col[k], alpha=.15)
ax.set_xlabel("step", fontsize=7); ax.set_ylabel("held-out accuracy", fontsize=7); ax.tick_params(labelsize=7); ax.legend(fontsize=6)
plt.tight_layout(); plt.savefig("results/figures/curves_main.pdf")
