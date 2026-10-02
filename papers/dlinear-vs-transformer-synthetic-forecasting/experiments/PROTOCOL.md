# Protocol
Tasks: seas1, trend, multiseas, noisy, regime (synthetic, 4 ch x 8000, 60/20/20 chronological), etth1 (first 14400 rows, 8640/2880/2880, 7 channels).
Systems: Seasonal naive, DLinear, PatchTST (reimplemented), GRU. Horizons 24/96/192, look-back 336. Metrics: MSE, MAE on z-scored data over all test windows (stride 1, no dropped batch).
Seeds 0,1,2 (synthetic: a different dataset per seed, same dataset for all systems; ETTh1: init/sampling only). No tuning; best-validation checkpoint.
Ablations: abl_design (H=96; trend, regime, etth1), sweep_dwell and sweep_noise (regime task, H=96).
Training-budget sweep (post hoc, after the audit): sweep_steps = regime and etth1 at 1000 and 2000 steps (all horizons) and seas1/trend/multiseas/noisy
at 2000 steps (H=96); sweep_dwell_2000 = dwell sweep at 2000 steps (H=96). Same code and settings as the main grid except --steps (cosine schedule
spans the budget; validation checkpoint every 100 steps). 400-step cells are the main-grid / sweep_dwell rows. Runner: experiments/run_budget.sh.
Hardware: shared CPU machine, 2 threads per process, <=2 processes. Runner: experiments/run_all.sh.
