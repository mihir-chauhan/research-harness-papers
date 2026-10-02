"""Lewis reconstruction game with a discrete channel (vocabulary V, message length L).

Systems
  gumbel       sender/receiver GRUs trained end to end through straight-through Gumbel-softmax
  reinforce    sender trained with REINFORCE (moving-average baseline, entropy bonus), receiver by backprop
  random_code  fixed sender: every object (also held-out ones) gets an i.i.d. random message; receiver learned
  oracle_comp  fixed sender: position j holds the value of attribute j (needs L >= n_attr), rest padded; receiver learned

Task string: "V<vocab>_L<length>", e.g. V5_L4. Objects: N_ATTR attributes x N_VAL values (4 x 4 = 256).
Writes a flat JSON of metrics.
"""
import argparse, json, math, time, itertools
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.stats import spearmanr

torch.set_num_threads(2)

N_ATTR, N_VAL = 4, 4
HOLDOUT_FRAC = 0.10


def parse_task(task):
    v, l = task.split("_")
    return int(v[1:]), int(l[1:])


def make_split(seed):
    """Random 10% of attribute combinations are held out (test). Every attribute value must remain
    present in training for every attribute (re-draw otherwise)."""
    objs = np.array(list(itertools.product(range(N_VAL), repeat=N_ATTR)))  # (256, 4)
    rng = np.random.RandomState(1000 + seed)
    n_test = int(round(HOLDOUT_FRAC * len(objs)))
    while True:
        perm = rng.permutation(len(objs))
        test_idx, train_idx = perm[:n_test], perm[n_test:]
        if all(len(set(objs[train_idx, a])) == N_VAL for a in range(N_ATTR)):
            return objs, np.sort(train_idx), np.sort(test_idx)


def onehot(objs):
    x = np.zeros((len(objs), N_ATTR * N_VAL), dtype=np.float32)
    for a in range(N_ATTR):
        x[np.arange(len(objs)), a * N_VAL + objs[:, a]] = 1.0
    return torch.from_numpy(x)


class Sender(nn.Module):
    def __init__(self, V, L, H):
        super().__init__()
        self.V, self.L, self.H = V, L, H
        self.enc = nn.Linear(N_ATTR * N_VAL, H)
        self.emb = nn.Parameter(torch.randn(V, H) * 0.1)
        self.start = nn.Parameter(torch.zeros(H))
        self.cell = nn.GRUCell(H, H)
        self.out = nn.Linear(H, V)

    def forward(self, x, mode, tau=1.0, greedy=False):
        """mode 'gumbel': returns one-hot (ST) messages (B, L, V), None
           mode 'reinforce': returns one-hot messages (no grad), (logp, entropy)"""
        B = x.shape[0]
        h = torch.tanh(self.enc(x))
        inp = self.start.unsqueeze(0).expand(B, -1)
        syms, logps, ents = [], [], []
        for _ in range(self.L):
            h = self.cell(inp, h)
            logits = self.out(h)
            if mode == "gumbel":
                if greedy:
                    y = F.one_hot(logits.argmax(-1), self.V).float()
                else:
                    y = F.gumbel_softmax(logits, tau=tau, hard=True)
            else:
                dist = torch.distributions.Categorical(logits=logits)
                a = logits.argmax(-1) if greedy else dist.sample()
                y = F.one_hot(a, self.V).float()
                logps.append(dist.log_prob(a))
                ents.append(dist.entropy())
            syms.append(y)
            inp = y @ self.emb
        msg = torch.stack(syms, 1)
        if mode == "reinforce":
            return msg, (torch.stack(logps, 1).sum(1), torch.stack(ents, 1).sum(1))
        return msg, None


class Receiver(nn.Module):
    def __init__(self, V, H):
        super().__init__()
        self.emb = nn.Parameter(torch.randn(V, H) * 0.1)
        self.gru = nn.GRU(H, H, batch_first=True)
        self.heads = nn.Linear(H, N_ATTR * N_VAL)

    def forward(self, msg):  # msg (B, L, V) one-hot or ST one-hot
        _, h = self.gru(msg @ self.emb)
        return self.heads(h[-1]).view(-1, N_ATTR, N_VAL)


def ce_per_sample(logits, objs):
    # sum over attributes of cross-entropy, shape (B,)
    lp = F.log_softmax(logits, -1)
    return -lp.gather(-1, objs.unsqueeze(-1)).squeeze(-1).sum(-1)


def accuracies(logits, objs):
    pred = logits.argmax(-1)
    ok = (pred == objs)
    return ok.all(-1).float().mean().item(), ok.float().mean().item()


def topsim(objs_np, msgs_np):
    """Spearman correlation between pairwise Hamming distances of meanings (attribute-value vectors)
    and of messages (symbol sequences)."""
    n = len(objs_np)
    iu = np.triu_indices(n, 1)
    dm = (objs_np[:, None, :] != objs_np[None, :, :]).sum(-1)[iu]
    dg = (msgs_np[:, None, :] != msgs_np[None, :, :]).sum(-1)[iu]
    if dg.std() == 0:
        return 0.0
    return float(spearmanr(dm, dg).correlation)


