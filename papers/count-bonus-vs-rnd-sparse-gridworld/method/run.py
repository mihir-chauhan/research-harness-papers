"""Tabular Q-learning with exploration bonuses on chain / multi-room gridworlds (numpy only).

Systems: egreedy | offset_only (zero bonus, constant -offset) | count_state | count_obs | rnd | rnd_nonorm
Tasks:   chain_<N>[_tv] | room_<R>[_tv]
RND normaliser guards (flags): --warmup W (no intrinsic signal for the first W errors, b = 1) and
--clip c (b <= c). `--warmup 0 --clip 0` is the unguarded normaliser e/(sd + 1e-8) of the first version
of this study, which blows up to 1e6-1e7 when the first errors coincide (sd = 0).
"""
import argparse, json, math, time
import numpy as np

ACTIONS_GRID = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]  # up, down, left, right, stay


class Env:
    def __init__(self, task, K, rng):
        self.rng, self.K = rng, K
        self.tv = task.endswith("_tv")
        kind, size = task.replace("_tv", "").split("_")
        size = int(size)
        if kind == "chain":
            self.W, self.H, self.T = size, 1, 2 * size
            self.walls, self.goal, self.tv_cell = set(), (size - 1, 0), (1, 0)
            self.acts = [(-1, 0), (1, 0), (0, 0)]
        else:
            R = size
            self.W, self.H, self.T = 5 * R + R - 1, 5, 12 * R + 16
            doors = [2, 4, 0, 3]
            self.walls = {(5 * (i + 1) + i, y) for i in range(R - 1) for y in range(5) if y != doors[i % 4]}
            self.goal, self.tv_cell = (self.W - 1, 4), (2, 2)
            self.acts = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]
        self.cells = [(x, y) for x in range(self.W) for y in range(self.H) if (x, y) not in self.walls]
        self.idx = {c: i for i, c in enumerate(self.cells)}
        self.S, self.A = len(self.cells), len(self.acts)
        self.tv_id = self.idx[self.tv_cell] if self.tv else -1
        self.goal_id = self.idx[self.goal]

    def reset(self):
        self.pos, self.t = (0, 0), 0
        return self.idx[self.pos]

    def step(self, a):
        dx, dy = self.acts[a]
        nx, ny = self.pos[0] + dx, self.pos[1] + dy
        if 0 <= nx < self.W and 0 <= ny < self.H and (nx, ny) not in self.walls:
            self.pos = (nx, ny)
        self.t += 1
        s = self.idx[self.pos]
        tok = int(self.rng.integers(self.K)) if s == self.tv_id else -1  # TV emits a fresh random token
        done = s == self.goal_id
        return s, tok, float(done), done or self.t >= self.T


class RND:
    """Random network distillation on obs = [onehot(state), onehot(TV token)]; numpy MLP, Adam."""
    def __init__(self, dim, rng, hid=64, out=16, lr=3e-3, norm=True, warmup=64, clip=5.0):
        mk = lambda i, o: rng.normal(0, 1 / math.sqrt(i), (i, o))
        self.T1, self.T2 = mk(dim, hid), mk(hid, out) * 2.0   # fixed random target
        self.P = [mk(dim, hid), np.zeros(hid), mk(hid, out), np.zeros(out)]
        self.m = [np.zeros_like(p) for p in self.P]; self.v = [np.zeros_like(p) for p in self.P]
        self.k, self.lr, self.norm = 0, lr, norm
        self.n, self.mean, self.M2 = 0, 0.0, 0.0
        self.buf = []
        self.warmup, self.clip, self.n_clip = warmup, clip, 0

    def feat(self, S, s, tok, K):
        x = np.zeros(S + K); x[s] = 1.0
        if tok >= 0: x[S + tok] = 1.0
        return x

    def err(self, x):
        t = np.tanh(x @ self.T1) @ self.T2
        h = np.tanh(x @ self.P[0] + self.P[1]); p = h @ self.P[2] + self.P[3]
        return float(np.mean((p - t) ** 2))

    def bonus(self, x):
        e = self.err(x)
        self.buf.append(x)
        self.n += 1; d = e - self.mean; self.mean += d / self.n; self.M2 += d * (e - self.mean)
        if len(self.buf) >= 8: self.train()
        if not self.norm: return e
        if self.n <= self.warmup: return 1.0  # statistics warm up: b - offset = 0, no intrinsic signal
        sd = math.sqrt(self.M2 / self.n) if self.n > 1 else 1.0
        b = e / (sd + 1e-8)
        if self.clip > 0 and b > self.clip:
            self.n_clip += 1; b = self.clip
        return b

    def train(self):
        X = np.array(self.buf); self.buf = []
        t = np.tanh(X @ self.T1) @ self.T2
        h = np.tanh(X @ self.P[0] + self.P[1]); p = h @ self.P[2] + self.P[3]
        g = 2 * (p - t) / (X.shape[0] * t.shape[1])
        gh = (g @ self.P[2].T) * (1 - h ** 2)
        grads = [X.T @ gh, gh.sum(0), h.T @ g, g.sum(0)]
        self.k += 1
        for i, gr in enumerate(grads):
            self.m[i] = 0.9 * self.m[i] + 0.1 * gr; self.v[i] = 0.999 * self.v[i] + 0.001 * gr * gr
            self.P[i] -= self.lr * (self.m[i] / (1 - 0.9 ** self.k)) / (np.sqrt(self.v[i] / (1 - 0.999 ** self.k)) + 1e-8)


