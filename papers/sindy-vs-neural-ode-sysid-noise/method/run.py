"""Sysid under measurement noise: SINDy-STLSQ vs MLP neural ODE vs DMDc, with LQR / MPC on the identified model.
Usage: python method/run.py --system sindy|node|dmdc|oracle --task pendulum|vdp --seed S --noise 0.05 --ntrain 1000 --out f.json
"""
import argparse, json, os, sys, time
import numpy as np
from scipy.linalg import expm, solve_discrete_are
from scipy.signal import savgol_filter

os.environ.setdefault("OMP_NUM_THREADS", "2")
DT = 0.05
L = 40          # steps per training / test trajectory
HOLD = 5        # input hold (steps)

# ---------------- true systems (state x=[x1,x2], scalar input u) ----------------
def f_pend(x, u):   # angle from the upright position; unstable equilibrium at 0
    return np.stack([x[..., 1], 9.81 * np.sin(x[..., 0]) - 0.5 * x[..., 1] + u], -1)
def f_vdp(x, u):
    return np.stack([x[..., 1], 1.0 * (1 - x[..., 0] ** 2) * x[..., 1] - x[..., 0] + u], -1)
SYS = {
    "pendulum": dict(f=f_pend, ic=1.0, umax=5.0, ucl=10.0, Q=np.diag([10., 1.]), R=0.1, cl_ic=0.5),
    "vdp": dict(f=f_vdp, ic=1.5, umax=3.0, ucl=10.0, Q=np.diag([1., 1.]), R=0.1, cl_ic=1.0),
}
JCAP = 1000.0

def rk4(f, x, u, dt=DT):
    k1 = f(x, u); k2 = f(x + dt / 2 * k1, u); k3 = f(x + dt / 2 * k2, u); k4 = f(x + dt * k3, u)
    return x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

def gen_data(sysd, ntraj, rng):
    x = rng.uniform(-sysd["ic"], sysd["ic"], (ntraj, 2))
    nblk = L // HOLD
    U = np.repeat(rng.uniform(-sysd["umax"], sysd["umax"], (ntraj, nblk)), HOLD, 1)
    X = np.zeros((ntraj, L + 1, 2)); X[:, 0] = x
    for k in range(L):
        X[:, k + 1] = rk4(sysd["f"], X[:, k], U[:, k])
    return X, U

# ---------------- models: all expose f(x,u) continuous-time (batched numpy) ----------------
def library(x, u, trig):
    x1, x2 = x[..., 0], x[..., 1]
    cols = [np.ones_like(x1), x1, x2, x1**2, x1*x2, x2**2, x1**3, x1**2*x2, x1*x2**2, x2**3]
    names = ["1", "x1", "x2", "x1^2", "x1x2", "x2^2", "x1^3", "x1^2x2", "x1x2^2", "x2^3"]
    if trig:
        cols += [np.sin(x1), np.cos(x1)]; names += ["sin x1", "cos x1"]
    cols.append(u); names.append("u")
    return np.stack(cols, -1), names

def stlsq(Th, dX, lam, iters=10):
    Xi = np.linalg.lstsq(Th, dX, rcond=None)[0]
    for _ in range(iters):
        small = np.abs(Xi) < lam
        Xi[small] = 0
        for j in range(dX.shape[1]):
            big = ~small[:, j]
            if big.any():
                Xi[big, j] = np.linalg.lstsq(Th[:, big], dX[:, j], rcond=None)[0]
    return Xi

def true_support(task, trig):
    _, names = library(np.zeros(2), 0.0, trig)
    ix = {n: i for i, n in enumerate(names)}
    S = np.zeros((len(names), 2), bool)
    S[ix["x2"], 0] = True
    if task == "pendulum":
        if trig: S[ix["sin x1"], 1] = True
        S[ix["x2"], 1] = True; S[ix["u"], 1] = True
        # without trig library the sin term has no exact representation: support is ill defined
    else:
        S[ix["x2"], 1] = True; S[ix["x1"], 1] = True; S[ix["x1^2x2"], 1] = True; S[ix["u"], 1] = True
    return S

def fit_sindy(Xn, U, task, lam, trig, smooth):
    Xs = Xn
    if smooth:
        Xs = savgol_filter(Xn, 9, 3, axis=1)
    dX = (Xs[:, 2:] - Xs[:, :-2]) / (2 * DT)       # central difference
    # the central difference at step k spans inputs u[k-1] and u[k]: regress on their average
    x = Xs[:, 1:-1].reshape(-1, 2); u = (0.5 * (U[:, 0:L - 1] + U[:, 1:L])).reshape(-1); dX = dX.reshape(-1, 2)
    Th, _ = library(x, u, trig)
    # column-normalise so that the threshold acts on comparable scales
    sc = np.linalg.norm(Th, axis=0) / np.sqrt(len(Th)); sc[sc == 0] = 1
    Xi = stlsq(Th / sc, dX, lam) / sc[:, None]
    f = lambda x, u: library(x, u, trig)[0] @ Xi
    info = {}
    if not (task == "pendulum" and not trig):
        S = true_support(task, trig); P = Xi != 0
        tp = (S & P).sum(); info["support_f1"] = float(2 * tp / (S.sum() + P.sum()))
    info["n_terms"] = float((Xi != 0).sum())
    return f, None, info

