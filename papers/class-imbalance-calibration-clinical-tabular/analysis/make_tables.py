"""Tables and figures computed from results/runs.jsonl only (the run registry).
All p-values are two-sided paired t-tests over the 10 seeds (scipy.stats.ttest_rel), unadjusted; they are
cross-checked at the end against the `rh compare` outputs in results/tables/compare/ (experiments/run_compare.sh)."""
import sys, glob, warnings, numpy as np, pandas as pd
sys.path.insert(0, 'analysis')
from load import load
from scipy.stats import ttest_rel
warnings.filterwarnings('ignore', category=RuntimeWarning)  # ttest_rel on identical arrays (threshold vs none)
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

d = load()
main = d[d.group == 'main']; abl = d[d.group == 'abl_priorcorr']; sw = d[d.group == 'sweep_smote_ratio']
TASKS = ['bc_natural', 'bc_1to5', 'bc_1to20', 'bc_1to50']
TL = {'bc_natural': 'nat.', 'bc_1to5': '1:5', 'bc_1to20': '1:20', 'bc_1to50': '1:50'}
SYS = ['no correction', 'reweight', 'ROS', 'SMOTE', 'threshold']
CORR = ['reweight', 'ROS', 'SMOTE']
STAR = '\\rlap{$^{*}$}'  # zero-width star so it cannot collide with the next column
ARMS = [f'{m} + {s}' for m in ['LR', 'GB'] for s in SYS]
f3 = lambda x: f'{x:.3f}'
out = 'results/tables/'

def ms(df, name, task, met, p=3):
    v = df[(df.name == name) & (df.task == task)][met].values
    return f'{v.mean():.{p}f} $\\pm$ {v.std(ddof=1):.{p}f}'

def mean(df, name, task, met):
    return df[(df.name == name) & (df.task == task)][met].mean()

def vals(df, name, task, met):
    return df[(df.name == name) & (df.task == task)].sort_values('seed')[met].values

def med(df, name, task, met):
    v = df[(df.name == name) & (df.task == task)][met].values
    q = np.percentile(v, [25, 50, 75]); return f'{q[1]:.2f} [{q[0]:.2f}, {q[2]:.2f}]'

def paired(df_x, nx, df_y, ny, t, met):
    """mean paired difference x - y over seeds, two-sided paired t-test p, number of seeds with x < y"""
    x = vals(df_x, nx, t, met); y = vals(df_y, ny, t, met)
    return float((x - y).mean()), float(ttest_rel(x, y).pvalue), int((x < y).sum())

# T1: primary task bc_1to20 (mean +- sd over 10 seeds; slope columns median [IQR] because slopes are heavy-tailed).
# Threshold rows are omitted: their probabilities are those of no correction (see h3_maxabsdiff.csv).
PROB = [a for a in ARMS if not a.endswith('threshold')]
mets = [('auroc', 'AUROC'), ('auprc', 'AUPRC'), ('brier', 'Brier'), ('cal_slope', 'slope $b$'), ('slope_dev', '$|b-1|$'), ('citl_abs', '$|a|$')]
L = ['\\begin{tabular}{l' + 'c' * len(mets) + '}', '\\toprule', 'System & ' + ' & '.join(h for _, h in mets) + ' \\\\', '\\midrule']
for i, a in enumerate(PROB):
    L.append(a + ' & ' + ' & '.join(med(main, a, 'bc_1to20', m) if m in ('cal_slope', 'slope_dev') else ms(main, a, 'bc_1to20', m) for m, _ in mets) + ' \\\\')
    if i == 3: L.append('\\midrule')
L += ['\\bottomrule', '\\end{tabular}']
open(out + 'main_1to20.tex', 'w').write('\n'.join(L))

# T2: regimes: AUROC and Brier means over tasks
L = ['\\begin{tabular}{l' + 'c' * 12 + '}', '\\toprule',
     ' & \\multicolumn{4}{c}{AUROC} & \\multicolumn{4}{c}{AUPRC} & \\multicolumn{4}{c}{Brier} \\\\',
     'System & ' + ' & '.join([TL[t] for t in TASKS] * 3) + ' \\\\', '\\midrule']
