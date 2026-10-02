"""Entrypoint: python method/run.py --system {cnn,linear,persistence,climatology} --task l96 --seed S --out FILE
Writes a flat JSON of metrics. All randomness derives from --seed."""
import argparse, json, os, sys, time
import numpy as np
os.environ.setdefault("OMP_NUM_THREADS", "2")
import torch
import torch.nn as nn
sys.path.insert(0, os.path.dirname(__file__))
import l96

torch.set_num_threads(2)
LEADS = {"t05": 10, "t10": 20, "t20": 40, "t30": 60, "t50": 100}   # steps of 0.05 time units
MAXLEAD = 100
BLOWUP = 50.0   # |x| above this (truth max is ~13) counts as divergence


def get_data(seed):
    """Independent train / val / test trajectories per seed (cached in /tmp, regenerated if missing)."""
    path = f"/tmp/l96_data_seed{seed}.npz"
    if os.path.exists(path):
        d = np.load(path)
        return d["tr"], d["va"], d["te"]
    tr = l96.simulate(32, 1250, 1000 + 3 * seed)
    va = l96.simulate(8, 500, 1001 + 3 * seed)
    te = l96.simulate(32, 1500, 1002 + 3 * seed)
    np.savez(path, tr=tr, va=va, te=te)
    return tr, va, te


