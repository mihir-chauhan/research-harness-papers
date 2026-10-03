"""Learned tactic policies: a small transformer over prefix-notation tokens and a feature-based MLP.
Both score every candidate tactic (compound formula on a side) of a goal; the policy is a softmax over candidates."""
import math
import numpy as np
import torch
import torch.nn as nn
from logic import candidates, size, depth, atoms, NVARS

PAD, CLS, SEP, COMMA = 0, 1, 2, 3
VAR0 = 4
OPS = {'not': VAR0 + NVARS, 'and': VAR0 + NVARS + 1, 'or': VAR0 + NVARS + 2, 'imp': VAR0 + NVARS + 3}
VOCAB = VAR0 + NVARS + 4


def prefix(f, out, root_marker=None):
    if f[0] == 'v':
        out.append(VAR0 + f[1])
    else:
        out.append(OPS[f[0]])
        for g in f[1:]:
            prefix(g, out)


def encode(goal):
    """-> tokens, segments, root positions (aligned with candidates(goal))"""
    toks, segs, roots = [CLS], [0], {}
    for side in (0, 1):
        for i, f in enumerate(goal[side]):
            roots[(side, i)] = len(toks)
            t = []
            prefix(f, t)
            toks += t
            segs += [side] * len(t)
            toks.append(COMMA if i < len(goal[side]) - 1 else SEP)
            segs.append(side)
    return toks, segs, [roots[c] for c in candidates(goal)]


def sinusoid(n, d):
    pos = torch.arange(n).float()[:, None]
    div = torch.exp(torch.arange(0, d, 2).float() * (-math.log(10000.0) / d))
    pe = torch.zeros(n, d)
    pe[:, 0::2] = torch.sin(pos * div)
    pe[:, 1::2] = torch.cos(pos * div)
    return pe


class TransformerPolicy(nn.Module):
    def __init__(self, d=64, layers=3, heads=4, ff=256, pos='sin', maxlen=256):
        super().__init__()
        self.d, self.pos, self.maxlen = d, pos, maxlen
        self.tok = nn.Embedding(VOCAB, d, padding_idx=PAD)
        self.seg = nn.Embedding(2, d)
        if pos == 'learned':
            self.pe = nn.Embedding(maxlen, d)
        layer = nn.TransformerEncoderLayer(d, heads, ff, dropout=0.0, batch_first=True, norm_first=True)
        self.enc = nn.TransformerEncoder(layer, layers, enable_nested_tensor=False)
        self.norm = nn.LayerNorm(d)
        self.head = nn.Sequential(nn.Linear(d, d), nn.GELU(), nn.Linear(d, 1))

    def forward(self, toks, segs, roots, rmask):
        B, L = toks.shape
        x = self.tok(toks) + self.seg(segs)
        if self.pos == 'sin':
            x = x + sinusoid(L, self.d)[None]
        else:
            x = x + self.pe(torch.clamp(torch.arange(L), max=self.maxlen - 1))[None]
        h = self.norm(self.enc(x, src_key_padding_mask=(toks == PAD)))
        hc = torch.gather(h, 1, roots[:, :, None].expand(-1, -1, self.d))
        lg = self.head(hc).squeeze(-1)
        return lg.masked_fill(~rmask, -1e9)


def batch_tf(items):
    """items: list of (tokens, segs, roots)"""
    B = len(items)
    L = max(len(t) for t, _, _ in items)
    K = max(len(r) for _, _, r in items)
    toks = torch.zeros(B, L, dtype=torch.long)
    segs = torch.zeros(B, L, dtype=torch.long)
    roots = torch.zeros(B, K, dtype=torch.long)
    rmask = torch.zeros(B, K, dtype=torch.bool)
    for b, (t, s, r) in enumerate(items):
        toks[b, :len(t)] = torch.tensor(t)
        segs[b, :len(s)] = torch.tensor(s)
        roots[b, :len(r)] = torch.tensor(r)
        rmask[b, :len(r)] = True
    return toks, segs, roots, rmask


# ---------------- feature MLP ----------------
NF = 8 + 4 + 8 + 4


def features(goal):
    """Per-candidate feature rows [K, NF]: (side x connective one-hot), size, depth, atom overlap with the opposite
    side's top-level atoms, and sequent-level context (counts of compound formulas per side x connective, sizes)."""
    cands = candidates(goal)
    ctx = np.zeros(8)
    for side in (0, 1):
        for f in goal[side]:
            if f[0] != 'v':
                ctx[side * 4 + ['not', 'and', 'or', 'imp'].index(f[0])] += 1
    total = sum(size(f) for f in goal[0] + goal[1])
    top_atoms = [{f[1] for f in goal[s] if f[0] == 'v'} for s in (0, 1)]
    rows = []
    for side, i in cands:
        f = goal[side][i]
        oh = np.zeros(8)
        oh[side * 4 + ['not', 'and', 'or', 'imp'].index(f[0])] = 1
        a = atoms(f)
        misc = np.array([size(f) / 10.0, depth(f) / 5.0, len(a & top_atoms[1 - side]) / 3.0, len(a & top_atoms[side]) / 3.0])
        g = np.array([total / 20.0, len(goal[0]) / 3.0, len(goal[1]) / 3.0, len(cands) / 5.0])
        rows.append(np.concatenate([oh, misc, ctx / 3.0, g]))
    return np.array(rows, dtype=np.float32)


class MLPPolicy(nn.Module):
    def __init__(self, h=128):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(NF, h), nn.ReLU(), nn.Linear(h, h), nn.ReLU(), nn.Linear(h, 1))

    def forward(self, feats, rmask):
        return self.net(feats).squeeze(-1).masked_fill(~rmask, -1e9)


def batch_mlp(items):
    B, K = len(items), max(len(x) for x in items)
    f = torch.zeros(B, K, NF)
    m = torch.zeros(B, K, dtype=torch.bool)
    for b, x in enumerate(items):
        f[b, :len(x)] = torch.from_numpy(x)
        m[b, :len(x)] = True
    return f, m
