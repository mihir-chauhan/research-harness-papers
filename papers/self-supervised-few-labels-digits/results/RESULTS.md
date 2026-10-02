# Results (5 seeds, test accuracy; tables in results/tables/)
- H1 SimCLR > supervised scratch at every budget: SUPPORTED at n10 (0.826 vs 0.662) and n50 (0.955 vs 0.918); INCONCLUSIVE at n200 (0.979 vs 0.976, paired p=0.18).
- H2 SimCLR > rotation: SUPPORTED at all budgets. Rotation (0.441/0.772/0.908) is below the random encoder at all budgets.
- H3 SSL > PCA at n10 and gap within 2 points at n200: REFUTED in part. SimCLR beats PCA at n10 (0.826 vs 0.505) but the n200 gap is 0.065; rotation does not beat PCA at n10.
- H4 removing an augmentation family lowers SimCLR at n50: SUPPORTED modestly (0.955 full; 0.927 geom-only; 0.918 photo-only); inconclusive at n10 (std 0.116).
Ablations: abl_aug, abl_supaug, sweep_tau, sweep_epochs. Registry de-duplicated (see `rh decide`).
