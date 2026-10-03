"""Builds LaTeX tables whose cells are \\rhval keys (values come from the run registry) and the figures from results/runs.jsonl."""
import json, re, collections, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
T = "physionet2012_mortality"
slug = lambda s: re.sub(r"[^a-z0-9+]+", "-", s.lower()).strip("-")
def v(g, name, m, stat="mean", f=3): return "\\rhval{%s/%s/%s/%s/%s:%d}" % (g, slug(name), T, m, stat, f)
def pm(g, name, m, f=4): return v(g, name, m, "mean", f) + " $\\pm$ " + v(g, name, m, "std", f)
def an(k, f=4): return "\\rhval{analysis/paired-analysis-v2/%s/%s/mean:%d}" % (T, k, f)
def hdr(cols): return "\\begin{tabular}{l" + "c" * len(cols) + "}\\toprule\n" + " & ".join(["System"] + cols) + " \\\\\\midrule\n"
# --- ablation table
rows = [("GRU-D (full)", "main", "GRU-D", None), ("w/o input decay", "abl_decay", "GRU-D w/o input decay", "noin_grud"),
        ("w/o hidden decay", "abl_decay", "GRU-D w/o hidden decay", "nohid_grud"), ("w/o any decay", "abl_decay", "GRU-D w/o any decay", "nodecay_grud"),
        ("LR (full)", "main", "LR (summary)", None), ("LR w/o counts", "abl_counts", "LR (summary) w/o counts", "lrnocnt_lr"),
        ("GBDT (full)", "main", "GBDT (summary)", None), ("GBDT w/o counts", "abl_counts", "GBDT (summary) w/o counts", "gbnocnt_gb")]
s = hdr(["AUROC", "AUPRC", "Brier", "$\\Delta$AUROC", "$p$", "wins"])
for lab, g, n, k in rows:
    d = ("%s & %s & %s" % (an("d_%s_auroc" % k), an("p_%s_auroc" % k, 4), an("w_%s_auroc" % k, 0))) if k else "-- & -- & --"
    s += "%s & %s & %s & %s & %s \\\\\n" % (lab, pm(g, n, "auroc"), pm(g, n, "auprc"), pm(g, n, "brier"), d)
    if lab in ("w/o any decay", "LR w/o counts"): s += "\\midrule\n"
open("results/tables/abl_report.tex", "w").write(s + "\\bottomrule\\end{tabular}\n")
# --- horizon table
systems = [("LR (summary)", "lr-summary"), ("GBDT (summary)", "gbdt-summary"), ("GRU (forward-fill)", "gru-forward-fill"), ("GRU (mask+delta)", "gru-mask+delta"), ("GRU-D", "gru-d")]
s = hdr(["\\rhval{const/h12} h", "\\rhval{const/h24} h", "\\rhval{const/n_hours} h"])
for n, _ in systems:
    s += "%s & %s & %s & %s \\\\\n" % (n, pm("sweep_horizon", n + " @12h", "auroc", 3), pm("sweep_horizon", n + " @24h", "auroc", 3), pm("main", n, "auroc", 3))
open("results/tables/horizon_auroc.tex", "w").write(s + "\\bottomrule\\end{tabular}\n")
s = hdr(["\\rhval{const/h12} h", "\\rhval{const/h24} h", "\\rhval{const/n_hours} h"])
for n, _ in systems:
    s += "%s & %s & %s & %s \\\\\n" % (n, pm("sweep_horizon", n + " @12h", "brier", 4), pm("sweep_horizon", n + " @24h", "brier", 4), pm("main", n, "brier", 4))
open("results/tables/horizon_brier.tex", "w").write(s + "\\bottomrule\\end{tabular}\n")
# --- paired tests (main, 48 h) and horizons
P = [("H1", "GRU-D $-$ GBDT", "grud_gbdt"), ("", "GRU-D $-$ LR", "grud_lr"), ("", "GBDT $-$ LR", "gbdt_lr"), ("H2", "GRU(m+d) $-$ GRU(ffill)", "md_ffill"),
     ("", "GRU-D $-$ GRU(ffill)", "grud_ffill"), ("H3", "GRU-D $-$ GRU(m+d)", "grud_md"), ("", "GRU(ffill) $-$ LR", "ffill_lr")]
