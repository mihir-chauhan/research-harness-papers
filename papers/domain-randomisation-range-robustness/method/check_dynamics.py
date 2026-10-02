"""Check the batched simulator against gymnasium CartPole-v1 (scaled params) for a fixed action sequence."""
import numpy as np, gymnasium as gym, sys
sys.path.insert(0, 'method'); import run
rng = np.random.default_rng(0)
mx = 0
for k in range(5):
    sc = np.exp(rng.uniform(-.5, .5, 4)); env = gym.make('CartPole-v1').unwrapped; env.reset(seed=k)
    env.masscart = 1.0 * sc[0]; env.masspole = .1 * sc[1]; env.length = .5 * sc[2]; env.force_mag = 10 * sc[3]
    env.total_mass = env.masspole + env.masscart; env.polemass_length = env.masspole * env.length
    s0 = np.array(env.state); acts = rng.integers(0, 2, 30)
    for a in acts: o, *_ = env.step(int(a))
    # replicate with batched code
    tm = run.NOM['mc']*sc[0] + run.NOM['mp']*sc[1]; mp = .1*sc[1]; l = .5*sc[2]; pml = mp*l; fm = 10*sc[3]
    x, xd, th, thd = s0
    for a in acts:
        f = fm if a else -fm; ct, st = np.cos(th), np.sin(th)
        t = (f + pml*thd**2*st)/tm; ta = (9.8*st - ct*t)/(l*(4/3 - mp*ct**2/tm)); xa = t - pml*ta*ct/tm
        x, xd, th, thd = x+.02*xd, xd+.02*xa, th+.02*thd, thd+.02*ta
    mx = max(mx, np.abs(np.array([x, xd, th, thd]) - o).max())
print('max abs diff vs gymnasium after 30 steps:', mx)