for i, a in enumerate(PROB):
    L.append(a + ' & ' + ' & '.join(f3(mean(main, a, t, m)) for m in ['auroc', 'auprc', 'brier'] for t in TASKS) + ' \\\\')
    if i == 3: L.append('\\midrule')
L += ['\\bottomrule', '\\end{tabular}']
open(out + 'regimes.tex', 'w').write('\n'.join(L))

# T3: paired differences (correction - none, same learner), 1:5, 1:20, 1:50
tt = ['bc_1to5', 'bc_1to20', 'bc_1to50']; dm = ['auroc', 'auprc', 'brier']
L = ['\\begin{tabular}{l' + 'c' * 9 + '}', '\\toprule',
     ' & \\multicolumn{3}{c}{1:5} & \\multicolumn{3}{c}{1:20} & \\multicolumn{3}{c}{1:50} \\\\',
     'Correction & ' + ' & '.join(['$\\Delta$AUROC', '$\\Delta$AUPRC', '$\\Delta$Brier'] * 3) + ' \\\\', '\\midrule']
for m in ['LR', 'GB']:
    for s_ in CORR:
        r = [f'{m} + {s_}']
        for t in tt:
            for met in dm:
                dl, p, _ = paired(main, f'{m} + {s_}', main, f'{m} + no correction', t, met)
                r.append(f'{dl:+.3f}' + (STAR if p < 0.05 else ''))
        L.append(' & '.join(r) + ' \\\\')
L += ['\\bottomrule', '\\end{tabular}']
open(out + 'deltas.tex', 'w').write('\n'.join(L))
# every correction-vs-none paired test (same learner), all tasks and metrics
ALLM = ['auroc', 'auprc', 'brier', 'cal_citl', 'citl_abs', 'cal_slope', 'slope_dev', 'mean_pred', 'sens', 'spec', 'bal_acc']
deltas = pd.DataFrame([(m, s_, t, met, mean(main, f'{m} + no correction', t, met), mean(main, f'{m} + {s_}', t, met), *paired(main, f'{m} + {s_}', main, f'{m} + no correction', t, met))
                       for m in ['LR', 'GB'] for s_ in CORR for t in TASKS for met in ALLM],
                      columns=['learner', 'correction', 'task', 'metric', 'none_mean', 'corr_mean', 'delta', 'paired_p', 'n_seeds_lower'])
deltas.to_csv(out + 'deltas_all.csv', index=False)

# T4: calibration: slope (median [IQR]) and |CITL| mean, per regime
L = ['\\begin{tabular}{l' + 'c' * 4 + '}', '\\toprule', 'System & ' + ' & '.join(TL[t] for t in TASKS) + ' \\\\', '\\midrule']
for i, a in enumerate(ARMS):
    if a.endswith('threshold'): continue
    L.append(a + ' & ' + ' & '.join(med(main, a, t, 'cal_slope') for t in TASKS) + ' \\\\')
    if i == 4: L.append('\\midrule')
L += ['\\bottomrule', '\\end{tabular}']
open(out + 'slopes.tex', 'w').write('\n'.join(L))

# T5: operating point of every system: sensitivity / specificity / balanced accuracy at its cut-off
# (0.5; training prevalence for threshold moving). Star: paired p < 0.05 against no correction, same learner.
om = [('sens', 'Sensitivity'), ('spec', 'Specificity'), ('bal_acc', 'Balanced accuracy')]
L = ['\\begin{tabular}{l' + 'c' * 12 + '}', '\\toprule',
     ' & ' + ' & '.join(f'\\multicolumn{{4}}{{c}}{{{h}}}' for _, h in om) + ' \\\\',
     'System & ' + ' & '.join([TL[t] for t in TASKS] * 3) + ' \\\\', '\\midrule']
for i, a in enumerate(ARMS):
    m = a[:2]; r = [a]
    for k, _ in om:
        for t in TASKS:
            c = f3(mean(main, a, t, k))
            if not a.endswith('no correction') and paired(main, a, main, f'{m} + no correction', t, k)[1] < 0.05: c += STAR
            r.append(c)
    L.append(' & '.join(r) + ' \\\\')
    if i == 4: L.append('\\midrule')