def fit_dmdc(Xn, U):
    X0 = Xn[:, :-1].reshape(-1, 2); X1 = Xn[:, 1:].reshape(-1, 2); u = U.reshape(-1, 1)
    Z = np.hstack([X0, u]); W = np.linalg.lstsq(Z, X1, rcond=None)[0].T
    A, B = W[:, :2], W[:, 2:]
    Ad_fun = lambda x, u: x @ A.T + u[..., None] * B[:, 0]
    return None, (A, B, Ad_fun), {}

def fit_node(Xn, U, seed, width=64, steps=2500):
    import torch
    torch.set_num_threads(2); torch.manual_seed(seed)
    X0 = Xn[:, :-1].reshape(-1, 2); X1 = Xn[:, 1:].reshape(-1, 2); u = U.reshape(-1, 1)
    mu, sd = X0.mean(0), X0.std(0) + 1e-8; usd = float(np.abs(u).max()) + 1e-8
    xin = torch.tensor(np.hstack([(X0 - mu) / sd, u / usd]), dtype=torch.float32)
    X0t = torch.tensor(X0, dtype=torch.float32); X1t = torch.tensor(X1, dtype=torch.float32); ut = torch.tensor(u, dtype=torch.float32)
    n = len(X0); rg = np.random.RandomState(seed); perm = rg.permutation(n); nv = max(n // 7, 20)
    va, tr = perm[:nv], perm[nv:]
    net = torch.nn.Sequential(torch.nn.Linear(3, width), torch.nn.Tanh(), torch.nn.Linear(width, width), torch.nn.Tanh(), torch.nn.Linear(width, 2))
    musd = (torch.tensor(mu, dtype=torch.float32), torch.tensor(sd, dtype=torch.float32))
    def fnet(x, uu):
        return net(torch.cat([(x - musd[0]) / musd[1], uu / usd], -1))
    def step(x, uu):
        k1 = fnet(x, uu); k2 = fnet(x + DT / 2 * k1, uu); k3 = fnet(x + DT / 2 * k2, uu); k4 = fnet(x + DT * k3, uu)
        return x + DT / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    opt = torch.optim.Adam(net.parameters(), lr=3e-3, weight_decay=1e-5)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps)
    best, bstate = 1e18, None
    bs = min(128, len(tr))
    # fixed budget of gradient steps (independent of the data size); validation every `ev` steps
    ev = 25; order = rg.permutation(tr); pos = 0
    for it in range(steps):
        if pos + bs > len(order):
            order = rg.permutation(tr); pos = 0
        b = order[pos:pos + bs]; pos += bs
        loss = ((step(X0t[b], ut[b]) - X1t[b]) ** 2).mean()
        opt.zero_grad(); loss.backward(); opt.step(); sched.step()
        if (it + 1) % ev == 0:
            with torch.no_grad():
                v = ((step(X0t[va], ut[va]) - X1t[va]) ** 2).mean().item()
            if v < best:
                best, bstate = v, {k: t.clone() for k, t in net.state_dict().items()}
    net.load_state_dict(bstate)
    W = [(m.weight.detach().double().numpy(), m.bias.detach().double().numpy()) for m in net if isinstance(m, torch.nn.Linear)]
    mu_, sd_ = mu, sd
    def f(x, u):
        h = np.concatenate([(x - mu_) / sd_, (np.asarray(u)[..., None]) / usd], -1)
        h = np.tanh(h @ W[0][0].T + W[0][1]); h = np.tanh(h @ W[1][0].T + W[1][1])
        return h @ W[2][0].T + W[2][1]
    return f, None, {"val_mse": best}

# ---------------- control ----------------
def linearise(f):
    eps = 1e-4; z = np.zeros(2)
    A = np.stack([(f(z + eps * e, 0.0) - f(z - eps * e, 0.0)) / (2 * eps) for e in np.eye(2)], 1)
    B = ((f(z, eps) - f(z, -eps)) / (2 * eps))[:, None]
    M = np.zeros((3, 3)); M[:2, :2] = A; M[:2, 2:] = B
    E = expm(M * DT)
    return E[:2, :2], E[:2, 2:]

def lqr(Ad, Bd, Q, R):
    try:
        P = solve_discrete_are(Ad, Bd, Q, np.array([[R]]))
        K = np.linalg.solve(Bd.T @ P @ Bd + R, Bd.T @ P @ Ad)
        if not np.all(np.isfinite(K)): raise ValueError
        return K, P
    except Exception:
        return None, 10 * Q

