"""Self-play / other-play / population training in small symmetric cooperative games.

All agents are tabular softmax policies trained with REINFORCE (batch-mean baseline, Adam).
N independent agents (or N independent populations) are trained in parallel as a tensor
dimension; evaluation of self-play and cross-play payoffs is exact (no sampling).
"""
import argparse, json, os, time
import numpy as np
import torch

torch.set_num_threads(2)


# ---------------------------------------------------------------- games
class Matrix:
    """Single-shot identical-interest matrix game R[a,b]; policy = logits over A actions."""
    kind = "matrix"

    def __init__(self, name):
        self.name = name
        if name == "lever":          # 9 symmetric levers pay 1.0, one distinct lever pays 0.9
            A = 10
            R = np.zeros((A, A)); 
            for i in range(9): R[i, i] = 1.0
            R[9, 9] = 0.9
            self.sym_idx = list(range(9))          # true symmetry: permute levers 0..8
        elif name == "safe":         # 4 symmetric levers (match -> 1), safe action 4 (0.5 if either plays it)
            A = 5
            R = np.zeros((A, A))
            for i in range(4): R[i, i] = 1.0
            R[4, :] = 0.5; R[:, 4] = 0.5
            self.sym_idx = list(range(4))
        else:
            raise ValueError(name)
        self.A = A
        self.R = torch.tensor(R, dtype=torch.float32)


class Signal:
    """Sender sees card c~prior, sends message m (M symbols); receiver sees m, guesses card g; payoff 1[g==c].
    Symmetry: relabelling of the M messages (cards are distinguishable via the non-uniform prior)."""
    kind = "signal"
    name = "signal"

    def __init__(self):
        self.prior = torch.tensor([0.4, 0.3, 0.2, 0.1])
        self.C = self.M = self.G = 4


def make_game(task):
    return Signal() if task == "signal" else Matrix(task)


# ---------------------------------------------------------------- permutations
def sample_perms(shape, n_total, sym_idx, gen):
    """Random permutations of range(n_total) that permute only sym_idx. Returns int tensor shape+(n_total,)."""
    cnt = int(np.prod(shape))
    base = torch.arange(n_total).repeat(cnt, 1)
    k = len(sym_idx)
    rnd = torch.argsort(torch.rand(cnt, k, generator=gen), dim=1)
    idx = torch.tensor(sym_idx)
    base[:, idx] = idx[rnd]
    return base.view(*shape, n_total)


# ---------------------------------------------------------------- agents
def init_params(game, N, init_std, gen):
    if game.kind == "matrix":
        return [(torch.randn(N, game.A, generator=gen) * init_std).requires_grad_()]
    return [(torch.randn(N, game.C, game.M, generator=gen) * init_std).requires_grad_(),
            (torch.randn(N, game.M, game.G, generator=gen) * init_std).requires_grad_()]


def sample(logits, gen):
    """logits [..., K] -> (action, logprob)."""
    lp = torch.log_softmax(logits, -1)
    a = torch.multinomial(lp.exp().reshape(-1, lp.shape[-1]), 1, generator=gen).reshape(lp.shape[:-1])
    return a, lp.gather(-1, a.unsqueeze(-1)).squeeze(-1)


def train_sp_or_op(game, N, steps, batch, lr, init_std, op_group, gen):
    """Self-play (op_group='none') or other-play. op_group: 'none' | 'true' | 'full'.
    Returns trained params (list of [N,...] tensors)."""
    params = init_params(game, N, init_std, gen)
    opt = torch.optim.Adam(params, lr=lr)
    for _ in range(steps):
        if game.kind == "matrix":
            lg = params[0].unsqueeze(1).expand(N, batch, game.A)
            a, la = sample(lg, gen)
            b, lb = sample(lg, gen)
            if op_group != "none":
                sym = game.sym_idx if op_group == "true" else list(range(game.A))
                sig = sample_perms((N, batch), game.A, sym, gen)
                b = sig.gather(-1, b.unsqueeze(-1)).squeeze(-1)   # partner plays sigma(pi): label b -> sigma(b)
                # log-prob of partner's own (unpermuted) action is lb, as in OP: grad through both copies
            r = game.R[a, b]
            adv = r - r.mean(1, keepdim=True)
            loss = -((la + lb) * adv).mean()
        else:
            ls, lr_ = params
            c = torch.multinomial(game.prior.expand(N * batch, 4), 1, generator=gen).view(N, batch)
            lgs = ls.gather(1, c.unsqueeze(-1).expand(N, batch, game.M))
            m, lm = sample(lgs, gen)
            if op_group != "none":
                sig = sample_perms((N, batch), game.M, list(range(game.M)), gen)   # all messages symmetric
                m_seen = sig.gather(-1, m.unsqueeze(-1)).squeeze(-1)
            else:
                m_seen = m
            lgr = lr_.gather(1, m_seen.unsqueeze(-1).expand(N, batch, game.G))
            g, lg_ = sample(lgr, gen)
            r = (g == c).float()
            adv = r - r.mean(1, keepdim=True)
            loss = -((lm + lg_) * adv).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return [p.detach() for p in params]