L += ['\\bottomrule', '\\end{tabular}']
open(out + 'operating.tex', 'w').write('\n'.join(L))
# exact equality check for H3
eq = {}
for m in ['LR', 'GB']:
    for t in TASKS:
        for k in ['auroc', 'auprc', 'brier', 'cal_slope']:
            eq[(m, t, k)] = float(np.max(np.abs(vals(main, f'{m} + no correction', t, k) - vals(main, f'{m} + threshold', t, k))))
pd.Series({'/'.join(k): v for k, v in eq.items()}).to_csv(out + 'h3_maxabsdiff.csv')
print('H3 max abs diff', max(eq.values()))
# paired operating-point tests: every strategy vs no correction, and threshold moving vs every correction
rows = []
for m in ['LR', 'GB']:
    for t in TASKS:
        for k in ['sens', 'spec', 'bal_acc']:
            for s_ in ['threshold'] + CORR:
                rows.append((m, t, k, s_, 'no correction', *paired(main, f'{m} + {s_}', main, f'{m} + no correction', t, k)[:2]))
            for s_ in CORR:
                rows.append((m, t, k, 'threshold', s_, *paired(main, f'{m} + threshold', main, f'{m} + {s_}', t, k)[:2]))
thr = pd.DataFrame(rows, columns=['learner', 'task', 'metric', 'system', 'reference', 'delta', 'paired_p'])
thr.to_csv(out + 'threshold_tests.csv', index=False)

# T6: prior-correction ablation: Brier gap to no correction, raw vs prior-corrected
L = ['\\begin{tabular}{l' + 'c' * 8 + '}', '\\toprule', ' & ' + ' & '.join(f'\\multicolumn{{2}}{{c}}{{{TL[t]}}}' for t in TASKS) + ' \\\\',
     'System & ' + ' & '.join(['raw', '+prior'] * 4) + ' \\\\', '\\midrule']
for m in ['LR', 'GB']:
    for s in ['reweight', 'ROS', 'SMOTE']:
        r = [f'{m} + {s}']
        for t in TASKS:
            b0 = mean(main, f'{m} + no correction', t, 'brier')
            r += [f'{mean(main, f"{m} + {s}", t, "brier") - b0:+.4f}', f'{mean(abl, f"{m} + {s} + prior corr", t, "brier") - b0:+.4f}']
        L.append(' & '.join(r) + ' \\\\')
L += ['\\bottomrule', '\\end{tabular}']
open(out + 'abl_prior_brier.tex', 'w').write('\n'.join(L))
# T7: calibration-in-the-large per task: signed a (raw), |a| (raw), |a| with the prior-shift offset.
# Star on signed a: paired p < 0.05 against no correction, same learner.
L = ['\\begin{tabular}{l' + 'c' * 12 + '}', '\\toprule', ' & ' + ' & '.join(f'\\multicolumn{{3}}{{c}}{{{TL[t]}}}' for t in TASKS) + ' \\\\',
     'System & ' + ' & '.join(['$a$', '$|a|$', '$|a|_{\\text{off}}$'] * 4) + ' \\\\', '\\midrule']
for m in ['LR', 'GB']:
    L.append(f'{m} + no correction & ' + ' & '.join(f'{mean(main, f"{m} + no correction", t, "cal_citl"):+.2f} & {mean(main, f"{m} + no correction", t, "citl_abs"):.2f} & --' for t in TASKS) + ' \\\\')
    for s_ in CORR:
        r = [f'{m} + {s_}']
        for t in TASKS:
            p = paired(main, f'{m} + {s_}', main, f'{m} + no correction', t, 'cal_citl')[1]
            r += [f'{mean(main, f"{m} + {s_}", t, "cal_citl"):+.2f}' + (STAR if p < 0.05 else ''), f'{mean(main, f"{m} + {s_}", t, "citl_abs"):.2f}',
                  f'{mean(abl, f"{m} + {s_} + prior corr", t, "citl_abs"):.2f}']
        L.append(' & '.join(r) + ' \\\\')
    if m == 'LR': L.append('\\midrule')
