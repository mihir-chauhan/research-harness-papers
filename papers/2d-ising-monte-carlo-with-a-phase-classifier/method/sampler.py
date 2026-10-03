"""Ising samplers (J = k_B = 1, periodic boundaries): batched Swendsen-Wang (main) and
checkerboard Metropolis (cross-check)."""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.special import ellipk

TC_EXACT = 2.0 / np.log(1.0 + np.sqrt(2.0))


def sw_sweep(S, T, rng):
    """One Swendsen-Wang sweep on a batch S (B,L,L) of +-1 spins; T has shape (B,)."""
    B, L, _ = S.shape
    p = (1.0 - np.exp(-2.0 / T))[:, None, None]
    ids = np.arange(B * L * L).reshape(B, L, L)
    rows, cols = [], []
    for axis in (1, 2):
        nb = np.roll(S, -1, axis=axis)
        act = (S == nb) & (rng.random(S.shape) < p)
        rows.append(ids[act])
        cols.append(np.roll(ids, -1, axis=axis)[act])
    rows, cols = np.concatenate(rows), np.concatenate(cols)
    n = B * L * L
    g = coo_matrix((np.ones(len(rows), dtype=np.int8), (rows, cols)), shape=(n, n))
    ncomp, lab = connected_components(g, directed=False)
    flip = rng.random(ncomp) < 0.5
    return np.where(flip[lab].reshape(B, L, L), -S, S).astype(np.int8)


def metropolis_sweep(S, T, rng):
    """One checkerboard Metropolis sweep (both sublattices) on a batch S (B,L,L)."""
    B, L, _ = S.shape
    ii, jj = np.indices((L, L))
    for parity in (0, 1):
        mask = ((ii + jj) % 2 == parity)[None]
        nn = (np.roll(S, 1, 1) + np.roll(S, -1, 1) + np.roll(S, 1, 2) + np.roll(S, -1, 2))
        dE = 2.0 * S * nn
        acc = rng.random(S.shape) < np.exp(-dE / T[:, None, None])
        S = np.where(mask & acc, -S, S).astype(np.int8)
    return S


def energy_per_site(S):
    return -(S * np.roll(S, -1, 1) + S * np.roll(S, -1, 2)).sum(axis=(1, 2)) / (S.shape[1] * S.shape[2])


def onsager_energy(T):
    """Exact infinite-lattice internal energy per site."""
    K = 1.0 / T
    k = 2.0 * np.sinh(2 * K) / np.cosh(2 * K) ** 2
    return -(1.0 / np.tanh(2 * K)) * (1 + (2 / np.pi) * (2 * np.tanh(2 * K) ** 2 - 1) * ellipk(k ** 2))


def generate(L, temps, n_chains=4, n_per_chain=50, therm=100, gap=10, seed=0):
    """Samples with shape (n_chains, n_T, n_per_chain, L, L); every (T, chain) is an
    independent Markov chain started from a random configuration."""
    rng = np.random.default_rng(seed)
    nT = len(temps)
    Tb = np.tile(temps, n_chains)
    S = rng.choice(np.array([-1, 1], dtype=np.int8), size=(n_chains * nT, L, L))
    for _ in range(therm):
        S = sw_sweep(S, Tb, rng)
    out = np.empty((n_per_chain, n_chains * nT, L, L), dtype=np.int8)
    for k in range(n_per_chain):
        for _ in range(gap):
            S = sw_sweep(S, Tb, rng)
        out[k] = S
    out = out.reshape(n_per_chain, n_chains, nT, L, L).transpose(1, 2, 0, 3, 4)
    return out