def episode_cost(sysd, policy, x0, T):
    x = x0.copy(); J = 0.0; Q, R = sysd["Q"], sysd["R"]; ucl = sysd["ucl"]
    for k in range(T):
        u = float(np.clip(policy(x), -ucl, ucl))
        J += (x @ Q @ x + R * u * u) * DT
        x = rk4(sysd["f"], x, u)
        if not np.all(np.isfinite(x)) or np.abs(x).max() > 50:
            return JCAP, True
    xf = np.linalg.norm(x)
    return min(J, JCAP), bool(xf > 0.5)

def mpc_policy(sysd, step_fn, P, rng, H=12, ns=48, iters=2, nel=8):
    Q, R, ucl = sysd["Q"], sysd["R"], sysd["ucl"]
    st = {"mu": np.zeros(H), "sd": np.full(H, ucl / 2)}
    def pol(x):
        mu = np.concatenate([st["mu"][1:], [0.0]]); sd = np.full(H, ucl / 2)
        for _ in range(iters):
            U = np.clip(mu + sd * rng.standard_normal((ns, H)), -ucl, ucl)
            xs = np.tile(x, (ns, 1)); c = np.zeros(ns)
            for h in range(H):
                c += (np.einsum("ni,ij,nj->n", xs, Q, xs) + R * U[:, h] ** 2) * DT
                xs = step_fn(xs, U[:, h]); xs = np.clip(xs, -1e3, 1e3)
            c += np.einsum("ni,ij,nj->n", xs, P, xs) * DT
            c = np.nan_to_num(c, nan=1e12)
            el = U[np.argsort(c)[:nel]]
            mu, sd = el.mean(0), el.std(0) + 0.05
        st["mu"] = mu
        return mu[0]
    return pol

# ---------------- evaluation ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True); ap.add_argument("--task", required=True)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--noise", type=float, default=0.05)
    ap.add_argument("--ntrain", type=int, default=1000); ap.add_argument("--lam", type=float, default=0.05)
    ap.add_argument("--trig", type=int, default=1); ap.add_argument("--smooth", type=int, default=0)
    ap.add_argument("--width", type=int, default=64); ap.add_argument("--mpc", type=int, default=1)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time(); sysd = SYS[a.task]
    rng = np.random.RandomState(1000 * a.seed + 7)
    X, U = gen_data(sysd, a.ntrain // L, rng)
    sig = X.reshape(-1, 2).std(0)
    Xn = X + a.noise * sig * rng.standard_normal(X.shape)       # measurement noise on the states only
    info = {}
    if a.system == "oracle":
        f = lambda x, u: sysd["f"](x, np.asarray(u)); Ad, Bd = linearise(f); stepfn = lambda x, u: rk4(sysd["f"], x, u)
    elif a.system == "dmdc":
        _, (Ad, Bd, dstep), info = fit_dmdc(Xn, U); stepfn = dstep
    else:
        if a.system == "sindy": f, _, info = fit_sindy(Xn, U, a.task, a.lam, bool(a.trig), bool(a.smooth))
        else: f, _, info = fit_node(Xn, U, a.seed, a.width)
        Ad, Bd = linearise(f); stepfn = lambda x, u: rk4(f, x, u)
    # multi-step prediction on 20 clean held-out trajectories (open loop, true IC)
    trg = np.random.RandomState(99991 + a.seed)
    Xt, Ut = gen_data(sysd, 20, trg)
    xs = Xt[:, 0].copy(); pred = [xs]
    with np.errstate(all="ignore"):
        for k in range(L):
            xs = np.clip(np.nan_to_num(stepfn(xs, Ut[:, k]), nan=50.0), -50, 50); pred.append(xs)
    pred = np.stack(pred, 1)
    tsd = Xt.reshape(-1, 2).std(0)
    err = (pred - Xt) / tsd
    out = {"pred_nrmse": float(np.sqrt((err ** 2).mean())),
           "pred_nrmse_h5": float(np.sqrt((err[:, 5] ** 2).mean()))}
    out.update({k: float(v) for k, v in info.items()})
    # closed loop
    K, P = lqr(Ad, Bd, sysd["Q"], sysd["R"])
    crng = np.random.RandomState(555 + a.seed)
    ics = crng.uniform(-sysd["cl_ic"], sysd["cl_ic"], (10, 2))
    if K is None:
        out["lqr_cost"], out["lqr_fail"] = JCAP, 1.0
    else:
        r = [episode_cost(sysd, lambda x: -(K @ x)[0], x0, 80) for x0 in ics]
        out["lqr_cost"] = float(np.mean([c for c, _ in r])); out["lqr_fail"] = float(np.mean([f_ for _, f_ in r]))
    if a.mpc:
        mrng = np.random.RandomState(31 + a.seed)
        r = []
        for x0 in ics[:6]:
            pol = mpc_policy(sysd, stepfn, P, mrng)
            r.append(episode_cost(sysd, pol, x0, 60))
        out["mpc_cost"] = float(np.mean([c for c, _ in r])); out["mpc_fail"] = float(np.mean([f_ for _, f_ in r]))
    out["seconds"] = time.time() - t0
    json.dump(out, open(a.out, "w"))
    print(out)

if __name__ == "__main__":
    main()
