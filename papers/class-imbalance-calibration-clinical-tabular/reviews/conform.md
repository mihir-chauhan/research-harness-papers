# Conformance report

No claim, hypothesis verdict, experiment or run was changed. No new runs were logged. Final state: `rh paper build` BUILD OK (7 pages), `rh lit verify` CITATIONS VERIFIED (10/10), `rh numbers` 684 checked / 0 untraced, `rh check` READY.

## Rule 1: numbers (one line per change)

- 569 (setup.tex, limitations.tex): declared constant `n_patients` (rows in the dataset).
- 212 (setup.tex): declared constant `n_malignant`.
- 357 (setup.tex): declared constant `n_benign`.
- 107 (setup.tex, limitations.tex): declared constant `n_test_benign` (benign cases in every 30% held-out split).
- 10^{-6} (method.tex, four occurrences): declared constant `prob_clip_eps` (EPS in `method/run.py`).
- 10^6 (method.tex): declared constant `calib_fit_C` (C of the recalibration fit).
- 30, 100, 0.1, 0.5, 0.05, 0.01, 0.005, 95 (method.tex, setup.tex, ablations.tex): not on the untraced list, but the tracer had matched these setup facts to unrelated result statistics of equal value (e.g. "100 trees" to a mean specificity of 1.0). Declared as `n_features`, `gb_n_trees`, `gb_learning_rate`, `default_cutoff`, `alpha`, `h1_gain_threshold`, `h4_brier_tolerance`, `interval_level_pct`. The tracer still prefers the aggregate match for most of them (only 11 literals are attributed to constants).
- 0.0019 (generated/abl_prior_brier.tex) and the other 47 cells of that table: the table held Brier differences (cross-group: `abl_priorcorr` or `main` system minus `main` no correction) computed by `analysis/make_tables.py`; `rh compare` cannot produce a cross-group difference. Replaced the whole table by mean Brier scores, every cell a `\rhval{<group>/<system>/<task>/brier/mean}` macro, with a no-correction row per learner as the reference. Caption and the sentence introducing the table reworded to match. Generator block T6 in `analysis/make_tables.py` rewritten to emit the same macros (only that block was executed; the rest of the script was not rerun).
- -0.0080, -0.0073 (ablations.tex, GB + SMOTE at 1:5 gap with offset / raw): hand-typed differences replaced by the three `\rhval` means they come from (0.03161 with offset, 0.03961 no correction, 0.03228 raw).
- +0.0072, +0.0047 (ablations.tex, GB + SMOTE at 1:20 gap raw / with offset): replaced by the `\rhval` means (0.02890 raw, 0.02166 no correction, 0.02637 with offset).
- "change below 2x10^{-4}" (ablations.tex): deleted. It is a cross-group difference from the analysis script that neither `rh compare` nor `\rhval` can give; the tracer had matched it to a runtime standard deviation. The sentence still says one run changes because clipping ties saturated predictions.
- "p<0.05 in 10" (ablations.tex, offset raises |a|): deleted. These are cross-group paired p-values (`abl_priorcorr` versus `main`) that `rh compare` cannot produce. The claim that the offset raises mean |a| in all 24 cells stays and is readable from the calibration-in-the-large table.
- 0.085 (results.tex, smallest Brier p at 1:20/1:50): replaced by `\rhval{cmp/main/lr-+-reweight/bc_1to20/brier/paired_p}` (prints 0.08484).
- `paper/main.tex`: added `\input{generated/values}` so `\rhval` resolves.

## Rule 1: what was checked and left as typed

- Text versus registry: no disagreement found. Every difference and p-value in abstract.tex, results.tex and ablations.tex was compared with `rh compare --group main` output for auroc, auprc, brier, citl_abs, cal_citl, cal_slope, slope_dev, bal_acc, sens and spec, against the references LR + no correction, GB + no correction, LR + threshold and GB + threshold. All agree to the printed rounding. The cell tallies in the text (11 of 18, 11 of 12, 5 of 12, 7 of 12, 23 / 22 / 11 of 24, 2 and 9 of 12) were recounted and agree.
- Weakness of the trace, stated plainly: `rh numbers` matches by value. Most differences and p-values in the prose, and the cells of `generated/deltas.tex`, are reported as traced because some unrelated statistic has the same rounded value (for example the AUPRC difference +0.011 is matched to a Brier standard deviation). They are correct (previous bullet) but they are not `\rhval` macros. They were not converted because the `cmp/` keys hold one reference system per metric (the default, LR + no correction), so the GB-versus-GB and threshold-reference comparisons have no key, and ranges and tallies have no key at all.
- `generated/deltas.tex`, `citl.tex`, `operating.tex`, `main_1to20.tex`, `regimes.tex` come from `analysis/make_tables.py`, not from `rh table`. They were left unchanged; their differences and significance stars were checked against `rh compare` as above. The `|a|_off` column of `citl.tex` holds `abl_priorcorr` means.

## Rule 2: hand-logged rows

- None. All 722 registry rows carry a command in their provenance (`rh run`). The one failed row is the early sanity run (missing output directory); its rerun is the `ok` sanity row, and the paper uses neither.

## Rule 3: reproducible metrics

- `research.yaml`: added `runtime_s` under `metrics:` with `nondeterministic: true` (wall-clock; the only timing metric the runs log). No result metric is marked.
- Check: eight logged runs (LR and GB; ROS, SMOTE, reweight, no correction; prior-corrected and SMOTE-ratio variants; several tasks and seeds) were rerun from their logged commands into /tmp. Every metric except `runtime_s` was identical to the last digit. All randomness is seeded (`train_test_split`, the two `RandomState` objects and the GB `random_state`), so no result metric is unreproducible from its seed.

## Rule 4: byline

- `paper/sections/author.tex` not edited; the platform's rewrite is committed as found.

## Rule 5: length and wording

- 7 pages. No "state of the art" and no "novel" in the paper. No change needed.

## Side effects

- `rh const add` rewrote `research.yaml` in its own YAML layout (block lists, wrapped strings); the content of the existing fields is unchanged.
- `rh compare` was run with non-default references for the check above. It overwrites `results/tables/compare_main_<metric>.csv`, which feeds the `cmp/` keys, so the outputs were moved to /tmp and `compare_main_brier.csv` was restored to its committed content (default reference).
- New tracked files written by `rh`: `paper/generated/values.tex`, `paper/number_trace.json`.
