"""Hypothesis tests registered in proposal.md, computed from results/runs.jsonl. Writes results/hypotheses.txt and figures."""
import json, numpy as np, pandas as pd
from scipy.stats import wilcoxon, spearmanr, ttest_1samp
rows = [json.loads(l) for l in open('results/runs.jsonl')]
df = pd.DataFrame([dict(group=r['group'], name=r['name'], task=r['task'], seed=r['seed'], n=r['config'].get('n_train'), **{k: v for k, v in r['metrics'].items()}) for r in rows if r['status'] == 'ok'])
df = df.drop_duplicates(['group', 'name', 'task', 'seed', 'n'])
df[['L', 'A', 'K']] = df.task.str.extract(r'L(\d+)_A(\d+)_K(\d+)').astype(int)
df.to_csv('results/all_runs.csv', index=False)
M = df[df.group == 'main']
out = []
P = lambda *a: out.append(' '.join(str(x) for x in a))
mean = M.groupby(['task', 'name']).spearman.mean().unstack()
P('runs per group', df.groupby('group').size().to_dict())
P('main mean spearman\n', mean.round(3).to_string())
P('main mean design_hit\n', M.groupby(['task', 'name']).design_hit.mean().unstack().round(2).to_string())
# H1
for t in ['L15_A4_K0', 'L20_A20_K0']: P('H1', t, 'Additive mean spearman', round(mean.loc[t, 'Additive ridge'], 4))
# H2
for (L, A) in [(15, 4), (20, 20)]:
    P('H2 additive mean by K', (L, A), [round(mean.loc[f'L{L}_A{A}_K{k}', 'Additive ridge'], 3) for k in [0, 1, 2, 4]])
    t = f'L{L}_A{A}_K1'
    p = M[(M.task == t) & (M.name == 'Pairwise ridge')].set_index('seed').spearman
    a = M[(M.task == t) & (M.name == 'Additive ridge')].set_index('seed').spearman
    d = (p - a).loc[sorted(p.index)]
    P('H2 K=1', t, 'pairwise-additive per seed', d.round(3).tolist(), 'mean', round(d.mean(), 3),
      'wilcoxon one-sided p', wilcoxon(d, alternative='greater').pvalue if (d != 0).any() else None)
# H3
for net in ['CNN', 'MLP']:
    cnt = 0; cells = []
    for t in M.task.unique():
        if t.endswith('K0'): continue
        w = mean.loc[t, net] > mean.loc[t, 'Pairwise ridge']; cnt += int(w); cells.append((t, round(mean.loc[t, net] - mean.loc[t, 'Pairwise ridge'], 3)))
    P('H3', net, 'cells above Pairwise ridge:', cnt, 'of 6', cells)
# H4
pw = M[M.name == 'Pairwise ridge'].set_index(['task', 'seed']); ad = M[M.name == 'Additive ridge'].set_index(['task', 'seed'])
ds = (pw.spearman - ad.spearman); dh = (pw.design_hit - ad.design_hit)
r = spearmanr(ds, dh); P('H4 spearman corr dSpearman vs dhit over', len(ds), 'units:', round(r[0], 3), 'p', round(r[1], 4))
r2 = spearmanr(ds[~ds.index.get_level_values(0).str.endswith('K0')], dh[~dh.index.get_level_values(0).str.endswith('K0')]); P('H4 excluding K=0:', round(r2[0], 3), round(r2[1], 4))
# H4 robustness: leave one task cell out, and correlation over the 8 task means
for t in sorted(M.task.unique()):
    k = ds.index.get_level_values(0) != t; r3 = spearmanr(ds[k], dh[k]); P('H4 leave-one-cell-out, without', t, ': rho', round(r3[0], 3), 'p', round(r3[1], 4), 'n', int(k.sum()))
