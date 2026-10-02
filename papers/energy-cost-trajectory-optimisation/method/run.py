"""Energy-based cost for iLQR-MPC swing-up: pendulum and cart-pole (numpy only).
Usage: python method/run.py --system <name> --task <pendulum|cartpole> --seed S --out file.json
Systems: iLQR-Quad, iLQR-Energy, iLQR-Quad+Energy, EnergyShaping-LQR
"""
import argparse, json, time
import numpy as np
from scipy.linalg import solve_discrete_are

DT = 0.05
TSIM = 6.0
G = 9.81

# ------------------------------------------------------------------ plants
class Pendulum:
    name = "pendulum"; nx = 2; umax = 3.0; b = 0.05; xlim = None
    def f(self, x, u):  # x: (...,2) [theta, omega], theta=0 upright; u torque (unit m,l)
        th, w = x[..., 0], x[..., 1]
        return np.stack([w, G * np.sin(th) + u - self.b * w], -1)
    def energy(self, x):  # zero potential at pivot height; upright E* = G
        return 0.5 * x[..., 1] ** 2 + G * np.cos(x[..., 0])
    def dE(self, x):
        return np.stack([-G * np.sin(x[..., 0]), x[..., 1]], -1)
    Estar = G
    # quadratic cost weights
    q = np.array([1.0, 0.1]); r = 0.05; qf = np.array([100.0, 10.0])
    def err(self, x):  # state error with wrapped angle
        e = x.copy(); e[..., 0] = wrap(x[..., 0]); return e
    def sample(self, rng):
        return np.array([rng.uniform(-np.pi, np.pi), rng.uniform(-1, 1)])
    def upright(self, x):
        return abs(wrap(x[0])) < 0.15 and abs(x[1]) < 0.6

class CartPole:
    name = "cartpole"; nx = 4; umax = 8.0; xlim = 2.4
    mc, mp, l, b = 1.0, 0.3, 0.5, 0.02  # point-mass pole at distance l
    # state [x, theta, v, omega]; theta=0 upright
    def f(self, x, u):
        th, v, w = x[..., 1], x[..., 2], x[..., 3]
        s, c = np.sin(th), np.cos(th)
        mc, mp, l = self.mc, self.mp, self.l
        a = (u + mp * l * w ** 2 * s - mp * G * s * c) / (mc + mp * s ** 2)
        al = (G * s - a * c) / l - self.b * w
        return np.stack([v, w, a, al], -1)
    def energy(self, x):  # pole energy, E* = mp g l
        return 0.5 * self.mp * (self.l * x[..., 3]) ** 2 + self.mp * G * self.l * np.cos(x[..., 1])
    def dE(self, x):
        z = np.zeros_like(x[..., 0])
        return np.stack([z, -self.mp * G * self.l * np.sin(x[..., 1]), z, self.mp * self.l ** 2 * x[..., 3]], -1)
    @property
    def Estar(self): return self.mp * G * self.l
    q = np.array([1.0, 10.0, 0.1, 0.1]); r = 0.01; qf = np.array([50.0, 500.0, 50.0, 50.0])
    def err(self, x):
        e = x.copy(); e[..., 1] = wrap(x[..., 1]); return e
    def sample(self, rng):
        return np.array([rng.uniform(-0.5, 0.5), rng.uniform(-np.pi, np.pi), 0.0, rng.uniform(-1, 1)])
    def upright(self, x):
        return abs(wrap(x[1])) < 0.15 and abs(x[3]) < 0.6 and abs(x[2]) < 0.6

def wrap(a): return (a + np.pi) % (2 * np.pi) - np.pi

def step(plant, x, u):  # RK4, zero-order hold
    u = np.clip(u, -plant.umax, plant.umax)
    k1 = plant.f(x, u); k2 = plant.f(x + DT / 2 * k1, u)
    k3 = plant.f(x + DT / 2 * k2, u); k4 = plant.f(x + DT * k3, u)
    return x + DT / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

