"""Tables (results/tables/*.tex) and figures (results/figures/*.pdf) from results/all_runs.csv (made by hyp.py from runs.jsonl)."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.stats import spearmanr
df = pd.read_csv('results/all_runs.csv'); M = df[df.group == 'main']
SYS = ['Additive ridge', 'Pairwise ridge', 'CNN', 'MLP', 'Random']; SH = ['Add.', 'Pair.', 'CNN', 'MLP', 'Rand.']
COL = {'Additive ridge': '#1b9e77', 'Pairwise ridge': '#d95f02', 'CNN': '#7570b3', 'MLP': '#e7298a', 'Random': '#888888'}
tasks = sorted(M.task.unique(), key=lambda t: (int(t.split('_')[1][1:]) , int(t.split('_K')[1])))
tasks = [t for t in ['L15_A4_K0','L15_A4_K1','L15_A4_K2','L15_A4_K4','L20_A20_K0','L20_A20_K1','L20_A20_K2','L20_A20_K4']]
def tt(t): return t.replace('_', r'\_')
# main table: Spearman and design_hit, means
sp = M.groupby(['task', 'name']).spearman.mean().unstack(); hit = M.groupby(['task', 'name']).design_hit.mean().unstack()
ch = M[M.name == 'Random'].groupby('task').frac_mutants_better.mean()  # exact chance hit rate; identical for all systems of a (task, seed)
s = r'\begin{tabular}{l' + 'r' * 5 + '|' + 'r' * 6 + '}\n\\toprule\n & \\multicolumn{5}{c|}{Spearman} & \\multicolumn{6}{c}{design\\_hit}\\\\\nTask & ' + ' & '.join(SH) + ' & ' + ' & '.join(SH) + ' & Chance\\\\\n\\midrule\n'
for t in tasks:
    best_s = max(sp.loc[t, x] for x in SYS[:4]); best_h = max(hit.loc[t, x] for x in SYS[:4])
    c1 = [(r'\textbf{%.3f}' if round(sp.loc[t, x], 3) == round(best_s, 3) and x != 'Random' else '%.3f') % sp.loc[t, x] for x in SYS]
    c2 = [(r'\textbf{%.2f}' if round(hit.loc[t, x], 2) == round(best_h, 2) and x != 'Random' else '%.2f') % hit.loc[t, x] for x in SYS]
    s += tt(t) + ' & ' + ' & '.join(c1) + ' & ' + ' & '.join(c2) + ' & %.3f' % ch.loc[t] + '\\\\\n'
    if t == 'L15_A4_K4': s += '\\midrule\n'
s += '\\bottomrule\n\\end{tabular}\n'
open('results/tables/main_summary.tex', 'w').write(s)
# per-seed spread table (std over seeds) for Spearman and design_hit
sd = M.groupby(['task', 'name']).spearman.std().unstack(); hsd = M.groupby(['task', 'name']).design_hit.std().unstack()
s = r'\begin{tabular}{l' + 'r' * 4 + '|' + 'r' * 5 + '}\n\\toprule\n & \\multicolumn{4}{c|}{SD of Spearman} & \\multicolumn{5}{c}{SD of design\\_hit}\\\\\nTask & ' + ' & '.join(SH[:4]) + ' & ' + ' & '.join(SH) + '\\\\\n\\midrule\n'
for t in tasks:
    s += tt(t) + ' & ' + ' & '.join('%.3f' % sd.loc[t, x] for x in SYS[:4]) + ' & ' + ' & '.join('%.2f' % hsd.loc[t, x] for x in SYS) + '\\\\\n'
    if t == 'L15_A4_K4': s += '\\midrule\n'
open('results/tables/main_sd.tex', 'w').write(s + '\\bottomrule\n\\end{tabular}\n')
# H4 robustness table: rank correlations and paired t-tests on design_hit (same statistics as analysis/hyp.py)
from scipy.stats import ttest_rel, ttest_1samp
def col(name, c='design_hit'): return M[M.name == name].set_index(['task', 'seed'])[c].sort_index()
pw_s, ad_s, pw_h, ad_h, rd_h, chs = col('Pairwise ridge', 'spearman'), col('Additive ridge', 'spearman'), col('Pairwise ridge'), col('Additive ridge'), col('Random'), col('Random', 'frac_mutants_better')
ds, dh = pw_s - ad_s, pw_h - ad_h
def pf(p): return '$<$0.001' if p < 0.001 else '%.2f' % p if p >= 0.0095 else '%.3f' % p
rowsH = []
r = spearmanr(ds, dh); rowsH.append((r'$\rho$, all 40 (task, seed) units', '%.2f' % r[0], pf(r[1])))
k = ds.index.get_level_values(0) != 'L15_A4_K1'; r = spearmanr(ds[k], dh[k]); rowsH.append((r'$\rho$, without L15\_A4\_K1 (35 units)', '%.2f' % r[0], pf(r[1])))
r = spearmanr(ds.groupby(level=0).mean(), dh.groupby(level=0).mean()); rowsH.append((r'$\rho$, the 8 task means', '%.2f' % r[0], pf(r[1])))
rowsH.append(None)
for t in ['L15_A4_K1', 'L15_A4_K2', 'L20_A20_K1']:
    rowsH.append((r'Pair.$-$Add. hit, ' + tt(t), '%.2f' % dh.loc[t].mean(), pf(ttest_rel(pw_h.loc[t], ad_h.loc[t]).pvalue)))
rowsH.append(None)
for t in ['L20_A20_K2', 'L20_A20_K4']:
    rowsH.append((r'Add.$-$Rand. hit, ' + tt(t), '%.2f' % (ad_h.loc[t] - rd_h.loc[t]).mean(), pf(ttest_rel(ad_h.loc[t], rd_h.loc[t]).pvalue)))
    rowsH.append((r'Add.$-$Chance hit, ' + tt(t), '%.3f' % (ad_h.loc[t] - chs.loc[t]).mean(), pf(ttest_1samp(ad_h.loc[t] - chs.loc[t], 0).pvalue)))
s = r'\begin{tabular}{lrr}' + '\n\\toprule\nQuantity & Value & $p$\\\\\n\\midrule\n'
for rw in rowsH: s += '\\midrule\n' if rw is None else ' & '.join(rw) + '\\\\\n'
open('results/tables/h4_summary.tex', 'w').write(s + '\\bottomrule\n\\end{tabular}\n')
# sweep table
S = df[df.group == 'sweep_n']; mm = M[M.task.isin(['L15_A4_K2', 'L20_A20_K1']) & M.name.isin(SYS[:4])]
A_ = pd.concat([S, mm]); A_['n'] = A_.n.astype(int)
tab = A_.groupby(['task', 'n', 'name']).spearman.mean().unstack()
s = r'\begin{tabular}{lr' + 'r' * 4 + 'r}\n\\toprule\nTask & $N$ & ' + ' & '.join(SH[:4]) + ' & Pair.$-$Add.\\\\\n\\midrule\n'
for t in ['L15_A4_K2', 'L20_A20_K1']:
    for n in [250, 500, 1000, 2000, 4000]:
        r = tab.loc[(t, n)]; s += f"{tt(t)} & {n} & " + ' & '.join('%.3f' % r[x] for x in SYS[:4]) + ' & %.3f' % (r['Pairwise ridge'] - r['Additive ridge']) + '\\\\\n'
    if t == 'L15_A4_K2': s += '\\midrule\n'
open('results/tables/sweep_n_summary.tex', 'w').write(s + '\\bottomrule\n\\end{tabular}\n')
# ablation table
Ab = pd.concat([df[df.group == 'abl_pair'], M[M.name == 'Pairwise ridge']])
am = Ab.groupby(['task', 'name']).spearman.mean().unstack(); asd = Ab.groupby(['task', 'name']).spearman.std().unstack()
cols = ['Pairwise ridge', 'Pairwise ridge (r fixed)', 'Pairwise ridge (oracle graph)']
s = r'\begin{tabular}{l' + 'r' * 3 + '}\n\\toprule\nTask & Pair. (tuned $r$) & Pair. ($r{=}1$) & Pair. (oracle graph)\\\\\n\\midrule\n'
for t in tasks: s += tt(t) + ' & ' + ' & '.join('%.3f $\\pm$ %.3f' % (am.loc[t, c], asd.loc[t, c]) for c in cols) + '\\\\\n'
open('results/tables/abl_pair_summary.tex', 'w').write(s + '\\bottomrule\n\\end{tabular}\n')
# Fig 1: Spearman and design_hit vs K
fig, ax = plt.subplots(2, 2, figsize=(7, 3.6), sharex=True)
for j, (L, A) in enumerate([(15, 4), (20, 20)]):
    for i, (met, lab) in enumerate([('spearman', 'test Spearman'), ('design_hit', 'design_hit')]):
        for x in SYS:
            g = M[(M.name == x) & (M.L == L)].groupby('K')[met]
            m, sdv = g.mean(), g.std()
            ax[i, j].errorbar(m.index + (list(COL).index(x) - 2) * 0.05, m.values, sdv.values, label=x, color=COL[x], marker='o', ms=3, lw=1.2, ls='--' if x == 'Random' else '-', capsize=2)
        ax[i, j].set_ylabel(lab); ax[i, j].grid(alpha=.3)
    ax[0, j].set_title(f'L={L}, A={A}, N=1000 (simulated NK)', fontsize=9); ax[1, j].set_xlabel('K'); ax[1, j].set_xticks([0, 1, 2, 4])
ax[0, 0].legend(fontsize=7); plt.tight_layout(); plt.savefig('results/figures/fig_vs_K.pdf'); plt.close()
# Fig 2: N sweep
fig, ax = plt.subplots(1, 2, figsize=(3.5, 2.2), sharey=False)
for k, t in enumerate(['L15_A4_K2', 'L20_A20_K1']):
    for x in SYS[:4]:
        g = A_[(A_.task == t) & (A_.name == x)].groupby('n').spearman; m, sdv = g.mean(), g.std()
        ax[k].errorbar(m.index, m.values, sdv.values, label=x, color=COL[x], marker='o', ms=2.5, lw=1, capsize=1.5)
    ax[k].set_xscale('log'); ax[k].set_xticks([250,1000,4000]); ax[k].set_xticklabels(['250','1000','4000']); ax[k].minorticks_off(); ax[k].set_title(t.replace('_', ' '), fontsize=7); ax[k].set_xlabel('N train', fontsize=7); ax[k].tick_params(labelsize=6); ax[k].grid(alpha=.3)
ax[0].set_ylabel('test Spearman', fontsize=7); ax[0].legend(fontsize=5); plt.tight_layout(); plt.savefig('results/figures/fig_sweep_n.pdf'); plt.close()
# Fig 3: delta spearman vs delta hit (Pairwise - Additive), per (task, seed)
pw = M[M.name == 'Pairwise ridge'].set_index(['task', 'seed']); ad = M[M.name == 'Additive ridge'].set_index(['task', 'seed'])
ds, dh = pw.spearman - ad.spearman, pw.design_hit - ad.design_hit
fig, ax = plt.subplots(figsize=(3.3, 2.5))
for t in tasks:
    ax.scatter(ds.loc[t], dh.loc[t] + np.random.default_rng(0).normal(0, .01, 5), s=10, label=t.replace('_', ' '), marker='o' if t.startswith('L15') else '^')
ax.axhline(0, c='k', lw=.5); ax.axvline(0, c='k', lw=.5); ax.set_xlabel('Spearman: Pairwise $-$ Additive', fontsize=7); ax.set_ylabel('design_hit: Pairwise $-$ Additive', fontsize=7)
ax.tick_params(labelsize=6); ax.legend(fontsize=4.5, ncol=2); plt.tight_layout(); plt.savefig('results/figures/fig_delta.pdf'); plt.close()
print('ok')
