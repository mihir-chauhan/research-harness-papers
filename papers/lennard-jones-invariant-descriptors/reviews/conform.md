# Conformance report: numbers traced, constants declared

No claim, verdict or experiment of the paper was changed. `rh numbers` went from 26 untraced to 0; `rh check` prints READY.
One line per change. "seed range" = registry `min`--`max` over seeds, printed with `\rhval`.

## Rule 1: every number traced

### Flagged by `rh numbers` (26)
- `ablations.tex` 0.824 (p, mid vs wide grid; cross-group, `rh compare` cannot recompute): deleted; replaced by the seed ranges of the three grids via `\rhval`.
- `ablations.tex` 0.269 (p, linear ridge vs RBF KRR; cross-group): deleted; replaced by the two seed ranges via `\rhval`.
- `ablations.tex`, `abstract.tex` 0.190 (p, radial-only vs full KRR; cross-group): deleted; "overlapping seed ranges" with `\rhval` ranges in the ablation section.
- `ablations.tex` 4.610 (SymFn-sum MLP, hand subset of seeds 0--2 of the main runs; not a registry aggregate): replaced by the registry mean of the main group, `\rhval{main/symfn-sum-mlp/.../mean}` = 4.513 (5 seeds); text now says which seeds each side uses. **Registry wins.**
- `ablations.tex` 15.090 (raw MLP, hand subset of seeds 0--2): replaced by `\rhval{main/raw-coords-mlp/.../mean}` = 15.03 (5 seeds), with seed ranges. **Registry wins.**
- `ablations.tex` 3000 (twice), `setup.tex` 3000, `generated/steps.tex` 3000 (three times): declared, `rh const add mlp_steps 3000`.
- `method.tex` 128 (twice): declared, `rh const add mlp_width 128`.
- `generated/abl.tex` 0.190, 0.269, 0.763, 2.60e-7, 3.94e-4 (p column, cross-group): column deleted; table rebuilt from `\rhval` keys (n, mean, std, inv. defect).
- `generated/abl.tex` 4.610, 15.090, 0.597 (3-seed subsets of the main MLP runs): rows now show the main-group aggregates (5 seeds) via `\rhval`; caption says so. **Registry wins.**
- `generated/steps.tex` p rows: deleted; table rebuilt from `\rhval` keys, the 3000-step column is the main group (5 seeds; was a hand subset of seeds 0--2: 0.65 -> 0.6347, 4.61 -> 4.513), a "seeds" row gives n. **Registry wins.**
- `generated/tests.tex` 0.359, 0.977 and `results.tex` 0.359, 0.977 (per-size p-values): deleted (see next block).

