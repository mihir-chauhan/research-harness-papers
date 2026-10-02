"""Toy ML potential on Lennard-Jones clusters: descriptors x {KRR, MLP}.

Usage: python method/run.py --system <key> --seed S --n_train N --out file.json
"""
import argparse, json, os, time, sys, warnings
import numpy as np
import scipy.optimize as so
import scipy.linalg as sl

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")

NMAX = 13
NMIN = 5
E_CAP = 50.0
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- physics
def lj_energy(x):
    d = x[:, None, :] - x[None, :, :]
    r2 = (d ** 2).sum(-1)
    iu = np.triu_indices(len(x), 1)
    s6 = 1.0 / r2[iu] ** 3
    return float(np.sum(4.0 * (s6 * s6 - s6)))


def lj_energy_grad(flat):
    x = flat.reshape(-1, 3)
    d = x[:, None, :] - x[None, :, :]
    r2 = (d ** 2).sum(-1) + np.eye(len(x))
    s6 = 1.0 / r2 ** 3
    e = 0.5 * np.sum(4.0 * (s6 * s6 - s6) * (1 - np.eye(len(x))))
    coef = (-48.0 * s6 * s6 + 24.0 * s6) / r2 * (1 - np.eye(len(x)))
    g = (coef[:, :, None] * d).sum(1)
    return e, g.ravel()


def random_cluster(n, rng, dmin=0.85):
    """Random configuration: points uniform in a ball, rejection on pair distance < dmin."""
    R = 0.62 * n ** (1 / 3) + 0.35
    pts = []
    while len(pts) < n:
        p = rng.normal(size=3)
        p *= R * rng.uniform() ** (1 / 3) / np.linalg.norm(p)
        if all(np.linalg.norm(p - q) >= dmin for q in pts):
            pts.append(p)
    return np.array(pts)


def find_minima(n, rng, tries=40):
    """Local minimisations from random starts; keep distinct energies (global-ish minima)."""
    found = {}
    for _ in range(tries):
        x0 = random_cluster(n, rng, 0.9)
        res = so.minimize(lj_energy_grad, x0.ravel(), jac=True, method="L-BFGS-B",
                          options={"maxiter": 2000, "gtol": 1e-7})
        key = round(res.fun, 4)
        found.setdefault(key, res.x.reshape(-1, 3))
    keys = sorted(found)[:4]  # four lowest distinct minima per size
    return [found[k] - found[k].mean(0) for k in keys]


def minima_library():
    path = os.path.join(HERE, "minima.npz")
    if os.path.exists(path):
        z = np.load(path, allow_pickle=True)
        return {int(k): list(z[k]) for k in z.files}
    rng = np.random.default_rng(12345)  # fixed library, shared by all seeds and systems
    lib = {n: find_minima(n, rng) for n in range(NMIN, NMAX + 1)}
    np.savez(path, **{str(k): np.array(v, dtype=object) for k, v in lib.items()})
    return lib


def random_rotation(rng):
    q, r = np.linalg.qr(rng.normal(size=(3, 3)))
    q *= np.sign(np.diag(r))
    if np.linalg.det(q) < 0:
        q[:, 0] *= -1
    return q


def make_dataset(m, rng, lib):
    """m configurations: half perturbed minima, half random. Atom order random. Returns
    coords [m,13,3] (zero padded), n_atoms [m], energy [m], kind [m] (0 perturbed, 1 random)."""
    X = np.zeros((m, NMAX, 3)); N = np.zeros(m, int); E = np.zeros(m); K = np.zeros(m, int)
    for i in range(m):
        n = int(rng.integers(NMIN, NMAX + 1))
        while True:  # truncated sampling: resample until E <= E_CAP (keeps the energy range finite)
            if i % 2 == 0:
                base = lib[n][int(rng.integers(len(lib[n])))]
                sigma = rng.uniform(0.02, 0.12)
                x = base @ random_rotation(rng).T + sigma * rng.normal(size=(n, 3))
                K[i] = 0
            else:
                x = random_cluster(n, rng)
                K[i] = 1
            if lj_energy(x) <= E_CAP:
                break
        x = x[rng.permutation(n)]
        X[i, :n] = x; N[i] = n; E[i] = lj_energy(x)
    return X, N, E, K


def transform(X, N, rng, rot=True, perm=True):
    Y = X.copy()
    for i in range(len(X)):
        n = N[i]
        x = X[i, :n]
        if rot:
            x = x @ random_rotation(rng).T
        if perm:
            x = x[rng.permutation(n)]
        Y[i, :n] = x
    return Y

