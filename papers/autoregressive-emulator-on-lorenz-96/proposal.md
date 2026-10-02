# Proposal

## Question
Does training a circular-CNN emulator of the 36 slow Lorenz-96 variables on a K-step rollout loss (K=4, 8) improve forecast skill over one-step training (K=1), and what does it do to long-run stability and climatological variance?

## Hypotheses (tests registered before running; paired by seed, 5 seeds, `rh compare`, alpha 0.05)
- H1: K=4 and K=8 have lower rmse_t20 (lead 2.0 time units) than K=1. Refuted if K=1 is not worse or the difference is within noise.
- H2: K=1 has lower stable_frac in 200-time-unit free runs than K=4/8. Refuted if all are stable.
- H3: multi-step training lowers var_ratio (climatological variance of the emulator / truth) below K=1 and below 1. Refuted if var_ratio is not lower.
- H4: CNNs beat persistence, climatology and linear stencil in acc_leadtime (lead at which mean ACC falls below 0.6).

## Method
Truth: two-scale L96 (K=36, J=10, F=10, h=1, c=b=10), RK4 dt=0.005, sampled every 0.05. Emulator sees only slow variables X. Residual 4-layer circular CNN (width 32, kernel 5, 10.7k params), loss = mean over K steps of normalised MSE, full BPTT. Fixed 1500 Adam steps, batch 32.

## Baselines
Persistence, climatology (training mean), linear 5-point stencil fitted by ridge regression (all reimplemented), CNN K=1.

## Ablations
Rollout length K=2 (sweep), input noise for K=1 (0.03, 0.1).

## Risks
All CNN variants may be equally stable and equally skilful at this scale (null result); the unobserved fast variables cap skill.

Note (post-hoc): the sweep_ntrain ablation (smaller training set) was added after registration and is exploratory.
