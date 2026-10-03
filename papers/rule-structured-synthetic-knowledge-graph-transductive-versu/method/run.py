"""Family-tree KG: TransE, TransE+fold-in, Path-MP (2-hop relational message passing), rule oracle.

Usage: python method/run.py --system <transe|transe_foldin|pathmp|oracle> --task <transductive|inductive>
                            --seed S --out metrics.json [hyperparameters]
"""
import argparse, json, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.set_num_threads(2)
R0 = 4  # base relations: 0 parent, 1 sibling, 2 grandparent, 3 uncle ; r+4 = inverse
REL = ["parent", "sibling", "grandparent", "uncle"]


# ---------------------------------------------------------------- data
def gen_family(n, rng):
    """Random multi-generation family forest with exactly n people. Returns (n, triples[(h,r,t)])."""
    cnt = 0
    parents = []  # list of (father, mother) per person or None
    def new():
        nonlocal cnt
        parents.append(None); cnt += 1
        return cnt - 1
    queue = []
    for _ in range(6):
        queue.append((new(), new(), 0))
    kids = {}
    qi = 0
    while cnt < n:
        if qi >= len(queue):
            if cnt + 2 > n: break
            queue.append((new(), new(), 0))
        m, f, g = queue[qi]; qi += 1
        k = int(rng.choice([1, 2, 3, 4], p=[.2, .35, .3, .15]))
        k = min(k, n - cnt)
        ch = []
        for _ in range(k):
            c = new(); parents[c] = (m, f); ch.append(c)
        kids[(m, f)] = ch
        if g < 5:
            for c in ch:
                if cnt < n and rng.random() < 0.8:
                    queue.append((c, new(), g + 1))
    while cnt < n:  # pad with isolated people if the queue ran dry
        new()
    perm = rng.permutation(n)
    par = set()
    for c, p in enumerate(parents):
        if p is not None:
            par.add((p[0], c)); par.add((p[1], c))
    sib = set()
    for ch in kids.values():
        for a in ch:
            for b in ch:
                if a != b: sib.add((a, b))
    pc = {}
    for p, c in par: pc.setdefault(c, []).append(p)
    gp = {(g, c) for p, c in par for g in pc.get(p, [])}
    sib_of = {}
    for a, b in sib: sib_of.setdefault(a, []).append(b)
    un = {(u, c) for p, c in par for u in sib_of.get(p, [])}
    T = [(h, 0, t) for h, t in par] + [(h, 1, t) for h, t in sib] + [(h, 2, t) for h, t in gp] + [(h, 3, t) for h, t in un]
    T = sorted({(int(perm[h]), r, int(perm[t])) for h, r, t in T})
    return n, np.array(T, dtype=np.int64)


def unit_key(h, r, t):
    return (min(h, t), r, max(h, t)) if r == 1 else (h, r, t)


def split_graph(T, rng, fr=(0.8, 0.1, 0.1)):
    """Split at the level of units (a sibling pair is one unit so its mirror triple cannot leak)."""
    keys = [unit_key(*x) for x in T]
    uniq = sorted(set(keys))
    order = rng.permutation(len(uniq))
    lab = {}
    a, b = int(fr[0] * len(uniq)), int((fr[0] + fr[1]) * len(uniq))
    for rank, i in enumerate(order):
        lab[uniq[i]] = 0 if rank < a else (1 if rank < b else 2)
    s = np.array([lab[k] for k in keys])
    return T[s == 0], T[s == 1], T[s == 2]


class Graph:
    """Message graph over a set of observed triples (forward + inverse edges)."""
    def __init__(self, n, obs):
        self.n = n
        ids = {}
        g = []
        for h, r, t in obs:
            k = unit_key(h, r, t)
            g.append(ids.setdefault(k, len(ids)))
        g = np.array(g, dtype=np.int64)
        h, r, t = obs[:, 0], obs[:, 1], obs[:, 2]
        self.src = torch.tensor(np.concatenate([h, t]))
        self.dst = torch.tensor(np.concatenate([t, h]))
        self.rel = torch.tensor(np.concatenate([r, r + R0]))
        self.gid = torch.tensor(np.concatenate([g, g]))
        self.obs = obs
        # triple lookup for query-edge removal: (h, rel) -> group ids
        self.tgid = {unit_key(*x): i for i, x in enumerate(obs)}
        self.unit_ids = ids


