"""Builds the grid pivot table, the T_c sweep table and the sweep/grid figure from results/runs.jsonl."""
import json, numpy as np, collections
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = [json.loads(l) for l in open("results/runs.jsonl")]
R = [r for r in R if r["status"] == "ok" and r["kind"] != "sanity"]
SYS = ["Uniform sampling", "Operand-size curriculum", "Anti-curriculum"]
SH = {"Uniform sampling": "Unif.", "Operand-size curriculum": "Curr.", "Anti-curriculum": "Anti"}
def vals(group, name, task=None, cfg=None, m="steps_to_95"):
    return [r["metrics"][m] for r in R if r["group"] == group and r["name"] == name
            and (task is None or r["task"] == task) and (cfg is None or r["config"] == cfg)]
def cell(v, reached):
    return f"{np.mean(v):.0f} ({int(round(sum(reached)))}/{len(v)})"
# grid pivot: mean steps_to_95 (censored at 4000) and number of seeds that reached 95%
rows = []
for wd in [0, 1, 3]:
    for f in [0.4, 0.5, 0.7]:
        task = f"wd{wd}_f{f}"; g = "main"
        out = []
        for s in SYS:
            v = vals(g, s, task); rc = vals(g, s, task, m="reached"); out.append(cell(v, rc))
        rows.append((wd, f, wd == 1 and f == 0.5, out))
with open("results/tables/grid_pivot.tex", "w") as fh:
    fh.write("\\begin{tabular}{rrl" + "c" * 3 + "}\n\\toprule\n$\\lambda$ & $f$ & $n$ & " + " & ".join(SH[s] for s in SYS) + " \\\\\n\\midrule\n")
    for wd, f, main, out in rows:
        fh.write(f"{wd} & {f} & {5 if main else 3} & " + " & ".join(out) + " \\\\\n")
    fh.write("\\bottomrule\n\\end{tabular}\n")
# T_c sweep
sw = []
for w in [250, 500, 1000, 2000, 4000]:
    if w == 1000: g, cfg = "main", None
    else: g, cfg = "sweep_warm", {"warm": w}
    n = "Operand-size curriculum"
    v = vals(g, n, "wd1_f0.5", cfg); rc = vals(g, n, "wd1_f0.5", cfg, "reached"); ta = vals(g, n, "wd1_f0.5", cfg, "final_test_acc")
    sw.append((f"curriculum, $T_c={w}$", v, rc, ta))
sw.append(("shuffled order, $T_c=1000$", vals("abl_shuffled", "Shuffled-order pool growth"), vals("abl_shuffled", "Shuffled-order pool growth", m="reached"), vals("abl_shuffled", "Shuffled-order pool growth", m="final_test_acc")))
u = "Uniform sampling"; sw.append(("uniform (main group)", vals("main", u, "wd1_f0.5"), vals("main", u, "wd1_f0.5", m="reached"), vals("main", u, "wd1_f0.5", m="final_test_acc")))
with open("results/tables/sweep_tc.tex", "w") as fh:
    fh.write("\\begin{tabular}{lccc}\n\\toprule\nVariant & steps\\_to\\_95 & reached & final acc \\\\\n\\midrule\n")
    for n, v, rc, ta in sw:
        fh.write(f"{n} & {np.mean(v):.0f} $\\pm$ {np.std(v, ddof=1):.0f} & {int(round(sum(rc)))}/{len(v)} & {np.mean(ta):.2f} \\\\\n")
    fh.write("\\bottomrule\n\\end{tabular}\n")
