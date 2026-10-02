"""Flow matching vs DDPM/DDIM vs reflow on 2D toy data, one shared MLP.
Usage: run.py --system {ddim,ddpm_anc,fm_euler,fm_heun,reflow,real} --task T --seed S --out FILE
"""
import argparse, json, os, time, math
import numpy as np, torch, torch.nn as nn
torch.set_num_threads(2)
KS = [1, 2, 4, 8, 16, 32, 64, 100]
CKPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "ckpt")

# ---------------- data ----------------
def sample_data(task, n, rng):
    if task == "eight_gaussians":
        a = rng.integers(0, 8, n) * (2 * np.pi / 8)
        c = 2.0 * np.stack([np.cos(a), np.sin(a)], 1)
        return (c + 0.1 * rng.standard_normal((n, 2))).astype(np.float32)
    if task == "two_moons":
        u = rng.integers(0, 2, n); th = rng.uniform(0, np.pi, n)
        x = np.where(u == 0, np.cos(th), 1 - np.cos(th)); y = np.where(u == 0, np.sin(th), 0.5 - np.sin(th))
        p = np.stack([x, y], 1) + 0.05 * rng.standard_normal((n, 2))
        return (2.0 * (p - np.array([0.5, 0.25]))).astype(np.float32)
    if task == "checkerboard":
        out = []; m = 0
        while m < n:
            p = rng.uniform(-2, 2, (2 * n, 2)); keep = (np.floor(p[:, 0]).astype(int) + np.floor(p[:, 1]).astype(int)) % 2 == 0
            out.append(p[keep]); m += keep.sum()
        return np.concatenate(out)[:n].astype(np.float32)
    raise ValueError(task)

# ---------------- model (shared by every system) ----------------
class MLP(nn.Module):
    def __init__(self, h=128, nf=8):
        super().__init__()
        self.register_buffer("fr", (2.0 ** torch.arange(nf)) * math.pi)
        self.net = nn.Sequential(nn.Linear(2 + 1 + 2 * nf, h), nn.SiLU(), nn.Linear(h, h), nn.SiLU(),
                                 nn.Linear(h, h), nn.SiLU(), nn.Linear(h, h), nn.SiLU(), nn.Linear(h, 2))
    def forward(self, x, t):  # t in [0,1], shape (n,)
        a = t[:, None] * self.fr[None]
        return self.net(torch.cat([x, t[:, None], torch.sin(a), torch.cos(a)], 1))

def fit(model, loss_fn, iters, bs, lr, seed):
    ema = MLP(); ema.load_state_dict(model.state_dict())
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, iters)
    for i in range(iters):
        loss = loss_fn(bs)
        opt.zero_grad(); loss.backward(); opt.step(); sched.step()
        with torch.no_grad():
            d = min(0.999, (1 + i) / (10 + i))
            for pe, pm in zip(ema.parameters(), model.parameters()): pe.mul_(d).add_(pm.detach(), alpha=1 - d)
    return ema.eval()

# ---------------- diffusion ----------------
T = 1000
def alpha_bar(sched):
    if sched == "linear":
        b = np.linspace(1e-4, 0.02, T)
    else:
        s = 0.008; f = lambda u: math.cos((u / T + s) / (1 + s) * math.pi / 2) ** 2
        b = np.array([min(1 - f(i + 1) / f(i), 0.999) for i in range(T)])
    return torch.tensor(np.cumprod(1 - b), dtype=torch.float32)

def train_diffusion(task, seed, sched, a):
    torch.manual_seed(seed); rng = np.random.default_rng(seed); ab = alpha_bar(sched)
    m = MLP()
    def loss(bs):
        x0 = torch.from_numpy(sample_data(task, bs, rng)); t = torch.randint(0, T, (bs,)); e = torch.randn(bs, 2)
        xt = ab[t].sqrt()[:, None] * x0 + (1 - ab[t]).sqrt()[:, None] * e
        return ((m(xt, t.float() / T) - e) ** 2).mean()
    return fit(m, loss, a.iters, a.bs, a.lr, seed)

@torch.no_grad()
def sample_ddim(m, ab, n, K, eta, g, traj=False, tmax=T - 1):
    x = torch.randn(n, 2, generator=g); ts = [int(tmax * (1 - i / K)) for i in range(K)] + [-1]
    path = [x]
    for i in range(K):
        t, tp = ts[i], ts[i + 1]; a = ab[t]; ap = ab[tp] if tp >= 0 else torch.tensor(1.0)
        e = m(x, torch.full((n,), t / T)); x0 = (x - (1 - a).sqrt() * e) / a.sqrt()
        sig = eta * ((1 - ap) / (1 - a)).sqrt() * (1 - a / ap).sqrt()
        x = ap.sqrt() * x0 + (1 - ap - sig ** 2).clamp(min=0).sqrt() * e + sig * torch.randn(n, 2, generator=g)
        path.append(x)
    return path if traj else x

# ---------------- flow matching (noise at t=0, data at t=1) ----------------
def train_fm(task, seed, a, init=None, pool=None):
    torch.manual_seed(seed); rng = np.random.default_rng(seed); m = MLP()
    if init is not None: m.load_state_dict(init.state_dict())
    def loss(bs):
        if pool is None:
            x1 = torch.from_numpy(sample_data(task, bs, rng)); x0 = torch.randn(bs, 2)
        else:
            idx = torch.from_numpy(rng.integers(0, len(pool[0]), bs)); x0, x1 = pool[0][idx], pool[1][idx]
        t = torch.rand(bs); xt = (1 - t)[:, None] * x0 + t[:, None] * x1
        return ((m(xt, t) - (x1 - x0)) ** 2).mean()
    return fit(m, loss, a.iters, a.bs, a.lr, seed)

