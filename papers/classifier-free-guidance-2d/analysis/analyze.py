"""Hypothesis tests, tables and figures, all read from results/runs.jsonl."""
import sys, numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, 'analysis')
from collect import load
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
df = load(); T = 'results/tables/'; F = 'results/figures/'
ov = df[df.task == 'mix_overlap']; sp = df[df.task == 'mix_sep']
def get(d, group=None, **kw):
    m = d if group is None else d[d.group == group]
    for k, v in kw.items(): m = m[np.isclose(m[k], v)]
    return m.sort_values('seed')
unG = get(ov, 'main', w=0, tau=1); cfg = get(ov, 'main', w=3, tau=1); lt = get(ov, 'main', w=0, tau=0.5)
# ---- hypothesis tests
rows = []
def paired(h, desc, a, b, metric):
    t = stats.ttest_rel(a[metric].values, b[metric].values)
    diff = a[metric].values - b[metric].values
    rows.append((h, desc, metric, diff.mean(), t.pvalue, diff.mean() / diff.std(ddof=1)))
paired('H1', 'CFG w=3 vs unguided', cfg, unG, 'class_acc')
paired('H2', 'CFG w=3 vs unguided', cfg, unG, 'mode_tv')
paired('H2', 'CFG w=3 vs unguided', cfg, unG, 'std_ratio')
paired('H3', 'CFG w=3 vs tau=0.5', cfg, lt, 'class_acc')
w8 = get(ov, 'sweep_w', w=8)
paired('H5', 'w=8 vs unguided', w8, unG, 'off_support')
d_ov = cfg.mode_tv.values - unG.mode_tv.values
d_sp = get(sp, 'main', w=3, tau=1).mode_tv.values - get(sp, 'main', w=0, tau=1).mode_tv.values
t = stats.ttest_ind(d_sp, d_ov, equal_var=False)
rows.append(('H4', 'sep minus overlap, w=3 minus w=0', 'mode_tv', d_sp.mean() - d_ov.mean(), t.pvalue, (d_sp.mean() - d_ov.mean()) / np.sqrt((d_sp.var(ddof=1) + d_ov.var(ddof=1)) / 2)))
H = pd.DataFrame(rows, columns=['H', 'comparison', 'metric', 'diff', 'p', 'd'])
print(H.to_string())
def fmt_p(p): return f'{p:.1e}' if p < 1e-3 else f'{p:.3f}'
with open(T + 'hyp.tex', 'w') as f:
    f.write('\\begin{tabular}{lllrrr}\\toprule H & Comparison & Metric & Mean diff & $p$ & $d_z$ \\\\\\midrule\n')
    for r in H.itertuples():
        f.write(f'{r.H} & {r.comparison} & \\texttt{{{r.metric.replace("_", chr(92)+"_")}}} & {r.diff:+.4f} & {fmt_p(r.p)} & {r.d:.1f} \\\\\n')
    f.write('\\bottomrule\\end{tabular}\n')
# ---- sweep table (overlap task)
M = ['class_acc', 'support_prec', 'mode_cov', 'mode_tv', 'std_ratio', 'off_support', 'swd']
short = ['acc', 'prec', 'cov', 'tv', 'std', 'off', 'swd']
def cell(g, m): return f'{g[m].mean():.3f}'
def table(name, entries, cols=M, heads=short, sd=False):
    with open(T + name + '.tex', 'w') as f:
        f.write('\\begin{tabular}{l' + 'r' * len(cols) + '}\\toprule System & ' + ' & '.join(heads) + ' \\\\\\midrule\n')
        for lab, g in entries:
            if lab == '--': f.write('\\midrule\n'); continue
            f.write(lab + ' & ' + ' & '.join(f'{g[m].mean():.3f}' + (f'\\,{{\\tiny$\\pm${g[m].std(ddof=1):.3f}}}' if sd else '') for m in cols) + ' \\\\\n')
        f.write('\\bottomrule\\end{tabular}\n')
E = [('Real samples', get(ov, 'ref')), ('--', None)]
for tau in [1.0, 0.8, 0.7, 0.5, 0.4, 0.3, 0.2]:
    g = get(ov, 'main', w=0, tau=tau) if tau in (1.0, 0.5) else get(ov, 'sweep_tau', tau=tau)
    E.append((f'Temperature $\\tau={tau}$' + (' (unguided)' if tau == 1.0 else ''), g))
E.append(('--', None))
for w in [0.5, 1, 2, 3, 5, 8]:
    g = get(ov, 'main', w=3, tau=1) if w == 3 else get(ov, 'sweep_w', w=w)
    E.append((f'CFG $w={w}$', g))
