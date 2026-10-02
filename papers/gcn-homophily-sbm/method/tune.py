"""Small validation-only tuning of lr / dropout / weight decay on tuning graphs (seeds 100-102, disjoint from eval seeds).
Selection uses validation accuracy only; test accuracy is never read here."""
import itertools, json, sys
sys.path.insert(0, 'method')
import numpy as np, torch
from run import make_graph, sym_norm, MLP, GCN, H2GCN, train_model

cells = [(0.2, 1.0), (0.5, 1.0), (0.8, 1.0)]
grid = list(itertools.product([0.01, 0.05], [0.0, 0.5], [5e-4, 5e-3]))
res = {}
for sysname in ['mlp', 'gcn', 'h2gcn']:
    for lr, dp, wd in grid:
        vs = []
        for (h, mu) in cells:
            for seed in (100, 101, 102):
                torch.manual_seed(seed)
                A, X, y, masks, _ = make_graph(900, 3, 10.0, h, mu, 16, seed)
                g = {'A_self': sym_norm(A + torch.eye(900)), 'A1': sym_norm(A)}
                m = {'mlp': MLP, 'gcn': GCN, 'h2gcn': H2GCN}[sysname](16, 32, 3, dp)
                va, _ = train_model(m, X, g, y, masks, lr, wd, 300, 100)
                vs.append(va)
        res[f'{sysname} lr={lr} dropout={dp} wd={wd}'] = float(np.mean(vs))
        print(sysname, lr, dp, wd, round(float(np.mean(vs)), 4), flush=True)
json.dump(res, open('experiments/tuning_log.json', 'w'), indent=1)
for s in ['mlp', 'gcn', 'h2gcn']:
    k = max((k for k in res if k.startswith(s + ' ')), key=res.get)
    print('BEST', k, res[k])
