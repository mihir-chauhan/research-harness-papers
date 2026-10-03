"""Writes paper tables whose cells are \\rhval{key} references (no typed numbers)."""
SYS = [("cnn", "CNN"), ("mlp", "MLP"), ("confusion-mlp", "Confusion (MLP)"), ("pca", "PCA"), ("binder-chi-reference", "Binder/$\\chi$ (ref.)"),
       ("logreg-z2-fixed", "LogReg (Z2-fixed)"), ("logreg-raw", "LogReg (raw)")]


def cell(key, spec="3"):
    return "\\rhval{%s:%s}" % (key, spec)


# Table: signed bias
L = ["\\begin{tabular}{lcccc}", "\\toprule", "System & $L{=}16$ & $L{=}24$ & $L{=}32$ & collapse \\\\", "\\midrule"]
for s, n in SYS:
    L.append(n + " & " + " & ".join(
        cell(f"main/{s}/ising/tc_bias_{m}/mean") + " $\\pm$ " + cell(f"main/{s}/ising/tc_bias_{m}/std") for m in ("l16", "l24", "l32", "fss")) + " \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open("paper/sections/tab_bias.tex", "w").write("\n".join(L) + "\n")

# Table: collapse variants (Tc error)
L = ["\\begin{tabular}{lccccc}", "\\toprule", "System & $w{=}0.6$ & $w{=}0.45$ & $w{=}0.3$ & $\\nu{=}1$ fixed & $|\\nu{-}1|$ free \\\\", "\\midrule"]
for s, n in SYS:
    cells = [cell(f"{g}/{s}/ising/tc_error_fss/mean") for g in ("main", "abl_window_0.45", "abl_window_0.3", "abl_nu_fixed")]
    cells.append(cell(f"main/{s}/ising/nu_error_fss/mean"))
    L.append(n + " & " + " & ".join(cells) + " \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open("paper/sections/tab_collapse.tex", "w").write("\n".join(L) + "\n")

# Table: sweeps
A = "analysis/sweep-summary/ising/"
L = ["\\begin{tabular}{llcccc}", "\\toprule", "Model & setting & $L{=}16$ & $L{=}32$ & collapse & ratio$_{32}$ \\\\", "\\midrule"]
for k, n in (("cnn", "CNN"), ("mlp", "MLP")):
    for p, vals, lab in (("margin", ["0p15", "0p3", "0p45", "0p6"], "margin"), ("nsamp", ["10", "25", "50"], "samples/chain"), ("nsamp_ep", ["10", "25"], "samples, scaled ep.")):
        for v in vals:
            t = f"{k}_{p}{v}"
            L.append(f"{n} & {lab} {v.replace('p', '.')} & " + " & ".join(cell(A + f"{t}_{m}_mean/mean") for m in ("l16", "l32", "fss")) +
                     " & " + cell(A + f"{t}_ratio_l32/mean", "2") + " \\\\")
    L.append("\\midrule")
L[-1] = "\\bottomrule"; L.append("\\end{tabular}")
open("paper/sections/tab_sweeps.tex", "w").write("\n".join(L) + "\n")

# Table: hypothesis tests
A = "analysis/paired-tests/ising/"
rows = [("H1", "CNN vs PCA, $L{=}32$", "h1_cnn_vs_pca_l32"), ("H1", "MLP vs PCA, $L{=}32$", "h1_mlp_vs_pca_l32"),
        ("H2", "CNN: collapse vs $L{=}32$", "h2_cnn_fss_vs_l32"), ("H2", "MLP: collapse vs $L{=}32$", "h2_mlp_fss_vs_l32"),
        ("H4", "PCA vs CNN (collapse)", "h4_pca_vs_cnn_fss"), ("H4", "Confusion vs CNN (collapse)", "h4_conf_vs_cnn_fss"),
        ("--", "Confusion vs CNN, $L{=}32$", "conf_vs_cnn_l32"), ("--", "Confusion vs MLP, $L{=}32$", "conf_vs_mlp_l32"), ("--", "CNN: $\\nu{=}1$ vs free (collapse)", "nu1_cnn"), ("--", "MLP: $\\nu{=}1$ vs free (collapse)", "nu1_mlp"),
        ("--", "MLP vs CNN (collapse)", "h4_mlp_vs_cnn_fss"), ("--", "Binder/$\\chi$ vs CNN (collapse)", "h4_binder_vs_cnn_fss")]
L = ["\\begin{tabular}{llccc}", "\\toprule", "Hyp. & comparison (first minus second) & mean diff. & Wilcoxon $p$ & seeds first lower \\\\", "\\midrule"]
for h, n, t in rows:
    L.append(f"{h} & {n} & " + cell(A + t + "_meandiff/mean") + " & " + cell(A + t + "_p/mean") + " & " + cell(A + t + "_wins/mean", "0") + " \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open("paper/sections/tab_tests.tex", "w").write("\n".join(L) + "\n")

# Table: sampler check
A = "sanity/sampler-check-long/ising/"
L = ["\\begin{tabular}{lccc}", "\\toprule", "$T$ & $e$ Swendsen--Wang & $e$ Metropolis & $e$ Onsager \\\\", "\\midrule"]
for T, k in (("1.8", "1p8"), ("2.0", "2p0"), ("3.0", "3p0"), ("3.5", "3p5")):
    L.append(T + " & " + " & ".join(cell(A + f"e_{m}_tlong_{k}/mean", "4") for m in ("sw", "metropolis", "onsager")) + " \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open("paper/sections/tab_sampler.tex", "w").write("\n".join(L) + "\n")
