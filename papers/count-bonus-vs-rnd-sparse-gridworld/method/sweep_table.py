"""Build sweep tables (per config value) from results/runs.jsonl -> results/tables/sweeps.{tex,md}."""
import json, collections, numpy as np
rows = [json.loads(l) for l in open("results/runs.jsonl")]
def tab(group, param, metrics, fname, vals):
    d = collections.defaultdict(list)
    for r in rows:
        if r["group"] == group and r["kind"] != "sanity" and r.get("config", {}).get(param) is not None:
            d[(r["name"], r["config"][param])].append(r["metrics"])
    names = sorted({k[0] for k in d})
    short = {"steps_to_first_reward": "steps", "tv_time_frac": "TV frac", "final_return": "return",
             "RND bonus": "RND", "Count bonus (obs)": "Cnt-obs", "Count bonus (state)": "Cnt-st"}
    head = [{"K": "$K$", "beta": "$\\beta$"}.get(param, param)] + [f"{short[n]} {short[m]}" for n in names for m in metrics]
    out = []
    for v in vals:
        cells = [str(v)]
        for n in names:
            for m in metrics:
                x = [e[m] for e in d[(n, v)]]
                cells.append(f"{np.mean(x):.2f} $\\pm$ {np.std(x, ddof=1):.2f}" if m.startswith(("final", "found", "tv")) else f"{np.mean(x):.0f} $\\pm$ {np.std(x, ddof=1):.0f}")
        out.append(cells)
    return head, out
for group, param, metrics, vals in [("sweep_K", "K", ["steps_to_first_reward", "tv_time_frac"], [1, 4, 16, 64]),
                                    ("sweep_beta", "beta", ["steps_to_first_reward", "final_return"], [0.03, 0.1, 0.3, 1.0])]:
    head, out = tab(group, param, metrics, group, vals)
    tex = "\\begin{tabular}{" + "l" + "r" * (len(head) - 1) + "}\n\\hline\n" + " & ".join(head) + " \\\\\n\\hline\n"
    tex += "".join(" & ".join(c) + " \\\\\n" for c in out) + "\\hline\n\\end{tabular}\n"
    open(f"results/tables/{group}_perconfig.tex", "w").write(tex)
    open(f"results/tables/{group}_perconfig.md", "w").write("| " + " | ".join(head) + " |\n|" + "---|" * len(head) + "\n" + "".join("| " + " | ".join(c) + " |\n" for c in out))
