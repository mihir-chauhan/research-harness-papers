# Response to the audit (fix round)

All numbers below are from `results/runs.jsonl` (ok, non-superseded rows) via `experiments/analyze.py`
(`results/tables/*.tex`, `results/analysis_stats.txt`) and `rh compare`.

## 1. Major: KRR grid truncated for SymFn-sum KRR — accepted, fixed by re-running
- `method/run.py`: every KRR system now uses gamma in 10^-7..10^2 (half decades, 19 values) and lambda in 10^-13..10^2
  (decades, 16 values), selected on validation MAE. A (gamma, lambda) pair is skipped when the Cholesky solve fails or LAPACK
  flags the matrix as ill-conditioned. The bounds were set from validation errors only (scratch scan of selected values, no test numbers).
  Each run logs `hp_gamma`, `hp_lambda`, `hp_gamma_at_edge`, `hp_lambda_at_edge`, `hp_n_skipped`.
- Code committed before the runs (commit 31a7341). Old KRR rows of main, sweep_ntrain and abl_sf were retired with `rh supersede`
  (kept in the registry); 45 KRR runs repeated (`experiments/run_fix.sh`). MLP rows kept: their code path is unchanged.
- New results: SymFn-sum KRR 0.889 +- 0.140 at n=500 (was 1.587), 2.65 / 1.49 / 0.71 at n=50 / 150 / 1500.
  It is now ahead of sorted-distance KRR at n=50, 150, 500 (Welch p=0.012, 0.032, 0.026) and behind at n=1500 (p=0.022).
- Rewritten: abstract, overview, H1-H4, where-it-fails, ablations, limitations, conclusion. H3 is now "supported, with caveats"
  (3 seeds, uncorrected, reverses at n=1500, grid dependent); the paper states that the first version reached the opposite
  verdict because of the grid. The angular-function claim is now "no resolved effect" (0.785 vs 0.889, p=0.19).
- New table "grid" (sweep_krrgrid: narrow 1.587, mid 0.907, wide 0.889 for SF-KRR; 1.096 / 1.095 / 1.095 for sorted KRR) and new
  table "hp" with the selected hyperparameters per system and size.
- What could not be achieved, and is disclosed instead: the selected gamma is interior in every wide-grid run except one
  (SF-KRR, n=50, seed 2), but the selected lambda of SymFn-sum KRR is the smallest numerically feasible value in 13 of 14 runs
  (sorted KRR 4 of 14). Smaller values give solves that LAPACK flags as ill-conditioned, so no grid brackets it in double
  precision. The paper says this in the ablation section and in limitation (v), and bounds the consequence two ways:
  mid -> wide changes the error from 0.907 to 0.889 (p=0.82), and linear ridge on the same descriptor, whose lambda is interior
  in 5/5 seeds, gives 0.805 (p=0.27 against RBF KRR). The new group abl_linear holds these runs.
- Side effect reported in the paper: with the flatter kernels the invariance defect of SF-KRR rises to 6.16e-5 (per-seed max
  8.34e-5, single configurations up to 4.2e-3), still below the registered 1e-4 but close to it.

## 2. Minor: limitations did not mention grid-edge selections — fixed
Limitation (v) now states that the grid was widened after the audit (so it is not pre-registered) and that lambda of SF-KRR
sits on the smallest feasible value in 13 of 14 runs.

## 3. Minor: "four minima per size", unlogged 10^7 claim — fixed
Setup now says "up to four ... one for N=5, two for N=6, four for N>=7". The 10^7 statement is removed. A logged sanity run
(`method/energy_tail.py`, group sanity) gives, for 4000 untruncated samples: 6.6% of perturbed configurations above 50,
maximum 5355; random configurations 0.1%, maximum 65.9. The same run logs the library sizes and the N=13 minimum (-44.327).

## 4. Minor: invariance defect wording — fixed
The main table has a new column with the largest per-seed defect. The text reports per-seed maxima, says "exactly 0" only for the
sum-pooled SF MLP and the sorted-distance MLP, gives 5.39e-7 for the atomwise MLP, and reports the per-configuration maximum for
SF-KRR (new metric `inv_defect_max`).

## 5. Minor: registered tests not reported — fixed
New table "tests": Welch p-values for H1 (four comparisons), H3, H4 (three descriptors) and raw-vs-mean-predictor at every n.
`rh compare` outputs with the raw systems as reference are saved as `results/tables/compare_main_energy_mae_ref_raw_{krr,mlp}.csv`.
The ablation table has a p column (Welch against the full model on the same seeds); the step table has p rows. The SF-MLP step
effect is now described as not resolved (p=0.264 and 0.056). `results/VERDICT.md` still prints "missing" for ablations because
`rh verdict` needs rows of the method inside the ablation group, which would mean re-logging identical runs; RESULTS.md says so.

## 6. Minor: runtime statement — fixed
Ranges now come from the registry: KRR/ridge 0.3-14.7 s, MLP 2.6-176.0 s, atomwise MLP 10.7-182.0 s.

## 7. Minor: "raw models learned essentially nothing up to n=1500" — fixed
Mean predictor run at n=50, 150, 1500 (3 seeds each, group sweep_ntrain) and added to the learning-curve table and figure.
The text now says raw KRR is not distinguishable from the mean predictor at any size (p >= 0.062) and raw MLP is worse (p <= 0.031).
Setup and limitation (viii) state that test sets differ between training sizes. Not changed: the data generator itself, because
drawing the test set first would invalidate every MLP run and exceed the compute budget.

## 8. Minor: Rupp et al. citation — fixed
Introduction and related work now say "sorted eigenvalue spectrum of the Coulomb matrix". One reference added with `rh lit cite`
(Barthelme et al., Gaussian process regression in the flat limit, arXiv:2201.01074; abstract read in the `rh lit search` result),
cited for the flat-limit behaviour that the SF-KRR selections show. `rh lit verify`: 12 cited, 12 verified.

## 9. Minor: Eq. (2) overflow, Fig. 1 legend, PROTOCOL.md — fixed
Eq. (2) is split over two lines; the Fig. 1 legend is below the axes; PROTOCOL.md is rewritten with all run groups, the
supersede history and the tuning grids. Tables use short system names so that none is shrunk below footnote size.

## Own audit, further changes
- H4: removed the claim that the SF gap "does not shrink"; it now says the MLP error stays several times the KRR error.
- Removed the mechanism wording for the angular-function result; mechanisms that have no isolating run use "may".
- `rh check`: READY. Remaining warnings: verdict tier 0 (the method is not the best system, as the paper says) and the number
  44.327, which is the logged `lowest_minimum_energy_n13` of the sanity run with its sign dropped by the checker.
