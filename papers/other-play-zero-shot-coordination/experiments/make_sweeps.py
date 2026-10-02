"""Build sweep tables and figure from results/runs.jsonl (no numbers typed by hand)."""
import json, collections, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
rows = [json.loads(l) for l in open("results/runs.jsonl")]
rows = [r for r in rows if r["status"] == "ok"]
def cell(group, name, task, key, val, m="cross_play", sel=None):
    v = [r["metrics"][m] for r in rows if r["group"] == group and r["name"] == name and r["task"] == task
         and (r["config"] or {}).get(key) == val]
    return np.mean(v), np.std(v, ddof=1), len(v)
Ks = [1, 2, 4, 8, 16, 32]
def popcell(task, K, m):
    src = [r for r in rows if r["name"].startswith("Population") and r["task"] == task and r["config"].get("pop_size") == K
           and r["group"] == ("main" if K == 8 else "sweep_popsize")]
    v = [r["metrics"][m] for r in src]
    return np.mean(v), np.std(v, ddof=1), len(v)
fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.3))
col = {"lever": "#1f77b4", "safe": "#d95f02", "signal": "#1b9e77"}
tex = ["\\begin{tabular}{lrrrrrr}\\toprule", "Task & $K{=}1$ & 2 & 4 & 8 & 16 & 32 \\\\ \\midrule"]
for t in ["lever", "safe", "signal"]:
    ms = [popcell(t, K, "cross_play") for K in Ks]
    tex.append(t + " & " + " & ".join(f"{m:.3f}" for m, s, n in ms) + " \\\\")
    ax[0].errorbar(Ks, [m for m, s, n in ms], [s for m, s, n in ms], marker="o", ms=3, label=t, color=col[t], capsize=2)
tex.append("\\bottomrule\\end{tabular}")
open("results/tables/sweep_popsize_tab.tex", "w").write("\n".join(tex))
ax[0].set_xscale("log", base=2); ax[0].set_xlabel("population size K"); ax[0].set_ylabel("cross-play"); ax[0].legend(fontsize=6)
ax[0].set_title("Population (FCP-style)", fontsize=8)
# init scale
sds = [0.25, 0.5, 1.0, 2.0, 4.0]
tex = ["\\begin{tabular}{llrrrrr}\\toprule", "System & Metric & sd 0.25 & 0.5 & 1 & 2 & 4 \\\\ \\midrule"]
for name, c in [("Self-play", "gray"), ("Other-play", "#1f77b4")]:
    for m in ["cross_play", "self_play"]:
        vals = []
        for sd in sds:
            if sd == 1.0:
                v = [r["metrics"][m] for r in rows if r["group"] == "main" and r["name"] == name and r["task"] == "lever"]
            else:
                v = [r["metrics"][m] for r in rows if r["group"] == "sweep_init" and r["name"] == name and r["config"].get("init_std") == sd]
            vals.append((np.mean(v), np.std(v, ddof=1)))
        tex.append(f"{name} & {m.replace('_','-')} & " + " & ".join(f"{a:.3f}" for a, b in vals) + " \\\\")
        if m == "cross_play":
            ax[1].errorbar(sds, [a for a, b in vals], [b for a, b in vals], marker="o", ms=3, label=name, color=c, capsize=2)
def opx(sd, m):
    if sd == 1.0:
        return [r["metrics"][m] for r in rows if r["group"] == "main" and r["name"] == "Other-play" and r["task"] == "lever"]
    return [r["metrics"][m] for r in rows if r["group"] == "sweep_init" and r["name"] == "Other-play" and r["task"] == "lever" and r["config"].get("init_std") == sd]
tex.append("Other-play & cross-play std & " + " & ".join(f"{np.std(opx(sd,'cross_play'),ddof=1):.3f}" for sd in sds) + " \\\\")
tex.append("Other-play & frac. special & " + " & ".join(f"{np.mean(opx(sd,'frac_special')):.2f}" for sd in sds) + " \\\\")
chk = lambda sd: np.mean([r["metrics"]["frac_init_above"] for r in rows if r["group"] == "init_check" and r["config"]["init_std"] == sd])
tex.append("Other-play & frac. init $>0.11$ & -- & -- & " + f"{chk(1.0):.2f}" + " & -- & " + f"{chk(4.0):.2f}" + " \\\\")
tex.append("\\bottomrule\\end{tabular}")
open("results/tables/sweep_init_tab.tex", "w").write("\n".join(tex))
ax[1].set_xscale("log", base=2); ax[1].set_xlabel("init std (lever)"); ax[1].legend(fontsize=6); ax[1].set_title("Init scale", fontsize=8)
# steps (OP, lever)
sts = [500, 1500, 5000, 15000]
tex = ["\\begin{tabular}{lrrrr}\\toprule", "Metric & 500 & 1500 & 5000 & 15000 \\\\ \\midrule"]
res = {}
for m in ["cross_play", "self_play", "frac_special"]:
    vals = []
    for st in sts:
        if st == 1500:
            v = [r["metrics"][m] for r in rows if r["group"] == "main" and r["name"] == "Other-play" and r["task"] == "lever"]
        else:
            v = [r["metrics"][m] for r in rows if r["group"] == "sweep_steps" and r["config"].get("steps") == st]
        vals.append((np.mean(v), np.std(v, ddof=1)))
    res[m] = vals
    tex.append(m.replace("_", "-") + " & " + " & ".join(f"{a:.3f}" for a, b in vals) + " \\\\")
tex.append("\\bottomrule\\end{tabular}")
open("results/tables/sweep_steps_tab.tex", "w").write("\n".join(tex))
for m, c in [("cross_play", "#1f77b4"), ("self_play", "#d95f02"), ("frac_special", "#1b9e77")]:
    ax[2].errorbar(sts, [a for a, b in res[m]], [b for a, b in res[m]], marker="o", ms=3, label=m.replace("_", "-"), color=c, capsize=2)
ax[2].set_xscale("log"); ax[2].set_xlabel("OP updates (lever)"); ax[2].legend(fontsize=6); ax[2].set_title("OP training length", fontsize=8)
for a in ax: a.tick_params(labelsize=7)
plt.tight_layout(); plt.savefig("results/figures/sweeps.pdf")
