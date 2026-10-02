"""Random-ReLU-features ridge regression: width sweep through the interpolation threshold.

One run = one (system, task, seed): the whole width sweep. Writes a flat JSON of summary metrics.
"""
import argparse, json, os, sys
import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "2"); os.environ.setdefault("MKL_NUM_THREADS", "2")

N_TRAIN, N_VAL, D_SYNTH, N_TEST_SYNTH = 200, 200, 50, 2000
RATIOS = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.25, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 25]
LAM_GRID = 10.0 ** np.arange(-6, 1.01, 0.5)   # 15 values, 1e-6 .. 10


def make_task(task, seed):
    """Returns Xtr, Ytr_noisy, Xva, Yva_noisy, Xte, Yte_clean, Ytr_clean."""
    kind, nz = task.split("_n")
    sigma = float(nz)
    rng = np.random.default_rng(10_000 + seed)
    if kind == "synth":
        w = rng.standard_normal(D_SYNTH); w /= np.linalg.norm(w)
        def gen(m):
            X = rng.standard_normal((m, D_SYNTH)); return X, np.tanh(2.0 * X @ w)[:, None]
        Xtr, Ytr = gen(N_TRAIN); Xva, Yva = gen(N_VAL); Xte, Yte = gen(N_TEST_SYNTH)
    elif kind == "digits":
        from sklearn.datasets import load_digits
        X, y = load_digits(return_X_y=True)
        p = rng.permutation(len(X)); X, y = X[p] / 16.0, y[p]
        Y = np.eye(10)[y]
        tr, va, te = slice(0, N_TRAIN), slice(N_TRAIN, N_TRAIN + N_VAL), slice(N_TRAIN + N_VAL, None)
        mu, sd = X[tr].mean(0), X[tr].std(0); keep = sd > 1e-8
        X = (X[:, keep] - mu[keep]) / sd[keep]
        Xtr, Ytr, Xva, Yva, Xte, Yte = X[tr], Y[tr], X[va], Y[va], X[te], Y[te]
    else:
        raise ValueError(task)
    Ytr_n = Ytr + sigma * rng.standard_normal(Ytr.shape)
    Yva_n = Yva + sigma * rng.standard_normal(Yva.shape)
    return Xtr, Ytr_n, Xva, Yva_n, Xte, Yte, Ytr


def fit_all_lams(Ftr, Ytr, Fev_list, lams, n):
    """Ridge (1/n)||y-Fa||^2 + lam||a||^2 for every lam via one SVD. lam=0 -> min-norm pseudo-inverse.
    Returns per lam: predictions on each eval feature matrix, and the train-prediction diagonal of the hat matrix."""
    U, s, Vt = np.linalg.svd(Ftr, full_matrices=False)
    UtY = U.T @ Ytr
    tol = 1e-10 * s.max()
    Gs = [F @ Vt.T for F in Fev_list]
    out = []
    for lam in lams:
        if lam == 0.0:
            f = np.where(s > tol, 1.0 / np.maximum(s, tol), 0.0)
            h = np.where(s > tol, 1.0, 0.0)
        else:
            f = s / (s ** 2 + n * lam); h = s ** 2 / (s ** 2 + n * lam)
        preds = [G @ (f[:, None] * UtY) for G in Gs]
        Hd = (U ** 2) @ h
        out.append((preds, Hd, U @ (h[:, None] * UtY)))
    return out


