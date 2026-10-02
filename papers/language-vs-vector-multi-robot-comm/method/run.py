"""Two point robots, hidden-target rendezvous. Systems: none | continuous | discrete | language.
Train:  run.py --mode train --system S --seed s --out metrics.json   (saves ckpt to results/ckpt/)
XPlay:  run.py --mode xplay --system S --seed s --nseeds N --out metrics.json
"""
import argparse, json, os, csv, numpy as np, torch, torch.nn as nn, torch.nn.functional as F
torch.set_num_threads(2)
T, DT, RADIUS = 10, 0.25, 0.3
SYS = {"none", "continuous", "discrete", "language"}
CK = "results/ckpt"

def mlp(i, o, h=64):
    return nn.Sequential(nn.Linear(i, h), nn.Tanh(), nn.Linear(h, h), nn.Tanh(), nn.Linear(h, o))

WORDS_X = ["far-west", "west", "east", "far-east"]
WORDS_Y = ["far-south", "south", "north", "far-north"]

def language_utterance(target, g):
    """Fixed templated utterance 'target is <row word> <col word>': (row idx, col idx) on a g x g grid."""
    idx = torch.clamp(((target + 1) / 2 * g).floor().long(), 0, g - 1)  # [B,2] (x,y)
    return idx[:, 1], idx[:, 0]   # row (y), col (x)

class Speaker(nn.Module):
    def __init__(s, system, d, V, L, tau=1.0):
        super().__init__(); s.system, s.d, s.V, s.L, s.tau = system, d, V, L, tau
        s.act = mlp(4, 2)   # own pos + target -> velocity (all systems)
        if system == "continuous": s.msg = mlp(2, d)
        if system == "discrete": s.msg = mlp(2, V * L)
    def message(self, target, hard):
        if self.system == "continuous": return torch.tanh(self.msg(target))
        if self.system == "discrete":
            lg = self.msg(target).view(-1, self.L, self.V)
            if hard: return F.one_hot(lg.argmax(-1), self.V).float().view(len(target), -1)
            return F.gumbel_softmax(lg, tau=self.tau, hard=True).view(len(target), -1)
        return None

class Listener(nn.Module):
    def __init__(s, system, d, V, L, g):
        super().__init__(); s.system, s.g = system, g
        if system == "none": mi = 0
        elif system == "continuous": mi = d
        elif system == "discrete": mi = V * L
        else: mi = 2 * g   # one-hot row word + one-hot col word
        s.net = mlp(2 + mi + 1, 2)
        s.mi = mi
    def forward(s, pos, msg, t):
        x = [pos, torch.full_like(pos[:, :1], t / T)]
        if s.mi: x.append(msg)
        return s.net(torch.cat(x, 1))

def lang_msg(target, g):
    r, c = language_utterance(target, g)
    return torch.cat([F.one_hot(r, g), F.one_hot(c, g)], 1).float()

def rollout(sp, ls, target, system, args, hard, noise):
    B = len(target)
    if system == "language": m = lang_msg(target, args.g)
    elif system == "none": m = None
    else:
        m = sp.message(target, hard)
        if system == "continuous" and noise > 0: m = m + noise * torch.randn_like(m)
    p0 = torch.zeros(B, 2); p1 = torch.zeros(B, 2)  # both start at origin
    for t in range(T):
        v0 = torch.tanh(sp.act(torch.cat([p0, target], 1)))
        v1 = torch.tanh(ls(p1, m, t))
        p0, p1 = p0 + DT * v0, p1 + DT * v1
    d0, d1 = (p0 - target).norm(dim=1), (p1 - target).norm(dim=1)
    return d0, d1

def evaluate(sp, ls, system, args, seed, n=2000):
    g = torch.Generator().manual_seed(seed)
    target = torch.rand(n, 2, generator=g) * 2 - 1
    with torch.no_grad():
        d0, d1 = rollout(sp, ls, target, system, args, True, args.noise)
    succ = ((d0 < RADIUS) & (d1 < RADIUS)).float().mean().item()
    return succ, torch.maximum(d0, d1).mean().item()

