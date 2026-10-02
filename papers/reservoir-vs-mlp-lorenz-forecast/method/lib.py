"""Data generation, models and metrics for the chaos-forecasting study (CPU, numpy/torch)."""
import numpy as np, scipy.sparse as sp
import torch, torch.nn as nn
from scipy.stats import wasserstein_distance

torch.set_num_threads(2)

# ---------------------------------------------------------------- systems
LYAP = {"lorenz63": 0.905, "lorenz96": 1.158}   # Benettin estimates logged by method/lyap.py (0.90517, 1.15771; group "lyapunov")
DT = {"lorenz63": 0.02, "lorenz96": 0.05}
DIM = {"lorenz63": 3, "lorenz96": 10}


def f_l63(x, s=10.0, r=28.0, b=8.0 / 3):
    return np.stack([s * (x[..., 1] - x[..., 0]), x[..., 0] * (r - x[..., 2]) - x[..., 1],
                     x[..., 0] * x[..., 1] - b * x[..., 2]], -1)


def f_l96(x, F=8.0):
    return (np.roll(x, -1, -1) - np.roll(x, 2, -1)) * np.roll(x, 1, -1) - x + F


FUN = {"lorenz63": f_l63, "lorenz96": f_l96}


def rk4(f, x, h):
    k1 = f(x); k2 = f(x + .5 * h * k1); k3 = f(x + .5 * h * k2); k4 = f(x + h * k3)
    return x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def integrate(task, x0, n, burn=0, sub=2):
    """Sampled trajectory (n, D) with sampling interval DT[task]; RK4 with `sub` substeps."""
    f, h = FUN[task], DT[task] / sub
    x = np.array(x0, float)
    for _ in range(burn * sub):
        x = rk4(f, x, h)
    out = np.empty((n,) + x.shape)
    for i in range(n):
        for _ in range(sub):
            x = rk4(f, x, h)
        out[i] = x
    return out


CLIM_LEN = 10000   # length (samples) of the free runs scored by the climate metric; chosen on validation seed 100 so that
                   # free runs of the TRUE system pass the clim_ok threshold (at 5000 samples 20% of true Lorenz-63 runs fail it)


def init_state(task, rng):
    if task == "lorenz63":
        return rng.normal(size=3) * 5 + np.array([0, 0, 25.0])
    x = 8.0 + rng.normal(size=10) * 0.5
    return x


def _cached(key, fn):
    import os
    path = f"results/cache/{key}.npy"
    if os.path.exists(path): return np.load(path)
    os.makedirs("results/cache", exist_ok=True); a = fn(); np.save(path, a); return a


def make_data(task, seed, n_train, n_test_ics=20, horizon_lt=15, washout=100, clim_len=CLIM_LEN):
    """Train / test / reference are three independent trajectories started from seed-dependent states
    (deterministic, so they are cached on disk; the cache is just a speed-up)."""
    rng = np.random.default_rng(1000 + seed)
    lam = LYAP[task]; H = int(round(horizon_lt / (lam * DT[task])))
    s0, s1, s2 = init_state(task, rng), init_state(task, rng), init_state(task, rng)
    seg = washout + H
    tr = _cached(f"{task}_{seed}_train{n_train}", lambda: integrate(task, s0, n_train + 1, burn=200))
    te = _cached(f"{task}_{seed}_test{seg}", lambda: integrate(task, s1, 20 * (seg + 50), burn=200))
    ref = _cached(f"{task}_{seed}_ref", lambda: integrate(task, s2, 15000, burn=200))
    mu, sd = tr.mean(0), tr.std(0)
    z = lambda a: (a - mu) / sd
    segs = np.stack([z(te[i * (seg + 50): i * (seg + 50) + seg]) for i in range(n_test_ics)])
    return dict(train=z(tr), test=segs, ref=z(ref), H=H, washout=washout, mu=mu, sd=sd, clim_len=clim_len)


