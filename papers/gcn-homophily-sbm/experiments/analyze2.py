"""Ablation (tied weights / 2-hop vs main H2GCN rows) and mean-degree sweep tables + figure.
Derived cells (differences, p-values) are emitted as \\rhval{<key>} from `rh compare` (see `rh values --list`), not typed."""
import json, numpy as np, pandas as pd
from scipy import stats
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows = [json.loads(l) for l in open('results/runs.jsonl')]
R = pd.DataFrame([{'name': r['name'], 'group': r['group'], 'task': r['task'], 'seed': r['seed'], 'h': r['config'].get('h'), 'mu': r['config'].get('mu'),
                   'acc': r['metrics']['accuracy']} for r in rows if r['group'] != 'sanity'])
full = R[(R.group == 'main') & (R.name == 'H2GCN-style (reimplemented)') & (R.mu == 1.0) & R.h.isin([0.1, 0.4, 0.9])]
ab = R[R.group == 'abl_h2gcn']
ABL = lambda v, h, stat: f'\\rhval{{cmp/abl_h2gcn/{v}/h{h:.1f}_mu1.0/accuracy/{stat}}}'  # full model (ref) minus variant
tex = ['\\begin{tabular}{lccccccc}', '\\toprule', '$h$ & H2GCN & tied & $\\Delta$ & $p$ & +2-hop & $\\Delta$ & $p$ \\\\', '\\midrule']
for h in [0.1, 0.4, 0.9]:
    f = full[full.h == h].sort_values('seed').acc.values
    t = ab[(ab.h == h) & ab.name.str.contains('tied')].sort_values('seed').acc.values
    o = ab[(ab.h == h) & ab.name.str.contains('2-hop')].sort_values('seed').acc.values
    pt = stats.ttest_rel(f, t).pvalue; po = stats.ttest_rel(o, f).pvalue
    tex.append(f'{h:.1f} & {f.mean():.3f}$\\pm${f.std(ddof=1):.3f} & {t.mean():.3f}$\\pm${t.std(ddof=1):.3f} & {ABL("h2gcn-tied-weights", h, "delta")} & {ABL("h2gcn-tied-weights", h, "paired_p")} & {o.mean():.3f}$\\pm${o.std(ddof=1):.3f} & {ABL("h2gcn-+-2-hop", h, "delta")} & {ABL("h2gcn-+-2-hop", h, "paired_p")} \\\\')
    print(h, 'full', f.mean(), 'tied', t.mean(), 'p', pt, '2hop', o.mean(), 'p', po)
tex += ['\\bottomrule', '\\end{tabular}']
open('results/tables/abl_h2gcn_custom.tex', 'w').write('\n'.join(tex))
# degree sweep
sw = R[R.group == 'sweep_deg'].copy()
sw['deg'] = sw.name.str.extract(r'deg(\d+)').astype(float); sw['sys'] = sw.name.str.split('_').str[0]
sw['sys'] = sw.name.str.split(' ').str[0]
main = R[(R.group == 'main') & (R.h == 0.4) & (R.mu == 1.0) & R.name.isin(['MLP', 'GCN (reimplemented)', 'H2GCN-style (reimplemented)'])].copy()
main['deg'] = 10.0; main['sys'] = main.name.map({'MLP': 'MLP', 'GCN (reimplemented)': 'GCN', 'H2GCN-style (reimplemented)': 'H2GCN'})
A = pd.concat([sw, main]); degs = [2, 5, 10, 20]
S = A.groupby(['sys', 'deg']).acc.agg(['mean', 'std'])
tex = ['\\begin{tabular}{lcccc}', '\\toprule', 'degree $d$ & ' + ' & '.join(str(d) for d in degs) + ' \\\\', '\\midrule']
for s in ['MLP', 'GCN', 'H2GCN']:
    tex.append(s + ' & ' + ' & '.join(f'{S.loc[(s, float(d)), "mean"]:.3f}$\\pm${S.loc[(s, float(d)), "std"]:.3f}' for d in degs) + ' \\\\')
P = A.pivot_table(index=['deg', 'seed'], columns='sys', values='acc')
DEG = lambda d, stat: f'\\rhval{{cmp/main/mlp/h0.4_mu1.0/accuracy/{stat}}}' if d == 10 else f'\\rhval{{cmp/sweep_deg_d{d}/mlp-deg{d}/h0.4_mu1.0/accuracy/{stat}}}'  # GCN (ref) minus MLP
tex.append('GCN$-$MLP & ' + ' & '.join(DEG(d, 'delta') for d in degs) + ' \\\\')
tex.append('$p$ (paired) & ' + ' & '.join(DEG(d, 'paired_p') for d in degs) + ' \\\\')
tex += ['\\bottomrule', '\\end{tabular}']
open('results/tables/sweep_deg_custom.tex', 'w').write('\n'.join(tex))
print(S.round(3)); 
for d in degs: print(d, (P.loc[float(d)].GCN-P.loc[float(d)].MLP).mean(), stats.ttest_rel(P.loc[float(d)].GCN, P.loc[float(d)].MLP).pvalue)
fig, ax = plt.subplots(figsize=(3.4, 2.3))
for s, c in zip(['MLP', 'GCN', 'H2GCN'], ['#555555', '#d95f02', '#1b9e77']):
    ax.errorbar(degs, [S.loc[(s, float(d)), 'mean'] for d in degs], yerr=[S.loc[(s, float(d)), 'std'] / np.sqrt(5) for d in degs], color=c, marker='o', ms=3, lw=1, capsize=2, label=s)
ax.set_xscale('log'); ax.minorticks_off(); ax.set_xticks(degs); ax.set_xticklabels(degs); ax.set_xlabel('mean degree $d$', fontsize=8); ax.set_ylabel('test accuracy', fontsize=8)
ax.tick_params(labelsize=7); ax.legend(fontsize=7); plt.tight_layout(); plt.savefig('results/figures/sweep_degree.pdf')