def true_sets(T):
    d = {}
    for h, r, t in T:
        d.setdefault((int(h), int(r)), set()).add(int(t))
        d.setdefault((int(t), int(r) + R0), set()).add(int(h))
    return d


# ---------------------------------------------------------------- evaluation
def rank_of(scores, target, filt):
    s = scores.copy()
    st = s[target]
    mask = np.zeros(len(s), dtype=bool)
    if filt: mask[list(filt)] = True
    mask[target] = False
    s[mask] = -np.inf
    s[target] = -np.inf
    return 1.0 + (s > st).sum() + 0.5 * (s == st).sum()  # ties split evenly


def evaluate(score_tails, test, truth):
    """score_tails(h, rel)-> np array over all entities. Head queries use the inverse relation."""
    ranks, per = [], {r: [] for r in range(R0)}
    for h, r, t in test:
        for (q, rel, tgt) in ((h, r, t), (t, r + R0, h)):
            rk = rank_of(score_tails(int(q), int(rel)), int(tgt), truth[(int(q), int(rel))])
            ranks.append(rk); per[int(r)].append(rk)
    ranks = np.array(ranks)
    out = {"mrr": float((1 / ranks).mean()), "hits1": float((ranks <= 1).mean()), "hits10": float((ranks <= 10).mean())}
    for r in range(R0):
        out["mrr_" + REL[r]] = float((1 / np.array(per[r])).mean()) if per[r] else float("nan")
    return out


# ---------------------------------------------------------------- TransE
class TransE(nn.Module):
    def __init__(self, n, dim, nrel=R0, p=1):
        super().__init__()
        self.E = nn.Parameter(torch.empty(n, dim)); self.R = nn.Parameter(torch.empty(nrel, dim))
        b = 6 / dim ** 0.5
        nn.init.uniform_(self.E, -b, b); nn.init.uniform_(self.R, -b, b)
        with torch.no_grad():
            self.R /= self.R.norm(dim=1, keepdim=True)
            self.E /= self.E.norm(dim=1, keepdim=True)
        self.p = p

    def dist(self, h, r, t):
        return (self.E[h] + self.R[r] - self.E[t]).norm(p=self.p, dim=-1)


def train_transe(model, triples, n, epochs, lr, margin, k, bs, gen, freeze_rel=False):
    params = [model.E] if freeze_rel else [model.E, model.R]
    opt = torch.optim.Adam(params, lr=lr)
    T = torch.tensor(triples)
    # one gradient triple per unit (sibling mirrors are both listed, which is fine for TransE)
    for ep in range(epochs):
        perm = torch.randperm(len(T), generator=gen)
        for i in range(0, len(T), bs):
            b = T[perm[i:i + bs]]
            h, r, t = b[:, 0], b[:, 1], b[:, 2]
            h = h.repeat_interleave(k); r = r.repeat_interleave(k); t = t.repeat_interleave(k)
            corrupt_head = torch.rand(len(h), generator=gen) < 0.5
            rnd = torch.randint(0, n, (len(h),), generator=gen)
            hn = torch.where(corrupt_head, rnd, h); tn = torch.where(corrupt_head, t, rnd)
            pos = model.dist(h, r, t); neg = model.dist(hn, r, tn)
            loss = F.relu(margin + pos - neg).mean()
            opt.zero_grad(); loss.backward(); opt.step()
            with torch.no_grad():
                model.E /= model.E.norm(dim=1, keepdim=True).clamp(min=1.0)  # ||e|| <= 1
    return model


def transe_scorer(model):
    E, R = model.E.detach(), model.R.detach()
    def f(q, rel):
        if rel < R0:
            d = (E[q] + R[rel] - E).norm(p=model.p, dim=1)
        else:
            d = (E + R[rel - R0] - E[q]).norm(p=model.p, dim=1)
        return (-d).numpy()
    return f


