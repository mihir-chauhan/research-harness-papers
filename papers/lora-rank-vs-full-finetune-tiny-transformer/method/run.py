"""Tiny-scale LoRA vs full fine-tuning vs last-layer tuning on synthetic sequence tasks.

python method/run.py --system lora --rank 4 --task reverse --seed 0 --out metrics.json
Systems: pretrained (no adaptation), scratch, full, lora, lastblock, head.
"""
import argparse, json, math, os, sys, time
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F

torch.set_num_threads(2)
L, V, SEP = 8, 14, 10          # digits per sequence, vocab (digits, SEP, 3 task tokens), separator id
TASK_ID = {"sort_asc": 11, "sort_desc": 12, "reverse": 13}   # first token of every sequence
D, H, FF, NLAYER = 64, 4, 128, 2
CKPT_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "raw", "ckpt")


def make_target(x, task):
    if task == "sort_asc": return np.sort(x, 1)
    if task == "sort_desc": return np.sort(x, 1)[:, ::-1].copy()
    if task == "reverse": return x[:, ::-1].copy()
    raise ValueError(task)


def make_data(task, n, seed):
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 10, size=(n, L))
    y = make_target(x, task)
    seq = np.concatenate([np.full((n, 1), TASK_ID[task]), x, np.full((n, 1), SEP), y], 1)
    return torch.tensor(seq, dtype=torch.long)


class LoRALinear(nn.Module):
    """y = W x + b + (alpha/r) B A x, with W frozen. B=0 at init, A Kaiming-uniform."""
    def __init__(self, base, r, alpha):
        super().__init__()
        self.base, self.r, self.scale = base, r, alpha / r
        self.A = nn.Parameter(torch.empty(r, base.in_features))
        nn.init.kaiming_uniform_(self.A, a=math.sqrt(5))
        self.B = nn.Parameter(torch.zeros(base.out_features, r))

    def forward(self, x):
        return self.base(x) + self.scale * F.linear(F.linear(x, self.A), self.B)


class Block(nn.Module):
    def __init__(self):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(D), nn.LayerNorm(D)
        self.q, self.k, self.v, self.o = (nn.Linear(D, D) for _ in range(4))
        self.ff1, self.ff2 = nn.Linear(D, FF), nn.Linear(FF, D)

    def forward(self, x):
        B, T, _ = x.shape
        h = self.ln1(x)
        sp = lambda t: t.view(B, T, H, D // H).transpose(1, 2)
        a = F.scaled_dot_product_attention(sp(self.q(h)), sp(self.k(h)), sp(self.v(h)), is_causal=True)
        x = x + self.o(a.transpose(1, 2).reshape(B, T, D))
        return x + self.ff2(F.gelu(self.ff1(self.ln2(x))))


class TinyLM(nn.Module):
    def __init__(self):
        super().__init__()
        self.tok, self.pos = nn.Embedding(V, D), nn.Embedding(2 * L + 2, D)
        self.blocks = nn.ModuleList(Block() for _ in range(NLAYER))
        self.lnf, self.head = nn.LayerNorm(D), nn.Linear(D, V, bias=False)

    def forward(self, s):
        x = self.tok(s) + self.pos(torch.arange(s.shape[1]))
        for b in self.blocks: x = b(x)
        return self.head(self.lnf(x))


def loss_fn(model, seq):
    logits = model(seq[:, :-1])[:, L + 1:]      # positions that predict the L output tokens
    return F.cross_entropy(logits.reshape(-1, V), seq[:, L + 2:].reshape(-1))


@torch.no_grad()
def evaluate(model, seq):
    """Exact match of greedy decoding equals teacher-forced argmax at all L output positions."""
    model.eval()
    pred = model(seq[:, :-1])[:, L + 1:].argmax(-1)
    ok = pred == seq[:, L + 2:]
    model.train()
    return ok.all(1).float().mean().item(), ok.float().mean().item()


def train(model, params, data, steps, bs, lr, seed, wd=0.0, hook=None):
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=wd)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1, (s + 1) / 50) * 0.5 * (1 + math.cos(math.pi * s / steps)))
    g = torch.Generator().manual_seed(seed)
    for s in range(steps):
        idx = torch.randint(0, len(data), (bs,), generator=g)
        loss = loss_fn(model, data[idx])
        opt.zero_grad(); loss.backward(); opt.step(); sched.step()
        if hook and (s + 1) % 50 == 0: hook(s + 1)
    return loss.item()


