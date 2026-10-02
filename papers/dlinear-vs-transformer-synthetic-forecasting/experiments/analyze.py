"""Win-rule analysis from results/runs.jsonl -> results/tables/wins.md, win_*.tex"""
import json, pandas as pd, numpy as np
rows = [json.loads(l) for l in open('results/runs.jsonl')]
rows = [r for r in rows if r.get('status', 'ok') == 'ok' and r['kind'] != 'sanity']
def df(group, m):
    return pd.DataFrame([dict(name=r['name'], task=r['task'], seed=r['seed'], cfg=json.dumps(r.get('config', {}), sort_keys=True), v=r['metrics'][m])
                         for r in rows if r['group'] == group and m in r['metrics']])
def rel(a, b):  # relative change of a vs b (negative = a better)
    return (a.mean() - b.mean()) / b.mean()
def win(x, ref):  # x beats ref: >=5% lower seed-mean and lower in every seed
    x, ref = x.sort_index(), ref.sort_index()
    return (rel(x, ref) <= -0.05) and bool((x.values < ref.values).all())
out = []
for H in (24, 96, 192):
    d = df('main', f'mse_{H}')
    for t, g in d.groupby('task'):
        p = g.pivot(index='seed', columns='name', values='v')
        for s in ('PatchTST', 'GRU', 'Seasonal naive'):
            out.append(dict(H=H, task=t, system=s, rel_vs_dlinear=100 * rel(p[s], p['DLinear']), seeds_better=int((p[s] < p['DLinear']).sum()), win=win(p[s], p['DLinear'])))
w = pd.DataFrame(out); w.to_csv('results/tables/wins.csv', index=False)
print(w[w.system != 'Seasonal naive'].round(2).to_string())
print(w[w.system == 'Seasonal naive'].round(1).to_string())

# ------------------------------------------------------------------ tables / figures built only from runs.jsonl
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def cfgval(c, k): return json.loads(c).get(k)
SYS = ['DLinear', 'PatchTST', 'GRU']
def relcell(x, ref):
    r = 100 * rel(x, ref); n = int((x.sort_index().values < ref.sort_index().values).sum())
    return f"{x.mean():.3f} & {r:+.1f}" + ("$^\\ast$" if win(x, ref) else "") + f" & {n}/3"
def sweep_frame(group, key, default_val, base_task='regime'):
    d = df(group, 'mse_96'); d['x'] = d.cfg.map(lambda c: cfgval(c, key))
    m = df('main', 'mse_96'); m = m[m.task == base_task].copy(); m['x'] = default_val
    return pd.concat([d[d.task == base_task], m])
lines = []
sw = {}
for group, key, dv, label in (('sweep_dwell', 'dwell', 500, 'dwell'), ('sweep_noise', 'noise', 0.3, 'noise')):
    f = sweep_frame(group, key, dv); sw[key] = f
    L = ["\\begin{tabular}{lrrrrrrr}", "\\toprule", f"{label} & DLinear & \\multicolumn{{3}}{{c}}{{PatchTST}} & \\multicolumn{{3}}{{c}}{{GRU}}\\\\",
         " & MSE & MSE & vs DL (\\%) & seeds & MSE & vs DL (\\%) & seeds\\\\", "\\midrule"]
    for xv in sorted(f.x.unique()):
        p = f[f.x == xv].pivot(index='seed', columns='name', values='v')
        L.append(f"{xv:g} & {p['DLinear'].mean():.3f} & {relcell(p['PatchTST'], p['DLinear'])} & {relcell(p['GRU'], p['DLinear'])}\\\\")
    L += ["\\bottomrule", "\\end{tabular}"]
    open(f'results/tables/sw_{key}.tex', 'w').write("\n".join(L))
    print(group); print("\n".join(L))
def fmtp(r): return f"{r:+.0f}" if abs(r) >= 100 else f"{r:+.1f}"
# design ablation: H=96, with-norm reference from main
a = df('abl_design', 'mse_96'); m = df('main', 'mse_96')
def medrel(x, ref):  # median over seeds of the per-seed relative change (robust to one outlier dataset)
    x, ref = x.sort_index(), ref.sort_index()
    return 100 * float(np.median((x.values - ref.values) / ref.values))
