"""Tables built from the run registry (results/runs.jsonl): weight sweeps, paired effort comparison across the sweep,
tuned-weight comparison and cost-term diagnostic. No statistic is computed or printed here: every cell is a
\\rhval{<key>} macro, i.e. a value rh recomputes from the registry at build time (`rh values --list` shows the keys).
Means and sample stds are rh aggregates; differences and paired p-values are `rh compare` statistics of the groups
built by experiments/compare_groups.py (run that first)."""
import csv, json, math
R = [json.loads(l) for l in open('results/runs.jsonl')]
R = [r for r in R if r['status'] == 'ok']
W = (0.01, 0.1, 1, 10, 100)
TASKS = (('pendulum', 'pend.'), ('cartpole', 'cart-p.'))
SW = (('sweep_wE', 'wE', 'Energy', 'ilqr-energy-ours'), ('sweep_qscale', 'qscale', 'Quad', 'ilqr-quad'))

def v(key, spec):
    return '\\rhval{%s:%s}' % (key, spec)

def sweep(g, p, sysk, w, t, m, spec, stat='mean'):
    """Aggregate over seeds 0-2 of one swept weight."""
    return v(f"{g.lower()}/{sysk}@{p.lower()}={w:g}/{t}/{m}/{stat}", spec)

def pval(group, t, m):
    """Paired p of `rh compare --group <group> --metric <m> --ref iLQR-Quad`. The CSV is read only to choose the
    number format (or '--' when the test is undefined); the printed value is the \\rhval macro."""
    row = [r for r in csv.DictReader(open(f'results/tables/compare_{group}_{m}.csv')) if r['task'] == t]
    assert len(row) == 1 and row[0]['ref'] == 'iLQR-Quad', (group, t, m)
    p = float(row[0]['paired_p'] or 'nan')
    return '--' if not math.isfinite(p) else v(f"cmp/{group.lower()}/ilqr-energy-ours/{t}/{m}/paired_p", '3' if p >= 0.001 else '4')

def write(name, lines):
    open(f'results/tables/{name}.tex', 'w').write('\n'.join(lines) + '\n'); print('\n'.join(lines))

# ---- Table: sweeps (seeds 0-2)
out = ['\\begin{tabular}{lllrrrrr}\\toprule', 'Cost & Task & Metric & 0.01 & 0.1 & 1 & 10 & 100 \\\\\\midrule']
for g, p, nm, sysk in SW:
    for t, tl in TASKS:
        for m, lab, spec in (('success_rate', 'success', '2'), ('control_effort', 'effort', '1'), ('time_to_upright', 'time (s)', '2')):
            out.append(f"{nm} & {tl} & {lab} & " + ' & '.join(sweep(g, p, sysk, w, t, m, spec) for w in W) + ' \\\\')
    out.append('\\midrule' if g == 'sweep_wE' else '\\bottomrule')
out.append('\\end{tabular}')
write('sweep_weights', out)

# ---- Table: effort of iLQR-Quad at each q minus iLQR-Energy at wE=1, paired over seeds 0-2 (groups pair_q<q>)
out = ['\\begin{tabular}{llrrrrr}\\toprule', 'Task & & $q{=}0.01$ & 0.1 & 1 & 10 & 100 \\\\\\midrule']
for t, tl in TASKS:
    out.append(f"{tl} & $\\Delta$ effort & " + ' & '.join(v(f"cmp/pair_q{w:g}/ilqr-energy-ours/{t}/control_effort/delta", '1') for w in W) + ' \\\\')
    out.append(f" & paired $p$ & " + ' & '.join(pval(f'pair_q{w:g}', t, 'control_effort') for w in W) + ' \\\\')
    out.append(f" & Quad success & " + ' & '.join(sweep('sweep_qscale', 'qscale', 'ilqr-quad', w, t, 'success_rate', '2') for w in W) + ' \\\\')
out += ['\\bottomrule', '\\end{tabular}']
write('sweep_paired', out)

# ---- Table: tuned weights (picked on seeds 0-2: highest mean success, ties by lowest mean effort); group tuned_all holds
#      seeds 0-4 at the picked weight, group tuned the held-out seeds 3-4
def pick(g, p, t):
    def mean(w, m):
        x = [r['metrics'][m] for r in R if r['group'] == g and r['task'] == t and r['config'].get(p) == w]
        assert len(x) == 3, (g, t, w); return sum(x) / 3
    return min(W, key=lambda w: (-mean(w, 'success_rate'), mean(w, 'control_effort')))
out = ['\\begin{tabular}{llrrrr}\\toprule', 'Task & Cost (weight) & success & effort & time (s) & eff.\\ 3--4 \\\\\\midrule']
for t, tl in TASKS:
    for g, p, nm, sysk in SW:
        w = pick(g, p, t)
        assert sorted(r['seed'] for r in R if r['group'] == 'tuned_all' and r['task'] == t and r['name'].lower().startswith(sysk[:9]) and r['config'].get(p, 1) == w) == [0, 1, 2, 3, 4]
        c = lambda m, spec: v(f"tuned_all/{sysk}/{t}/{m}/mean", spec) + '$\\pm$' + v(f"tuned_all/{sysk}/{t}/{m}/std", spec)
        out.append(f"{tl} & {nm} ({'$w_E$' if nm == 'Energy' else '$q$'}={w:g}) & {c('success_rate', '2')} & {c('control_effort', '1')} & {c('time_to_upright', '2')} & " + v(f"tuned/{sysk}/{t}/control_effort/mean", '1') + ' \\\\')
    ps = [pval('tuned_all', t, m) for m in ('success_rate', 'control_effort', 'time_to_upright')]
    out.append(f" & paired $p$ ($n{{=}}5$) & {ps[0]} & {ps[1]} & {ps[2]} & \\\\")
    out.append('\\midrule' if t == 'pendulum' else '\\bottomrule')
out.append('\\end{tabular}')
write('tuned', out)

# ---- Table: closed-loop size of the two state-cost terms under the combined cost (default weights, seeds 0-2)
out = ['\\begin{tabular}{lrrr}\\toprule', 'Task & energy term & quad.\\ term & ratio \\\\\\midrule']
for t, tl in (('pendulum', 'pendulum'), ('cartpole', 'cart-pole')):
    assert sorted(r['seed'] for r in R if r['group'] == 'diag_terms' and r['task'] == t) == [0, 1, 2]
    out.append(f"{tl} & " + ' & '.join(v(f"diag_terms/ilqr-quad+energy/{t}/{m}/mean", '2') for m in ('energy_term', 'quad_term', 'term_ratio')) + ' \\\\')
out += ['\\bottomrule', '\\end{tabular}']
write('diag_terms', out)
