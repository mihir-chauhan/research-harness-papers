# Echo state networks versus delay-coordinate MLPs versus GRUs for forecasting Lorenz-63 and Lorenz-96

## Seed
Forecasting chaos: echo state networks (reservoir computing) versus an MLP on delay coordinates versus a small LSTM or GRU for Lorenz-63 and Lorenz-96, measured by valid prediction time in Lyapunov times and by whether long rollouts reproduce the attractor's statistics. How sensitive is the reservoir to spectral radius and size, and how much training data does each need?

## Precise question
On fully observed, noise-free Lorenz-63 (D=3, dt=0.02) and Lorenz-96 (D=10, F=8, dt=0.05), with each model trained once as a one-step predictor and rolled out in closed loop: (a) how do an echo state network (ESN), a one-step MLP on delay coordinates and a small GRU compare in valid prediction time (VPT, Lyapunov times) and in climate fidelity of long free runs; (b) how sensitive is the ESN to spectral radius and reservoir size; (c) how does each system's performance depend on the amount of training data.

## Decisions taken without a human (also in `rh decide`)
- Lorenz-96 uses D=10 (not 40) so a CPU study can train a recurrent net in under a minute; global (not local-parallel) reservoirs only.
- GRU is the recurrent baseline (LSTM is the same family; not run).
- Models are one-step predictors on standardised states, with residual output; MLP and GRU are trained with Adam for a number of steps (not epochs) and a learning rate that are tuned on the validation seed, and with Gaussian input noise (MLP {0, 0.01, 0.03}, GRU {0, 0.01, 0.03, 0.1, 0.3}).
- Hyperparameters are tuned on a separate validation trajectory (seed 100, 10 initial conditions) with a small grid per system and task (ESN 27 cells; MLP 9 model cells then 9 optimiser cells; GRU 5 noise cells then 6 optimiser cells); the criterion is mean VPT.
- Lyapunov exponents are measured here with Benettin's method (`method/lyap.py`): 0.905 (L63), 1.158 (L96, D=10), logged in the registry (group `lyapunov`); these set the unit of time.
- VPT: first time the RMS error (standardised units) exceeds 0.4, capped at 15 Lyapunov times, mean over 20 test initial conditions.
- Climate: 20 free-running rollouts of 10000 steps, one from each test initial condition (length chosen on the validation seed so that free runs of the true system pass the threshold below; a `True system` row gives the sampling floor); mean over components of the Wasserstein-1 distance between the rollout and a 15000-step reference trajectory (units of the reference std, per-rollout cap 1.0); `clim_ok` = fraction of rollouts with W1 < 0.1; `blowup` = fraction of rollouts that are non-finite or leave the box of 3x the largest reference magnitude (counted as W1 = 1).
- Seeds 0-4 for the main table and ablation; seeds 0-2 for the sweeps. A seed fixes the three trajectories (train, test, reference), the model initialisation (the ESN spectral radius comes from a dense eigensolver, so the reservoir is exactly reproducible) and the SGD sampling.
- Audit fix round (recorded with `rh decide`): all runs were redone with the points above; the earlier rows are superseded in the registry, not deleted. The ESN grid was not extended after the test-seed spectral-radius sweep showed a better radius on Lorenz-96, because that would be tuning on test seeds.

- Second fix round: H2's registered rule is met on Lorenz-63 by a 0.01 difference in `clim_ok` (paired p=0.70); the paper reports the rule as formally met and states that this is not evidence of a dissociation. The bar chart, the spectral-radius figure and the climate-versus-training-length table were dropped from the paper to keep it at 6 pages (their numbers stay in `results/`).

## Hypotheses (falsifiable; tests registered in `proposal.md`)
- H1: at tuned defaults and 5000 training steps the ESN has a longer mean VPT than both the MLP and the GRU on both tasks.
- H2: VPT and climate fidelity dissociate: the ranking of the three systems by `clim_ok` differs from their ranking by VPT on at least one task.
- H3: ESN VPT is sensitive to spectral radius: best/worst mean VPT over the swept radii exceeds 2 on each task.
- H4: ESN VPT grows with reservoir size: mean VPT at N=1000 exceeds that at N=100 on both tasks.
- H5: data efficiency: with 500 training steps the ESN reaches a longer VPT than MLP and GRU on both tasks.

## Method and baselines (all reimplemented in `method/`)
ESN (Pathak et al. style: sparse tanh reservoir, ridge readout, even-node squared features), MLP on delay coordinates (one-step, residual), GRU one-step forecaster (teacher forcing on windows). All three are compared; there is no new method.

## Tasks, metrics
Lorenz-63 and Lorenz-96 (D=10). Metrics: `vpt` (higher better), `clim_w1` (lower better), `clim_ok` (higher better), `blowup` (lower better), `fit_seconds` (training time).

## Ablations / sweeps
Spectral radius sweep, reservoir size sweep, training-set size sweep for all systems (500, 2000, 5000, 10000 steps), an optimiser-step sweep for the MLP and GRU, and a component ablation (ESN squared-feature readout, GRU input noise; the tuned MLP uses no input noise, so it has no noise ablation).

## Out of scope
Partial observation, observation noise, long-horizon (>15 Lyapunov times) forecasting, local parallel reservoirs, Kuramoto-Sivashinsky, next-generation RC, LSTM, hybrid models, GPU-scale training, Lyapunov-spectrum comparison of the learned models.
