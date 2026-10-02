"""One entrypoint: train one system on Burgers (u0 -> u(T=1)) at 128 points, evaluate at 128 and zero-shot at 256 / 512.
python method/run.py --system fno|deeponet|mlp|cnn --seed S --out metrics.json [--modes 16 --width 32 --lr 1e-3 --epochs 300 --n_train 400]
"""
import argparse, json, time, sys, os
import numpy as np
import torch, torch.nn as nn, torch.nn.functional as F

sys.path.insert(0, os.path.dirname(__file__))
from data import make_dataset

torch.set_num_threads(2)
N_VAL, N_TEST = 100, 100


# ---------------- models ----------------
class SpectralConv1d(nn.Module):
    """y = irfft( W_k * rfft(v)_k ) for the lowest `modes` frequencies, complex weights W_k in C^{c x c} (Li et al. 2020)."""
    def __init__(self, c, modes):
        super().__init__()
        self.modes = modes
        self.w = nn.Parameter(torch.randn(c, c, modes, dtype=torch.cfloat) / c)

    def forward(self, v):
        n = v.shape[-1]
        vh = torch.fft.rfft(v, dim=-1)
        out = torch.zeros(v.shape[0], v.shape[1], n // 2 + 1, dtype=torch.cfloat)
        out[..., : self.modes] = torch.einsum("bix,iox->box", vh[..., : self.modes], self.w)
        return torch.fft.irfft(out, n=n, dim=-1)


class FNO1d(nn.Module):
    def __init__(self, modes=16, width=32, layers=4, use_grid=True):
        super().__init__()
        self.use_grid = use_grid
        self.lift = nn.Linear(2 if use_grid else 1, width)
        self.spec = nn.ModuleList([SpectralConv1d(width, modes) for _ in range(layers)])
        self.skip = nn.ModuleList([nn.Conv1d(width, width, 1) for _ in range(layers)])
        self.p1, self.p2 = nn.Linear(width, 128), nn.Linear(128, 1)

    def forward(self, u):  # u: (b, n)
        n = u.shape[-1]
        feats = [u]
        if self.use_grid:
            feats.append((torch.arange(n) / n).expand_as(u))
        v = self.lift(torch.stack(feats, -1)).transpose(1, 2)
        for i, (s, w) in enumerate(zip(self.spec, self.skip)):
            v = s(v) + w(v)
            if i < len(self.spec) - 1:
                v = F.gelu(v)
        return self.p2(F.gelu(self.p1(v.transpose(1, 2)))).squeeze(-1)


def mlp(sizes):
    layers = []
    for i in range(len(sizes) - 1):
        layers.append(nn.Linear(sizes[i], sizes[i + 1]))
        if i < len(sizes) - 2:
            layers.append(nn.GELU())
    return nn.Sequential(*layers)


class DeepONet(nn.Module):
    """G(u)(y) = sum_k b_k(u(x_1..x_m)) t_k(y) + b0 ; branch sees the 128 training-grid sensors, trunk sees the query y."""
    def __init__(self, m=128, p=64, hidden=128):
        super().__init__()
        self.branch = mlp([m, hidden, hidden, p])
        self.trunk = mlp([1, hidden, hidden, p])
        self.m, self.b0 = m, nn.Parameter(torch.zeros(1))

    def forward(self, u, n_out=None):
        n_out = n_out or u.shape[-1]
        u = u[:, :: u.shape[-1] // self.m]  # sensors are always the 128 training-grid points
        y = (torch.arange(n_out) / n_out).unsqueeze(-1)
        return self.branch(u) @ self.trunk(y).T + self.b0


class PlainMLP(nn.Module):
    def __init__(self, m=128, hidden=512):
        super().__init__()
        self.net, self.m = mlp([m, hidden, hidden, m]), m

    def forward(self, u):
        return self.net(u[:, :: u.shape[-1] // self.m])  # always a 128-point output


class CNN1d(nn.Module):
    """Plain fully convolutional net, circular padding, kernel 9, 6 conv layers (receptive field 49 points); no pooling."""
    def __init__(self, ch=32, layers=6, k=9):
        super().__init__()
        cs = [1] + [ch] * (layers - 1) + [1]
        self.convs = nn.ModuleList([nn.Conv1d(cs[i], cs[i + 1], k, padding=k // 2, padding_mode="circular") for i in range(layers)])

    def forward(self, u):
        v = u.unsqueeze(1)
        for i, c in enumerate(self.convs):
            v = c(v)
            if i < len(self.convs) - 1:
                v = F.gelu(v)
        return v.squeeze(1)


def build(a):
    if a.system == "fno":
        return FNO1d(a.modes, a.width, 4, use_grid=bool(a.grid))
    return {"deeponet": DeepONet, "mlp": PlainMLP, "cnn": CNN1d}[a.system]()


# ---------------- helpers ----------------
def trig_interp(v, n_out):
    """Fourier (band-limited) interpolation of samples v (b, n) to n_out points."""
    n = v.shape[-1]
    vh = torch.fft.rfft(v, dim=-1)
    out = torch.zeros(v.shape[0], n_out // 2 + 1, dtype=torch.cfloat)
    out[:, : n // 2] = vh[:, : n // 2]
    return torch.fft.irfft(out, n=n_out, dim=-1) * (n_out / n)


def rel_l2(pred, true):
    return (torch.linalg.norm(pred - true, dim=-1) / torch.linalg.norm(true, dim=-1)).mean().item()


@torch.no_grad()
def predict(model, system, u, n_out):
    """Native application on the grid of u. MLP has a fixed 128-point output (trig-interpolated to n_out)."""
    out = model(u)
    if out.shape[-1] != n_out:
        out = trig_interp(out, n_out)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--system", required=True, choices=["fno", "deeponet", "mlp", "cnn"])
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", required=True)
    p.add_argument("--modes", type=int, default=16)
    p.add_argument("--width", type=int, default=32)
    p.add_argument("--grid", type=int, default=1)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--epochs", type=int, default=300)
    p.add_argument("--batch", type=int, default=20)
    p.add_argument("--n_train", type=int, default=400)
    p.add_argument("--data_seed", type=int, default=None, help="default: = seed")
    a = p.parse_args()
    print("CONFIG", json.dumps(vars(a)), flush=True)
    torch.manual_seed(a.seed); np.random.seed(a.seed)
    dseed = a.seed if a.data_seed is None else a.data_seed
    ds = make_dataset(400 + N_VAL + N_TEST, 1000 + dseed)  # fixed pool; n_train takes the first n_train of the 400 train samples
    T = {r: tuple(torch.tensor(z, dtype=torch.float32) for z in ds[r]) for r in ds}
    tr = slice(0, a.n_train); va = slice(400, 400 + N_VAL); te = slice(400 + N_VAL, 400 + N_VAL + N_TEST)
    x_tr, y_tr = T[128][0][tr], T[128][1][tr]
    scale = x_tr.std().item()  # global input/output scaling by the training-set std (one scalar, same for all systems)

    model = build(a)
    n_par = sum(q.numel() * (2 if q.is_complex() else 1) for q in model.parameters())
    opt = torch.optim.Adam(model.parameters(), lr=a.lr, weight_decay=1e-5)
    steps = a.epochs * int(np.ceil(a.n_train / a.batch))
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=a.lr, total_steps=steps, pct_start=0.1)
    best, best_state, t0 = 1e9, None, time.time()
    for ep in range(a.epochs):
        model.train()
        perm = torch.randperm(a.n_train)
        for i in range(0, a.n_train, a.batch):
            idx = perm[i : i + a.batch]
            pred = model(x_tr[idx] / scale) * scale
            loss = (torch.linalg.norm(pred - y_tr[idx], dim=-1) / torch.linalg.norm(y_tr[idx], dim=-1)).mean()
            opt.zero_grad(); loss.backward(); opt.step(); sched.step()
        if (ep + 1) % 10 == 0 or ep == a.epochs - 1:
            model.eval()
            v = rel_l2(predict(model, a.system, T[128][0][va] / scale, 128) * scale, T[128][1][va])
            if v < best:
                best, best_state = v, {k: t.clone() for k, t in model.state_dict().items()}
            if (ep + 1) % 50 == 0:
                print(f"ep {ep+1} train_loss {loss.item():.4f} val {v:.4f}", flush=True)
    train_s = time.time() - t0
    model.load_state_dict(best_state); model.eval()

    def ev(res, split, resamp=False):
        u, y = T[res][0][split], T[res][1][split]
        if resamp:  # subsample input to the 128 training grid, then Fourier-interpolate the 128-point output to res
            return rel_l2(trig_interp(predict(model, a.system, u[:, :: res // 128] / scale, 128) * scale, res), y)
        return rel_l2(predict(model, a.system, u / scale, res) * scale, y)

    m = {
        "rel_l2": ev(128, te),
        "rel_l2_val": ev(128, va),
        "train_rel_l2": ev(128, tr),
        "rel_l2_256": ev(256, te),
        "rel_l2_512": ev(512, te),
        "rel_l2_256_resamp": ev(256, te, True),
        "interp_floor_256": rel_l2(trig_interp(T[128][1][te], 256), T[256][1][te]),
        "params": float(n_par),
        "train_s": train_s,
    }
    print("METRICS", json.dumps(m), flush=True)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(m, open(a.out, "w"))


if __name__ == "__main__":
    main()
