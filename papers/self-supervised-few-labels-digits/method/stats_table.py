"""Layout of results/tables/stats_main.tex (SimCLR-style probe minus each baseline, paired over 5 seeds).

No statistic is computed here: every cell is a \\rhval key of
  rh compare --group main --metric test_acc --ref "SimCLR-style probe"
"""
names = [("PCA + LR", "pca-+-lr"), ("Pixels + LR", "pixels-+-lr"), ("Random CNN + probe", "random-cnn-+-probe"),
         ("Rotation (reimplemented)", "rotation-reimplemented"), ("Supervised scratch", "supervised-scratch")]
order = ["n10", "n50", "n200"]
L = [r"\begin{tabular}{llrrr}", r"\toprule", r"Task & Baseline & $\Delta$ acc & paired $p$ & $d$ \\", r"\midrule"]
for t in order:
    for name, s in names:
        key = f"cmp/main/{s}/{t}/test_acc"
        L.append(f"{t} & {name} & \\rhval{{{key}/delta:3}} & \\rhval{{{key}/paired_p:4}} & \\rhval{{{key}/cohen_d:1}} \\\\")
    if t != order[-1]: L.append(r"\midrule")
L += [r"\bottomrule", r"\end{tabular}"]
open("results/tables/stats_main.tex", "w").write("\n".join(L) + "\n")
print("\n".join(L))
