# Proposal

## Direction
Operator learning on 1D viscous Burgers at small scale; FNO vs DeepONet vs MLP/CNN; zero-shot finer-grid evaluation.

## Question
With 400 training pairs at 128 grid points, how do a small FNO, DeepONet, MLP and CNN compare in test relative L2, and how does each behave when evaluated on 256- and 512-point grids without retraining?

## Hypotheses (decision rules fixed before running)
| ID | Hypothesis | Group | Metric | Refuted if |
|---|---|---|---|---|
| H1 | FNO has lower rel_l2 than DeepONet, MLP, CNN at 128 pts | main | rel_l2 | Welch t-test as reported by `rh compare` (alpha .05, 5 seeds) fails against any baseline, or FNO <10% better than the best baseline |
| H2 | FNO rel_l2_256/rel_l2 < 1.5 and CNN's ratio > 1.5 | main | rel_l2_256 / rel_l2 | FNO ratio >= 1.5 or CNN ratio <= 1.5 |
| H3 | FNO saturates in modes: 8->16 changes error <10%; 4 modes clearly worse | sweep_modes | rel_l2 | otherwise |
| H4 | FNO beats DeepONet at n_train 100, 200, 400 | sweep_ntrain | rel_l2 | DeepONet mean error <= FNO mean at any n_train |

## Method / baselines
FNO (Li et al. 2020), DeepONet (Lu et al. 2019), plain MLP, plain CNN - all reimplemented in PyTorch. Same data, loss (relative L2), optimiser (Adam, one-cycle), epochs, batch size, checkpoint selection on a validation split; learning rate chosen from {3e-4,1e-3,3e-3} on a separate tuning seed. (Amendment after tuning, before the main runs: grid extended to 1e-2, see experiments/PROTOCOL.md. Hypotheses and tests unchanged.)

## Data
600 samples per seed (400 train / 100 val / 100 test), nu=0.01, T=1, ETDRK4 at 512 points subsampled to 128/256/512. 5 seeds (seed changes data and initialisation).

## Metrics
Mean-over-samples relative L2 at 128 (train grid), 256 and 512 (zero-shot, native), and a resampled variant (input subsampled to 128, output Fourier-interpolated).

## Out of scope
Physics-informed losses, autoregressive rollout, other PDEs, CNO/U-Net/transformers, GPU-scale studies.
