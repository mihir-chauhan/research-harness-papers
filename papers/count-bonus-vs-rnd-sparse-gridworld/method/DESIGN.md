# Design
`method/run.py`: numpy tabular Q-learning (alpha 0.5, gamma 0.99, eps 0.1 epsilon-greedy with random tie-breaking, Q0 = 0), online, single environment, reward only at the goal (terminal).
Update target: r + beta*(b - offset) + gamma*max Q(s'), offset = 1, beta = 0.1, with b the bonus of the arrival observation (epsilon-greedy has no bonus and no offset: its shaped reward is 0).

Systems (`--system`, flags):
- `egreedy`: no bonus, no offset.
- `offset_only` ("Step penalty only (optimistic init)"): b = 0 with the offset, i.e. a constant reward of -beta per step.
- `count_state`: b = 1/sqrt(N(s')). With `--offset 0`: "Count bonus (state), no offset".
- `count_obs`: b = 1/sqrt(N(s', token)), token = noisy-TV value (-1 elsewhere).
- `rnd` (method, "RND bonus"): obs = [onehot(state) (S), onehot(TV token) (K)]; fixed random target MLP (hid 64, out 16, tanh, no biases, output layer scaled by 2), trained predictor MLP of the same layer sizes with biases (Adam lr 3e-3, one step on the last 8 observations every 8 transitions). e = prediction MSE; sigma = running std of all errors seen so far (the error is added to the statistics before the bonus is computed).
  Guarded normaliser (default): b = 1 for the first `--warmup` = 64 errors (no intrinsic signal, b - offset = 0), then b = min(e / (sigma + 1e-8), `--clip` = 5).
- `rnd --warmup 0 --clip 0`: "RND, unguarded normaliser (v1)", b = e / (sigma + 1e-8) from the first step. This is the normaliser of the first version of the study. When the first errors coincide (the agent stays on the start cell and the predictor has not been updated yet) sigma = 0 and b is 1e6-1e7.
- `rnd --clip 0`: "RND, warm-up only". `rnd --warmup 0`: "RND, clip only".
- `rnd_nonorm`: b = e (raw MSE), "no bonus normalisation (rnd_nonorm)".

W = 64 (eight predictor updates) and c = 5 were set a priori, not tuned; the clip sweep (c in 2, 5, 20, none) reports the sensitivity.
The offset centres the bonus so that untried actions (Q = 0) look better than visited ones; the pilot (seed 100, group `pilot` in the registry) is the run that motivated it.

Envs: chain_N (N states, goal at right end, episode limit 2N, TV cell at index 1); room_R (R rooms of 5x5 cells in a row, one door per wall at varying heights, start top-left, goal bottom-right, limit 12R+16, TV at cell (2,2) in room 1). `_tv` tasks: the TV cell emits a uniform random token in {0..K-1} (K=16 default) on every visit.

Metrics: steps_to_first_reward (budget if never), found_reward, final_return (mean of last 20% training episodes), greedy_success (greedy policy reaches goal), tv_time_frac, coverage (non-TV cells visited).
Diagnostics (logged for every run): bonus_max, bonus_max_early (max over the first 100 steps), bonus_median, bonus_gt1_frac (share of steps with b > 1, i.e. a positive shaped reward), bonus_clip_frac (share of steps where the clip was active), q_abs_max (largest |Q| written during the run). All refer to the raw bonus b before the offset.

Scripts: `experiments/run_all.py` (every registry run, through `rh run`), `method/make_tables.py` (tables and figures from `results/runs.jsonl`).
