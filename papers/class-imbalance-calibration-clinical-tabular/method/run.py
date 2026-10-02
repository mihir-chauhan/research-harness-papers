"""Imbalance corrections vs calibration on breast-cancer Wisconsin (scikit-learn).

python method/run.py --system smote --model lr --task bc_1to20 --seed 0 --out metrics.json
systems: none | reweight | ros | smote | threshold ; flag --prior_corr adds the analytic logit-offset correction;
--smote_ratio sets the target minority:majority ratio after resampling (default 1.0).
"""
import argparse, json, os, time
import numpy as np
os.environ.setdefault("OMP_NUM_THREADS", "2")
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from scipy.optimize import brentq
from sklearn.metrics import roc_auc_score, average_precision_score

EPS = 1e-6
RATIOS = {"bc_natural": None, "bc_1to5": 5, "bc_1to20": 20, "bc_1to50": 50}


def make_data(task, seed):
    """Positive = malignant (212), negative = benign (357). Stratified 70/30 split of the full data first. For 1:k the
    TRAINING positives are subsampled to round(n_neg_train/k); the test set keeps all held-out rows and the test
    positives get weight w so the weighted test prevalence is 1:k (all metrics below are weighted by w)."""
    X, y = load_breast_cancer(return_X_y=True)
    y = 1 - y  # sklearn codes malignant as 0
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=seed)
    rng = np.random.RandomState(seed)
    k = RATIOS[task]
    w = np.ones(len(yte))
    if k is not None:
        pos = np.where(ytr == 1)[0]; neg = np.where(ytr == 0)[0]
        npos = max(int(round(len(neg) / k)), 2)
        keep = np.concatenate([rng.choice(pos, npos, replace=False), neg])
        Xtr, ytr = Xtr[keep], ytr[keep]
        w[yte == 1] = (np.sum(yte == 0) / k) / np.sum(yte == 1)
    return Xtr, Xte, ytr, yte, w


def smote(X, y, ratio, rng, k=5):
    """SMOTE (Chawla et al. 2002): synthetic minority points on segments to one of the k nearest minority neighbours."""
    Xm = X[y == 1]; n_min = len(Xm); n_maj = int((y == 0).sum())
    n_new = int(round(ratio * n_maj)) - n_min
    if n_new <= 0:
        return X, y
    if n_min < 2:
        idx = rng.randint(0, n_min, n_new)
        Xs = Xm[idx]
    else:
        kk = min(k, n_min - 1)
        D = ((Xm[:, None, :] - Xm[None, :, :]) ** 2).sum(-1)
        np.fill_diagonal(D, np.inf)
        nn = np.argsort(D, axis=1)[:, :kk]
        base = rng.randint(0, n_min, n_new)
        nbr = nn[base, rng.randint(0, kk, n_new)]
        gap = rng.rand(n_new, 1)
        Xs = Xm[base] + gap * (Xm[nbr] - Xm[base])
    return np.vstack([X, Xs]), np.concatenate([y, np.ones(n_new, int)])


def ros(X, y, ratio, rng):
    """Random oversampling: duplicate minority rows drawn with replacement."""
    pos = np.where(y == 1)[0]; n_new = int(round(ratio * (y == 0).sum())) - len(pos)
    if n_new <= 0:
        return X, y
    idx = rng.choice(pos, n_new, replace=True)
    return np.vstack([X, X[idx]]), np.concatenate([y, np.ones(n_new, int)])


def make_model(name, seed, class_weight=None):
    if name == "lr":
        return LogisticRegression(C=1.0, max_iter=2000, class_weight=class_weight)
    return GradientBoostingClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=seed)


def logit(p):
    p = np.clip(p, EPS, 1 - EPS)
    return np.log(p / (1 - p))


def cal_slope_intercept(p, y, w):
    """Calibration slope b: weighted logistic regression y ~ a + b*logit(p). Intercept a_c (calibration-in-the-large):
    weighted logistic regression of y on offset logit(p) with slope fixed to 1 (1-D Newton)."""
    z = logit(p)
    lr = LogisticRegression(C=1e6, max_iter=5000)
    lr.fit(z[:, None], y, sample_weight=w)
    slope = float(lr.coef_[0, 0])
    g = lambda t: np.sum(w * (y - 1 / (1 + np.exp(-(z + t)))))
    a = float(brentq(g, -20, 20)) if g(-20) * g(20) < 0 else float(-20 if g(-20) < 0 else 20)
    return slope, a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True, choices=["none", "reweight", "ros", "smote", "threshold"])
    ap.add_argument("--model", required=True, choices=["lr", "gb"])
    ap.add_argument("--task", required=True, choices=list(RATIOS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smote_ratio", type=float, default=1.0)
    ap.add_argument("--prior_corr", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    print("config:", vars(a), flush=True)
    t0 = time.time()
    Xtr, Xte, ytr, yte, w = make_data(a.task, a.seed)
    sc = StandardScaler().fit(Xtr); Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
    rng = np.random.RandomState(1000 + a.seed)
    prev = float(ytr.mean())
    Xf, yf, cw = Xtr, ytr, None
    eff_prev = prev
    if a.system == "reweight":
        # balanced class weights n/(2 n_c): LR via class_weight; GB via sample_weight
        cw = "balanced"; eff_prev = 0.5
    elif a.system == "ros":
        Xf, yf = ros(Xtr, ytr, a.smote_ratio, rng); eff_prev = float(yf.mean())
    elif a.system == "smote":
        Xf, yf = smote(Xtr, ytr, a.smote_ratio, rng); eff_prev = float(yf.mean())
    m = make_model(a.model, a.seed, cw)
    if a.system == "reweight" and a.model == "gb":
        sw = np.where(ytr == 1, 0.5 / prev, 0.5 / (1 - prev))
        m.fit(Xf, yf, sample_weight=sw)
    else:
        m.fit(Xf, yf)
    p = m.predict_proba(Xte)[:, 1]
    if a.prior_corr:
        z = logit(p) + np.log(prev / (1 - prev)) - np.log(eff_prev / (1 - eff_prev))
        p = 1 / (1 + np.exp(-z))
    thr = prev if a.system == "threshold" else 0.5  # threshold moving: cut-off at the training prevalence
    pred = (p >= thr).astype(int)
    sens = float(np.sum(w * ((pred == 1) & (yte == 1))) / np.sum(w * (yte == 1)))
    spec = float(np.sum(w * ((pred == 0) & (yte == 0))) / np.sum(w * (yte == 0)))
    slope, citl = cal_slope_intercept(p, yte, w)
    out = {
        "auroc": float(roc_auc_score(yte, p, sample_weight=w)),
        "auprc": float(average_precision_score(yte, p, sample_weight=w)),
        "brier": float(np.sum(w * (p - yte) ** 2) / np.sum(w)),
        "cal_slope": slope, "cal_citl": citl, "slope_dev": abs(slope - 1.0), "citl_abs": abs(citl),
        "mean_pred": float(np.sum(w * p) / np.sum(w)),
        "obs_prev": float(np.sum(w * yte) / np.sum(w)),
        "sens": sens, "spec": spec, "bal_acc": 0.5 * (sens + spec),
        "n_train_pos": int(ytr.sum()), "n_train": int(len(ytr)), "n_test_pos": int(yte.sum()),
        "n_fit": int(len(yf)), "runtime_s": time.time() - t0,
    }
    json.dump(out, open(a.out, "w"))
    print("metrics:", json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
