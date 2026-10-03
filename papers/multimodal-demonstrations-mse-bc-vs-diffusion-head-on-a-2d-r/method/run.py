"""Bimodal 2D reach: MSE-MLP vs Gaussian-mixture head vs DDPM action head (all reimplemented)."""
import argparse, json, math, time
import numpy as np, torch, torch.nn as nn

torch.set_num_threads(2)
GOAL = np.array([1.0, 0.0]); OBS_C = np.array([0.5, 0.0]); OBS_R = 0.15
WAY_X, WAY_Y = 0.5, 0.35
VMAX = 0.05; GOAL_R = 0.05; T_MAX = 40
TASKS = {  # P(right mode) in demonstrations, start jitter half-width
    "bimodal50": dict(p_upper=0.5),
    "bimodal80": dict(p_upper=0.8),
    "unimodal": dict(p_upper=1.0),
}

def clip_norm(a, m=VMAX):
    n = np.linalg.norm(a, axis=-1, keepdims=True)
    return a * np.minimum(1.0, m / np.maximum(n, 1e-9))

def gen_demos(n, p_upper, rng, jit):
    """Scripted expert: go to waypoint (0.5, +-0.35) then to goal. Returns obs (N,2), act (N,2), traj index, step index."""
    O, A, I, S = [], [], [], []
    for i in range(n):
        pos = rng.uniform(-jit, jit, 2)
        sgn = 1.0 if rng.random() < p_upper else -1.0
        way = np.array([WAY_X, sgn * WAY_Y]) + rng.normal(0, 0.02, 2)
        phase = 0
        for t in range(T_MAX):
            tgt = way if phase == 0 else GOAL
            a = clip_norm(tgt - pos) + rng.normal(0, 0.003, 2)
            O.append(pos.copy()); A.append(a); I.append(i); S.append(t)
            pos = pos + a
            if phase == 0 and np.linalg.norm(way - pos) < 0.05: phase = 1
            if np.linalg.norm(pos - GOAL) < GOAL_R: break
    return np.array(O, np.float32), np.array(A, np.float32), np.array(I), np.array(S)

def make_chunks(O, A, I, K):
    """Chunk target for step t = actions t..t+K-1 of the same demo (repeat the last action as padding)."""
    N = len(O); out = np.zeros((N, K, 2), np.float32)
    for j in range(N):
        for k in range(K):
            jj = j + k
            if jj >= N or I[jj] != I[j]:
                jj = j + k - 1
                while jj >= N or I[jj] != I[j]: jj -= 1
            out[j, k] = A[jj]
    return out.reshape(N, K * 2)

def mlp(i, o, w, depth=3):
    L, d = [], i
    for _ in range(depth): L += [nn.Linear(d, w), nn.ReLU()]; d = w
    return nn.Sequential(*L, nn.Linear(d, o))

class MSEPolicy(nn.Module):
    def __init__(s, D, w): super().__init__(); s.net = mlp(2, D, w)
    def loss(s, o, a): return ((s.net(o) - a) ** 2).mean()
    @torch.no_grad()
    def act(s, o, gen): return s.net(o)

class GMMPolicy(nn.Module):
    def __init__(s, D, w, M): super().__init__(); s.D, s.M = D, M; s.net = mlp(2, M * (1 + 2 * D), w)
    def params(s, o):
        x = s.net(o); M, D = s.M, s.D
        logit = x[:, :M]; mu = x[:, M:M + M * D].view(-1, M, D)
        logsig = x[:, M + M * D:].view(-1, M, D).clamp(-6, 2)
        return logit, mu, logsig
    def loss(s, o, a):
        logit, mu, logsig = s.params(o)
        lp = (-0.5 * ((a[:, None] - mu) / logsig.exp()) ** 2 - logsig - 0.5 * math.log(2 * math.pi)).sum(-1)
        return -(torch.logsumexp(torch.log_softmax(logit, -1) + lp, -1)).mean()
    @torch.no_grad()
    def act(s, o, gen):
        logit, mu, logsig = s.params(o)
        k = torch.multinomial(torch.softmax(logit, -1), 1, generator=gen).squeeze(1)
        r = torch.arange(len(o))
        return mu[r, k] + logsig[r, k].exp() * torch.randn(mu[r, k].shape, generator=gen)

class DDPMPolicy(nn.Module):
    """eps-prediction DDPM over the (normalised) action chunk, conditioned on obs; cosine schedule, ancestral sampling."""
    def __init__(s, D, w, n_steps):
        super().__init__(); s.D, s.N = D, n_steps
        s.net = mlp(2 + D + 16, D, w, depth=4)
        t = torch.arange(n_steps + 1) / n_steps
        ab = torch.cos((t + 0.008) / 1.008 * math.pi / 2) ** 2; ab = ab / ab[0]
        beta = (1 - ab[1:] / ab[:-1]).clamp(max=0.999)
        s.register_buffer("beta", beta); s.register_buffer("alpha", 1 - beta)
        s.register_buffer("abar", torch.cumprod(1 - beta, 0))
    def temb(s, k):
        f = torch.exp(-math.log(1000) * torch.arange(8) / 8)
        e = (k.float()[:, None] + 1) * f[None]
        return torch.cat([e.sin(), e.cos()], -1)
    def eps(s, o, x, k): return s.net(torch.cat([o, x, s.temb(k)], -1))
    def loss(s, o, a):
        k = torch.randint(0, s.N, (len(o),)); e = torch.randn_like(a)
        ab = s.abar[k][:, None]
        return ((s.eps(o, ab.sqrt() * a + (1 - ab).sqrt() * e, k) - e) ** 2).mean()
    @torch.no_grad()
    def act(s, o, gen):
        x = torch.randn(len(o), s.D, generator=gen)
        for k in reversed(range(s.N)):
            kk = torch.full((len(o),), k)
            e = s.eps(o, x, kk)
            x = (x - s.beta[k] / (1 - s.abar[k]).sqrt() * e) / s.alpha[k].sqrt()
            if k > 0:
                var = s.beta[k] * (1 - s.abar[k - 1]) / (1 - s.abar[k])  # posterior variance
                x = x + var.sqrt() * torch.randn(x.shape, generator=gen)
        return x.clamp(-5, 5)

