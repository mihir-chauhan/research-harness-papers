"""Aggregates results/runs.jsonl (group main): cell means, paired tests, win map, accuracy-vs-h curves."""
import json, numpy as np, pandas as pd
from scipy import stats
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

rows = [json.loads(l) for l in open('results/runs.jsonl')]
df = pd.DataFrame([{'name': r['name'], 'group': r['group'], 'seed': r['seed'], 'h': r['config'].get('h'), 'mu': r['config'].get('mu'),
                    'acc': r['metrics']['accuracy'], 'rh': r['metrics'].get('realized_h')} for r in rows if r['group'] == 'main'])
short = {'MLP': 'MLP', 'GCN (reimplemented)': 'GCN', 'H2GCN-style (reimplemented)': 'H2GCN', 'Label propagation (reimplemented)': 'LP'}
df['sys'] = df.name.map(short)
SYS = ['MLP', 'GCN', 'H2GCN', 'LP']
mus = sorted(df.mu.unique()); hs = sorted(df.h.unique())
m = df.groupby(['mu', 'h', 'sys']).acc.mean().unstack('sys')[SYS]
sd = df.groupby(['mu', 'h', 'sys']).acc.std().unstack('sys')[SYS]
print(df.groupby(['mu', 'h', 'sys']).size().describe()[['min', 'max']].values)
out = []
# --- per-cell table: mean (std), winner
tex = ['\\begin{tabular}{rr' + 'c' * 4 + 'l}', '\\toprule', '$\\mu$ & $h$ & MLP & GCN & H2GCN & LP & best \\\\', '\\midrule']
for mu in mus:
    for h in hs:
        r = m.loc[(mu, h)]; s = sd.loc[(mu, h)]
        best = r.idxmax()
        cells = [f'{r[k]:.3f}' if k != best else f'\\textbf{{{r[k]:.3f}}}' for k in SYS]
        tex.append(f'{mu:g} & {h:.1f} & ' + ' & '.join(cells) + f' & {best} \\\\')
    if mu != mus[-1]: tex.append('\\midrule')
tex += ['\\bottomrule', '\\end{tabular}']
open('results/tables/cells.tex', 'w').write('\n'.join(tex))
# --- paired tests GCN-MLP, H2GCN-MLP, H2GCN-GCN per cell
P = df.pivot_table(index=['mu', 'h', 'seed'], columns='sys', values='acc')
trows = []
for (mu, h), g in P.groupby(level=[0, 1]):
    d1 = g['GCN'] - g['MLP']; d2 = g['H2GCN'] - g['GCN']; d3 = g['H2GCN'] - g['MLP']
    t1 = stats.ttest_rel(g['GCN'], g['MLP']); t2 = stats.ttest_rel(g['H2GCN'], g['GCN'])
    trows.append(dict(mu=mu, h=h, gcn_minus_mlp=d1.mean(), p_gcn_mlp=t1.pvalue, h2_minus_gcn=d2.mean(), p_h2_gcn=t2.pvalue,
                      h2_minus_mlp=d3.mean(), h2_vs_max=(g['H2GCN'] - g[['MLP', 'GCN']].max(axis=1)).mean() if False else m.loc[(mu, h), 'H2GCN'] - max(m.loc[(mu, h), 'MLP'], m.loc[(mu, h), 'GCN']),
                      lp_minus_mlp=(g['LP'] - g['MLP']).mean(), n=len(g)))
T = pd.DataFrame(trows); T.to_csv('results/tables/paired_tests.csv', index=False)
print(T.round(3).to_string())
# H1 cells
print('H1', T[(T.mu == 1.0) & T.h.isin([0.3, 0.4, 0.5])].round(4).to_string())
print('H2 violations (h2 below max(mlp,gcn) by >0.02):', T[T.h2_vs_max < -0.02][['mu', 'h', 'h2_vs_max']].round(3).values.tolist())
print('H2 min margin', T.h2_vs_max.min())
# H3
for mu in mus:
    print('winners mu', mu, {h: m.loc[(mu, h)].idxmax() for h in hs})
# H4: crossover = lowest h>=1/3 side? report all h where GCN > MLP mean
for mu in mus:
    print('GCN>MLP at h (mu=%g):' % mu, [h for h in hs if m.loc[(mu, h), 'GCN'] > m.loc[(mu, h), 'MLP']])
# win-count compact table
wt = ['\\begin{tabular}{lcccccccccccc}', '\\toprule', '$\\mu$ \\textbackslash\\ $h$ & ' + ' & '.join(f'{h:.1f}' for h in hs) + ' \\\\', '\\midrule']
for mu in mus:
    wt.append(f'{mu:g} & ' + ' & '.join(m.loc[(mu, h)].idxmax() for h in hs) + ' \\\\')
