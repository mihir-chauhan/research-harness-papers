"""VMC for the periodic 1D TFIM H = -J sum s^z_i s^z_{i+1} - G sum s^x_i (J=1) with
mean-field, Jastrow and RBM wavefunctions, optimised by plain SGD or stochastic reconfiguration.
Real positive amplitudes (the TFIM ground state is nodeless). Pure numpy."""
import argparse, json, re, time
import numpy as np

J = 1.0


class Model:
    def __init__(self, kind, N, alpha, rng, init=0.01):
        self.kind, self.N = kind, N
        if kind == "mf":      # psi = exp(sum a_i s_i)
            self.shapes = [(N,)]
        elif kind == "jastrow":  # psi = exp(sum a_i s_i + sum_{i<j} J_ij s_i s_j)
            self.shapes = [(N,), (N * (N - 1) // 2,)]   # one J_ij per pair i<j
        else:                 # rbm: psi = exp(a.s) prod_j 2cosh(b_j + W_j.s)
            self.H = int(round(alpha * N))
            self.shapes = [(N,), (self.H,), (self.H, N)]
        self.sizes = [int(np.prod(s)) for s in self.shapes]
        self.p = rng.normal(0, init, sum(self.sizes))

    def unpack(self):
        out, k = [], 0
        for s, n in zip(self.shapes, self.sizes):
            out.append(self.p[k:k + n].reshape(s)); k += n
        return out

    def _jmat(self, Jp):  # symmetric N x N coupling matrix with zero diagonal from the pair parameters
        U = np.zeros((self.N, self.N)); U[np.triu_indices(self.N, 1)] = Jp
        return U + U.T

    def logpsi(self, S):
        P = self.unpack()
        if self.kind == "mf":
            return S @ P[0]
        if self.kind == "jastrow":
            Jm = self._jmat(P[1])
            return S @ P[0] + 0.5 * np.einsum("mi,mi->m", S @ Jm, S)
        a, b, W = P
        th = b + S @ W.T
        return S @ a + np.sum(np.logaddexp(th, -th), axis=1)

    def flips(self, S):
        """log psi(flip_i s) - log psi(s), shape (M,N)."""
        P = self.unpack()
        if self.kind == "mf":
            return -2 * S * P[0]
        if self.kind == "jastrow":
            Jm = self._jmat(P[1])
            return -2 * S * (P[0] + S @ Jm)
        a, b, W = P
        th = b + S @ W.T                                   # (M,H)
        thf = th[:, None, :] - 2 * S[:, :, None] * W.T[None]  # (M,N,H)
        lc = lambda x: np.logaddexp(x, -x)
        return -2 * S * a + np.sum(lc(thf) - lc(th)[:, None, :], axis=2)

    def grad(self, S):
        """O_k = d log psi / d p_k, shape (M,P)."""
        M, N = S.shape
        if self.kind == "mf":
            return S.copy()
        if self.kind == "jastrow":
            iu = np.triu_indices(N, 1)
            return np.concatenate([S, S[:, iu[0]] * S[:, iu[1]]], axis=1)
        a, b, W = self.unpack()
        t = np.tanh(b + S @ W.T)
        return np.concatenate([S, t, (t[:, :, None] * S[:, None, :]).reshape(M, -1)], axis=1)


def eloc(model, S, G):
    diag = -J * np.sum(S * np.roll(S, -1, axis=1), axis=1)
    return diag - G * np.sum(np.exp(model.flips(S)), axis=1)


def metropolis(model, S, lp, rng, steps):
    M, N = S.shape
    for _ in range(steps):
        Sn = S.copy()
        glob = rng.random(M) < 0.1     # 10% global spin flips, 90% single-site flips
        site = rng.integers(0, N, M)
        Sn[np.arange(M), site] *= -1
        Sn[glob] = -S[glob]
        lpn = model.logpsi(Sn)
        acc = np.log(rng.random(M)) < 2 * (lpn - lp)
        S[acc] = Sn[acc]; lp[acc] = lpn[acc]
    return S, lp


def tfim_exact(N, G):
    """Sparse-free ED in the sigma^z basis; returns E0, psi0 (index bit i set => s_i=+1)."""
    import scipy.sparse as sp
    from scipy.sparse.linalg import eigsh
    D = 2 ** N
    idx = np.arange(D)
    Sall = ((idx[:, None] >> np.arange(N)) & 1) * 2.0 - 1
    H = sp.diags(-J * np.sum(Sall * np.roll(Sall, -1, axis=1), axis=1)).tocsr()
    for i in range(N):
        H = H + sp.csr_matrix((-G * np.ones(D), (idx, idx ^ (1 << i))), shape=(D, D))
    w, v = eigsh(H, k=1, which="SA", tol=1e-12)
    return w[0], np.abs(v[:, 0]), Sall, H


def enum_obs(model, Sall, psi0, N, G):
    """Exact (sum over all 2^N configs) observables of the variational state."""
    lp = model.logpsi(Sall)
    p = np.exp(lp - lp.max()); p /= np.sqrt(np.sum(p ** 2))
    w = p ** 2
    E = np.sum(w * eloc(model, Sall, G))
    mz = np.sum(w * np.abs(Sall.mean(1)))
    mx = np.sum(w * np.exp(model.flips(Sall)).mean(1))
    fid = np.sum(p * psi0) ** 2
    return E, mz, mx, fid


def exact_opt(model, Sall, psi0, E0, mz0, mx0, N, G, maxiter):
    """Reference without sampling: minimise the exactly enumerated energy E(theta) with L-BFGS, using the exact
    gradient 2 sum_s p(s) (E_loc(s) - E) O(s). Gives an upper bound on the best energy the ansatz can reach."""
    from scipy.optimize import minimize

    def fg(p):
        model.p = p
        lp = model.logpsi(Sall)
        w = np.exp(2 * (lp - lp.max())); w /= w.sum()
        with np.errstate(over="ignore", invalid="ignore"):
            El = eloc(model, Sall, G)
            E = np.sum(w * El)
            g = 2 * (w * (El - E)) @ model.grad(Sall)
        if not (np.isfinite(E) and np.all(np.isfinite(g))):
            return 1e10, np.zeros_like(p)
        return E, g

    r = minimize(fg, model.p.copy(), jac=True, method="L-BFGS-B",
                 options={"maxiter": maxiter, "maxfun": 2 * maxiter, "ftol": 1e-15, "gtol": 1e-9})
    model.p = r.x
    E, mz, mx, fid = enum_obs(model, Sall, psi0, N, G)
    return {"energy": float(E), "rel_energy_error": float((E - E0) / abs(E0)), "mz_error": float(abs(mz - mz0)),
            "mx_error": float(abs(mx - mx0)), "infidelity": float(1 - fid), "n_params": int(len(model.p)),
            "lbfgs_iters": int(r.nit), "lbfgs_evals": int(r.nfev)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ansatz", required=True, choices=["mf", "jastrow", "rbm"])
    ap.add_argument("--alpha", type=float, default=1.0)
    ap.add_argument("--opt", required=True, choices=["sgd", "sr", "exact"],
                    help="sgd / sr: VMC; exact: sampling-free L-BFGS on the exactly enumerated energy (reference only)")
    ap.add_argument("--exact-maxiter", type=int, default=1000)
    ap.add_argument("--task", default="", help="tfim_N<N>_g<G>, overrides --N/--G")
    ap.add_argument("--N", type=int, default=10)
    ap.add_argument("--G", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--lr", type=float, default=0.05)
    ap.add_argument("--shift", type=float, default=1e-2)
    ap.add_argument("--samples", type=int, default=256)
    ap.add_argument("--iters", type=int, default=300)
    ap.add_argument("--init", type=float, default=0.01)
    ap.add_argument("--field-init", type=float, default=0.0,
                    help="constant added to the initial visible fields a_i (0: symmetric start, >0: symmetry-broken start)")
    ap.add_argument("--curve", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.task:
        m = re.fullmatch(r"tfim_N(\d+)_g([0-9.]+)", a.task)
        a.N, a.G = int(m.group(1)), float(m.group(2))
    print("config:", json.dumps(vars(a)), flush=True)
    t0 = time.time()
    rng = np.random.default_rng(1000 * a.seed + a.N)
    N, G = a.N, a.G
    E0, psi0, Sall, _ = tfim_exact(N, G)
    mz0 = float(np.sum(psi0 ** 2 * np.abs(Sall.mean(1))))
    ix = np.arange(2 ** N)
    mx0 = float(sum(np.sum(psi0 * psi0[ix ^ (1 << i)]) for i in range(N)) / N)
    model = Model(a.ansatz, N, a.alpha, rng, init=a.init)
    if a.field_init:
        model.p[:N] += a.field_init                     # a_i are the first N parameters of every ansatz
    if a.opt == "exact":
        res = exact_opt(model, Sall, psi0, E0, mz0, mx0, N, G, a.exact_maxiter)
        res["runtime_s"] = float(time.time() - t0)
        print("exact E0 %.6f  Mz0 %.4f Mx0 %.4f" % (E0, mz0, mx0))
        print("metrics:", json.dumps(res), flush=True)
        json.dump(res, open(a.out, "w"))
        return
    S = rng.choice([-1.0, 1.0], size=(a.samples, N))
    lp = model.logpsi(S)
    S, lp = metropolis(model, S, lp, rng, 10 * N)       # burn-in
    rows, Emc = [], []
    for it in range(a.iters):
        S, lp = metropolis(model, S, lp, rng, N)          # N steps between samples
        El = eloc(model, S, G)
        O = model.grad(S)
        Ec = El - El.mean(); Oc = O - O.mean(0)
        g = 2 * Oc.T @ Ec / len(El)
        if a.opt == "sgd":
            step = g
        else:
            Smat = Oc.T @ Oc / len(El)
            step = np.linalg.solve(Smat + a.shift * np.eye(len(g)), g)
        model.p = model.p - a.lr * step
        lp = model.logpsi(S)
        Emc.append(El.mean())
        if a.curve:
            rows.append((it, (El.mean() - E0) / abs(E0)))
    if a.curve:
        with open(a.curve, "w") as f:
            f.write("step,value,seed,name\n")
            for it, v in rows:
                f.write(f"{it},{v},{a.seed},{a.ansatz}{a.alpha:g}-{a.opt}\n")
    E, mz, mx, fid = enum_obs(model, Sall, psi0, N, G)
    res = {
        "energy": float(E),
        "rel_energy_error": float((E - E0) / abs(E0)),
        "mz_error": float(abs(mz - mz0)),
        "mx_error": float(abs(mx - mx0)),
        "infidelity": float(1 - fid),
        "mc_energy_error": float((np.mean(Emc[-20:]) - E0) / abs(E0)),
        "n_params": int(len(model.p)),
        "runtime_s": float(time.time() - t0),
    }
    print("exact E0 %.6f  Mz0 %.4f Mx0 %.4f" % (E0, mz0, mx0))
    print("metrics:", json.dumps(res), flush=True)
    json.dump(res, open(a.out, "w"))


if __name__ == "__main__":
    main()
