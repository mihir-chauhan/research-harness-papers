"""One run = one system x one seed x 5-fold patient-level CV on PhysioNet 2012 set-a.
Systems: lr, gbdt (summary features); gru_ffill, gru_md (GRU-simple with mask+delta), grud (GRU-D)."""
import argparse, json, os, sys, time, numpy as np, torch, torch.nn as nn
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data

torch.set_num_threads(2)
DEF = dict(horizon=48, C=0.01, lr_gb=0.05, leaves=8, l2=1.0, hidden=64, lr=1e-3, wd=1e-4, drop=0.2, epochs=40,
           patience=6, bs=64, dscale=12.0, counts=1, in_decay=1, h_decay=1)

# ---------------- preprocessing (statistics from the training fold only) ----------------
def norm_stats(X, S):
    mu = np.nanmean(X.reshape(-1, X.shape[2]), 0); sd = np.nanstd(X.reshape(-1, X.shape[2]), 0) + 1e-6
    smu = np.nanmean(S, 0); ssd = np.nanstd(S, 0) + 1e-6
    return mu, sd, smu, ssd

def static_feats(S, icu, st):
    _, _, smu, ssd = st
    Z = np.where(np.isnan(S), smu, S); Z = (Z - smu) / ssd
    Z = np.clip(Z, -5, 5)
    oh = np.eye(5)[icu][:, 1:]  # ICU types 1..4
    return np.concatenate([Z[:, :4], oh, np.isnan(S[:, 2:4]).astype(float)], 1).astype(np.float32)

def summary(X, M, S, icu, st, cfg):
    """per-variable min,max,mean,std,first,last,(count) over the horizon + static (NaN kept for gbdt)."""
    n, T, V = X.shape
    with np.errstate(all="ignore"):
        import warnings; warnings.simplefilter("ignore")
        f = [np.nanmin(X, 1), np.nanmax(X, 1), np.nanmean(X, 1), np.nanstd(X, 1)]
        idx = np.arange(T)[None, :, None]
        first = np.where(M > 0, idx, T).argmin(1); last = np.where(M > 0, idx, -1).argmax(1)
        fv = np.take_along_axis(X, first[:, None, :], 1)[:, 0]; lv = np.take_along_axis(X, last[:, None, :], 1)[:, 0]
        f += [fv, lv]
    if cfg["counts"]: f.append(M.sum(1))
    F = np.concatenate(f + [S, np.eye(5)[icu][:, 1:]], 1).astype(np.float32)
    return F

# ---------------- neural models ----------------
def build_seq(X, M, st, T):
    mu, sd = st[0], st[1]
    Z = np.clip((X - mu) / sd, -5, 5); Z = np.where(M > 0, Z, 0.0).astype(np.float32)
    n, _, V = X.shape
    last_val = np.zeros((n, T, V), np.float32); delta = np.zeros((n, T, V), np.float32); ffill = np.zeros((n, T, V), np.float32)
    cur = np.zeros((n, V), np.float32); lastt = np.full((n, V), -1.0, np.float32)  # lastt=-1: never observed
    for t in range(T):
        # state *before* step t (x_last, delta) as in GRU-D
        last_val[:, t] = cur
        delta[:, t] = np.where(lastt < 0, float(t), t - lastt)
        obs = M[:, t] > 0
        cur = np.where(obs, Z[:, t], cur); lastt = np.where(obs, float(t), lastt)
        ffill[:, t] = cur
    return [torch.tensor(a) for a in (Z, M[:, :T].astype(np.float32), last_val, delta, ffill)]

class Net(nn.Module):
    def __init__(self, mode, V, ds, cfg):
        super().__init__()
        self.mode, self.V, H = mode, V, cfg["hidden"]; self.H = H; self.cfg = cfg
        din = {"ffill": V, "md": 3 * V, "grud": 2 * V}[mode]
        self.Wx = nn.Linear(din, 3 * H); self.Wh = nn.Linear(H, 3 * H, bias=False)
        if mode == "grud":
            self.gx_w = nn.Parameter(torch.zeros(V)); self.gx_b = nn.Parameter(torch.zeros(V))
            self.gh = nn.Linear(V, H)
            nn.init.uniform_(self.gx_w, 0.0, 0.5)
        self.head = nn.Sequential(nn.Dropout(cfg["drop"]), nn.Linear(H + ds, 32), nn.ReLU(), nn.Linear(32, 1))

    def forward(self, Z, M, L, D, F, S):
        n, T, V = Z.shape; h = torch.zeros(n, self.H); cfg = self.cfg; ds = cfg["dscale"]
        for t in range(T):
            if self.mode == "ffill": x = F[:, t]
            elif self.mode == "md": x = torch.cat([F[:, t], M[:, t], D[:, t] / ds], 1)
            else:
                d = D[:, t] / ds
                if cfg["in_decay"]:
                    gx = torch.exp(-torch.relu(self.gx_w * d + self.gx_b)); xh = M[:, t] * Z[:, t] + (1 - M[:, t]) * gx * L[:, t]
                else: xh = M[:, t] * Z[:, t] + (1 - M[:, t]) * L[:, t]
                x = torch.cat([xh, M[:, t]], 1)
                if cfg["h_decay"]: h = h * torch.exp(-torch.relu(self.gh(d)))
            gi = self.Wx(x); gh = self.Wh(h)
            ir, iz, inn = gi.chunk(3, 1); hr, hz, hn = gh.chunk(3, 1)
            r = torch.sigmoid(ir + hr); z = torch.sigmoid(iz + hz); c = torch.tanh(inn + r * hn)
            h = (1 - z) * c + z * h
        return self.head(torch.cat([h, S], 1)).squeeze(1)

