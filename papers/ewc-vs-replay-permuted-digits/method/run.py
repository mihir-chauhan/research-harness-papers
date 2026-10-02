"""Continual learning on sklearn digits: finetune / EWC / experience replay / joint.
Usage: run.py --system {finetune,ewc,replay,joint} --task {perm_dil,split_cil,split_til} --seed S
              [--lam L] [--buffer M] [--lr LR] [--epochs E] --out file.json [--curve file.csv]
"""
import argparse, json, sys
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

torch.set_num_threads(2)
T = 5          # tasks per sequence
CLIP = 5.0     # gradient-norm clip
BS = 32        # minibatch size (new data; replay batch is also BS)


def make_tasks(task, seed):
    X, y = load_digits(return_X_y=True)
    X = X.astype(np.float32) / 16.0
    idx = np.arange(len(y))
    tr, rest = train_test_split(idx, train_size=0.6, stratify=y, random_state=seed)
    va, te = train_test_split(rest, train_size=0.5, stratify=y[rest], random_state=seed)
    rng = np.random.RandomState(1000 + seed)
    tasks = []
    if task == "perm_dil":
        perms = [np.arange(64)] + [rng.permutation(64) for _ in range(T - 1)]
        for p in perms:
            tasks.append({s: (torch.tensor(X[ii][:, p]), torch.tensor(y[ii])) for s, ii in (("tr", tr), ("va", va), ("te", te))})
        classes = [list(range(10))] * T
    else:
        order = rng.permutation(10)
        classes = [list(order[2 * k:2 * k + 2]) for k in range(T)]
        for c in classes:
            d = {}
            for s, ii in (("tr", tr), ("va", va), ("te", te)):
                m = np.isin(y[ii], c)
                d[s] = (torch.tensor(X[ii][m]), torch.tensor(y[ii][m]))
            tasks.append(d)
    return tasks, classes


class MLP(nn.Module):
    def __init__(s):
        super().__init__()
        s.net = nn.Sequential(nn.Linear(64, 100), nn.ReLU(), nn.Linear(100, 100), nn.ReLU(), nn.Linear(100, 10))

    def forward(s, x):
        return s.net(x)


def masked(logits, tid, cmask):
    """cmask: None (single head over 10 classes) or [T,10] bool for task-incremental."""
    if cmask is None:
        return logits
    return logits.masked_fill(~cmask[tid], -1e9)


def accuracy(model, data, tid, cmask):
    x, y = data
    with torch.no_grad():
        out = masked(model(x), torch.full((len(y),), tid), cmask)
    return (out.argmax(1) == y).float().mean().item()


def fisher_diag(model, data, tid, cmask, gen):
    """Diagonal empirical Fisher with labels sampled from the model's own predictive distribution."""
    x, _ = data
    fis = [torch.zeros_like(p) for p in model.parameters()]
    for i in range(len(x)):
        model.zero_grad()
        lo = masked(model(x[i:i + 1]), torch.tensor([tid]), cmask)
        yy = torch.multinomial(F.softmax(lo, 1).detach(), 1, generator=gen)[0]
        F.cross_entropy(lo, yy).backward()
        for f, p in zip(fis, model.parameters()):
            f += p.grad.detach() ** 2
    return [f / len(x) for f in fis]


def train_stage(model, stream, opt, epochs, lam, ewc_terms, buf, cmask, gen):
    """stream: (x, y, tid) tensors. buf: (x,y,tid) or None."""
    x, y, t = stream
    n = len(y)
    for _ in range(epochs):
        perm = torch.randperm(n, generator=gen)
        for b in range(0, n, BS):
            ii = perm[b:b + BS]
            loss = F.cross_entropy(masked(model(x[ii]), t[ii], cmask), y[ii])
            if buf is not None:
                bi = torch.randint(0, len(buf[1]), (BS,), generator=gen)
                loss = loss + F.cross_entropy(masked(model(buf[0][bi]), buf[2][bi], cmask), buf[1][bi])
            if ewc_terms and lam > 0:
                pen = 0.0
                for fis, anchor in ewc_terms:
                    for f, a, p in zip(fis, anchor, model.parameters()):
                        pen = pen + (f * (p - a) ** 2).sum()
                loss = loss + 0.5 * lam * pen
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), CLIP)  # same for every system; keeps large-lambda EWC finite
            opt.step()


