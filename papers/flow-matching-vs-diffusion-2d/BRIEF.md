# Flow matching versus denoising diffusion on 2D toy distributions

## Question
With the same small MLP, data stream and training budget, does flow matching (straight conditional paths) give better few-step samples than denoising diffusion, and what does one rectified-flow reflow round add? Quality = sliced Wasserstein-1 (SW) and MMD against 10k held-out points, for 1..100 sampling steps.

## Hypotheses (tests in proposal.md)
H1 FM-Euler beats DDIM at K=4 (SW, each task). H2 The gap shrinks by K=100. H3 One reflow round lowers K=1 SW, no gain at K=100. H4 FM paths are straighter than DDIM paths; reflow straighter still.

## Method / systems (all reimplemented, same 4x128 SiLU MLP with Fourier time features, Adam 2e-3 cosine, 3000 it, batch 512, EMA)
DDPM epsilon-prediction (T=1000, linear betas) sampled with DDIM (eta=0) and ancestral/eta=1; conditional FM (x_t=(1-t)z+t x) with Euler and Heun; reflow-1 = FM model initialised from the teacher and retrained on (noise, ODE-endpoint) pairs from 100 Euler steps.

## Tasks / metrics
eight Gaussians, two moons, checkerboard; K in {1,2,4,8,16,32,64,100}; SW (256 fixed projections, 10k samples), MMD (4-bandwidth RBF, 3000 samples, biased), chord/arc straightness. A data-vs-heldout "real" row gives the metric noise floor. Seeds 0-4 (main), 0-2 (ablations).

## Ablations
DDIM with cosine schedule (is DDIM's few-step weakness a schedule artifact?); reflow teacher sampled with 4 instead of 100 steps; second reflow round. NFE-matched comparison FM-Heun vs FM-Euler (exploratory, not a registered hypothesis; reported in the results section and the exploratory-tests table).

## Out of scope
Images, guidance, distillation/consistency models, learned time grids, high-order DDIM solvers, other architectures; no hyper-parameter tuning beyond the shared defaults (none was tuned on the held-out set).
