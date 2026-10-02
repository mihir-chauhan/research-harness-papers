# Design
method/l96.py: two-scale L96 (RK4, dt 0.0025, sampled every 0.005) and slow-only RK4 step (dt 0.005; closure evaluated at each stage, AR(1) noise held fixed within a step).
method/run.py: data caching (data/), closures (Poly via least squares on standardised X_k; MLP 1-32-32-1 tanh, Adam 3e-3 cosine, 40 epochs, batch 1024, best-validation-epoch on 4 held-out chains; AR(1) on polynomial residuals), evaluation.
Training data per seed: 16 chains x 25 t.u. (after 20 t.u. spin-up), thinned x4 -> 8x(~20000)x... pairs; validation 4 chains; test 10 chains x 30 t.u.; reference: 40 chains x 100 t.u. (fixed seed 9999); noise-floor: independent 40x100 run per seed.
AR(1): phi = lag-1 autocorrelation of residuals at 0.005, sigma = residual std (x sigma_scale), noise initialised from its stationary distribution (the unobserved fast state is not known at forecast start).
Forecast: 100 ICs (10 per chain, every 3 t.u., on 10 test chains), 10 members, 2 t.u.; valid time threshold 0.5 of reference std on the ensemble mean.
Climate: 20 chains x 400 t.u. from random reference states, 10 t.u. discarded, X stored every 0.05; compared to the reference pooled over sectors.
Hyperparameters were fixed a priori; none tuned.
Step-size pre-check: experiments/precheck_dt.py (logged as a sanity run) compares mean and variance of X at dt 0.0025 and 0.00125.
