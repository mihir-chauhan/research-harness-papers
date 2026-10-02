# Protocol
Tasks: chain_10/20/40, room_2/4/6, chain_20_tv, room_4_tv. Budget 30k steps (chains) / 100k (rooms), online, one environment. Seeds 0-4 for every cell. No train/test split: metrics are online training metrics plus one greedy rollout at the end.

Every run of the study is produced by `experiments/run_all.py` through `rh run`, from one commit that contains the code; each run has its own metrics file (`results/raw/r2/`) and records its full configuration (beta, offset, K, warmup, clip). All systems share alpha 0.5, gamma 0.99, eps 0.1, beta 0.1, K 16 and the same budgets; the only per-system settings are the system definition itself (see `method/DESIGN.md`).

Groups:
- `main`: Epsilon-greedy Q-learning, Step penalty only (optimistic init), Count bonus (state), no offset, Count bonus (state), Count bonus (obs), RND bonus (method, guarded normaliser), and the four RND normaliser ablations (no bonus normalisation, unguarded normaliser (v1), warm-up only, clip only). 10 systems x 8 tasks x 5 seeds = 400 runs.
- `sweep_beta`: beta in {0.03, 0.3, 1} on room_4, RND bonus and Count bonus (state); the beta = 0.1 cell is the `main` run.
- `sweep_K`: K in {1, 4, 64} on room_4_tv, RND bonus and Count bonus (obs); K = 16 is the `main` run.
- `sweep_clip`: clip in {2, 20} on chain_20 and room_4, RND bonus; clip 5 is the `main` run and "no clip" is the warm-up-only ablation.
- `pilot` (kind sanity, seed 100, chain_40 and room_6): bonus systems without the offset, and two with it. This is the pilot that motivated the offset; it is not used in any table of results.

Tuning budget: none on the evaluation seeds. The offset was introduced after the seed-100 pilot. The normaliser guard (warm-up 64, clip 5) was fixed a priori after an audit found that the first version's normaliser divided by a zero running std; the first version's runs remain in the registry as superseded rows.

Statistics: mean and sample standard deviation over 5 seeds; Welch and paired t-tests from `rh compare` (uncorrected, on budget-censored values, descriptive).
Hardware: one laptop CPU, numpy, two processes at a time; under 9 s per run, about 20 CPU-minutes for all 492 runs (main 400, sweeps 80, pilot 12).

Rebuild: `python experiments/run_all.py all` (runs), `sh experiments/build_results.sh` (rh table, rh compare, method/make_tables.py, rh verdict), `rh paper build`.
