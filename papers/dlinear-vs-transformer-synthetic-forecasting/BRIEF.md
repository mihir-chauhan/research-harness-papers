# Are simple linear models enough for long-horizon forecasting

## Seed
Are simple linear models enough for long-horizon forecasting? On synthetic series with controlled trend, multiple seasonalities, noise and regime changes (and on ETTh1 if the public CSV of a few MB downloads), compare seasonal-naive, a DLinear-style decomposition-plus-linear model, a small patch transformer and a small GRU at horizons 24, 96 and 192. Find which data properties, if any, make the nonlinear models win.

## Research question
Are simple linear models enough for long-horizon forecasting? On synthetic series with controlled trend, multiple seasonalities, noise and regime changes (and on ETTh1 if the public CSV of a few MB downloads), compare seasonal-naive, a DLinear-style decomposition-plus-linear model, a small patch transformer and a small GRU at horizons 24, 96 and 192. Find which data properties, if any, make the nonlinear models win.

Field: time-series long-horizon-forecasting
Scale: quick study, cpu, about 30 minutes of experiments.

## Precise study design (decided by the author agent)

**Question.** On univariate-per-channel series with controlled trend, multiple seasonalities, noise and
regime changes, and on ETTh1, when (if ever) does a small patch transformer or a small GRU beat a
DLinear-style decomposition+linear model, at horizons 24, 96, 192?

**Systems (all reimplemented here, same look-back 336, same instance normalisation, same budget).**
Seasonal naive (period in {24,168} picked on validation), DLinear-style (moving-average decomposition + two
linear maps), PatchTST-style (patch 16/stride 8, 2-layer encoder, d=64, flatten head), GRU (patches of 8 as
time steps, hidden 64). No hyper-parameter tuning: learning rates fixed a priori; the checkpoint with best validation MSE
(evaluated every 100 of 400 steps) is kept.

**Tasks.** Synthetic (4 channels x 8000 steps, 60/20/20 chronological split, seed = new dataset):
`seas1` (one period-24 sine), `trend` (+ piecewise-linear trend), `multiseas` (periods 24/168/12),
`noisy` (multiseas, AR(1) noise sd 1.5 instead of 0.3), `regime` (multiseas with Markov switching of periods and
amplitudes, mean dwell 500 steps). Real: `etth1` (7 channels, standard 12/4/4-month split, channel-independent).

**Hypotheses (falsifiable; "win" = lower seed-mean test MSE by >=5% relative AND lower in all 3 seeds).**
- H1: without regime changes (seas1, trend, multiseas, noisy) no nonlinear model wins over DLinear at any horizon.
- H2: with regime changes (regime) at least one nonlinear model wins at H=96 and 192, and the margin grows with
  switching rate (sweep over mean dwell).
- H3: raising noise erases any nonlinear advantage (sweep over noise sd on regime task).
- H4: on ETTh1, DLinear is not beaten by the patch transformer or GRU at H=96 and 192, and all learned models beat seasonal naive.
- H5 (design check): removing the decomposition (single linear map) changes DLinear MSE by <5% on trend, regime, etth1 at H=96.

**Metrics.** MSE (primary) and MAE on z-scored data, per horizon (mse_24, mse_96, mse_192), plus runtime.
**Ablations / sensitivity.** `abl_design` (no decomposition; no instance norm for each learned model, H=96, trend/regime/etth1),
`sweep_dwell`, `sweep_noise` (regime task, H=96).
**Training-budget sweep (added in the fix round after the independent audit; post hoc, not registered).** The audit showed that
the 400-step verdicts change at 2000 steps. Added with unchanged code and settings except `--steps`: `sweep_steps` (regime and etth1 at
1000 and 2000 steps, all horizons; seas1/trend/multiseas/noisy at 2000 steps, H=96) and `sweep_dwell_2000` (dwell sweep at 2000 steps,
H=96). Hypotheses and the win rule are unchanged; verdicts are reported per budget. The noise sweep and the design ablation exist at
400 steps only.
**Out of scope.** Large benchmarks, tuning, probabilistic forecasts, multivariate cross-channel models, foundation models,
statistical tests beyond 3-5 seeds.
