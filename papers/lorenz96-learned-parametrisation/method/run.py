"""Entry point: python method/run.py --system {noclosure,poly,mlp,ar1,truth} --task F20_c10 --seed 0 --out metrics.json

Trains (offline, on truth U_k vs local slow state) a closure for the slow-only Lorenz-96 model, then evaluates
(i) offline R2, (ii) ensemble forecasts from truth initial conditions, (iii) long free rollouts: stability + climate.
"""
import argparse, json, os, sys, time
os.environ.setdefault("OMP_NUM_THREADS", "2"); os.environ.setdefault("MKL_NUM_THREADS", "2")
import numpy as np
from scipy.stats import wasserstein_distance
sys.path.insert(0, os.path.dirname(__file__))
import l96
from l96 import K

TASKS = {"F20_c10": dict(F=20.0, c=10.0), "F20_c4": dict(F=20.0, c=4.0)}
DATA = os.path.join(os.path.dirname(__file__), "..", "data")
BLOW = 60.0           # |X| above this (or non-finite) = diverged chain


def cached(name, fn):
    os.makedirs(DATA, exist_ok=True)
    p = os.path.join(DATA, name + ".npz")
    if os.path.exists(p):
        d = np.load(p); return d["X"], d["U"]
    X, U = fn(); tmp = p + f".{os.getpid()}.npz"; np.savez(tmp, X=X, U=U); os.replace(tmp, p); return X, U


def stencil(X, s):
    """Features for sector k: (X_{k-s},...,X_{k+s}); X (...,K) -> (...,K,2s+1)."""
    return np.stack([np.roll(X, -o, -1) for o in range(-s, s + 1)], -1)


# ---------------- closures: callables X(...,K) -> U(...,K) -----------------
class Poly:
    def __init__(s, deg): s.deg = deg
    def fit(s, X, U):
        x = X.reshape(-1); s.mu, s.sd = x.mean(), x.std()
        s.w = np.linalg.lstsq(np.vander((x - s.mu) / s.sd, s.deg + 1), U.reshape(-1), rcond=None)[0]
        return s
    def __call__(s, X): return np.polyval(s.w, (X - s.mu) / s.sd)


class MLP:
    def __init__(s, st, hidden, epochs, seed): s.st, s.hidden, s.epochs, s.seed = st, hidden, epochs, seed
    def fit(s, X, U, Xv, Uv):
        import torch; torch.set_num_threads(2); torch.manual_seed(s.seed)
        f = stencil(X, s.st).reshape(-1, 2 * s.st + 1); y = U.reshape(-1, 1)
        s.mu, s.sd = f.mean(), f.std(); s.ym, s.ys = y.mean(), y.std()
        T = lambda a: torch.tensor(a, dtype=torch.float32)
        xt, yt = T((f - s.mu) / s.sd), T((y - s.ym) / s.ys)
        fv = stencil(Xv, s.st).reshape(-1, 2 * s.st + 1); xv, yv = T((fv - s.mu) / s.sd), T((Uv.reshape(-1, 1) - s.ym) / s.ys)
        h = s.hidden
        s.net = torch.nn.Sequential(torch.nn.Linear(2 * s.st + 1, h), torch.nn.Tanh(), torch.nn.Linear(h, h), torch.nn.Tanh(), torch.nn.Linear(h, 1))
        opt = torch.optim.Adam(s.net.parameters(), 3e-3)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, s.epochs)
        g = torch.Generator().manual_seed(s.seed); best, bs = 1e9, None
        for ep in range(s.epochs):
            perm = torch.randperm(len(xt), generator=g)
            for i in range(0, len(xt), 1024):
                idx = perm[i:i + 1024]; opt.zero_grad()
                torch.nn.functional.mse_loss(s.net(xt[idx]), yt[idx]).backward(); opt.step()
            sched.step()
            with torch.no_grad(): v = torch.nn.functional.mse_loss(s.net(xv), yv).item()
            if v < best: best, bs = v, {k: t.clone() for k, t in s.net.state_dict().items()}
        s.net.load_state_dict(bs); s.torch = torch
        # export weights to numpy for fast batched rollouts
        s.W = [(m.weight.detach().numpy().astype(np.float64), m.bias.detach().numpy().astype(np.float64)) for m in s.net if hasattr(m, "weight")]
        return s
    def __call__(s, X):
        a = (stencil(X, s.st) - s.mu) / s.sd
        a = np.tanh(a @ s.W[0][0].T + s.W[0][1]); a = np.tanh(a @ s.W[1][0].T + s.W[1][1])
        return ((a @ s.W[2][0].T + s.W[2][1])[..., 0]) * s.ys + s.ym


