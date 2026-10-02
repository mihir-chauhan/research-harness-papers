"""Two-scale Lorenz-96 (Lorenz 1996; Wilks 2005 parametrisation) and slow-only closed models.

dX_k/dt = -X_{k-1}(X_{k-2}-X_{k+1}) - X_k + F - U_k,   U_k = (h c / b) * sum_j Y_{j,k}
dY_i/dt = -c b Y_{i+1}(Y_{i+2}-Y_{i-1}) - c Y_i + (h c / b) X_{k(i)}      (Y on a ring of K*J points)
All functions are batched over a leading axis of independent chains.
"""
import numpy as np

K, J, H, B = 8, 32, 1.0, 10.0
DT_SAMPLE = 0.005          # sampling interval of the data and step of the closed slow model
DT_TRUTH = 0.0025          # RK4 step of the full two-scale model


def slow_tend(X, F):
    return -np.roll(X, 1, -1) * (np.roll(X, 2, -1) - np.roll(X, -1, -1)) - X + F


def two_scale_rhs(X, Y, F, c):
    hcb = H * c / B
    dX = slow_tend(X, F) - hcb * Y.reshape(*Y.shape[:-1], K, J).sum(-1)
    dY = (-c * B * np.roll(Y, -1, -1) * (np.roll(Y, -2, -1) - np.roll(Y, 1, -1)) - c * Y
          + hcb * np.repeat(X, J, -1))
    return dX, dY


def rk4_full(X, Y, F, c, dt):
    k1x, k1y = two_scale_rhs(X, Y, F, c)
    k2x, k2y = two_scale_rhs(X + .5 * dt * k1x, Y + .5 * dt * k1y, F, c)
    k3x, k3y = two_scale_rhs(X + .5 * dt * k2x, Y + .5 * dt * k2y, F, c)
    k4x, k4y = two_scale_rhs(X + dt * k3x, Y + dt * k3y, F, c)
    return (X + dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x),
            Y + dt / 6 * (k1y + 2 * k2y + 2 * k3y + k4y))


def simulate_truth(seed, n_chains, t_spin, t_len, F, c, dt=DT_TRUTH):
    """Return X (T, n_chains, K) and U (T, n_chains, K) sampled every DT_SAMPLE after spin-up."""
    rng = np.random.default_rng(seed)
    X = F * 0.5 + rng.normal(size=(n_chains, K)) * 2.0
    Y = rng.normal(size=(n_chains, K * J)) * 0.1
    sub = int(round(DT_SAMPLE / dt))
    for _ in range(int(round(t_spin / dt))):
        X, Y = rk4_full(X, Y, F, c, dt)
    n = int(round(t_len / DT_SAMPLE))
    Xs = np.empty((n, n_chains, K)); Us = np.empty_like(Xs)
    for i in range(n):
        Xs[i] = X; Us[i] = H * c / B * Y.reshape(n_chains, K, J).sum(-1)
        for _ in range(sub):
            X, Y = rk4_full(X, Y, F, c, dt)
    assert np.isfinite(Xs).all()
    return Xs, Us


def rk4_slow(X, e, closure, F, dt=DT_SAMPLE):
    """One RK4 step of the slow-only model; closure(X) evaluated at each stage, noise e fixed over the step."""
    f = lambda x: slow_tend(x, F) - closure(x) - e
    k1 = f(X); k2 = f(X + .5 * dt * k1); k3 = f(X + .5 * dt * k2); k4 = f(X + dt * k3)
    return X + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