def linearize(plant):
    n = plant.nx; x0 = np.zeros(n); eps = 1e-6
    A = np.zeros((n, n))
    for i in range(n):
        d = np.zeros(n); d[i] = eps
        A[:, i] = (step(plant, x0 + d, 0.0) - step(plant, x0 - d, 0.0)) / (2 * eps)
    B = ((step(plant, x0, eps) - step(plant, x0, -eps)) / (2 * eps))[:, None]
    return A, B

def lqr_gain(plant, scale=1.0):
    A, B = linearize(plant)
    Q = np.diag(plant.q) * scale; R = np.array([[plant.r]])
    P = solve_discrete_are(A, B, Q, R)
    return np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)

# ------------------------------------------------------------------ iLQR
class ILQR:
    """Gauss-Newton iLQR on residual costs l = 0.5*||r||^2. Controls are clipped to the limits in the rollout."""
    def __init__(self, plant, cost, horizon, iters=4, first_iters=25):
        self.p, self.c, self.T = plant, cost, horizon
        self.iters, self.first_iters = iters, first_iters
        self.U = np.zeros(horizon); self.first = True
        self.eps = 1e-5
    def dyn_jac(self, X, U):  # batched finite-difference Jacobians of the RK4 step
        p, n = self.p, self.p.nx
        A = np.zeros((len(U), n, n))
        for i in range(n):
            d = np.zeros(n); d[i] = self.eps
            A[:, :, i] = (step(p, X[:-1] + d, U) - step(p, X[:-1] - d, U)) / (2 * self.eps)
        B = (step(p, X[:-1], U + self.eps) - step(p, X[:-1], U - self.eps)) / (2 * self.eps)
        return A, B
    def rollout(self, x0, U, X=None, K=None, k=None, alpha=0.0):
        p = self.p; Xn = np.zeros((self.T + 1, p.nx)); Xn[0] = x0; Un = np.zeros(self.T)
        for t in range(self.T):
            u = U[t]
            if K is not None: u = u + alpha * k[t] + K[t] @ (Xn[t] - X[t])
            u = float(np.clip(u, -p.umax, p.umax)); Un[t] = u
            Xn[t + 1] = step(p, Xn[t], u)
        return Xn, Un
    def total(self, X, U):
        return self.c.stage(X[:-1], U)[0].sum() * DT + self.c.term(X[-1])[0]
    def solve(self, x0):
        p, n, T = self.p, self.p.nx, self.T
        U = self.U; X, U = self.rollout(x0, U); J = self.total(X, U); mu = 1e-3
        for _ in range(self.first_iters if self.first else self.iters):
            A, B = self.dyn_jac(X, U)
            _, lx, lu, lxx, luu = self.c.stage(X[:-1], U)
            lx, lu, lxx, luu = lx * DT, lu * DT, lxx * DT, luu * DT
            _, Vx, Vxx = self.c.term(X[-1])
            K = np.zeros((T, n)); k = np.zeros(T); ok = True
            for t in range(T - 1, -1, -1):
                Qx = lx[t] + A[t].T @ Vx; Qu = lu[t] + B[t] @ Vx
                Qxx = lxx[t] + A[t].T @ Vxx @ A[t]
                Quu = luu[t] + B[t] @ Vxx @ B[t] + mu
                Qux = B[t] @ Vxx @ A[t]
                K[t] = -Qux / Quu; k[t] = -Qu / Quu
                Vx = Qx + K[t] * Quu * k[t] + K[t] * Qu + Qux * k[t]
                Vxx = Qxx + np.outer(K[t], K[t]) * Quu + np.outer(K[t], Qux) + np.outer(Qux, K[t])
                Vxx = 0.5 * (Vxx + Vxx.T)
            improved = False
            for alpha in (1.0, 0.5, 0.25, 0.1, 0.03):
                Xn, Un = self.rollout(x0, U, X, K, k, alpha)
                Jn = self.total(Xn, Un)
                if np.isfinite(Jn) and Jn < J:
                    X, U, J, improved = Xn, Un, Jn, True; mu = max(mu * 0.5, 1e-6); break
            if not improved:
                mu *= 10
                if mu > 1e4: break
        self.first = False
        self.U, self.X, self.K = U, X, K
        return U

    def shift(self):
        self.U = np.concatenate([self.U[1:], self.U[-1:]])

