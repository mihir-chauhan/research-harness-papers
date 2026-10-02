# Response to the audit

No new experiment runs were needed: every finding concerned analysis or wording. The registry (`results/runs.jsonl`) is
unchanged. `analysis/make_tables.py` was extended and all tables, tests and figures were regenerated from the registry; the
counts quoted in the paper are printed in `results/tables/analysis_log.txt`.

## Major

1. **"Threshold moving was the only strategy that reliably changed sensitivity and balanced accuracy for LR" (conclusion,
   H3).** Correct, the claim was wrong and is removed. Changes:
   - `threshold_tests.csv` now holds, per learner, task and metric (sens, spec, bal_acc), the paired test of every strategy
     against no correction and of threshold moving against every correction (168 rows).
   - Table IV is now the operating point of all ten systems (sensitivity, specificity, balanced accuracy at four
     prevalences) with a star for paired p < 0.05 against no correction (`operating.tex`, replaces `threshold.tex`).
   - New results paragraph "Operating point of the corrections (not registered)": reweighting, ROS and SMOTE raise LR
     sensitivity in all 12 cells (p <= 0.012) and LR balanced accuracy at 1:5, 1:20, 1:50 (p = 0.0003-0.032, 0.863 to
     0.905-0.906 at 1:50), with a specificity loss significant in 7 of 12 cells; threshold moving raises balanced accuracy
     more than each correction at 1:20 and 1:50 (p < 0.01; p = 0.014-0.077 at 1:5; no difference at natural prevalence).
     For GB the corrections help in one cell only (SMOTE at 1:5).
   - Abstract and conclusion reworded accordingly; the advice is reduced to "try the threshold before resampling when only
     the operating point matters".

## Minor

2. **Abstract, blanket statement on the offset.** Now: "does not consistently bring the Brier score closer to no correction
   (11 of 24 cells, mostly GB) and increases the mean absolute calibration intercept in every cell". The ablation text
   gives 2 of 12 (LR), 9 of 12 (GB), |a| higher in 24 of 24 cells (p < 0.05 in 10), from `abl_prior_summary.csv`, which
   now carries these columns and tests.
3. **Signed calibration-in-the-large and signed slope.** Added. Table VI (`citl.tex`, replaces `abl_prior_citl.tex`) shows
   signed a with stars, |a| and |a| with the offset at all four prevalences. New paragraph "Signed calibration-in-the-large
   (not registered)": LR goes from underestimation (+0.33 to +0.76) to overestimation (-0.35 to -0.89) at 1:5-1:50,
   p <= 0.0002 in all 12 LR cells, toward zero at natural prevalence. The slope paragraph reports the signed slope test
   (p = 0.0002-0.027 at 1:5-1:50, absent at natural prevalence) next to the registered |b-1| (p >= 0.16). The unsupported
   sentence "distortion is visible in the slope" is gone. The registered |a| verdict for H2 is kept (higher in 5 of 12
   cells, none significant) and the one cell that refutes H2 under the registered rule is named. `deltas_all.csv` now has
   cal_citl, cal_slope, mean_pred, sens, spec and bal_acc. Limitations state that these analyses were not registered.
4. **AUPRC sd range.** Now 0.11-0.17 (both places).
5. **Sign of the offset effect.** Now: the offset shifts every logit by about -3 at 1:20 and therefore raises a by about 3;
   the raw corrected LR models overestimated by less than one logit (a = -0.38 to -0.78), so the offset overshoots.
6. **ceil vs round.** Method section now writes round() for ROS and SMOTE, and states that pi_eff is the realised prevalence
   (0.5 at r = 1), which is what the code uses. `method/DESIGN.md` updated.
7. **Median [IQR] for slopes; source of p-values.** Table I now gives slope b and |b-1| as median [IQR]; the mean of |b-1|
   is no longer quoted. This changed one statement: at 1:20 the median |b-1| is larger with a correction (0.10 vs
   0.22-0.28) while the mean is smaller, so the paper now draws no conclusion on |b-1|. The Statistics paragraph says the
   p-values come from `analysis/make_tables.py`; in addition `experiments/run_compare.sh` runs `rh compare` for every
   metric, task and reference arm (104 CSVs in `results/tables/compare/`), and the analysis script cross-checks them: 408
   paired p-values match with maximum absolute difference 1.1e-16 (mean_pred, 24 tests, is not a registered metric and
   is not in `rh compare`).
8. **Introduction and related work.** "Recent simulation and empirical studies"; Andersen et al. described as real clinical
   datasets with several model families; Carriero et al. as varying event fraction across algorithms. The stated addition
   is restricted to the threshold-moving arm and the prior-shift offset on a small bundled dataset. Guo et al. "use" the
   binned ECE. `literature/landscape.md` and the `gap` field of `research.yaml` were narrowed in the same way.
9. **Stars colliding in Table III.** Stars are now zero-width (`\rlap`) in all generated tables; checked in the rendered PDF.

## Found in the self-audit (not in the audit report)

- "AUROC differences exactly 0" for the offset was false for one run: GB + ROS at 1:5, seed 7, changes AUROC by 1.5e-4
  because the offset is applied to probabilities clipped to [1e-6, 1-1e-6], which ties saturated predictions. The method
  and ablation sections now say so.
- "Training positives ... on average" is exact (50, 12, 5 in every split); reworded.
- Mechanism sentences without an isolating run were removed or kept with "may" (C = 1 penalty sentence removed; GB
  overfitting of resampled positives and near-separability kept with "may" and "not tested").
- Extreme values: slopes range from 0.19 to 18.6 (largest for GB at 1:50, seed 8), a from -11.5 to 9.6, none at the +-20
  search bound; minimum AUROC 0.58 (GB + ROS/SMOTE, 1:50, seed 9). Stated in the setup, failure paragraph and RESULTS.md.
- The Brier-difference figure was removed to stay within 6 pages after the two new analyses; its content is in Table III
  (1:5-1:50, with tests) and the raw columns of Table V (all four prevalences). Two figures remain (slope, SMOTE sweep).
  Tables I and II no longer repeat the threshold rows, which equal no correction on probability metrics by construction.
- Figure captions now say "normal-approximation 95% interval".
