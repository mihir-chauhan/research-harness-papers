"""Size generalisation for neural Bellman-Ford. One entrypoint: train on n<=8, test on 8/16/32/64."""
import argparse, json, time
import numpy as np, torch, torch.nn as nn

torch.set_num_threads(2)
NMAX = 64
SIZES = [8, 16, 32, 64]


def make_graphs(rng, B, n, family):
    """Connected undirected weighted graphs: random spanning tree + Erdos-Renyi edges, weights U(0.2,1).
    family: 'train' p=0.4; 'sparse' p=3/(n-1) (constant expected degree); 'dense' p=0.4 (degree grows with n)."""
    p = {"train": 0.4, "dense": 0.4, "sparse": min(1.0, 3.0 / (n - 1))}[family]
    A = np.zeros((B, n, n), bool)
    for b in range(B):
        perm = rng.permutation(n)
        for k in range(1, n):
            j = perm[rng.integers(0, k)]
            A[b, perm[k], j] = A[b, j, perm[k]] = True
    U = np.triu(rng.random((B, n, n)) < p, 1)
    A |= U | U.transpose(0, 2, 1)
    W = rng.uniform(0.2, 1.0, (B, n, n))
    W = np.triu(W, 1); W = W + W.transpose(0, 2, 1)
    W = W * A
    src = rng.integers(0, n, B)
    return A, W.astype(np.float32), src


def bellman_ford(A, W, src, T):
    """Return distances after t=1..T synchronous relaxation rounds: (T,B,n), inf = unreached."""
    B, n, _ = A.shape
    d = np.full((B, n), np.inf, np.float32); d[np.arange(B), src] = 0
    Wi = np.where(A, W, np.inf)
    out = []
    for _ in range(T):
        d = np.minimum(d, (d[:, None, :] + Wi).min(2))
        out.append(d.copy())
    return np.stack(out)


class MLP(nn.Module):
    def __init__(s, i, h, o):
        super().__init__(); s.f = nn.Sequential(nn.Linear(i, h), nn.ReLU(), nn.Linear(h, h), nn.ReLU(), nn.Linear(h, o))
    def forward(s, x): return s.f(x)


class FlatMLP(nn.Module):
    """MLP on the flattened (zero-padded to 64x64) weighted adjacency + one-hot source."""
    def __init__(s, H=128):
        super().__init__(); s.f = MLP(NMAX * NMAX + NMAX, H, NMAX)
    def forward(s, A, W, src, T):
        B, n, _ = W.shape
        Wp = torch.zeros(B, NMAX, NMAX); Wp[:, :n, :n] = W
        sp = torch.zeros(B, NMAX); sp[torch.arange(B), src] = 1
        return [s.f(torch.cat([Wp.flatten(1), sp], 1))[:, :n]], None


class MPNN(nn.Module):
    """h_i <- U([h_i, AGG_j M([h_i,h_j,w_ij])]); T = n-1 steps; every step decodes (dist, reached-logit)."""
    def __init__(s, agg, H=32):
        super().__init__(); s.agg = agg; s.H = H
        s.enc = MLP(1, H, H); s.msg = MLP(2 * H + 1, H, H); s.upd = MLP(2 * H, H, H); s.dec = MLP(H, H, 2)
    def forward(s, A, W, src, T):
        B, n, _ = W.shape
        x = torch.zeros(B, n, 1); x[torch.arange(B), src] = 1
        h = s.enc(x); mask = A.unsqueeze(-1)
        dists, reach = [], []
        for _ in range(T):
            hi = h.unsqueeze(2).expand(B, n, n, s.H); hj = h.unsqueeze(1).expand(B, n, n, s.H)
            m = s.msg(torch.cat([hi, hj, W.unsqueeze(-1)], -1))
            if s.agg == "sum": a = (m * mask).sum(2)
            elif s.agg == "mean": a = (m * mask).sum(2) / mask.sum(2).clamp(min=1)
            else:
                a = m.masked_fill(~mask, -1e9).max(2).values
                a = torch.where(mask.any(2), a, torch.zeros_like(a))
            h = s.upd(torch.cat([h, a], -1))
            o = s.dec(h); dists.append(o[..., 0]); reach.append(o[..., 1])
        return dists, reach


def batch_tensors(A, W, src):
    return torch.from_numpy(A), torch.from_numpy(W), torch.from_numpy(src)


def loss_fn(model, hints, A, W, src, n):
    T = n - 1
    Ab, Wb, sb = batch_tensors(A, W, src)
    dists, reach = model(Ab, Wb, sb, T)
    D = torch.from_numpy(bellman_ford(A, W, src, T))
    if isinstance(model, FlatMLP) or not hints:
        return ((dists[-1] - D[-1]) ** 2).mean()
    tot = 0
    for t in range(T):
        r = torch.isfinite(D[t]); tgt = torch.where(r, D[t], torch.zeros_like(D[t]))
        tot = tot + (((dists[t] - tgt) ** 2) * r).sum() / r.sum() \
            + nn.functional.binary_cross_entropy_with_logits(reach[t], r.float())
    return tot / T


@torch.no_grad()
def evaluate(model, rng, n, family, nb=4, B=50, step_mult=1.0):
    err, ref = [], []
    T = max(1, int(round(step_mult * (n - 1))))
    for _ in range(nb):
        A, W, src = make_graphs(rng, B, n, family)
        d, _ = model(*batch_tensors(A, W, src), T)
        true = bellman_ford(A, W, src, n - 1)[-1]
        err.append(np.abs(d[-1].numpy() - true)); ref.append(true)
    e, r = np.concatenate(err), np.concatenate(ref)
    return dict(mae=float(e.mean()), rel=float(e.sum() / r.sum()), acc=float((e < 0.05).mean()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True)  # mlp | sum | max | mean ; suffix -hint
    ap.add_argument("--task", default="bellman_ford")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--steps", type=int, default=1000)
    ap.add_argument("--lr", type=float, default=3e-3)
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--step_mult", type=float, default=1.0)
    ap.add_argument("--nmax_train", type=int, default=8)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    print("config", json.dumps(vars(a)))
    torch.manual_seed(a.seed); rng = np.random.default_rng(a.seed)
    agg, hints = a.system.replace("-hint", ""), a.system.endswith("-hint")
    model = FlatMLP() if agg == "mlp" else MPNN(agg)
    opt = torch.optim.Adam(model.parameters(), lr=a.lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, a.steps)
    t0 = time.time()
    for it in range(a.steps):
        n = int(rng.integers(4, a.nmax_train + 1))
        A, W, src = make_graphs(rng, a.bs, n, "train")
        loss = loss_fn(model, hints, A, W, src, n)
        opt.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sched.step()
        if it % 500 == 0: print(f"it {it} loss {loss.item():.4f}", flush=True)
    ev = np.random.default_rng(10_000 + a.seed)  # evaluation graphs independent of training stream
    res = {"train_loss_last": float(loss.item())}
    val = evaluate(model, np.random.default_rng(777 + a.seed), 8, "train", nb=2)  # validation: train distribution
    res["val_mae_n8"] = val["mae"]
    for fam in ["sparse", "dense"]:
        for n in SIZES:
            r = evaluate(model, ev, n, fam, step_mult=a.step_mult)
            for k, v in r.items(): res[f"{k}_{fam}_n{n}"] = v
    res["train_seconds"] = time.time() - t0
    print(json.dumps(res, indent=1))
    json.dump(res, open(a.out, "w"))


if __name__ == "__main__":
    main()
