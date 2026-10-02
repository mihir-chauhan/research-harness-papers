# Design
`method/run.py` is the single entrypoint: `--system {snaive,dlinear,linear,patchtst,gru} --task {seas1,trend,multiseas,noisy,regime,etth1} --seed s --out file.json`.
- Look-back 336 for all systems; a separate model is trained per horizon (24, 96, 192); data z-scored with training statistics.
- Instance normalisation (window mean/std, de-normalised outputs) is applied identically to all learned models (`--no_norm` switches it off).
- snaive: y(t+h)=y(t+h-m*ceil(h/m)), m in {24,168} selected on validation MSE.
- dlinear: moving average (k=25, replicate padding) trend + remainder, two Linear(336,H) maps (shared across channels), summed. `linear` = one map, no decomposition.
- patchtst: patch 16, stride 8 (41 tokens), linear embedding + learned positions, 2 pre-norm encoder layers, d=64, 4 heads, ff 128, dropout 0.1, flatten + linear head, channel independent.
- gru: non-overlapping patches of 8 (42 steps), 1-layer GRU hidden 64, linear head on last state.
- Training: AdamW (wd 1e-4), cosine schedule, batch 64, 400 steps (budget sweep: `--steps 1000|2000`, nothing else changed), lr 3e-3 (dlinear, linear, gru), 1e-3 (patchtst), grad-clip 1; MSE loss;
  validation MSE every 100 steps (every 8th window), best checkpoint kept. No tuning of any hyper-parameter.
- Synthetic generator: sum of sinusoids with integrated phase; regimes rescale periods (x1, x1.6, x0.6) and amplitudes; piecewise-linear trend;
  AR(1) noise (rho 0.5, stationary sd = `noise`). 4 channels per dataset, seed 1000+seed.
