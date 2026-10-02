# Protocol
Tasks bc_natural (212:357), bc_1to5, bc_1to20, bc_1to50 (train positives 50, 12, 5 approx.). Seeds 0-9, each a different stratified 70/30 split and different subsample/resampling randomness. No hyperparameter tuning (equal budget zero) for all systems. Same metric code for every system. Hardware: CPU, 2 threads, macOS. Groups: main (10 arms x 4 tasks x 10 seeds = 400 runs), abl_priorcorr, sweep_smote_ratio.

Statistics: two-sided paired t-tests over seeds, unadjusted, computed by analysis/make_tables.py (scipy.stats.ttest_rel) and cross-checked with `rh compare` via experiments/run_compare.sh (results/tables/compare/). Slopes and |b-1| are summarised by median [IQR]; other metrics by mean (sd).
