"""Train a small U-Net on synthetic shapes with noisy labels; report per-class IoU on the clean test set."""
import argparse, json, os, time
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from scipy import ndimage as ndi
from data import make_split, corrupt, CLASSES

torch.set_num_threads(2)
POOL_SEED, TEST_SEED = 1000, 2000


def block(i, o):
    return nn.Sequential(nn.Conv2d(i, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(True),
                         nn.Conv2d(o, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(True))


def block1(i, o):
    return nn.Sequential(nn.Conv2d(i, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(True))


class UNet(nn.Module):
    def __init__(self, w=8, nc=4):
        super().__init__()
        self.e1, self.e2, self.e3 = block1(3, w), block(w, 2 * w), block(2 * w, 4 * w)
        self.b = block(4 * w, 8 * w)
        self.u3, self.d3 = nn.ConvTranspose2d(8 * w, 4 * w, 2, 2), block(8 * w, 4 * w)
        self.u2, self.d2 = nn.ConvTranspose2d(4 * w, 2 * w, 2, 2), block(4 * w, 2 * w)
        self.u1, self.d1 = nn.ConvTranspose2d(2 * w, w, 2, 2), block1(2 * w, w)
        self.out = nn.Conv2d(w, nc, 1)

    def forward(self, x):
        e1 = self.e1(x); e2 = self.e2(F.max_pool2d(e1, 2)); e3 = self.e3(F.max_pool2d(e2, 2))
        b = self.b(F.max_pool2d(e3, 2))
        d3 = self.d3(torch.cat([self.u3(b), e3], 1)); d2 = self.d2(torch.cat([self.u2(d3), e2], 1))
        d1 = self.d1(torch.cat([self.u1(d2), e1], 1))
        return self.out(d1)


def pixel_loss(system, logits, y, band, q, alpha, beta):
    """Per-pixel loss map (B,H,W) and weight map."""
    logp = F.log_softmax(logits, 1)
    py = logp.gather(1, y[:, None])[:, 0].exp()
    w = torch.ones_like(py)
    if system in ("CE", "BandIgnoreCE"):
        l = -py.clamp_min(1e-8).log()
        if system == "BandIgnoreCE":
            w = (~band).float()
    elif system == "GCE":  # Zhang & Sabuncu 2018: (1 - p_y^q)/q
        l = (1 - py.clamp_min(1e-8) ** q) / q
    elif system == "SCE":  # Wang et al. 2019: alpha*CE + beta*RCE, log 0 := A = -4
        l = alpha * -py.clamp_min(1e-8).log() + beta * 4.0 * (1 - py)
    else:
        raise ValueError(system)
    return l, w


def miou(pred, gt):
    ious = {}
    for k, n in enumerate(CLASSES):
        i = ((pred == k) & (gt == k)).sum(); u = ((pred == k) | (gt == k)).sum()
        ious[n] = i / u if u else float("nan")
    return ious


def cached_split(n, seed):
    """Data generation is deterministic in (n, seed); cache it on disk to save time."""
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache", f"split_{n}_{seed}.npz")
    if os.path.exists(f):
        z = np.load(f)
        return z["x"], z["l"], z["i"]
    x, l, i = make_split(n, seed)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    np.savez(f + f".tmp{os.getpid()}.npz", x=x, l=l, i=i)
    os.replace(f + f".tmp{os.getpid()}.npz", f)
    return x, l, i


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", default="CE"); ap.add_argument("--task", default="boundary_p0.2")
    ap.add_argument("--n", type=int, default=500); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--steps", type=int, default=600); ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--lr", type=float, default=1e-2); ap.add_argument("--q", type=float, default=0.7)
    ap.add_argument("--alpha", type=float, default=0.1); ap.add_argument("--beta", type=float, default=1.0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    print("config", vars(a), flush=True)
    kind, _, ps = a.task.partition("_p")
    p = float(ps) if ps else 0.0
    t0 = time.time()
    X, L, I = cached_split(2000, POOL_SEED); Xt, Lt, _ = cached_split(500, TEST_SEED)
    rng = np.random.default_rng(10_000 + a.seed)
    idx = rng.permutation(2000)[: a.n]
    X, L, I = X[idx], L[idx], I[idx]
    Ln = corrupt(L, I, kind, p, 20_000 + a.seed)
    noisy_frac = float((Ln != L).mean())
    band = np.stack([ndi.maximum_filter(l, size=5) != ndi.minimum_filter(l, size=5) for l in Ln])
    X, Ln, band = torch.tensor(X), torch.tensor(Ln), torch.tensor(band)
    torch.manual_seed(a.seed)
    net = UNet()
    opt = torch.optim.AdamW(net.parameters(), lr=a.lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, a.lr, total_steps=a.steps)
    g = torch.Generator().manual_seed(a.seed)
    for s in range(a.steps):
        b = torch.randint(0, a.n, (a.bs,), generator=g)
        x, y, bd = X[b], Ln[b], band[b]
        if torch.rand(1, generator=g) < 0.5:  # flip augmentation (same for all systems)
            x, y, bd = x.flip(-1), y.flip(-1), bd.flip(-1)
        l, w = pixel_loss(a.system, net(x), y, bd, a.q, a.alpha, a.beta)
        loss = (l * w).sum() / w.sum().clamp_min(1)
        opt.zero_grad(); loss.backward(); opt.step(); sched.step()
    net.eval()
    with torch.no_grad():
        pred = torch.cat([net(torch.tensor(Xt[i:i + 100])).argmax(1) for i in range(0, 500, 100)]).numpy()
        ptr = torch.cat([net(X[i:i + 100]).argmax(1) for i in range(0, a.n, 100)]).numpy()
    ious = miou(pred, Lt)
    res = {"miou": float(np.mean(list(ious.values()))), "miou_fg": float(np.mean([ious[c] for c in CLASSES[1:]]))}
    res.update({f"iou_{k}": float(v) for k, v in ious.items()})
    res["train_fit_noisy"] = float((ptr == Ln.numpy()).mean())  # agreement with the (noisy) training labels
    res["train_fit_clean"] = float((ptr == L).mean())
    res["label_noise_pixels"] = noisy_frac
    print("metrics", json.dumps(res), "time", round(time.time() - t0, 1), flush=True)
    if a.out:
        json.dump(res, open(a.out, "w"))


if __name__ == "__main__":
    main()
