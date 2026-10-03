"""Entrypoint: python method/run.py --system <name> --seed <s> --out metrics.json [--margin ...]
One run = one system, one seed, all three lattice sizes (data are regenerated from the seed
and cached under data/). Writes a flat JSON of metrics and prints config + metrics."""
import argparse, json, os, sys, time
import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sampler import generate, TC_EXACT, sw_sweep, metropolis_sweep, energy_per_site, onsager_energy
from estimators import crossing, peak, collapse

torch.set_num_threads(2)
LS = (16, 24, 32)
TEMPS = np.linspace(1.5, 3.5, 40)
TC_REF = 2.27  # rounded prior knowledge used only to place the training windows
SYSTEMS = ["LogReg (raw)", "LogReg (Z2-fixed)", "MLP", "CNN", "PCA", "Confusion (MLP)", "Binder/chi (reference)"]
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def get_data(L, seed):
    os.makedirs(ROOT, exist_ok=True)
    f = os.path.join(ROOT, f"ising_L{L}_s{seed}.npy")
    if os.path.exists(f):
        return np.load(f)
    X = generate(L, TEMPS, seed=1000 * seed + L)
    np.save(f + f".tmp{os.getpid()}.npy", X)
    os.replace(f + f".tmp{os.getpid()}.npy", f)
    return X


# ---------------- models ----------------
class CNN(nn.Module):
    def __init__(self, ch=8):
        super().__init__()
        self.c1 = nn.Conv2d(1, ch, 3, padding=1, padding_mode="circular")
        self.c2 = nn.Conv2d(ch, ch, 3, padding=1, padding_mode="circular")
        self.fc = nn.Linear(ch, 1)

    def forward(self, x):
        x = torch.relu(self.c1(x.view(-1, 1, *x.shape[-2:])))
        x = torch.relu(self.c2(x))
        return self.fc(x.mean((2, 3))).squeeze(-1)


def make_model(kind, L, hidden, ch):
    if kind == "logreg":
        return nn.Sequential(nn.Flatten(), nn.Linear(L * L, 1), nn.Flatten(0))
    if kind == "mlp":
        return nn.Sequential(nn.Flatten(), nn.Linear(L * L, hidden), nn.ReLU(), nn.Linear(hidden, 1), nn.Flatten(0))
    return CNN(ch)


def train(model, X, y, epochs, lr, wd, seed, bs=128):
    g = torch.Generator().manual_seed(seed)
    X, y = torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)
    w = torch.where(y > 0.5, 0.5 / y.mean(), 0.5 / (1 - y.mean()))  # balanced class weights
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=wd)
    for _ in range(epochs):
        perm = torch.randperm(len(X), generator=g)
        for i in range(0, len(X), bs):
            b = perm[i:i + bs]
            loss = (nn.functional.binary_cross_entropy_with_logits(model(X[b]), y[b], reduction="none") * w[b]).mean()
            opt.zero_grad(); loss.backward(); opt.step()
    return model


def predict(model, X):
    with torch.no_grad():
        return torch.sigmoid(torch.cat([model(torch.tensor(X[i:i + 512], dtype=torch.float32))
                                        for i in range(0, len(X), 512)])).numpy()


def z2fix(X):
    s = np.sign(X.sum(axis=(-1, -2), keepdims=True)); s[s == 0] = 1
    return X * s


# ---------------- per-size curves ----------------
def split(D, nsamp):
    """D: (4 chains, nT, 50, L, L) -> train chains 0-2 (first nsamp samples), test chain 3."""
    return D[:3, :, :nsamp], D[3]


