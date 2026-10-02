"""Message passing on contextual SBM graphs: MLP, GCN, H2GCN-style, label propagation (plain torch)."""
import argparse, json, os, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.set_num_threads(2)


# validation-selected (lr, dropout, weight decay), see method/tune.py and experiments/tuning_log.json
TUNED = {'mlp': (0.01, 0.5, 5e-3), 'gcn': (0.05, 0.5, 5e-4), 'h2gcn': (0.05, 0.5, 5e-3)}


# ---------------------------------------------------------------- data
def make_graph(n, k, d, h, mu, dim, seed):
    """Contextual SBM. Balanced classes; each node draws ~d/2 'half-edges' so mean degree is d.
    An edge is intra-class with prob h, else the other endpoint's class is uniform over the k-1 other classes.
    Features: x = mu * m_y + N(0, I), m_y random unit vectors in R^dim."""
    rng = np.random.RandomState(seed)
    y = np.arange(n) % k
    rng.shuffle(y)
    members = [np.where(y == c)[0] for c in range(k)]
    m = int(round(n * d / 2))
    src = rng.randint(0, n, size=m)
    intra = rng.rand(m) < h
    off = rng.randint(1, k, size=m)
    tgt_cls = np.where(intra, y[src], (y[src] + off) % k)
    dst = np.array([members[c][rng.randint(len(members[c]))] for c in tgt_cls])
    keep = src != dst
    src, dst = src[keep], dst[keep]
    A = np.zeros((n, n), dtype=np.float32)
    A[src, dst] = 1.0
    A[dst, src] = 1.0
    means = rng.randn(k, dim)
    means /= np.linalg.norm(means, axis=1, keepdims=True)
    X = mu * means[y] + rng.randn(n, dim)
    perm = rng.permutation(n)
    ntr, nva = int(0.2 * n), int(0.2 * n)
    masks = [torch.zeros(n, dtype=torch.bool) for _ in range(3)]
    masks[0][perm[:ntr]] = True
    masks[1][perm[ntr:ntr + nva]] = True
    masks[2][perm[ntr + nva:]] = True
    ei = A.nonzero()
    real_h = float((y[ei[0]] == y[ei[1]]).mean()) if len(ei[0]) else float('nan')
    return torch.tensor(A), torch.tensor(X, dtype=torch.float32), torch.tensor(y), masks, real_h


def sym_norm(A):
    deg = A.sum(1)
    dinv = torch.where(deg > 0, deg.pow(-0.5), torch.zeros_like(deg))
    return dinv[:, None] * A * dinv[None, :]


# ---------------------------------------------------------------- models
class MLP(nn.Module):
    def __init__(s, din, hid, k, p):
        super().__init__(); s.l1 = nn.Linear(din, hid); s.l2 = nn.Linear(hid, k); s.p = p
    def forward(s, X, g):
        h = F.relu(s.l1(F.dropout(X, s.p, s.training)))
        return s.l2(F.dropout(h, s.p, s.training))


class GCN(nn.Module):
    """Kipf & Welling: H' = relu(D^-1/2 (A+I) D^-1/2 H W), two layers."""
    def __init__(s, din, hid, k, p):
        super().__init__(); s.l1 = nn.Linear(din, hid); s.l2 = nn.Linear(hid, k); s.p = p
    def forward(s, X, g):
        Ah = g['A_self']
        h = F.relu(Ah @ s.l1(F.dropout(X, s.p, s.training)))
        return Ah @ s.l2(F.dropout(h, s.p, s.training))


class H2GCN(nn.Module):
    """Ego/neighbour separation: H' = relu(H W_self + sum_j A_j H W_nb_j) with A_1 = sym-normalised A (no self loops)
    and, if twohop, A_2 = sym-normalised strict 2-hop adjacency. sep=False ties W_self = W_nb (ablation)."""
    def __init__(s, din, hid, k, p, sep=True, twohop=False):
        super().__init__()
        s.sep, s.twohop, s.p = sep, twohop, p
        nh = 2 if twohop else 1
        dims = [(din, hid), (hid, k)]
        s.self_w = nn.ModuleList([nn.Linear(a, b) for a, b in dims])
        s.nb_w = nn.ModuleList([nn.ModuleList([nn.Linear(a, b, bias=False) for _ in range(nh)]) for a, b in dims]) if sep else None
    def layer(s, i, h, g):
        h = F.dropout(h, s.p, s.training)
        out = s.self_w[i](h)
        mats = [g['A1']] + ([g['A2']] if s.twohop else [])
        for j, M in enumerate(mats):
            if s.sep:
                out = out + M @ s.nb_w[i][j](h)
            else:
                out = out + M @ F.linear(h, s.self_w[i].weight)  # tied weights
        return out
    def forward(s, X, g):
        return s.layer(1, F.relu(s.layer(0, X, g)), g)


