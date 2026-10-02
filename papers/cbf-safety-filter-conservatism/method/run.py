"""CBF safety filters on an unsafe nominal controller (numpy only, vectorised over episodes).

Systems: nominal | ct (continuous-time CBF at discrete steps, ZOH) | dt (discrete-time CBF) | heur (braking heuristic)
Tasks:   double_integrator | unicycle
"""
import argparse, json, os
import numpy as np

H = 0.005          # plant integration step (s); control period dt must be a multiple of it
TMAX = 30.0
GOAL_TOL = 0.15
NOBS = 3
L = 0.15           # unicycle look-ahead point offset
KB = 4.0           # braking gain of the heuristic (double integrator)
TOL = 1e-9         # clearance below -TOL counts as a violation (same for every system); a point projected
                   # exactly onto the boundary sits at about -1e-14 m by round-off and is not a violation


def scenarios(seed, E):
    rng = np.random.default_rng(10_000 + seed)
    s = np.stack([rng.uniform(-0.5, 0.5, E), rng.uniform(-1, 1, E)], 1)
    g = np.stack([np.full(E, 9.0), rng.uniform(-1, 1, E)], 1)
    ox = np.array([2.5, 4.8, 7.1])[None] + rng.uniform(-0.3, 0.3, (E, NOBS))
    yl = s[:, 1:2] + (g[:, 1:2] - s[:, 1:2]) * ox / 9.0
    oy = yl + rng.uniform(-0.6, 0.6, (E, NOBS))
    C = np.stack([ox, oy], 2)                      # (E,K,2)
    R = rng.uniform(0.5, 0.8, (E, NOBS))
    th = rng.uniform(-0.5, 0.5, E)
    return s, g, C, R, th


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def nearest(pt, C, rad):
    d = np.linalg.norm(pt[:, None] - C, axis=2) - rad            # (E,K)
    k = np.argmin(d, 1)
    i = np.arange(len(pt))
    return C[i, k], rad[i, k]


# ---------------- double integrator (p,v in R^2, input a) ----------------
def di_nominal(p, v, g):
    return 1.5 * (g - p) - 2.5 * v


def most_critical(p, v, C, R, alpha):
    """Obstacle with the smallest first-order HOCBF margin psi1 = hd + alpha h (one active constraint)."""
    z = p[:, None] - C
    psi = 2 * (z * v[:, None]).sum(2) + alpha * ((z ** 2).sum(2) - R ** 2)
    k = np.argmin(psi, 1)
    i = np.arange(len(p))
    return C[i, k], R[i, k]


def di_filter(system, p, v, a0, C, R, alpha, dt, dth, select="critical"):
    if system == "heur" or select == "nearest":
        c, r = nearest(p, C, R)
    else:
        c, r = most_critical(p, v, C, R, alpha)
    z = p - c
    if system == "ct":      # HOCBF with h=|z|^2-r^2: hdd + 2 a hd + a^2 h >= 0
        h = (z ** 2).sum(1) - r ** 2
        row = 2 * z
        rhs = -(2 * (v ** 2).sum(1) + 4 * alpha * (z * v).sum(1) + alpha ** 2 * h)
    elif system == "dt":    # h(x_{k+1}) >= (1-g) h(x_k) on the exact ZOH successor z+dt v+0.5 dt^2 a
        g1 = min(1.0, alpha * dt)
        h = (z ** 2).sum(1) - r ** 2
        rho = np.sqrt(r ** 2 + (1 - g1) * h)
        w = z + dt * v + 0.5 * dt ** 2 * a0
        wn = np.linalg.norm(w, axis=1, keepdims=True)
        dirn = w / np.maximum(wn, 1e-12)
        w2 = np.where(wn < rho[:, None], dirn * rho[:, None], w)   # radial projection onto the ball
        return a0 + (w2 - w) * 2.0 / dt ** 2
    elif system == "heur":
        n = z / np.linalg.norm(z, axis=1, keepdims=True)
        d = np.linalg.norm(z, axis=1) - r
        vn = (v * n).sum(1)
        act = (d < dth) & (vn < 0)
        an = (a0 * n).sum(1)
        a = a0 - np.where(act & (an < 0), an, 0.0)[:, None] * n
        a = a + np.where(act, -KB * vn, 0.0)[:, None] * n
        return a
    sl = (row * a0).sum(1) - rhs
    nr = (row ** 2).sum(1) + 1e-12
    return a0 + (np.maximum(0.0, -sl) / nr)[:, None] * row


# ---------------- unicycle (x,y,theta; input v,omega) ----------------
def uni_nominal(x, g):
    e = g - x[:, :2]
    dist = np.linalg.norm(e, axis=1)
    err = wrap(np.arctan2(e[:, 1], e[:, 0]) - x[:, 2])
    v = np.minimum(1.0, dist) * np.maximum(0.0, np.cos(err))
    return v, np.clip(2.0 * err, -3, 3)