# ---------------------------------------------------------------- Path-MP
class PathMP(nn.Module):
    """Query-conditioned relational message passing with L layers (NBFNet-style, sum aggregation).

    state x_0[v] = 1[v == h] * q_rel ; x_{l}[v] = ReLU(LN(U_l [x_{l-1}[v] ; sum_{(u,e,v)} x_{l-1}[u] * w_l(e|q)] + x_0[v]))
    w_l(e|q) = W_l q_rel (one d-vector per edge relation). score(v) = MLP(x_L[v]).
    """
    def __init__(self, d, L, nrel=2 * R0):
        super().__init__()
        self.d, self.L, self.nrel = d, L, nrel
        self.Q = nn.Embedding(nrel, d)
        self.W = nn.ModuleList([nn.Linear(d, nrel * d) for _ in range(L)])
        self.U = nn.ModuleList([nn.Linear(2 * d, d) for _ in range(L)])
        self.ln = nn.ModuleList([nn.LayerNorm(d) for _ in range(L)])
        self.out = nn.Sequential(nn.Linear(d, d), nn.ReLU(), nn.Linear(d, 1))

    def forward(self, g, h, qrel, drop_gid=None):
        B, n, d = len(h), g.n, self.d
        q = self.Q(qrel)  # B,d
        x0 = torch.zeros(B, n, d); x0[torch.arange(B), h] = q
        x = x0
        if drop_gid is not None:
            keep = (g.gid[None, :] != drop_gid[:, None]).float()  # B,M
        for l in range(self.L):
            w = self.W[l](q).view(B, self.nrel, d)[:, g.rel]  # B,M,d
            msg = x[:, g.src] * w
            if drop_gid is not None: msg = msg * keep[:, :, None]
            agg = torch.zeros(B, n, d).index_add_(1, g.dst, msg)
            x = F.relu(self.ln[l](self.U[l](torch.cat([x, agg], -1)) + x0))
        return self.out(x).squeeze(-1)  # B,n


def train_pathmp(model, g, train, n, epochs, lr, bs, gen, drop_query_edge=True, steps_cap=None):
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    truth = true_sets(train)
    # queries: both directions of every training triple
    Q = [(int(h), int(r), int(t), g.tgid[unit_key(h, r, t)]) for h, r, t in train] + \
        [(int(t), int(r) + R0, int(h), g.tgid[unit_key(h, r, t)]) for h, r, t in train]
    # tgid indexes obs rows; map to the group id used by edges
    gid_of_row = torch.zeros(len(g.obs), dtype=torch.long)
    for k, i in g.tgid.items(): gid_of_row[i] = g.unit_ids[k]
    Qa = torch.tensor([[a, b, c, int(gid_of_row[e])] for a, b, c, e in Q])
    for ep in range(epochs):
        perm = torch.randperm(len(Qa), generator=gen)
        if steps_cap: perm = perm[: steps_cap * bs]
        for i in range(0, len(perm), bs):
            b = Qa[perm[i:i + bs]]
            h, r, t, gd = b[:, 0], b[:, 1], b[:, 2], b[:, 3]
            logits = model(g, h, r, gd if drop_query_edge else None)
            mask = torch.zeros_like(logits, dtype=torch.bool)
            for j in range(len(h)):  # mask other known training positives
                other = truth[(int(h[j]), int(r[j]))] - {int(t[j])}
                if other: mask[j, list(other)] = True
            logits = logits.masked_fill(mask, -1e9)
            loss = F.cross_entropy(logits, t)
            opt.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(model.parameters(), 5.0); opt.step()
    return model


def pathmp_scorer(model, g):
    def f(q, rel):
        with torch.no_grad():
            return model(g, torch.tensor([q]), torch.tensor([rel]))[0].numpy()
    return f