L += ['\\bottomrule', '\\end{tabular}']
open(out + 'citl.tex', 'w').write('\n'.join(L))
# ablation summary csv: Brier gap, |a| and signed a, raw vs offset, with paired tests (offset vs raw)
rr = []
for m in ['LR', 'GB']:
    for s_ in CORR:
        for t in TASKS:
            n0, nr, npc = f'{m} + no correction', f'{m} + {s_}', f'{m} + {s_} + prior corr'
            b0 = mean(main, n0, t, 'brier'); gr = mean(main, nr, t, 'brier') - b0; gp = mean(abl, npc, t, 'brier') - b0
            da, pa, _ = paired(abl, npc, main, nr, t, 'citl_abs')
            rr.append((m, s_, t, gr, gp, abs(gp) < abs(gr), abs(gp) <= 0.005, paired(abl, npc, main, nr, t, 'brier')[1],
                       mean(main, nr, t, 'citl_abs'), mean(abl, npc, t, 'citl_abs'), da, pa,
                       mean(main, nr, t, 'cal_citl'), mean(abl, npc, t, 'cal_citl'),
                       float(np.max(np.abs(vals(main, nr, t, 'auroc') - vals(abl, npc, t, 'auroc')))),
                       float(np.max(np.abs(vals(main, nr, t, 'auprc') - vals(abl, npc, t, 'auprc'))))))
ab = pd.DataFrame(rr, columns=['learner', 'corr', 'task', 'brier_gap_raw', 'brier_gap_offset', 'gap_smaller_with_offset', 'offset_gap_within_0.005', 'brier_p_offset_vs_raw',
                               'citl_abs_raw', 'citl_abs_offset', 'citl_abs_delta', 'citl_abs_p', 'citl_raw', 'citl_offset', 'auroc_max_abs_diff', 'auprc_max_abs_diff'])
ab.to_csv(out + 'abl_prior_summary.csv', index=False)

# Figures
plt.rcParams.update({'font.size': 8})
cols = {'reweight': '#1b9e77', 'ROS': '#d95f02', 'SMOTE': '#7570b3'}
def band(v): return 1.96 * v.std(ddof=1) / np.sqrt(len(v))  # normal-approximation 95% interval
for met, fn, yl in [('brier', 'fig_dbrier', '$\\Delta$ Brier vs no correction'), ('auprc', 'fig_dauprc', '$\\Delta$ AUPRC vs no correction')]:
    fig, ax = plt.subplots(1, 2, figsize=(3.5, 1.65), sharey=True)
    for j, m in enumerate(['LR', 'GB']):
        for k, s in enumerate(['reweight', 'ROS', 'SMOTE']):
            mu, ci = [], []
            for t in TASKS:
                dl = vals(main, f'{m} + {s}', t, met) - vals(main, f'{m} + no correction', t, met)
                mu.append(dl.mean()); ci.append(band(dl))
            ax[j].errorbar(np.arange(4) + 0.08 * (k - 1), mu, yerr=ci, marker='o', ms=3, lw=1, capsize=2, color=cols[s], label=s)
        ax[j].axhline(0, color='k', lw=0.6); ax[j].set_title(m); ax[j].set_xticks(range(4)); ax[j].set_xticklabels([TL[t] for t in TASKS])
    ax[0].set_ylabel(yl); ax[0].legend(frameon=False, fontsize=6)
    fig.tight_layout(); fig.savefig(f'results/figures/{fn}.pdf'); plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(3.5, 1.65), sharey=True)
for j, m in enumerate(['LR', 'GB']):
    for s, c in [('no correction', 'k'), ('reweight', cols['reweight']), ('ROS', cols['ROS']), ('SMOTE', cols['SMOTE'])]:
        q = np.array([np.percentile(vals(main, f'{m} + {s}', t, 'cal_slope'), [25, 50, 75]) for t in TASKS])
        ax[j].errorbar(np.arange(4) + 0.08 * (['no correction', 'reweight', 'ROS', 'SMOTE'].index(s) - 1.5), q[:, 1], yerr=[q[:, 1] - q[:, 0], q[:, 2] - q[:, 1]],
                       marker='o', ms=3, lw=1, capsize=2, color=c, label=s)
    ax[j].axhline(1, color='gray', ls='--', lw=0.6); ax[j].set_title(m); ax[j].set_xticks(range(4)); ax[j].set_xticklabels([TL[t] for t in TASKS]); ax[j].set_yscale('log')
