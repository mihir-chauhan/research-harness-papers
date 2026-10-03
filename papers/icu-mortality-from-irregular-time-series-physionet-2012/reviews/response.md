# Response to audit
1. (major) Calibration paragraph: rewritten. GBDT under-predicts mean risk (per-seed range quoted from the registry); GRU-D and LR are close to the observed rate; the "not driven by global bias" conclusion is dropped.
2. Percent signs added to the Data paragraph in setup.tex.
3. GBDT now described as best on AUROC and AUPRC, tied with LR on Brier; Table II caption notes the tie with the paired p-value.
4. Per-regime sentence rephrased as a comparison among recurrent models only.
5. Conclusion: "similar-sized tuning grids" with cell counts (5, 9, 9).
6. Related work: uncited generalisation replaced by a statement about this study only.
7. Limitations: all GRUs chose the smallest hidden size (32) in the grid; smaller/more regularised models not explored (grid not extended, noted as a limitation).
8. Stray file `main` moved to results/raw/tune_select_stdout.json.
