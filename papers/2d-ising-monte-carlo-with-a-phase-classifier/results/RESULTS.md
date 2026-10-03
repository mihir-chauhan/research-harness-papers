# Results (10 seeds, main group; analysis and sweep rows in results/runs.jsonl)
Primary numbers: see paper/main.pdf Tables II-VI (generated from the run registry).
- H1 supported: CNN and MLP single-size error at L=32 below PCA (paired Wilcoxon p = 0.004 / 0.002; rh compare paired t for CNN p = 2e-4). Confusion (read out at the trial boundary T', after the abscissa fix) has the lowest mean L=32 error (0.015) but is not distinguishable from the CNN (Wilcoxon p = 0.105) or the MLP (p = 0.375).
- H2 not supported: FSS collapse does not reduce the error (CNN: collapse error larger, p = 0.084; MLP: no difference, p = 1.0).
- H3 supported: raw LogReg acc_far = 0.51 (<0.6), Z2-fixed 0.72 (>0.6); Z2-fixed crossing still strongly biased.
- H4 supported for PCA (p = 0.002, CNN lower on all seeds); for confusion supported only via a failed collapse (p = 0.002); that collapse fails (grid boundary Tc = 2.6, nu = 2 on all seeds, also with windows 0.45 and 0.3). MLP and Binder reference are not distinguishable from the CNN.
- H5 mixed: MLP |nu-1| = 0.17 (< 0.25), CNN 0.70 (refuted).
- H6: window width (0.15-0.6) stays within a factor 1.9 for both. At fixed epochs 10 samples/chain multiplies the L=32 error by about 3.4 (MLP, CNN); with epochs scaled to a constant number of updates (sweep_nsamp_ep) the MLP ratio is 2.78 (still > 2, refuted for MLP) and the CNN ratio 1.00 (supported for CNN: an optimisation-budget effect).
- nu=1 fixed collapse vs free: paired Wilcoxon p = 0.023 (CNN), 0.125 (MLP), 0.078 (Binder), 0.002 (PCA).
Verdict (advisory): target not reached; CNN is not best on the primary metric (MLP lower by mean, not significant).
