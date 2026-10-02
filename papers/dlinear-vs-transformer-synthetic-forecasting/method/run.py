"""Long-horizon forecasting study: seasonal naive, DLinear-style, patch transformer, GRU.

Usage: python method/run.py --system dlinear --task regime --seed 0 --out metrics.json
Writes a flat JSON {"mse_24": ..., "mae_24": ..., ...} (z-scored units, chronological test split).
"""
import argparse, json, math, os, time
os.environ.setdefault("OMP_NUM_THREADS", "2"); os.environ.setdefault("MKL_NUM_THREADS", "2")
import numpy as np
import torch, torch.nn as nn

torch.set_num_threads(2)
LOOKBACK = 336
SYSTEMS = ["snaive", "dlinear", "linear", "patchtst", "gru"]

# ---------------------------------------------------------------- data
TASKS = {  # name -> generator parameters
    "seas1":     dict(periods=[24], amps=[1.0], trend=0.0, noise=0.3, dwell=0),
    "trend":     dict(periods=[24], amps=[1.0], trend=1.0, noise=0.3, dwell=0),
    "multiseas": dict(periods=[24, 168, 12], amps=[1.0, 0.7, 0.4], trend=0.0, noise=0.3, dwell=0),
    "noisy":     dict(periods=[24, 168, 12], amps=[1.0, 0.7, 0.4], trend=0.0, noise=1.5, dwell=0),
    "regime":    dict(periods=[24, 168, 12], amps=[1.0, 0.7, 0.4], trend=0.0, noise=0.3, dwell=500),
    "etth1":     None,
}
# alternative regimes: each rescales the periods and amplitudes of the base components
REGIME_PERIOD_SCALE = [1.0, 1.6, 0.6]
REGIME_AMP_SCALE = [[1, 1, 1], [0.5, 1.2, 1.0], [1.3, 0.3, 1.5]]


def gen_series(rng, n, periods, amps, trend, noise, dwell, rho=0.5):
    t = np.arange(n)
    # regime path (0 if dwell == 0): geometric dwell times, next regime uniformly among the others
    reg = np.zeros(n, dtype=int)
    if dwell > 0:
        i, r = 0, 0
        while i < n:
            d = int(rng.geometric(1.0 / dwell))
            reg[i:i + d] = r
            i += d
            r = int(rng.choice([k for k in range(3) if k != r]))
    y = np.zeros(n)
    for k, (P, A) in enumerate(zip(periods, amps)):
        Pt = P * np.array(REGIME_PERIOD_SCALE)[reg]
        At = A * np.array(REGIME_AMP_SCALE)[:, k][reg]
        phase = rng.uniform(0, 2 * np.pi) + np.cumsum(2 * np.pi / Pt)  # integrated phase: continuous at switches
        y += At * np.sin(phase)
    if trend > 0:  # piecewise-linear trend, slope redrawn every ~1000 steps
        slope = np.zeros(n); i = 0
        while i < n:
            d = int(rng.integers(600, 1400)); slope[i:i + d] = rng.normal(0, trend * 3e-3); i += d
        y += np.cumsum(slope)
    e = np.zeros(n); eps = rng.normal(0, noise, n)
    for i in range(1, n):
        e[i] = rho * e[i - 1] + eps[i] * math.sqrt(1 - rho ** 2)
    return y + e


def load_task(task, seed, a):
    """Returns array (n, C) and split borders (train_end, val_end)."""
    if task == "etth1":
        import pandas as pd
        x = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "data", "ETTh1.csv")).iloc[:, 1:].values.astype(np.float64)
        x = x[:14400]
        return x, 8640, 11520
    p = dict(TASKS[task])
    if a.noise is not None: p["noise"] = a.noise
    if a.dwell is not None: p["dwell"] = a.dwell
    rng = np.random.default_rng(1000 + seed)
    n = 8000
    x = np.stack([gen_series(rng, n, **p) for _ in range(4)], 1)
    return x, int(0.6 * n), int(0.8 * n)


