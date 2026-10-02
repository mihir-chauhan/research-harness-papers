"""Lorenz-63 data generation, derivative estimators, weak form and STLSQ (numpy/scipy only)."""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.signal import savgol_filter
from scipy.interpolate import make_smoothing_spline

SIGMA, RHO, BETA = 10.0, 28.0, 8.0 / 3.0
DT, T_END, BURN = 0.01, 10.0, 5.0
TERMS = ["1", "x", "y", "z", "x^2", "xy", "xz", "y^2", "yz", "z^2"]


def lorenz(t, s):
    x, y, z = s
    return [SIGMA * (y - x), x * (RHO - z) - y, x * y - BETA * z]


def true_coefs():
    """(10, 3) matrix, column k = right-hand side of state k over TERMS."""
    Xi = np.zeros((10, 3))
    Xi[1, 0], Xi[2, 0] = -SIGMA, SIGMA
    Xi[1, 1], Xi[2, 1], Xi[6, 1] = RHO, -1.0, -1.0
    Xi[3, 2], Xi[5, 2] = -BETA, 1.0
    return Xi


def simulate(seed, level):
    """Clean + noisy trajectory. Noise std = level * per-component std of the clean signal."""
    rng = np.random.default_rng(seed)
    s0 = np.array([-8.0, 7.0, 27.0]) + rng.normal(0, 1.0, 3)
    burn = solve_ivp(lorenz, (0, BURN), s0, method="DOP853", rtol=1e-12, atol=1e-12)
    t = np.arange(0, T_END + 1e-9, DT)
    sol = solve_ivp(lorenz, (0, T_END), burn.y[:, -1], method="DOP853", t_eval=t, rtol=1e-12, atol=1e-12)
    x = sol.y.T
    noisy = x + level * x.std(0) * rng.normal(size=x.shape)
    return t, x, noisy


def library(X):
    x, y, z = X.T
    return np.stack([np.ones_like(x), x, y, z, x * x, x * y, x * z, y * y, y * z, z * z], 1)


def stlsq(Theta, dX, thr, iters=10):
    """Sequentially thresholded least squares; columns normalised, threshold in original units."""
    nrm = np.linalg.norm(Theta, axis=0)
    Th = Theta / nrm
    Xi = np.linalg.lstsq(Th, dX, rcond=None)[0] / nrm[:, None]
    for _ in range(iters):
        small = np.abs(Xi) < thr
        Xi[small] = 0.0
        for k in range(dX.shape[1]):
            big = ~small[:, k]
            if big.any():
                Xi[big, k] = np.linalg.lstsq(Th[:, big], dX[:, k], rcond=None)[0] / nrm[big]
    return Xi


# ---------------- derivative estimators (return smoothed state or None, derivative) ----------------
def d_fd(x, dt, **_):
    return None, np.gradient(x, dt, axis=0, edge_order=2)


def d_sg(x, dt, window=51, order=3, **_):
    return (savgol_filter(x, window, order, axis=0),
            savgol_filter(x, window, order, deriv=1, delta=dt, axis=0))


def d_spline(x, dt, lam=1e-6, **_):
    t = np.arange(len(x)) * dt
    sp = [make_smoothing_spline(t, x[:, k], lam=lam) for k in range(x.shape[1])]
    return (np.stack([s(t) for s in sp], 1), np.stack([s.derivative()(t) for s in sp], 1))


_AT = {}


def tv_deriv_1d(f, dt, alpha, iters=20, eps=1e-6):
    """Chartrand (2011) TV-regularised differentiation, lagged-diffusivity Newton-type iteration."""
    n = len(f)
    if n not in _AT:
        A = np.tril(np.ones((n, n)), -1) * dt
        A[np.arange(1, n), 0] = dt / 2
        A[np.arange(1, n), np.arange(1, n)] = dt / 2
        A[0, :] = 0.0
        D = (np.eye(n, k=1) - np.eye(n))[:-1] / dt
        _AT[n] = (A, A.T @ A, D)
    A, AtA, D = _AT[n]
    fz = f - f[0]
    u = np.gradient(f, dt)
    for _ in range(iters):
        Q = 1.0 / np.sqrt((D @ u) ** 2 + eps)
        L = dt * (D.T * Q) @ D
        g = A.T @ (A @ u - fz) + alpha * (L @ u)
        u = u - np.linalg.solve(AtA + alpha * L, g)
    return u


def d_tv(x, dt, alpha=1e-2, **_):
    return None, np.stack([tv_deriv_1d(x[:, k], dt, alpha) for k in range(x.shape[1])], 1)


# ---------------- weak form ----------------
def weak_system(t, X, width, p=3, K=200):
    """Integrated library and integrated LHS for K windows with test function (1-s^2)^p (zero boundary terms)."""
    dt = t[1] - t[0]
    n = len(t)
    half = width / 2
    centers = np.linspace(t[0] + half, t[-1] - half, K)
    s = (t[None, :] - centers[:, None]) / half
    inside = np.abs(s) < 1
    phi = np.where(inside, (1 - s ** 2) ** p, 0.0)
    dphi = np.where(inside, -2 * p * s * (1 - s ** 2) ** (p - 1) / half, 0.0)
    w = np.full(n, dt); w[0] = w[-1] = dt / 2  # trapezoid
    Theta = (phi * w) @ library(X)
    G = -(dphi * w) @ X
    return Theta, G


def problem(system, t, noisy, cfg):
    """Regression problem (Theta, dX) of a system; independent of the STLSQ threshold."""
    dt = t[1] - t[0]
    if system == "weak":
        Theta, dX = weak_system(t, noisy, cfg["width"], cfg.get("p", 3), cfg.get("K", 200))
    else:
        fn = {"fd": d_fd, "sg": d_sg, "spline": d_spline, "tv": d_tv}[system]
        xs, dX = fn(noisy, dt, **{k: v for k, v in cfg.items() if k not in ("thr", "lib_smooth")})
        Xlib = xs if (cfg.get("lib_smooth") and xs is not None) else noisy
        m = int(0.05 * len(t))  # trim 5% at both ends (boundary artefacts of smoothers)
        Theta, dX = library(Xlib)[m:-m], dX[m:-m]
    return Theta, dX


def fit(system, t, noisy, cfg):
    """Return (Xi, Theta, dX) so oracle-support refits can reuse the same regression problem."""
    Theta, dX = problem(system, t, noisy, cfg)
    return stlsq(Theta, dX, cfg["thr"]), Theta, dX


def metrics(Xi, Theta, dX):
    Xt = true_coefs()
    sup, sup_t = Xi != 0, Xt != 0
    # oracle-support refit: least squares restricted to the true support with the same regression problem
    Xo = np.zeros_like(Xt)
    for k in range(3):
        idx = sup_t[:, k]
        Xo[idx, k] = np.linalg.lstsq(Theta[:, idx], dX[:, k], rcond=None)[0]
    nt = np.linalg.norm(Xt)
    return {
        "support_exact": float((sup == sup_t).all()),
        "coef_err": float(np.linalg.norm(Xi - Xt) / nt),
        "coef_err_oracle": float(np.linalg.norm(Xo - Xt) / nt),
        "false_pos": float((sup & ~sup_t).sum()),
        "false_neg": float((~sup & sup_t).sum()),
    }
