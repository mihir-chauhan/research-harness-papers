"""Tabular overestimation study: Q-learning vs double-Q family, vectorised over R independent runs.

Usage: python method/run.py --system q|double|wdq|maxmin|double_both --task maxbias|random20 --seed S --out F.json
Every one of the R replicas has its own tables, its own random MDP (random20) and its own noise.
"""
import argparse, json, os
import numpy as np

SYSTEMS = ["q", "double", "wdq", "maxmin", "double_both"]


class Task:
    """Batched episodic MDP. States 0..S-1 (+ terminal index S). Action mask valid[s,a]."""

    def __init__(self, name, R, rng, a):
        self.name, self.R = name, R
        if name == "maxbias":
            # Sutton & Barto Ex. 6.7: A=0 (start), B=1, terminal=2. A: right(0)->T r=0, left(1)->B r=0.
            # B: n actions, r ~ N(mu, sigma^2), then terminal. V*(A)=0 (right), Q(A,left)=mu<0.
            self.S, self.A, self.gamma, self.H = 2, max(2, a.n_actions), 1.0, 2
            self.valid = np.zeros((2, self.A), bool)
            self.valid[0, :2] = True
            self.valid[1, :a.n_actions] = True
            self.mu, self.sigma = a.mu, a.sigma
            self.Vstar = np.tile(np.array([0.0, a.mu]), (R, 1))
            self.Qstar_A = np.array([0.0, a.mu])
            self.decision = np.array([True, False])  # states with a unique optimal action
            self.optact = np.zeros((R, 2), int)       # optimal action at A is 0 (right)
            self.optact[:, 1] = 0
        else:
            S, A, K = a.n_states, a.n_actions, a.branch
            self.S, self.A, self.gamma, self.H = S, A, a.gamma, a.horizon
            self.valid = np.ones((S, A), bool)
            self.sigma = a.sigma
            # K distinct random successors per (s,a), Dirichlet(1) probabilities, mean reward N(0,1)
            self.succ = np.argsort(rng.random((R, S, A, S)), axis=-1)[..., :K]
            w = rng.gamma(1.0, size=(R, S, A, K))
            self.prob = w / w.sum(-1, keepdims=True)
            self.cum = np.cumsum(self.prob, -1)
            self.rmean = rng.normal(size=(R, S, A))
            # true Q*, V* by value iteration (per replica)
            P = np.zeros((R, S, A, S))
            np.put_along_axis(P, self.succ, self.prob, axis=-1)
            Q = np.zeros((R, S, A))
            for _ in range(600):
                Q = self.rmean + self.gamma * np.einsum('rsat,rt->rsa', P, Q.max(-1))
            self.Qstar = Q
            self.Vstar = Q.max(-1)
            self.optact = Q.argmax(-1)
            gap = np.sort(Q, -1)
            self.mean_gap = float((gap[..., -1] - gap[..., -2]).mean())
            self.decision = np.ones(S, bool)

    def step(self, s, a, rng):
        R = self.R
        idx = np.arange(R)
        if self.name == "maxbias":
            noise = rng.normal(self.mu, self.sigma, R)
            at_A = s == 0
            r = np.where(at_A, 0.0, noise)
            s2 = np.where(at_A & (a == 1), 1, 0)
            done = ~(at_A & (a == 1))
            return s2, r, done
        u = rng.random(R)
        k = (u[:, None] > self.cum[idx, s, a]).sum(-1).clip(max=self.succ.shape[-1] - 1)
        s2 = self.succ[idx, s, a, k]
        r = self.rmean[idx, s, a] + rng.normal(0.0, self.sigma, R)
        return s2, r, np.zeros(R, bool)


