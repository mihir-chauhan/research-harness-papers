# Results (mix_overlap unless stated; 5 seeds; paired t-tests as registered in proposal.md)
- H1 supported: class_acc CFG w=3 0.999 vs unguided 0.926, p=5.6e-8 (paper Table III/I). Real samples score 0.915, so accuracy above this is not fidelity.
- H2 supported: mode_tv 0.017 -> 0.129 (p=3.2e-6); std_ratio 0.917 -> 0.800 (p=1.3e-4). Caveat: std_ratio is non-monotone in w (min 0.748 at w=1, 1.083 at w=8).
- H3 supported for the registered comparison (CFG w=3 vs tau=0.5, class_acc 0.999 vs 0.993, p=3.8e-6) but the spreads differ (0.800 vs 0.527); exploratory matched-spread view favours CFG on accuracy at w<=1.
- H4 refuted: mode_tv increase w=0->3 is the same on mix_sep and mix_overlap (diff -0.0004, Welch p=0.935).
- H5 supported (borderline, uncorrected): off_support w=8 0.055 vs 0.007, p=0.020.
- Ablations: label dropout has little effect on mode loss; guidance only in t/T in [0,0.5] keeps coverage 1.000 and acc 0.999; only [0.5,1] gives acc 0.936. Per-mode: minor mode keeps 0.63 (w=3), 0.34 (w=8), 0.44 (tau=0.5) of its mass.
- rh verdict "TARGET REACHED" is advisory and not meaningful here: CFG is not claimed to beat baselines on every metric.
- 20 registry rows with status failed come from a shell quoting bug launching the per-mode runs; rerun correctly.
Tables: results/tables/*.tex (analysis/analyze.py); runs: results/runs.jsonl.