ax[0].set_ylabel('calibration slope (median, IQR)'); ax[0].legend(frameon=False, fontsize=6)
fig.tight_layout(); fig.savefig('results/figures/fig_slope.pdf'); plt.close(fig)

# sweep: SMOTE target ratio at 1:20 (ratio 1.0 = main group rows)
sm = pd.concat([sw.assign(ratio=sw.smote_ratio), main[(main.name.str.endswith('SMOTE')) & (main.task == 'bc_1to20')].assign(ratio=1.0)])
nn = main[(main.name.str.endswith('no correction')) & (main.task == 'bc_1to20')]
fig, ax = plt.subplots(1, 2, figsize=(3.5, 1.65))
rows = []
for j, (met, yl) in enumerate([('brier', 'Brier'), ('auprc', 'AUPRC')]):
    for m, c in [('LR', 'C0'), ('GB', 'C3')]:
        g = sm[sm.name == f'{m} + SMOTE'].groupby('ratio')[met]
        mu, sd, n = g.mean(), g.std(ddof=1), g.count()
        ax[j].errorbar(mu.index, mu.values, yerr=1.96 * sd / np.sqrt(n), marker='o', ms=3, lw=1, capsize=2, color=c, label=f'{m} + SMOTE')
        b = nn[nn.name == f'{m} + no correction'][met].mean()
        ax[j].axhline(b, color=c, ls=':', lw=0.8)
        for r_, v_ in mu.items(): rows.append((m, met, r_, v_, b))
    ax[j].set_xlabel('SMOTE target ratio'); ax[j].set_ylabel(yl)
ax[0].legend(frameon=False, fontsize=6)
fig.tight_layout(); fig.savefig('results/figures/fig_sweep_smote.pdf'); plt.close(fig)
pd.DataFrame(rows, columns=['learner', 'metric', 'ratio', 'mean', 'none_mean']).to_csv(out + 'sweep_summary.csv', index=False)
# sweep table
L = ['\\begin{tabular}{llccccc}', '\\toprule', 'Learner & Metric & 0.10 & 0.25 & 0.50 & 0.75 & 1.00 \\\\', '\\midrule']
for m in ['LR', 'GB']:
    for met, yl in [('brier', 'Brier'), ('auprc', 'AUPRC'), ('auroc', 'AUROC'), ('citl_abs', '$|a|$')]:
        g = sm[sm.name == f'{m} + SMOTE'].groupby('ratio')[met].mean()
        L.append(f'{m} & {yl} & ' + ' & '.join(f'{g[r]:.3f}' for r in [0.1, 0.25, 0.5, 0.75, 1.0]) + ' \\\\')
L += ['\\bottomrule', '\\end{tabular}']
open(out + 'sweep_smote.tex', 'w').write('\n'.join(L))

# Counts quoted in the paper (printed so that every count in the text has a line in the log of this script)
def cnt(msg, mask): print(f'{msg}: {int(mask.sum())} of {len(mask)}')
D = deltas; hi = D.task.isin(['bc_1to20', 'bc_1to50']); imb = D.task != 'bc_natural'
print('--- counts')
print('max |dAUROC| LR, all tasks:', D[(D.learner == 'LR') & (D.metric == 'auroc')].delta.abs().max())
cnt('GB dAUROC/dAUPRC > 0 at 1:5-1:50', D[(D.learner == 'GB') & imb & D.metric.isin(['auroc', 'auprc'])].delta > 0)
x = D[D.metric.isin(['auroc', 'auprc'])]; print('H1 refuting cells (gain >= 0.01, p < 0.05):'); print(x[(x.delta >= 0.01) & (x.paired_p < 0.05)].to_string(index=False))
cnt('Brier higher with correction at 1:20, 1:50', D[hi & (D.metric == 'brier')].delta > 0)
print('min p Brier at 1:20, 1:50:', D[hi & (D.metric == 'brier')].paired_p.min())
cnt('|a| higher with correction at 1:20, 1:50', D[hi & (D.metric == 'citl_abs')].delta > 0)
print('min p |a| at 1:20, 1:50:', D[hi & (D.metric == 'citl_abs')].paired_p.min())
for lr in ['LR', 'GB']:
    for met in ['cal_citl', 'cal_slope', 'slope_dev', 'mean_pred', 'sens', 'spec', 'bal_acc']:
        for nm, mk in [('nat', D.task == 'bc_natural'), ('1:5-1:50', imb)]:
            z = D[(D.learner == lr) & (D.metric == met) & mk]
            print(f'{lr} {met} {nm}: delta {z.delta.min():+.4f}..{z.delta.max():+.4f}, p {z.paired_p.min():.2g}..{z.paired_p.max():.2g}, p<0.05 in {(z.paired_p < 0.05).sum()} of {len(z)}')
