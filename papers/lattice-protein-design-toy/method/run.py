"""Design-for-target experiments on the exhaustive 2D HP N=16 lattice.

Systems: random (random search), sa (simulated annealing), ar (conditional autoregressive model).
Every system gets the same targets and the same budget K = number of ground-state-oracle calls per design;
a design is the best candidate (lowest objective f) among the K candidates it examined.
f(s;t) = (E(s,t) - E_min(s)) + 0.5*[E_min(s) attained by >1 conformation]; f=0  <=>  s folds uniquely to t.
"""
import argparse, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lattice as L

ALL_KS = [1, 10, 100, 1000]
KS = list(ALL_KS)
N = L.N
DIRS = L.DIRS


def coords(moves):
    xy = [(0, 0), (1, 0)]
    for d in moves[1:]:
        x, y = xy[-1]; dx, dy = DIRS[d]; xy.append((x + dx, y + dy))
    return xy


def features(T, idx):
    """per-conformation features: contact matrix [N,N] and free-neighbour counts [N]."""
    out_M = np.zeros((len(idx), N, N), np.float32); out_F = np.zeros((len(idx), N), np.int64)
    for a, c in enumerate(idx):
        for p, (i, j) in enumerate(L.PAIRS):
            if T["contacts"][c, p]:
                out_M[a, i, j] = out_M[a, j, i] = 1
        xy = coords(T["moves"][c]); occ = set(xy)
        for i, (x, y) in enumerate(xy):
            out_F[a, i] = sum((x + dx, y + dy) not in occ for dx, dy in DIRS)
    return out_M, out_F


def bits(codes):
    codes = np.asarray(codes)
    return ((codes[:, None] >> (N - 1 - np.arange(N))[None, :]) & 1).astype(np.int64)


def codes_of(b):
    return (b * (1 << (N - 1 - np.arange(N)))[None, :]).sum(1)


class Oracle:
    """Exact ground-state oracle (table lookup over the full enumeration)."""
    def __init__(self, T, obj="bin"):
        self.obj = obj
        self.emin = T["emin"].astype(np.int32); self.cnt = T["cnt"]; self.calls = 0
        self.pi = np.array([p[0] for p in L.PAIRS]); self.pj = np.array([p[1] for p in L.PAIRS])
        self.contacts = T["contacts"].astype(np.float32)

    def f(self, b, tgt):
        """b [M,N] bit arrays, tgt [M] conformation indices -> objective f [M]."""
        self.calls += len(b)
        w = b[:, self.pi] * b[:, self.pj]
        Et = -(w * self.contacts[tgt]).sum(1)
        c = codes_of(b)
        if self.obj == "log":  # graded degeneracy penalty (extra SA baseline); zero iff unique ground state
            return (Et - self.emin[c]) + 0.5 * np.log2(self.cnt[c])
        return (Et - self.emin[c]) + 0.5 * (self.cnt[c] > 1)


def reverse_index(T, des):
    """map each designable conformation to the conformation obtained by reading the chain backwards."""
    key = {T["moves"][c].tobytes(): c for c in des}
    sym = []
    for a in (0, 1):
        for rot in range(4):
            sym.append((a, rot))
    vec = np.array(DIRS)
    out = {}
    for c in des:
        steps = vec[T["moves"][c]]                     # N-1 step vectors (first = +x)
        rsteps = -steps[::-1]                           # reversed walk
        for a, rot in sym:
            st = rsteps.copy()
            if a: st[:, 1] = -st[:, 1]
            for _ in range(rot): st = np.stack([-st[:, 1], st[:, 0]], 1)
            if tuple(st[0]) != (1, 0): continue
            nz = [s for s in st if tuple(s) != (1, 0)]
            if nz and tuple(nz[0]) != (0, 1): continue
            m = np.array([DIRS.index(tuple(s)) for s in st], np.uint8)
            out[c] = key[m.tobytes()]; break
    return out


