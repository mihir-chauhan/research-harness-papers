"""Tables built from the run registry (results/runs.jsonl): weight sweeps, paired effort comparison across the sweep,
tuned-weight comparison and cost-term diagnostic. Std is the sample std (ddof=1) over seeds; p is a paired t-test over seeds."""
import json, numpy as np
from scipy import stats
R = [json.loads(l) for l in open('results/runs.jsonl')]
R = [r for r in R if r['status'] == 'ok']
W = (0.01, 0.1, 1, 10, 100)
TASKS = (('pendulum', 'pend.'), ('cartpole', 'cart-p.'))
SW = (('sweep_wE', 'wE', 'Energy'), ('sweep_qscale', 'qscale', 'Quad'))

def get(group, task, metric, name=None, cfg=None, seeds=None):
    """seed -> value for the matching rows (exactly one row per seed)."""
    d = {}
    for r in R:
        if r['group'] != group or r['task'] != task: continue
        if name is not None and r['name'] != name: continue
        if cfg is not None and any(r['config'].get(k) != v for k, v in cfg.items()): continue
        if seeds is not None and r['seed'] not in seeds: continue
        assert r['seed'] not in d, (group, task, name, cfg, r['seed'])
        d[r['seed']] = r['metrics'][metric]
    return d

def fp(p):
    return '--' if not np.isfinite(p) else ('$<$0.001' if p < 0.001 else '%.3f' % p)

def write(name, lines):
    open(f'results/tables/{name}.tex', 'w').write('\n'.join(lines) + '\n'); print('\n'.join(lines))

# ---- Table: sweeps (seeds 0-2)
out = ['\\begin{tabular}{lllrrrrrr}\\toprule', 'Cost & Task & Metric & 0.01 & 0.1 & 1 & 10 & 100 & range \\\\\\midrule']
for g, p, nm in SW:
    for t, tl in TASKS:
        for m, lab, f in (('success_rate', 'success', '%.2f'), ('control_effort', 'effort', '%.1f'), ('time_to_upright', 'time (s)', '%.2f')):
            vals = []
            for w in W:
                v = get(g, t, m, cfg={p: w}); assert sorted(v) == [0, 1, 2], (g, t, w, v)
                vals.append(np.mean(list(v.values())))
            out.append(f"{nm} & {tl} & {lab} & " + ' & '.join(f % x for x in vals) + f" & {f % (max(vals) - min(vals))} \\\\")
    out.append('\\midrule' if g == 'sweep_wE' else '\\bottomrule')
out.append('\\end{tabular}')
write('sweep_weights', out)

# ---- Table: effort of iLQR-Quad at each q minus iLQR-Energy at wE=1, paired over seeds 0-2
out = ['\\begin{tabular}{llrrrrr}\\toprule', 'Task & & $q{=}0.01$ & 0.1 & 1 & 10 & 100 \\\\\\midrule']
for t, tl in TASKS:
    e = get('sweep_wE', t, 'control_effort', cfg={'wE': 1})
    d, pv, sr = [], [], []
    for w in W:
        q = get('sweep_qscale', t, 'control_effort', cfg={'qscale': w})
        diff = np.array([q[s] - e[s] for s in (0, 1, 2)])
        d.append(diff.mean()); pv.append(stats.ttest_rel([q[s] for s in (0, 1, 2)], [e[s] for s in (0, 1, 2)]).pvalue)
        sr.append(np.mean(list(get('sweep_qscale', t, 'success_rate', cfg={'qscale': w}).values())))
    out.append(f"{tl} & $\\Delta$ effort & " + ' & '.join('%.1f' % x for x in d) + ' \\\\')
    out.append(f" & paired $p$ & " + ' & '.join(fp(x) for x in pv) + ' \\\\')
    out.append(f" & Quad success & " + ' & '.join('%.2f' % x for x in sr) + ' \\\\')
out += ['\\bottomrule', '\\end{tabular}']
write('sweep_paired', out)

# ---- Table: tuned weights (picked on seeds 0-2: highest mean success, ties by lowest mean effort), seeds 0-2 / 3-4 / all
def pick(g, p, t):
    best = None
    for w in W:
        key = (-np.mean(list(get(g, t, 'success_rate', cfg={p: w}).values())), np.mean(list(get(g, t, 'control_effort', cfg={p: w}).values())))
        if best is None or key < best[0]: best = (key, w)
    return best[1]
def tuned(g, p, t, w, m):
    d = get(g, t, m, cfg={p: w})                       # seeds 0-2 from the sweep
    h = get('tuned', t, m, cfg={p: w})                 # seeds 3-4 from group tuned
    if not h and g == 'sweep_wE' and w == 1:           # default weight: seeds 3-4 are the main-group runs
        h = get('main', t, m, name='iLQR-Energy (ours)', seeds=(3, 4))
    assert sorted(h) == [3, 4], (g, t, w, h)
    d.update(h); return d
out = ['\\begin{tabular}{llrrrr}\\toprule', 'Task & Cost (weight) & success & effort & time (s) & eff.\\ 3--4 \\\\\\midrule']
for t, tl in TASKS:
    res = {}
    for g, p, nm in SW:
        w = pick(g, p, t); res[nm] = {m: tuned(g, p, t, w, m) for m in ('success_rate', 'control_effort', 'time_to_upright')}
        c = lambda m, f: (f + '$\\pm$' + f) % (np.mean(list(res[nm][m].values())), np.std(list(res[nm][m].values()), ddof=1))
        ho = np.mean([res[nm]['control_effort'][s] for s in (3, 4)])
        out.append(f"{tl} & {nm} ({'$w_E$' if nm == 'Energy' else '$q$'}={w:g}) & {c('success_rate', '%.2f')} & {c('control_effort', '%.1f')} & {c('time_to_upright', '%.2f')} & {ho:.1f} \\\\")
    ps = []
    for m in ('success_rate', 'control_effort', 'time_to_upright'):
        a = [res['Energy'][m][s] for s in range(5)]; b = [res['Quad'][m][s] for s in range(5)]
        ps.append(fp(stats.ttest_rel(a, b).pvalue))
    out.append(f" & paired $p$ ($n{{=}}5$) & {ps[0]} & {ps[1]} & {ps[2]} & \\\\")
    out.append('\\midrule' if t == 'pendulum' else '\\bottomrule')
out.append('\\end{tabular}')
write('tuned', out)

# ---- Table: closed-loop size of the two state-cost terms under the combined cost (default weights, seeds 0-2)
out = ['\\begin{tabular}{lrrr}\\toprule', 'Task & energy term & quad.\\ term & ratio \\\\\\midrule']
for t, tl in (('pendulum', 'pendulum'), ('cartpole', 'cart-pole')):
    e = get('diag_terms', t, 'energy_term'); q = get('diag_terms', t, 'quad_term'); assert sorted(e) == [0, 1, 2]
    em, qm = np.mean(list(e.values())), np.mean(list(q.values()))
    out.append(f"{tl} & {em:.2f} & {qm:.2f} & {em / qm:.2f} \\\\")
out += ['\\bottomrule', '\\end{tabular}']
write('diag_terms', out)