s = "\\begin{tabular}{llcccccc}\\toprule\nH & Pair (48 h) & $\\Delta$AUROC & $p$ & wins & $\\Delta$AUPRC & $\\Delta$Brier & $p_{\\mathrm{Br}}$\\\\\\midrule\n"
for h, lab, k in P:
    s += "%s & %s & %s & %s & %s & %s & %s & %s \\\\\n" % (h, lab, an("d_%s_auroc" % k), an("p_%s_auroc" % k, 4), an("w_%s_auroc" % k, 0), an("d_%s_auprc" % k), an("d_%s_brier" % k), an("p_%s_brier" % k, 4))
open("results/tables/paired_main.tex", "w").write(s + "\\bottomrule\\end{tabular}\n")
s = "\\begin{tabular}{llccc}\\toprule\nHorizon & Pair & $\\Delta$AUROC & $p$ & wins\\\\\\midrule\n"
for h in (12, 24):
    for lab, k in (("GBDT $-$ GRU-D", "gbdt_grud"), ("GRU-D $-$ LR", "grud_lr"), ("GRU-D $-$ GRU(ffill)", "grud_ffill"), ("GRU(m+d) $-$ GRU(ffill)", "md_ffill")):
        s += "\\rhval{const/h%d} h & %s & %s & %s & %s \\\\\n" % (h, lab, an("d_h%d_%s_auroc" % (h, k)), an("p_h%d_%s_auroc" % (h, k), 4), an("w_h%d_%s_auroc" % (h, k), 0))
open("results/tables/paired_horizon.tex", "w").write(s.replace("%d h" , "") + "\\bottomrule\\end{tabular}\n")
s = hdr(["CCU", "CSRU", "MICU", "SICU", "pooled"])
for n, _ in systems:
    s += n + " & " + " & ".join(pm("main", n, m, 3) for m in ("auroc_icu1", "auroc_icu2", "auroc_icu3", "auroc_icu4", "auroc_pooled")) + " \\\\\n"
open("results/tables/icu_auroc.tex", "w").write(s + "\\bottomrule\\end{tabular}\n")
# --- figures from the registry
rows = [json.loads(l) for l in open("results/runs.jsonl")]
def auc(g, n): return [r["metrics"]["auroc"] for r in sorted((r for r in rows if r["group"] == g and r["name"] == n and r["status"] == "ok"), key=lambda r: r["seed"])]
col = {"LR (summary)": "#4c78a8", "GBDT (summary)": "#f58518", "GRU (forward-fill)": "#54a24b", "GRU (mask+delta)": "#b279a2", "GRU-D": "#e45756"}
fig, ax = plt.subplots(figsize=(3.4, 2.5))
for n, _ in systems:
    m = [np.mean(auc("sweep_horizon", n + " @12h")), np.mean(auc("sweep_horizon", n + " @24h")), np.mean(auc("main", n))]
    sd = [np.std(auc("sweep_horizon", n + " @12h"), ddof=1), np.std(auc("sweep_horizon", n + " @24h"), ddof=1), np.std(auc("main", n), ddof=1)]
    ax.errorbar([12, 24, 48], m, yerr=sd, marker="o", ms=3, lw=1.2, capsize=2, color=col[n], label=n)
ax.set_xlabel("observation horizon (h)"); ax.set_ylabel("AUROC (mean $\\pm$ sd, 5 seeds)"); ax.set_xticks([12, 24, 48]); ax.legend(fontsize=6, frameon=False)
ax.spines[["top", "right"]].set_visible(False); fig.tight_layout(); fig.savefig("results/figures/horizon_auroc.pdf"); plt.close(fig)
fig, ax = plt.subplots(figsize=(3.4, 2.5)); names = [n for n, _ in systems]
for i, n in enumerate(names):
    a = auc("main", n); ax.scatter([i] * 5 + np.linspace(-.12, .12, 5), a, s=14, color=col[n]); ax.hlines(np.mean(a), i - .25, i + .25, color="k", lw=1)
for s_ in range(5): ax.plot(range(5), [auc("main", n)[s_] for n in names], color="0.8", lw=.6, zorder=0)
ax.set_xticks(range(5)); ax.set_xticklabels(["LR", "GBDT", "GRU\nffill", "GRU\nm+d", "GRU-D"], fontsize=7); ax.set_ylabel("AUROC per seed (48 h)")
ax.spines[["top", "right"]].set_visible(False); fig.tight_layout(); fig.savefig("results/figures/seed_auroc.pdf"); plt.close(fig)