def splits(T, seed, mode):
    """Split designable conformations into train/test by chain-reversal class (c and its reverse stay together:
    reversing a conformation and its designing sequence gives another valid pair, so splitting them leaks)."""
    cnt1 = np.where(T["cnt"] == 1)[0]
    des = np.unique(T["arg"][cnt1])
    rev = reverse_index(T, des)
    classes = sorted({tuple(sorted((c, rev[c]))) for c in des})
    cl = np.array(classes, dtype=object)
    order = np.random.RandomState(12345).permutation(len(classes))  # global, seed-independent DEV partition
    ndev = int(0.2 * len(classes)); dev_c = [classes[i] for i in order[:ndev]]; pool_c = [classes[i] for i in order[ndev:]]
    flat = lambda cs: np.array(sorted({c for t in cs for c in t}))
    pool_c = [pool_c[i] for i in np.random.RandomState(seed).permutation(len(pool_c))]
    if mode == "tune":
        return flat(pool_c), flat(dev_c)      # train on whole pool, evaluate on DEV
    nte = int(0.25 * len(pool_c))
    return flat(pool_c[nte:]), flat(pool_c[:nte])


def regime(T, tgt):
    cnt1 = np.where(T["cnt"] == 1)[0]
    n = np.bincount(T["arg"][cnt1], minlength=len(T["moves"]))
    return n[tgt]  # number of sequences with unique ground state == target


# ---------------------------------------------------------------- baselines
def run_random(orc, targets, rng):
    K = max(KS)
    best = np.full((len(targets), len(KS)), np.inf)
    cur = np.full(len(targets), np.inf); ki = 0
    for k in range(1, K + 1):
        b = rng.randint(0, 2, size=(len(targets), N))
        cur = np.minimum(cur, orc.f(b, targets))
        if k in KS: best[:, KS.index(k)] = cur
    return best


def sa_run(orc, targets, rng, K, T0, T1, init=None):
    M = len(targets)
    b = rng.randint(0, 2, size=(M, N)) if init is None else init.copy()
    f = orc.f(b, targets); best = f.copy()
    for k in range(1, K):
        T = T0 * (T1 / T0) ** (k / max(K - 1, 1))
        nb = b.copy(); pos = rng.randint(0, N, M); nb[np.arange(M), pos] ^= 1
        nf = orc.f(nb, targets)
        acc = (nf <= f) | (rng.rand(M) < np.exp(-(nf - f) / T))
        b[acc] = nb[acc]; f = np.where(acc, nf, f); best = np.minimum(best, f)
    return best


def run_sa(orc, targets, rng, T0, T1, init=None):
    res = np.zeros((len(targets), len(KS)))
    for a, K in enumerate(KS):
        res[:, a] = sa_run(orc, targets, rng, K, T0, T1, init)
    return res


# ---------------------------------------------------------------- conditional AR model
def make_model(args):
    import torch, torch.nn as nn

    class Net(nn.Module):
        def __init__(s, d=64, conditional=True, drop=0.1):
            super().__init__()
            s.cond = conditional
            s.feat = nn.Linear(N + 4 + 1, d); s.pos = nn.Embedding(N, d); s.tok = nn.Embedding(3, d)  # 0=P,1=H,2=BOS
            enc = nn.TransformerEncoderLayer(d, 4, 4 * d, drop, batch_first=True, norm_first=True)
            dec = nn.TransformerDecoderLayer(d, 4, 4 * d, drop, batch_first=True, norm_first=True)
            s.enc = nn.TransformerEncoder(enc, 2); s.dec = nn.TransformerDecoder(dec, 2)
            s.out = nn.Linear(d, 2)
            s.register_buffer("mask", torch.triu(torch.ones(N, N, dtype=torch.bool), 1))

        def memory(s, M, F):
            x = torch.cat([M, torch.nn.functional.one_hot(F, 4).float(), M.sum(2, keepdim=True)], -1)
            if not s.cond: x = torch.zeros_like(x)
            h = s.feat(x) + s.pos.weight[None]
            return s.enc(h)

        def forward(s, mem, prev):
            n = prev.shape[1]
            h = s.tok(prev) + s.pos.weight[None, :n]
            return s.out(s.dec(h, mem, tgt_mask=s.mask[:n, :n]))

    return Net


