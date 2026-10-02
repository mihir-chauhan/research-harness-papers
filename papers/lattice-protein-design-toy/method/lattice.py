"""Exhaustive 2D HP lattice model, chain length N=16.

Conformations are self-avoiding walks on the square lattice modulo rotation/reflection
(first step is +x, first turn is +y). Residue i,j are in contact if lattice-adjacent and |i-j|>=3.
Energy of sequence h in {0,1}^N (1=H) on a conformation: E = -sum_{contacts (i,j)} h_i h_j.
A precomputed table gives, for all 2^N sequences, the minimum energy, the number of conformations
attaining it (degeneracy) and the index of the first minimiser.
"""
import os, sys, numpy as np

N = 16
PAIRS = [(i, j) for i in range(N) for j in range(i + 3, N, 2)]  # only odd separations can touch (bipartite lattice)
PIDX = {p: k for k, p in enumerate(PAIRS)}
P = len(PAIRS)
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data_cache")
DIRS = [(1, 0), (0, 1), (0, -1), (-1, 0)]


def enumerate_conformations():
    """Return (moves[N_conf, N-1] uint8 in 0..3 index into DIRS, contacts[N_conf, P] uint8)."""
    sys.setrecursionlimit(10000)
    moves_out, mask_out = [], []
    occ = {(0, 0): 0, (1, 0): 1}
    path = [0]

    def rec(i, x, y, turned, mask):
        # residue i placed at (x,y); place residue i+1
        if i == N - 1:
            moves_out.append(tuple(path)); mask_out.append(mask); return
        for d, (dx, dy) in enumerate(DIRS):
            if not turned and d == 2:  # first turn is +y only (symmetry breaking)
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in occ:
                continue
            j = i + 1
            m = mask
            for ex, ey in DIRS:
                k = occ.get((nx + ex, ny + ey))
                if k is not None and j - k >= 3:
                    m |= 1 << PIDX[(k, j)]
            occ[(nx, ny)] = j
            path.append(d)
            rec(j, nx, ny, turned or d != 0, m)
            path.pop()
            del occ[(nx, ny)]

    rec(1, 1, 0, False, 0)
    moves = np.array(moves_out, dtype=np.uint8)
    masks = np.array(mask_out, dtype=np.uint64)
    contacts = ((masks[:, None] >> np.arange(P, dtype=np.uint64)[None, :]) & 1).astype(np.uint8)
    return moves, contacts


def seq_bits(code):
    return np.array([(code >> (N - 1 - i)) & 1 for i in range(N)], dtype=np.float32)


def build_tables():
    moves, contacts = enumerate_conformations()
    C = contacts.astype(np.float32)
    ii = np.array([p[0] for p in PAIRS]); jj = np.array([p[1] for p in PAIRS])
    S = 1 << N
    emin = np.zeros(S, np.int8); cnt = np.zeros(S, np.int32); arg = np.zeros(S, np.int32)
    B = 64
    for s0 in range(0, S, B):
        codes = np.arange(s0, min(S, s0 + B))
        H = np.stack([seq_bits(c) for c in codes])  # [B,N]
        W = (H[:, ii] * H[:, jj]).T                  # [P,B]
        E = -(C @ W)                                 # [Nc,B]
        m = E.min(0)
        emin[codes] = m.astype(np.int8)
        hit = E == m[None, :]
        cnt[codes] = hit.sum(0)
        arg[codes] = hit.argmax(0)
    return moves, contacts, emin, cnt, arg


def load():
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, "tables.npz")
    if not os.path.exists(f):
        moves, contacts, emin, cnt, arg = build_tables()
        np.savez_compressed(f, moves=moves, contacts=contacts, emin=emin, cnt=cnt, arg=arg)
    z = np.load(f)
    return {k: z[k] for k in z.files}


if __name__ == "__main__":
    import json, time
    t = time.time()
    T = load()
    out = {"n_conformations": int(len(T["moves"])),
           "n_unique_gs_sequences": int((T["cnt"] == 1).sum()),
           "n_designable_conformations": int(len(np.unique(T["arg"][T["cnt"] == 1])))}
    print(json.dumps(out))
    path = os.environ.get("RH_METRICS_FILE")
    if path:
        json.dump(out, open(path, "w"))