# ---------------------------------------------------------------- descriptors
def pair_inv(X, N):
    """Inverse pair distances [m,13,13] with 0 for padded / self pairs."""
    d = X[:, :, None, :] - X[:, None, :, :]
    r = np.sqrt((d ** 2).sum(-1))
    mask = (np.arange(NMAX)[None, :] < N[:, None])
    pm = mask[:, :, None] & mask[:, None, :] & ~np.eye(NMAX, dtype=bool)[None]
    inv = np.where(pm, 1.0 / np.where(pm, r, 1.0), 0.0)
    return inv, np.where(pm, r, 0.0), pm, mask


def feat_raw(X, N):
    return np.concatenate([X.reshape(len(X), -1), N[:, None].astype(float)], 1)


def feat_sorted(X, N):
    inv, r, pm, mask = pair_inv(X, N)
    iu = np.triu_indices(NMAX, 1)
    v = inv[:, iu[0], iu[1]]
    v = -np.sort(-v, axis=1)  # descending inverse distance = ascending distance; padding (0) last
    return np.concatenate([v, N[:, None].astype(float)], 1)


RC = 4.0
ETAS = np.array([0.5, 1.0, 2.0, 4.0, 8.0])
RS = np.array([0.9, 1.1, 1.4, 1.8, 2.3, 3.0])
ANG = [(eta, zeta, lam) for eta in (0.3, 1.5) for zeta in (1.0, 4.0) for lam in (1.0, -1.0)]


def atom_sf(X, N, angular=True):
    """Behler-Parrinello symmetry functions per atom: [m,13,F]. Padded atoms are zeroed."""
    inv, r, pm, mask = pair_inv(X, N)
    fc = np.where(pm & (r < RC), 0.5 * (np.cos(np.pi * r / RC) + 1.0), 0.0)
    g2 = []
    for rs in RS:  # radial: sum_j exp(-eta (r-rs)^2) fc, one eta per shell width
        for eta in (2.0, 6.0):
            g2.append((np.exp(-eta * (r - rs) ** 2) * fc).sum(2))
    g2.append(fc.sum(2))  # coordination number
    feats = list(g2)
    if angular:
        # cos theta_jik for centre i: [m,i,j,k]
        d = X[:, None, :, :] - X[:, :, None, :]  # d[m,i,j] = x_j - x_i
        rr = np.where(pm, r, 1.0)
        cos = np.einsum("mijc,mikc->mijk", d, d) / (rr[:, :, :, None] * rr[:, :, None, :])
        w = fc[:, :, :, None] * fc[:, :, None, :]
        w = w * (1 - np.eye(NMAX))[None, None]  # exclude j == k
        r2 = r[:, :, :, None] ** 2 + r[:, :, None, :] ** 2
        # r_jk^2 from law of cosines, so G4 uses r_ij, r_ik, r_jk with cutoff on all three
        rjk = np.sqrt(np.maximum(r2 - 2 * r[:, :, :, None] * r[:, :, None, :] * cos, 0))
        fjk = np.where(rjk < RC, 0.5 * (np.cos(np.pi * rjk / RC) + 1.0), 0.0)
        for eta, zeta, lam in ANG:
            t = (2.0 ** (1 - zeta)) * (1 + lam * cos).clip(min=0) ** zeta * np.exp(-eta * (r2 + rjk ** 2)) \
                * w * fjk
            feats.append(t.sum((2, 3)))
    F = np.stack(feats, 2)
    return F * mask[:, :, None]


def feat_sf_sum(X, N, angular=True):
    F = atom_sf(X, N, angular)
    return np.concatenate([F.sum(1), N[:, None].astype(float)], 1)  # sum pooling over atoms

# ---------------------------------------------------------------- models
# KRR hyperparameter grids (gamma, lambda). "wide" is the grid of all reported KRR results; "mid" and
# "narrow" exist only for the grid-sensitivity study (narrow = the truncated grid of the first version).
KRR_GRIDS = {
    "wide": ([10.0 ** (k / 2) for k in range(-14, 5)], [10.0 ** k for k in range(-13, 3)]),
    "mid": ([10.0 ** (k / 2) for k in range(-8, 1)], [10.0 ** k for k in range(-11, 0)]),
    "narrow": ([0.01, 0.03, 0.1, 0.3, 1.0], [1e-9, 1e-7, 1e-5, 1e-3, 1e-1]),
}


