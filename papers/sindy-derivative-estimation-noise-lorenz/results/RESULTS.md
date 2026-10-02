# Results (tables: results/tables/rep_*.tex; tests: Welch from `rh compare`, p<0.05, uncorrected)
Main runs use method/tuned.json (revised tie rule: largest threshold among configurations with equal support rate and equal median error). The first-version runs
(method/tuned_v1.json, smallest threshold on a tie) are superseded in the registry; their rates are the underlined
cells of rep_thr_a/b.tex.
- H1 refuted (registered test: higher mean and p<0.05 against every baseline at every level >= 1%). Weak support rate
  1.00 / 1.00 / 0.65 / 0.10 at 1 / 2 / 5 / 10%. 1%: SG, spline, TV also 1.00 (no difference). 2%: baselines 0.80-0.90,
  p=0.042 vs FD and spline, 0.163 vs SG, 0.083 vs TV. 5%: baselines 0.00-0.40, significant vs FD, SG, spline, not TV
  (0.119). 10%: baselines 0.00, p=0.163. Weak is never below a baseline. With the first tie rule weak was 0.75 at
  0.5-2% vs 0.80-0.90 (rep_thr_a/b): the ordering below 5% follows the tie rule.
- H2 refuted (registered: refuted if any smoother is not lower than FD at some level >= 1%). At 5% SG 0.0772, spline
  0.0636, TV 0.0536 vs FD 0.0469 (higher; p=0.000, 0.004, 0.369). Lower than FD at 1, 2, 10%, significant only for
  spline and TV at 1%. Depends on the FD threshold at 5% (0.1; 0.1354 at 0.05, rep_thr_err_b), chosen by median error
  alone because every threshold scored 0.00 tuning support; 0.05 and 0.1 tied in median but give different models on
  3 of 5 tuning trajectories (rep_ties.tex; mean tuning error 0.0664 vs 0.0566). At equal thresholds at 5% (rep_thr_err_5)
  SG is above FD at all five thresholds, spline at four (not 0.05), TV below FD at all five; the TV difference at the
  tuned thresholds is not significant (0.369). Only SG, and spline for thresholds >= 0.1, are above FD regardless of threshold.
- H3 supported: all five systems 1.00 at 0% (first tie rule, threshold 0.05: FD and SG 0.95; 1.00 at any threshold >= 0.1).
- H4 partly supported (descriptive, 2%): rate 1.00 at widths 0.3, 0.6, 1.0; 0.60, 0.35, 0.15 at 1.5, 2.5, 4.0. The width
  matters, but the registered direction (too narrow loses the advantage) is not supported.
- H5 not supported (descriptive, support at 2%): SG 0.90 -> 0.85, spline 0.80 -> 0.85. Coefficient error is lower with
  the smoothed library in all four cells (2 and 5%).
- Coefficient error: weak has the lowest mean at every level; significant vs all four baselines only at 0% and 10%.
  Medians at 10%: weak 0.1094 vs 0.1224-0.1337.
- Resolution: at n=20 the smallest rate difference with p<0.05 is 0.20 (1.00 vs 0.80, p=0.042, uncorrected; would not
  survive a Bonferroni correction over the 4 comparisons at 2%); 0.25 between 0.65 and 0.40 is not significant (0.119).
- Exponent ablation (2%): support 1.00 for p = 2, 3, 4, 6; mean coefficient error 0.0039, 0.0035, 0.0033, 0.0031 (rep_p.tex).
- Threshold grid (test seeds, diagnostic): at 0-1% all systems 1.00 at threshold 0.4; at 5% the best cell of each
  baseline (FD 0.25, SG 0.25, spline 0.20, TV 0.40) is below weak 0.65; at 10% no cell exceeds 0.10.