@torch.no_grad()
def sample_flow(m, n, K, g, heun=False, traj=False, x=None):
    x = torch.randn(n, 2, generator=g) if x is None else x; path = [x]; dt = 1.0 / K
    for i in range(K):
        t = torch.full((n,), i * dt); v = m(x, t)
        if heun:
            v2 = m(x + dt * v, t + dt); v = 0.5 * (v + v2)
        x = x + dt * v; path.append(x)
    return path if traj else x

@torch.no_grad()
def make_pairs(m, task_seed, npairs, steps):
    g = torch.Generator().manual_seed(task_seed + 777)
    z = torch.randn(npairs, 2, generator=g); x = sample_flow(m, npairs, steps, g, x=z.clone())
    return z, x

# ---------------- metrics ----------------
def sliced_w1(x, y, proj):
    px, py = torch.sort(x @ proj, 0).values, torch.sort(y @ proj, 0).values
    return (px - py).abs().mean().item()

def mmd(x, y, bws=(0.1, 0.3, 1.0, 3.0)):
    def k(a, b):
        d = torch.cdist(a, b) ** 2
        return sum(torch.exp(-d / (2 * s * s)) for s in bws) / len(bws)
    return (k(x, x).mean() + k(y, y).mean() - 2 * k(x, y).mean()).item()

def straightness(path):
    p = torch.stack(path); chord = (p[-1] - p[0]).norm(dim=1); arc = (p[1:] - p[:-1]).norm(dim=2).sum(0)
    return (chord / arc.clamp(min=1e-9)).mean().item()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True); ap.add_argument("--task", required=True)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out", required=True)
    ap.add_argument("--sched", default="linear"); ap.add_argument("--rounds", type=int, default=1)
    ap.add_argument("--teacher_steps", type=int, default=100)
    ap.add_argument("--iters", type=int, default=3000); ap.add_argument("--bs", type=int, default=512)
    ap.add_argument("--lr", type=float, default=2e-3); ap.add_argument("--npairs", type=int, default=20000)
    ap.add_argument("--start_ab", type=float, default=0.0)  # DDIM grid starts at the last index with alpha_bar >= start_ab
    ap.add_argument("--nref", type=int, default=10000); ap.add_argument("--nmmd", type=int, default=3000)
    a = ap.parse_args(); print("CONFIG", json.dumps(vars(a)))
    os.makedirs(CKPT, exist_ok=True); t0 = time.time()
    ref = torch.from_numpy(sample_data(a.task, a.nref, np.random.default_rng(12345)))   # held-out reference, fixed
    proj = torch.randn(2, 256, generator=torch.Generator().manual_seed(4242)); proj = proj / proj.norm(dim=0)
    g = torch.Generator().manual_seed(1000 + a.seed)
    def cached(key, fn):
        p = os.path.join(CKPT, f"{key}_{a.task}_s{a.seed}.pt")
        if os.path.exists(p):
            m = MLP(); m.load_state_dict(torch.load(p)); print("loaded", key); return m.eval()
        m = fn(); torch.save(m.state_dict(), p); print("trained", key); return m
    def get_fm(): return cached("fm", lambda: train_fm(a.task, a.seed, a))
    def get_reflow(r, ts):
        if r == 0: return get_fm()
        key = f"reflow{r}_ts{ts}_np{a.npairs}"
        def f():
            teach = get_reflow(r - 1, 100 if r > 1 else ts)
            pool = make_pairs(teach, a.seed + 10 * r, a.npairs, ts if r == 1 else 100)
            return train_fm(a.task, a.seed + 100 * r, a, init=teach, pool=pool)
        return cached(key, f)
    res = {}
    if a.system == "real":
        x = torch.from_numpy(sample_data(a.task, a.nref, np.random.default_rng(999 + a.seed)))
        s, mm = sliced_w1(x, ref, proj), mmd(x[:a.nmmd], ref[:a.nmmd])
        for K in KS: res[f"sw_k{K}"] = s; res[f"mmd_k{K}"] = mm
    else:
        if a.system in ("ddim", "ddpm_anc"):
            ab = alpha_bar(a.sched); m = cached(f"diff_{a.sched}", lambda: train_diffusion(a.task, a.seed, a.sched, a))
            eta = 0.0 if a.system == "ddim" else 1.0
            tmax = int((ab >= a.start_ab).nonzero().max()) if a.start_ab > 0 else T - 1
            print("DDIM start index", tmax, "alpha_bar", ab[tmax].item())
            sampler = lambda K, n, traj=False: sample_ddim(m, ab, n, K, eta, g, traj, tmax)
        else:
            m = get_reflow(a.rounds, a.teacher_steps) if a.system == "reflow" else get_fm()
            sampler = lambda K, n, traj=False: sample_flow(m, n, K, g, heun=(a.system == "fm_heun"), traj=traj)
        for K in KS:
            x = sampler(K, a.nref); assert torch.isfinite(x).all()
            res[f"sw_k{K}"] = sliced_w1(x, ref, proj); res[f"mmd_k{K}"] = mmd(x[:a.nmmd], ref[:a.nmmd])
        if a.system != "ddpm_anc":
            res["straight"] = straightness(sampler(100, 2000, traj=True))
    res["train_plus_eval_s"] = time.time() - t0
    print("METRICS", json.dumps(res)); json.dump(res, open(a.out, "w"))
main()
