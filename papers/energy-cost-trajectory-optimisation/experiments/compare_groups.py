"""Comparison groups for `rh compare`: existing runs are listed in further groups with `rh log --from-run`
(metrics and provenance are copied from the registry, nothing is typed or re-run), then `rh compare` is called so
that every difference and p-value the paper reports is a statistic rh recomputes from the registry.

  pair_q<q>   iLQR-Quad at scale q and iLQR-Energy at wE=1, seeds 0-2, both tasks (paired effort comparison)
  tuned_all   each cost at its picked weight (pick() below), seeds 0-4 (sweep seeds 0-2 + group tuned / main seeds 3-4)
  tuned       gets iLQR-Energy on the cart-pole, seeds 3-4 (wE=1 is the default weight: the main-group runs)

Usage: python experiments/compare_groups.py   (idempotent: a copy that is already in the group is skipped)"""
import json, subprocess
R = [json.loads(l) for l in open('results/runs.jsonl')]
R = [r for r in R if r['status'] == 'ok']
E, Q = 'iLQR-Energy (ours)', 'iLQR-Quad'
W = (0.01, 0.1, 1, 10, 100)
TASKS = ('pendulum', 'cartpole')
def pick(group, param, task):
    """The selection rule of the tuned comparison: highest mean success on seeds 0-2, ties broken by lowest mean effort."""
    def mean(w, m):
        v = [r['metrics'][m] for r in R if r['group'] == group and r['task'] == task and r['config'].get(param) == w and r['seed'] in (0, 1, 2)]
        assert len(v) == 3, (group, task, w); return sum(v) / 3
    return min(W, key=lambda w: (-mean(w, 'success_rate'), mean(w, 'control_effort')))

def find(group, name, task, seed, cfg=None):
    m = [r for r in R if r['group'] == group and r['name'] == name and r['task'] == task and r['seed'] == seed
         and 'copied_from' not in r['provenance'] and all(r['config'].get(k) == v for k, v in (cfg or {}).items())]
    assert len(m) == 1, (group, name, task, seed, cfg, len(m))
    return m[0]

def copy(src, group):
    if any(r['group'] == group and r['provenance'].get('copied_from') == src['run_id'] for r in R): return
    subprocess.run(['rh', 'log', '--kind', 'ablation', '--name', src['name'], '--group', group, '--task', src['task'],
                    '--seed', str(src['seed']), '--from-run', src['run_id']], check=True)

def compare(group, metric):
    subprocess.run(['rh', 'compare', '--group', group, '--metric', metric, '--ref', Q], check=True, stdout=subprocess.DEVNULL)

for q in W:
    for t in TASKS:
        for s in (0, 1, 2):
            copy(find('sweep_qscale', Q, t, s, {'qscale': q}), f'pair_q{q:g}')
            copy(find('sweep_wE', E, t, s, {'wE': 1}), f'pair_q{q:g}')
    compare(f'pair_q{q:g}', 'control_effort')
for t in TASKS:
    for n, g, p in ((E, 'sweep_wE', 'wE'), (Q, 'sweep_qscale', 'qscale')):
        w = pick(g, p, t)
        for s in (0, 1, 2):
            copy(find(g, n, t, s, {p: w}), 'tuned_all')
        for s in (3, 4):
            if (t, n) == ('cartpole', E):       # default weight: seeds 3-4 are the main-group runs
                src = find('main', n, t, s); copy(src, 'tuned')
            else:
                src = find('tuned', n, t, s, {p: w})
            copy(src, 'tuned_all')
for m in ('success_rate', 'control_effort', 'time_to_upright'):
    compare('tuned_all', m)
