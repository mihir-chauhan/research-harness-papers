"""Pooled 7-seed check at the main cell and the Fig. 2 curves.
Seeds 0-4 are group main, 5-6 group curves; group pooled7 holds copies of these 21 runs (rh log --from-run), so every
number in the table is a registry value (\rhval key, see `rh values --list --group pooled7`). The anti-curriculum vs
uniform p-values are read from results/tables/compare_pooled7_steps_to_95_ref_uniform.csv, written by
`rh compare --group pooled7 --metric steps_to_95 --ref "Uniform sampling"`; nothing is computed here."""
import json, numpy as np, csv
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = [json.loads(l) for l in open("results/runs.jsonl")]
R = [r for r in R if r["status"] == "ok" and r["task"] == "wd1_f0.5" and r["group"] in ("main", "curves", "pooled7")]
SYS = ["Uniform sampling", "Operand-size curriculum", "Anti-curriculum"]
T = "wd1_f0.5"
slug = lambda s: s.lower().replace(" ", "-")
def row(s, g):
    rc = [r["metrics"]["reached"] for r in R if r["name"] == s and r["group"] == g]
    k = f"{g}/{slug(s)}/{T}/steps_to_95"
    return f"\\rhval{{{k}/mean:0}} $\\pm$ \\rhval{{{k}/std:0}} & {int(round(sum(rc)))}/{len(rc)}"
ref = {r["name"]: r for r in csv.DictReader(open("results/tables/compare_pooled7_steps_to_95_ref_uniform.csv")) if r["task"] == T}
with open("results/tables/pooled7.tex", "w") as fh:
    fh.write("\\begin{tabular}{lcccc}\n\\toprule\n & \\multicolumn{2}{c}{seeds 0--4 (registered)} & \\multicolumn{2}{c}{seeds 5--6 only} \\\\\nSystem & steps\\_to\\_95 & reached & steps\\_to\\_95 & reached \\\\\n\\midrule\n")
    for s in SYS:
        fh.write(f"{s} & {row(s, 'main')} & {row(s, 'curves')} \\\\\n")
    fh.write("\\midrule\n & \\multicolumn{2}{c}{pooled, 7 seeds (post hoc)} & Welch $p$ & paired $p$ \\\\\n\\midrule\n")
    for s in SYS:
        if s == SYS[0]: ps = " & "
        elif s == SYS[1]:
            k = f"cmp/pooled7/{slug(SYS[0])}/{T}/steps_to_95"
            ps = f"\\rhval{{{k}/welch_p:2}} & \\rhval{{{k}/paired_p:2}}"
        else:
            ps = f"{float(ref[s]['welch_p']):.2f} & {float(ref[s]['paired_p']):.2f}"
        fh.write(f"{s} & {row(s, 'pooled7')} & {ps} \\\\\n")
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
