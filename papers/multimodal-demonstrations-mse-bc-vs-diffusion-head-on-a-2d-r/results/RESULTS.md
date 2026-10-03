# Results
Numbers: results/tables/*.md and paper/sections/{results,ablations}.tex.
H1 supported (bimodal50, jitter 0.01: MSE 0.754 vs GMM 1.0, DDPM 0.999). H2 supported (no DDPM-GMM difference; ceiling). H3 supported for GMM/DDPM; MSE collapses to majority mode on bimodal80. H4 supported for MSE (0.0 at jitter 0 to 0.977 at 0.1; GMM flat, DDPM ~flat). H5 partly: 1 step fails, 5/10 steps not distinguishable from 20. Extra: DDPM weaker than GMM at chunk K=8.
