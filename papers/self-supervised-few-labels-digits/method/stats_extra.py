"""Paired-by-seed t-tests from results/runs.jsonl for ablation and baseline pairs -> results/tables/stats_extra.tex."""
import json, numpy as np
from scipy import stats
R = [json.loads(l) for l in open("results/runs.jsonl")]
R = [r for r in R if r["status"] == "ok" and r["kind"] != "sanity"]
def acc(group, name, task, tag=None):
    d = {r["seed"]: r["metrics"]["test_acc"] for r in R if r["group"] == group and r["name"] == name and r["task"] == task
         and (tag is None or all(r["config"].get(k) == v for k, v in tag.items()))}
    return d
pairs = [("abl_aug", "SimCLR geom-only", "main", "SimCLR-style probe"),
         ("abl_aug", "SimCLR photo-only", "main", "SimCLR-style probe"),
         ("abl_supaug", "Supervised + aug", "main", "Supervised scratch"),
         ("abl_supaug", "Supervised + aug", "main", "SimCLR-style probe"),
         ("main", "Rotation (reimplemented)", "main", "PCA + LR"),
         ("main", "Rotation (reimplemented)", "main", "Random CNN + probe"),
         ("main", "Random CNN + probe", "main", "PCA + LR"),
         ("main", "Random CNN + probe", "main", "Pixels + LR")]
L = [r"\begin{tabular}{llrrrr}", r"\toprule", r"Task & A $-$ B & $\Delta$ acc & paired $p$ & A wins \\", r"\midrule"]
L[0] = r"\begin{tabular}{llrrr}"
for ga, na, gb, nb in pairs:
    for t in ["n10", "n50", "n200"]:
        a, b = acc(ga, na, t), acc(gb, nb, t)
        s = sorted(set(a) & set(b)); x = np.array([a[i] for i in s]); y = np.array([b[i] for i in s])
        p = stats.ttest_rel(x, y).pvalue
        L.append(f"{t} & {na} $-$ {nb} & {np.mean(x-y):.3f} & {p:.3f} & {int((x>y).sum())}/{len(s)} \\\\")
    L.append(r"\midrule")
L[-1] = r"\bottomrule"; L.append(r"\end{tabular}")
open("results/tables/stats_extra.tex", "w").write("\n".join(L) + "\n"); print("\n".join(L))
ts = sorted(r["provenance"]["started"] for r in R); print(ts[0], ts[-1])
print(max((r["provenance"]["duration_s"], r["name"], r["task"], r["seed"]) for r in R))