def rev_feats(M, F, S):
    return M[:, ::-1, ::-1].copy(), F[:, ::-1].copy(), S[:, ::-1].copy()


def run_ar(T, orc, train, targets, seed, args, rng):
    import torch, torch.nn.functional as Fn
    torch.manual_seed(seed); torch.set_num_threads(2)
    cnt1 = np.where(T["cnt"] == 1)[0]
    # "sampled sequences": a random fraction of sequence space is scored by the oracle
    sub = rng.rand(1 << N) < args.data_frac
    use = cnt1[sub[cnt1] & np.isin(T["arg"][cnt1], train)]
    conf = T["arg"][use]; S = bits(use)
    M, F = features(T, conf)
    if args.augment:
        M2, F2, S2 = rev_feats(M, F, S)
        M, F, S = np.concatenate([M, M2]), np.concatenate([F, F2]), np.concatenate([S, S2])
    n_pairs = len(S)
    # distinct (features, sequence) pairs: at data_frac=1 the reversed pair is already present, so augmentation duplicates
    n_distinct = len(np.unique(np.concatenate([M.reshape(n_pairs, -1), F.reshape(n_pairs, -1), S.reshape(n_pairs, -1)], 1), axis=0))
    Net = make_model(args); net = Net(conditional=bool(args.conditional), drop=args.dropout)
    opt = torch.optim.AdamW(net.parameters(), lr=args.lr, weight_decay=0.01)
    Mt, Ft, St = torch.tensor(M), torch.tensor(F), torch.tensor(S)
    gen = torch.Generator().manual_seed(seed)
    steps_per = max(1, int(np.ceil(n_pairs / args.batch)))
    total = args.epochs * steps_per; sched = torch.optim.lr_scheduler.OneCycleLR(opt, args.lr, total_steps=total)
    bos = torch.full((1, 1), 2, dtype=torch.long)
    for ep in range(args.epochs):
        net.train(); perm = torch.randperm(n_pairs, generator=gen)
        for s0 in range(0, n_pairs, args.batch):
            ix = perm[s0:s0 + args.batch]
            s = St[ix]; prev = torch.cat([bos.expand(len(ix), 1), s[:, :-1]], 1)
            logit = net(net.memory(Mt[ix], Ft[ix]), prev)
            loss = Fn.cross_entropy(logit.reshape(-1, 2), s.reshape(-1))
            opt.zero_grad(); loss.backward(); opt.step(); sched.step()
    net.eval()
    tM, tF = features(T, targets)
    tM, tF = torch.tensor(tM), torch.tensor(tF)
    # held-out NLL of the true designing sequences of the target conformations
    nll = float("nan")
    usef = cnt1[np.isin(T["arg"][cnt1], targets)]
    with torch.no_grad():
        if len(usef):
            conf_t = T["arg"][usef]; Mq, Fq = features(T, conf_t); Sq = torch.tensor(bits(usef))
            prev = torch.cat([bos.expand(len(usef), 1), Sq[:, :-1]], 1)
            lg = net(net.memory(torch.tensor(Mq), torch.tensor(Fq)), prev)
            nll = Fn.cross_entropy(lg.reshape(-1, 2), Sq.reshape(-1)).item()
        K = max(KS); n_t = len(targets)
        best = np.full((n_t, len(KS)), np.inf)
        # sample K sequences per target in chunks of targets
        allf = np.zeros((n_t, K))
        g2 = torch.Generator().manual_seed(seed + 777)
        for t0 in range(0, n_t, 8):
            sl = slice(t0, min(n_t, t0 + 8)); nt = sl.stop - sl.start
            mem = net.memory(tM[sl], tF[sl]).repeat_interleave(K, 0)
            seq = torch.full((nt * K, 1), 2, dtype=torch.long)
            for i in range(N):
                lg = net(mem, seq)[:, -1] / args.tau
                nxt = torch.multinomial(torch.softmax(lg, -1), 1, generator=g2)
                seq = torch.cat([seq, nxt], 1)
            b = seq[:, 1:].numpy()
            tg = np.repeat(targets[sl], K)
            allf[sl] = orc.f(b, tg).reshape(nt, K)
    cm = np.minimum.accumulate(allf, axis=1)
    for a, k in enumerate(KS): best[:, a] = cm[:, k - 1]
    return best, dict(train_pairs=n_pairs, **({"distinct_pairs": n_distinct} if args.report_distinct else {}), test_nll=nll, sample_rate=float((allf == 0).mean()))


