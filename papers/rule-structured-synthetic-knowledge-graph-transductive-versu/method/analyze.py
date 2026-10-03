"""Derived statistics for sweeps/ablations, computed only from logged runs (results/runs.jsonl).
Writes a flat metrics JSON, LaTeX tables and a sweep figure."""
import json, sys, collections
import numpy as np
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

out = sys.argv[1]
rows = [json.loads(l) for l in open("results/runs.jsonl")]
rows = [r for r in rows if r.get("status") == "ok" and r["group"] in ("main", "abl_nodrop", "sweep_layers", "sweep_density")]
SYS = {"Path-MP (2-hop)": "pm", "TransE (reimplemented)": "te", "TransE+fold-in (reimplemented)": "tf", "Rule oracle (hand-written)": "or"}
def get(group, name, task, cfgkey=None, cfgval=None):
    d = {}
    for r in rows:
        if r["group"] != group or r["name"] != name or r["task"] != task: continue
        c = r["config"] if isinstance(r["config"], dict) else json.loads(r["config"] or "{}")
        if cfgkey is not None and c.get(cfgkey) != cfgval: continue
        d[int(r["seed"])] = r["metrics"]
    return d
M = {}
def stat(tag, d, metric="mrr"):
    v = np.array([d[s][metric] for s in sorted(d)])
    M[tag + "_mean"] = float(v.mean()); M[tag + "_std"] = float(v.std(ddof=1)); return v
def paired(tag, a, b):
    s = sorted(set(a) & set(b)); x = np.array([a[i]["mrr"] for i in s]); y = np.array([b[i]["mrr"] for i in s])
    M[tag + "_diff"] = float((x - y).mean())
    M[tag + "_p"] = float(stats.ttest_rel(x, y).pvalue) if np.abs(x - y).std() > 0 else 1.0

# --- density sweep (inductive); fraction 1.0 is the main-group row
dens = {}
for name, k in SYS.items():
    if k == "te": continue
    for f in (0.25, 0.5, 0.75, 1.0):
        d = get("main", name, "inductive") if f == 1.0 else get("sweep_density", name, "inductive", "obs_frac", f)
        dens[(k, f)] = d
        stat("dens_%s_f%d" % (k, round(f * 100)), d)
for f in (0.25, 0.5, 0.75):
    paired("dens_pm_vs_tf_f%d" % round(f * 100), dens[("pm", f)], dens[("tf", f)])
    paired("dens_pm_vs_or_f%d" % round(f * 100), dens[("pm", f)], dens[("or", f)])
paired("dens_pm_f100_vs_f75", dens[("pm", 1.0)], dens[("pm", 0.75)])

# --- depth and edge-removal ablations
lay = {}
for task in ("transductive", "inductive"):
    t = task[:5]
    lay[(task, 1)] = get("sweep_layers", "Path-MP (2-hop)", task, "layers", 1)
    lay[(task, 2)] = get("main", "Path-MP (2-hop)", task)
    lay[(task, 3)] = get("sweep_layers", "Path-MP (2-hop)", task, "layers", 3)
    nd = get("abl_nodrop", "Path-MP (2-hop)", task)
    for L in (1, 2, 3): stat("lay_%s_L%d" % (t, L), lay[(task, L)])
    stat("nodrop_%s" % t, nd)
    for rel in ("parent", "sibling", "grandparent", "uncle"): stat("nodrop_%s_%s" % (t, rel), nd, "mrr_" + rel)
    paired("lay_%s_L3_vs_L2" % t, lay[(task, 3)], lay[(task, 2)])
    paired("lay_%s_L1_vs_L2" % t, lay[(task, 1)], lay[(task, 2)])
    paired("nodrop_%s_vs_L2" % t, nd, lay[(task, 2)])
# --- transductive -> inductive change per system (paired by seed)
for name, k in SYS.items():
    paired("shift_%s" % k, get("main", name, "inductive"), get("main", name, "transductive"))

# --- H3: fold-in against frozen random embeddings (inductive)
paired("h3_tf_vs_te_ind", get("main", "TransE+fold-in (reimplemented)", "inductive"), get("main", "TransE (reimplemented)", "inductive"))
paired("h3_pm_vs_tf_ind", get("main", "Path-MP (2-hop)", "inductive"), get("main", "TransE+fold-in (reimplemented)", "inductive"))

# --- tables
def f3(x): return "%.3f" % x
with open("results/tables/analysis_depth.tex", "w") as fh:
    fh.write("\\begin{tabular}{lcccc}\\toprule\nVariant & MRR trans. & MRR induct. & $\\Delta$ vs L=2 (trans.) & $\\Delta$ vs L=2 (induct.) \\\\\\midrule\n")
    for lab, tag in (("1 layer", "L1"), ("2 layers (main)", "L2"), ("3 layers", "L3")):
        dt = "--" if tag == "L2" else f3(M["lay_trans_%s_vs_L2_diff" % tag]); di = "--" if tag == "L2" else f3(M["lay_induc_%s_vs_L2_diff" % tag])
        fh.write("%s & %s$\\pm$%s & %s$\\pm$%s & %s & %s \\\\\n" % (lab, f3(M["lay_trans_%s_mean" % tag]), f3(M["lay_trans_%s_std" % tag]), f3(M["lay_induc_%s_mean" % tag]), f3(M["lay_induc_%s_std" % tag]), dt, di))
    fh.write("2 layers, no edge removal & %s$\\pm$%s & %s$\\pm$%s & %s & %s \\\\\n" % (f3(M["nodrop_trans_mean"]), f3(M["nodrop_trans_std"]), f3(M["nodrop_induc_mean"]), f3(M["nodrop_induc_std"]), f3(M["nodrop_trans_vs_L2_diff"]), f3(M["nodrop_induc_vs_L2_diff"])))
    fh.write("\\bottomrule\\end{tabular}\n")
with open("results/tables/analysis_density.tex", "w") as fh:
    fh.write("\\begin{tabular}{lcccc}\\toprule\nSystem & 25\\% & 50\\% & 75\\% & 100\\% \\\\\\midrule\n")
    for lab, k in (("Path-MP (2-hop)", "pm"), ("TransE+fold-in", "tf"), ("Rule oracle", "or")):
        fh.write(lab + " & " + " & ".join("%s$\\pm$%s" % (f3(M["dens_%s_f%d_mean" % (k, f)]), f3(M["dens_%s_f%d_std" % (k, f)])) for f in (25, 50, 75, 100)) + " \\\\\n")
    fh.write("\\bottomrule\\end{tabular}\n")

# --- figure
fig, ax = plt.subplots(figsize=(3.4, 2.5))
for lab, k, c, mk in (("Path-MP (2-hop)", "pm", "#1b6ca8", "o"), ("TransE+fold-in", "tf", "#d9822b", "s"), ("Rule oracle", "or", "#555555", "^")):
    xs = [25, 50, 75, 100]
    m = np.array([M["dens_%s_f%d_mean" % (k, f)] for f in xs]); s = np.array([M["dens_%s_f%d_std" % (k, f)] for f in xs])
    ax.errorbar(xs, m, yerr=s, label=lab, color=c, marker=mk, capsize=2, lw=1.2, ms=4)
ax.set_xlabel("observed fraction of the new graph (%)"); ax.set_ylabel("inductive filtered MRR"); ax.set_ylim(0, 1.02)
ax.legend(fontsize=7, frameon=False); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig("results/figures/sweep_density_mrr.pdf")
print(json.dumps(M, indent=0))
json.dump(M, open(out, "w"))
