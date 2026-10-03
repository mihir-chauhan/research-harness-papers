"""Diagnostic: on states visited by the greedy hand-heuristic proof of each task problem, how often does the trained
policy's top-1 tactic agree with the heuristic's top-1 tactic, and, among states that offer both a non-branching and
a branching tactic, how often does it choose a non-branching one ('defer_rate')?
usage: diag.py --system transformer|mlp --task T --seed N --out file"""
import argparse, json, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import torch
from logic import gen_provable, candidates, apply, open_goals, branches
from search import heuristic_costs
import policy as P
from run import TASKS, NPROB, DEFAULTS, train_policy

ap = argparse.ArgumentParser()
ap.add_argument('--system', required=True); ap.add_argument('--task', required=True)
ap.add_argument('--seed', type=int, required=True); ap.add_argument('--out', required=True)
a = ap.parse_args()
cfg = dict(DEFAULTS)
print('config', json.dumps({'system': a.system, 'task': a.task, 'seed': a.seed, **cfg}), flush=True)
model, _, _ = train_policy(a.system, a.seed, cfg, print)
enc = P.encode if a.system == 'transformer' else P.features
bt = P.batch_tf if a.system == 'transformer' else P.batch_mlp
lo, hi, off = TASKS[a.task]
probs = gen_provable(random.Random(100000 * off + a.seed), lo, hi, NPROB)
agree = n = mixed = defer = 0
for p in probs:
    goals = open_goals([p])
    steps = 0
    while goals and steps < 300:
        g = goals[0]
        hc = heuristic_costs(g, cfg['heur'])
        top_h = min(hc, key=lambda x: x[1])[0]
        with torch.no_grad():
            lg = model(*bt([enc(g)]))[0].tolist()[:len(candidates(g))]
        c = candidates(g)
        top_p = c[int(np.argmax(lg))]
        n += 1; agree += top_p == top_h
        br = [branches(t, g) for t in c]
        if any(br) and not all(br):
            mixed += 1; defer += not branches(top_p, g)
        goals = open_goals(apply(g, top_h)) + goals[1:]
        steps += 1
out = dict(agree_heur=agree / n, defer_rate=defer / max(mixed, 1), mixed_frac=mixed / n, n_states=n)
print('final', json.dumps(out)); json.dump(out, open(a.out, 'w'))
