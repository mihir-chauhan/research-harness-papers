"""Win-rule analysis from results/runs.jsonl -> results/tables/wins.csv, budget_wins.csv and the custom .tex tables.

The .tex tables contain no typed or computed result: every numeric cell is a \\rhval{<key>} macro, which
`rh paper build` expands from the registry (`rh values --list` shows the keys; the ratio cells need the
`rh compare --group main --metric mse_<H> --ref DLinear` files). This script only lays the tables out and
adds the two verdicts of the registered win rule that are not numbers `rh` records: the count of seeds in
which a model is better than DLinear and the win mark. Percent changes are printed to the console and the
CSVs for the analysis notes only; they are not used in the paper."""
import json, re, pandas as pd, numpy as np
rows = [json.loads(l) for l in open('results/runs.jsonl')]
rows = [r for r in rows if r.get('status', 'ok') == 'ok' and r['kind'] != 'sanity']
def df(group, m):
    return pd.DataFrame([dict(name=r['name'], task=r['task'], seed=r['seed'], cfg=json.dumps(r.get('config', {}), sort_keys=True), v=r['metrics'][m])
                         for r in rows if r['group'] == group and m in r['metrics']])
def slug(s):  # key component, as rh/numbers.py
    return re.sub(r"[^a-z0-9_.+-]+", "-", str(s).lower()).strip("-") or "x"
def V(group, name, task, metric, stat='mean', spec='3', **cfg):
    """\\rhval macro of an aggregate over seeds. cfg selects one value of a swept setting, e.g. steps=2000;
    the key carries it (system@param=value) when that setting varies inside (group, system, task), as in rh."""
    cell = [r for r in rows if r['group'] == group and r['name'] == name and r['task'] == task]
    sub = [r for r in cell if all(r.get('config', {}).get(k) == v for k, v in cfg.items())]
    assert sub and all(metric in r['metrics'] for r in sub), (group, name, task, metric, cfg)
    vary = [k for k, v in cfg.items() if len({json.dumps(r.get('config', {}).get(k)) for r in cell}) > 1]
    assert len(vary) <= 1 and (vary or len(sub) == len(cell)), (group, name, task, cfg)
    sysk = slug(name) + (f"@{slug(vary[0])}={slug(cfg[vary[0]])}" if vary else "")
    return f"\\rhval{{{slug(group)}/{sysk}/{slug(task)}/{slug(metric)}/{stat}" + (f":{spec}" if spec else "") + "}"
def R(name, task, metric, spec='4'):
    """\\rhval macro of the MSE ratio to DLinear in the main grid (`rh compare`: inv_ratio = system mean / DLinear mean)."""
    return f"\\rhval{{cmp/main/{slug(name)}/{slug(task)}/{slug(metric)}/inv_ratio:{spec}}}"
def mark(x, ref):  # seeds in which x is better than ref, and the win mark
    n = int((x.sort_index().values < ref.sort_index().values).sum())
    return f"$^{{{n}" + ("\\ast" if win(x, ref) else "") + "}$"
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
SWEEP_HEAD = " & DLinear & PatchTST & GRU\\\\"
def sweep_frame(group, key, default_val, base_task='regime'):
    d = df(group, 'mse_96'); d['x'] = d.cfg.map(lambda c: cfgval(c, key))
    m = df('main', 'mse_96'); m = m[m.task == base_task].copy(); m['x'] = default_val
    return pd.concat([d[d.task == base_task], m])
lines = []
sw = {}
for group, key, dv, label in (('sweep_dwell', 'dwell', 500, 'dwell'), ('sweep_noise', 'noise', 0.3, 'noise')):
    f = sweep_frame(group, key, dv); sw[key] = f
    L = ["\\begin{tabular}{lrrr}", "\\toprule", label + SWEEP_HEAD, "\\midrule"]
    for xv in sorted(f.x.unique()):
        p = f[f.x == xv].pivot(index='seed', columns='name', values='v')
        cell = lambda s_: V('main', s_, 'regime', 'mse_96') if xv == dv else V(group, s_, 'regime', 'mse_96', **{key: xv})
        L.append(f"{xv:g} & {cell('DLinear')} & " + " & ".join(cell(s_) + mark(p[s_], p['DLinear']) for s_ in ('PatchTST', 'GRU')) + "\\\\")
    L += ["\\bottomrule", "\\end{tabular}"]
    open(f'results/tables/sw_{key}.tex', 'w').write("\n".join(L))
    print(group); print("\n".join(L))
# design ablation: H=96, with-norm reference from main
a = df('abl_design', 'mse_96'); m = df('main', 'mse_96')
def medrel(x, ref):  # median over seeds of the per-seed relative change (robust to one outlier dataset)
    x, ref = x.sort_index(), ref.sort_index()
    return 100 * float(np.median((x.values - ref.values) / ref.values))
L = ["\\begin{tabular}{llrrrrr}", "\\toprule", " & & \\multicolumn{2}{c}{seed mean} & \\multicolumn{2}{c}{seed median} & No decomp\\\\",
     "Task & System & Full & No norm & Full & No norm & (seed mean)\\\\", "\\midrule"]