def supervised_curve(kind, L, D, a, seed):
    Dtr, Dte = split(D, a.nsamp)
    if kind == "logreg_z2":
        Dtr, Dte = z2fix(Dtr), z2fix(Dte)
    lo, hi = TC_REF - a.margin, TC_REF + a.margin
    mo, md = TEMPS <= lo, TEMPS >= hi
    Xo, Xd = Dtr[:, mo].reshape(-1, L, L), Dtr[:, md].reshape(-1, L, L)
    X = np.concatenate([Xo, Xd]).astype(np.float32)
    y = np.concatenate([np.ones(len(Xo)), np.zeros(len(Xd))])
    base = "logreg" if kind.startswith("logreg") else kind
    torch.manual_seed(seed)
    model = train(make_model(base, L, a.hidden, a.channels), X, y, a.epochs, a.lr, a.wd, seed)
    P = predict(model, Dte.reshape(-1, L, L).astype(np.float32)).reshape(len(TEMPS), -1)
    p = P.mean(1)
    far = np.concatenate([((P[mo] > 0.5).mean(1)), ((P[md] <= 0.5).mean(1))])
    return p, float(np.mean(far))


def pca_curve(L, D, a):
    Dtr, Dte = split(D, a.nsamp)
    X = Dtr.reshape(-1, L * L).astype(np.float64)
    mu = X.mean(0)
    X -= mu
    w, V = np.linalg.eigh(X.T @ X / len(X))
    v = V[:, -1]
    z = np.abs((Dte.reshape(len(TEMPS), -1, L * L).astype(np.float64) - mu) @ v)
    return z.var(1), z.mean(1) / z.mean(1).max()  # susceptibility-like, order-parameter-like


def confusion_curve(L, D, a, seed):
    Dtr, Dte = split(D, a.nsamp)
    Xtr = Dtr.reshape(3, len(TEMPS), -1, L, L)
    trial = np.where((TEMPS >= 1.7) & (TEMPS <= 3.3))[0]
    acc, bounds = [], []
    for k, it in enumerate(trial):
        Tp = (TEMPS[it] + TEMPS[it + 1]) / 2  # trial boundary between grid points (trial <= 3.3 < TEMPS[-1])
        bounds.append(Tp)
        lab_t = (TEMPS < Tp).astype(np.float64)
        ytr = np.broadcast_to(lab_t[None, :, None], Xtr.shape[:3]).reshape(-1)
        torch.manual_seed(seed * 100 + k)
        m = train(make_model("mlp", L, a.conf_hidden, a.channels), Xtr.reshape(-1, L, L).astype(np.float32), ytr,
                  a.conf_epochs, a.lr, a.wd, seed * 100 + k)
        pr = predict(m, Dte.reshape(-1, L, L).astype(np.float32)).reshape(len(TEMPS), -1)
        yte = np.broadcast_to(lab_t[:, None], pr.shape)
        acc.append(float(((pr > 0.5) == (yte > 0.5)).mean()))
    return np.array(bounds), np.array(acc)  # abscissa = the trial boundaries T' used for the labels


