import json, pandas as pd
def load():
    rows = []
    for l in open('results/runs.jsonl'):
        r = json.loads(l)
        if r['status'] != 'ok': continue
        d = dict(group=r['group'], name=r['name'], task=r['task'], seed=r['seed'], commit=r['provenance']['git_commit'], **r['config'], **r['metrics'])
        rows.append(d)
    df = pd.DataFrame(rows)
    for c, v in dict(w=0.0, tau=1.0, lo=0.0, hi=1.0, p_uncond=0.1).items():
        df[c] = df[c].fillna(v) if c in df else v
    return df
