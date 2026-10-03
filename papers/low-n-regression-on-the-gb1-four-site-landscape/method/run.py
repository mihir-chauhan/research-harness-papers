"""Low-N regression on the GB1 four-site landscape (Wu et al. 2016, FLIP copy).

Usage: run.py --system {ridge,pairwise,gp,cnn} --task {rand_N,dbl_N} --seed S --out file.json
Task names: rand_48 ... (train = N uniformly random variants), dbl_48 ... (train = N random variants of
Hamming distance <= 2 from wild type). Test = every variant not in the training set (rand) or every variant
with Hamming distance >= 3 (dbl).
"""
import argparse, json, os, time
import numpy as np, pandas as pd
from scipy.stats import spearmanr

os.environ.setdefault("OMP_NUM_THREADS", "2")
AA = "ACDEFGHIKLMNPQRSTVWY"
WT = "VDGV"
CSV = os.path.join(os.path.dirname(__file__), "..", "data", "four_mutations_full_data.csv")
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]


def load():
    d = pd.read_csv(CSV, usecols=["Variants", "Fitness"])
    X = np.array([[AA.index(c) for c in v] for v in d.Variants], dtype=np.int64)
    hd = (X != np.array([AA.index(c) for c in WT])).sum(1)
    return X, d.Fitness.values.astype(np.float64), hd


def onehot(X):
    Z = np.zeros((len(X), 80))
    for s in range(4):
        Z[np.arange(len(X)), s * 20 + X[:, s]] = 1.0
    return Z


def pair_feats(X):
    F = [onehot(X)]
    for (i, j) in PAIRS:
        P = np.zeros((len(X), 400))
        P[np.arange(len(X)), X[:, i] * 20 + X[:, j]] = 1.0
        F.append(P)
    return np.hstack(F)


def ridge_fit(F, y, alpha):
    """Ridge with unpenalised intercept, dual solve (n << p)."""
    mu, ym = F.mean(0), y.mean()
    Fc = F - mu
    K = Fc @ Fc.T
    a = np.linalg.solve(K + alpha * np.eye(len(y)), y - ym)
    return Fc.T @ a, mu, ym


def cv_alpha(F, y, grid, rng, k=5):
    idx = rng.permutation(len(y))
    folds = np.array_split(idx, k)
    err = np.zeros(len(grid))
    for f in folds:
        tr = np.setdiff1d(idx, f)
        for gi, al in enumerate(grid):
            w, mu, ym = ridge_fit(F[tr], y[tr], al)
            err[gi] += (((F[f] - mu) @ w + ym - y[f]) ** 2).sum()
    return grid[int(np.argmin(err))]


def predict_chunks(fn, X, n=20000):
    return np.concatenate([fn(X[i:i + n]) for i in range(0, len(X), n)])


def sys_ridge(Xtr, ytr, Xte, rng, cfg, pairwise):
    feat = pair_feats if pairwise else onehot
    F = feat(Xtr)
    grid = np.array([10.0 ** e for e in range(-3, 4)])
    alpha = cfg["alpha"] if cfg.get("alpha") is not None else cv_alpha(F, ytr, grid, rng)
    w, mu, ym = ridge_fit(F, ytr, alpha)
    pred = predict_chunks(lambda Z: (feat(Z) - mu) @ w + ym, Xte)
    return pred, {"alpha": float(alpha)}


def hamming(Za, Zb):
    return 4.0 - Za @ Zb.T


def sys_gp(Xtr, ytr, Xte, rng, cfg):
    """GP, kernel s2 * exp(-gamma * Hamming) (RBF on one-hot, since |z-z'|^2 = 2 Hamming) + noise.
    Hyper-parameters (s2, gamma, noise) by grid search on the log marginal likelihood of the training data."""
    Z = onehot(Xtr)
    Hd = hamming(Z, Z)
    m, sd = ytr.mean(), ytr.std() + 1e-12
    yt = (ytr - m) / sd
    n = len(yt)
    if cfg.get("fixed"):
        grid = [(1.0, 0.5, 0.1)]
    else:
        grid = [(s2, g, nz) for s2 in (0.3, 1.0, 3.0) for g in (0.05, 0.1, 0.2, 0.4, 0.8, 1.6) for nz in (0.01, 0.05, 0.2, 0.8)]
    best = None
    for (s2, g, nz) in grid:
        K = s2 * np.exp(-g * Hd) + nz * np.eye(n)
        try:
            L = np.linalg.cholesky(K)
        except np.linalg.LinAlgError:
            continue
        a = np.linalg.solve(L.T, np.linalg.solve(L, yt))
        lml = -0.5 * yt @ a - np.log(np.diag(L)).sum()
        if best is None or lml > best[0]:
            best = (lml, s2, g, nz, a)
    _, s2, g, nz, a = best
    pred = predict_chunks(lambda Xc: (s2 * np.exp(-g * hamming(onehot(Xc), Z))) @ a * sd + m, Xte, 5000)
    return pred, {"gp_s2": s2, "gp_gamma": g, "gp_noise": nz}


