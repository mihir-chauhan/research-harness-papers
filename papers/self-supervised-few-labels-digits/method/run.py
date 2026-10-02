"""Few-label digits: self-supervised pretraining vs scratch vs PCA.

python method/run.py --system simclr --task n50 --seed 0 --out metrics.json
Systems: pca_lr, pixels_lr, random_cnn, supervised, rotation, simclr
Tasks: n10, n50, n200 (total labelled examples, class balanced)
"""
import argparse, json, math, os, time
import numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

torch.set_num_threads(2)
N_TEST = 497          # fixed-size stratified test split, never used for training or selection


def get_split(seed, n_labels):
    X, y = load_digits(return_X_y=True)
    X = (X / 16.0).astype(np.float32).reshape(-1, 1, 8, 8)
    rng = np.random.RandomState(seed)
    test, pool = [], []
    lab_order = {}
    for c in range(10):
        idx = rng.permutation(np.where(y == c)[0])
        k = int(round(N_TEST * len(idx) / len(y)))
        test += list(idx[:k]); rest = idx[k:]
        pool += list(rest); lab_order[c] = rest   # rest is already shuffled
    per = n_labels // 10
    lab = np.concatenate([lab_order[c][:per] for c in range(10)])
    return X, y, np.array(pool), lab, np.array(test)


class Encoder(nn.Module):
    def __init__(self, w=32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(1, w, 3, padding=1), nn.BatchNorm2d(w), nn.ReLU(),
            nn.Conv2d(w, 2 * w, 3, padding=1), nn.BatchNorm2d(2 * w), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(2 * w, 2 * w, 3, padding=1), nn.BatchNorm2d(2 * w), nn.ReLU(),
            nn.AdaptiveAvgPool2d(2), nn.Flatten())
        self.dim = 2 * w * 4
    def forward(self, x): return self.net(x)


def affine_aug(x, rot=15.0, shift=1.0, scale=0.1):
    B = x.shape[0]
    a = (torch.rand(B) * 2 - 1) * rot * math.pi / 180
    s = 1 + (torch.rand(B) * 2 - 1) * scale
    t = (torch.rand(B, 2) * 2 - 1) * shift * 0.25   # 1 px = 0.25 in normalised coords for 8 px
    th = torch.zeros(B, 2, 3)
    th[:, 0, 0] = torch.cos(a) / s; th[:, 0, 1] = -torch.sin(a) / s
    th[:, 1, 0] = torch.sin(a) / s; th[:, 1, 1] = torch.cos(a) / s
    th[:, :, 2] = t
    g = F.affine_grid(th, x.shape, align_corners=False)
    return F.grid_sample(x, g, padding_mode="zeros", align_corners=False)


def photo_aug(x, noise=0.1, bright=0.2):
    B = x.shape[0]
    x = x * (1 + (torch.rand(B, 1, 1, 1) * 2 - 1) * bright) + noise * torch.randn_like(x)
    return x.clamp(0, 1)


def augment(x, mode):
    if mode in ("full", "geom"): x = affine_aug(x)
    if mode in ("full", "photo"): x = photo_aug(x)
    return x


def nt_xent(z1, z2, tau):
    z = F.normalize(torch.cat([z1, z2]), dim=1)
    B = z1.shape[0]
    sim = z @ z.t() / tau
    sim.fill_diagonal_(-1e9)
    tgt = torch.cat([torch.arange(B, 2 * B), torch.arange(0, B)])
    return F.cross_entropy(sim, tgt)


def pretrain_simclr(Xu, enc, a):
    proj = nn.Sequential(nn.Linear(enc.dim, 128), nn.ReLU(), nn.Linear(128, 64))
    opt = torch.optim.Adam(list(enc.parameters()) + list(proj.parameters()), lr=a.lr, weight_decay=1e-5)
    N = len(Xu); last = 0.0
    for ep in range(a.epochs):
        perm = torch.randperm(N); tot = 0; nb = 0
        for i in range(0, N - a.batch + 1, a.batch):
            xb = Xu[perm[i:i + a.batch]]
            loss = nt_xent(proj(enc(augment(xb, a.aug))), proj(enc(augment(xb, a.aug))), a.tau)
            opt.zero_grad(); loss.backward(); opt.step(); tot += loss.item(); nb += 1
        last = tot / max(nb, 1)
    return last


def pretrain_rotation(Xu, enc, a):
    head = nn.Linear(enc.dim, 4)
    opt = torch.optim.Adam(list(enc.parameters()) + list(head.parameters()), lr=a.lr, weight_decay=1e-5)
    N = len(Xu); last = 0.0
    for ep in range(a.epochs):
        perm = torch.randperm(N); tot = 0; nb = 0
        for i in range(0, N - a.batch + 1, a.batch):
            xb = Xu[perm[i:i + a.batch]]
            xs = torch.cat([torch.rot90(xb, k, (2, 3)) for k in range(4)])
            ys = torch.arange(4).repeat_interleave(len(xb))
            loss = F.cross_entropy(head(enc(xs)), ys)
            opt.zero_grad(); loss.backward(); opt.step(); tot += loss.item(); nb += 1
        last = tot / max(nb, 1)
    return last