def krr_fit_predict(Ftr, ytr, Fva, yva, Fte_list, kernel="rbf", grid="wide"):
    """Kernel ridge regression, (gamma, lambda) chosen by validation MAE. kernel "lin" is plain ridge
    regression on the standardised descriptor (no gamma). A (gamma, lambda) pair whose Cholesky solve
    fails or is reported ill-conditioned by LAPACK (rcond below machine precision) is skipped."""
    mu, sd = Ftr.mean(0), Ftr.std(0) + 1e-8
    f = lambda A: (A - mu) / sd
    A, B = f(Ftr), f(Fva)
    ym, ys = ytr.mean(), ytr.std()
    yt = (ytr - ym) / ys
    d = A.shape[1]

    def kmat(P, Q, g):
        if kernel == "lin":
            return P @ Q.T / d
        d2 = (P ** 2).sum(1)[:, None] + (Q ** 2).sum(1)[None] - 2 * P @ Q.T
        return np.exp(-g * np.maximum(d2, 0) / d)

    gammas, lams = KRR_GRIDS[grid]
    if kernel == "lin":
        gammas = [1.0]
    best = None
    n_skip = 0
    floor = {}  # smallest lambda with a well-conditioned solve, per gamma
    for g in gammas:
        K = kmat(A, A, g); Kv = kmat(B, A, g)
        for lam in lams:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("error", sl.LinAlgWarning)
                    c = sl.solve(K + lam * np.eye(len(A)), yt, assume_a="pos")
            except (sl.LinAlgError, sl.LinAlgWarning):
                n_skip += 1
                continue
            floor.setdefault(g, lam)
            err = np.mean(np.abs(Kv @ c * ys + ym - yva))
            if best is None or err < best[0]:
                best = (err, g, lam, c)
    _, g, lam, c = best
    outs = [kmat(f(F), A, g) @ c * ys + ym for F in Fte_list]
    info = {"hp_lambda": lam, "val_mae": float(best[0]), "hp_n_skipped": n_skip,
            # 1 if the selected value is the first or last grid value (lambda: also the smallest feasible one)
            "hp_lambda_at_edge": int(lam == floor[g] or lam == lams[-1])}
    if kernel != "lin":
        info.update({"hp_gamma": g, "hp_gamma_at_edge": int(g in (gammas[0], gammas[-1]))})
    return outs, info


def torch_mlp_fit(system, Xtr, Ntr, ytr, Xva, Nva, yva, Xte_list, Nte, seed, steps, aug=False):
    import torch, torch.nn as nn
    torch.set_num_threads(2)
    atomwise = system == "atomwise"
    if atomwise:
        fx = lambda X, N: atom_sf(X, N)
    elif system == "raw":
        fx = feat_raw
    elif system == "sorted":
        fx = feat_sorted
    else:
        fx = lambda X, N: feat_sf_sum(X, N, system != "sf_rad")
    Ftr = fx(Xtr, Ntr)
    if atomwise:
        mask = (np.arange(NMAX)[None] < Ntr[:, None])
        flat = Ftr[mask]
        mu, sd = flat.mean(0), flat.std(0) + 1e-8
    else:
        mu, sd = Ftr.mean(0), Ftr.std(0) + 1e-8
    ym, ys = ytr.mean(), ytr.std()
    if atomwise:  # per-atom energy target scale
        ym = (ytr / Ntr).mean(); ys = (ytr / Ntr).std()

    def prep(X, N):
        F = (fx(X, N) - mu) / sd
        if atomwise:
            F = F * (np.arange(NMAX)[None] < N[:, None])[:, :, None]
        return torch.tensor(F, dtype=torch.float32)

    def predict(net, X, N):
        with torch.no_grad():
            out = net(prep(X, N)).squeeze(-1)
            if atomwise:
                m = torch.tensor(np.arange(NMAX)[None] < N[:, None], dtype=torch.float32)
                e = ((out * ys + ym) * m).sum(1).numpy()
            else:
                e = out.numpy() * ys + ym
        return e

    d_in = prep(Xtr[:2], Ntr[:2]).shape[-1]
    best = None
    for lr in (1e-3, 4e-3):
        torch.manual_seed(seed)
        net = nn.Sequential(nn.Linear(d_in, 128), nn.SiLU(), nn.Linear(128, 128), nn.SiLU(), nn.Linear(128, 1))
        opt = torch.optim.Adam(net.parameters(), lr=lr)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps)
        rng = np.random.default_rng(seed)
        bs = min(64, len(Xtr))
        Ftr_t = prep(Xtr, Ntr)
        yt_t = torch.tensor((ytr - ym) / ys if not atomwise else ytr, dtype=torch.float32)
        mtr = torch.tensor(np.arange(NMAX)[None] < Ntr[:, None], dtype=torch.float32)
        for s in range(steps):
            idx = rng.choice(len(Xtr), bs, replace=False)
            if aug:  # fresh random rotation + atom permutation of each training minibatch
                Xb = transform(Xtr[idx], Ntr[idx], rng)
                xb = prep(Xb, Ntr[idx])
            else:
                xb = Ftr_t[idx]
            out = net(xb).squeeze(-1)
            if atomwise:
                pred = ((out * ys + ym) * mtr[idx]).sum(1)
                loss = ((pred - yt_t[idx]) ** 2).mean() / (ys * 9.0) ** 2
            else:
                loss = ((out - yt_t[idx]) ** 2).mean()
            opt.zero_grad(); loss.backward(); opt.step(); sched.step()
        err = np.mean(np.abs(predict(net, Xva, Nva) - yva))
        if best is None or err < best[0]:
            best = (err, lr, net)
    err, lr, net = best
    return [predict(net, X, Nte) for X in Xte_list], {"hp_lr": lr, "val_mae": float(err)}