def fit_nn(mode, tr, va, te, cfg, seed, V):
    torch.manual_seed(seed); np.random.seed(seed)
    net = Net(mode, V, tr[-2].shape[1], cfg); opt = torch.optim.Adam(net.parameters(), lr=cfg["lr"], weight_decay=cfg["wd"])
    lossf = nn.BCEWithLogitsLoss(); ytr = tr[-1]; n = len(ytr)
    best, bs_state, bad = 1e9, None, 0; g = torch.Generator().manual_seed(seed)
    def pred(d):
        net.eval(); out = []
        with torch.no_grad():
            for i in range(0, len(d[0]), 512): out.append(net(*[a[i:i+512] for a in d[:-1]]))
        return torch.cat(out)
    for ep in range(cfg["epochs"]):
        net.train(); perm = torch.randperm(n, generator=g)
        for i in range(0, n, cfg["bs"]):
            b = perm[i:i+cfg["bs"]]
            opt.zero_grad(); l = lossf(net(*[a[b] for a in tr[:-1]]), ytr[b].float()); l.backward()
            nn.utils.clip_grad_norm_(net.parameters(), 5.0); opt.step()
        vl = lossf(pred(va), va[-1].float()).item()
        if vl < best - 1e-5: best, bad, bs_state = vl, 0, {k: v.clone() for k, v in net.state_dict().items()}
        else:
            bad += 1
            if bad >= cfg["patience"]: break
    net.load_state_dict(bs_state)
    return torch.sigmoid(pred(te)).numpy(), ep + 1

# ---------------- one fold ----------------
def run_fold(system, Xa, Ma, Sa, icua, ya, tri, tei, cfg, seed):
    T = cfg["horizon"]; Xa, Ma = Xa[:, :T], Ma[:, :T]
    st = norm_stats(Xa[tri], Sa[tri])
    fit, val = train_test_split(tri, test_size=0.15, stratify=ya[tri], random_state=seed)
    if system in ("lr", "gbdt"):
        F = summary(Xa, Ma, Sa, icua, st, cfg)
        if system == "lr":
            med = np.nanmedian(F[tri], 0); med = np.where(np.isnan(med), 0, med)
            Fi = np.where(np.isnan(F), med, F); mu, sd = Fi[tri].mean(0), Fi[tri].std(0) + 1e-6
            Fi = np.clip((Fi - mu) / sd, -5, 5)
            m = LogisticRegression(C=cfg["C"], max_iter=2000).fit(Fi[tri], ya[tri]); return m.predict_proba(Fi[tei])[:, 1], 0
        m = HistGradientBoostingClassifier(learning_rate=cfg["lr_gb"], max_iter=500, max_leaf_nodes=cfg["leaves"], l2_regularization=cfg["l2"],
                                           min_samples_leaf=20, early_stopping=True, validation_fraction=0.15, n_iter_no_change=30, random_state=seed)
        m.fit(F[tri], ya[tri]); return m.predict_proba(F[tei])[:, 1], m.n_iter_
    mode = {"gru_ffill": "ffill", "gru_md": "md", "grud": "grud"}[system]
    seq = build_seq(Xa, Ma, st, T); Sf = torch.tensor(static_feats(Sa, icua, st)); yt = torch.tensor(ya)
    mk = lambda ix: [a[ix] for a in seq] + [Sf[ix], yt[ix]]
    return fit_nn(mode, mk(fit), mk(val), mk(tei), cfg, seed, Xa.shape[2])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--config", default="{}"); ap.add_argument("--out", required=True)
    ap.add_argument("--tune", type=int, default=0, help="1: hold out 25%% of fold-0 training set, report on it (no test data touched)")
    a = ap.parse_args(); cfg = {**DEF, **json.loads(a.config)}
    print("system", a.system, "seed", a.seed, "config", json.dumps(cfg), flush=True)
    X, M, S, y, icu, _ = data.load(); N = len(y)
    skf = StratifiedKFold(5, shuffle=True, random_state=a.seed)
    folds = list(skf.split(np.zeros(N), y))
    t0 = time.time(); P = np.zeros(N); fm = {"auroc": [], "auprc": [], "brier": []}; its = []
    if a.tune:
        tri0, _ = folds[0]; tri, tei = train_test_split(tri0, test_size=0.25, stratify=y[tri0], random_state=a.seed); folds = [(tri, tei)]
    for k, (tri, tei) in enumerate(folds):
        p, it = run_fold(a.system, X, M, S, icu, y, tri, tei, cfg, a.seed * 10 + k)
        P[tei] = p; its.append(it)
        fm["auroc"].append(roc_auc_score(y[tei], p)); fm["auprc"].append(average_precision_score(y[tei], p)); fm["brier"].append(brier_score_loss(y[tei], p))
        print(f"fold {k} auroc {fm['auroc'][-1]:.4f} auprc {fm['auprc'][-1]:.4f} brier {fm['brier'][-1]:.4f} iters {it} t={time.time()-t0:.0f}s", flush=True)
    res = {k: float(np.mean(v)) for k, v in fm.items()}
    res["auroc_fold_sd"] = float(np.std(fm["auroc"]))
    if not a.tune:
        for c in (1, 2, 3, 4):
            m = icu == c; res[f"auroc_icu{c}"] = float(roc_auc_score(y[m], P[m]))
        res["auroc_pooled"] = float(roc_auc_score(y, P)); res["mean_epochs_or_trees"] = float(np.mean(its))
        res["mean_pred"] = float(P.mean())
    json.dump(res, open(a.out, "w")); print("final", json.dumps(res), flush=True)

if __name__ == "__main__": main()
