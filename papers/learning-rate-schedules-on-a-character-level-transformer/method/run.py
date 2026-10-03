"""Char-level GPT on Tiny Shakespeare with four LR schedules (all AdamW-family)."""
import argparse, json, math, time, os
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
torch.set_num_threads(2)

ap = argparse.ArgumentParser()
ap.add_argument("--system", required=True)  # constant | cosine | step | schedulefree
ap.add_argument("--lr", type=float, required=True)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--warmup", type=int, default=-1)  # -1 = system default
ap.add_argument("--steps", type=int, default=1500)
ap.add_argument("--batch", type=int, default=32)
ap.add_argument("--block", type=int, default=64)
ap.add_argument("--wd", type=float, default=0.1)
ap.add_argument("--out", required=True)
ap.add_argument("--curve", default="")
a = ap.parse_args()
print("config", json.dumps(vars(a)))

text = open(os.path.join(os.path.dirname(__file__), "..", "data", "shakespeare.txt")).read()
chars = sorted(set(text)); V = len(chars); stoi = {c: i for i, c in enumerate(chars)}
data = torch.tensor([stoi[c] for c in text], dtype=torch.long)
n_tr = int(0.9 * len(data)); train, val = data[:n_tr], data[n_tr:]
# fixed validation windows (same for every run)
g = torch.Generator().manual_seed(12345)
vi = torch.randint(0, len(val) - a.block - 1, (256,), generator=g)
vx = torch.stack([val[i:i + a.block] for i in vi]); vy = torch.stack([val[i + 1:i + a.block + 1] for i in vi])

torch.manual_seed(a.seed); np.random.seed(a.seed)
D, H, L = 128, 4, 2
class Block(nn.Module):
    def __init__(s):
        super().__init__()
        s.ln1 = nn.LayerNorm(D); s.ln2 = nn.LayerNorm(D)
        s.qkv = nn.Linear(D, 3 * D); s.proj = nn.Linear(D, D)
        s.fc = nn.Linear(D, 4 * D); s.fo = nn.Linear(4 * D, D)
    def forward(s, x):
        B, T, _ = x.shape
        q, k, v = s.qkv(s.ln1(x)).view(B, T, 3, H, D // H).permute(2, 0, 3, 1, 4)
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True).transpose(1, 2).reshape(B, T, D)
        x = x + s.proj(y)
        return x + s.fo(F.gelu(s.fc(s.ln2(x))))
class GPT(nn.Module):
    def __init__(s):
        super().__init__()
        s.te = nn.Embedding(V, D); s.pe = nn.Embedding(a.block, D)
        s.blocks = nn.ModuleList([Block() for _ in range(L)]); s.lnf = nn.LayerNorm(D)
        s.head = nn.Linear(D, V, bias=False)
        for m in s.modules():
            if isinstance(m, (nn.Linear, nn.Embedding)): nn.init.normal_(m.weight, std=0.02)
            if isinstance(m, nn.Linear) and m.bias is not None: nn.init.zeros_(m.bias)
    def forward(s, x, y):
        h = s.te(x) + s.pe(torch.arange(x.shape[1]))
        for b in s.blocks: h = b(h)
        return F.cross_entropy(s.head(s.lnf(h)).view(-1, V), y.view(-1))
model = GPT()
params = [p for p in model.parameters()]
decay = [p for p in params if p.dim() >= 2]; nodecay = [p for p in params if p.dim() < 2]
for p in params: pass

def batch(rng):
    i = rng.integers(0, n_tr - a.block - 1, a.batch)
    return (torch.stack([train[j:j + a.block] for j in i]), torch.stack([train[j + 1:j + a.block + 1] for j in i]))

DEFAULT_WARM = {"constant": 0, "cosine": 100, "step": 0, "schedulefree": 100}
W = DEFAULT_WARM[a.system] if a.warmup < 0 else a.warmup
T = a.steps
def lr_at(t):  # t = 0-based step
    w = min(1.0, (t + 1) / W) if W > 0 else 1.0
    if a.system in ("constant", "schedulefree"): return a.lr * w
    if a.system == "cosine":
        if t < W: return a.lr * w
        pr = (t - W) / max(1, T - W)
        return a.lr * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * pr)))
    if a.system == "step":
        return a.lr * w * (0.3 ** ((t >= T // 3) + (t >= 2 * T // 3)))
    raise ValueError(a.system)

b1, b2, eps = 0.9, 0.95, 1e-8
m = [torch.zeros_like(p) for p in params]; v = [torch.zeros_like(p) for p in params]
isdec = [p.dim() >= 2 for p in params]
sf = a.system == "schedulefree"
if sf:
    z = [p.detach().clone() for p in params]; x = [p.detach().clone() for p in params]; Wsum = 0.0

def evaluate(use_x):
    if sf and use_x:
        saved = [p.detach().clone() for p in params]
        with torch.no_grad():
            for p, xi in zip(params, x): p.copy_(xi)
    model.eval()
    with torch.no_grad(): l = float(model(vx, vy))
    model.train()
    if sf and use_x:
        with torch.no_grad():
            for p, s_ in zip(params, saved): p.copy_(s_)
    return l

rng = np.random.default_rng(a.seed + 1000)
curve = []; tl = []; t0 = time.time(); diverged = False
for t in range(T):
    xb, yb = batch(rng)
    loss = model(xb, yb)
    if not math.isfinite(float(loss)): diverged = True; break
    for p in params: p.grad = None
    loss.backward()
    torch.nn.utils.clip_grad_norm_(params, 1.0)
    lr = lr_at(t); tl.append(float(loss))
    bc2 = 1 - b2 ** (t + 1)
    with torch.no_grad():
        if not sf:
            bc1 = 1 - b1 ** (t + 1)
            for i, p in enumerate(params):
                gr = p.grad
                m[i].mul_(b1).add_(gr, alpha=1 - b1); v[i].mul_(b2).addcmul_(gr, gr, value=1 - b2)
                if isdec[i]: p.mul_(1 - lr * a.wd)
                p.addcdiv_(m[i] / bc1, (v[i] / bc2).sqrt().add_(eps), value=-lr)
        else:  # Schedule-Free AdamW (Defazio et al. 2024), r=0, weight power 2; p holds y
            Wsum += lr ** 2; c = lr ** 2 / Wsum
            for i, p in enumerate(params):
                gr = p.grad
                v[i].mul_(b2).addcmul_(gr, gr, value=1 - b2)
                step = gr / ((v[i] / bc2).sqrt() + eps)
                if isdec[i]: step = step + a.wd * p
                z[i].add_(step, alpha=-lr)
                x[i].mul_(1 - c).add_(z[i], alpha=c)
                p.copy_(x[i] * b1 + z[i] * (1 - b1))
    if (t + 1) % 150 == 0 and a.curve:
        curve.append((t + 1, evaluate(True)))
if diverged: val_loss = float("nan")
else: val_loss = evaluate(True)
out = {"val_loss": val_loss if not diverged else 10.0, "train_loss": float(np.mean(tl[-100:])) if tl else 10.0,
       "diverged": float(diverged or val_loss > 4.0)}
if sf and not diverged: out["val_loss_y"] = evaluate(False)
print("final", json.dumps(out), "time %.1fs" % (time.time() - t0))
json.dump(out, open(a.out, "w"))
if a.curve:
    with open(a.curve, "w") as f:
        f.write("step,value,seed,name\n")
        for s_, vl in curve: f.write(f"{s_},{vl},{a.seed},{a.system}_{a.lr}\n")