def run_heuristic(T, orc, targets):
    """deterministic: residue is H iff it has at least one contact in the target (one design, repeated for every K)."""
    M, _ = features(T, targets)
    b = (M.sum(2) > 0).astype(np.int64)
    f = orc.f(b, targets)
    return np.repeat(f[:, None], len(KS), 1)


def main():
    global KS
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True); ap.add_argument("--task", default="hp16")
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out", default=os.environ.get("RH_METRICS_FILE"))
    ap.add_argument("--mode", default="test")
    ap.add_argument("--epochs", type=int, default=100); ap.add_argument("--tau", type=float, default=1.0)
    ap.add_argument("--lr", type=float, default=2e-3); ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--dropout", type=float, default=0.1)
    ap.add_argument("--data_frac", type=float, default=1.0)
    ap.add_argument("--augment", type=int, default=1); ap.add_argument("--conditional", type=int, default=1)
    ap.add_argument("--T0", type=float, default=1.0); ap.add_argument("--T1", type=float, default=0.1)
    ap.add_argument("--obj", default="bin"); ap.add_argument("--report_distinct", type=int, default=0)
    ap.add_argument("--kmax", type=int, default=1000)
    args = ap.parse_args()
    KS = [k for k in ALL_KS if k <= args.kmax]
    print("config", json.dumps(vars(args)), flush=True)
    t0 = time.time()
    T = L.load(); orc = Oracle(T, args.obj)
    train, targets = splits(T, args.seed, args.mode)
    rng = np.random.RandomState(args.seed)
    extra = {}
    if args.system == "random": res = run_random(orc, targets, rng)
    elif args.system == "heuristic": res = run_heuristic(T, orc, targets)
    elif args.system == "sa": res = run_sa(orc, targets, rng, args.T0, args.T1)
    elif args.system == "sa_warm":  # SA started from the contact-heuristic sequence
        res = run_sa(orc, targets, rng, args.T0, args.T1, (features(T, targets)[0].sum(2) > 0).astype(np.int64))
    elif args.system == "ar": res, extra = run_ar(T, orc, train, targets, args.seed, args, rng)
    else: raise SystemExit("unknown system")
    out = {}
    reg = regime(T, targets); single = reg == 1
    for a, k in enumerate(KS):
        ok = res[:, a] == 0
        out[f"succ_k{k}"] = float(ok.mean())
        if args.obj == "bin": out[f"gap_k{k}"] = float(np.floor(res[:, a]).mean())  # energy gap of the best design (0.5 degeneracy penalty dropped)
        if k in (10, 100):
            out[f"succ_k{k}_single"] = float(ok[single].mean()) if single.any() else float("nan")
            out[f"succ_k{k}_multi"] = float(ok[~single].mean()) if (~single).any() else float("nan")
    out["n_targets"] = int(len(targets)); out["n_train_conf"] = int(len(train))
    out["n_single_targets"] = int(single.sum())
    for k, v in extra.items():
        out[k] = v
    print("metrics", json.dumps(out), "elapsed", round(time.time() - t0, 1), flush=True)
    if args.out: json.dump(out, open(args.out, "w"))


if __name__ == "__main__":
    main()