def fixed_messages(system, objs_np, V, L, rng):
    n = len(objs_np)
    if system == "random_code":
        return rng.randint(0, V, size=(n, L))
    if system == "oracle_comp":
        m = np.zeros((n, L), dtype=np.int64)
        k = min(L, N_ATTR)
        m[:, :k] = objs_np[:, :k]
        return m
    raise ValueError(system)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True, choices=["gumbel", "reinforce", "random_code", "oracle_comp"])
    ap.add_argument("--task", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--hidden", type=int, default=64)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--tau", type=float, default=1.0)
    ap.add_argument("--ent", type=float, default=0.01)  # REINFORCE sender entropy bonus
    ap.add_argument("--curve", default="")  # optional csv path for the train-accuracy curve
    a = ap.parse_args()

    t0 = time.time()
    V, L = parse_task(a.task)
    torch.manual_seed(a.seed)
    np.random.seed(a.seed)
    rng = np.random.RandomState(a.seed)
    objs_np, tr_idx, te_idx = make_split(a.seed)
    X_all = onehot(objs_np)
    O_all = torch.from_numpy(objs_np)
    tr = torch.from_numpy(tr_idx)
    H = a.hidden

    learned = a.system in ("gumbel", "reinforce")
    sender = Sender(V, L, H) if learned else None
    recv = Receiver(V, H)
    params = list(recv.parameters()) + (list(sender.parameters()) if learned else [])
    opt = torch.optim.Adam(params, lr=a.lr)
    if not learned:
        fixed = torch.from_numpy(fixed_messages(a.system, objs_np, V, L, rng))
        fixed_oh = F.one_hot(fixed, V).float()

    baseline = 0.0
    curve = []
    for step in range(a.steps):
        bi = tr[torch.randint(len(tr), (a.batch,))]
        x, o = X_all[bi], O_all[bi]
        if a.system == "gumbel":
            msg, _ = sender(x, "gumbel", tau=a.tau)
            loss = ce_per_sample(recv(msg), o).mean()
        elif a.system == "reinforce":
            msg, (logp, ent) = sender(x, "reinforce")
            ce = ce_per_sample(recv(msg), o)
            reward = -ce.detach()
            adv = reward - baseline
            baseline = 0.99 * baseline + 0.01 * reward.mean().item() if step > 0 else reward.mean().item()
            loss = ce.mean() + (-(adv * logp) - a.ent * ent).mean()
        else:
            loss = ce_per_sample(recv(fixed_oh[bi]), o).mean()
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(params, 5.0)
        opt.step()
        if a.curve and (step % 100 == 0 or step == a.steps - 1):
            with torch.no_grad():
                if learned:
                    m, _ = sender(X_all[tr], a.system, greedy=True)
                else:
                    m = fixed_oh[tr]
                acc, _ = accuracies(recv(m), O_all[tr])
            curve.append((step, acc))

    # ---- evaluation (greedy messages; held-out combinations never seen in training) ----
    with torch.no_grad():
        if learned:
            msg_all, _ = sender(X_all, a.system, greedy=True)
        else:
            msg_all = fixed_oh
        logits = recv(msg_all)
        tr_acc, tr_attr = accuracies(logits[tr], O_all[tr])
        te = torch.from_numpy(te_idx)
        te_acc, te_attr = accuracies(logits[te], O_all[te])
        # message dependence: shuffle messages across objects (a listener ignoring messages would not change)
        perm = torch.from_numpy(rng.permutation(len(objs_np)))
        sh_acc, sh_attr = accuracies(recv(msg_all[perm])[te], O_all[te])
        msgs_np = msg_all.argmax(-1).numpy()
        ts_all = topsim(objs_np, msgs_np)
        ts_train = topsim(objs_np[tr_idx], msgs_np[tr_idx])
        n_unique = len({tuple(m) for m in msgs_np})
        # symbols actually used per position
        used = float(np.mean([len(set(msgs_np[:, j])) for j in range(L)]))

    res = {
        "heldout_acc": te_acc,
        "train_acc": tr_acc,
        "heldout_attr_acc": te_attr,
        "train_attr_acc": tr_attr,
        "gen_gap": tr_acc - te_acc,
        "topsim": ts_all,
        "topsim_train": ts_train,
        "n_unique_messages": float(n_unique),
        "symbols_used_per_position": used,
        "shuffled_msg_heldout_attr_acc": sh_attr,
        "capacity_bits": L * math.log2(V),
        "wall_s": time.time() - t0,
    }
    with open(a.out, "w") as f:
        json.dump(res, f)
    if a.curve:
        with open(a.curve, "w") as f:
            f.write("step,value,seed,name\n")
            for s, v in curve:
                f.write(f"{s},{v},{a.seed},{a.system}_{a.task}\n")
    print(json.dumps(res))


if __name__ == "__main__":
    main()
