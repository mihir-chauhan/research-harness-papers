# Results (verdicts use the tests registered in proposal.md)

Tables: `results/tables/main_fmt.md` (main group), `abl_sam_fmt.md`, `compare_main_test_acc.csv` (`rh compare`), `rho_sweep.md`, `wd_sweep.md`, `corr.md`.

**H1 (SAM > SGD and > SGD+WD on noisy digits): supported against SGD, mixed against SGD+WD.**
- vs SGD: 0.938 vs 0.799 (digits_n0.2) and 0.901 vs 0.625 (digits_n0.4); paired and Welch p < 1e-4.
- vs SGD+WD at 20% noise: margin 0.0078, paired p 0.049, Welch p 0.294 -> inconclusive (one of five seeds negative).
- vs SGD+WD at 40% noise: margin 0.027, paired p 0.025, Welch p 0.0073 -> supported only without multiple-comparison correction; the Holm-adjusted paired p over the 8 paired tests is 0.101, and one of five seeds is negative.
- spirals_n0.2: no effect (SAM 0.912, SGD 0.919, SGD+WD 0.914; paired p 0.320 and 0.606).

**H2 (interior optimum in rho; larger/wider useful range under noise): partly supported.**
- digits_n0.0: best 0.974 at rho 0.2, 0.960-0.974 over rho 0.02-0.5, collapse (0.136) at 1.0; gain over SGD under two seed SDs.
- noisy digits: monotone rise to rho 0.5 (0.938, 0.901), collapse at 1.0 (0.103, 0.118); best value larger than without noise, but the range is not wider (rho 0.2 gives 0.862, 0.698), and no value between 0.2 and 1.0 other than 0.5 was tested.
- spirals: monotone decreasing from rho 0.02 (0.921) to chance at rho >= 0.5 -> refuted on this task.

**H3 (sharpness positively rank-correlated with the gap): not supported.**
- pooled Spearman over 260 runs 0.07-0.24 over the two sharpness measures and two gaps; within-task signs differ (spirals -0.72 / -0.34 with gap_acc; digits_n0.0 adversarial vs loss gap -0.65).
- on noisy digits adversarial sharpness ranks SGD flattest although it has the largest gap; random-direction sharpness ranks SAM flattest.

**Ablations.** Random-direction SAM matches SGD (0.800, 0.623 on noisy digits). SAM+WD with separately selected rho and lambda collapses on noisy digits (0.223 +/- 0.290, 0.099) and is comparable to SAM without noise (0.972 vs 0.970).

Known protocol caveats: epoch-matched budget (SAM uses 2x gradient evaluations); digits tuning seeds re-split the same image pool as the evaluation seeds.