table('sweep_overlap', E)
E2 = [('Real samples', get(sp, 'ref')), ('Unguided', get(sp, 'main', w=0, tau=1)), ('Temperature $\\tau=0.5$', get(sp, 'main', w=0, tau=0.5)),
      ('CFG $w=3$', get(sp, 'main', w=3, tau=1)), ('CFG $w=8$', get(sp, 'sweep_w', w=8))]
table('sweep_sep', E2)
# ---- ablation table (overlap)
E3 = [('CFG $w=3$, $p=0.1$ (main)', cfg)]
for p in [0.02, 0.3]: E3.append((f'CFG $w=3$, label dropout $p={p}$', get(ov, 'abl_dropout', p_uncond=p)))
E3.append(('--', None))
E3.append(('Guidance on all steps (main)', cfg))
for lo, hi in [(0, 0.5), (0.2, 0.6), (0.5, 1)]:
    E3.append((f'Guidance only $t/T\\in[{lo},{hi}]$', get(ov, 'abl_interval', lo=lo, hi=hi)))
table('abl_cfg', E3)
# ---- per-mode mass table
pm = df[df.group == 'abl_permode']
with open(T + 'permode.tex', 'w') as f:
    f.write('\\begin{tabular}{lrrr}\\toprule Sampler & major (0.5) & middle (0.3) & minor (0.2) \\\\\\midrule\n')
    for lab, w, tau in [('Unguided', 0, 1), ('Temperature $\\tau=0.5$', 0, 0.5), ('CFG $w=3$', 3, 1), ('CFG $w=8$', 8, 1)]:
        g = pm[np.isclose(pm.w, w) & np.isclose(pm.tau, tau)]
        f.write(lab + ' & ' + ' & '.join(f'{g[c].mean():.2f}\\,{{\\tiny$\\pm${g[c].std(ddof=1):.2f}}}' for c in ['ratio_major', 'ratio_mid', 'ratio_minor']) + ' \\\\\n')
    f.write('\\bottomrule\\end{tabular}\n')
# ---- figures
ws = [0, 0.5, 1, 2, 3, 5, 8]; taus = [1.0, 0.8, 0.7, 0.5, 0.4, 0.3, 0.2]
def cw(w): return get(ov, 'main', w=w, tau=1) if w in (0, 3) else get(ov, 'sweep_w', w=w)
def ct(t): return get(ov, 'main', w=0, tau=t) if t in (1.0, 0.5) else get(ov, 'sweep_tau', tau=t)
def band(ax, xs, gs, m, **kw):
    mu = np.array([g[m].mean() for g in gs]); sd = np.array([g[m].std(ddof=1) for g in gs])
    ax.plot(xs, mu, marker='o', ms=3, **kw); ax.fill_between(xs, mu - sd, mu + sd, alpha=.2, color=kw.get('color'))
fig, axs = plt.subplots(1, 4, figsize=(7.2, 1.9))
for ax, m, tt in zip(axs, ['class_acc', 'mode_cov', 'std_ratio', 'off_support'], ['class acc.', 'mode coverage', 'std ratio', 'off-support']):
    band(ax, ws, [cw(w) for w in ws], m, color='C0')
    ax.set_title(tt, fontsize=8); ax.set_xlabel('guidance $w$', fontsize=7); ax.tick_params(labelsize=6)
    ax.axhline(get(ov, 'ref')[m].mean(), color='gray', ls=':', lw=.8)
fig.tight_layout(); fig.savefig(F + 'cfg_vs_w.pdf'); plt.close(fig)
fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.0))
for ax, m, tt in zip(axs, ['class_acc', 'mode_tv', 'off_support'], ['class accuracy', 'mode-weight TV', 'off-support mass']):
    for gs, lab, c in [([cw(w) for w in ws], 'CFG, $w$ from 0 to 8', 'C0'), ([ct(t) for t in taus], 'temperature, $\\tau$ from 1 to 0.2', 'C1')]:
        x = np.array([g.std_ratio.mean() for g in gs]); y = np.array([g[m].mean() for g in gs])
        ax.plot(x, y, marker='o', ms=3, color=c, label=lab)
    ax.set_xlabel('std ratio (variance retained)', fontsize=7); ax.set_title(tt, fontsize=8); ax.tick_params(labelsize=6)
axs[0].legend(fontsize=6); fig.tight_layout(); fig.savefig(F + 'frontier.pdf'); plt.close(fig)
