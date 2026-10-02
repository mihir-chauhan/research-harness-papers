"""Tabular Q-learning, Dyna-Q, Dyna-Q+ and prioritized sweeping on changing / stochastic gridworlds."""
import argparse, heapq, json, math, os, random, time
import numpy as np

H, W = 6, 9
START, GOAL = (5, 3), (0, 8)
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]
NA = 4

# task -> (horizon, change_step, slip, walls_before, walls_after)
def wall(cols): return {(2, c) for c in cols}
TASKS = {
    "blocking": dict(T=3000, change=1000, slip=0.0, w0=wall(range(0, 8)), w1=wall(range(1, 9))),
    "shortcut": dict(T=6000, change=3000, slip=0.0, w0=wall(range(1, 9)), w1=wall(range(1, 8))),
    "stochastic": dict(T=3000, change=None, slip=0.3, w0=wall(range(0, 8)), w1=None),
    "static": dict(T=3000, change=None, slip=0.0, w0=wall(range(0, 8)), w1=None),
    # stochastic AND changing: the model is wrong from two sources at once
    "stoch_blocking": dict(T=3000, change=1000, slip=0.3, w0=wall(range(0, 8)), w1=wall(range(1, 9))),
}

class Maze:
    def __init__(self, cfg, rng):
        self.cfg, self.rng = cfg, rng
        self.walls = cfg["w0"]; self.pos = START
    def reset(self): self.pos = START; return self.pos[0] * W + self.pos[1]
    def switch(self): self.walls = self.cfg["w1"]
    def step(self, a):
        if self.cfg["slip"] > 0 and self.rng.random() < self.cfg["slip"]:
            a = self.rng.randrange(NA)
        r, c = self.pos; dr, dc = MOVES[a]
        nr, nc = r + dr, c + dc
        if 0 <= nr < H and 0 <= nc < W and (nr, nc) not in self.walls: self.pos = (nr, nc)
        done = self.pos == GOAL
        return self.pos[0] * W + self.pos[1], (1.0 if done else 0.0), done

def run(system, task, seed, n_plan, alpha, gamma, eps, kappa, theta, untried, no_bonus_in_action):
    cfg = TASKS[task]
    rng = random.Random(seed)
    env = Maze(cfg, rng)
    NS = H * W
    Q = [[0.0] * NA for _ in range(NS)]
    model = {}            # (s,a) -> (r, s', done)
    last = {}             # (s,a) -> last real time tried
    seen_sa = []          # list for uniform sampling
    seen_states = set()
    preds = {}            # s' -> set of (s,a) (for prioritized sweeping)
    pq = []               # heap of (-priority, s, a)
    plus = system == "dynaq+"
    greedy_tie = lambda qs: rng.choice([i for i, q in enumerate(qs) if q == max(qs)])

    def push(s, a, p):
        if p > theta: heapq.heappush(pq, (-p, s, a))

    def target(s, a, r, s2, done, t_bonus=0.0):
        return r + t_bonus + (0.0 if done else gamma * max(Q[s2]))

    s = env.reset(); rewards = np.zeros(cfg["T"])
    steps_per_ep = []; ep_len = 0
    for t in range(cfg["T"]):
        if cfg["change"] is not None and t == cfg["change"]: env.switch()
        a = rng.randrange(NA) if rng.random() < eps else greedy_tie(Q[s])
        s2, r, done = env.step(a)
        rewards[t] = r; ep_len += 1
        # direct RL update
        if system == "ps":
            p = abs(target(s, a, r, s2, done) - Q[s][a])
        Q[s][a] += alpha * (target(s, a, r, s2, done) - Q[s][a])
        if system != "q":
            if (s, a) not in model: seen_sa.append((s, a))
            model[(s, a)] = (r, s2, done); last[(s, a)] = t + 1
            if plus and untried and s not in seen_states:
                for b in range(NA):
                    if b != a and (s, b) not in model:
                        model[(s, b)] = (0.0, s, False); last[(s, b)] = 0; seen_sa.append((s, b))
            seen_states.add(s)
            if system == "ps":
                preds.setdefault(s2, set()).add((s, a)); push(s, a, p)
            for _ in range(n_plan):
                if system == "ps":
                    if not pq: break
                    _, ps_, pa = heapq.heappop(pq)
                    pr, pn, pd = model[(ps_, pa)]
                    Q[ps_][pa] += alpha * (target(ps_, pa, pr, pn, pd) - Q[ps_][pa])
                    for (qs, qa) in preds.get(ps_, ()):
                        qr, qn, qd = model[(qs, qa)]
                        push(qs, qa, abs(target(qs, qa, qr, qn, qd) - Q[qs][qa]))
                else:
                    ps_, pa = rng.choice(seen_sa)
                    pr, pn, pd = model[(ps_, pa)]
                    bonus = kappa * math.sqrt(t + 1 - last[(ps_, pa)]) if plus else 0.0
                    Q[ps_][pa] += alpha * (target(ps_, pa, pr, pn, pd, bonus) - Q[ps_][pa])
        s = s2
        if done:
            steps_per_ep.append(ep_len); ep_len = 0; s = env.reset()
    cum = np.cumsum(rewards)
    ch = cfg["change"] if cfg["change"] is not None else cfg["T"] // 2
    first = np.argmax(rewards > 0) + 1 if rewards.any() else cfg["T"]
    # steps needed to finish first episode(s) after change, measured as reward gained in the 500 steps after change
    return rewards, dict(
        cum_reward=float(cum[-1]),
        pre_reward=float(cum[ch - 1]),
        post_reward=float(cum[-1] - cum[ch - 1]),
        late_reward=float(cum[-1] - cum[-min(500, cfg["T"]) - 1]),
        first_goal_step=float(first),
        early_reward=float(cum[min(500, cfg["T"]) - 1]),
    )

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True, choices=["q", "dynaq", "dynaq+", "ps"])
    ap.add_argument("--task", required=True, choices=list(TASKS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--alpha", type=float, default=0.5)
    ap.add_argument("--gamma", type=float, default=0.95)
    ap.add_argument("--eps", type=float, default=0.1)
    ap.add_argument("--kappa", type=float, default=1e-3)
    ap.add_argument("--theta", type=float, default=1e-4)
    ap.add_argument("--untried", type=int, default=1)
    ap.add_argument("--out", required=True)
    ap.add_argument("--curve", default="")
    a = ap.parse_args()
    t0 = time.time()
    rewards, m = run(a.system, a.task, a.seed, a.n, a.alpha, a.gamma, a.eps, a.kappa, a.theta, a.untried, 0)
    m["runtime_s"] = time.time() - t0
    json.dump(m, open(a.out, "w"))
    if a.curve:
        cum = np.cumsum(rewards)
        with open(a.curve, "w") as f:
            f.write("step,value,seed,name\n")
            for i in range(0, len(cum), 25):
                f.write(f"{i+1},{cum[i]},{a.seed},{a.curve.split('/')[-1].split('__')[1]}\n")
