import json, collections
rows = []
for l in open('results/runs.jsonl'):
    r = json.loads(l)
    if r.get('kind') == 'control' and r.get('op') == 'supersede':   # superseded rows are dropped
        rows = [x for x in rows if not (x['group'] == r['group'] and x['name'] == r['name'])]
    elif r.get('group') == 'tune_lr3' and 'metrics' in r:
        rows.append(r)
m = {"Mean-field": "mf1", "Jastrow": "jastrow1", "RBM alpha=1": "rbm1", "RBM alpha=2": "rbm2", "RBM alpha=4": "rbm4"}
tab = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rows:
    nm, o = r['name'].rsplit(' ', 1)
    e = r['metrics']['rel_energy_error']; e = float('inf') if e != e else e
    tab[(nm, o)][r['config']['lr']].append(e)
lr = {}
for (nm, o), d in sorted(tab.items()):
    mean = {k: sum(v) / len(v) for k, v in d.items()}
    k = min(mean, key=mean.get); lr[f"{m[nm]}_{o.lower()}"] = k
    print(nm, o, len(next(iter(d.values()))), {a: '%.1e' % b for a, b in sorted(mean.items())}, '->', k)
json.dump(lr, open('experiments/lr.json', 'w'), indent=1)
