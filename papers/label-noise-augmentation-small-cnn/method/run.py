"""Label-noise robustness of a small CNN on sklearn 8x8 digits.
Usage: python method/run.py --system ce|ls|mixup|smallloss --noise 0.4 --seed 0 --out m.json
"""
import argparse, json, time
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

torch.set_num_threads(2)
p = argparse.ArgumentParser()
p.add_argument("--system", required=True, choices=["ce", "ls", "mixup", "smallloss"])
p.add_argument("--noise", type=float, required=True)
p.add_argument("--seed", type=int, default=0)
p.add_argument("--epochs", type=int, default=60)
p.add_argument("--bs", type=int, default=64)
p.add_argument("--lr", type=float, default=0.05)
p.add_argument("--wd", type=float, default=5e-4)
p.add_argument("--ls_eps", type=float, default=0.1)
p.add_argument("--mix_alpha", type=float, default=1.0)
p.add_argument("--sl_warmup", type=int, default=10)   # epochs before forgetting starts
p.add_argument("--sl_ramp", type=int, default=10)     # epochs to ramp the forget rate to its target
p.add_argument("--sl_rate", type=float, default=-1.0) # assumed noise rate; <0 means the true rate
p.add_argument("--out", required=True)
a = p.parse_args()
print("config", json.dumps(vars(a)))
t0 = time.time()

# data: fixed split (seed-independent stratified 60/40), noise and init depend on seed
X, y = load_digits(return_X_y=True)
X = (X / 16.0).astype(np.float32).reshape(-1, 1, 8, 8)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.4, stratify=y, random_state=1234)
rng = np.random.RandomState(a.seed)
K = 10
n = len(ytr)
ynoisy = ytr.copy()
flip = rng.rand(n) < a.noise            # symmetric: replaced by a uniformly random *other* class
for i in np.where(flip)[0]:
    ynoisy[i] = rng.choice([c for c in range(K) if c != ytr[i]])
corrupt = ynoisy != ytr
torch.manual_seed(a.seed)
Xtr_t, Xte_t = torch.tensor(Xtr), torch.tensor(Xte)
yn_t = torch.tensor(ynoisy)

net = nn.Sequential(
    nn.Conv2d(1, 16, 3, padding=1), nn.BatchNorm2d(16), nn.ReLU(),
    nn.Conv2d(16, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),
    nn.Flatten(), nn.Linear(64 * 2 * 2, 64), nn.ReLU(), nn.Linear(64, K))
opt = torch.optim.SGD(net.parameters(), lr=a.lr, momentum=0.9, weight_decay=a.wd)
sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, a.epochs)

def ls_loss(logits, y, eps):
    return F.cross_entropy(logits, y, label_smoothing=eps, reduction="none")

def predict(x):
    net.eval()
    with torch.no_grad():
        return net(x).argmax(1).numpy()

forget_target = a.noise if a.sl_rate < 0 else a.sl_rate
curve = []
for ep in range(a.epochs):
    net.train()
    perm = torch.randperm(n)
    for s in range(0, n, a.bs):
        idx = perm[s:s + a.bs]
        if len(idx) < 2: continue
        x, yb = Xtr_t[idx], yn_t[idx]
        if a.system == "ce":
            loss = F.cross_entropy(net(x), yb)
        elif a.system == "ls":
            loss = ls_loss(net(x), yb, a.ls_eps).mean()
        elif a.system == "mixup":
            lam = float(np.random.RandomState(a.seed * 100003 + ep * 997 + s).beta(a.mix_alpha, a.mix_alpha)) if a.mix_alpha > 0 else 1.0
            j = torch.randperm(len(idx))
            out = net(lam * x + (1 - lam) * x[j])
            loss = lam * F.cross_entropy(out, yb) + (1 - lam) * F.cross_entropy(out, yb[j])
        else:  # smallloss: one network, keep the (1-forget) fraction of smallest-loss samples per batch
            if ep < a.sl_warmup:
                forget = 0.0
            else:
                forget = forget_target * min(1.0, (ep - a.sl_warmup + 1) / max(1, a.sl_ramp))
            l = F.cross_entropy(net(x), yb, reduction="none")
            keep = max(1, int(round((1 - forget) * len(idx))))
            sel = torch.argsort(l.detach())[:keep]
            loss = l[sel].mean()
        opt.zero_grad(); loss.backward(); opt.step()
    sched.step()
    if ep % 5 == 4 or ep == a.epochs - 1:
        curve.append((ep + 1, float((predict(Xte_t) == yte).mean())))

ptr, pte = predict(Xtr_t), predict(Xte_t)
res = {
    "test_acc": float((pte == yte).mean()),
    "train_fit_noisy": float((ptr == ynoisy).mean()),            # agreement with the given (noisy) labels
    "mem_rate": float((ptr[corrupt] == ynoisy[corrupt]).mean()) if corrupt.any() else 0.0,   # corrupted samples fitted to the wrong label
    "recover_rate": float((ptr[corrupt] == ytr[corrupt]).mean()) if corrupt.any() else 0.0,  # corrupted samples predicted as the true label
    "clean_fit": float((ptr[~corrupt] == ynoisy[~corrupt]).mean()),
}
res["mem_gap"] = res["mem_rate"] - res["recover_rate"]
res["n_corrupt"] = int(corrupt.sum())
res["runtime_s"] = time.time() - t0
print("curve(epoch,test_acc)", curve)
print("metrics", json.dumps(res))
json.dump(res, open(a.out, "w"))
