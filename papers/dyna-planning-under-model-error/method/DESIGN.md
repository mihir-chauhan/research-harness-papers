# Design
`method/run.py` implements four tabular agents in pure Python (reimplemented, no external RL code) on 6x9 mazes.
- Q-learning (n=0), Dyna-Q (uniform planning from a last-outcome deterministic model), Dyna-Q+ (planning reward r + kappa*sqrt(tau); untried actions of a newly visited state enter the model as self-loops with reward 0), prioritized sweeping (priority queue, threshold theta, predecessor lists).
- Fixed hyperparameters (no tuning): epsilon 0.1, alpha 0.5, gamma 0.95, kappa 1e-3, theta 1e-4, n=10 in the main group. Q initialised to 0, ties broken at random.
- Environment: start (5,3), goal (0,8), reward 1 at goal then reset to start; walls on row 2. Slip: with prob. 0.3 the action is replaced by a uniform random one. Changes happen at a fixed step.
- Ablations are flags: `--kappa 0` (no bonus), `--untried 0` (no untried-action init).
- Entry: `python method/run.py --system {q,dynaq,dynaq+,ps} --task T --seed S --n N --out FILE`.