class CNN(nn.Module):
    def __init__(self, width=48, layers=4, ks=5, residual=True):
        super().__init__()
        ch = [1] + [width] * (layers - 1) + [1]
        self.convs = nn.ModuleList(
            nn.Conv1d(ch[i], ch[i + 1], ks, padding=ks // 2, padding_mode="circular") for i in range(layers))
        self.residual = residual

    def forward(self, x):  # x: (B,K) normalised
        h = x[:, None]
        for i, c in enumerate(self.convs):
            h = c(h)
            if i < len(self.convs) - 1:
                h = torch.nn.functional.gelu(h)
        h = h[:, 0]
        return x + h if self.residual else h


def windows(traj, stride, L):
    """Start indices (traj, t) of length-L windows."""
    N, T, _ = traj.shape
    return [(i, t) for i in range(N) for t in range(0, T - L, stride)]


def forecast_metrics(step_fn, traj, mu, sd, stride, prefix=""):
    """Roll step_fn (numpy (B,K)->(B,K)) for MAXLEAD steps from test inits; RMSE and ACC vs lead."""
    idx = windows(traj, stride, MAXLEAD + 1)
    x0 = np.stack([traj[i, t] for i, t in idx])
    truth = np.stack([traj[i, t:t + MAXLEAD + 1] for i, t in idx])   # (W,L+1,K)
    pred = [x0]
    x = x0
    for _ in range(MAXLEAD):
        x = step_fn(x)
        pred.append(x)
    pred = np.stack(pred, 1)
    rmse = np.sqrt(((pred - truth) ** 2).mean((0, 2)))                # (L+1,)
    pa, ta = pred - mu, truth - mu
    num = (pa * ta).sum(2)
    den = np.sqrt((pa ** 2).sum(2) * (ta ** 2).sum(2))
    acc = np.where(den > 0, num / np.maximum(den, 1e-12), 0.0).mean(0)  # ACC := 0 for a zero-anomaly forecast
    out = {f"{prefix}rmse_{k}": float(rmse[v]) for k, v in LEADS.items()}
    out[f"{prefix}rmse_1step"] = float(rmse[1])
    if not prefix:
        out.update({f"acc_{k}": float(acc[v]) for k, v in LEADS.items()})
        # lead time (time units) at which mean ACC first drops below 0.6, linear interpolation
        below = np.where(acc < 0.6)[0]
        if len(below) == 0:
            lt = MAXLEAD * l96.DT_OBS
        else:
            j = below[0]
            lt = (j - 1 + (acc[j - 1] - 0.6) / (acc[j - 1] - acc[j])) * l96.DT_OBS if j > 0 else 0.0
        out["acc_leadtime"] = float(lt)
    return out, rmse, acc


def long_run(step_fn, te, steps=4000, n=16):
    x = te[:n, 0].copy()
    traj = np.empty((steps, n, te.shape[2]))
    alive = np.ones(n, bool)
    surv = np.full(n, steps)
    with np.errstate(all="ignore"):
        for s in range(steps):
            x = step_fn(x)
            bad = ~np.isfinite(x).all(1) | (np.abs(x) > BLOWUP).any(1)
            newly = alive & bad
            surv[newly] = s
            alive &= ~bad
            x = np.where(alive[:, None], x, 0.0)   # park dead members, they are excluded below
            traj[s] = x
    out = {"stable_frac": float(alive.mean()), "survival_time": float(surv.mean() * l96.DT_OBS)}
    tr_all = te.reshape(-1, te.shape[2])
    if alive.any():
        e = traj[200:, alive].reshape(-1, te.shape[2])    # drop first 10 time units
        d2 = lambda a: np.roll(a, -1, 1) - 2 * a + np.roll(a, 1, 1)
        out["var_ratio"] = float(e.var() / tr_all.var())
        out["mean_bias"] = float(e.mean() - tr_all.mean())
        out["roughness_ratio"] = float(d2(e).var() / d2(tr_all).var())
        a, b = np.sort(e.ravel()), np.sort(tr_all.ravel())
        grid = np.union1d(a[::50], b[::50])
        out["ks"] = float(np.abs(np.searchsorted(a, grid, side="right") / len(a)
                                  - np.searchsorted(b, grid, side="right") / len(b)).max())
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--system", required=True)
    p.add_argument("--task", default="l96")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", required=True)
    p.add_argument("--rollout", type=int, default=1, help="training rollout length K (steps in the loss)")
    p.add_argument("--iters", type=int, default=1500)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--lr", type=float, default=3e-3)
    p.add_argument("--noise", type=float, default=0.0, help="std of Gaussian input noise (normalised units)")
    p.add_argument("--width", type=int, default=32)
    p.add_argument("--residual", type=int, default=1)
    p.add_argument("--ntrain", type=int, default=32, help="number of training trajectories used (of 32)")
    p.add_argument("--curve", default="")
    a = p.parse_args()
    print("CONFIG", json.dumps(vars(a)), flush=True)
    np.random.seed(a.seed); torch.manual_seed(a.seed)
    tr, va, te = get_data(a.seed)
    tr = tr[:a.ntrain]
    mu, sd = float(tr.mean()), float(tr.std())
    t0 = time.time()
    m = {}
    if a.system == "persistence":
        fn = lambda x: x
    elif a.system == "climatology":
        fn = lambda x: np.full_like(x, mu)
    elif a.system == "linear":
        # translation-invariant linear stencil (5 points) fitted by ridge regression on one-step increments
        z = (tr - mu) / sd
        zc = np.stack([np.roll(z, s, 2) for s in (2, 1, 0, -1, -2)], -1)[:, :-1].reshape(-1, 5)
        y = (z[:, 1:] - z[:, :-1]).reshape(-1)
        A = np.c_[zc, np.ones(len(zc))]
        w = np.linalg.solve(A.T @ A + 1e-3 * np.eye(6), A.T @ y)
        def fn(x):
            zx = (x - mu) / sd
            f = np.stack([np.roll(zx, s, 1) for s in (2, 1, 0, -1, -2)], -1) @ w[:5] + w[5]
            return (zx + f) * sd + mu
    elif a.system == "cnn":
        net = CNN(a.width, residual=bool(a.residual))
        m["n_params"] = float(sum(q.numel() for q in net.parameters()))
        opt = torch.optim.Adam(net.parameters(), lr=a.lr)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, a.iters)
        z = torch.tensor((tr - mu) / sd, dtype=torch.float32)
        N, T, _ = z.shape
        g = torch.Generator().manual_seed(a.seed)
        L = a.rollout
        curve = []
        for it in range(a.iters):
            i = torch.randint(0, N, (a.batch,), generator=g)
            t = torch.randint(0, T - L, (a.batch,), generator=g)
            seq = torch.stack([z[i, t + k] for k in range(L + 1)], 0)   # (L+1,B,K)
            x = seq[0]
            if a.noise > 0:
                x = x + a.noise * torch.randn(x.shape, generator=g)
            loss = 0.0
            for k in range(1, L + 1):
                x = net(x)
                loss = loss + ((x - seq[k]) ** 2).mean()
            loss = loss / L
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(net.parameters(), 1.0)
            opt.step(); sched.step()
            if it % 100 == 0:
                curve.append((it, float(loss.detach())))
        net.eval()
        def fn(x):
            with torch.no_grad():
                zx = torch.tensor((x - mu) / sd, dtype=torch.float32)
                return net(zx).double().numpy() * sd + mu
        if a.curve:
            with open(a.curve, "w") as f:
                f.write("step,value,seed,name\n")
                for s, v in curve:
                    f.write(f"{s},{v},{a.seed},{a.system}\n")
        m["final_train_loss"] = curve[-1][1]
    else:
        raise SystemExit("unknown system")
    fm, rmse, acc = forecast_metrics(fn, te, mu, sd, 50)
    m.update(fm)
    vm, _, _ = forecast_metrics(fn, va, mu, sd, 50, prefix="val_")
    m.update(vm)
    if a.system in ("cnn", "linear"):
        m.update(long_run(fn, te))
    m["truth_std"] = float(te.std())
    if a.curve:
        with open(a.curve.replace("curve_", "leadcurve_rmse_"), "w") as f:
            f.write("step,value,seed,name\n")
            for l in range(MAXLEAD + 1):
                f.write(f"{l},{rmse[l]},{a.seed},{a.system}\n")
        with open(a.curve.replace("curve_", "leadcurve_acc_"), "w") as f:
            f.write("step,value,seed,name\n")
            for l in range(MAXLEAD + 1):
                f.write(f"{l},{acc[l]},{a.seed},{a.system}\n")
    json.dump(m, open(a.out, "w"))
    print("METRICS", json.dumps(m), f"[{time.time()-t0:.0f}s]", flush=True)


if __name__ == "__main__":
    main()
