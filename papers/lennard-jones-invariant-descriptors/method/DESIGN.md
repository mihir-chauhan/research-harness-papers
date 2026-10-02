# Design
method/run.py: data generation (LJ energy, minima library), descriptors, KRR, linear ridge, MLP, metrics.
method/energy_tail.py: sanity check of the untruncated energy distribution and of the minima library.
- raw: padded (13x3) coordinates + N. sorted: all 78 inverse pair distances sorted descending (padding 0) + N.
- SF: per atom 13 radial G2 (6 shells x eta {2,6} + coordination number) and 8 angular G4 (eta{0.3,1.5} x zeta{1,4} x lambda{+-1}), cosine cutoff Rc=4; summed over atoms, + N.
- KRR: standardised features, RBF exp(-g|a-b|^2/d), chosen on validation MAE. Grid "wide" (all reported results):
  g in 10^-7..10^2 in half decades, lambda in 10^-13..10^2 in decades. A (g, lambda) pair is skipped when the Cholesky
  solve raises or LAPACK warns that the matrix is ill-conditioned. Grids "mid" and "narrow" (`--krr_grid`) exist only
  for the grid-sensitivity study; "narrow" is the 5x5 grid of the first version (g in {.01,.03,.1,.3,1}, lambda in {1e-9..1e-1}).
  The run logs hp_gamma, hp_lambda, whether gamma is a grid edge, whether lambda is the smallest feasible value, and the number of skipped pairs.
- Linear ridge (`sf_lin`, `sfrad_lin`, `sorted_lin`): the same solver with kernel z.z'/d; only lambda is selected.
- MLP: 2x128 SiLU, Adam, batch 64, 3000 steps cosine schedule, lr in {1e-3,4e-3} chosen on validation. Atomwise: same net applied per atom on SF vector, outputs summed. Aug variant: random rotation+permutation of each minibatch.
