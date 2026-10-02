"""Calibration under shift on scikit-learn digits.
Usage: python method/run.py --system {mlp,ts,ts_oracle,mcd,mcd_det,ens} --task rot30 --seed 0 --out metrics.json
Models are trained once per (architecture, seed) and cached in /tmp/calib_cache (training is deterministic)."""
import argparse, json, os, hashlib
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from scipy.ndimage import rotate
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

torch.set_num_threads(2)
CACHE = "/tmp/calib_cache"
EPOCHS, LR, BS, HID = 100, 1e-3, 64, 128

def split(seed):
    X, y = load_digits(return_X_y=True)
    X = (X / 16.0).astype(np.float32)
    Xtr, Xr, ytr, yr = train_test_split(X, y, test_size=0.4, stratify=y, random_state=seed)
    Xva, Xte, yva, yte = train_test_split(Xr, yr, test_size=0.625, stratify=yr, random_state=seed)
    return Xtr, ytr, Xva, yva, Xte, yte  # 1078 / 269 / 450

def shift(X, task, rng):
    """task: rot<deg>, noise<sigma>, rot<deg>_noise<sigma>. Rotation first, then additive Gaussian noise, clip to [0,1]."""
    X = X.copy()
    for part in task.split("_"):
        if part.startswith("rot") and float(part[3:]) != 0:
            a = float(part[3:])
            X = np.stack([rotate(x.reshape(8, 8), a, reshape=False, order=1, mode="constant", cval=0.0).ravel() for x in X])
        elif part.startswith("noise"):
            X = np.clip(X + rng.normal(0, float(part[5:]), X.shape), 0, 1)
    return X.astype(np.float32)

def make_net(p):
    return nn.Sequential(nn.Linear(64, HID), nn.ReLU(), nn.Dropout(p), nn.Linear(HID, HID), nn.ReLU(), nn.Dropout(p), nn.Linear(HID, 10))

def train(Xtr, ytr, seed, p):
    key = hashlib.md5(f"{seed}-{p}-{EPOCHS}-{LR}-{BS}-{HID}".encode()).hexdigest()[:10]
    path = f"{CACHE}/{key}.pt"
    net = make_net(p)
    if os.path.exists(path):
        net.load_state_dict(torch.load(path)); return net
    torch.manual_seed(seed)
    net = make_net(p)
    opt = torch.optim.Adam(net.parameters(), lr=LR)
    X, y = torch.tensor(Xtr), torch.tensor(ytr)
    g = torch.Generator().manual_seed(seed)
    net.train()
    for _ in range(EPOCHS):
        perm = torch.randperm(len(X), generator=g)
        for i in range(0, len(X), BS):
            idx = perm[i:i + BS]
            opt.zero_grad(); F.cross_entropy(net(X[idx]), y[idx]).backward(); opt.step()
    os.makedirs(CACHE, exist_ok=True); torch.save(net.state_dict(), path)
    return net

@torch.no_grad()
def logits(net, X, train_mode=False):
    net.train(train_mode)
    return net(torch.tensor(X))

def fit_temperature(lg, y):
    logT = torch.zeros(1, requires_grad=True)
    opt = torch.optim.LBFGS([logT], lr=0.1, max_iter=200)
    y = torch.tensor(y)
    def closure():
        opt.zero_grad(); l = F.cross_entropy(lg / logT.exp(), y); l.backward(); return l
    opt.step(closure)
    return float(logT.exp().detach())

def metrics(P, y, nb=15):
    P = np.clip(P, 1e-12, 1); P = P / P.sum(1, keepdims=True)
    conf, pred = P.max(1), P.argmax(1)
    corr = (pred == y).astype(float)
    ece = 0.0
    edges = np.linspace(0, 1, nb + 1)
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any():
            ece += m.mean() * abs(corr[m].mean() - conf[m].mean())
    onehot = np.eye(10)[y]
    return {"accuracy": float(corr.mean()), "ece": float(ece), "nll": float(-np.log(P[np.arange(len(y)), y]).mean()),
            "brier": float(((P - onehot) ** 2).sum(1).mean()), "conf": float(conf.mean())}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True); ap.add_argument("--task", required=True)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out", required=True)
    ap.add_argument("--members", type=int, default=5); ap.add_argument("--p", type=float, default=0.2)
    ap.add_argument("--mc", type=int, default=20)
    a = ap.parse_args()
    print("config:", vars(a), f"epochs={EPOCHS} lr={LR} bs={BS} hidden={HID}", flush=True)
    Xtr, ytr, Xva, yva, Xte, yte = split(a.seed)
    Xs = shift(Xte, a.task, np.random.default_rng(10_000 + a.seed))  # test shift
    out = {}
    if a.system in ("mlp", "ts", "ts_oracle"):
        net = train(Xtr, ytr, a.seed * 100, 0.0)
        lg = logits(net, Xs)
        T = 1.0
        if a.system == "ts":
            T = fit_temperature(logits(net, Xva), yva)  # fitted on unshifted validation split
        elif a.system == "ts_oracle":
            Xvs = shift(Xva, a.task, np.random.default_rng(20_000 + a.seed))  # val shifted like the test condition
            T = fit_temperature(logits(net, Xvs), yva)
        P = F.softmax(lg / T, 1).numpy(); out["temperature"] = T
    elif a.system == "mcd":
        net = train(Xtr, ytr, a.seed * 100, a.p)
        torch.manual_seed(5_000 + a.seed)
        P = np.mean([F.softmax(logits(net, Xs, True), 1).numpy() for _ in range(a.mc)], 0)
    elif a.system == "mcd_det":  # ablation: same dropout-trained net as mcd, but deterministic (dropout off) single pass
        net = train(Xtr, ytr, a.seed * 100, a.p)
        P = F.softmax(logits(net, Xs), 1).numpy()
    elif a.system == "ens":
        nets = [train(Xtr, ytr, a.seed * 100 + m, 0.0) for m in range(a.members)]
        P = np.mean([F.softmax(logits(n, Xs), 1).numpy() for n in nets], 0)
    else:
        raise SystemExit("unknown system")
    out.update(metrics(P, yte))
    print("metrics:", json.dumps(out), flush=True)
    json.dump(out, open(a.out, "w"))

if __name__ == "__main__":
    main()