class Cost:
    """Residual cost. kind in {'quad','energy','both'}.
    quad  : 0.5 e'Qe + 0.5 r u^2
    energy: 0.5 wE (E-E*)^2 + 0.5 r u^2 + 0.5 wq0 e'Qe (small regulariser; wq0 = 0 for pure energy by default)
    both  : quad + energy
    terminal cost is always the quadratic 0.5 e'Qf e (identical across systems)."""
    def __init__(self, plant, kind, wE=1.0, qscale=1.0, rscale=1.0, q_in_energy=0.0):
        self.p, self.kind, self.wE = plant, kind, wE
        self.Q = np.diag(plant.q) * (qscale if kind != "energy" else q_in_energy)
        self.R = plant.r * rscale; self.Qf = np.diag(plant.qf)
        self.use_e = kind in ("energy", "both")
    def stage(self, X, U):
        p = self.p; e = p.err(X)
        c = 0.5 * np.einsum("ti,ij,tj->t", e, self.Q, e) + 0.5 * self.R * U ** 2
        lx = e @ self.Q; lxx = np.broadcast_to(self.Q, (len(U),) + self.Q.shape).copy()
        lu = self.R * U; luu = np.full(len(U), self.R)
        if self.use_e:
            d = p.energy(X) - p.Estar; J = p.dE(X)
            c = c + 0.5 * self.wE * d ** 2
            lx = lx + self.wE * d[:, None] * J
            lxx = lxx + self.wE * J[:, :, None] * J[:, None, :]  # Gauss-Newton
        return c, lx, lu, lxx, luu
    def term(self, x):
        e = self.p.err(x); return 0.5 * e @ self.Qf @ e, self.Qf @ e, self.Qf

# ------------------------------------------------------------------ controllers
class MPC:
    def __init__(self, plant, cost, horizon):
        self.ilqr = ILQR(plant, cost, horizon)
    def act(self, x):
        U = self.ilqr.solve(x); u = U[0]; self.ilqr.shift(); return u

class EnergyShaping:
    """Astrom-Furuta energy swing-up + LQR catch (reimplemented)."""
    def __init__(self, plant, k=None):
        self.p = plant; self.K = lqr_gain(plant)[0]; self.mode = "swing"
        self.k = k if k is not None else (1.0 if plant.name == "pendulum" else 5.0)
    def act(self, x):
        p = self.p
        th = wrap(x[0] if p.name == "pendulum" else x[1])
        near = abs(th) < 0.35 and abs(p.energy(x) - p.Estar) < 0.25 * abs(p.Estar)
        if near: self.mode = "lqr"
        if self.mode == "lqr" and abs(th) > 0.8: self.mode = "swing"
        if self.mode == "lqr":
            xe = p.err(x); return float(np.clip(-self.K @ xe, -p.umax, p.umax))
        dE = p.energy(x) - p.Estar
        if p.name == "pendulum":
            w = x[1]
            if abs(w) < 0.05: w = 0.05 if th >= 0 else -0.05  # kick off the rest point
            return float(np.clip(-self.k * dE * w, -p.umax, p.umax))
        w = x[3]
        if abs(w) < 0.05: w = 0.05 if th >= 0 else -0.05
        ades = -self.k * (p.Estar - dE * 0 - p.energy(x)) * w * np.cos(th) * 1.0
        ades = np.clip(ades, -8.0, 8.0) - 1.0 * x[0] - 1.5 * x[2]
        s = np.sin(x[1]); mc, mp, l = p.mc, p.mp, p.l
        F = ades * (mc + mp * s ** 2) - mp * l * x[3] ** 2 * s + mp * G * s * np.cos(x[1])
        return float(np.clip(F, -p.umax, p.umax))