# ---------------- rollouts -----------------
class Noise:
    """AR(1) red noise per sector: e' = phi e + sigma sqrt(1-phi^2) xi (stationary std sigma); none if sigma==0."""
    def __init__(s, phi, sigma, rng): s.phi, s.sigma, s.rng = phi, sigma, rng
    def init(s, shape): return s.sigma * s.rng.normal(size=shape)
    def step(s, e):
        return s.phi * e + s.sigma * np.sqrt(1 - s.phi ** 2) * s.rng.normal(size=e.shape)


def rollout(X0, closure, noise, F, n_steps, every, blow=None):
    """X0 (M,K). Returns samples (n_steps//every, M, K) (nan after divergence) and alive mask (M,)."""
    X = X0.copy(); e = noise.init(X.shape) if noise else np.zeros_like(X)
    out = np.full((n_steps // every,) + X.shape, np.nan); alive = np.ones(len(X), bool)
    for n in range(n_steps):
        if n % every == 0: out[n // every][alive] = X[alive]
        with np.errstate(all="ignore"):
            X = l96.rk4_slow(X, e, closure, F)
        if noise: e = noise.step(e)
        bad = ~np.isfinite(X).all(-1) | (np.abs(np.nan_to_num(X, nan=1e9)).max(-1) > BLOW)
        alive &= ~bad; X[~alive] = 0.0
    return out, alive


def spectrum(S):
    S = S[np.isfinite(S).all(-1)]
    return (np.abs(np.fft.rfft(S, axis=-1)) ** 2).mean(0)  # (K//2+1,)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True, choices=["noclosure", "poly", "mlp", "ar1", "truth"])
    ap.add_argument("--task", default="F20_c10"); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--deg", type=int, default=4)            # polynomial degree (poly, ar1)
    ap.add_argument("--stencil", type=int, default=0)        # MLP half-width (0 = local X_k only)
    ap.add_argument("--hidden", type=int, default=32); ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--sigma_scale", type=float, default=1.0)  # multiplies the fitted AR(1) std
    ap.add_argument("--phi", type=float, default=-1.0)       # <0: fitted lag-1 autocorrelation
    ap.add_argument("--F_test", type=float, default=None)    # forcing used for test/reference/slow model (shift study)
    ap.add_argument("--members", type=int, default=10)
    a = ap.parse_args(); t0 = time.time()
    print("config", json.dumps(vars(a)), flush=True)
    cfg = TASKS[a.task]; F_tr, c = cfg["F"], cfg["c"]; F_te = a.F_test or F_tr
    tag = lambda k, F: f"{k}_F{F:g}_c{c:g}"
    # ---- data (seed-specific train/val/test; one fixed long reference run per regime) ----
    Xtr, Utr = cached(tag(f"train_s{a.seed}", F_tr), lambda: l96.simulate_truth(100 + a.seed, 16, 20, 25, F_tr, c))
    Xva, Uva = cached(tag(f"val_s{a.seed}", F_tr), lambda: l96.simulate_truth(200 + a.seed, 4, 20, 25, F_tr, c))
    Xte, Ute = cached(tag(f"test_s{a.seed}", F_te), lambda: l96.simulate_truth(300 + a.seed, 10, 20, 30, F_te, c))
    Xref, _ = cached(tag("ref", F_te), lambda: l96.simulate_truth(9999, 40, 20, 100, F_te, c))
    if a.system == "truth":   # noise floor: an independent truth run scored against the reference
        Xsmp, _ = cached(tag(f"indep_s{a.seed}", F_te), lambda: l96.simulate_truth(5000 + a.seed, 40, 20, 100, F_te, c))
        samples = Xsmp[::10]
    thin = 4
    Xt, Ut = Xtr[::thin], Utr[::thin]
    m = {}
    # ---- fit ----
    rng = np.random.default_rng(1000 + a.seed); closure = None; noise = None
    if a.system == "noclosure": closure = lambda X: np.zeros_like(X)
    if a.system in ("poly", "ar1"):
        closure = Poly(a.deg).fit(Xt, Ut)
    if a.system == "mlp":
        closure = MLP(a.stencil, a.hidden, a.epochs, a.seed).fit(Xt, Ut, Xva[::thin], Uva[::thin])
    if a.system == "ar1":
        r = Utr - closure(Xtr)           # residual at the sampling interval
        phi = float(np.mean(r[1:] * r[:-1]) / np.mean(r * r)) if a.phi < 0 else a.phi
        sigma = float(r.std()) * a.sigma_scale
        noise = Noise(phi, sigma, rng); m.update(ar1_phi=phi, ar1_sigma=sigma)
    # ---- offline skill on held-out test chains (training regime data if shifted: use val chains) ----
    if closure is not None and a.system != "noclosure":
        Xo, Uo = (Xte, Ute) if F_te == F_tr else (Xva, Uva)
        res = ((Uo - closure(Xo)) ** 2).sum(); tot = ((Uo - Uo.mean()) ** 2).sum()
        m["offline_r2"] = float(1 - res / tot)
    elif a.system == "noclosure":
        m["offline_r2"] = 0.0
    if a.system != "truth":
        # ---- short-term forecasts: ICs every 3 time units on the 10 test chains, 2 time units long ----
        lead_n = int(round(2.0 / l96.DT_SAMPLE)); ic_idx = np.arange(0, len(Xte) - lead_n - 1, int(round(3.0 / l96.DT_SAMPLE)))
        X0 = Xte[ic_idx].reshape(-1, K)                                  # (n_ic*10, K)
        truth = np.stack([Xte[ic_idx + n] for n in range(0, lead_n + 1)]).reshape(lead_n + 1, -1, K)
        Xe = np.repeat(X0[None], a.members, 0).reshape(-1, K)            # members x ICs
        noise_f = Noise(noise.phi, noise.sigma, np.random.default_rng(5000 + a.seed)) if noise else None
        fc, _ = rollout(Xe, closure, noise_f, F_te, lead_n + 1, 1)     # fc[n] = state after n steps
        fc = fc.reshape(lead_n + 1, a.members, -1, K)
        ens = np.nanmean(fc, 1)                                           # ensemble mean (lead, IC, K)
        sd = Xref.std()
        err = np.sqrt(np.nanmean((ens - truth) ** 2, axis=(1, 2))) / sd   # normalised RMSE vs lead
        mem = np.sqrt(np.nanmean((fc[:, 0] - truth) ** 2, axis=(1, 2))) / sd
        leads = np.arange(lead_n + 1) * l96.DT_SAMPLE
        i05 = int(round(0.5 / l96.DT_SAMPLE))
        m["rmse_0p5"] = float(err[i05]); m["rmse_member_0p5"] = float(mem[i05])
        # valid time: per-IC first lead where normalised ensemble-mean error over sectors exceeds 0.5
        pe = np.sqrt(np.nanmean((ens - truth) ** 2, axis=2)) / sd         # (lead, IC)
        thr = pe > 0.5; first = np.where(thr.any(0), leads[thr.argmax(0)], leads[-1])
        m["valid_time"] = float(first.mean())
        # ---- long free rollouts ----
        M, T = 20, 400.0; n_steps = int(T / l96.DT_SAMPLE); every = 10
        x0 = Xref[rng.integers(0, len(Xref), M), rng.integers(0, Xref.shape[1], M)]
        noise_r = Noise(noise.phi, noise.sigma, np.random.default_rng(7000 + a.seed)) if noise else None
        S, alive = rollout(x0, closure, noise_r, F_te, n_steps, every)
        S = S[int(10.0 / (every * l96.DT_SAMPLE)):]                        # drop 10 time units of spin-up
        m["stable_frac"] = float(alive.mean())
        ok = np.isfinite(S).all(-1)
        samples = S[ok] if ok.any() else None
        m["n_valid_samples"] = int(ok.sum())
    # ---- climate vs reference (pooled over sectors, which are statistically equivalent) ----
    if samples is not None and len(samples):
        ref = Xref[::10].reshape(-1, K); smp = samples.reshape(-1, K)
        m["mean_err"] = float(abs(smp.mean() - ref.mean()))
        m["var_err"] = float(abs(smp.var() / ref.var() - 1)); m["var_ratio"] = float(smp.var() / ref.var())
        m["w1_pdf"] = float(wasserstein_distance(smp.reshape(-1)[::7], ref.reshape(-1)[::7]))
        ps, pr = spectrum(smp), spectrum(ref)
        m["spec_err"] = float(np.sqrt(np.mean((np.log10(ps[1:]) - np.log10(pr[1:])) ** 2)))
        # temporal decorrelation: lag-1 (0.05 t.u.) autocorrelation not scored; keep spectrum log-ratio per wavenumber
        for k in range(1, 5): m[f"logspec_k{k}"] = float(np.log10(ps[k] / pr[k]))
    m["runtime_s"] = time.time() - t0
    json.dump(m, open(a.out, "w")); print("metrics", json.dumps(m), flush=True)


if __name__ == "__main__":
    main()