def uni_filter(system, x, v0, w0, C, R, alpha, dt, dth):
    th = x[:, 2]
    ct, st = np.cos(th), np.sin(th)
    q = x[:, :2] + L * np.stack([ct, st], 1)
    rho_all = R + L
    c, rho = nearest(q, C, rho_all)
    z = q - c
    # point velocity m = J u, J=[[cos,-L sin],[sin,L cos]]
    m0 = np.stack([ct * v0 - L * st * w0, st * v0 + L * ct * w0], 1)
    if system == "ct":
        h = (z ** 2).sum(1) - rho ** 2
        row = 2 * z
        sl = (row * m0).sum(1) + alpha * h
        m = m0 + (np.maximum(0.0, -sl) / ((row ** 2).sum(1) + 1e-12))[:, None] * row
    elif system == "dt":
        g1 = min(1.0, alpha * dt)
        zn = np.linalg.norm(z, axis=1)
        Rr = np.sqrt((1 - g1) * zn ** 2 + g1 * rho ** 2)
        w = z + dt * m0
        wn = np.linalg.norm(w, axis=1, keepdims=True)
        dirn = np.where(wn > 1e-9, w / np.maximum(wn, 1e-12), z / zn[:, None])
        w2 = np.where(wn[:, 0:1] < Rr[:, None], dirn * Rr[:, None], w)
        m = (w2 - z) / dt
    elif system == "heur":
        zn = np.linalg.norm(z, axis=1)
        n = z / zn[:, None]
        d = zn - rho
        mn = (m0 * n).sum(1)
        act = (d < dth) & (mn < 0)
        sc = np.clip(d / dth, 0, 1)
        m = m0 + np.where(act, -mn * (1 - sc), 0.0)[:, None] * n
    v = ct * m[:, 0] + st * m[:, 1]
    w = (-st * m[:, 0] + ct * m[:, 1]) / L
    return v, w


def simulate(a):
    E = a.episodes
    s, g, C, R, th0 = scenarios(a.seed, E)
    ns = int(round(a.dt / H))
    assert abs(ns * H - a.dt) < 1e-9
    di = a.task == "double_integrator"
    p = s.copy(); v = np.zeros((E, 2)); x = np.concatenate([s, th0[:, None]], 1)
    done = np.zeros(E, bool); tg = np.full(E, TMAX)
    minc = np.full(E, np.inf)
    minb = np.full(E, np.inf)      # barrier-level clearance (unicycle: look-ahead point vs radius+L)
    mins = np.full(E, np.inf)      # barrier-level clearance at control sample instants only
    traj = []
    nctrl = int(TMAX / a.dt)
    for k in range(nctrl):
        pos = p if di else x[:, :2]
        newly = (~done) & (np.linalg.norm(pos - g, axis=1) < GOAL_TOL)
        tg[newly] = k * a.dt
        done |= newly
        if done.all():
            break
        if di:
            a0 = di_nominal(p, v, g)
            u = a0 if a.system == "nominal" else di_filter(a.system, p, v, a0, C, R, a.alpha, a.dt, a.dth, a.select)
        else:
            v0, w0 = uni_nominal(x, g)
            if a.system == "nominal":
                vv, ww = v0, w0
            else:
                vv, ww = uni_filter(a.system, x, v0, w0, C, R, a.alpha, a.dt, a.dth)
        act = ~done
        for j in range(ns):
            if di:
                p = np.where(act[:, None], p + H * v + 0.5 * H * H * u, p)
                v = np.where(act[:, None], v + H * u, v)
                pos = p
            else:
                thm = x[:, 2] + 0.5 * H * ww
                nx = np.stack([x[:, 0] + H * vv * np.cos(thm), x[:, 1] + H * vv * np.sin(thm), x[:, 2] + H * ww], 1)
                x = np.where(act[:, None], nx, x)
                pos = x[:, :2]
            d = (np.linalg.norm(pos[:, None] - C, axis=2) - R).min(1)
            minc = np.where(act, np.minimum(minc, d), minc)
            if di:
                db = d
            else:
                q = x[:, :2] + L * np.stack([np.cos(x[:, 2]), np.sin(x[:, 2])], 1)
                db = (np.linalg.norm(q[:, None] - C, axis=2) - (R + L)).min(1)
            minb = np.where(act, np.minimum(minb, db), minb)
            if j == ns - 1:
                mins = np.where(act, np.minimum(mins, db), mins)
        if a.traj:
            traj.append(pos[0].tolist())
    return dict(minc=minc, minb=minb, mins=mins, done=done, tg=tg, traj=traj, goal0=g[0].tolist(), C0=C[0].tolist(), R0=R[0].tolist())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True, choices=["nominal", "ct", "dt", "heur"])
    ap.add_argument("--task", required=True, choices=["double_integrator", "unicycle"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--alpha", type=float, default=2.0)
    ap.add_argument("--dt", type=float, default=0.05)
    ap.add_argument("--select", default="critical", choices=["critical", "nearest"])
    ap.add_argument("--dth", type=float, default=1.0)
    ap.add_argument("--episodes", type=int, default=100)
    ap.add_argument("--out", required=True)
    ap.add_argument("--traj", default="")
    a = ap.parse_args()
    r = simulate(a)
    m = r["minc"]
    out = {
        "violation_rate": float((m < -TOL).mean()),
        "success_rate": float(r["done"].mean()),
        "time_to_goal": float(r["tg"].mean()),
        "min_clearance": float(m.mean()),
        "worst_penetration": float(max(0.0, -m.min())),
        "barrier_violation_rate": float((r["minb"] < -TOL).mean()),
        "barrier_penetration": float(max(0.0, -r["minb"].min())),
        "sample_violation_rate": float((r["mins"] < -TOL).mean()),
        "sample_penetration": float(max(0.0, -r["mins"].min())),
    }
    print(json.dumps(dict(system=a.system, task=a.task, seed=a.seed, alpha=a.alpha, dt=a.dt, select=a.select, dth=a.dth,
                          episodes=a.episodes, plant_step=H, tol=TOL, **out)))
    json.dump(out, open(a.out, "w"))
    if a.traj:
        json.dump(dict(traj=r["traj"], dt=a.dt, goal=r["goal0"], C=r["C0"], R=r["R0"]), open(a.traj, "w"))


if __name__ == "__main__":
    main()