def rollout(policy, K, a_mu, a_sd, o_mu, o_sd, n, seed, gen, jit):
    rng = np.random.default_rng(seed)
    pos = rng.uniform(-jit, jit, (n, 2))
    alive = np.ones(n, bool); succ = np.zeros(n, bool); coll = np.zeros(n, bool)
    side = np.zeros(n)  # sign of y when first crossing x=OBS_X
    t = 0
    while t < T_MAX and alive.any():
        o = torch.tensor((pos - o_mu) / o_sd, dtype=torch.float32)
        a = policy.act(o, gen).numpy() * a_sd + a_mu
        a = a.reshape(n, K, 2)
        for k in range(K):
            if t >= T_MAX: break
            step = clip_norm(a[:, k]) * alive[:, None]
            new = pos + step
            crossed = alive & (pos[:, 0] < OBS_C[0]) & (new[:, 0] >= OBS_C[0])
            side[crossed] = np.sign(new[crossed, 1] + 1e-12)
            # collision check on the segment (sampled points)
            hit = np.zeros(n, bool)
            for f in (0.25, 0.5, 0.75, 1.0):
                q = pos + f * step
                hit |= np.linalg.norm(q - OBS_C, axis=1) < OBS_R
            coll |= alive & hit
            pos = new
            reach = alive & ~hit & (np.linalg.norm(pos - GOAL, axis=1) < GOAL_R)
            succ |= reach
            alive &= ~(hit | reach)
            t += 1
    return succ, coll, side

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True, choices=["mse", "gmm", "ddpm"])
    ap.add_argument("--task", default="bimodal50")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--jit", type=float, default=0.01)
    ap.add_argument("--n_demos", type=int, default=2000)
    ap.add_argument("--chunk", type=int, default=1)
    ap.add_argument("--n_comp", type=int, default=2)
    ap.add_argument("--n_steps", type=int, default=50)
    ap.add_argument("--width", type=int, default=128)
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--n_rollouts", type=int, default=200)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    print("config:", json.dumps(vars(a)), flush=True)
    t0 = time.time()
    torch.manual_seed(a.seed); np.random.seed(a.seed)
    rng = np.random.default_rng(a.seed)
    O, A, I, S = gen_demos(a.n_demos, TASKS[a.task]["p_upper"], rng, a.jit)
    K = a.chunk; D = 2 * K
    Y = make_chunks(O, A, I, K)
    o_mu, o_sd = O.mean(0), O.std(0) + 1e-6
    a_mu, a_sd = np.tile(A.mean(0), K), np.tile(A.std(0) + 1e-6, K)
    X = torch.tensor((O - o_mu) / o_sd); Yt = torch.tensor((Y - a_mu) / a_sd)
    if a.system == "mse": pol = MSEPolicy(D, a.width)
    elif a.system == "gmm": pol = GMMPolicy(D, a.width, a.n_comp)
    else: pol = DDPMPolicy(D, a.width, a.n_steps)
    opt = torch.optim.Adam(pol.parameters(), lr=a.lr)
    steps = a.epochs * math.ceil(len(X) / a.batch)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps)
    for ep in range(a.epochs):
        perm = torch.randperm(len(X)); tot = 0.0
        for i in range(0, len(X), a.batch):
            b = perm[i:i + a.batch]
            l = pol.loss(X[b], Yt[b]); opt.zero_grad(); l.backward(); opt.step(); sched.step(); tot += l.item() * len(b)
        if ep % 10 == 9: print(f"epoch {ep+1} train_loss {tot/len(X):.4f}", flush=True)
    pol.eval()
    gen = torch.Generator().manual_seed(a.seed + 1000)
    succ, coll, side = rollout(pol, K, a_mu, a_sd, o_mu, o_sd, a.n_rollouts, a.seed + 2000, gen, a.jit)
    n = a.n_rollouts
    U = float((succ & (side > 0)).sum()) / n  # y>0 side
    R = float((succ & (side < 0)).sum()) / n  # y<0 side
    m = {"success": float(succ.mean()), "collision": float(coll.mean()),
         "upper_share": U, "lower_share": R,
         "mode_balance": (1 - abs(U - R) / (U + R)) if (U + R) > 0 else 0.0,
         "upper_frac": (U / (U + R)) if (U + R) > 0 else 0.0,  # share of successful rollouts via y>0 mode
         "demo_upper_share": float(TASKS[a.task]["p_upper"])}
    json.dump(m, open(a.out, "w"))
    print("metrics:", json.dumps(m), f"(wall {time.time()-t0:.0f}s)", flush=True)

if __name__ == "__main__": main()
