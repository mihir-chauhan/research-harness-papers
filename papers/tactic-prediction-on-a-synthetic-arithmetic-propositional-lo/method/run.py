"""Entrypoint: python method/run.py --system S --task T --seed N --out metrics.json [--config JSON]
Systems: bfs | heuristic | transformer | mlp.  Tasks: tune_21_35 | val_3_10 | test_11_20 | test_21_40 | test_41_70."""
import argparse, json, os, pickle, random, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import torch
from logic import gen_provable, Oracle, collect_states, candidates
from search import prove, heuristic_costs, policy_cost_fn
import policy as P

torch.set_num_threads(2)
CACHE = '/tmp/tacpred_cache'
TRAIN_RANGE = (3, 10)
TASKS = {'tune_21_35': (21, 35, 11), 'val_3_10': (3, 10, 12), 'test_11_20': (11, 20, 13),
         'test_21_40': (21, 40, 14), 'test_41_70': (41, 70, 15)}
NPROB = 150
DEFAULTS = dict(ntrain=20000, steps=2000, bs=128, lr=2e-3, budget=100, mode='bestfirst', pos='sin', heur='large', cost='nll')


def get_data(seed, ntrain):
    path = f'{CACHE}/data_s{seed}_n{ntrain}.pkl'
    if os.path.exists(path):
        return pickle.load(open(path, 'rb'))
    rng = random.Random(1000 + seed)
    seqs = gen_provable(rng, *TRAIN_RANGE, ntrain)
    val = gen_provable(rng, *TRAIN_RANGE, 1000, exclude=seqs)
    orc = Oracle(cap=10 ** 7)
    def states(xs):
        out = {}
        for x in xs:
            for g, opt in collect_states(x, orc, rng, maxstates=30):
                out[g] = opt
        return list(out.items())
    d = dict(train=states(seqs), val=states(val), n_seq=len(seqs))
    os.makedirs(CACHE, exist_ok=True)
    pickle.dump(d, open(path, 'wb'))
    return d


def target(goal, opt):
    c = candidates(goal)
    t = np.zeros(len(c), dtype=np.float32)
    for o in opt:
        t[c.index(o)] = 1
    return t / t.sum()


def train_policy(system, seed, cfg, log):
    path = f"{CACHE}/model_{system}_s{seed}_n{cfg['ntrain']}_t{cfg['steps']}_{cfg['pos']}.pt"
    torch.manual_seed(seed); np.random.seed(seed)
    model = P.TransformerPolicy(pos=cfg['pos']) if system == 'transformer' else P.MLPPolicy()
    data = get_data(seed, cfg['ntrain'])
    enc = P.encode if system == 'transformer' else P.features
    bt = P.batch_tf if system == 'transformer' else P.batch_mlp
    def prep(states):
        return [enc(g) for g, _ in states], [target(g, o) for g, o in states]
    def fwd(items):
        b = bt(items)
        return model(*b)
    vx, vy = prep(data['val'])
    def evaluate():
        model.eval(); loss = acc = 0.0
        with torch.no_grad():
            for i in range(0, len(vx), 256):
                lg = fwd(vx[i:i + 256]); ys = vy[i:i + 256]
                K = lg.shape[1]
                y = torch.zeros(len(ys), K)
                for b, t in enumerate(ys):
                    y[b, :len(t)] = torch.from_numpy(t)
                lp = torch.log_softmax(lg, -1)
                loss += -(y * lp.masked_fill(y == 0, 0)).sum().item()
                acc += (y.gather(1, lg.argmax(1, keepdim=True)) > 0).sum().item()
        model.train()
        return loss / len(vx), acc / len(vx)
    if os.path.exists(path):
        model.load_state_dict(torch.load(path))
        model.eval()
        return model, evaluate(), len(data['train'])
    tx, ty = prep(data['train'])
    opt = torch.optim.AdamW(model.parameters(), lr=cfg['lr'], weight_decay=0.01)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=cfg['lr'], total_steps=cfg['steps'], pct_start=0.1)
    rng = np.random.RandomState(seed)
    model.train()
    for step in range(cfg['steps']):
        idx = rng.randint(0, len(tx), cfg['bs'])
        lg = fwd([tx[i] for i in idx])
        K = lg.shape[1]
        y = torch.zeros(len(idx), K)
        for b, i in enumerate(idx):
            y[b, :len(ty[i])] = torch.from_numpy(ty[i])
        lp = torch.log_softmax(lg, -1)
        loss = -(y * lp.masked_fill(y == 0, 0)).sum(1).mean()
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step(); sched.step()
        if step % 500 == 0:
            log(f'  train step {step} loss {loss.item():.4f}')
    model.eval()
    torch.save(model.state_dict(), path)
    return model, evaluate(), len(data['train'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--system', required=True); ap.add_argument('--task', required=True)
    ap.add_argument('--seed', type=int, required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--config', default='{}')
    a = ap.parse_args()
    cfg = {**DEFAULTS, **json.loads(a.config)}
    print('config', json.dumps({'system': a.system, 'task': a.task, 'seed': a.seed, **cfg}), flush=True)
    lo, hi, off = TASKS[a.task]
    probs = gen_provable(random.Random(100000 * off + a.seed), lo, hi, NPROB)
    out = {}
    if a.system == 'bfs':
        fn, mode = None, 'bfs'
    elif a.system == 'heuristic':
        fn, mode = (lambda g: heuristic_costs(g, cfg['heur'])), cfg['mode']
    else:
        model, (vl, va), nst = train_policy(a.system, a.seed, cfg, lambda s: print(s, flush=True))
        print(f'train states {nst} val_loss {vl:.4f} val_acc {va:.4f}', flush=True)
        if a.task == 'val_3_10':
            out.update(val_loss=vl, val_top1=va)
        enc = P.encode if a.system == 'transformer' else P.features
        bt = P.batch_tf if a.system == 'transformer' else P.batch_mlp
        def score(goal):
            with torch.no_grad():
                return model(*bt([enc(goal)]))[0].tolist()[:len(candidates(goal))]
        fn, mode = policy_cost_fn(score, cfg['cost']), cfg['mode']
    res = [prove(g, fn, cfg['budget'], mode) for g in probs]
    solved = np.mean([s for s, _ in res]); exps = np.mean([e for _, e in res])
    out.update(solved=float(solved), mean_exp=float(exps))
    print('final', json.dumps(out), flush=True)
    json.dump(out, open(a.out, 'w'))


if __name__ == '__main__':
    main()