# ---------------------------------------------------------------- rule oracle (hand-written)
def oracle_scorer(n, obs):
    A = [np.zeros((n, n)) for _ in range(R0)]
    for h, r, t in obs: A[r][h, t] = 1
    P, S, G, U = A
    eye = np.eye(n); ne = 1 - eye
    # one-step Horn closure of the generative rules over the observed graph (scores = number of groundings)
    M0 = P @ S                                     # parent(x,y) <- parent(x,z), sibling(z,y)
    M1 = (P.T @ P) * ne + S.T + (S @ S) * ne + (U @ P.T) * ne   # sibling: shared parent, symmetry, transitivity, uncle(x,c)&parent(y,c)
    M2 = P @ P + P @ U + G @ S                     # grandparent: parent.parent, parent.uncle, grandparent.sibling
    M3 = S @ P + U @ S                             # uncle: sibling.parent, uncle.sibling
    Ms = [M0, M1, M2, M3]
    def f(q, rel):
        if rel < R0: return Ms[rel][q, :].copy()
        return Ms[rel - R0][:, q].copy()
    return f


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True); ap.add_argument("--task", required=True)
    ap.add_argument("--seed", type=int, required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--people", type=int, default=500)
    ap.add_argument("--dim", type=int, default=64); ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--lr", type=float, default=0.01); ap.add_argument("--margin", type=float, default=8.0)
    ap.add_argument("--negs", type=int, default=10); ap.add_argument("--bs", type=int, default=512)
    ap.add_argument("--p", type=int, default=1)
    ap.add_argument("--fold_epochs", type=int, default=200)
    ap.add_argument("--layers", type=int, default=2); ap.add_argument("--d", type=int, default=32)
    ap.add_argument("--pm_epochs", type=int, default=3); ap.add_argument("--pm_lr", type=float, default=0.003)
    ap.add_argument("--pm_bs", type=int, default=32)
    ap.add_argument("--no_drop", action="store_true")
    ap.add_argument("--obs_frac", type=float, default=1.0, help="fraction of observed new-graph triples used as message graph (inductive)")
    ap.add_argument("--eval_split", default="test", choices=["test", "val"])
    a = ap.parse_args()
    print("config", json.dumps(vars(a)))
    torch.manual_seed(a.seed); np.random.seed(a.seed)
    gen = torch.Generator().manual_seed(a.seed)
    t0 = time.time()
    # graph 1 (train world) and graph 2 (fresh entities) are generated from seed-derived streams
    n, T1 = gen_family(a.people, np.random.default_rng(1000 + a.seed))
    tr1, va1, te1 = split_graph(T1, np.random.default_rng(2000 + a.seed))
    n2, T2 = gen_family(a.people, np.random.default_rng(3000 + a.seed))
    tr2, va2, te2 = split_graph(T2, np.random.default_rng(4000 + a.seed))
    stats = {"n_triples_g1": len(T1), "n_train_g1": len(tr1), "n_test_g1": len(te1), "n_triples_g2": len(T2), "n_test_g2": len(te2)}
    for r in range(R0): stats["frac_" + REL[r]] = float((T1[:, 1] == r).mean())
    print("stats", stats)
    if a.task == "transductive":
        obs, test, truth_T, N = np.concatenate([tr1, va1]) if a.eval_split == "test" else tr1, (te1 if a.eval_split == "test" else va1), T1, n
    else:
        obs2 = np.concatenate([tr2, va2])
        if a.obs_frac < 1.0:
            keys = sorted(set(unit_key(*x) for x in obs2)); rr = np.random.default_rng(5000 + a.seed)
            keep = set(keys[i] for i in rr.permutation(len(keys))[: int(a.obs_frac * len(keys))])
            obs2 = np.array([x for x in obs2 if unit_key(*x) in keep])
        obs, test, truth_T, N = obs2, te2, T2, n2
    truth = true_sets(truth_T)
    train_obs = np.concatenate([tr1, va1]) if (a.task == "transductive" and a.eval_split == "test") else tr1
    # models are always trained on graph 1's training triples (train+val for the final test; val-tuning uses train only)
    if a.system in ("transe", "transe_foldin"):
        m = TransE(n, a.dim, p=a.p)
        train_transe(m, train_obs, n, a.epochs, a.lr, a.margin, a.negs, a.bs, gen)
        if a.task == "inductive":
            m = _fresh_entities(m, n2, a)
            if a.system == "transe_foldin":
                train_transe(m, obs, n2, a.fold_epochs, a.lr, a.margin, a.negs, a.bs, gen, freeze_rel=True)
        scorer = transe_scorer(m)
    elif a.system == "pathmp":
        m = PathMP(a.d, a.layers)
        g1 = Graph(n, train_obs)
        train_pathmp(m, g1, train_obs, n, a.pm_epochs, a.pm_lr, a.pm_bs, gen, drop_query_edge=not a.no_drop)
        m.eval()
        g = Graph(N, obs)
        scorer = pathmp_scorer(m, g)
    elif a.system == "oracle":
        scorer = oracle_scorer(N, obs)
    else:
        raise SystemExit("unknown system")
    res = evaluate(scorer, test, truth)
    res.update(stats)
    print("final", json.dumps(res))
    json.dump(res, open(a.out, "w"))


def _fresh_entities(m, n2, a):
    """New entity table (fresh random init, same init law as training); relation vectors copied."""
    new = TransE(n2, a.dim, p=a.p)
    with torch.no_grad(): new.R.copy_(m.R)
    return new


if __name__ == "__main__":
    main()