for t in ('trend', 'regime', 'etth1'):
    for s in SYS:
        full = m[(m.task == t) & (m.name == s)].set_index('seed').v
        nn_ = a[(a.task == t) & (a.name == f'{s} no norm')].set_index('seed').v
        nd = V('abl_design', 'Linear (no decomp)', t, 'mse_96') if s == 'DLinear' else '--'
        if s == 'DLinear':
            r_nd = 100 * rel(a[(a.task == t) & (a.name == 'Linear (no decomp)')].set_index('seed').v, full)
            print(f"no decomp {t}: {r_nd:+.1f}%")
        print(f"no norm {t} {s}: mean {100 * rel(nn_, full):+.1f}%, median per-seed {medrel(nn_, full):+.1f}%")
        L.append(f"{t} & {s} & {V('main', s, t, 'mse_96')} & {V('abl_design', s + ' no norm', t, 'mse_96')} & "
                 f"{V('main', s, t, 'mse_96', 'median', '4')} & {V('abl_design', s + ' no norm', t, 'mse_96', 'median', '4')} & {nd}\\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open('results/tables/abl_design_full.tex', 'w').write("\n".join(L)); print("\n".join(L))
# win table (H=96 and 192, relative to DLinear), compact
L = ["\\begin{tabular}{lrrrrrr}", "\\toprule", " & \\multicolumn{3}{c}{PatchTST vs DLinear} & \\multicolumn{3}{c}{GRU vs DLinear}\\\\", "Task & 24 & 96 & 192 & 24 & 96 & 192\\\\", "\\midrule"]
for t in ['seas1', 'trend', 'multiseas', 'noisy', 'regime', 'etth1']:
    c = []
    for s in ('PatchTST', 'GRU'):
        for H in (24, 96, 192):
            r = w[(w.task == t) & (w.system == s) & (w.H == H)].iloc[0]
            c.append(R(s, t, f'mse_{H}') + f"$^{{{r.seeds_better}" + ("\\ast" if r.win else "") + "}$")
    L.append(f"{t} & " + " & ".join(c) + "\\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open('results/tables/rel.tex', 'w').write("\n".join(L)); print("\n".join(L))
# size / runtime table: parameter count and the median over the three seeds of the run time on the regime task
# (runs that train all three horizons: main grid at 400 steps, sweep_steps at 2000 steps)
L = ["\\begin{tabular}{lrrr}", "\\toprule", " & Params & \\multicolumn{2}{c}{Median run (s)}\\\\", "System & ($H$=96) & 400 steps & 2000 steps\\\\", "\\midrule"]
for s_ in ['Seasonal naive', 'DLinear', 'PatchTST', 'GRU']:
    learned = s_ != 'Seasonal naive'
    L.append(f"{s_} & {V('main', s_, 'regime', 'n_params_h96', 'mean', '') if learned else '--'} & {V('main', s_, 'regime', 'runtime_s', 'median', '1')} & "
             f"{V('sweep_steps', s_, 'regime', 'runtime_s', 'median', '1', steps=2000) if learned else '--'}\\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open('results/tables/size.tex', 'w').write("\n".join(L)); print("\n".join(L))

# ------------------------------------------------------------------ training-budget sweep (fix round)
def budget_frame(H):
    """rows: name, task, seed, steps, v for horizon H; 400 = main grid, 1000/2000 = sweep_steps."""
    m = df('main', f'mse_{H}'); m['steps'] = 400
    d = df('sweep_steps', f'mse_{H}'); d['steps'] = d.cfg.map(lambda c: cfgval(c, 'steps'))
    return pd.concat([m[m.name.isin(SYS)], d])
def bcell(s_, t, H, st):  # 400 steps: the main-grid row; 1000/2000 steps: sweep_steps
    return V('main', s_, t, f'mse_{H}') if st == 400 else V('sweep_steps', s_, t, f'mse_{H}', steps=st)
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
                L.append(f"{t} & {H} & {st} & {bcell('DLinear', t, H, st)} & " + " & ".join(bcell(s_, t, H, st) + mark(p[s_], p['DLinear']) for s_ in ('PatchTST', 'GRU')) + "\\\\")
                for s_ in ('PatchTST', 'GRU'):
                    bw.append(dict(task=t, H=H, steps=st, system=s_, dlinear=p['DLinear'].mean(), mse=p[s_].mean(), rel=100 * rel(p[s_], p['DLinear']),
                                   seeds_better=int((p[s_] < p['DLinear']).sum()), win=win(p[s_], p['DLinear'])))
        L.append("\\midrule")
    return L[:-1]
HEAD = ["\\begin{tabular}{lrrrrr}", "\\toprule", "Task & $H$ & steps & DLinear & PatchTST & GRU\\\\", "\\midrule"]
L = HEAD + budget_rows(['regime', 'etth1'], (24, 96, 192)) + ["\\midrule"] + budget_rows(['seas1', 'trend', 'multiseas', 'noisy'], (96,)) + ["\\bottomrule", "\\end{tabular}"]
open('results/tables/budget.tex', 'w').write("\n".join(L)); print("\n".join(L))
bw = pd.DataFrame(bw); bw.to_csv('results/tables/budget_wins.csv', index=False)
# dwell sweep at 2000 steps (dwell 500 = the 2000-step regime row of sweep_steps)
d2 = df('sweep_dwell_2000', 'mse_96')
if True:
    d2['x'] = d2.cfg.map(lambda c: cfgval(c, 'dwell'))
    r5 = B[96]; r5 = r5[(r5.task == 'regime') & (r5.steps == 2000)].copy(); r5['x'] = 500
    f2 = pd.concat([d2, r5])
    L = ["\\begin{tabular}{lrrr}", "\\toprule", "dwell" + SWEEP_HEAD, "\\midrule"]
    for xv in sorted(f2.x.unique()):
        p = f2[f2.x == xv].pivot(index='seed', columns='name', values='v')
        if len(p) < 3 or p.isna().any().any(): continue
        cell = lambda s_: V('sweep_steps', s_, 'regime', 'mse_96', steps=2000) if xv == 500 else V('sweep_dwell_2000', s_, 'regime', 'mse_96', dwell=xv)
        L.append(f"{xv:g} & {cell('DLinear')} & " + " & ".join(cell(s_) + mark(p[s_], p['DLinear']) for s_ in ('PatchTST', 'GRU')) + "\\\\")
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
