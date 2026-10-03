"""Tc read-outs and finite-size-scaling collapse."""
import numpy as np


def crossing(T, p, level=0.5):
    """First downward crossing of `level` scanning from low T (linear interpolation).
    Returns (Tc, found); if there is none, the grid edge on the side of the failure."""
    for i in range(len(T) - 1):
        if p[i] >= level > p[i + 1]:
            return T[i] + (p[i] - level) / (p[i] - p[i + 1]) * (T[i + 1] - T[i]), True
    return (T[0] if p[0] < level else T[-1]), False


def peak(T, y, lo=None, hi=None):
    """Argmax of y over T in [lo, hi], refined by a 3-point parabola."""
    m = np.ones(len(T), bool)
    if lo is not None:
        m &= T >= lo
    if hi is not None:
        m &= T <= hi
    idx = np.where(m)[0]
    i = idx[np.argmax(y[idx])]
    if 0 < i < len(T) - 1:
        a, b, c = y[i - 1], y[i], y[i + 1]
        den = a - 2 * b + c
        if den < 0:
            return T[i] + 0.5 * (a - c) / den * (T[i + 1] - T[i - 1]) / 2.0
    return T[i]


def collapse(T, curves, Tc_grid=np.arange(2.0, 2.601, 0.005), nu_grid=np.arange(0.5, 2.001, 0.025),
             window=0.6, npts=30):
    """Data collapse of curves {L: y_L(T)} onto a function of x=(T-Tc) L^(1/nu).
    Cost = mean variance across L of the linearly interpolated curves on a common x grid
    (|T-Tc| <= window for every L, so the common range is set by the smallest L).
    Returns (Tc, nu, cost); grid search, no local refinement."""
    Ls = sorted(curves)
    best = (np.inf, None, None)
    for Tc in Tc_grid:
        for nu in nu_grid:
            xs = [(T - Tc) * L ** (1.0 / nu) for L in Ls]
            xm = min(window * L ** (1.0 / nu) for L in Ls)
            xg = np.linspace(-xm, xm, npts)
            ys = []
            ok = True
            for L, x in zip(Ls, xs):
                if x[0] > xg[0] or x[-1] < xg[-1]:
                    ok = False
                    break
                ys.append(np.interp(xg, x, curves[L]))
            if not ok:
                continue
            ys = np.array(ys)
            cost = np.mean(np.var(ys, axis=0)) / (np.var(ys) + 1e-12)
            if cost < best[0]:
                best = (cost, Tc, nu)
    return best[1], best[2], best[0]
