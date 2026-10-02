# Protocol
- Tasks: synth_n{0,0.25,0.5,1}, digits_n{0,0.15,0.3,0.6} (suffix = label-noise sd on train/val labels). Test MSE vs clean targets.
- n=200 train, 200 validation, test 2000 (synthetic) / 1397 (digits). Seeds 0-4 (5): seed controls data draw, noise, split and random features.
- Width grid N/n: 0.05..25 (24 values), nested features.
- Groups: main (MinNorm, FixedRidge lam=1e-2, GlobalRidge, TunedRidge), abl_tuning (TunedRidge-LOO, TunedRidge-val50), sweep_lambda (FixedRidge, lam in {1e-6,1e-4,1e-3,1e-1,1,10}).
- Tuning budget: 15-value lambda grid per width (TunedRidge), validation 200 labelled noisy points; no tuning on test. No hyperparameter of other systems was tuned (FixedRidge lam fixed a priori).
- Hardware: CPU (shared laptop-class machine, 2 threads); each run 1-5 s.
- Thresholds for hypotheses: see proposal.md.