# ---------------------------------------------------------------- models
class ESN:
    """Echo state network, Pathak et al. 2018 style: sparse tanh reservoir + ridge readout, closed-loop rollout."""
    def __init__(self, D, size=500, rho=0.9, sigma=0.5, ridge=1e-6, sq=1, degree=3, seed=0, **kw):
        rng = np.random.default_rng(seed)
        A = sp.random(size, size, density=min(1.0, degree / size), random_state=rng,
                      data_rvs=lambda k: rng.uniform(-1, 1, k)).tocsr()
        ev = np.abs(np.linalg.eigvals(A.toarray())).max()   # dense solver: deterministic for a given seed (no random start vector)
        self.A = A * (rho / ev)
        self.Win = rng.uniform(-sigma, sigma, (size, D)); self.b = rng.uniform(-sigma, sigma, size)
        self.ridge, self.sq, self.N, self.D = ridge, sq, size, D

    def step(self, R, U):  # R (B,N), U (B,D)
        return np.tanh((self.A @ R.T).T + U @ self.Win.T + self.b)

    def phi(self, R):
        if not self.sq: return R
        P = R.copy(); P[..., 0::2] = P[..., 0::2] ** 2
        return P

    def fit(self, X, washout=100):
        U, Y = X[:-1], X[1:]
        R = np.zeros((1, self.N)); S = np.empty((len(U), self.N))
        for t in range(len(U)):
            R = self.step(R, U[t:t + 1]); S[t] = R[0]
        P = self.phi(S)[washout:]
        G = P.T @ P + self.ridge * np.eye(self.N)
        self.Wout = np.linalg.solve(G, P.T @ Y[washout:])
        return self

    def rollout(self, warm, steps):  # warm (B,W,D) -> (B,steps,D); pred[0] is the state one step after warm
        B = warm.shape[0]; R = np.zeros((B, self.N))
        for t in range(warm.shape[1]): R = self.step(R, warm[:, t])
        out = np.empty((B, steps, self.D))
        for k in range(steps):
            y = self.phi(R) @ self.Wout
            y = np.clip(np.nan_to_num(y, nan=1e3, posinf=1e3, neginf=-1e3), -1e3, 1e3)   # same clamp as MLP/GRU, per rollout
            out[:, k] = y; R = self.step(R, y)
        return out


class MLP:
    """One-step MLP on d delay coordinates (x_t..x_{t-d+1}), residual output, trained with input noise."""
    def __init__(self, D, delays=2, hidden=128, layers=3, noise=0.0, steps=4000, lr=2e-3, seed=0, **kw):
        torch.manual_seed(seed); self.d, self.D, self.noise, self.steps, self.lr, self.seed = delays, D, noise, steps, lr, seed
        mods, i = [], delays * D
        for _ in range(layers): mods += [nn.Linear(i, hidden), nn.GELU()]; i = hidden
        mods += [nn.Linear(i, D)]
        self.net = nn.Sequential(*mods)

    def _f(self, Xd):  # Xd (B, d*D) newest first
        return Xd[:, :self.D] + self.scale * self.net(Xd)

    def fit(self, X, washout=0):
        d, D = self.d, self.D
        self.scale = torch.tensor((X[1:] - X[:-1]).std(0), dtype=torch.float32)
        idx = np.arange(d - 1, len(X) - 1)
        inp = np.concatenate([X[idx - j] for j in range(d)], 1); tgt = X[idx + 1]
        inp, tgt = torch.tensor(inp, dtype=torch.float32), torch.tensor(tgt, dtype=torch.float32)
        g = torch.Generator().manual_seed(self.seed)
        opt = torch.optim.Adam(self.net.parameters(), lr=self.lr)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, self.steps)
        bs = min(256, len(inp))
        for s in range(self.steps):
            b = torch.randint(0, len(inp), (bs,), generator=g)
            x = inp[b]; x = x + self.noise * torch.randn(x.shape, generator=g)
            loss = ((self._f(x) - tgt[b]) ** 2).mean()
            opt.zero_grad(); loss.backward(); opt.step(); sched.step()
        return self

    @torch.no_grad()
    def rollout(self, warm, steps):
        hist = torch.tensor(warm[:, -self.d:][:, ::-1].copy(), dtype=torch.float32)  # (B,d,D) newest first
        out = np.empty((warm.shape[0], steps, self.D))
        for k in range(steps):
            y = self._f(hist.reshape(len(hist), -1))
            y = torch.nan_to_num(y, nan=1e3, posinf=1e3, neginf=-1e3).clamp(-1e3, 1e3)
            out[:, k] = y.numpy(); hist = torch.cat([y[:, None], hist[:, :-1]], 1)
        return out


class Truth:
    """The true system integrated from the last warm-up state (same RK4 as the data): gives the sampling floor of the climate metric."""
    def __init__(self, D, **kw): self.task = self.mu = self.sd = None   # set by run.py from the data dict
    def fit(self, X, washout=0): return self
    def rollout(self, warm, steps):
        return (integrate(self.task, warm[:, -1] * self.sd + self.mu, steps).transpose(1, 0, 2) - self.mu) / self.sd


