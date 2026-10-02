"""Two-scale Lorenz-96 (Lorenz 1996; Wilks 2005 parameters), NumPy RK4, batched over trajectories."""
import numpy as np

K, J = 36, 10
F, H, C, B = 10.0, 1.0, 10.0, 10.0
DT_INT = 0.005      # RK4 step
DT_OBS = 0.05       # emulator step (10 RK4 steps)


def tendency(X, Y):
    # X: (N,K); Y: (N,K*J) with Y[:, k*J+j] the fast variables coupled to X[:,k]
    dX = (np.roll(X, -1, 1) - np.roll(X, 2, 1)) * np.roll(X, 1, 1) - X + F
    Yk = Y.reshape(Y.shape[0], K, J)
    dX = dX - (H * C / B) * Yk.sum(2)
    dY = -C * B * np.roll(Y, -1, 1) * (np.roll(Y, -2, 1) - np.roll(Y, 1, 1)) - C * Y \
        + (H * C / B) * np.repeat(X, J, axis=1)
    return dX, dY


def rk4(X, Y, dt):
    k1x, k1y = tendency(X, Y)
    k2x, k2y = tendency(X + .5 * dt * k1x, Y + .5 * dt * k1y)
    k3x, k3y = tendency(X + .5 * dt * k2x, Y + .5 * dt * k2y)
    k4x, k4y = tendency(X + dt * k3x, Y + dt * k3y)
    return (X + dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x),
            Y + dt / 6 * (k1y + 2 * k2y + 2 * k3y + k4y))


def simulate(n_traj, n_steps, seed, spinup=400):
    """Return slow variables (n_traj, n_steps, K) sampled every DT_OBS after spin-up."""
    rng = np.random.default_rng(seed)
    X = F * (0.5 + 0.5 * rng.standard_normal((n_traj, K)))
    Y = 0.1 * rng.standard_normal((n_traj, K * J))
    sub = int(round(DT_OBS / DT_INT))
    out = np.empty((n_traj, n_steps, K))
    for t in range(spinup + n_steps):
        for _ in range(sub):
            X, Y = rk4(X, Y, DT_INT)
        if t >= spinup:
            out[:, t - spinup] = X
    return out