def sys_cnn(Xtr, ytr, Xte, rng, cfg, seed):
    import torch, torch.nn as nn
    torch.set_num_threads(2)
    torch.manual_seed(seed)
    H, E = cfg["width"], cfg["epochs"]
    m, sd = ytr.mean(), ytr.std() + 1e-12

    class Net(nn.Module):
        def __init__(s):
            super().__init__()
            s.emb = nn.Embedding(20, 16)
            s.conv = nn.Conv1d(16, H, 2, padding=1)  # length 4 -> 5
            s.head = nn.Sequential(nn.ReLU(), nn.Flatten(), nn.Dropout(cfg["dropout"]), nn.Linear(H * 5, 32), nn.ReLU(), nn.Linear(32, 1))

        def forward(s, x):
            return s.head(s.conv(s.emb(x).transpose(1, 2))).squeeze(-1)

    xt = torch.tensor(Xtr)
    yt = torch.tensor((ytr - m) / sd, dtype=torch.float32)
    preds = []
    for e in range(cfg["ensemble"]):
        net = Net()
        opt = torch.optim.AdamW(net.parameters(), lr=cfg["lr"], weight_decay=cfg["wd"])
        bs = min(32, len(yt))
        net.train()
        for ep in range(E):
            perm = torch.randperm(len(yt))
            for i in range(0, len(yt), bs):
                b = perm[i:i + bs]
                opt.zero_grad()
                loss = ((net(xt[b]) - yt[b]) ** 2).mean()
                loss.backward()
                opt.step()
        net.eval()
        with torch.no_grad():
            preds.append(np.concatenate([net(torch.tensor(Xte[i:i + 50000])).numpy() for i in range(0, len(Xte), 50000)]))
    return np.mean(preds, 0) * sd + m, {}


def top100_recall(y, pred):
    k = 100
    return len(set(np.argsort(-y)[:k]) & set(np.argsort(-pred)[:k])) / k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--alpha", type=float, default=None)
    ap.add_argument("--gp_fixed", type=int, default=0)
    ap.add_argument("--width", type=int, default=64)
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--lr", type=float, default=3e-3)
    ap.add_argument("--wd", type=float, default=1e-1)
    ap.add_argument("--dropout", type=float, default=0.2)
    ap.add_argument("--ensemble", type=int, default=1)
    ap.add_argument("--log_target", type=int, default=0)
    a = ap.parse_args()
    print("config", vars(a), flush=True)
    t0 = time.time()
    regime, n = a.task.split("_")
    n = int(n)
    X, y, hd = load()
    rng = np.random.RandomState(1000 * a.seed + n)  # same draw for every system at (task, seed)
    pool = np.arange(len(y)) if regime == "rand" else np.where(hd <= 2)[0]
    tr = rng.choice(pool, n, replace=False)
    mask = np.ones(len(y), bool)
    if regime == "dbl":
        mask = hd >= 3
    mask[tr] = False
    te = np.where(mask)[0]
    ytr = y[tr]
    if a.log_target:
        ytr = np.log(ytr + 0.01)
    srng = np.random.RandomState(a.seed)
    cfg = vars(a)
    if a.system == "ridge":
        pred, info = sys_ridge(X[tr], ytr, X[te], srng, cfg, False)
    elif a.system == "pairwise":
        pred, info = sys_ridge(X[tr], ytr, X[te], srng, cfg, True)
    elif a.system == "gp":
        pred, info = sys_gp(X[tr], ytr, X[te], srng, {"fixed": a.gp_fixed})
    elif a.system == "cnn":
        pred, info = sys_cnn(X[tr], ytr, X[te], srng, cfg, a.seed)
    else:
        raise SystemExit("unknown system")
    yte = y[te]
    out = {"spearman": float(spearmanr(pred, yte)[0]), "top100_recall": top100_recall(yte, pred),
           "n_train": n, "n_test": int(len(te))}
    for h in (2, 3, 4):
        mk = hd[te] == h
        if mk.sum() >= 100:
            out[f"spearman_hd{h}"] = float(spearmanr(pred[mk], yte[mk])[0])
    out.update(info)
    print("metrics", json.dumps(out), "seconds", round(time.time() - t0, 1), flush=True)
    json.dump(out, open(a.out, "w"))


if __name__ == "__main__":
    main()
