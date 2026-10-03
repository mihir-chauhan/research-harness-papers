# 2D Ising Monte Carlo with a phase classifier

## Seed
(see seed in the task statement) Generate 2D Ising spin configurations for L = 16, 24, 32 at 40 temperatures in [1.5, 3.5],
train classifiers far from Tc, read Tc from the 0.5 crossing, do a finite-size-scaling (FSS) collapse, compare with PCA and
learning by confusion, measure the Tc error against the Onsager value 2/ln(1+sqrt 2).

## Question
How accurately, and from which readout, can small supervised classifiers trained only deep inside the two phases, and
two reimplemented alternatives (PCA, learning by confusion), recover the critical temperature of the 2D Ising model
on L = 16, 24, 32 lattices, and does an FSS collapse of the classifier output remove the finite-size bias of the 0.5 crossing?

## Hypotheses (tests fixed before the main runs; paired over seeds, alpha = 0.05, `rh compare`)
- H1: nonlinear classifiers (MLP, CNN) trained far from Tc give a single-size crossing error at L=32 lower than PCA (susceptibility-like peak) at L=32.
- H2: the FSS collapse of the classifier output reduces the Tc error relative to the L=32 single-size crossing (paired Wilcoxon over seeds, CNN and MLP).
- H3: logistic regression on raw spins cannot learn the phase (held-out accuracy far from Tc below 0.6) because the Z2 symmetry makes a linear readout of s blind to order; fixing the gauge (flip each configuration to positive magnetisation) restores the accuracy above 0.6.
- H4: label-free methods (PCA, learning by confusion) do not beat the CNN on the FSS Tc error (paired test).
- H5: the collapse exponent nu from the CNN/MLP collapse is within 0.25 of the exact nu = 1 on average (mean |nu - 1| < 0.25).
- H6 (sensitivity): the CNN/MLP Tc error is not sensitive to the width of the excluded window around Tc (margin 0.15-0.6) or to the number of training samples per temperature (10-50) -- falsified if the error at any setting is more than twice the default.

## Method
Data: batched Swendsen-Wang cluster sampler in NumPy/SciPy (substituted for Wolff / checkerboard Metropolis, see decision; checkerboard Metropolis implemented and used to cross-check the sampler against Onsager's energy). 4 independent chains x 50 samples (gap 10 sweeps) = 200 per temperature; chains 0-2 train, chain 3 test. Seeds 0-9 (data and models are regenerated per seed).
Systems: LogReg (raw), LogReg (Z2-fixed), MLP, CNN (supervised, trained on T <= 1.97 vs T >= 2.57, 0.5 crossing of the held-out mean output),
PCA (peak of Var|PC1| and collapse of mean|PC1|), Confusion (MLP) (reimplemented learning by confusion, central peak of the W-shaped accuracy), Binder/chi (reference, non-ML physical estimator).
FSS: grid-search collapse of the output curves over (Tc, nu).
Metrics: tc_error (|Tc_est - Tc_exact|) per size and after collapse, nu_error, acc_far.
Ablations/sensitivity: training-window margin; training samples per temperature.
Out of scope: other universality classes, larger L, learned samplers, interpretability beyond the discussion.
