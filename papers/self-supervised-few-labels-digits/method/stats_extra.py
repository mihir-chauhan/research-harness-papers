"""Layout of the additional paired-comparison table -> results/tables/stats_extra.tex.

No statistic is computed here. Every cell is a \\rhval key of `rh compare` (delta = A minus B, paired-by-seed p):
  rh compare --group cmp_aug      --metric test_acc --ref "SimCLR-style probe"
  rh compare --group cmp_supaug   --metric test_acc --ref "Supervised + aug"
  rh compare --group cmp_rotation --metric test_acc --ref "Rotation (reimplemented)"
  rh compare --group cmp_random   --metric test_acc --ref "Random CNN + probe"
The cmp_* groups hold copies (`rh log --from-run`) of the main and ablation rows, so that systems of
different groups can be compared by `rh compare`; they are not additional runs.
"""
# (group, A = reference system, B, slug of B)
pairs = [("cmp_aug", "SimCLR-style probe", "SimCLR geom-only", "simclr-geom-only"),
         ("cmp_aug", "SimCLR-style probe", "SimCLR photo-only", "simclr-photo-only"),
         ("cmp_supaug", "Supervised + aug", "Supervised scratch", "supervised-scratch"),
         ("cmp_supaug", "Supervised + aug", "SimCLR-style probe", "simclr-style-probe"),
         ("cmp_rotation", "Rotation (reimplemented)", "PCA + LR", "pca-+-lr"),
         ("cmp_rotation", "Rotation (reimplemented)", "Random CNN + probe", "random-cnn-+-probe"),
         ("cmp_random", "Random CNN + probe", "PCA + LR", "pca-+-lr"),
         ("cmp_random", "Random CNN + probe", "Pixels + LR", "pixels-+-lr")]
L = [r"\begin{tabular}{llrr}", r"\toprule", r"Task & A $-$ B & $\Delta$ acc & paired $p$ \\", r"\midrule"]
for g, a, b, sb in pairs:
    for t in ["n10", "n50", "n200"]:
        key = f"cmp/{g}/{sb}/{t}/test_acc"
        L.append(f"{t} & {a} $-$ {b} & \\rhval{{{key}/delta:3}} & \\rhval{{{key}/paired_p:3}} \\\\")
    L.append(r"\midrule")
L[-1] = r"\bottomrule"; L.append(r"\end{tabular}")
open("results/tables/stats_extra.tex", "w").write("\n".join(L) + "\n"); print("\n".join(L))