def binder_chi(L, D):
    # use all four chains for these direct estimators (no training involved)
    m = np.abs(D.mean((-1, -2))).transpose(1, 0, 2).reshape(len(TEMPS), -1)
    chi = L * L * (np.mean(m ** 2, 1) - np.mean(m, 1) ** 2) / TEMPS
    u4 = 1 - np.mean(m ** 4, 1) / (3 * np.mean(m ** 2, 1) ** 2)
    return chi, u4


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True, choices=SYSTEMS + ["sampler_check", "sampler_check_long"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--margin", type=float, default=0.3)
    ap.add_argument("--nsamp", type=int, default=50)
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--wd", type=float, default=1e-4)
    ap.add_argument("--hidden", type=int, default=64)
    ap.add_argument("--channels", type=int, default=8)
    ap.add_argument("--conf_hidden", type=int, default=32)
    ap.add_argument("--conf_epochs", type=int, default=8)
    a = ap.parse_args()
    print("CONFIG", json.dumps(vars(a)), flush=True)
    t0 = time.time()
    M = {}
    if a.system == "sampler_check":
        M = sampler_check(a.seed)
    elif a.system == "sampler_check_long":
        M = sampler_check(a.seed, nch=64, nper=100, tag="long_")
    else:
        curves, tcs, accs = {}, {}, []
        Tgrid = TEMPS
        for L in LS:
            D = get_data(L, a.seed)
            if a.system.startswith(("LogReg", "MLP", "CNN")):
                kind = {"LogReg (raw)": "logreg", "LogReg (Z2-fixed)": "logreg_z2", "MLP": "mlp", "CNN": "cnn"}[a.system]
                p, far = supervised_curve(kind, L, D, a, a.seed)
                tc, found = crossing(TEMPS, p)
                M[f"crossing_found_l{L}"] = float(found); accs.append(far)
                curves[L] = p
            elif a.system == "PCA":
                chi, q = pca_curve(L, D, a)
                tc = peak(TEMPS, chi, 1.9, 3.1)
                curves[L] = q
            elif a.system == "Confusion (MLP)":
                Tgrid, acc = confusion_curve(L, D, a, a.seed)
                tc = peak(Tgrid, acc, 1.9, 3.1)
                curves[L] = acc
            else:
                chi, u4 = binder_chi(L, D)
                tc = peak(TEMPS, chi, 1.9, 3.1)
                curves[L] = u4
            M[f"tc_error_l{L}"] = abs(tc - TC_EXACT)
            M[f"tc_bias_l{L}"] = tc - TC_EXACT
            print(f"L={L} Tc={tc:.4f}", flush=True)
        if accs:
            M["acc_far"] = float(np.mean(accs))
        tcf, nu, cost = collapse(Tgrid, curves)
        M["tc_error_fss"] = abs(tcf - TC_EXACT) if tcf is not None else float("nan")
        M["tc_bias_fss"] = tcf - TC_EXACT
        M["nu_fss"] = nu
        M["nu_error_fss"] = abs(nu - 1.0)
        M["collapse_cost"] = cost
        np.savez(os.path.splitext(a.out)[0] + "_curves.npz", T=Tgrid, **{f"L{L}": c for L, c in curves.items()})
    print("METRICS", json.dumps(M), flush=True)
    json.dump(M, open(a.out, "w"))


def sampler_check(seed, nch=8, nper=50, tag=""):
    """Swendsen-Wang vs checkerboard Metropolis vs exact Onsager energy, and SW decorrelation."""
    M = {}
    rng = np.random.default_rng(seed)
    L = 24
    Tt = np.array([1.8, 2.0, 3.0, 3.5])
    # Metropolis from a cold start, SW from a hot start
    S = np.ones((len(Tt) * nch, L, L), dtype=np.int8); Tb = np.repeat(Tt, nch)
    for _ in range(600): S = metropolis_sweep(S, Tb, rng)
    e = []
    for _ in range(600):
        S = metropolis_sweep(S, Tb, rng); e.append(energy_per_site(S))
    em = np.mean(e, 0).reshape(len(Tt), nch).mean(1)
    D = generate(L, Tt, n_chains=nch, n_per_chain=nper, seed=seed)
    es = energy_per_site(D.reshape(-1, L, L)).reshape(nch, len(Tt), nper).mean((0, 2))
    for T, a_, b_ in zip(Tt, es, em):
        k = tag + f"{T:.1f}".replace(".", "p")
        M[f"e_sw_T{k}"] = float(a_); M[f"e_metropolis_T{k}"] = float(b_); M[f"e_onsager_T{k}"] = float(onsager_energy(T))
        M[f"e_diff_sw_metropolis_T{k}"] = float(abs(a_ - b_))
    # autocorrelation of |m| between stored SW samples at T closest to Tc (L=32)
    Ttc = np.array([2.27])
    D = generate(32, Ttc, n_chains=8, n_per_chain=200, seed=seed + 7)
    m = np.abs(D[:, 0].mean((-1, -2))); m = m - m.mean(1, keepdims=True)
    ac = (m[:, 1:] * m[:, :-1]).mean() / (m * m).mean()
    M["lag1_autocorr_absm_L32_Tc"] = float(ac)
    return M


if __name__ == "__main__":
    main()
