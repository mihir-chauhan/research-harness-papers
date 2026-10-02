# Autoregressive emulator on Lorenz-96 -- brief

**Question.** For a small circular 1D CNN emulating the 36 slow variables of two-scale Lorenz-96 (fast variables hidden), what does training on a K-step rollout loss (K=1,2,4,8) change in forecast skill (RMSE, ACC vs lead), long-run survival, and climatological variance?

**Hypotheses (tests registered in proposal.md).** H1 K=4/8 lower RMSE at lead 2 than K=1 (paired test over 5 seeds). H2 K=1 less stable in 200-time-unit free runs. H3 multi-step training lowers variance ratio. H4 CNNs beat persistence, climatology, linear stencil in ACC lead time.

**Method.** Truth: NumPy RK4 two-scale L96 (K=36, J=10, F=10, h=1, c=b=10), sampled every 0.05. Emulator: residual circular CNN, 4 conv layers width 32, 1500 Adam steps, K-step loss with full BPTT.

**Baselines (reimplemented).** Persistence, climatology, ridge linear 5-point stencil; CNN K=1 is the one-step reference.

**Tasks / metrics.** One task (l96). RMSE and ACC at leads 0.5,1,2,3,5; ACC lead time; stable_frac, survival_time, var_ratio, roughness_ratio, KS in 200-time-unit free runs.

**Ablations.** K=2 sweep point; input noise (0.03, 0.1) for K=1; 4 vs 32 training trajectories.

**Out of scope.** Ensembles / CRPS, other architectures, K>8, equal-compute comparisons, real weather data.

**Decisions.** See `rh decide` log: lr 3e-3 from validation tuning on seed 100; method display name "CNN K=4"; fixed optimiser budget across K.