# ------------------------------------------------------------------ evaluation
def make_controller(system, plant, a):
    if system == "EnergyShaping-LQR": return EnergyShaping(plant)
    kind = {"iLQR-Quad": "quad", "iLQR-Energy": "energy", "iLQR-Quad+Energy": "both"}[system]
    cost = Cost(plant, kind, wE=a.wE, qscale=a.qscale, rscale=a.rscale, q_in_energy=a.q_in_energy)
    return MPC(plant, cost, a.horizon)

def episode(plant, ctrl, x0, tsim=TSIM, diag=None):
    x = x0.copy(); n = int(tsim / DT); effort = 0.0; ok_run = 0; t_up = None; solve = []
    inbound = True
    for i in range(n):
        if diag is not None:  # closed-loop size of the two state-cost terms at default weights (not used by the controller)
            e = plant.err(x); diag[0].append(0.5 * (plant.energy(x) - plant.Estar) ** 2); diag[1].append(0.5 * e @ (plant.q * e))
        t0 = time.perf_counter(); u = float(np.clip(ctrl.act(x), -plant.umax, plant.umax)); solve.append(time.perf_counter() - t0)
        effort += u ** 2 * DT
        x = step(plant, x, u)
        if plant.xlim and abs(x[0]) > plant.xlim: inbound = False
        if not np.all(np.isfinite(x)): inbound = False; break
        if plant.upright(x):
            ok_run += 1
            if ok_run * DT >= 1.0 and t_up is None: t_up = (i + 1) * DT - 1.0  # first time of a 1 s upright hold
        else:
            ok_run = 0; t_up = None
    final_ok = inbound and plant.upright(x) and ok_run * DT >= 1.0
    return final_ok, effort, (t_up if final_ok else None), np.mean(solve)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True); ap.add_argument("--task", required=True)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out", required=True)
    ap.add_argument("--nep", type=int, default=20); ap.add_argument("--horizon", type=int, default=30)
    ap.add_argument("--wE", type=float, default=1.0); ap.add_argument("--qscale", type=float, default=1.0)
    ap.add_argument("--rscale", type=float, default=1.0); ap.add_argument("--q_in_energy", type=float, default=0.0)
    ap.add_argument("--diag", action="store_true", help="also report closed-loop means of the energy and quadratic state-cost terms")
    a = ap.parse_args()
    print("config:", vars(a))
    plant = Pendulum() if a.task == "pendulum" else CartPole()
    rng = np.random.default_rng(a.seed)
    X0 = [plant.sample(rng) for _ in range(a.nep)]
    succ, eff, tup, st, far = [], [], [], [], []
    diag = ([], []) if a.diag else None
    for x0 in X0:
        ctrl = make_controller(a.system, plant, a)
        ok, e, t, s = episode(plant, ctrl, x0, diag=diag)
        succ.append(ok); eff.append(e); tup.append(t if ok else TSIM); st.append(s)
        th0 = x0[0] if a.task == "pendulum" else x0[1]
        if abs(wrap(th0)) > np.pi / 2: far.append(ok)
    out = {"success_rate": float(np.mean(succ)),
           "success_rate_far": float(np.mean(far)) if far else float("nan"),
           "control_effort": float(np.mean(eff)),
           "time_to_upright": float(np.mean(tup)),
           "solve_ms": float(np.mean(st) * 1e3)}
    if a.diag:  # unit-weight terms: 0.5 (E-E*)^2 and 0.5 e'Qe, mean over all closed-loop steps
        out["energy_term"] = float(np.mean(diag[0])); out["quad_term"] = float(np.mean(diag[1]))
        out["term_ratio"] = out["energy_term"] / out["quad_term"]
    json.dump(out, open(a.out, "w")); print(out)

if __name__ == "__main__":
    main()
