"""Discrete temperature sweep and dense-evaluation tables from results/runs.jsonl -> results/tables/{abl_tau,dense_eval}.tex"""
import json, collections, numpy as np
rows = [json.loads(l) for l in open('results/runs.jsonl')]
def ms(m, k): a = np.array([x[k] for x in m]); return f"{a.mean():.3f} $\\pm$ {a.std(ddof=1):.3f}"
def ms0(m, k): a = np.array([x[k] for x in m]); return f"{a.mean():.0f} $\\pm$ {a.std(ddof=1):.0f}"
d = collections.defaultdict(list)
for r in rows:
    if r['group'] == 'abl_tau' and r['status'] == 'ok': d[r['config']['tau']].append(r['metrics'])
out = [r"\begin{tabular}{lrrrr}\toprule Gumbel $\tau$ & val\_success\_final & success\_rate & success\_auc & msgs\_used \\\midrule"]
for t, m in sorted(d.items()):
    out.append(f"{t} & {ms(m,'val_success_final')} & {ms(m,'success_rate')} & {ms(m,'success_auc')} & {ms(m,'msgs_used').split(' ')[0][:-1] if False else ms(m,'msgs_used')[:4]} \\\\")
out.append(r"\bottomrule\end{tabular}")
open('results/tables/abl_tau.tex', 'w').write("\n".join(out) + "\n")
d = collections.defaultdict(list)
for r in rows:
    if r['group'] == 'dense_eval' and r['status'] == 'ok': d[r['name'].split(' (')[0]].append(r['metrics'])
out = [r"\begin{tabular}{lrrrr}\toprule System & success\_rate & success\_auc & episodes\_to\_50 & episodes\_to\_90 \\\midrule"]
for n, m in sorted(d.items()):
    out.append(f"{n} & {ms(m,'success_rate')} & {ms(m,'success_auc')} & {ms0(m,'episodes_to_50')} & {ms0(m,'episodes_to_90')} \\\\")
out.append(r"\bottomrule\end{tabular}")
open('results/tables/dense_eval.tex', 'w').write("\n".join(out) + "\n")