def windows(x, lo, hi, H):
    """All (lookback, horizon) windows whose target lies in [lo, hi); x is (n, C)."""
    starts = np.arange(lo - LOOKBACK, hi - LOOKBACK - H + 1)
    starts = starts[starts >= 0]
    return starts


def make_batch(x, starts, H, ch):
    idx = starts[:, None] + np.arange(LOOKBACK + H)[None, :]
    w = x[idx, ch[:, None]]  # (B, L+H)
    return torch.tensor(w[:, :LOOKBACK], dtype=torch.float32), torch.tensor(w[:, LOOKBACK:], dtype=torch.float32)


# ---------------------------------------------------------------- models
class InstNorm(nn.Module):
    """Per-window mean/std normalisation of the input; the output is de-normalised."""
    def __init__(self, on): super().__init__(); self.on = on
    def fwd(self, x):
        if not self.on: return x, 0.0, 1.0
        m = x.mean(1, keepdim=True); s = x.std(1, keepdim=True) + 1e-5
        return (x - m) / s, m, s


class DLinear(nn.Module):
    def __init__(self, H, norm, decomp=True, k=25):
        super().__init__(); self.norm = InstNorm(norm); self.decomp, self.k = decomp, k
        self.seas = nn.Linear(LOOKBACK, H)
        if decomp: self.trend = nn.Linear(LOOKBACK, H)
        for l in ([self.seas] + ([self.trend] if decomp else [])):  # DLinear init: uniform average
            nn.init.constant_(l.weight, 1.0 / LOOKBACK); nn.init.zeros_(l.bias)
    def forward(self, x):
        x, m, s = self.norm.fwd(x)
        if not self.decomp: return self.seas(x) * s + m
        pad = torch.cat([x[:, :1].repeat(1, (self.k - 1) // 2), x, x[:, -1:].repeat(1, (self.k - 1) // 2)], 1)
        tr = pad.unfold(1, self.k, 1).mean(-1)
        return (self.seas(x - tr) + self.trend(tr)) * s + m


class PatchTST(nn.Module):
    def __init__(self, H, norm, P=16, S=8, d=64, L=2, heads=4, ff=128, drop=0.1):
        super().__init__(); self.norm = InstNorm(norm); self.P, self.S = P, S
        n = (LOOKBACK - P) // S + 1
        self.emb = nn.Linear(P, d); self.pos = nn.Parameter(torch.randn(1, n, d) * 0.02)
        layer = nn.TransformerEncoderLayer(d, heads, ff, drop, batch_first=True, norm_first=True)
        self.enc = nn.TransformerEncoder(layer, L, enable_nested_tensor=False)
        self.head = nn.Linear(n * d, H)
    def forward(self, x):
        x, m, s = self.norm.fwd(x)
        z = self.enc(self.emb(x.unfold(1, self.P, self.S)) + self.pos)
        return self.head(z.flatten(1)) * s + m


class GRUNet(nn.Module):
    def __init__(self, H, norm, P=8, d=64):
        super().__init__(); self.norm = InstNorm(norm); self.P = P
        self.rnn = nn.GRU(P, d, batch_first=True); self.head = nn.Linear(d, H)
    def forward(self, x):
        x, m, s = self.norm.fwd(x)
        _, h = self.rnn(x.unfold(1, self.P, self.P))  # non-overlapping patches as time steps
        return self.head(h[-1]) * s + m


def build(system, H, norm):
    return {"dlinear": lambda: DLinear(H, norm), "linear": lambda: DLinear(H, norm, decomp=False),
            "patchtst": lambda: PatchTST(H, norm), "gru": lambda: GRUNet(H, norm)}[system]()


# ---------------------------------------------------------------- evaluation
def evaluate(pred_fn, x, lo, hi, H, bs=512, stride=1):
    C = x.shape[1]; starts = windows(x, lo, hi, H)[::stride]
    se = ae = n = 0.0
    for c in range(C):
        for i in range(0, len(starts), bs):
            s = starts[i:i + bs]; xb, yb = make_batch(x, s, H, np.full(len(s), c))
            with torch.no_grad(): p = pred_fn(xb)
            se += ((p - yb) ** 2).sum().item(); ae += (p - yb).abs().sum().item(); n += yb.numel()
    return se / n, ae / n


def snaive_fn(m, H):
    def f(xb):
        idx = [LOOKBACK - m + (h % m) for h in range(H)]
        return xb[:, idx]
    return f


def train_eval(system, x, tr_end, va_end, H, a, seed):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    model = build(system, H, not a.no_norm)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, a.steps)
    starts = windows(x, 0, tr_end, H)
    best, best_state = float("inf"), None
    for step in range(1, a.steps + 1):
        model.train()
        s = rng.choice(starts, a.bs); ch = rng.integers(0, x.shape[1], a.bs)
        xb, yb = make_batch(x, s, H, ch)
        loss = ((model(xb) - yb) ** 2).mean()
        opt.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sched.step()
        if step % a.eval_every == 0 or step == a.steps:
            model.eval(); v, _ = evaluate(model, x, tr_end, va_end, H, stride=8)  # validation split only, every 8th window
            if v < best: best, best_state = v, {k: t.clone() for k, t in model.state_dict().items()}
    model.load_state_dict(best_state); model.eval()
    return model, best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True, choices=SYSTEMS); ap.add_argument("--task", required=True, choices=list(TASKS))
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out", required=True)
    ap.add_argument("--horizons", default="24,96,192")
    ap.add_argument("--lr", type=float, default=None); ap.add_argument("--steps", type=int, default=400)
    ap.add_argument("--bs", type=int, default=64); ap.add_argument("--eval_every", type=int, default=100)
    ap.add_argument("--no_norm", action="store_true", help="disable instance normalisation")
    ap.add_argument("--noise", type=float, default=None); ap.add_argument("--dwell", type=int, default=None)
    ap.add_argument("--split", default="test", choices=["test", "val"], help="split to report (the registry only contains test runs)")
    a = ap.parse_args()
    if a.lr is None: a.lr = {"dlinear": 3e-3, "linear": 3e-3, "patchtst": 1e-3, "gru": 3e-3}.get(a.system, 0)
    print("config", json.dumps(vars(a)), flush=True)
    t0 = time.time()
    x, tr_end, va_end = load_task(a.task, a.seed, a)
    mu, sd = x[:tr_end].mean(0), x[:tr_end].std(0)
    x = (x - mu) / sd  # z-score with training statistics only
    lo, hi = (va_end, len(x)) if a.split == "test" else (tr_end, va_end)
    out = {}
    for H in [int(h) for h in a.horizons.split(",")]:
        if a.system == "snaive":
            cands = {m: evaluate(snaive_fn(m, H), x, tr_end, va_end, H)[0] for m in (24, 168)}
            m = min(cands, key=cands.get)  # period chosen on validation
            mse, mae = evaluate(snaive_fn(m, H), x, lo, hi, H); out[f"snaive_period_{H}"] = m
        else:
            model, vbest = train_eval(a.system, x, tr_end, va_end, H, a, a.seed)
            mse, mae = evaluate(model, x, lo, hi, H); out[f"val_mse_{H}"] = vbest
        out[f"mse_{H}"], out[f"mae_{H}"] = mse, mae
        print(f"H={H} mse={mse:.4f} mae={mae:.4f}", flush=True)
    out["mse_mean"] = float(np.mean([out[f"mse_{int(h)}"] for h in a.horizons.split(",")]))
    out["runtime_s"] = time.time() - t0
    if a.system != "snaive": out["n_params_h96"] = sum(p.numel() for p in build(a.system, 96, True).parameters())
    print("final", json.dumps(out), flush=True)
    json.dump(out, open(a.out, "w"))


if __name__ == "__main__":
    main()
