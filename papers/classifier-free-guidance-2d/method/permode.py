"""Per-mode mass ratio on the cached networks of method/run.py: share of in-support samples that fall in the
major (true weight 0.5), middle (0.3) and minor (0.2) mode of each class, divided by the true weight."""
import argparse, json, sys, numpy as np, torch
sys.path.insert(0, 'method')
import run as R
ap = argparse.ArgumentParser()
ap.add_argument('--task', default='mix_overlap'); ap.add_argument('--seed', type=int, default=0)
ap.add_argument('--w', type=float, default=0.0); ap.add_argument('--tau', type=float, default=1.0)
ap.add_argument('--n', type=int, default=1500); ap.add_argument('--out', required=True)
a = ap.parse_args(); print('config:', json.dumps(vars(a)))
net = R.Net(); net.load_state_dict(torch.load(f'results/raw/ckpt/{a.task}_s{a.seed}_p0.1_n5000.pt')); net.eval()
gen = torch.Generator().manual_seed(7000 + a.seed)   # same generator seed as run.py
mu, cls, w = R.layout(); sig = R.SIGMA[a.task]
cnt = np.zeros(3); tot = 0
for c in range(R.K):
    x = R.sample(net, np.full(a.n, c), a.w, a.tau, gen)
    mods = np.where(cls == c)[0]
    d = np.linalg.norm(x[:, None] - mu[None, mods], axis=2) / sig
    ok = d.min(1) <= R.RADIUS; near = d.argmin(1)
    for m in range(3): cnt[m] += np.sum(ok & (near == m))
    tot += ok.sum()
m = {f'ratio_{k}': float(cnt[i] / tot / R.WEIGHTS[i]) for i, k in enumerate(['major', 'mid', 'minor'])}
print('metrics:', json.dumps(m)); json.dump(m, open(a.out, 'w'))
