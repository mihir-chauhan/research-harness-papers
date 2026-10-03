"""PhysioNet 2012 set-a loader: hourly-binned tensors (cached in data/cache.npz)."""
import glob, os, numpy as np
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
STATIC = ["Age", "Gender", "Height", "Weight", "ICUType"]
SKIP = set(STATIC) | {"RecordID"}
T = 48

def load():
    cache = os.path.join(ROOT, "cache.npz")
    if os.path.exists(cache):
        z = np.load(cache, allow_pickle=True)
        return z["X"], z["M"], z["S"], z["y"], z["icu"], list(z["vars"])
    out = {l.split(",")[0]: int(l.strip().split(",")[-1]) for l in open(os.path.join(ROOT, "Outcomes-a.txt")).read().strip().split("\n")[1:]}
    files = sorted(glob.glob(os.path.join(ROOT, "set-a", "*.txt")))
    names = sorted({l.split(",")[1] for f in files for l in open(f).read().split("\n")[1:] if l} - SKIP)
    vi = {n: i for i, n in enumerate(names)}
    N, V = len(files), len(names)
    X = np.full((N, T, V), np.nan, np.float32); S = np.full((N, 5), np.nan, np.float32); y = np.zeros(N, np.int64)
    for k, f in enumerate(files):
        rid = os.path.basename(f)[:-4]; y[k] = out[rid]
        rows = [l.split(",") for l in open(f).read().split("\n")[1:] if l]
        for t, p, v in rows:  # file order is chronological, so the last value in a bin wins
            v = float(v); h, m = t.split(":"); b = min(int(h) * 60 + int(m), 48 * 60 - 1) // 60
            if p in STATIC:
                j = STATIC.index(p)
                if v >= 0 and np.isnan(S[k, j]): S[k, j] = v
            elif p != "RecordID":
                if v == -1: continue
                X[k, b, vi[p]] = v
    M = (~np.isnan(X)).astype(np.float32); icu = S[:, 4].astype(int)
    np.savez(cache, X=X, M=M, S=S, y=y, icu=icu, vars=np.array(names))
    return X, M, S, y, icu, names
