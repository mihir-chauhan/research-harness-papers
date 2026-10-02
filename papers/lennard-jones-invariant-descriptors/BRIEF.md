# Brief: descriptors for a toy ML potential on LJ clusters
Seed: predict energies of 5-13 atom Lennard-Jones clusters (perturbed minima + random configs) from raw coordinates, sorted pair distances, or sum-pooled symmetry functions; compare KRR and small MLP on energy error, data efficiency and rotation/permutation behaviour.

## Decisions (no human available)
- Data: reduced units (eps=sigma=1). Fixed library of up to 4 lowest distinct minima per N (L-BFGS, 40 random starts; 1 minimum found for N=5, 2 for N=6, 4 for N>=7; N=13 gives -44.327, matching the known value). Half of each set = minima + Gaussian noise (sigma in U[0.02,0.12]) with random rotation; half = random ball configurations with pair distance >= 0.85. Truncated sampling E <= 50 (smoke test showed unbounded energies otherwise). Random atom order.
- Splits: per seed, n_train (50..1500), validation max(50, n/4) used only for hyperparameter selection, 1000 test. Same data for all systems per seed. Minima library is shared by train and test (limitation).
- Test-time transforms: random rotation, random permutation, both.
- Method (pre-registered "ours"): SymFn-sum KRR. Others reimplemented baselines.
## Question
Does invariance in the descriptor matter more than the regressor, and how do descriptors differ in data efficiency?
## Hypotheses (tests in proposal.md / research.yaml)
H1 invariant > raw at n=500; H2 raw degrades >=2x under rot/perm, invariants unchanged; H3 SF-KRR beats sorted-KRR at n=50,150; H4 KRR beats MLP at n<=150.
## Systems
{raw, sorted inverse distance, SF-sum} x {KRR (RBF), MLP 2x128 SiLU}, plus BP-style atomwise MLP.
## Metrics
Test energy MAE (eps), MAE per atom, MAE on rotated+permuted test, invariance defect.
## Ablations
Radial-only SFs (KRR, MLP); raw MLP with on-the-fly rotation/permutation augmentation; training size sweep.
Added in the fix round: linear ridge instead of the RBF kernel; KRR hyperparameter-grid sensitivity (narrow / mid / wide); MLP step count.
## Out of scope
Forces, MD, real chemistry, equivariant networks, multiple elements.

## Decisions of the fix round (after the audit)
- KRR grid: the first 5x5 grid (gamma 0.01-1, lambda 1e-9-1e-1) clipped SymFn-sum KRR at its smallest gamma. New grid for every
  KRR system: gamma 10^-7..10^2 in half decades, lambda 10^-13..10^2 in decades, validation MAE; ill-conditioned solves skipped.
  Bounds were set from validation errors only. All KRR runs were repeated; the old rows are superseded, not deleted.
- The selected lambda of SymFn-sum KRR still sits on the smallest numerically feasible value; this cannot be bracketed in double
  precision and is reported in the paper together with a grid-sensitivity table and a linear-ridge control (interior lambda).
- H3 changed from "not supported" to "supported with caveats" as a consequence; the paper says so and reports both grids.
- Mean predictor run at every training size; untruncated-energy tail and minima-library sizes logged by a sanity run.
- MLP runs were not repeated (their code path is unchanged). Test sets differ between training sizes (stated as a limitation).
