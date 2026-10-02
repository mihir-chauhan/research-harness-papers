import json, pandas as pd
def load():
    rows = []
    for l in open('results/runs.jsonl'):
        d = json.loads(l)
        if d.get('status') != 'ok' or d['kind'] == 'sanity': continue
        r = {k: d[k] for k in ['group', 'name', 'task', 'seed', 'kind']}
        r.update(d['config'] or {}); r.update(d['metrics']); rows.append(r)
    return pd.DataFrame(rows)
