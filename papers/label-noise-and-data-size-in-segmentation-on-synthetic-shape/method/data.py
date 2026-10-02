"""Synthetic shapes dataset and label-noise models (numpy only)."""
import numpy as np
from scipy import ndimage as ndi

S = 64
CLASSES = ["bg", "circle", "square", "triangle"]


def _texture(rng, base, amp, sigma):
    n = ndi.gaussian_filter(rng.standard_normal((S, S)), sigma)
    n = n / (n.std() + 1e-8)
    yy, xx = np.mgrid[0:S, 0:S] / S
    th, fr = rng.uniform(0, np.pi), rng.uniform(2, 8)
    grat = np.sin(2 * np.pi * fr * (xx * np.cos(th) + yy * np.sin(th)) + rng.uniform(0, 6.28))
    return base + amp * (0.7 * n + 0.3 * grat)


def make_image(rng):
    """Returns image (3,S,S) float32, label (S,S) int64 (visible class), inst (S,S) int (visible instance id, 0=bg)."""
    img = np.stack([_texture(rng, rng.uniform(0.3, 0.7), rng.uniform(0.05, 0.12), rng.uniform(1.5, 4)) for _ in range(3)])
    lab = np.zeros((S, S), np.int64)
    inst = np.zeros((S, S), np.int64)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    for k in range(rng.integers(3, 6)):
        c = int(rng.integers(1, 4))
        cx, cy = rng.uniform(12, S - 12, 2)
        r = rng.uniform(8, 14)
        th = rng.uniform(0, 2 * np.pi)
        if c == 1:
            m = (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r
        elif c == 2:
            u = (xx - cx) * np.cos(th) + (yy - cy) * np.sin(th)
            v = -(xx - cx) * np.sin(th) + (yy - cy) * np.cos(th)
            m = (np.abs(u) <= 0.85 * r) & (np.abs(v) <= 0.85 * r)
        else:
            ang = th + np.array([0, 2 * np.pi / 3, 4 * np.pi / 3])
            P = np.stack([cx + 1.15 * r * np.cos(ang), cy + 1.15 * r * np.sin(ang)], 1)
            m = np.ones((S, S), bool)
            for i in range(3):
                a, b = P[i], P[(i + 1) % 3]
                cr = (b[0] - a[0]) * (yy - a[1]) - (b[1] - a[1]) * (xx - a[0])
                m &= cr >= 0 if _orient(P) > 0 else cr <= 0
        col = rng.uniform(0.2, 0.9, 3)
        tex = _texture(rng, 0.0, rng.uniform(0.02, 0.06), rng.uniform(0.7, 2.5))
        for ch in range(3):
            img[ch][m] = (col[ch] + tex)[m]
        lab[m] = c
        inst[m] = k + 1
    img += 0.02 * rng.standard_normal(img.shape)
    return np.clip(img, 0, 1).astype(np.float32), lab, inst


def _orient(P):
    return (P[1, 0] - P[0, 0]) * (P[2, 1] - P[0, 1]) - (P[1, 1] - P[0, 1]) * (P[2, 0] - P[0, 0])


def make_split(n, seed):
    rng = np.random.default_rng(seed)
    out = [make_image(rng) for _ in range(n)]
    return (np.stack([o[0] for o in out]), np.stack([o[1] for o in out]), np.stack([o[2] for o in out]))


def boundary_noise(lab, p, rng):
    """Each pixel in the 5x5 boundary band (within 2 px of a label edge) is, with prob p,
    relabelled with the label of a random pixel in its 5x5 neighbourhood."""
    band = ndi.maximum_filter(lab, size=5) != ndi.minimum_filter(lab, size=5)
    dy, dx = rng.integers(-2, 3, lab.shape), rng.integers(-2, 3, lab.shape)
    yy, xx = np.mgrid[0:S, 0:S]
    shifted = lab[np.clip(yy + dy, 0, S - 1), np.clip(xx + dx, 0, S - 1)]
    flip = band & (rng.random(lab.shape) < p)
    return np.where(flip, shifted, lab)


def flip_noise(lab, inst, p, rng):
    """Each visible object is, with prob p, relabelled as a different random foreground class."""
    out = lab.copy()
    for i in np.unique(inst):
        if i == 0 or rng.random() >= p:
            continue
        m = inst == i
        c = lab[m][0]
        out[m] = rng.choice([k for k in (1, 2, 3) if k != c])
    return out


def corrupt(labs, insts, kind, p, seed):
    rng = np.random.default_rng(seed)
    if p == 0 or kind == "none":
        return labs.copy()
    if kind == "boundary":
        return np.stack([boundary_noise(l, p, rng) for l in labs])
    if kind == "flip":
        return np.stack([flip_noise(l, i, p, rng) for l, i in zip(labs, insts)])
    raise ValueError(kind)