def build(system, args):
    return Speaker(system, args.d, args.vocab, args.L, args.tau), Listener(system, args.d, args.vocab, args.L, args.vocab)

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--mode", default="train"); a.add_argument("--system", required=True)
    a.add_argument("--task", default="rendezvous"); a.add_argument("--seed", type=int, default=0)
    a.add_argument("--out", required=True); a.add_argument("--steps", type=int, default=2000)
    a.add_argument("--batch", type=int, default=64); a.add_argument("--lr", type=float, default=3e-3)
    a.add_argument("--d", type=int, default=4); a.add_argument("--vocab", type=int, default=4)  # vocab = tokens/slot = grid words per axis
    a.add_argument("--L", type=int, default=2); a.add_argument("--noise", type=float, default=0.1)
    a.add_argument("--nseeds", type=int, default=5); a.add_argument("--tag", default="")
    a.add_argument("--tau", type=float, default=1.0); a.add_argument("--eval_every", type=int, default=100)
    args = a.parse_args(); args.g = args.vocab
    system = args.system; assert system in SYS
    os.makedirs(CK, exist_ok=True)
    ck = lambda s: f"{CK}/{system}_V{args.vocab}_n{args.noise}{args.tag}_s{s}.pt"
    if args.mode == "train":
        torch.manual_seed(args.seed); np.random.seed(args.seed)
        sp, ls = build(system, args)
        opt = torch.optim.Adam(list(sp.parameters()) + list(ls.parameters()), lr=args.lr)
        curve = []; val_seed = 10_000 + args.seed
        for step in range(args.steps + 1):
            if step % args.eval_every == 0:
                curve.append((step, evaluate(sp, ls, system, args, val_seed, 1000)[0]))
                if step % 500 == 0: print(f"step {step} val_success {curve[-1][1]:.3f}", flush=True)
            if step == args.steps: break
            target = torch.rand(args.batch, 2) * 2 - 1
            d0, d1 = rollout(sp, ls, target, system, args, False, args.noise)
            loss = (d0 ** 2 + d1 ** 2).mean()
            opt.zero_grad(); loss.backward(); opt.step()
        succ, dist = evaluate(sp, ls, system, args, 20_000 + args.seed, 4000)  # held-out test targets
        torch.save({"sp": sp.state_dict(), "ls": ls.state_dict()}, ck(args.seed))
        name = os.environ.get("RH_SYSTEM_NAME", system)
        os.makedirs("results/raw", exist_ok=True)
        with open(f"results/raw/curve_{system}_V{args.vocab}_n{args.noise}{args.tag}_s{args.seed}.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(["step", "value", "seed", "name"])
            for st, v in curve: w.writerow([st * args.batch, v, args.seed, name])
        vals = [v for _, v in curve]
        first = next((st * args.batch for st, v in curve if v >= 0.5), args.steps * args.batch)
        first90 = next((st * args.batch for st, v in curve if v >= 0.9), args.steps * args.batch)  # capped when never reached
        out = {"success_rate": succ, "final_dist": dist, "success_auc": float(np.mean(vals)),
               "episodes_to_50": first, "episodes_to_90": first90, "val_success_final": vals[-1]}
        if system == "discrete":  # number of distinct messages the speaker actually emits on test targets
            with torch.no_grad():
                tg = torch.rand(4000, 2, generator=torch.Generator().manual_seed(20_000 + args.seed)) * 2 - 1
                out["msgs_used"] = len(torch.unique(sp.message(tg, True), dim=0))
        print(json.dumps(out))
        json.dump(out, open(args.out, "w"))
    else:  # xplay: listener of this seed with speakers of other seeds; selfplay reference also
        torch.manual_seed(0)
        sp, ls = build(system, args)
        L = torch.load(ck(args.seed)); ls.load_state_dict(L["ls"])
        res = []
        for j in range(args.nseeds):
            if j == args.seed: continue
            sp.load_state_dict(torch.load(ck(j))["sp"])
            res.append(evaluate(sp, ls, system, args, 20_000 + args.seed, 4000)[0])
        print({"xplay_success": float(np.mean(res))})
        json.dump({"xplay_success": float(np.mean(res))}, open(args.out, "w"))

if __name__ == "__main__": main()