# ---------------------------------------------------------------- main
SYSTEMS = {
    # key: (descriptor, model)
    "raw_krr": ("raw", "krr"), "raw_mlp": ("raw", "mlp"), "raw_mlp_aug": ("raw", "mlp_aug"),
    "sorted_krr": ("sorted", "krr"), "sorted_mlp": ("sorted", "mlp"),
    "sf_krr": ("sf", "krr"), "sf_mlp": ("sf", "mlp"), "sf_atomwise": ("atomwise", "mlp"),
    "const": ("none", "const"), "sfrad_krr": ("sf_rad", "krr"), "sfrad_mlp": ("sf_rad", "mlp"),
    "sorted_lin": ("sorted", "lin"), "sf_lin": ("sf", "lin"), "sfrad_lin": ("sf_rad", "lin"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True, choices=list(SYSTEMS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n_train", type=int, default=500)
    ap.add_argument("--n_test", type=int, default=1000)
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--krr_grid", default="wide", choices=list(KRR_GRIDS))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    print("config:", json.dumps(vars(a)), flush=True)
    t0 = time.time()
    desc, model = SYSTEMS[a.system]
    lib = minima_library()
    # data seed depends only on the run seed -> every system sees identical train/val/test sets
    rng = np.random.default_rng(1000 + a.seed)
    n_val = max(50, a.n_train // 4)
    Xtr, Ntr, ytr, _ = make_dataset(a.n_train, rng, lib)
    Xva, Nva, yva, _ = make_dataset(n_val, rng, lib)
    Xte, Nte, yte, Kte = make_dataset(a.n_test, rng, lib)
    trng = np.random.default_rng(777 + a.seed)
    Xrot = transform(Xte, Nte, trng, rot=True, perm=False)
    Xperm = transform(Xte, Nte, trng, rot=False, perm=True)
    Xboth = transform(Xte, Nte, trng, rot=True, perm=True)
    tests = [Xte, Xrot, Xperm, Xboth]
    if model == "const":  # reference: predict the training-set mean energy
        preds, info = [np.full(a.n_test, ytr.mean())] * 4, {"val_mae": float(np.abs(yva - ytr.mean()).mean())}
    elif model in ("krr", "lin"):
        fx = {"raw": feat_raw, "sorted": feat_sorted, "sf": feat_sf_sum,
              "sf_rad": lambda X, N: feat_sf_sum(X, N, False)}[desc]
        preds, info = krr_fit_predict(fx(Xtr, Ntr), ytr, fx(Xva, Nva), yva, [fx(X, Nte) for X in tests],
                                      kernel="rbf" if model == "krr" else "lin", grid=a.krr_grid)
    else:
        preds, info = torch_mlp_fit(desc, Xtr, Ntr, ytr, Xva, Nva, yva, tests, Nte, a.seed, a.steps,
                                    aug=(model == "mlp_aug"))
    p0, pr, pp, pb = preds
    ae = np.abs(p0 - yte)
    out = {
        "energy_mae": float(ae.mean()),
        "energy_mae_per_atom": float((ae / Nte).mean()),
        "mae_perturbed": float(ae[Kte == 0].mean()),
        "mae_random": float(ae[Kte == 1].mean()),
        "mae_rotated": float(np.abs(pr - yte).mean()),
        "mae_permuted": float(np.abs(pp - yte).mean()),
        "mae_rot_perm": float(np.abs(pb - yte).mean()),
        "inv_defect": float(np.abs(pb - p0).mean()),  # |E(gx)-E(x)|, mean over test set
        "inv_defect_max": float(np.abs(pb - p0).max()),
        "test_energy_std": float(yte.std()),
        "val_mae": info["val_mae"],
        "runtime_s": time.time() - t0,
    }
    out.update({k: v for k, v in info.items() if k.startswith("hp_")})
    print(json.dumps(out, indent=1))
    json.dump(out, open(a.out, "w"))


if __name__ == "__main__":
    main()