def run(a):
    rng = np.random.default_rng(a.seed)
    R = a.runs
    T = Task(a.task, R, rng, a)
    K = 1 if a.system == "q" else a.n_est if a.system == "maxmin" else 2
    S, A, g = T.S, T.A, T.gamma
    NEG = -1e18
    Q = np.zeros((K, R, S, A))
    if a.init == "true":  # warm start at the true optimal Q (isolates steady-state estimator bias)
        if T.name == "maxbias":
            Q[:, :, 0, 0], Q[:, :, 0, 1], Q[:, :, 1, :] = 0.0, T.mu, T.mu
        else:
            Q[:] = T.Qstar
    mask = np.where(T.valid, 0.0, NEG)  # (S,A)
    idx = np.arange(R)
    alpha = a.alpha

    def behaviour(s):  # acting values for all states (s=0 placeholder) -> (R,S,A)
        return Q.min(0) if a.system == "maxmin" else Q.mean(0)

    def acting_at(s):  # acting values at the current states -> (R,A)
        q = Q[:, idx, s]
        return q.min(0) if a.system == "maxmin" else q.mean(0)

    def est(s_vals_table):  # state-value estimate used as "estimated V": max over actions of acting values
        return (s_vals_table + mask).max(-1)

    eps_curve = {k: [] for k in ["bias0", "bias_all", "subopt", "greedy0", "greedy_all"]}
    for ep in range(a.episodes):
        s = rng.integers(0, S, R) if (a.random_start and T.name == 'random20') else np.zeros(R, int)
        active = np.ones(R, bool)
        nsub = np.zeros(R)
        nact = np.zeros(R)
        for t in range(T.H):
            qa = acting_at(s) + mask[s]
            # random tie-breaking: tiny noise
            greedy = (qa + 1e-9 * rng.random(qa.shape)).argmax(-1)
            nv = T.valid[s].sum(-1)
            rand_a = (rng.random(R) * nv).astype(int)
            # map rand index to valid action index (valid actions are a prefix in both tasks)
            explore = rng.random(R) < a.epsilon
            act = np.where(explore, rand_a, greedy)
            if T.name == "maxbias":
                opt = (s == 0)  # optimal at A is action 0; B has no unique optimum
                nsub += active * (opt & (act != 0))
                nact += active * opt
            else:
                nsub += active * (act != T.optact[idx, s])
                nact += active
            s2, r, done = T.step(s, act, rng)
            term = done
            # ---- update (only for active replicas) ----
            sn = s2
            if a.system == "q":
                nxt = (Q[0, idx, sn] + mask[sn]).max(-1)
                nxt = np.where(term, 0.0, nxt)
                tgt = r + g * nxt
                cur = Q[0, idx, s, act]
                Q[0, idx, s, act] = np.where(active, cur + alpha * (tgt - cur), cur)
            elif a.system == "maxmin":
                qmin = (Q[:, idx, sn] + mask[sn]).min(0)  # (R,A) min over estimators
                nxt = np.where(term, 0.0, (qmin + mask[sn]).max(-1))
                tgt = r + g * nxt
                u = rng.integers(0, K, R)
                cur = Q[u, idx, s, act]
                Q[u, idx, s, act] = np.where(active, cur + alpha * (tgt - cur), cur)
            else:
                if a.system == "double_both":
                    us = [np.zeros(R, int), np.ones(R, int)]
                else:
                    us = [rng.integers(0, 2, R)]
                for u in us:
                    o = 1 - u
                    qu = Q[u, idx, sn] + mask[sn]
                    astar = qu.argmax(-1)
                    qo_star = Q[o, idx, sn, astar]
                    if a.system == "wdq":
                        qo = Q[o, idx, sn]
                        alow = np.where(T.valid[sn], qu, np.inf).argmin(-1)
                        d = np.abs(qo_star - Q[o, idx, sn, alow])
                        beta = d / (a.wdq_c + d)
                        nxt = beta * Q[u, idx, sn, astar] + (1 - beta) * qo_star
                    else:
                        nxt = qo_star
                    nxt = np.where(term, 0.0, nxt)
                    tgt = r + g * nxt
                    cur = Q[u, idx, s, act]
                    Q[u, idx, s, act] = np.where(active, cur + alpha * (tgt - cur), cur)
            active = active & ~term
            s = s2
            if not active.any():
                break
        # ---- per-episode measurements ----
        ev = est(behaviour(0))  # (R,S) estimated V per state, acting values
        if T.name == "maxbias":
            b0 = ev[:, 0] - T.Vstar[:, 0]
            ball = ev[:, :2] - T.Vstar
            ball = ball[:, :1]  # only A has a unique optimum; B's V* is mu (reported via bias_B below)
            g0 = ((behaviour(0)[:, 0] + mask[0]).argmax(-1) != 0).astype(float)
            gall = g0[:, None]
        else:
            b0 = ev[:, 0] - T.Vstar[:, 0]
            ball = (ev - T.Vstar).mean(-1, keepdims=True)
            ga = ((behaviour(0) + mask).argmax(-1) != T.optact)
            g0 = ga[:, 0].astype(float)
            gall = ga.mean(-1, keepdims=True)
        qa_all = behaviour(0)
        if T.name == "maxbias":
            qb = qa_all[:, 0, 1] - T.mu
        else:
            qb = (qa_all - T.Qstar).mean((-1, -2))
        eps_curve.setdefault("qbias", []).append(qb.mean())
        eps_curve["bias0"].append(b0.mean())
        eps_curve["bias_all"].append(ball.mean())
        eps_curve["subopt"].append((nsub / np.maximum(nact, 1)).mean())
        eps_curve["greedy0"].append(g0.mean())
        eps_curve["greedy_all"].append(gall.mean())
        eps_curve.setdefault("babs0", []).append(np.abs(b0).mean())
    c = {k: np.array(v) for k, v in eps_curve.items()}
    nf, n1 = a.final_window, a.first_window
    m = {
        "bias_final": c["bias0"][-nf:].mean(),
        "bias_abs_final": c["babs0"][-nf:].mean(),
        "bias_first": c["bias0"][:n1].mean(),
        "bias_peak": c["bias0"].max(),
        "qbias_final": c["qbias"][-nf:].mean(),
        "qbias_min": c["qbias"].min(),
        "bias_allstates_final": c["bias_all"][-nf:].mean(),
        "subopt_all": c["subopt"].mean(),
        "subopt_first": c["subopt"][:n1].mean(),
        "subopt_final": c["subopt"][-nf:].mean(),
        "greedy_err_final": c["greedy0"][-nf:].mean(),
        "greedy_err_allstates_final": c["greedy_all"][-nf:].mean(),
    }
    if T.name == "random20":
        m["mean_optimal_gap"] = T.mean_gap
    m = {k: float(v) for k, v in m.items()}
    return m, c


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--system", required=True, choices=SYSTEMS)
    p.add_argument("--task", required=True, choices=["maxbias", "random20"])
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", required=True)
    p.add_argument("--runs", type=int, default=1000)
    p.add_argument("--episodes", type=int, default=None)
    p.add_argument("--alpha", type=float, default=0.1)
    p.add_argument("--epsilon", type=float, default=0.1)
    p.add_argument("--n_actions", type=int, default=None)
    p.add_argument("--sigma", type=float, default=1.0)
    p.add_argument("--mu", type=float, default=-0.1)
    p.add_argument("--gamma", type=float, default=None)
    p.add_argument("--n_states", type=int, default=20)
    p.add_argument("--branch", type=int, default=3)
    p.add_argument("--horizon", type=int, default=None)
    p.add_argument("--n_est", type=int, default=2)
    p.add_argument("--wdq_c", type=float, default=1.0)
    p.add_argument("--final_window", type=int, default=20)
    p.add_argument("--first_window", type=int, default=20)
    p.add_argument("--random_start", type=int, default=None)
    p.add_argument("--init", default="zero", choices=["zero", "true"])
    p.add_argument("--curve", default="")
    a = p.parse_args()
    if a.n_actions is None:
        a.n_actions = 10 if a.task == "maxbias" else 4
    rnd = a.task == "random20"
    a.episodes = a.episodes or (1000 if rnd else 300)
    a.gamma = a.gamma if a.gamma is not None else (0.7 if rnd else 1.0)
    a.horizon = a.horizon or 25
    a.random_start = int(rnd) if a.random_start is None else a.random_start
    print("config:", json.dumps(vars(a), sort_keys=True))
    m, c = run(a)
    print("metrics:", json.dumps(m, sort_keys=True))
    with open(a.out, "w") as f:
        json.dump(m, f)
    if a.curve:
        with open(a.curve, "w") as f:
            f.write("step,value,seed,name\n")
            for i in range(a.episodes):
                f.write(f"{i+1},{c['bias0'][i]:.6f},{a.seed},{a.system}\n")
        with open(a.curve.replace("curve_", "curvesub_"), "w") as f:
            f.write("step,value,seed,name\n")
            for i in range(a.episodes):
                f.write(f"{i+1},{c['subopt'][i]:.6f},{a.seed},{a.system}\n")
