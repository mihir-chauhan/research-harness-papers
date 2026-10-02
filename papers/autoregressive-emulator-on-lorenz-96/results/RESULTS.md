# Results (5 seeds, group main unless noted; numbers in results/tables/*.md)
- H1 (K=4/8 lower rmse_t20 than K=1): supported for K=8 (paired p=0.0025, K=1 is 5.2% higher than K=8, i.e. 4.98% reduction relative to K=1), weak for K=4 (paired p=0.032, Welch p=0.49, 1.4% lower). Effect small; one-step RMSE worsens with K.
- H2 (K=1 less stable): refuted -- stable_frac = 1 for every system, including K=1.
- H3 (multi-step lowers variance): not supported -- var_ratio 1.003/1.002/0.998 for K=1/4/8, paired p 0.63 (K=4), 0.08 (K=8).
- H4 (CNN beats baselines in ACC lead time): supported (about 4.0 vs 0.19/0.02/0.37 time units). Failure: RMSE at lead 5 exceeds climatology for all CNNs.
- Ablations: input noise hurts and damps variance/roughness; 8x less training data changes nothing.