def evaluate(model, tasks, cmask, split):
    return [accuracy(model, tasks[j][split], j, cmask) for j in range(len(tasks))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True); ap.add_argument("--task", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--lam", type=float, default=0.0); ap.add_argument("--buffer", type=int, default=0)
    ap.add_argument("--lr", type=float, default=0.1); ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--out", required=True); ap.add_argument("--curve", default=None)
    a = ap.parse_args()
    print("config:", json.dumps(vars(a)), flush=True)
    torch.manual_seed(a.seed)
    gen = torch.Generator().manual_seed(a.seed)
    tasks, classes = make_tasks(a.task, a.seed)
    cmask = None
    if a.task == "split_til":
        cmask = torch.zeros(T, 10, dtype=torch.bool)
        for k, c in enumerate(classes):
            cmask[k, c] = True
    tid_of = lambda k, n: torch.full((n,), k)
    def stream_of(ks):
        return (torch.cat([tasks[k]["tr"][0] for k in ks]), torch.cat([tasks[k]["tr"][1] for k in ks]),
                torch.cat([tid_of(k, len(tasks[k]["tr"][1])) for k in ks]))

    # acc[split][i][j]: accuracy on task j after training stage i
    acc = {"va": [], "te": []}
    model = MLP()
    ewc_terms, buf = [], None
    for i in range(T):
        if a.system == "joint":
            model = MLP()  # upper bound: retrain from scratch on the union of tasks 0..i
            opt = torch.optim.SGD(model.parameters(), lr=a.lr)
            train_stage(model, stream_of(range(i + 1)), opt, a.epochs, 0, None, None, cmask, gen)
        else:
            opt = torch.optim.SGD(model.parameters(), lr=a.lr)
            train_stage(model, stream_of([i]), opt, a.epochs, a.lam, ewc_terms,
                        buf if a.system == "replay" else None, cmask, gen)
            if a.system == "ewc":
                fis = fisher_diag(model, tasks[i]["tr"], i, cmask, gen)
                ewc_terms.append((fis, [p.detach().clone() for p in model.parameters()]))
            if a.system == "replay" and a.buffer > 0:
                # equal share of the M slots for each task seen so far, random exemplars per task
                per = a.buffer // (i + 1)
                bx, by, bt = [], [], []
                for k in range(i + 1):
                    x, y = tasks[k]["tr"]
                    sel = torch.randperm(len(y), generator=gen)[:per] if (k == i or buf is None) else None
                    if k < i:  # shrink earlier shares
                        m = (buf[2] == k).nonzero().flatten()
                        sel_old = m[torch.randperm(len(m), generator=gen)[:per]]
                        bx.append(buf[0][sel_old]); by.append(buf[1][sel_old]); bt.append(buf[2][sel_old])
                    else:
                        bx.append(x[sel]); by.append(y[sel]); bt.append(tid_of(k, len(sel)))
                buf = (torch.cat(bx), torch.cat(by), torch.cat(bt))
        for s in ("va", "te"):
            acc[s].append(evaluate(model, tasks, cmask, s))
    out = {}
    for s, pre in (("te", ""), ("va", "val_")):
        A = np.array(acc[s])
        out[pre + "average_accuracy"] = float(A[-1].mean())
        out[pre + "forgetting"] = float(np.mean([A[:-1, j].max() - A[-1, j] for j in range(T - 1)]))
        if s == "te":
            out["backward_transfer"] = float(np.mean([A[-1, j] - A[j, j] for j in range(T - 1)]))
            out["last_task_accuracy"] = float(A[-1, -1])
            out["mean_seen_accuracy"] = float(np.mean([A[i, :i + 1].mean() for i in range(T)]))
            out["acc_matrix"] = A.round(4).tolist()
    if a.curve:
        A = np.array(acc["te"])
        with open(a.curve, "w") as f:
            f.write("step,value,seed,name\n")
            for i in range(T):
                f.write(f"{i + 1},{A[i, :i + 1].mean():.5f},{a.seed},{a.system}\n")
    json.dump({k: v for k, v in out.items() if k != "acc_matrix"}, open(a.out, "w"))
    print("metrics:", json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
