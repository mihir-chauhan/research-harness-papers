"""One-layer transformer on (a+b) mod p with uniform / curriculum / anti-curriculum sampling.
Writes a flat JSON of metrics to --out and prints config + metrics."""
import argparse, json, math, os, time, csv
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
torch.set_num_threads(2)

ap = argparse.ArgumentParser()
ap.add_argument("--system", required=True, choices=["uniform", "curriculum", "anticurriculum"])
ap.add_argument("--task", default="modadd")
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--p", type=int, default=23)
ap.add_argument("--frac", type=float, default=0.5)      # fraction of all p^2 pairs used for training
ap.add_argument("--wd", type=float, default=1.0)        # AdamW decoupled weight decay
ap.add_argument("--lr", type=float, default=3e-3)
ap.add_argument("--bs", type=int, default=128)
ap.add_argument("--max_steps", type=int, default=4000)
ap.add_argument("--warm", type=int, default=1000)       # curriculum length T_c (steps until full train set)
ap.add_argument("--q0", type=float, default=0.15)       # initial fraction of train set in the pool
ap.add_argument("--order", default="max", choices=["max", "random"])  # difficulty key; random = shuffled-order control
ap.add_argument("--d", type=int, default=64)
ap.add_argument("--eval_every", type=int, default=25)
ap.add_argument("--curve", default="")
ap.add_argument("--out", default=os.environ.get("RH_METRICS_FILE", "metrics.json"))
a = ap.parse_args()
print("config:", json.dumps(vars(a)))

torch.manual_seed(a.seed); rng = np.random.default_rng(a.seed)
p = a.p
A, B = np.meshgrid(np.arange(p), np.arange(p), indexing="ij")
pairs = np.stack([A.ravel(), B.ravel()], 1)
perm = rng.permutation(len(pairs))
ntr = int(round(a.frac * len(pairs)))
tr, te = pairs[perm[:ntr]], pairs[perm[ntr:]]       # held-out = all remaining pairs
def tens(x): return torch.tensor(np.concatenate([x, np.full((len(x), 1), p)], 1)), torch.tensor((x[:, 0] + x[:, 1]) % p)
Xtr, Ytr = tens(tr); Xte, Yte = tens(te)

# difficulty = operand size max(a,b); ties broken at random. Curriculum: small first; anti: large first.
key = tr.max(1) + rng.random(ntr) * 0.5 if a.order == "max" else rng.random(ntr)
order = np.argsort(key)
if a.system == "anticurriculum": order = order[::-1].copy()

class Net(nn.Module):
    def __init__(s, d, h=4, ff=4):
        super().__init__()
        s.emb = nn.Embedding(p + 1, d); s.pos = nn.Parameter(torch.randn(3, d) * 0.02)
        s.ln1 = nn.LayerNorm(d); s.att = nn.MultiheadAttention(d, h, batch_first=True)
        s.ln2 = nn.LayerNorm(d); s.mlp = nn.Sequential(nn.Linear(d, ff * d), nn.ReLU(), nn.Linear(ff * d, d))
        s.lnf = nn.LayerNorm(d); s.out = nn.Linear(d, p)
    def forward(s, x):
        h = s.emb(x) + s.pos
        y = s.ln1(h); h = h + s.att(y, y, y, need_weights=False)[0]
        h = h + s.mlp(s.ln2(h))
        return s.out(s.lnf(h[:, -1]))
net = Net(a.d)
opt = torch.optim.AdamW(net.parameters(), lr=a.lr, weight_decay=a.wd, betas=(0.9, 0.98))

def acc(X, Y):
    with torch.no_grad(): return (net(X).argmax(1) == Y).float().mean().item()

s95 = s_tr95 = None; curve = []; t0 = time.time()
for step in range(a.max_steps + 1):
    if step % a.eval_every == 0:
        ta, tra = acc(Xte, Yte), acc(Xtr, Ytr)
        curve.append((step, ta, tra))
        if s_tr95 is None and tra >= 0.95: s_tr95 = step
        if ta >= 0.95: s95 = step; break
    if a.system == "uniform": q = 1.0
    else: q = min(1.0, a.q0 + (1 - a.q0) * step / a.warm)
    pool = order[:max(a.bs // 4, int(math.ceil(q * ntr)))] if a.system != "uniform" else order
    idx = torch.tensor(rng.choice(pool, size=a.bs, replace=True))
    loss = F.cross_entropy(net(Xtr[idx]), Ytr[idx])
    opt.zero_grad(); loss.backward(); opt.step()

reached = s95 is not None
res = {"steps_to_95": float(s95 if reached else a.max_steps), "reached": float(reached),
       "final_test_acc": curve[-1][1], "final_train_acc": curve[-1][2],
       "steps_to_train95": float(s_tr95 if s_tr95 is not None else a.max_steps),
       "wall_s": time.time() - t0}
res["grok_gap"] = res["steps_to_95"] - res["steps_to_train95"]
if a.curve:
    with open(a.curve, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["step", "value", "seed", "name"])
        for s, ta, _ in curve: w.writerow([s, ta, a.seed, a.system])
json.dump(res, open(a.out, "w")); print("metrics:", json.dumps(res))
