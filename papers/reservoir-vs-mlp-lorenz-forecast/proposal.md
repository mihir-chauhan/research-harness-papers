# Proposal

## Question
ESN vs one-step MLP on delay coordinates vs small GRU, on Lorenz-63 and Lorenz-96 (D=10): valid prediction time (VPT, Lyapunov times) and climate fidelity of long free runs; sensitivity of the ESN to spectral radius and size; data requirements. Full protocol in `BRIEF.md` and `experiments/PROTOCOL.md`.

## Closest work and gap
See `literature/landscape.md`: pathak2017using (ESN), vlachas2018data / vlachas2020backpropagation (RNNs vs RC), haluszczynski2019good (short-term vs climate), racca2021robust (ESN hyperparameter validation), gauthier2021next (data efficiency of RC variants). Gap: a same-protocol head-to-head of the three families with sensitivity and data sweeps at CPU scale. No novelty claim.

## Hypotheses and registered tests
Unit of analysis: seed (5 seeds main, 3 seeds sweeps). Tests are run with `rh compare` (paired by seed against the ESN) and summarised by mean over seeds; alpha = 0.05, but with 5 seeds the tests are low-powered and we report effect sizes too.
- H1 (ESN longest VPT at 5000 steps): supported on a task if the ESN mean VPT exceeds both MLP and GRU means and `rh compare` gives p<0.05 against each. Refuted on a task if any competitor's mean is >= the ESN's.
- H2 (VPT and climate dissociate): supported if the order of the three systems by mean `clim_ok` differs from the order by mean `vpt` on at least one task. Refuted if orders agree on both tasks.
- H3 (spectral-radius sensitivity): supported if, on each task, max/min of mean VPT over the swept radii (sweep rows plus the main-table setting for seeds 0-2) exceeds 2. Refuted if the ratio is <= 2 on either task.
- H4 (size): supported if the mean VPT at N=1000 exceeds that at N=100 on both tasks (seeds 0-2). Refuted otherwise.
- H5 (data efficiency): supported on a task if at n_train=500 the ESN mean VPT exceeds both neural models' mean VPT. Refuted if any neural model's mean is >= the ESN's.
Descriptive, no test: smallest n_train at which each system reaches 80% of its own VPT at the largest n_train.

## Baselines
MLP on delay coordinates and GRU, reimplemented; ESN is the reference ("method" slot in `research.yaml`, though no new method is proposed).

## Fix round after the audit (tests unchanged)
The hypotheses and the registered tests above are unchanged. What changed is the measurement, for all systems alike: Lyapunov constants 0.905 / 1.158 (logged), deterministic ESN construction, climate metrics from 20 free runs of 10000 steps (length fixed on the validation seed), MLP and GRU optimiser steps and learning rate tuned on the validation seed, training-length grid 500 / 2000 / 5000 / 10000. Component ablations are logged in group `main` (same data and seeds as the full systems) so that `rh compare --ref` pairs each ablation with its full system. A descriptive optimiser-step sweep (`sweep_steps`) was added; it has no hypothesis.
