"""Viscous Burgers u_t + u u_x = nu u_xx on the periodic unit interval, ETDRK4 pseudo-spectral solver."""
import numpy as np

NU = 0.01
T_FINAL = 1.0
N_SOLVE = 512          # solver grid; 128 / 256 data are exact subsamples of it
KMAX = 63              # initial conditions are band-limited so every grid >= 128 holds them exactly


def sample_ics(n, seed, N=N_SOLVE):
    """Random-Fourier-series ICs; mode k has std 25*sqrt(2)/((2 pi k)^2 + 25) (Gaussian measure of the FNO Burgers data)."""
    rng = np.random.default_rng(seed)
    x = np.arange(N) / N
    k = np.arange(1, KMAX + 1)
    s = 25.0 * np.sqrt(2.0) / ((2 * np.pi * k) ** 2 + 25.0)
    a = rng.standard_normal((n, KMAX)) * s
    b = rng.standard_normal((n, KMAX)) * s
    ang = 2 * np.pi * np.outer(k, x)
    return a @ np.cos(ang) + b @ np.sin(ang)


def solve(u0, nu=NU, T=T_FINAL, dt=1e-3, M=32):
    """ETDRK4 (Kassam-Trefethen contour-integral coefficients), 2/3 dealiasing. u0: (n, N). Returns u(T)."""
    n, N = u0.shape
    k = 2 * np.pi * np.fft.fftfreq(N, d=1.0 / N)
    L = -nu * k ** 2
    E, E2 = np.exp(dt * L), np.exp(dt * L / 2)
    r = np.exp(1j * np.pi * (np.arange(1, M + 1) - 0.5) / M)
    LR = dt * L[:, None] + r[None, :]
    Q = dt * np.mean((np.exp(LR / 2) - 1) / LR, axis=1).real
    f1 = dt * np.mean((-4 - LR + np.exp(LR) * (4 - 3 * LR + LR ** 2)) / LR ** 3, axis=1).real
    f2 = dt * np.mean((2 + LR + np.exp(LR) * (-2 + LR)) / LR ** 3, axis=1).real
    f3 = dt * np.mean((-4 - 3 * LR - LR ** 2 + np.exp(LR) * (4 - LR)) / LR ** 3, axis=1).real
    mask = (np.abs(np.fft.fftfreq(N, d=1.0 / N)) < N / 3).astype(float)
    g = -0.5j * k

    def Nf(v):
        return g * np.fft.fft(np.real(np.fft.ifft(v, axis=-1)) ** 2, axis=-1) * mask

    v = np.fft.fft(u0, axis=-1)
    for _ in range(int(round(T / dt))):
        Nv = Nf(v)
        a = E2 * v + Q * Nv
        Na = Nf(a)
        b = E2 * v + Q * Na
        Nb = Nf(b)
        c = E2 * a + Q * (2 * Nb - Nv)
        Nc = Nf(c)
        v = E * v + Nv * f1 + 2 * (Na + Nb) * f2 + Nc * f3
    return np.real(np.fft.ifft(v, axis=-1))


def make_dataset(n_total, seed, cache_dir="results/data"):
    """Returns dict res -> (u0, uT) for res in 128, 256, 512 (subsampled from the 512-point solve). Cached per (n, seed)."""
    import os
    f = os.path.join(cache_dir, f"burgers_n{n_total}_s{seed}.npz")
    if os.path.exists(f):
        z = np.load(f); u0, uT = z["u0"], z["uT"]
    else:
        u0 = sample_ics(n_total, seed)
        uT = solve(u0)
        os.makedirs(cache_dir, exist_ok=True)
        np.savez(f, u0=u0, uT=uT)
    return {r: (u0[:, :: N_SOLVE // r], uT[:, :: N_SOLVE // r]) for r in (128, 256, 512)}


if __name__ == "__main__":
    import time
    u0 = sample_ics(20, 123)
    t = time.time(); a = solve(u0); print("time", time.time() - t)
    b = solve(u0, dt=5e-4); print("dt conv", np.linalg.norm(a - b) / np.linalg.norm(b))
    u0c = u0[:, ::2]; c = solve(u0c)
    print("grid 256 vs 512", np.linalg.norm(c - a[:, ::2]) / np.linalg.norm(a))
    u0d = u0[:, ::4]; d = solve(u0d)
    print("grid 128 vs 512", np.linalg.norm(d - a[:, ::4]) / np.linalg.norm(a))
    print("max |u0|", np.abs(u0).max(), "max|uT|", np.abs(a).max(), "mass", np.abs(a.mean(1)).max())
    print("max |u_x| T", np.abs(np.diff(a, axis=1)).max() * 512)