def train_br_to_population(game, pop_params, K, N, steps, batch, lr, init_std, gen):
    """Stage 2 of the population method: a best-response agent trained against frozen population members.
    pop_params: list of [N*K,...] tensors laid out as [N,K,...]."""
    pop = [p.view(N, K, *p.shape[1:]) for p in pop_params]
    params = init_params(game, N, init_std, gen)
    opt = torch.optim.Adam(params, lr=lr)
    ar = torch.arange(N).unsqueeze(1)
    for _ in range(steps):
        k = torch.randint(0, K, (N, batch), generator=gen)
        if game.kind == "matrix":
            lg = params[0].unsqueeze(1).expand(N, batch, game.A)
            a, la = sample(lg, gen)
            b, _ = sample(pop[0][ar, k], gen)
            r = game.R[a, b]
            adv = r - r.mean(1, keepdim=True)
            loss = -(la * adv).mean()
        else:
            ls, lr_ = params
            c = torch.multinomial(game.prior.expand(N * batch, 4), 1, generator=gen).view(N, batch)
            # episode type 1: BR sender -> frozen receiver
            m, lm = sample(ls.gather(1, c.unsqueeze(-1).expand(N, batch, game.M)), gen)
            ni, bi = torch.arange(N).view(N, 1), torch.arange(batch).view(1, batch)
            g, _ = sample(pop[1][ar, k][ni, bi, m], gen)
            r1 = (g == c).float()
            # episode type 2: frozen sender -> BR receiver
            ms, _ = sample(pop[0][ar, k][ni, bi, c], gen)
            g2, lg2 = sample(lr_.gather(1, ms.unsqueeze(-1).expand(N, batch, game.G)), gen)
            r2 = (g2 == c).float()
            loss = -(lm * (r1 - r1.mean(1, keepdim=True)) + lg2 * (r2 - r2.mean(1, keepdim=True))).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return [p.detach() for p in params]


# ---------------------------------------------------------------- exact evaluation
def pair_payoff(game, P, Q):
    """Exact expected payoff of every (i,j): agent i (from P) paired with agent j (from Q). Returns [N,N] where
    for signal game the value is the mean of both seatings (i sends/j receives, j sends/i receives)."""
    if game.kind == "matrix":
        p = torch.softmax(P[0], -1); q = torch.softmax(Q[0], -1)
        return p @ game.R @ q.T
    ps = torch.softmax(P[0], -1); pr = torch.softmax(P[1], -1)   # [N,C,M], [N,M,G]
    qs = torch.softmax(Q[0], -1); qr = torch.softmax(Q[1], -1)
    pri = game.prior
    # sender i, receiver j: sum_c prior_c sum_m ps[i,c,m] qr[j,m,c]
    sr = torch.einsum("c,icm,jmc->ij", pri, ps, qr)
    rs = torch.einsum("c,jcm,imc->ij", pri, qs, pr)   # sender j, receiver i
    return 0.5 * (sr + rs)


def evaluate(game, params):
    M = pair_payoff(game, params, params)
    N = M.shape[0]
    sp = M.diagonal().mean().item()
    off = (M.sum() - M.diagonal().sum()) / (N * (N - 1))
    xp_min = M[~torch.eye(N, dtype=bool)].min().item()
    return sp, off.item(), xp_min, M


def convention_entropy(game, params):
    """Mean policy entropy (nats) of the agents (matrix: action dist.; signal: sender message dist. given card)."""
    lg = params[0]
    p = torch.softmax(lg, -1)
    return float(-(p * torch.log(p + 1e-12)).sum(-1).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True, choices=["SP", "OP", "OP-full", "PBT"])
    ap.add_argument("--task", required=True, choices=["lever", "safe", "signal"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n_agents", type=int, default=20)
    ap.add_argument("--steps", type=int, default=1500)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--lr", type=float, default=0.05)
    ap.add_argument("--init_std", type=float, default=1.0)
    ap.add_argument("--pop_size", type=int, default=8)
    ap.add_argument("--out", default=os.environ.get("RH_METRICS_FILE", "metrics.json"))
    args = ap.parse_args()
    print("config:", json.dumps(vars(args)), flush=True)
    t0 = time.time()
    gen = torch.Generator().manual_seed(1000 * args.seed + 17)
    game = make_game(args.task)
    N = args.n_agents
    if args.system in ("SP", "OP", "OP-full"):
        grp = {"SP": "none", "OP": "true", "OP-full": "full"}[args.system]
        if grp == "full" and args.task == "signal":
            grp = "true"   # all messages are already symmetric in the signalling game
        params = train_sp_or_op(game, N, args.steps, args.batch, args.lr, args.init_std, grp, gen)
    else:
        K = args.pop_size
        pop = train_sp_or_op(game, N * K, args.steps, args.batch, args.lr, args.init_std, "none", gen)
        params = train_br_to_population(game, pop, K, N, args.steps, args.batch, args.lr, args.init_std, gen)
    sp, xp, xpmin, M = evaluate(game, params)
    out = {"self_play": sp, "cross_play": xp, "cross_play_min": xpmin, "gap": sp - xp,
           "entropy": convention_entropy(game, params), "runtime_s": time.time() - t0}
    if args.task == "lever":   # fraction of agents that converged to the distinct (0.9) lever
        out["frac_special"] = float((torch.softmax(params[0], -1)[:, 9] > 0.5).float().mean())
    if args.task == "safe":    # fraction choosing the safe action
        out["frac_safe"] = float((torch.softmax(params[0], -1)[:, 4] > 0.5).float().mean())
    print("metrics:", json.dumps(out), flush=True)
    json.dump(out, open(args.out, "w"))


if __name__ == "__main__":
    main()