def features(enc, X):
    enc.eval()
    with torch.no_grad(): return enc(torch.from_numpy(X)).numpy()


def probe(Ftr, ytr, Fte, yte, C):
    sc = StandardScaler().fit(Ftr)
    clf = LogisticRegression(C=C, max_iter=2000).fit(sc.transform(Ftr), ytr)
    return clf.score(sc.transform(Fte), yte), clf.score(sc.transform(Ftr), ytr)


def train_supervised(enc, Xl, yl, a):
    head = nn.Linear(enc.dim, 10)
    opt = torch.optim.Adam(list(enc.parameters()) + list(head.parameters()), lr=a.sup_lr, weight_decay=a.sup_wd)
    bs = min(len(Xl), 32)
    enc.train()
    for step in range(a.sup_steps):
        idx = torch.randperm(len(Xl))[:bs]
        xb = augment(Xl[idx], a.sup_aug) if a.sup_aug != "none" else Xl[idx]
        loss = F.cross_entropy(head(enc(xb)), yl[idx])
        opt.zero_grad(); loss.backward(); opt.step()
    enc.eval()
    return enc, head


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--system", required=True); p.add_argument("--task", required=True)
    p.add_argument("--seed", type=int, default=0); p.add_argument("--out", required=True)
    p.add_argument("--epochs", type=int, default=60); p.add_argument("--batch", type=int, default=128)
    p.add_argument("--lr", type=float, default=1e-3); p.add_argument("--tau", type=float, default=0.5)
    p.add_argument("--aug", default="full", choices=["full", "geom", "photo"])
    p.add_argument("--C", type=float, default=1.0); p.add_argument("--pca_dim", type=int, default=16)
    p.add_argument("--width", type=int, default=32)
    p.add_argument("--sup_steps", type=int, default=300); p.add_argument("--sup_lr", type=float, default=1e-3)
    p.add_argument("--sup_wd", type=float, default=1e-4); p.add_argument("--sup_aug", default="none")
    a = p.parse_args()
    print("config:", json.dumps(vars(a)), flush=True)
    t0 = time.time()
    torch.manual_seed(a.seed); np.random.seed(a.seed)
    nl = int(a.task[1:])
    X, y, pool, lab, test = get_split(a.seed, nl)
    Xl, yl, Xt, yt = X[lab], y[lab], X[test], y[test]
    out = {}
    if a.system == "pixels_lr":
        acc, tr = probe(Xl.reshape(len(Xl), -1), yl, Xt.reshape(len(Xt), -1), yt, a.C)
    elif a.system == "pca_lr":
        # PCA is fitted on the same unlabeled pool the SSL encoders see (no labels, no test data)
        pca = PCA(n_components=a.pca_dim, random_state=a.seed).fit(X[pool].reshape(len(pool), -1))
        acc, tr = probe(pca.transform(Xl.reshape(len(Xl), -1)), yl, pca.transform(Xt.reshape(len(Xt), -1)), yt, a.C)
    else:
        enc = Encoder(a.width)
        Xu = torch.from_numpy(X[pool])
        if a.system in ("simclr", "rotation"):
            # pretraining uses only the unlabeled pool and does not depend on the label budget, so the
            # encoder is cached per (system, seed, pretraining hyperparameters) and shared across tasks
            key = f"{a.system}_s{a.seed}_e{a.epochs}_b{a.batch}_lr{a.lr}_t{a.tau}_{a.aug}_w{a.width}"
            path = os.path.join("results", "cache", key + ".pt")
            if os.path.exists(path):
                ck = torch.load(path); enc.load_state_dict(ck["enc"]); out["pretrain_loss"] = ck["loss"]
                print("loaded cached encoder", key, flush=True)
            else:
                fn = pretrain_simclr if a.system == "simclr" else pretrain_rotation
                out["pretrain_loss"] = fn(Xu, enc, a)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                torch.save({"enc": enc.state_dict(), "loss": out["pretrain_loss"]}, path)
        if a.system == "supervised":
            enc, head = train_supervised(enc, torch.from_numpy(Xl), torch.from_numpy(yl), a)
            with torch.no_grad():
                acc = (head(enc(torch.from_numpy(Xt))).argmax(1).numpy() == yt).mean()
                tr = (head(enc(torch.from_numpy(Xl))).argmax(1).numpy() == yl).mean()
            acc, tr = float(acc), float(tr)
        elif a.system in ("random_cnn", "simclr", "rotation"):
            acc, tr = probe(features(enc, Xl), yl, features(enc, Xt), yt, a.C)
        else:
            raise SystemExit("unknown system")
    out.update(test_acc=float(acc), train_acc=float(tr), seconds=time.time() - t0)
    print("metrics:", json.dumps(out), flush=True)
    json.dump(out, open(a.out, "w"))


if __name__ == "__main__":
    main()
