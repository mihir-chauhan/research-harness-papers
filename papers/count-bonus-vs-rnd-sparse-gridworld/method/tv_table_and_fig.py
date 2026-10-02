"""TV-time table (TV tasks only) and a readable steps-to-first-reward bar figure, both from results/runs.jsonl."""
import json, collections, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
rows = [json.loads(l) for l in open("results/runs.jsonl")]
main = [r for r in rows if r["group"] == "main" and r["status"] == "ok"]
order = ["Epsilon-greedy Q-learning", "Step penalty only (optimistic init)", "Count bonus (state), no offset",
         "Count bonus (state)", "Count bonus (obs)", "RND bonus"]
short = dict(zip(order, ["eps-greedy", "penalty only", "count, no offset", "count (state)", "count (obs)", "RND"]))
tasks = ["chain_10", "chain_20", "chain_40", "room_2", "room_4", "room_6", "chain_20_tv", "room_4_tv"]
d = collections.defaultdict(list)
for r in main: d[(r["name"], r["task"])].append(r["metrics"])
# TV table
tex = "\\begin{tabular}{l" + "r" * 2 + "}\n\\hline\nSystem & chain\\_20\\_tv & room\\_4\\_tv \\\\\n\\hline\n"
for n in order:
    cells = []
    for t in ["chain_20_tv", "room_4_tv"]:
        x = [m["tv_time_frac"] for m in d[(n, t)]]
        cells.append(f"{np.mean(x):.2f} $\\pm$ {np.std(x, ddof=1):.2f}")
    tex += short[n] + " & " + " & ".join(cells) + " \\\\\n"
tex += "\\hline\n\\end{tabular}\n"
open("results/tables/tv_frac.tex", "w").write(tex)
# bars
fig, axs = plt.subplots(1, 2, figsize=(7, 3.2))
cols = ["#999999", "#e69f00", "#f0e442", "#0072b2", "#56b4e9", "#d55e00"]
for ax, ts, bud in [(axs[0], [t for t in tasks if t.startswith("chain")], 30000), (axs[1], [t for t in tasks if t.startswith("room")], 100000)]:
    w = 0.13
    for i, n in enumerate(order):
        mu = [np.mean([m["steps_to_first_reward"] for m in d[(n, t)]]) for t in ts]
        sd = [np.std([m["steps_to_first_reward"] for m in d[(n, t)]], ddof=1) for t in ts]
        ax.bar(np.arange(len(ts)) + (i - 2.5) * w, mu, w, yerr=sd, color=cols[i], label=short[n], capsize=1, error_kw={"lw": .6})
    ax.set_xticks(range(len(ts))); ax.set_xticklabels([t.replace("_", "\n", 1).replace("_tv", " TV") for t in ts], fontsize=7)
    ax.axhline(bud, color="k", lw=.5, ls=":"); ax.set_ylabel("steps to first reward", fontsize=8); ax.tick_params(labelsize=7)
axs[0].legend(fontsize=6, ncol=2)
plt.tight_layout(); plt.savefig("results/figures/bars_main_steps_to_first_reward.pdf")
