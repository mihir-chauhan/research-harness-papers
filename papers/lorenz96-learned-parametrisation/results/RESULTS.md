# Results (F20_c10 primary; 5 seeds main, 3 ablations; Welch p from `rh compare`, uncorrected)
- H1 supported: valid_time 0.363 (no closure) -> 1.398 poly / 1.421 MLP / 1.252 AR(1) at c=10; 0.673 -> 1.097 / 1.099 / 0.942 at c=4; all p<1e-6 (main table, compare_main_valid_time_ref_noclosure.csv).
- H2 supported at c=10 (var_err 0.002 vs 0.042, p=1.7e-4; spec_err 0.056 vs 0.144, p=5.6e-4), not at c=4 (spec_err 0.007 vs 0.009, p=0.33; var_err nominally worse). AR(1) loses valid time (1.252 vs 1.398, p=2.9e-4; c=4: 0.942 vs 1.097, p=8.1e-5; compare_main_valid_time_ref_polynomial.csv).
- H3 supported: offline R2 0.850 vs 0.847; valid_time p=0.36 (c=4: p=0.92; compare_main_valid_time_ref_polynomial.csv), spec_err p=0.67 (c=10). Absence of evidence only (n=5; paired valid_time p=0.051).
- H4 stability supported but trivial (stable_frac=1 everywhere); shift part refuted (MLP w1_pdf lower than poly at F=18 and F=22); shift too mild to test extrapolation.
- H5 weakly supported descriptively (n=3): white noise spec_err 0.067 vs fitted AR(1) 0.057; deterministic 0.137.
- Failure cases: polynomial degree 2 (spec_err 0.381); AR(1) at F=18 (worse than poly). Exploratory: MLP with neighbour inputs better (3 seeds).
Tables: results/tables/*.md|tex; figures: results/figures.
