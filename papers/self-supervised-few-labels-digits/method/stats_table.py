"""Builds results/tables/stats_main.tex from rh compare output (SimCLR vs each baseline, paired over 5 seeds)."""
import pandas as pd
d = pd.read_csv("results/tables/compare_main_test_acc.csv")
d["task"] = d["task"].str.strip()
order = ["n10", "n50", "n200"]
L = [r"\begin{tabular}{llrrr}", r"\toprule", r"Task & Baseline & $\Delta$ acc & paired $p$ & $d$ \\", r"\midrule"]
for t in order:
    for _, r in d[d.task == t].iterrows():
        L.append(f"{t} & {r['name']} & {r['delta']:.3f} & {r['paired_p']:.4f} & {r['cohen_d']:.1f} \\\\")
    if t != order[-1]: L.append(r"\midrule")
L += [r"\bottomrule", r"\end{tabular}"]
open("results/tables/stats_main.tex", "w").write("\n".join(L) + "\n")
print("\n".join(L))