wt[0] = '\\begin{tabular}{l' + 'c' * len(hs) + '}'
wt += ['\\bottomrule', '\\end{tabular}']
open('results/tables/winners.tex', 'w').write('\n'.join(wt))
# GCN-MLP gap table
gt = ['\\begin{tabular}{l' + 'c' * len(hs) + '}', '\\toprule', '$\\mu$ \\textbackslash\\ $h$ & ' + ' & '.join(f'{h:.1f}' for h in hs) + ' \\\\', '\\midrule']
for mu in mus:
    gt.append(f'{mu:g} & ' + ' & '.join(f'{T[(T.mu==mu)&(T.h==h)].gcn_minus_mlp.values[0]*100:+.1f}' for h in hs) + ' \\\\')
gt += ['\\bottomrule', '\\end{tabular}']
open('results/tables/gcn_mlp_gap.tex', 'w').write('\n'.join(gt))
# --- figures
col = {'MLP': '#555555', 'GCN': '#d95f02', 'H2GCN': '#1b9e77', 'LP': '#7570b3'}
fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.4), sharey=True)
for ax, mu in zip(axs, mus):
    for k in SYS:
        ax.errorbar(hs, m.loc[mu][k], yerr=sd.loc[mu][k] / np.sqrt(5), color=col[k], label=k, marker='o', ms=2.5, lw=1, capsize=1.5)
    ax.axvline(1 / 3, color='k', ls=':', lw=0.7); ax.set_title(f'$\\mu$={mu:g}', fontsize=9); ax.set_xlabel('edge homophily $h$', fontsize=8)
    ax.tick_params(labelsize=7)
axs[0].set_ylabel('test accuracy', fontsize=8); axs[0].legend(fontsize=6.5, loc='lower right')
plt.tight_layout(); plt.savefig('results/figures/acc_vs_h.pdf'); plt.close()
fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.2), sharey=True)
for ax, mu in zip(axs, mus):
    for k in ['GCN', 'H2GCN', 'LP']:
        ax.plot(hs, [m.loc[(mu, h), k] - m.loc[(mu, h), 'MLP'] for h in hs], color=col[k], label=k + ' $-$ MLP', marker='o', ms=2.5, lw=1)
    ax.axhline(0, color='k', lw=0.6); ax.axvline(1 / 3, color='k', ls=':', lw=0.7)
    ax.set_title(f'$\\mu$={mu:g}', fontsize=9); ax.set_xlabel('edge homophily $h$', fontsize=8); ax.tick_params(labelsize=7)
axs[0].set_ylabel('accuracy gain over MLP', fontsize=8); axs[0].legend(fontsize=6.5)
plt.tight_layout(); plt.savefig('results/figures/gain_vs_mlp.pdf'); plt.close()
print('realized h mean abs dev', (df.rh - df.h).abs().mean(), 'max', (df.rh - df.h).abs().max())
# --- main-text table: mu=1, mean +- std over 5 seeds, paired p for GCN-MLP
tex = ['\\begin{tabular}{rccccc}', '\\toprule', '$h$ & MLP & GCN & H2GCN & LP & $p_{\\rm GCN-MLP}$ \\\\', '\\midrule']
for h in hs:
    r = m.loc[(1.0, h)]; s = sd.loc[(1.0, h)]; best = r.idxmax()
    cl = [(f'\\textbf{{{r[k]:.3f}}}' if k == best else f'{r[k]:.3f}') + f'$\\pm${s[k]:.3f}' for k in SYS]
    tex.append(f'{h:.1f} & ' + ' & '.join(cl) + f' & {T[(T.mu==1.0)&(T.h==h)].p_gcn_mlp.values[0]:.3f} \\\\')
tex += ['\\bottomrule', '\\end{tabular}']
open('results/tables/main_mu1.tex', 'w').write('\n'.join(tex))
# --- H2 violations table
V = T[T.h2_vs_max < -0.02]
tex = ['\\begin{tabular}{rrcccc}', '\\toprule', '$\\mu$ & $h$ & MLP & GCN & H2GCN & H2GCN$-$best \\\\', '\\midrule']
for _, r in V.iterrows():
    c = m.loc[(r.mu, r.h)]
    tex.append(f'{r.mu:g} & {r.h:.1f} & {c.MLP:.3f} & {c.GCN:.3f} & {c.H2GCN:.3f} & {r.h2_vs_max:+.3f} \\\\')
tex += ['\\bottomrule', '\\end{tabular}']
open('results/tables/h2_viol.tex', 'w').write('\n'.join(tex))
