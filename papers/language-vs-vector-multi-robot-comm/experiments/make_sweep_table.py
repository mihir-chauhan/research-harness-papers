"""Per-setting summary of the sweeps, read from results/runs.jsonl -> results/tables/sweeps_summary.tex"""
import json, collections, numpy as np
rows = [json.loads(l) for l in open('results/runs.jsonl')]
out = [r"\begin{tabular}{llrrr}\toprule System & Setting & success\_rate & success\_auc & $n$ \\\midrule"]
for g, p, lab in (("sweep_vocab", "vocab", "V"), ("sweep_noise", "noise", r"$\sigma$")):
    d = collections.defaultdict(list)
    for r in rows:
        if r['group'] == g and r['status'] == 'ok': d[(r['name'], r['config'][p])].append(r['metrics'])
    for (n, v), ms in sorted(d.items(), key=lambda x: (x[0][0], float(x[0][1]))):
        sr = np.array([m['success_rate'] for m in ms]); au = np.array([m['success_auc'] for m in ms])
        out.append(f"{n.split(' (')[0]} & {lab}={v} & {sr.mean():.3f} $\\pm$ {sr.std(ddof=1):.3f} & {au.mean():.3f} $\\pm$ {au.std(ddof=1):.3f} & {len(ms)} \\\\")
    out.append(r"\midrule")
out[-1] = r"\bottomrule\end{tabular}"
open('results/tables/sweeps_summary.tex', 'w').write("\n".join(out) + "\n")