L = ["\\begin{tabular}{llrrrrr}", "\\toprule", "Task & System & Full & No norm & mean (\\%) & median (\\%) & No decomp\\\\", "\\midrule"]
for t in ('trend', 'regime', 'etth1'):
    for s in SYS:
        full = m[(m.task == t) & (m.name == s)].set_index('seed').v
        nn_ = a[(a.task == t) & (a.name == f'{s} no norm')].set_index('seed').v
        nd = ''
        if s == 'DLinear':
            nd = f"{a[(a.task == t) & (a.name == 'Linear (no decomp)')].v.mean():.3f}"
            r_nd = 100 * rel(a[(a.task == t) & (a.name == 'Linear (no decomp)')].set_index('seed').v, full)
            nd += f" ({r_nd:+.1f}\\%)"
        L.append(f"{t} & {s} & {full.mean():.3f} & {nn_.mean():.3f} & {fmtp(100 * rel(nn_, full))} & {fmtp(medrel(nn_, full))} & {nd or '--'}\\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open('results/tables/abl_design_full.tex', 'w').write("\n".join(L)); print("\n".join(L))
# win table (H=96 and 192, relative to DLinear), compact
L = ["\\begin{tabular}{lrrrrrr}", "\\toprule", " & \\multicolumn{3}{c}{PatchTST vs DLinear} & \\multicolumn{3}{c}{GRU vs DLinear}\\\\", "Task & 24 & 96 & 192 & 24 & 96 & 192\\\\", "\\midrule"]
for t in ['seas1', 'trend', 'multiseas', 'noisy', 'regime', 'etth1']:
    c = []
    for s in ('PatchTST', 'GRU'):
        for H in (24, 96, 192):
            r = w[(w.task == t) & (w.system == s) & (w.H == H)].iloc[0]
            c.append(f"{r.rel_vs_dlinear:+.2f}" + ("$^\\ast$" if r.win else "") + f"$^{{{r.seeds_better}}}$")
    L.append(f"{t} & " + " & ".join(c) + "\\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open('results/tables/rel.tex', 'w').write("\n".join(L)); print("\n".join(L))
# size / runtime table (runs that train all three horizons: main grid at 400 steps, sweep_steps regime/etth1 at 2000 steps)
pm = pd.DataFrame([dict(name=r['name'], rt=r['metrics']['runtime_s'], npar=r['metrics'].get('n_params_h96', np.nan)) for r in rows if r['group'] == 'main'])
p2 = pd.DataFrame([dict(name=r['name'], rt=r['metrics']['runtime_s']) for r in rows
                   if r['group'] == 'sweep_steps' and r['config'].get('steps') == 2000 and 'mse_192' in r['metrics']])
L = ["\\begin{tabular}{lrrr}", "\\toprule", " & Params & \\multicolumn{2}{c}{Median run (s)}\\\\", "System & ($H$=96) & 400 steps & 2000 steps\\\\", "\\midrule"]
for s_ in ['Seasonal naive', 'DLinear', 'PatchTST', 'GRU']:
    g = pm[pm.name == s_]; g2 = p2[p2.name == s_]
    L.append(f"{s_} & {'--' if np.isnan(g.npar.iloc[0]) else int(g.npar.iloc[0])} & {g.rt.median():.1f} & {'--' if not len(g2) else format(g2.rt.median(), '.1f')}\\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open('results/tables/size.tex', 'w').write("\n".join(L)); print("\n".join(L))

# ------------------------------------------------------------------ training-budget sweep (fix round)
def budget_frame(H):
    """rows: name, task, seed, steps, v for horizon H; 400 = main grid, 1000/2000 = sweep_steps."""
    m = df('main', f'mse_{H}'); m['steps'] = 400
    d = df('sweep_steps', f'mse_{H}'); d['steps'] = d.cfg.map(lambda c: cfgval(c, 'steps'))
    return pd.concat([m[m.name.isin(SYS)], d])
def relshort(x, ref):
    r = 100 * rel(x, ref); n = int((x.sort_index().values < ref.sort_index().values).sum())
    return f"{r:+.1f}$^{{{n}" + ("\\ast" if win(x, ref) else "") + "}$"
B = {H: budget_frame(H) for H in (24, 96, 192)}
bw = []  # machine-readable version of the budget table
def budget_rows(tasks, Hs, first_col=True):
    L = []
    for t in tasks:
        for H in Hs:
            f = B[H]; f = f[f.task == t]
            for st in sorted(f.steps.unique()):
                p = f[f.steps == st].pivot(index='seed', columns='name', values='v')
                if len(p) < 3 or p.isna().any().any(): continue
                L.append(f"{t} & {H} & {st} & {p['DLinear'].mean():.3f} & {p['PatchTST'].mean():.3f} & {relshort(p['PatchTST'], p['DLinear'])} & {p['GRU'].mean():.3f} & {relshort(p['GRU'], p['DLinear'])}\\\\")
                for s_ in ('PatchTST', 'GRU'):
                    bw.append(dict(task=t, H=H, steps=st, system=s_, dlinear=p['DLinear'].mean(), mse=p[s_].mean(), rel=100 * rel(p[s_], p['DLinear']),
                                   seeds_better=int((p[s_] < p['DLinear']).sum()), win=win(p[s_], p['DLinear'])))
        L.append("\\midrule")
    return L[:-1]
HEAD = ["\\begin{tabular}{lrrrrrrr}", "\\toprule", " & & & DLinear & \\multicolumn{2}{c}{PatchTST} & \\multicolumn{2}{c}{GRU}\\\\",
        "Task & $H$ & steps & MSE & MSE & vs DL & MSE & vs DL\\\\", "\\midrule"]
L = HEAD + budget_rows(['regime', 'etth1'], (24, 96, 192)) + ["\\midrule"] + budget_rows(['seas1', 'trend', 'multiseas', 'noisy'], (96,)) + ["\\bottomrule", "\\end{tabular}"]
open('results/tables/budget.tex', 'w').write("\n".join(L)); print("\n".join(L))
bw = pd.DataFrame(bw); bw.to_csv('results/tables/budget_wins.csv', index=False)
# dwell sweep at 2000 steps (dwell 500 = the 2000-step regime row of sweep_steps)
d2 = df('sweep_dwell_2000', 'mse_96')
if True:
    d2['x'] = d2.cfg.map(lambda c: cfgval(c, 'dwell'))
    r5 = B[96]; r5 = r5[(r5.task == 'regime') & (r5.steps == 2000)].copy(); r5['x'] = 500
    f2 = pd.concat([d2, r5])
    L = ["\\begin{tabular}{lrrrrrrr}", "\\toprule", "dwell & DLinear & \\multicolumn{3}{c}{PatchTST} & \\multicolumn{3}{c}{GRU}\\\\",
         " & MSE & MSE & vs DL (\\%) & seeds & MSE & vs DL (\\%) & seeds\\\\", "\\midrule"]
    for xv in sorted(f2.x.unique()):
        p = f2[f2.x == xv].pivot(index='seed', columns='name', values='v')
        if len(p) < 3 or p.isna().any().any(): continue
        L.append(f"{xv:g} & {p['DLinear'].mean():.3f} & {relcell(p['PatchTST'], p['DLinear'])} & {relcell(p['GRU'], p['DLinear'])}\\\\")
    L += ["\\bottomrule", "\\end{tabular}"]
    open('results/tables/sw_dwell2000.tex', 'w').write("\n".join(L)); print("\n".join(L))
# figure: H=96 relative MSE per task at 400 and 2000 steps (drawn at column width so fonts keep their size)
plt.rcParams.update({'font.size': 7, 'axes.labelsize': 7, 'xtick.labelsize': 6.5, 'ytick.labelsize': 6.5})
fig, ax = plt.subplots(figsize=(3.45, 1.5))
tasks = ['seas1', 'trend', 'multiseas', 'noisy', 'regime', 'etth1']
for s_, c, st, off, al in (('PatchTST', 'C0', 400, -0.3, 0.45), ('PatchTST', 'C0', 2000, -0.1, 1.0), ('GRU', 'C3', 400, 0.1, 0.45), ('GRU', 'C3', 2000, 0.3, 1.0)):
    v = [bw[(bw.task == t) & (bw.system == s_) & (bw.H == 96) & (bw.steps == st)].rel.iloc[0] for t in tasks]
    ax.bar(np.arange(6) + off, v, 0.2, color=c, alpha=al, label=f"{s_}, {st} steps")
ax.axhline(0, color='k', lw=.6); ax.axhline(-5, color='gray', ls='--', lw=.6)
ax.set_xticks(range(6)); ax.set_xticklabels(tasks); ax.set_ylabel('MSE vs DLinear (%), H=96')
ax.legend(fontsize=6, ncol=2, loc='lower left', bbox_to_anchor=(0, 1.0), frameon=False, columnspacing=1.0)
plt.tight_layout(pad=0.3); plt.savefig('results/figures/rel96.pdf'); plt.close()
# figure: dwell sweep (400 steps solid, 2000 steps dashed) and noise sweep (400 steps)
fig, ax = plt.subplots(1, 2, figsize=(3.45, 1.5))
for a_, (key, lab) in zip(ax, (('dwell', 'mean regime dwell (steps)'), ('noise', 'AR(1) noise sd'))):
    f = sw[key]
    for s_, c in zip(SYS, ('k', 'C0', 'C3')):
        g = f[f.name == s_].groupby('x').v; mu, sd = g.mean(), g.std()
        a_.errorbar(mu.index, mu.values, sd.values, label=f"{s_}, 400", color=c, marker='o', ms=2.5, capsize=1.5, lw=0.9)
        if key == 'dwell':
            g = f2[f2.name == s_].groupby('x').v.mean()
            a_.plot(g.index, g.values, color=c, ls='--', marker='x', ms=3, lw=0.9, label=f"{s_}, 2000")
    a_.set_xscale('log'); a_.set_xlabel(lab)
ax[0].set_ylabel('test MSE, H=96')
h, l = ax[0].get_legend_handles_labels()
fig.legend(h, l, fontsize=6, ncol=3, loc='upper center', frameon=False, columnspacing=1.0, handlelength=1.8)
plt.tight_layout(pad=0.3, rect=(0, 0, 1, 0.81)); plt.savefig('results/figures/sweeps.pdf'); plt.close()
print(bw.round(2).to_string())
# per-seed values behind the claims on trend / no-norm and the noise-sweep GRU trend
print(a[a.task == 'trend'].pivot(index='name', columns='seed', values='v').round(4))
f = sw['noise']; print(f.pivot_table(index=['x', 'seed'], columns='name', values='v').round(4))
