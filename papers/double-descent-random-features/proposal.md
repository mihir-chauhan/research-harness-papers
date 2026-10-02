# Proposal

## Question
In random-ReLU-features ridge regression with n=200 training points, how do label noise and ridge strength change the height and position of the test-error peak near N/n=1, and does optimally tuned ridge remove it?

## Setup summary
Features phi(x)=relu(Wx/sqrt(d))/sqrt(N), nested widths N/n from 0.05 to 25 (N up to 5000). Tasks: synthetic single-index teacher (d=50) and sklearn digits (d=64, 10 one-hot targets), each with 4 label-noise levels (noise on train and validation labels only; test error against clean targets). 5 seeds.

## Systems
- MinNorm (reimplemented): ridgeless minimum-norm least squares (pseudo-inverse).
- FixedRidge (reimplemented): ridge with lambda=1e-2 at every width.
- GlobalRidge: a single lambda for all widths chosen on validation.
- TunedRidge (the "method"): lambda chosen per width on a held-out validation set of 200 points, grid of 15 values 1e-6..10.

## Metrics (per run = one full width sweep)
test_mse (at N=n, interpolation threshold), peak_mse (max over the threshold window 0.4<=N/n<=4; the window was added after smoke runs showed that for tuned ridge the global maximum is the under-fitted left edge N/n=0.05, not a peak), log10_peak_mse, peak_pos (N/n at the argmax in that window), best_mse (min), final_mse (N/n=25), bump_rel = hump height / best_mse, where hump = max over grid index p of min(m_p - min_{j<p} m_j, m_p - min_{j>p} m_j).

## Hypotheses (pre-registered tests)
- H1 (position): for MinNorm with noise>0, the argmax of the test error lies at N/n in [0.9,1.1] on every task (all seeds' median).  Refuted if the median peak_pos is outside on any noisy task.
- H2 (noise raises the peak): MinNorm peak_mse increases with label noise level on both datasets (mean over 5 seeds strictly increasing in noise level; paired Wilcoxon between lowest and highest level).
- H3 (ridge lowers the peak): for FixedRidge sweeps lambda in {0,1e-6,1e-4,1e-3,1e-2,1e-1,1}, mean peak_mse is non-increasing in lambda on each task; peak position is reported exploratorily (no direction predicted).
- H4 (tuned ridge removes the peak): TunedRidge mean bump_rel < 0.05 on every task, and bump_rel lower than MinNorm (paired comparison, rh compare, alpha 0.05). Refuted on a task if mean bump_rel >= 0.05.
- H5 (tuning protocol matters; exploratory): GlobalRidge and LOO-tuned / small-validation tuned ridge also remove the bump (same threshold).

## Refutation
H1: peak elsewhere. H2: non-monotone in noise. H3: any increase of mean peak_mse with lambda beyond 1 s.e. H4: bump_rel >=0.05.

## Ablations
abl_tuning: per-width tuning with leave-one-out CV on train only (no validation set); with a 50-point validation set. Sweep: sweep_lambda (H3).