def label_propagation(A, y, train, val, k, alphas=(0.5, 0.9, 0.99), iters=50):
    """Zhou et al. LP: F <- alpha S F + (1-alpha) Y0, S = D^-1/2 A D^-1/2; alpha picked on validation accuracy."""
    S = sym_norm(A)
    Y0 = torch.zeros(len(y), k)
    Y0[train, y[train]] = 1.0
    best = None
    for a in alphas:
        Fm = Y0.clone()
        for _ in range(iters):
            Fm = a * (S @ Fm) + (1 - a) * Y0
        pred = Fm.argmax(1)
        va = (pred[val] == y[val]).float().mean().item()
        if best is None or va > best[0]:
            best = (va, pred, a)
    return best


# ---------------------------------------------------------------- train
def train_model(model, X, g, y, masks, lr, wd, epochs, patience):
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=wd)
    best_va, best_te, bad = -1, 0, 0
    for ep in range(epochs):
        model.train(); opt.zero_grad()
        out = model(X, g)
        F.cross_entropy(out[masks[0]], y[masks[0]]).backward(); opt.step()
        model.eval()
        with torch.no_grad():
            pred = model(X, g).argmax(1)
        va = (pred[masks[1]] == y[masks[1]]).float().mean().item()
        te = (pred[masks[2]] == y[masks[2]]).float().mean().item()
        if va > best_va:
            best_va, best_te, bad = va, te, 0
        else:
            bad += 1
            if bad >= patience: break
    return best_va, best_te


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--system', required=True, choices=['mlp', 'gcn', 'h2gcn', 'lp'])
    ap.add_argument('--h', type=float, required=True)
    ap.add_argument('--mu', type=float, required=True)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--n', type=int, default=900)
    ap.add_argument('--k', type=int, default=3)
    ap.add_argument('--deg', type=float, default=10.0)
    ap.add_argument('--dim', type=int, default=16)
    ap.add_argument('--hid', type=int, default=32)
    ap.add_argument('--dropout', type=float, default=None)  # default: per-system value from method/tune.py
    ap.add_argument('--lr', type=float, default=None)
    ap.add_argument('--wd', type=float, default=None)
    ap.add_argument('--epochs', type=int, default=300)
    ap.add_argument('--patience', type=int, default=100)
    ap.add_argument('--sep', type=int, default=1)      # H2GCN: separate self / neighbour weights
    ap.add_argument('--twohop', type=int, default=0)   # H2GCN: add strict 2-hop neighbourhood
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    for key, v in zip(('lr', 'dropout', 'wd'), TUNED.get(a.system, (None,) * 3)):
        if getattr(a, key) is None: setattr(a, key, v)
    print('config', json.dumps(vars(a)), flush=True)
    t0 = time.time()
    torch.manual_seed(a.seed); np.random.seed(a.seed)
    A, X, y, masks, real_h = make_graph(a.n, a.k, a.deg, a.h, a.mu, a.dim, a.seed)
    extra = {}
    if a.system == 'lp':
        va, pred, alpha = label_propagation(A, y, masks[0], masks[1], a.k)
        te = (pred[masks[2]] == y[masks[2]]).float().mean().item()
        extra['lp_alpha'] = alpha
    else:
        g = {'A_self': sym_norm(A + torch.eye(a.n))}
        if a.system == 'h2gcn':
            g['A1'] = sym_norm(A)
            if a.twohop:
                A2 = ((A @ A) > 0).float()
                A2 = A2 * (1 - A) * (1 - torch.eye(a.n))
                g['A2'] = sym_norm(A2)
        if a.system == 'mlp': model = MLP(a.dim, a.hid, a.k, a.dropout)
        elif a.system == 'gcn': model = GCN(a.dim, a.hid, a.k, a.dropout)
        else: model = H2GCN(a.dim, a.hid, a.k, a.dropout, bool(a.sep), bool(a.twohop))
        va, te = train_model(model, X, g, y, masks, a.lr, a.wd, a.epochs, a.patience)
    res = {'accuracy': te, 'val_accuracy': va, 'realized_h': real_h, 'seconds': time.time() - t0, **extra}
    print('metrics', json.dumps(res), flush=True)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(res, open(a.out, 'w'))


if __name__ == '__main__':
    main()