def bump(m):
    m = np.asarray(m); best = 0.0
    for p in range(1, len(m) - 1):
        best = max(best, min(m[p] - m[:p].min(), m[p] - m[p + 1:].min()))
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True, choices=["minnorm", "fixed", "global", "tuned", "loo"])
    ap.add_argument("--task", required=True); ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--lam", type=float, default=1e-2)
    ap.add_argument("--val-size", type=int, default=N_VAL)
    ap.add_argument("--curve", default=None); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    print("config:", json.dumps(vars(a)), flush=True)

    Xtr, Ytr, Xva, Yva, Xte, Yte, Ytr_clean = make_task(a.task, a.seed)
    Xva, Yva = Xva[:a.val_size], Yva[:a.val_size]
    n, d = Xtr.shape
    Nmax = int(round(max(RATIOS) * n))
    W = np.random.default_rng(20_000 + a.seed).standard_normal((d, Nmax))
    relu = lambda Z: np.maximum(Z, 0.0)
    Ptr, Pva, Pte = relu(Xtr @ W / np.sqrt(d)), relu(Xva @ W / np.sqrt(d)), relu(Xte @ W / np.sqrt(d))

    lams = [0.0] if a.system == "minnorm" else [a.lam] if a.system == "fixed" else list(LAM_GRID)
    Ns = [int(round(r * n)) for r in RATIOS]
    te_mse = np.zeros((len(Ns), len(lams))); va_mse = np.zeros_like(te_mse); loo_mse = np.zeros_like(te_mse)
    tr_mse = np.zeros_like(te_mse); te_acc = np.zeros_like(te_mse)
    for i, N in enumerate(Ns):
        sc = 1.0 / np.sqrt(N)
        res = fit_all_lams(Ptr[:, :N] * sc, Ytr, [Pva[:, :N] * sc, Pte[:, :N] * sc], lams, n)
        for j, (preds, Hd, trp) in enumerate(res):
            va_mse[i, j] = np.mean((preds[0] - Yva) ** 2)
            te_mse[i, j] = np.mean((preds[1] - Yte) ** 2)
            te_acc[i, j] = np.mean(preds[1].argmax(1) == Yte.argmax(1)) if Yte.shape[1] > 1 else np.nan
            tr_mse[i, j] = np.mean((trp - Ytr) ** 2)
            r = (Ytr - trp) / np.maximum(1.0 - Hd, 1e-12)[:, None]
            loo_mse[i, j] = np.mean(r ** 2)

    if a.system in ("minnorm", "fixed"):
        sel = np.zeros(len(Ns), dtype=int)
    elif a.system == "global":
        sel = np.full(len(Ns), int(np.argmin(va_mse.mean(0))))
    elif a.system == "tuned":
        sel = va_mse.argmin(1)
    else:  # loo
        sel = loo_mse.argmin(1)
    ix = np.arange(len(Ns))
    m, acc, trm = te_mse[ix, sel], te_acc[ix, sel], tr_mse[ix, sel]
    chosen = np.array(lams)[sel]
    t = RATIOS.index(1.0)
    win = [i for i, r in enumerate(RATIOS) if 0.4 <= r <= 4.0]   # threshold window; excludes the under-fitting left edge
    p = win[int(np.argmax(m[win]))]
    out = {"test_mse": m[t], "train_mse_thresh": trm[t], "peak_mse": m[p], "log10_peak_mse": np.log10(m[p]), "peak_pos": RATIOS[p],
           "best_mse": m.min(), "final_mse": m[-1], "bump_rel": bump(m) / m.min(),
           "peak_over_final": m[p] / m[-1]}
    if a.system not in ("minnorm", "fixed"):
        out["log10_lam_thresh"] = float(np.log10(chosen[t])); out["log10_lam_final"] = float(np.log10(chosen[-1]))
    if not np.isnan(acc).any():
        out["acc_thresh"] = acc[t]; out["acc_final"] = acc[-1]; out["acc_best"] = acc.max()
    out = {k: float(v) for k, v in out.items()}
    if a.curve:
        with open(a.curve, "w") as f:
            f.write("step,value,seed,name\n")
            for r_, v in zip(RATIOS, m): f.write(f"{r_},{v},{a.seed},{a.system}\n")
        if a.system not in ("minnorm", "fixed"):
            with open(os.path.join(os.path.dirname(a.curve), "lam_" + os.path.basename(a.curve)[6:]), "w") as f:
                f.write("step,value,seed,name\n")
                for r_, v in zip(RATIOS, np.log10(chosen)): f.write(f"{r_},{v},{a.seed},{a.system}\n")
    print("metrics:", json.dumps(out), flush=True)
    json.dump(out, open(a.out, "w"))


if __name__ == "__main__":
    main()