r4 = spearmanr(ds.groupby(level=0).mean(), dh.groupby(level=0).mean()); P('H4 over the 8 task means: rho', round(r4[0], 3), 'p', round(r4[1], 4))
P('H4 per-task mean dSpearman / mean dhit / SD dhit (Pairwise-Additive)\n', pd.DataFrame({'dspearman': ds.groupby(level=0).mean(), 'dhit': dh.groupby(level=0).mean(), 'dhit_sd': dh.groupby(level=0).std()}).round(3).to_string())
hit = M.groupby(['task', 'name']).design_hit.mean().unstack()
P('H4 learned vs Random hit, K<=1 cells\n', hit.loc[[t for t in hit.index if t.endswith('K0') or t.endswith('K1')]].round(2).to_string())
# design_hit: seed SD, exact chance rate (frac_mutants_better, identical for all systems of a (task, seed)), paired t-tests
P('main SD design_hit\n', M.groupby(['task', 'name']).design_hit.std().unstack().round(2).to_string())
ch = M[M.name == 'Random'].set_index(['task', 'seed']).frac_mutants_better
assert all(np.allclose(M[M.name == x].set_index(['task', 'seed']).frac_mutants_better.loc[ch.index], ch) for x in M.name.unique())
P('exact chance hit rate (mean frac_mutants_better)\n', ch.groupby(level=0).mean().round(3).to_string())
rd = M[M.name == 'Random'].set_index(['task', 'seed']).design_hit
for t in sorted(M.task.unique()):
    for x in ['Additive ridge', 'Pairwise ridge', 'CNN', 'MLP']:
        h = M[(M.name == x) & (M.task == t)].set_index('seed').design_hit.sort_index()
        d1, d2 = h - rd.loc[t].sort_index(), h - ch.loc[t].sort_index()
        p1 = ttest_1samp(d1, 0).pvalue if d1.std() > 0 else float('nan'); p2 = ttest_1samp(d2, 0).pvalue if d2.std() > 0 else float('nan')
        P('design_hit', t, x, 'per seed', h.round(1).tolist(), 'mean', round(h.mean(), 2), '| vs Random: diff', round(d1.mean(), 2), 'paired t p', round(p1, 3), '| vs exact chance: diff', round(d2.mean(), 3), 'paired t p', round(p2, 3))
# H5
S = df[(df.group == 'sweep_n')].copy()
mm = df[(df.group == 'main') & df.task.isin(['L15_A4_K2', 'L20_A20_K1']) & df.name.isin(['Pairwise ridge', 'Additive ridge', 'CNN', 'MLP'])]
A_ = pd.concat([S, mm])
tab = A_.groupby(['task', 'name', 'n']).spearman.mean().unstack()
P('sweep mean spearman\n', tab.round(3).to_string())
for t in ['L15_A4_K2', 'L20_A20_K1']:
    g = {n: tab.loc[(t, 'Pairwise ridge'), n] - tab.loc[(t, 'Additive ridge'), n] for n in [250, 500, 1000, 2000, 4000]}
    P('H5 gap pairwise-additive', t, {k: round(v, 3) for k, v in g.items()})
# ablation
Ab = df[df.group == 'abl_pair']
al = pd.concat([Ab, M[M.name == 'Pairwise ridge']])
P('ablation mean spearman\n', al.groupby(['task', 'name']).spearman.mean().unstack().round(3).to_string())
for t in sorted(M.task.unique()):
    b = M[(M.name == 'Pairwise ridge') & (M.task == t)].set_index('seed').spearman.sort_index()
    for c in ['Pairwise ridge (r fixed)', 'Pairwise ridge (oracle graph)']:
        d = Ab[(Ab.name == c) & (Ab.task == t)].set_index('seed').spearman.sort_index() - b
        P('ablation delta vs tuned Pairwise', t, c, 'mean', round(d.mean(), 3), 'paired t p', round(ttest_1samp(d, 0).pvalue, 4))
# sweep details quoted in the paper
for t in ['L15_A4_K2', 'L20_A20_K1']:
    for net in ['CNN', 'MLP']:
        P('sweep', t, net, 'minus Additive by N', {n: round(tab.loc[(t, net), n] - tab.loc[(t, 'Additive ridge'), n], 4) for n in [250, 500, 1000, 2000, 4000]},
          '| Pairwise minus', net, 'at N=4000', round(tab.loc[(t, 'Pairwise ridge'), 4000] - tab.loc[(t, net), 4000], 3))
P('sweep SD spearman\n', A_.groupby(['task', 'name', 'n']).spearman.std().unstack().round(3).to_string())
# runtime from the registry
ok = [r for r in rows if r['status'] == 'ok']; du = np.array([r['provenance']['duration_s'] for r in ok])
st = pd.to_datetime([r['provenance']['started'] for r in ok]); en = pd.to_datetime([r['logged'] for r in ok])
P('runtime: runs', len(du), 'max duration_s', du.max(), 'runs over 20 s', int((du > 20).sum()), 'runs over 15 s', int((du > 15).sum()), 'sum of durations min', round(du.sum() / 60, 1), 'registry span min', round((en.max() - st.min()).total_seconds() / 60, 1))
P('hp r chosen (main Pairwise) counts\n', M[M.name == 'Pairwise ridge'].groupby(['task']).hp_r.apply(lambda s: s.value_counts().to_dict()).to_string())
open('results/hypotheses.txt', 'w').write('\n'.join(out)); print('\n'.join(out))
