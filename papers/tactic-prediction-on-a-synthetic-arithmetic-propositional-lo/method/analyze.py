"""Derived statistics and figures from the raw per-run metric files (results/raw). Paired t-tests over the 5 seeds
(the test problems of a (task, seed) pair are identical for every system)."""
import json, os, sys
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RAW = 'results/raw'
SEEDS = range(5)
TESTS = ['test_11_20', 'test_21_40', 'test_41_70']
SHORT = {'test_11_20': 't11', 'test_21_40': 't21', 'test_41_70': 't41'}
out = {}


def load(pattern, task, metric='solved', **kw):
    return np.array([json.load(open(f'{RAW}/{pattern.format(task=task, s=s, **kw)}.json'))[metric] for s in SEEDS])


SYS = {'bfs': 'main_bfs_{task}_{s}', 'heur': 'main_heur_{task}_{s}', 'mlp': 'main_mlp_{task}_{s}', 'tf': 'main_tf_{task}_{s}',
       'greedy': 'abl_search_greedy_{task}_{s}', 'tfrank': 'abl_search_rank_{task}_{s}',
       'mlprank': 'abl_search_mlprank_{task}_{s}', 'lp': 'abl_pos_lp_{task}_{s}'}
PAIRS = [('greedy', 'tf'), ('tfrank', 'tf'), ('mlprank', 'mlp'), ('mlprank', 'heur'), ('greedy', 'heur'), ('lp', 'tf'),
         ('mlp', 'tf'), ('tfrank', 'heur')]
for t in TESTS:
    for a, b in PAIRS:
        x, y = load(SYS[a], t), load(SYS[b], t)
        out[f'd_{a}_{b}_{SHORT[t]}'] = float((x - y).mean())
        out[f'p_{a}_{b}_{SHORT[t]}'] = float(stats.ttest_rel(x, y).pvalue)
    for s_ in ['mlprank', 'tfrank', 'greedy']:
        out[f'm_{s_}_{SHORT[t]}'] = float(load(SYS[s_], t).mean())
        out[f'sd_{s_}_{SHORT[t]}'] = float(load(SYS[s_], t).std(ddof=1))
    out[f'm_lp_{SHORT[t]}'] = float(load(SYS['lp'], t).mean())
    out[f'sd_lp_{SHORT[t]}'] = float(load(SYS['lp'], t).std(ddof=1))
    # H3 gap: transformer - heuristic
    out[f'gap_tf_heur_{SHORT[t]}'] = float((load(SYS['tf'], t) - load(SYS['heur'], t)).mean())
    out[f'gap_mlp_heur_{SHORT[t]}'] = float((load(SYS['mlp'], t) - load(SYS['heur'], t)).mean())

# training-size sweep (20000 = main transformer rows)
NT = [1000, 4000, 10000, 20000]
nt = {}
for t in ['test_11_20', 'test_41_70']:
    for n in NT:
        v = load(SYS['tf'], t) if n == 20000 else load('sweep_ntrain_n%d_{task}_{s}' % n, t)
        nt[(t, n)] = v
        out[f'nt{n}_{SHORT[t]}_m'] = float(v.mean()); out[f'nt{n}_{SHORT[t]}_sd'] = float(v.std(ddof=1))
# budget sweep on the largest bin (100 = main rows)
BUD = [25, 50, 100, 200]
bud = {}
for name, tag, main in [('Transformer policy', 'tf', 'tf'), ('Hand heuristic', 'h', 'heur'), ('BFS', 'b', 'bfs')]:
    for b in BUD:
        v = load(SYS[main], 'test_41_70') if b == 100 else load('sweep_budget_%s%d_test_41_70_{s}' % (tag, b), 'x')
        bud[(name, b)] = v
        out[f'bud{b}_{tag}_m'] = float(v.mean()); out[f'bud{b}_{tag}_sd'] = float(v.std(ddof=1))

# figures
plt.rcParams.update({'font.size': 8})
fig, ax = plt.subplots(figsize=(3.4, 2.4))
for t, c in [('test_11_20', '#1f77b4'), ('test_41_70', '#d62728')]:
    m = [nt[(t, n)].mean() for n in NT]; sd = [nt[(t, n)].std(ddof=1) for n in NT]
    ax.errorbar(NT, m, yerr=sd, marker='o', capsize=2, color=c, label=t.replace('test_', 'bin ').replace('_', '-'))
ax.set_xscale('log'); ax.set_xlabel('training sequents'); ax.set_ylabel('solved (100 exp.)'); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig('results/figures/sweep_ntrain_fig.pdf'); plt.close(fig)
fig, ax = plt.subplots(figsize=(3.4, 2.4))
for (name, c) in [('Transformer policy', '#d62728'), ('Hand heuristic', '#2ca02c'), ('BFS', '#7f7f7f')]:
    m = [bud[(name, b)].mean() for b in BUD]; sd = [bud[(name, b)].std(ddof=1) for b in BUD]
    ax.errorbar(BUD, m, yerr=sd, marker='o', capsize=2, color=c, label=name)
ax.set_xscale('log'); ax.set_xlabel('expansion budget'); ax.set_ylabel('solved (bin 41-70)'); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig('results/figures/sweep_budget_fig.pdf'); plt.close(fig)
fig, ax = plt.subplots(figsize=(3.4, 2.5))
names = [('bfs', 'BFS'), ('heur', 'Heuristic'), ('tf', 'Transf.'), ('mlp', 'MLP'), ('greedy', 'Transf. greedy'), ('mlprank', 'MLP rank')]
w = 0.13
for i, (k, lab) in enumerate(names):
    m = [load(SYS[k], t).mean() for t in TESTS]; sd = [load(SYS[k], t).std(ddof=1) for t in TESTS]
    ax.bar(np.arange(3) + (i - 2.5) * w, m, w, yerr=sd, capsize=1, label=lab)
ax.set_xticks(range(3)); ax.set_xticklabels(['11-20', '21-40', '41-70']); ax.set_xlabel('connectives in test sequent')
ax.set_ylabel('solved (100 exp.)'); ax.set_ylim(0, 1.35); ax.legend(frameon=False, fontsize=6, ncol=3, loc='upper center')
fig.tight_layout(); fig.savefig('results/figures/perbin_fig.pdf'); plt.close(fig)
print('config', json.dumps({'seeds': list(SEEDS)}))
print('final', json.dumps(out))
json.dump(out, open(sys.argv[1], 'w'))
