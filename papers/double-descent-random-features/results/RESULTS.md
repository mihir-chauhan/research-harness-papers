# Results (5 seeds, n=200; numbers in results/analysis.md, results/tables/*)
- H1 SUPPORTED: MinNorm peak_pos = 1.0 in all 40 runs (8 tasks x 5 seeds).
- H2 SUPPORTED (weakly powered): mean peak_mse rises monotonically with noise on both datasets; one-sided paired Wilcoxon highest vs lowest p=0.031 (the smallest attainable with 5 seeds). But the peak is huge even at zero noise (mean 269 synth, 458 digits), so noise raises, not creates, the peak.
- H3 REFUTED as registered: mean window peak_mse is not non-increasing in lambda on any task; it falls from lambda=0 to 1e-3 (all tasks) and rises again for lambda>=1e-2 because the whole curve is over-regularised (high plateau, no peak). The monotone-to-1e-3 statement is post hoc.
- H4 PARTLY SUPPORTED: TunedRidge mean bump_rel < 0.05 on all 8 tasks (max 0.0328), but 3 tasks have an individual seed >= 0.05; the registered paired comparison with MinNorm on bump_rel is not significant (p 0.06-0.21) because MinNorm bump has a huge variance; the unregistered log10 peak comparison has p<=0.0036 everywhere.
- H5 MIXED: GlobalRidge < 0.05 everywhere; LOO fails on synth_n1 (0.0600); val50 fails on synth_n0.25 (0.0501) and synth_n1 (0.155).