def pretrained(seed, args):
    path = os.path.join(CKPT_DIR, f"pre_seed{seed}.pt")
    torch.manual_seed(seed)
    m = TinyLM()
    if os.path.exists(path):
        m.load_state_dict(torch.load(path)); return m
    data = make_data("sort_asc", 20000, 1000 + seed)
    train(m, m.parameters(), data, args.pre_steps, 128, 2e-3, seed)
    os.makedirs(CKPT_DIR, exist_ok=True); torch.save(m.state_dict(), path)
    return m


def add_lora(model, r, alpha, targets):
    for b in model.blocks:
        for n in targets:
            setattr(b, n, LoRALinear(getattr(b, n), r, alpha))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--system", required=True); p.add_argument("--task", required=True)
    p.add_argument("--seed", type=int, default=0); p.add_argument("--out", required=True)
    p.add_argument("--rank", type=int, default=4); p.add_argument("--alpha_per_rank", type=float, default=2.0)
    p.add_argument("--targets", default="q,k,v,o,ff1,ff2"); p.add_argument("--lr", type=float, default=None)
    p.add_argument("--n_train", type=int, default=2000); p.add_argument("--steps", type=int, default=1500)
    p.add_argument("--bs", type=int, default=64); p.add_argument("--pre_steps", type=int, default=4000)
    p.add_argument("--curve_csv", default=None); p.add_argument("--eval_split", default="test", choices=["test", "val"])
    a = p.parse_args()
    t0 = time.time()
    print("config:", json.dumps(vars(a)), flush=True)
    ev = lambda task: make_data(task, 2000, 5000 if a.eval_split == "test" else 7000)
    model = pretrained(a.seed, a)
    pre_before = evaluate(model, ev("sort_asc"))[0]
    tgt_before = evaluate(model, ev(a.task))[0]
    train_data = make_data(a.task, a.n_train, 2000 + a.seed)   # fixed finite adaptation set
    # default learning rates = argmax of mean validation accuracy over the tuning grid (group `tune`, experiments/PROTOCOL.md)
    lr = a.lr
    if a.system == "scratch":
        torch.manual_seed(a.seed + 77); model = TinyLM()
    if a.system == "pretrained":
        params = []
    elif a.system in ("full", "scratch"):
        params = list(model.parameters()); lr = lr or (3e-3 if a.system == "scratch" else 1e-2)
    elif a.system == "lora":
        for q in model.parameters(): q.requires_grad_(False)
        add_lora(model, a.rank, a.alpha_per_rank * a.rank, a.targets.split(","))
        params = [q for n, q in model.named_parameters() if n.endswith((".A", ".B"))]
        for q in params: q.requires_grad_(True)
        lr = lr or 3e-2
    elif a.system in ("lastblock", "head"):
        for q in model.parameters(): q.requires_grad_(False)
        mods = [model.head] if a.system == "head" else [model.blocks[-1], model.lnf, model.head]
        params = [q for m in mods for q in m.parameters()]
        for q in params: q.requires_grad_(True)
        lr = lr or (3e-2 if a.system == "head" else 1e-2)
    else:
        raise ValueError(a.system)
    ntrain = sum(q.numel() for q in params)
    hook = None
    if a.curve_csv:
        rows, name = [], f"{a.system}" + (f"-r{a.rank}" if a.system == "lora" else "")
        ev_t, ev_p = ev(a.task)[:500], ev("sort_asc")[:500]
        def hook(step):
            rows.append(f"{step},{evaluate(model, ev_p)[0]},{a.seed},{name} (sort_asc retention)")
            rows.append(f"{step},{evaluate(model, ev_t)[0]},{a.seed},{name} (target)")
    final_loss = train(model, params, train_data, a.steps, a.bs, lr, a.seed, hook=hook) if params else float("nan")
    if a.curve_csv:
        open(a.curve_csv, "w").write("step,value,seed,name\n" + "\n".join(rows) + "\n")
    acc, tok = evaluate(model, ev(a.task))
    pre_after, _ = evaluate(model, ev("sort_asc"))
    m = dict(adapt_acc=acc, adapt_tok_acc=tok, trainable_params=ntrain, pretask_acc=pre_after,
             pretask_acc_before=pre_before, forgetting=pre_before - pre_after, zero_shot_acc=tgt_before,
             train_loss=final_loss, seconds=time.time() - t0)
    print("metrics:", json.dumps(m), flush=True)
    json.dump(m, open(a.out, "w"))


if __name__ == "__main__":
    main()
