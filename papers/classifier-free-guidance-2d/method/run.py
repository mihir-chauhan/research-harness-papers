"""Conditional diffusion on a 2D class-conditional mixture; CFG / low-temperature sampling; metrics.

Usage: python method/run.py --task mix_overlap --seed 0 --w 3 --tau 1 --out m.json
w = guidance scale (Ho & Salimans convention: eps = (1+w) eps_c - w eps_u; w=0 is unguided).
tau = temperature: scales the initial noise x_T and every ancestral noise injection.
"""
import argparse, json, os, time, math
import numpy as np, torch, torch.nn as nn
torch.set_num_threads(2)

K, M, R = 4, 3, 4.0
WEIGHTS = np.array([0.5, 0.3, 0.2])
SIGMA = {"mix_overlap": 0.6, "mix_sep": 0.35}
T = 100
SCALE = 3.0          # data are divided by SCALE before the network sees them
CLIP = 3.0           # x0-prediction clipping (normalised units), identical for every system
RADIUS = 3.0         # a sample is "in" a mode if within RADIUS sigma of its centre


def layout():
    j = np.arange(K * M)
    ang = 2 * np.pi * j / (K * M)
    mu = R * np.stack([np.cos(ang), np.sin(ang)], 1)
    cls = j % K
    w = WEIGHTS[j // K]
    return mu, cls, w


def sample_data(task, n, rng, cls_fixed=None):
    mu, cls, w = layout()
    sig = SIGMA[task]
    c = rng.integers(0, K, n) if cls_fixed is None else np.full(n, cls_fixed)
    x = np.zeros((n, 2))
    for k in range(K):
        idx = np.where(c == k)[0]
        mods = np.where(cls == k)[0]
        pick = rng.choice(mods, size=len(idx), p=w[mods])
        x[idx] = mu[pick] + sig * rng.standard_normal((len(idx), 2))
    return x.astype(np.float32), c


class Net(nn.Module):
    def __init__(self, h=128):
        super().__init__()
        self.cemb = nn.Embedding(K + 1, 32)     # index K = null label
        self.temb = nn.Sequential(nn.Linear(16, 32), nn.SiLU())
        self.f = nn.Sequential(nn.Linear(2 + 64, h), nn.SiLU(), nn.Linear(h, h), nn.SiLU(),
                               nn.Linear(h, h), nn.SiLU(), nn.Linear(h, 2))

    def forward(self, x, t, c):
        fr = torch.exp(torch.linspace(0, math.log(100.0), 8))
        a = (t[:, None].float() / T) * fr[None] * 2 * math.pi
        te = self.temb(torch.cat([a.sin(), a.cos()], 1))
        return self.f(torch.cat([x, te, self.cemb(c)], 1))


def schedule():
    s = np.linspace(0, 1, T + 1)
    f = np.cos((s + 0.008) / 1.008 * np.pi / 2) ** 2
    ab = f / f[0]
    betas = np.clip(1 - ab[1:] / ab[:-1], 0, 0.999)
    alphas = 1 - betas
    abar = np.cumprod(alphas)
    return [torch.tensor(v, dtype=torch.float32) for v in (betas, alphas, abar)]


def train(task, seed, p_uncond, steps, bs=512, lr=2e-3):
    torch.manual_seed(seed); rng = np.random.default_rng(1000 + seed)
    net = Net(); opt = torch.optim.Adam(net.parameters(), lr=lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps)
    _, _, abar = schedule()
    for it in range(steps):
        x, c = sample_data(task, bs, rng)
        x0 = torch.tensor(x) / SCALE; c = torch.tensor(c)
        c = torch.where(torch.rand(bs) < p_uncond, torch.full_like(c, K), c)
        t = torch.randint(0, T, (bs,)); eps = torch.randn_like(x0)
        xt = abar[t].sqrt()[:, None] * x0 + (1 - abar[t]).sqrt()[:, None] * eps
        loss = ((net(xt, t, c) - eps) ** 2).mean()
        opt.zero_grad(); loss.backward(); opt.step(); sched.step()
    return net, float(loss.detach())


@torch.no_grad()
def sample(net, c, w, tau, gen, lo=0.0, hi=1.0):
    """Ancestral DDPM sampling. Guidance is applied only when lo <= t/T <= hi (default: always)."""
    betas, alphas, abar = schedule()
    n = len(c); c = torch.tensor(c); cn = torch.full_like(c, K)
    x = tau * torch.randn(n, 2, generator=gen)
    for t in range(T - 1, -1, -1):
        tt = torch.full((n,), t)
        e = net(x, tt, c)
        if w != 0 and lo <= (t + 1) / T <= hi:
            e = (1 + w) * e - w * net(x, tt, cn)
        x0 = ((x - (1 - abar[t]).sqrt() * e) / abar[t].sqrt()).clamp(-CLIP, CLIP)
        ab_prev = abar[t - 1] if t > 0 else torch.tensor(1.0)
        mean = (ab_prev.sqrt() * betas[t] / (1 - abar[t])) * x0 + (alphas[t].sqrt() * (1 - ab_prev) / (1 - abar[t])) * x
        if t > 0:
            var = betas[t] * (1 - ab_prev) / (1 - abar[t])
            x = mean + tau * var.sqrt() * torch.randn(n, 2, generator=gen)
        else:
            x = mean
    return x.numpy() * SCALE


def sliced_w(a, b, rng, nproj=64):
    th = rng.standard_normal((nproj, 2)); th /= np.linalg.norm(th, axis=1, keepdims=True)
    pa, pb = np.sort(a @ th.T, 0), np.sort(b @ th.T, 0)
    return float(np.mean(np.abs(pa - pb)))


def metrics(task, xs, rng):
    """xs: dict class -> samples (n,2). Averages over classes."""
    mu, cls, w = layout(); sig = SIGMA[task]
    out = {k: [] for k in ["class_acc", "support_prec", "mode_cov", "mode_tv", "std_ratio", "off_support", "swd"]}
    for c in range(K):
        x = xs[c]; n = len(x)
        d_all = np.linalg.norm(x[:, None] - mu[None], axis=2) / sig        # (n,12)
        logp = -0.5 * d_all ** 2 + np.log(w)[None]                           # equal class priors
        pc = np.stack([np.logaddexp.reduce(logp[:, cls == k], axis=1) for k in range(K)], 1)
        out["class_acc"].append(np.mean(pc.argmax(1) == c))
        out["off_support"].append(np.mean(d_all.min(1) > RADIUS))
        mods = np.where(cls == c)[0]
        d = d_all[:, mods]; near = d.argmin(1); dm = d.min(1); ok = dm <= RADIUS
        out["support_prec"].append(ok.mean())
        cnt = np.array([np.sum(ok & (near == m)) for m in range(M)])
        wt = w[mods]
        out["mode_cov"].append(np.mean(cnt / n >= 0.5 * wt))
        out["mode_tv"].append(0.5 * np.abs(cnt / max(cnt.sum(), 1) - wt).sum())
        out["std_ratio"].append(np.sqrt(np.mean(dm[ok] ** 2) / 2) if ok.any() else 0.0)
        ref, _ = sample_data(task, n, rng, cls_fixed=c)
        out["swd"].append(sliced_w(x, ref, rng))
    return {k: float(np.mean(v)) for k, v in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="mix_overlap"); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--w", type=float, default=0.0); ap.add_argument("--tau", type=float, default=1.0)
    ap.add_argument("--p_uncond", type=float, default=0.1); ap.add_argument("--steps", type=int, default=5000)
    ap.add_argument("--lo", type=float, default=0.0); ap.add_argument("--hi", type=float, default=1.0)
    ap.add_argument("--n", type=int, default=1500, help="samples per class")
    ap.add_argument("--real", action="store_true", help="evaluate fresh real samples (reference row)")
    ap.add_argument("--ckpt_dir", default="results/raw/ckpt"); ap.add_argument("--out", required=True)
    a = ap.parse_args(); print("config:", json.dumps(vars(a)), flush=True)
    rng = np.random.default_rng(5000 + a.seed); t0 = time.time(); extra = {}
    if a.real:
        xs = {c: sample_data(a.task, a.n, rng, cls_fixed=c)[0] for c in range(K)}
    else:
        os.makedirs(a.ckpt_dir, exist_ok=True)
        f = f"{a.ckpt_dir}/{a.task}_s{a.seed}_p{a.p_uncond}_n{a.steps}.pt"
        if os.path.exists(f):
            net = Net(); net.load_state_dict(torch.load(f)); print("loaded cached model", f)
        else:
            net, loss = train(a.task, a.seed, a.p_uncond, a.steps); torch.save(net.state_dict(), f)
            print(f"trained model, last-batch loss {loss:.4f}, {time.time()-t0:.0f}s")
        net.eval(); gen = torch.Generator().manual_seed(7000 + a.seed)
        xs = {c: sample(net, np.full(a.n, c), a.w, a.tau, gen, a.lo, a.hi) for c in range(K)}
    m = metrics(a.task, xs, rng)
    m["wall_s"] = time.time() - t0
    print("metrics:", json.dumps(m)); json.dump(m, open(a.out, "w"))

if __name__ == "__main__":
    main()
