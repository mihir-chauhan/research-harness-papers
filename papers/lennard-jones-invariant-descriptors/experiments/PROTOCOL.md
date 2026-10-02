# Protocol

Task `lj_clusters`: energies of 5-13 atom Lennard-Jones clusters (reduced units). Entry point `method/run.py`;
drivers `experiments/run_all.sh` (first round), `experiments/run_extra.sh` (mean predictor, step sweep) and
`experiments/run_fix.sh` (fix round after the audit). Analysis: `experiments/analyze.py`.

## Data, splits, seeds
- Per seed s one generator (`default_rng(1000+s)`) draws, in this order, n training, max(50, n//4) validation and 1000 test
  configurations. All systems of a seed see the same data. For a given seed the training sets are nested across n,
  but the validation and test sets differ between n.
- Half of each set: library minimum + random rotation + Gaussian noise (sigma ~ U[0.02, 0.12]); half: random points in a
  ball (pair distance >= 0.85). Resampled until E <= 50. Random atom order.
- Minima library (`method/minima.npz`): 1 minimum for N=5, 2 for N=6, 4 for each N=7..13; shared by train and test.
- Test transforms (generator `777+s`): rotation, permutation, both.

## Run groups (registry `results/runs.jsonl`, ok and not superseded)
| group | systems | n_train | seeds |
|---|---|---|---|
| main | Mean predictor; Raw/Sorted/SymFn-sum x KRR/MLP; SymFn atomwise MLP (8 systems) | 500 | 0-4 |
| sweep_ntrain | the same 8 systems | 50, 150, 1500 | 0-2 |
| abl_sf | SymFn-sum KRR radial-only (seeds 0-4); SymFn-sum MLP radial-only (seeds 0-2) | 500 | see left |
| abl_aug | Raw coords MLP + rot/perm augmentation | 500 | 0-2 |
| abl_linear | linear ridge on SymFn-sum, SymFn-sum radial-only, sorted distances | 500 | 0-4 |
| sweep_krrgrid | SymFn-sum KRR and Sorted dist KRR with the narrow and the mid KRR grid | 500 | 0-4 |
| sweep_steps | Sorted dist MLP, SymFn-sum MLP with 1000 and 12000 Adam steps | 500 | 0-2 |
| sanity | smoke test; untruncated-energy tail and minima-library check (`method/energy_tail.py`) | - | - |

## Tuning (validation MAE only; the test set is never used for selection)
- KRR, every descriptor: gamma in 10^-7 .. 10^2 (half decades, 19 values), lambda in 10^-13 .. 10^2 (decades, 16 values).
  A pair is skipped if the Cholesky solve fails or LAPACK flags it as ill-conditioned. Linear ridge: the same lambda values.
- MLP / atomwise MLP: lr in {1e-3, 4e-3}; 3000 Adam steps, batch 64, cosine schedule; 2x128 SiLU. Not tuned per system.
- History: the first round used a 5x5 KRR grid (gamma 0.01-1, lambda 1e-9-1e-1). An audit showed it clipped SymFn-sum KRR
  at its smallest gamma. All KRR rows of main, sweep_ntrain and abl_sf were re-run with the wide grid and the old rows
  marked superseded (`rh supersede`); they stay in `results/runs.jsonl` and their raw files in `results/raw/`.
  MLP rows were kept: the MLP code path is unchanged. The narrow grid survives only as `--krr_grid narrow` in sweep_krrgrid.

## Metrics
energy_mae (primary), energy_mae_per_atom, mae_perturbed, mae_random, mae_rotated, mae_permuted, mae_rot_perm,
inv_defect (test mean of |E(gx)-E(x)|), inv_defect_max (largest single-configuration value; KRR re-runs only),
selected hyperparameters (hp_*), runtime_s.

## Tests
Two-sided Welch t-test over seeds (`rh compare`, `experiments/analyze.py`), alpha 0.05, no multiplicity correction.

## Hardware
Shared CPU machine, 2 threads, at most two runs at a time, `nice -n 10`. Runtimes in `results/analysis_stats.txt`.
