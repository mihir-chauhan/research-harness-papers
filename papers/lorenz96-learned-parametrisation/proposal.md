# Proposal

## Direction
Lorenz-96 as a testbed for learned subgrid parametrisation: replace the fast variables of the two-scale L96 by (a) a polynomial closure fitted by regression, (b) a small MLP, (c) a stochastic AR(1) closure; compare short-term forecast skill, long-rollout stability and slow-variable climate (mean, variance, spectrum) with the full two-scale truth.

## Question
With identical training data, inputs and metrics, how do deterministic polynomial, deterministic MLP, and polynomial+AR(1) closures differ in (i) forecast skill, (ii) free-run stability and (iii) climate fidelity, and does the answer change with scale separation and a forcing shift?

## Method
Truth: K=8, J=32, h=1, b=10, F=20, c=10 (task F20_c10) and c=4 (task F20_c4, weaker separation). Closure U_k = g(X_k) learned offline from (X_k, U_k) pairs (U_k = hc/b sum_j Y_jk). Slow-only model dX/dt = f(X) - g(X) - e. AR(1): e_{n+1} = phi e_n + sigma sqrt(1-phi^2) xi_n fitted to polynomial residuals. Reimplemented, no external code.

## Baselines
No closure (U=0) as lower reference; polynomial (Wilks 2005 style, degree 4 fixed a priori); MLP 1-32-32-1 tanh. Reference "truth, independent run" gives the sampling-noise floor of the climate metrics.

## Metrics
valid_time (higher better; first lead where ensemble-mean RMSE/clim. std > 0.5, 100 ICs, 2 t.u. horizon), rmse_0p5 (lower), stable_frac (higher; 20 chains x 400 t.u., diverged if |X|>60 or non-finite), mean_err, var_err, w1_pdf, spec_err (lower). offline_r2 (higher) reported.

## Hypotheses (tests registered before any logged run; 5 seeds main, 3 seeds ablations; alpha=0.05 with `rh compare` per-metric significance of each system against the reference system, directions as stated)
- H1 (skill): each of the three learned closures has higher valid_time than No closure on both tasks. Refuted if any closure is not better (p>=0.05 or wrong sign) on F20_c10.
- H2 (climate, stochastic): AR(1) has lower var_err and lower spec_err than the deterministic polynomial on F20_c10. Refuted if either is not lower; inconclusive if the direction is right but p>=0.05.
- H3 (MLP vs polynomial): with the same local input X_k, the MLP is not better than the polynomial: offline R2 differs by <0.01 and valid_time and spec_err differences have p>=0.05. Refuted if the MLP is significantly better on valid_time or spec_err.
- H4 (stability / shift): all closures are stable (stable_frac = 1) in-regime; under a forcing shift (trained at F=20, deployed at F=18 and F=22) the MLP has larger climate error (w1_pdf) than the polynomial. Refuted if the MLP w1_pdf is not larger on average in both shifts.
- H5 (AR(1) memory): stochastic benefit comes from temporal correlation: AR(1) with phi=0 (white noise, same variance) has larger spec_err than AR(1) with fitted phi on F20_c10. (Descriptive, 3 seeds.)

## Ablations / sensitivity
polynomial degree 1-6; AR(1) noise amplitude (x0.5, x1, x1.5) and phi=0; MLP stencil width 0/1/3 (local vs neighbours); forcing shift.

## Out of scope
Online (coupled) training, GAN/RNN stochastic closures, data assimilation, state-dependent noise, more than 8 slow variables.

## Risks
Differences between closures may be within noise; deterministic closures may be stable at these settings so H4 stability is trivial.