# figure: (a) steps vs T_c, per-seed points; (b) reached rate per grid cell and system
fig, ax = plt.subplots(1, 2, figsize=(7, 2.6))
col = {"Uniform sampling": "#4c78a8", "Operand-size curriculum": "#e45756", "Anti-curriculum": "#72b7b2"}
ws = [250, 500, 1000, 2000, 4000]
ax[0].plot(range(5), [np.mean(x[1]) for x in sw[:5]], "o-", c=col["Operand-size curriculum"], label="curriculum (mean)")
for i, x in enumerate(sw[:5]): ax[0].scatter([i] * len(x[1]), x[1], s=8, c="k", alpha=.4, zorder=3)
ax[0].axhline(np.mean(sw[6][1]), c=col["Uniform sampling"], ls="--", label="uniform (mean)")
ax[0].axhline(np.mean(sw[5][1]), c="gray", ls=":", label="shuffled order, $T_c$=1000")
ax[0].set_xticks(range(5)); ax[0].set_xticklabels(ws); ax[0].set_xlabel("curriculum length $T_c$ (steps)"); ax[0].set_ylabel("steps to 95% (censored 4000)"); ax[0].legend(fontsize=6)
ax[0].set_title("(a) pacing sweep, $\\lambda$=1, $f$=0.5", fontsize=8)
x = np.arange(len(rows)); wdt = 0.27
for k, s in enumerate(SYS):
    rr = []
    for wd, f, main, _ in rows:
        g = "main"; rc = vals(g, s, f"wd{wd}_f{f}", m="reached"); rr.append(np.mean(rc))
    ax[1].bar(x + (k - 1) * wdt, rr, wdt, color=col[s], label=SH[s])
ax[1].set_xticks(x); ax[1].set_xticklabels([f"{wd}/{f}" for wd, f, _, _ in rows], rotation=60, fontsize=6)
ax[1].set_xlabel("weight decay / train fraction"); ax[1].set_ylabel("fraction of seeds reaching 95%"); ax[1].legend(fontsize=6)
ax[1].set_title("(b) grid", fontsize=8)
for a in ax: a.tick_params(labelsize=7)
plt.tight_layout(); plt.savefig("results/figures/sweep_grid.pdf")
print(open("results/tables/grid_pivot.tex").read()); print(open("results/tables/sweep_tc.tex").read())
# main cell table, test table and per-seed bar figure (task wd1_f0.5, group main)
import pandas as pd
T = "wd1_f0.5"
with open("results/tables/main_cell.tex", "w") as fh:
    fh.write("\\begin{tabular}{lcccc}\n\\toprule\nSystem & steps\\_to\\_95 & reached & train95 & grok\\_gap \\\\\n\\midrule\n")
    for s in SYS:
        g = lambda m: vals("main", s, T, m=m)
        fh.write(f"{s} & {np.mean(g('steps_to_95')):.0f} $\\pm$ {np.std(g('steps_to_95'), ddof=1):.0f} & {int(round(sum(g('reached'))))}/5 & "
                 f"{np.mean(g('steps_to_train95')):.0f} $\\pm$ {np.std(g('steps_to_train95'), ddof=1):.0f} & {np.mean(g('grok_gap')):.0f} $\\pm$ {np.std(g('grok_gap'), ddof=1):.0f} \\\\\n")
    fh.write("\\bottomrule\n\\end{tabular}\n")
c = pd.read_csv("results/tables/compare_main_steps_to_95.csv"); c = c[c.task == T]
with open("results/tables/tests.tex", "w") as fh:
    fh.write("\\begin{tabular}{lccc}\n\\toprule\nCurriculum vs. & mean diff. & Welch $p$ & paired $p$ \\\\\n\\midrule\n")
    for _, r in c.iterrows():
        k = f"cmp/main/{r['name'].lower().replace(' ', '-')}/{T}/steps_to_95"   # values come from the registry (rh values), not retyped
        fh.write(f"{r['name']} & \\rhval{{{k}/delta}} & \\rhval{{{k}/welch_p:2}} & \\rhval{{{k}/paired_p:2}} \\\\\n")
    fh.write("\\bottomrule\n\\end{tabular}\n")
fig, ax = plt.subplots(figsize=(3.3, 2.3))
for k, s in enumerate(SYS):
    v = vals("main", s, T); ax.bar(k, np.mean(v), color=col[s], alpha=.8)
    ax.scatter([k] * len(v) + np.linspace(-.12, .12, len(v)), v, s=10, c="k", zorder=3)
ax.set_xticks(range(3)); ax.set_xticklabels([SH[s] for s in SYS]); ax.set_ylabel("steps to 95% (censored 4000)", fontsize=7); ax.tick_params(labelsize=7)
plt.tight_layout(); plt.savefig("results/figures/main_bars.pdf")
print(open("results/tables/main_cell.tex").read(), open("results/tables/tests.tex").read())
