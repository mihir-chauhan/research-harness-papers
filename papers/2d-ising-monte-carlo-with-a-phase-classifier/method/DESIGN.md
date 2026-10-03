# Design
- `sampler.py`: batched Swendsen-Wang sweeps (bond activation p = 1-exp(-2/T) on equal-spin neighbours, connected components via scipy.sparse.csgraph over the whole batch, independent 50% flip per cluster); checkerboard Metropolis (cross-check); Onsager energy per site.
  Data: per (seed, L), 4 chains x 40 T, each a separate chain from a random start, 100 thermalisation sweeps, 50 samples at a gap of 10 sweeps.
- `estimators.py`: first downward 0.5 crossing with linear interpolation (grid edge if none); parabola-refined peak; FSS collapse grid search (Tc 2.0-2.6 step 0.005, nu 0.5-2.0 step 0.025), cost = mean across-L variance of interpolated curves on 30 common x points, normalised by total variance.
- `run.py`: one entrypoint, `--system` in {LogReg (raw), LogReg (Z2-fixed), MLP, CNN, PCA, Confusion (MLP), Binder/chi (reference), sampler_check}.
  Supervised: windows T<=2.27-margin (label 1) and T>=2.27+margin (label 0), class-weighted BCE, Adam lr 1e-3, wd 1e-4, 20 epochs, batch 128; MLP 64 ReLU hidden; CNN 2x(3x3 circular conv, 8 ch, ReLU) -> global mean -> linear; LogReg = single linear unit (Z2-fixed: each configuration multiplied by sign of its magnetisation).
  Curves are the mean output over held-out chain 3 at every T.
  PCA: PC1 of covariance of training chains (all T pooled); Tc = peak of Var|z1| (searched in [1.9,3.1]); collapse curve mean|z1|/max.
  Confusion: trial boundaries at midpoints between grid points in [1.7,3.3]; MLP (32 hidden, 8 epochs) trained on all training chains with labels T<trial; Tc = peak of held-out accuracy in [1.9,3.1]; collapse curve = accuracy.
  Reference: connected susceptibility of |m| (all four chains) peak; Binder U4 collapse.