class GRUNet:
    """Small GRU one-step forecaster: x_{t+1} = x_t + s*W h_t, trained with teacher forcing on windows + input noise."""
    def __init__(self, D, hidden=64, noise=0.0, steps=3000, lr=3e-3, win=48, seed=0, cell="gru", **kw):
        torch.manual_seed(seed); self.D, self.noise, self.steps, self.lr, self.win, self.seed = D, noise, steps, lr, win, seed
        self.rnn = (nn.GRU if cell == "gru" else nn.LSTM)(D, hidden, batch_first=True); self.head = nn.Linear(hidden, D)

    def fit(self, X, washout=0):
        self.scale = torch.tensor((X[1:] - X[:-1]).std(0), dtype=torch.float32)
        Xt = torch.tensor(X, dtype=torch.float32); n = len(Xt) - 1; W = min(self.win, n)
        g = torch.Generator().manual_seed(self.seed)
        params = list(self.rnn.parameters()) + list(self.head.parameters())
        opt = torch.optim.Adam(params, lr=self.lr); sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, self.steps)
        bs = 32; ar = torch.arange(W)
        for s in range(self.steps):
            st = torch.randint(0, n - W + 1, (bs,), generator=g)
            ix = st[:, None] + ar[None]
            x = Xt[ix]; y = Xt[ix + 1]
            xn = x + self.noise * torch.randn(x.shape, generator=g)
            h, _ = self.rnn(xn)
            pred = xn + self.scale * self.head(h)
            loss = ((pred[:, 20:] - y[:, 20:]) ** 2).mean()   # first 20 steps are state spin-up, not scored
            opt.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(params, 1.0); opt.step(); sched.step()
        return self

    @torch.no_grad()
    def rollout(self, warm, steps):
        x = torch.tensor(warm, dtype=torch.float32)
        h, st = self.rnn(x); y = x[:, -1] + self.scale * self.head(h[:, -1])
        out = np.empty((warm.shape[0], steps, warm.shape[2]))
        for k in range(steps):
            y = torch.nan_to_num(y, nan=1e3, posinf=1e3, neginf=-1e3).clamp(-1e3, 1e3)
            out[:, k] = y.numpy()
            h, st = self.rnn(y[:, None], st); y = y + self.scale * self.head(h[:, 0])
        return out


def build(system, D, seed, **cfg):
    if system == "esn": return ESN(D, seed=seed, **cfg)
    if system == "mlp": return MLP(D, seed=seed, **cfg)
    if system == "gru": return GRUNet(D, seed=seed, cell="gru", **cfg)
    if system == "truth": return Truth(D, **cfg)
    if system == "lstm": return GRUNet(D, seed=seed, cell="lstm", **cfg)
    raise ValueError(system)


# ---------------------------------------------------------------- metrics
OK_THR = 0.1   # clim_ok threshold on the capped W1 distance


def valid_time(model, data, task, thr=0.4, n=None):
    """Valid prediction time in Lyapunov times: first step where ||err||/sqrt(D) > thr (standardised units), capped at horizon."""
    S = data["test"][:n] if n else data["test"]; W, H = data["washout"], data["H"]
    pred = model.rollout(S[:, :W], H)
    err = np.linalg.norm(pred - S[:, W:W + H], axis=-1) / np.sqrt(S.shape[-1])
    bad = (err > thr) | ~np.isfinite(err)
    first = np.where(bad.any(1), bad.argmax(1), H)
    return first * DT[task] * LYAP[task]


def climate(model, data, task, n_roll=20, cap=1.0, ok_thr=OK_THR):
    """Free-run n_roll long rollouts (one per test initial condition); per-component W1 to the reference sample divided by the
    reference std, averaged over components, capped at `cap`. A rollout that is non-finite or leaves the box of 3x the largest
    reference magnitude counts as escaped (`blowup`) and gets distance `cap`."""
    S, W, T = data["test"][:n_roll], data["washout"], data["clim_len"]
    pred = model.rollout(S[:, :W], T)
    ref = data["ref"]; lim = 3 * np.abs(ref).max()
    w1s, blow = [], []
    for p in pred:
        fin = np.all(np.isfinite(p)) and np.abs(p).max() < lim
        blow.append(not fin)
        if not fin: w1s.append(cap); continue
        w = np.mean([wasserstein_distance(p[:, j], ref[:, j]) / ref[:, j].std() for j in range(p.shape[1])])
        w1s.append(min(w, cap))
    w1s = np.array(w1s)
    return dict(clim_w1=float(w1s.mean()), clim_w1_max=float(w1s.max()), clim_ok=float((w1s < ok_thr).mean()), blowup=float(np.mean(blow)))