for lr in ['LR', 'GB']:
    for met in ['sens', 'spec', 'bal_acc']:
        for t in TASKS:
            z = thr[(thr.learner == lr) & (thr.metric == met) & (thr.task == t)]
            a_ = z[(z.system == 'threshold') & (z.reference == 'no correction')].iloc[0]; b_ = z[(z.system == 'threshold') & (z.reference != 'no correction')]
            print(f'{lr} {met} {TL[t]}: threshold - none {a_.delta:+.4f} p={a_.paired_p:.2g}; threshold - corrections {b_.delta.min():+.4f}..{b_.delta.max():+.4f} p {b_.paired_p.min():.2g}..{b_.paired_p.max():.2g}')
cnt('offset: Brier gap smaller in magnitude', ab.gap_smaller_with_offset)
for lr in ['LR', 'GB']: cnt(f'  of which {lr}', ab[ab.learner == lr].gap_smaller_with_offset)
cnt('offset: gap within 0.005 (H4)', ab['offset_gap_within_0.005']); cnt('raw gap within 0.005', ab.brier_gap_raw.abs() <= 0.005)
cnt('offset: mean |a| higher than raw', ab.citl_abs_delta > 0); cnt('offset: |a| higher with p < 0.05', (ab.citl_abs_delta > 0) & (ab.citl_abs_p < 0.05))
print('offset: max AUROC / AUPRC change in any run:', ab.auroc_max_abs_diff.max(), ab.auprc_max_abs_diff.max(), 'runs with a change:', int((ab.auroc_max_abs_diff > 1e-12).sum()), 'cell(s)')
print('GB AUPRC sd at 1:20:', [round(float(vals(main, f'GB + {s_}', 'bc_1to20', 'auprc').std(ddof=1)), 3) for s_ in SYS[:4]])
print('extremes: slope', d.cal_slope.min(), d.cal_slope.max(), '| a', d.cal_citl.min(), d.cal_citl.max(), '| AUROC min', d.auroc.min(), '| sens min', d.sens.min())
print('n paired tests written:', len(deltas) + len(thr) + 2 * len(ab))

# Cross-check against rh compare (results/tables/compare/*.csv, experiments/run_compare.sh)
cmp_ = pd.concat([pd.read_csv(f) for f in glob.glob(out + 'compare/*.csv')])
key = {(r.ref, r['name'], r.task, r.metric): r.paired_p for _, r in cmp_.iterrows()}
mx, n = 0.0, 0
for _, r in deltas.iterrows():
    k = (f'{r.learner} + no correction', f'{r.learner} + {r.correction}', r.task, r.metric)
    if k in key: mx = max(mx, abs(key[k] - r.paired_p)); n += 1
for _, r in thr.iterrows():
    k = (f'{r.learner} + {r.reference}', f'{r.learner} + {r.system}', r.task, r.metric)
    if k not in key: k = (f'{r.learner} + {r.system}', f'{r.learner} + {r.reference}', r.task, r.metric)
    if k in key: mx = max(mx, abs(key[k] - r.paired_p)); n += 1
print(f'rh compare cross-check: {n} paired p-values matched, max abs difference {mx:.2e}')
