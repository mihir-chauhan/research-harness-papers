# Results (5 seeds, hp16)
Tables: results/tables/main.md, extra_sa_warm.md, extra_sa_log.md, abl_components.md, regime.md; paired tests: group analysis_paired and `rh compare`.
- H1 (K=1, AR > random and heuristic): NOT SUPPORTED. AR beats random; heuristic is higher than AR (p=0.094, n.s.).
- H2 (K=100, AR > SA): SUPPORTED for registered SA (binary penalty); vs post-hoc graded SA with heuristic init the difference is not detectable.
- H3 (K=1000, SA >= AR): REFUTED for registered SA; post-hoc graded SA matches (cold) or beats (heuristic init) AR.
- H4 (conditioning matters): SUPPORTED (uncond ~ random level).
- H5 (augmentation, data): augmentation NOT SUPPORTED; data fraction raises K=1 success, K=100 flat (mixed).
