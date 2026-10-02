# Results (10 seeds; two-sided paired t-tests, unadjusted)
Tables in `results/tables` are written by `analysis/make_tables.py` from `results/runs.jsonl`; its printed counts are in
`results/tables/analysis_log.txt`. Every paired p-value is in `deltas_all.csv` (correction vs none), `threshold_tests.csv`
(operating point) or `abl_prior_summary.csv` (offset), and 408 of them were re-computed with `rh compare`
(`results/tables/compare/`, `experiments/run_compare.sh`): maximum absolute difference 1.1e-16.

- H1 (no AUROC/AUPRC gain >= 0.01): mostly supported for LR (|dAUROC| <= 0.003 in all 12 cells; reweight/ROS slightly worse
  at 1:5). For GB mixed: refuted in one cell (ROS, 1:5, AUPRC +0.011, p<0.05, one of 18 tests); GB worse at 1:50 (not
  significant). Rows: deltas.tex.
- H2 (Brier and |CITL| worse at 1:20, 1:50): Brier higher in 11/12 cells, none significant (min p 0.085); refuted for the
  cell LR + SMOTE at 1:20 under the registered rule. |CITL| higher in only 5/12 cells, none significant (min p 0.11): not
  supported. Rows: deltas.tex, citl.tex.
- Signed calibration (not registered, added in the revision): for LR every correction lowers signed CITL in all 12 cells
  (p <= 0.0002); a goes from +0.33..+0.76 (underestimation) to -0.35..-0.89 (overestimation) at 1:5, 1:20, 1:50 and to
  about 0 at natural prevalence. Signed LR slope is lower with a correction at 1:5-1:50 (p = 0.0002-0.027, 9 cells), not at
  natural prevalence. |b-1| does not change significantly in any LR cell (p >= 0.16). GB: signed CITL lower at natural
  prevalence (p <= 0.0002), otherwise only SMOTE at 1:5 (p = 0.027). Rows: citl.tex, main_1to20.tex, deltas_all.csv.
- H3 (threshold moving): probability metrics identical by construction (max abs diff 0); sensitivity up, specificity down;
  LR balanced accuracy up at 1:5, 1:20, 1:50 (p<0.01). Supported.
- Operating point of the corrections (not registered, added in the revision): reweighting, ROS and SMOTE also raise LR
  sensitivity at the 0.5 cut-off in all 12 cells (p <= 0.012) and LR balanced accuracy at 1:5, 1:20, 1:50 (p = 0.0003-0.032).
  Threshold moving raises balanced accuracy more than each correction at 1:20 and 1:50 (p < 0.01). For GB the corrections
  help only in one cell (SMOTE, 1:5). Rows: operating.tex, threshold_tests.csv.
- H4 (prior offset restores Brier within 0.005): formally met in 23/24 cells but raw gaps already below 0.005 in 22/24; the
  gap shrinks in magnitude in 11/24 cells (LR 2/12, GB 9/12); mean |CITL| increases in 24/24 cells (p<0.05 in 10).
  Refuted in spirit. Rows: abl_prior_brier.tex, citl.tex, abl_prior_summary.csv.
- Extremes checked: calibration slope ranges 0.19 to 18.6 (largest values: GB at 1:50, seed 8), CITL -11.5 to 9.6 (GB, a few
  saturated false positives or misses), none at the +-20 search bound; minimum AUROC 0.58 (GB + ROS/SMOTE, 1:50, seed 9).
