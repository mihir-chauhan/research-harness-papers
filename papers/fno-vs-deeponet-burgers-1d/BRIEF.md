# Operator learning on 1D viscous Burgers at small scale: FNO vs DeepONet vs MLP/CNN, with zero-shot finer-grid evaluation

## Question
With 400 training pairs of (u(x,0), u(x,1)) at 128 grid points (nu=0.01, periodic), how do a small FNO, DeepONet, MLP and CNN compare in test relative L2, and how does each behave when applied zero-shot to 256- and 512-point grids?

## Hypotheses (tests fixed in proposal.md)
H1 FNO < all baselines in rel_l2 at 128 pts. H2 FNO zero-shot ratio (256-pt / 128-pt error) < 1.5 while the CNN's > 1.5. H3 FNO saturates in Fourier modes (8->16 <10% change, 4 modes worse). H4 FNO beats DeepONet at n_train in {100,200,400}.

## Method
Reimplemented PyTorch models: FNO1d (4 layers, width 32, 16 modes, grid channel), DeepONet (branch MLP on 128 sensors, trunk MLP on x, p=64), MLP (128-512-512-128), CNN (6 circular conv layers, k=9, 32 ch). Loss: per-sample relative L2; Adam + one-cycle; 100 epochs, batch 20; checkpoint by validation error. Data: random Fourier-series ICs (FNO Burgers measure), ETDRK4 solver at 512 pts subsampled to 128/256/512; 400/100/100 train/val/test; 5 seeds (seed changes data and init).
Zero-shot rules: models that accept any grid (FNO, CNN) are applied natively; MLP and DeepONet's branch take the 128 training-grid sensors by stride-subsampling the finer input; DeepONet trunk queries finer points natively; MLP's 128-point output is Fourier-interpolated. A "resamp" variant (subsample input to 128, Fourier-interpolate output) is reported for all.

## Metrics
Relative L2 (mean over test samples) at 128, 256, 512; parameter count; training time.

## Ablations / sensitivity
FNO modes {4,8,16,32}; n_train {100,200,400} for FNO and DeepONet; epochs 500 and 2000 for the cheap baselines DeepONet and MLP (budget fairness check; the CNN is too slow for this within the per-run limit); FNO without grid channel.

## Decisions
Same 100-epoch budget for all systems; learning rate per system from {3e-4,1e-3,3e-3,1e-2} on tuning seed 100 (validation error); no tuning on test. The grid started as {3e-4,1e-3,3e-3} and was extended to 1e-2 because the FNO's best rate sat at the upper edge; FNO, DeepONet and MLP were run at 1e-2 before the main runs, the CNN's 1e-2 point was run in the revision (it diverges, selection unchanged). Selected: FNO 1e-2, DeepONet 3e-3, CNN 3e-3, MLP 1e-3.

## Out of scope
Physics-informed losses, rollout, other PDEs, U-Net/CNO/transformer baselines, GPU scale, claims of novelty.