### Same class of number, not flagged only because it matched an unrelated statistic by coincidence
- All other hand-computed p-values (`tests.tex`: 44 cells; text: 0.012, 0.032, 0.022, 0.311, 0.147, 0.125, 0.003, 0.006, 0.264, 0.056, 0.830 and the bounds `p<0.001`, `p>=0.062`, `p<=0.031`, `p<=0.034`, `p<=0.012`, `p<=0.009`) were "traced" to unrelated values (e.g. p=0.012 to a std of MAE per atom, p=0.032 to a std of runtime). `rh compare` recomputes Welch tests only within one group against one reference and pools over `n_train`, so per-size, other-pair and cross-group tests cannot be traced. Deleted all of them; the verdict sentences stay and now cite registry means and seed ranges.
- `generated/tests.tex`: replaced the 11x4 p-value table by the output of `rh compare --group main --metric energy_mae` (SymFn-sum KRR vs each of the 7 other systems, n=500): mean, delta, Welch p, all `\rhval{cmp/main/...}`.
- `abstract.tex`, `results.tex` p=0.014, 0.026 (n=500, SF-KRR vs sorted MLP / sorted KRR), H1 SF-KRR vs raw KRR, H4 SF-KRR vs SF-MLP: now `\rhval{cmp/main/.../welch_p}` (0.01427, 0.02647, 3.210e-9, 1.491e-10).
- `results.tex` "Bonferroni threshold of 0.025" (alpha/2 typed by hand): number deleted, sentence kept ("would not pass a Bonferroni correction for the two tests").
- `limitations.tex` "p-values of 0.012 and 0.032": numbers deleted ("rests on two such 3-seed tests").
- `setup.tex`: added a paragraph "Which statistics are printed" stating that only `rh compare` p-values are printed and that the other registered tests are in `results/analysis_stats.txt` (written by `experiments/analyze.py`).
- `setup.tex` 6.6% and 0.1% (energy-tail fractions, matched to a runtime and an MAE): now `\rhval{sanity/energy-tail-untruncated/.../perturbed_frac_above_cap/mean}` (0.066) and `.../random_frac_above_cap/mean` (0.001), printed as fractions; the two maxima also via `\rhval`.
- `setup.tex` 15.24 (lower bound of the test-energy std, matched to an MAE): both bounds now `\rhval` (`test_energy_std` min / max).
- `setup.tex` runtimes 0.3--14.7 s, 2.6--176.0 s, 10.7--182.0 s (hand min/max over groups, lower bounds matched to MAEs) and "about 23 minutes" (hand sum): lower bounds and the total deleted; the three maxima are `\rhval{.../runtime_s/max}` (14.73, 176.0, 182.0).
- `results.tex`, `abstract.tex`, `conclusion.tex`, `ablations.tex` rounded means matched to the wrong statistic (2.65, 1.21, 0.71, 0.45, 1.09, 0.89, 15.2, 2.88, 1.7, 0.65, 0.54, 4.81, 4.61, 4.39, 6.38, 0.140, 11.14, 11.80, 2.39, 3.93, 1.49, 2.07): replaced by the `\rhval` key of the intended aggregate (4 significant digits).
- `ablations.tex` "gamma <= 10^-3 in every SF-KRR run": now `\rhval{sweep_ntrain/symfn-sum-krr/lj_clusters/hp_gamma/max}`; "4x more steps": now "12000 steps".
- `generated/maintab.tex`, `generated/lcurve.tex` (written by `experiments/analyze.py`, values correct but several cells matched to unrelated statistics): rebuilt cell by cell from `\rhval` keys; same rows and columns.
- `experiments/analyze.py`: no longer writes `tests`, `abl`, `steps`, `lcurve`, `maintab` (it would overwrite the `\rhval` tables); `experiments/PROTOCOL.md` notes this.
- `paper/main.tex`: added `\input{generated/values}` (defines `\rhval`).
- `ablations.tex`: steps table wrapped in the `\resizebox` used by the other tables (it became wider than the column).
- Left as they are: `generated/grid.tex` and `generated/hp.tex` (written by `analyze.py`; means, stds and selected hyperparameters trace; the "k/n runs at a grid edge" counts are small integers that `rh numbers` does not check, and the text's "13 of 14", "4 of 14", "4 of 5" are the same counts).

### Constants declared (`rh const add`, 33; all setup facts read off `method/run.py`, `method/energy_tail.py`, `research.yaml`)
- mlp_steps 3000, mlp_width 128, mlp_batch 64, mlp_lr_low 0.001, mlp_lr_high 0.004, n_test 1000, n_val_min 50, energy_cap 50, tail_check_samples 4000, alpha 0.05.
- sf_cutoff_radius 4, sf_radial_shift_1..6 (0.9, 1.1, 1.4, 1.8, 2.3, 3.0), sf_angular_eta_low 0.3, sf_angular_eta_high 1.5.
- noise_std_min 0.02, noise_std_max 0.12, ball_radius_coef 0.62, ball_radius_offset 0.35, min_pair_distance 0.85, minima_random_starts 40.
- krr_gamma_min 1e-7, krr_gamma_max 100, krr_lambda_min 1e-13, krr_narrow_gamma_min 0.01, krr_narrow_lambda_min 1e-9, krr_narrow_lambda_max 0.1, krr_mid_gamma_min 1e-4, krr_mid_lambda_min 1e-11.
- Only mlp_steps and mlp_width were needed to clear the list; the others had passed by matching an unrelated statistic and are declared so that they are stated as what they are. None is a result.

## Rule 2: only real runs
- No row of `results/runs.jsonl` was logged by hand: all 218 run rows present at the start of this pass (219 now) have a `provenance.command`. Nothing to replace.

## Rule 3: reproducible metrics
- `research.yaml`: added `runtime_s: {higher_is_better: false, nondeterministic: true}` (the only wall-clock metric the runs log). No result metric is marked.
- Checked by re-running, to /tmp and without logging, the seed-0 command of every (group, system, config) in the registry and comparing every metric except `runtime_s` bit for bit: all 48 current rows are identical (KRR, ridge, MLP, atomwise, mean predictor, energy tail). All randomness is seeded (`default_rng(1000+seed)`, `default_rng(777+seed)`, `torch.manual_seed(seed)`); no unseeded result metric was found. This was checked on this machine only: the near-singular KRR solves may differ with another BLAS/LAPACK build (already limitation (v) of the paper).
- Not reproducible, and not hidden: the 12 superseded KRR configurations checked (first-version rows, commits `8fc63ed`) do not reproduce from their logged commands, because the default KRR grid in `method/run.py` was widened in the fix round. They are retired rows and the paper does not use them.
- One non-superseded row had the same problem: the smoke test `sanity / SymFn-sum KRR / seed 99` (`de99420bbb`, first code version; 3.18 logged, 1.48 when re-run). Retired it with `rh supersede` (control row `cea2eba268`) and re-ran the identical command with `rh run` (`fbe9827979`), which reproduces. The paper does not use this row. This is the only run added.

## Rule 4: byline
- `paper/sections/author.tex`: not edited (the platform's version is committed as found).

## Rule 5: length and wording
- 7 pages. No "state of the art", no "novel" in the paper; nothing to change.

## What a reader should know
- The verdicts on H1 (three of the four pairs), H3 (n=50, 150, 1500), H4 (other sizes and pairs) and all ablation comparisons still rest on Welch tests whose p-values the paper no longer prints, because the platform cannot recompute them; they remain in `results/analysis_stats.txt`. Every "disjoint" / "overlapping" seed-range statement was checked against the registry keys before it was written.
- Ablation comparisons for the two MLP variants are now 3 seeds (variant) against 5 seeds (full model) instead of the same 3 seeds; the conclusions (no resolved effect of the angular terms; augmentation helps but stays far above invariant descriptors; sorted MLP not converged at 3000 steps) are unchanged.

## Final state
- `rh paper build`: BUILD OK (7 pages). `rh lit verify`: CITATIONS VERIFIED. `rh numbers`: ALL NUMBERS TRACED. `rh check`: READY (one warning kept: verdict tier 0 < target 2, the method is not the best system; the paper says so).