def greedy_success(env, Q):
    s = env.reset()
    for _ in range(env.T):
        s, _, r, done = env.step(int(np.argmax(Q[s])))
        if r > 0: return 1.0
        if done: break
    return 0.0


def run(a):
    rng = np.random.default_rng(a.seed)
    env = Env(a.task, a.K, rng)
    steps = a.steps or (30000 if a.task.startswith("chain") else 100000)
    Q = np.zeros((env.S, env.A))
    counts_s = np.zeros(env.S)
    counts_o = {}
    rnd = RND(env.S + a.K, rng, norm=(a.system != "rnd_nonorm"), hid=a.hid, warmup=a.warmup, clip=a.clip) if a.system.startswith("rnd") else None
    first, ep_rets, tv_steps, visited = None, [], 0, set()
    curve, bs, q_abs_max = [], [], 0.0  # bs: raw bonus per step (before the offset), for the diagnostics
    s, t_ep, ep_r = env.reset(), 0, 0.0
    for t in range(1, steps + 1):
        a_ = int(rng.integers(env.A)) if rng.random() < a.eps else int(rng.choice(np.flatnonzero(Q[s] == Q[s].max())))
        s2, tok, r, done = env.step(a_)
        if s2 == env.tv_id: tv_steps += 1
        elif s2 != env.tv_id: visited.add(s2)
        b = 0.0
        if a.system == "count_state":
            counts_s[s2] += 1; b = 1 / math.sqrt(counts_s[s2])
        elif a.system == "count_obs":
            key = (s2, tok); counts_o[key] = counts_o.get(key, 0) + 1; b = 1 / math.sqrt(counts_o[key])
        elif rnd is not None:
            b = rnd.bonus(rnd.feat(env.S, s2, tok, a.K))
        bs.append(b)
        if a.system != "egreedy": b -= a.offset  # centred bonus: untried (Q=0) beats visited, see DESIGN.md
        if r > 0 and first is None: first = t
        target = r + a.beta * b + (0.0 if r > 0 else a.gamma * Q[s2].max())
        Q[s, a_] += a.alpha * (target - Q[s, a_])
        q_abs_max = max(q_abs_max, abs(Q[s, a_]))
        ep_r += r; s = s2
        if done:
            ep_rets.append(ep_r); ep_r = 0.0; s = env.reset()
        if a.curve and t % 500 == 0:
            curve.append((t, float(np.mean(ep_rets[-20:])) if ep_rets else 0.0))
    n_last = max(1, len(ep_rets) // 5)
    n_cells = env.S - (1 if env.tv else 0)
    out = {
        "steps_to_first_reward": float(first if first is not None else steps),
        "found_reward": float(first is not None),
        "final_return": float(np.mean(ep_rets[-n_last:])) if ep_rets else 0.0,
        "greedy_success": greedy_success(env, Q),
        "tv_time_frac": tv_steps / steps,
        "coverage": len(visited) / n_cells,
        # bonus diagnostics (raw bonus b before the offset; 0 for systems without a bonus)
        "bonus_max": float(np.max(bs)),
        "bonus_max_early": float(np.max(bs[:100])),
        "bonus_median": float(np.median(bs)),
        "bonus_gt1_frac": float(np.mean(np.array(bs) > 1.0)),
        "bonus_clip_frac": (rnd.n_clip / steps) if rnd is not None else 0.0,
        "q_abs_max": float(q_abs_max),
    }
    return out, curve


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--system", required=True); p.add_argument("--task", required=True)
    p.add_argument("--seed", type=int, default=0); p.add_argument("--out", required=True)
    p.add_argument("--beta", type=float, default=0.1); p.add_argument("--eps", type=float, default=0.1)
    p.add_argument("--alpha", type=float, default=0.5); p.add_argument("--gamma", type=float, default=0.99)
    p.add_argument("--offset", type=float, default=1.0)
    p.add_argument("--K", type=int, default=16); p.add_argument("--hid", type=int, default=64)
    p.add_argument("--warmup", type=int, default=64); p.add_argument("--clip", type=float, default=5.0)
    p.add_argument("--steps", type=int, default=0); p.add_argument("--curve", default="")
    a = p.parse_args()
    t0 = time.time()
    a.curve = a.curve or ""
    print("config", json.dumps(vars(a), sort_keys=True))
    out, curve = run(a)
    json.dump(out, open(a.out, "w"))
    if a.curve:
        with open(a.curve, "w") as f:
            f.write("step,value,seed,name\n")
            for st, v in curve: f.write(f"{st},{v},{a.seed},{a.system}\n")
    print("metrics", json.dumps(out, sort_keys=True))
    print(f"runtime {time.time()-t0:.1f}s")
