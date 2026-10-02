"""Logged 5-epoch test-accuracy curves of the main-grid runs (test-set, optimistic) and the paired no-warm-up comparison.
Diagnostic only: prints to stdout. These values are read from run logs or computed here, not registry statistics,
so the paper states the ordering of the curves in words and quotes none of these numbers."""
import json, re, ast, glob, numpy as np
from scipy import stats
rows = [json.loads(l) for l in open("results/runs.jsonl")]
rows = [r for r in rows if r["status"] == "ok"]
def curve(r):
    log = r["provenance"]["log"]
    for l in open(log):
        if l.startswith("curve"):
            return dict(ast.literal_eval(l[l.index("["):]))
names = ["CE", "Label smoothing", "Mixup", "Small-loss (1 net)"]
short = {"CE": "CE", "Label smoothing": "LS", "Mixup": "Mixup", "Small-loss (1 net)": "Small-loss"}
L = [r"\begin{tabular}{llccc}", r"\toprule", r"Noise & System & epoch 10 & best ckpt & epoch 60 \\", r"\midrule"]
for t in ["digits_noise20", "digits_noise40", "digits_noise60"]:
    for n in names:
        rs = [r for r in rows if r["group"] == "main" and r["name"] == n and r["task"] == t]
        assert len(rs) == 5
        cs = [curve(r) for r in rs]
        assert all(abs(c[60] - r["metrics"]["test_acc"]) < 1e-9 for c, r in zip(cs, rs))
        e10 = np.mean([c[10] for c in cs]); best = np.mean([max(c.values()) for c in cs]); e60 = np.mean([c[60] for c in cs])
        L.append(f"{t[-2:]}\\% & {short[n]} & {e10:.3f} & {best:.3f} & {e60:.3f} \\\\")
    if t != "digits_noise60": L.append(r"\midrule")
L += [r"\bottomrule", r"\end{tabular}"]
print("\n".join(L))
# paired no-warm-up vs main small-loss at 40%
a = {r["seed"]: r["metrics"] for r in rows if r["group"] == "main" and r["name"] == "Small-loss (1 net)" and r["task"] == "digits_noise40"}
b = {r["seed"]: r["metrics"] for r in rows if r["group"] == "abl_smallloss"}
ss = sorted(a); assert sorted(b) == ss
for m in ["test_acc", "mem_rate"]:
    d = np.array([b[s][m] - a[s][m] for s in ss]); print(m, d.mean(), stats.ttest_rel([b[s][m] for s in ss], [a[s][m] for s in ss]).pvalue)
W = [r"\begin{tabular}{lrr}", r"\toprule", r"Metric & paired $\Delta$ (no warm-up $-$ main) & $p$ \\", r"\midrule"]
for m in ["test_acc", "mem_rate"]:
    d = np.array([b[s][m] - a[s][m] for s in ss]); p = stats.ttest_rel([b[s][m] for s in ss], [a[s][m] for s in ss]).pvalue
    W.append(f"{m.replace('_', chr(92)+'_')} & {d.mean():+.3f} & {p:.4f}".replace('0.0000','$<$0.0001') + " \\\\")
W += [r"\bottomrule", r"\end{tabular}"]
print("\n".join(W))
