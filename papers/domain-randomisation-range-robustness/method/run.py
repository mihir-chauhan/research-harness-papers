"""CEM + tiny MLP policy on batched CartPole with domain randomisation of physical parameters.

Dynamics follow gymnasium CartPole-v1 (euler, tau=0.02) with per-environment scale factors on
cart mass, pole mass, pole length and force magnitude. See method/DESIGN.md.
"""
import argparse, json, math, os
import numpy as np

NOM = dict(mc=1.0, mp=0.1, l=0.5, f=10.0)
G, TAU, XT, TT, T_MAX = 9.8, 0.02, 2.4, 12 * 2 * math.pi / 360, 500
H = 8                      # hidden units
NP = 4 * H + H + H + 1     # MLP 4-8-1 parameter count


def sample_scales(rng, n, w):
    """log-uniform scales exp(U(-w,w)) for (mc, mp, l, f); w=0 is the nominal system."""
    return np.exp(rng.uniform(-w, w, size=(n, 4)))


def rollout(theta, scales, rng_init):
    """theta: (P, NP) policies, scales: (E,4) env params; every policy runs on every env.
    Returns (P, E) episode lengths (return = steps survived, max 500)."""
    P, E = theta.shape[0], scales.shape[0]
    W1 = theta[:, :4 * H].reshape(P, 4, H); b1 = theta[:, 4 * H:5 * H]
    W2 = theta[:, 5 * H:6 * H]; b2 = theta[:, 6 * H]
    mc = NOM['mc'] * scales[:, 0]; mp = NOM['mp'] * scales[:, 1]
    l = NOM['l'] * scales[:, 2]; fm = NOM['f'] * scales[:, 3]
    tm = mc + mp; pml = mp * l
    s = rng_init.uniform(-0.05, 0.05, size=(E, 4))
    s = np.broadcast_to(s, (P, E, 4)).copy()
    alive = np.ones((P, E), bool); length = np.zeros((P, E))
    for _ in range(T_MAX):
        h = np.tanh(np.einsum('pes,psh->peh', s, W1) + b1[:, None, :])
        a = np.einsum('peh,ph->pe', h, W2) + b2[:, None]
        force = np.where(a > 0, fm, -fm)
        x, xd, th, thd = s[..., 0], s[..., 1], s[..., 2], s[..., 3]
        ct, st = np.cos(th), np.sin(th)
        temp = (force + pml * thd ** 2 * st) / tm
        tacc = (G * st - ct * temp) / (l * (4.0 / 3.0 - mp * ct ** 2 / tm))
        xacc = temp - pml * tacc * ct / tm
        s = np.stack([x + TAU * xd, xd + TAU * xacc, th + TAU * thd, thd + TAU * tacc], -1)
        length += alive
        alive &= (np.abs(s[..., 0]) <= XT) & (np.abs(s[..., 2]) <= TT)
        if not alive.any():
            break
    return length


def train(mode, width, seed, iters, pop, n_env, step, thresh, wmax, log):
    rng = np.random.default_rng(seed)
    mean = rng.normal(0, 0.5, NP); std = np.full(NP, 0.5)
    w = 0.0 if mode == 'curriculum' else (0.0 if mode == 'none' else width)
    for it in range(iters):
        theta = mean + std * rng.normal(size=(pop, NP))
        sc = sample_scales(rng, n_env, w)
        L = rollout(theta, sc, rng)
        fit = L.mean(1)
        el = np.argsort(-fit)[:pop // 5]
        mean = theta[el].mean(0); std = theta[el].std(0) + 0.05 * (1 - it / iters) + 0.01
        succ = float((L[el[0]] >= T_MAX).mean())   # success rate of best candidate on this iteration's draw
        log.append((it, w, float(fit.max())))
        if mode == 'curriculum' and succ >= thresh:
            w = min(wmax, w + step)
    return mean, w


def evaluate(theta, seed):
    rng = np.random.default_rng(10_000 + seed)   # eval draws disjoint from training stream
    out = {}
    for name, w in [('nominal', 0.0), ('w25', 0.25), ('w50', 0.5), ('w75', 0.75), ('w100', 1.0), ('w150', 1.5), ('w200', 2.0)]:
        sc = sample_scales(rng, 300, w)
        L = rollout(theta[None], sc, rng)[0]
        out['ret_' + name] = float(L.mean())
        out['succ_' + name] = float((L >= T_MAX).mean())
    out['ret_robust'] = float(np.mean([out['ret_' + k] for k in ('w25', 'w50', 'w75', 'w100', 'w150', 'w200')]))
    out['ret_ood'] = float(np.mean([out['ret_w150'], out['ret_w200']]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--system', required=True)   # none | uniform | curriculum
    ap.add_argument('--task', default='cartpole')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--width', type=float, default=0.0)
    ap.add_argument('--iters', type=int, default=60)
    ap.add_argument('--pop', type=int, default=40)
    ap.add_argument('--n_env', type=int, default=16)
    ap.add_argument('--step', type=float, default=0.05)
    ap.add_argument('--thresh', type=float, default=0.8)
    ap.add_argument('--wmax', type=float, default=0.75)
    ap.add_argument('--curve', default='')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    log = []
    theta, wend = train(a.system, a.width, a.seed, a.iters, a.pop, a.n_env, a.step, a.thresh, a.wmax, log)
    m = evaluate(theta, a.seed)
    m['train_width_end'] = float(wend)
    json.dump(m, open(a.out, 'w'))
    print(json.dumps(m))
    if a.curve:
        with open(a.curve, 'w') as f:
            f.write('step,value,seed,name\n')
            for it, w, _ in log:
                f.write(f'{it},{w},{a.seed},{a.system}\n')


if __name__ == '__main__':
    main()
