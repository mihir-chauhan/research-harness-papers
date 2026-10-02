"""SGD / SGD+WD / SAM on a small MLP with symmetric label noise. One run = one (system, task, seed)."""
import argparse, json, time
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from sklearn.datasets import load_digits

torch.set_num_threads(2)

def spirals(n, rng, turns=1.5, sigma=0.15):
    y = rng.integers(0, 2, n)
    t = np.sqrt(rng.uniform(0.05, 1.0, n)) * turns * 2 * np.pi
    s = np.where(y == 0, 1.0, -1.0)
    x = np.stack([s * t * np.cos(t), s * t * np.sin(t)], 1) / (turns * 2 * np.pi)
    return (x + sigma * rng.standard_normal((n, 2)) * 0.5).astype(np.float32), y

def make_data(task, seed):
    """task = <dataset>_n<noise>; split depends on the seed; noise only in train/val labels."""
    ds, nz = task.split("_n")
    eta = float(nz)
    rng = np.random.default_rng(seed)
    if ds == "digits":
        d = load_digits(); X = (d.data / 16.0).astype(np.float32); y = d.target
        idx = rng.permutation(len(y)); ntr, nva = 600, 300
    else:
        X, y = spirals(1000, rng); idx = np.arange(1000); ntr, nva = 400, 200
    tr, va, te = idx[:ntr], idx[ntr:ntr + nva], idx[ntr + nva:]
    K = int(y.max()) + 1
    def flip(lab):
        lab = lab.copy(); m = rng.random(len(lab)) < eta
        lab[m] = (lab[m] + rng.integers(1, K, m.sum())) % K
        return lab
    out = dict(K=K, Xtr=X[tr], ytr_clean=y[tr], ytr=flip(y[tr]), Xva=X[va], yva=flip(y[va]), Xte=X[te], yte=y[te])
    return {k: (torch.tensor(v) if isinstance(v, np.ndarray) else v) for k, v in out.items()}

def mlp(din, K, h, seed):
    torch.manual_seed(seed)
    return nn.Sequential(nn.Linear(din, h), nn.ReLU(), nn.Linear(h, h), nn.ReLU(), nn.Linear(h, K))

def flat_grad(params):
    return torch.cat([p.grad.reshape(-1) for p in params])

def add_flat(params, v, sign=1.0):
    i = 0
    with torch.no_grad():
        for p in params:
            n = p.numel(); p.add_(sign * v[i:i + n].view_as(p)); i += n

@torch.no_grad()
def evaluate(m, X, y):
    o = m(X); return F.cross_entropy(o, y).item(), (o.argmax(1) == y).float().mean().item()

def full_loss_grad(m, X, y, params):
    m.zero_grad(); l = F.cross_entropy(m(X), y); l.backward(); return l.item(), flat_grad(params)

def sharpness(m, X, y, params, rho_s, n_dir, gen):
    """loss increase on the (noisy) training set under a perturbation of Euclidean norm rho_s:
    random = mean over n_dir uniformly random directions; adv = one normalised-gradient ascent step."""
    base, g = full_loss_grad(m, X, y, params)
    adv_e = rho_s * g / (g.norm() + 1e-12)
    add_flat(params, adv_e); adv = evaluate(m, X, y)[0] - base; add_flat(params, adv_e, -1.0)
    rs = []
    for _ in range(n_dir):
        u = torch.randn(g.numel(), generator=gen); e = rho_s * u / u.norm()
        add_flat(params, e); rs.append(evaluate(m, X, y)[0] - base); add_flat(params, e, -1.0)
    return float(np.mean(rs)), adv

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True, choices=["sgd", "sgd_wd", "sam", "sam_random", "sam_wd"])
    ap.add_argument("--task", required=True); ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--rho", type=float, default=0.0); ap.add_argument("--wd", type=float, default=0.0)
    ap.add_argument("--lr", type=float, default=0.1); ap.add_argument("--epochs", type=int, default=150)
    ap.add_argument("--batch", type=int, default=100); ap.add_argument("--hidden", type=int, default=128)
    ap.add_argument("--rho_sharp", type=float, default=0.5); ap.add_argument("--out", required=True)
    a = ap.parse_args(); t0 = time.time()
    print("config", json.dumps(vars(a)), flush=True)
    D = make_data(a.task, a.seed)
    m = mlp(D["Xtr"].shape[1], D["K"], a.hidden, a.seed); params = list(m.parameters())
    opt = torch.optim.SGD(params, lr=a.lr, momentum=0.9, weight_decay=a.wd)
    n = len(D["ytr"]); steps_per = int(np.ceil(n / a.batch)); total = a.epochs * steps_per
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, total)
    gen = torch.Generator().manual_seed(1000 + a.seed); perm_rng = np.random.default_rng(a.seed)
    sam = a.system.startswith("sam")
    for ep in range(a.epochs):
        perm = perm_rng.permutation(n)
        for i in range(steps_per):
            b = torch.tensor(perm[i * a.batch:(i + 1) * a.batch]); X, y = D["Xtr"][b], D["ytr"][b]
            if sam:
                m.zero_grad(); F.cross_entropy(m(X), y).backward(); g = flat_grad(params)
                if a.system == "sam_random":
                    u = torch.randn(g.numel(), generator=gen); e = a.rho * u / u.norm()
                else:
                    e = a.rho * g / (g.norm() + 1e-12)
                add_flat(params, e)
                m.zero_grad(); F.cross_entropy(m(X), y).backward()   # gradient at w+e
                add_flat(params, e, -1.0)
            else:
                m.zero_grad(); F.cross_entropy(m(X), y).backward()
            opt.step(); sched.step()
    ltr, atr = evaluate(m, D["Xtr"], D["ytr"]); lte, ate = evaluate(m, D["Xte"], D["yte"])
    lva, ava = evaluate(m, D["Xva"], D["yva"])
    flipped = D["ytr"] != D["ytr_clean"]
    with torch.no_grad(): pred = m(D["Xtr"]).argmax(1)
    mem = (pred[flipped] == D["ytr"][flipped]).float().mean().item() if flipped.any() else 0.0
    sr, sa = sharpness(m, D["Xtr"], D["ytr"], params, a.rho_sharp, 20, gen)
    wn = float(torch.sqrt(sum((p.detach() ** 2).sum() for p in params)))
    res = dict(test_acc=ate, val_acc=ava, train_acc=atr, test_loss=lte, train_loss=ltr,
               gap_acc=atr - ate, gap_loss=lte - ltr, memorised=mem,
               sharp_rand=sr, sharp_adv=sa, weight_norm=wn, runtime_s=time.time() - t0)
    print("final", json.dumps(res), flush=True)
    json.dump(res, open(a.out, "w"))

if __name__ == "__main__":
    main()
