# Conformance to the new platform rules

No claim, hypothesis verdict or experiment changed. No new run was logged. One line per change.

## Rule 1: every number traced (`rh numbers`: 486 checked, 0 untraced; was 7 untraced)

### Setup facts declared as constants (`rh const add`, stored in `research.yaml: constants`)
- `5000` (method.tex, setup.tex): declared `max_features` (largest N = 25 n, columns of the nested feature matrix).
- `10^{-10}` (method.tex, limitations.tex): declared `pinv_rtol` (singular-value cutoff of the pseudo-inverse).
- `1797` (setup.tex): declared `digits_images` (size of sklearn digits).
- `1397` (setup.tex): declared `digits_test` (digits test-set size after the 200/200 split).
- Also declared, although the tracer already accepted them through a coincidental match with some result (e.g. `200` matched "min of bump_rel"): `n_train` 200, `n_val` 200, `n_test_synth` 2000, `d_synth` 50, `n_widths` 24, `lam_grid_size` 15, `hump_threshold` 0.05, `alpha` 0.05, `grid_step_threshold` 0.05, `window_lo` 0.4, `window_hi` 4, `val50_size` 50, `ratio_min` 0.05, `ratio_max` 25, the ten other grid ratios `ratio_0.1` ... `ratio_1.5`, and the five non-zero label-noise sds `noise_synth_0.25`, `noise_synth_0.5`, `noise_digits_0.15`, `noise_digits_0.3`, `noise_digits_0.6`. The tracer still prints the coincidental aggregate for these because it prefers aggregates over constants; they are setup facts, not results.

### Wall-clock numbers removed (not metrics, no registry key)
- `0.8` and `123` seconds, `31` CPU-minutes, `19` minutes wall-clock (setup.tex, Compute): sentence reworded without figures ("from about a second to about two minutes", "about half an hour of CPU time").
- `481` logged runs (setup.tex): now `\rhval{count/runs}`.
- `160`, `80`, `240` runs (setup.tex): now `\rhval{count/main/runs}`, `\rhval{count/abl_tuning/runs}`, `\rhval{count/sweep_lambda/runs}`.
- `40` runs (abstract.tex, results.tex H1): now `\rhval{count/main/minnorm/runs}`.

### p-values
- Wilcoxon `p=0.031` (abstract.tex, results.tex H2, limitations.tex, footer of Table II): removed everywhere. It was computed by `analysis/make_extra.py` with scipy; `rh compare` has no test across tasks, so no registry-backed value exists. The text now states what the registry shows (the peak is higher at the highest than at the lowest noise level in each of the 5 paired seeds on both datasets, so the registered test takes its smallest attainable p-value for 5 pairs). The H2 verdict is unchanged. The scipy value remains in `results/analysis.md` only.
- `p` range `0.06 to 0.21` (results.tex H4): now `\rhval{cmp/main/minnorm/synth_n1/bump_rel/paired_p:2}` and `\rhval{cmp/main/minnorm/synth_n0/bump_rel/paired_p:2}` (from `rh compare --metric bump_rel`, ref TunedRidge). Same printed values.
- Table IV columns `p_bump`, `p_peak`: were scipy values written by my script; now `\rhval{cmp/main/minnorm/<task>/{bump_rel,log10_peak_mse}/paired_p}`. Same printed values on all 8 rows. Caption says the value comes from `rh compare`.

### Hand-written tables (built by `analysis/make_extra.py`, not by `rh table`)
- Table II (`noise_minnorm.tex`): every cell is now an `\rhval` key (median `peak_pos`, mean and sd of `log10_peak_mse`, mean and median `peak_mse`, mean `best_mse`). Mean/median peak now print four significant digits (e.g. 268.7 instead of 269, 16340 instead of 1.63e+04).
- Table III (`sweep_peak.tex`): every cell is now an `\rhval` key (mean `peak_mse` per lambda). Four significant digits instead of three.
- Table IV (`h4.tex`): every cell is now an `\rhval` key. Printed values identical.
- `analysis/make_extra.py`: the three table writers emit keys instead of formatted numbers; the Wilcoxon footer is no longer written. `results/analysis.md` is byte-identical after the rerun; figures were not changed.

### Results typed in the prose, replaced by `\rhval`
- abstract.tex `0.033` (largest tuned hump): `\rhval{main/tunedridge/synth_n0.5/bump_rel/mean:3}`.
- results.tex H1 `10^{-30}` (training MSE at N=n): now "rounding-error level" with `\rhval{main/minnorm/synth_n0/train_mse_thresh/mean}`.
- results.tex H2 `269` and `0.161`: `\rhval{main/minnorm/synth_n0/peak_mse/mean}` (prints 268.7) and `.../best_mse/mean:3`.
- results.tex H3 medians `0.8, 1.25, 2.0`: three `\rhval{sweep_lambda/fixedridge-sweep@lam=.../peak_pos/median}` keys.
- results.tex H3 `0.0551` and `0.0554`: `\rhval{main/fixedridge/digits_n0.3/peak_mse/mean:4}` and `\rhval{sweep_lambda/fixedridge-sweep@lam=0.001/digits_n0.3/peak_mse/mean:4}`.
- results.tex H4 `0.0328`: `\rhval{main/tunedridge/synth_n0.5/bump_rel/mean:4}`.
- results.tex H4 `10^3 to 10^5` (MinNorm hump): the two extreme task means, `\rhval{main/minnorm/synth_n1/bump_rel/mean}` and `\rhval{main/minnorm/digits_n0.6/bump_rel/mean}`.
- results.tex H4 `0.326`, `0.608`, `0.021`: `final_mse/mean:3` keys of TunedRidge and MinNorm on synth_n1 and digits_n0.
- results.tex H4 `0.370`, `0.162`: `final_mse/mean:3` keys of FixedRidge and MinNorm on synth_n0.
- ablations.tex `0.0005` and `0.0000`: `bump_rel/mean:4` keys of GlobalRidge and TunedRidge on digits_n0.
- ablations.tex `0.0501`, `0.1555`, `0.0600`, sd `0.089`: `abl_tuning/.../bump_rel/{mean:4,std:3}` keys.
- ablations.tex `0.06` (largest tuned seed): `\rhval{main/tunedridge/digits_n0.15/bump_rel/max:2}`.
- ablations.tex `0.1--0.9 dex`, `2.3--2.7 dex on five of the eight tasks`, `-1.0 at N/n=0.05`: removed. These were read by hand from the per-width lambda curves in `results/raw/`, which are not registry metrics. The sentence now says the selected lambda moves little inside the window and considerably more across the full grid (Fig. 3), with the two logged values `\rhval{main/tunedridge/synth_n0/log10_lam_thresh/mean:1}` and `.../log10_lam_final/mean:1` as the example.

### Text that disagreed with the registry (registry wins)
- abstract.tex: the noise-free MinNorm peak was given as "a factor of 10^3 to 10^5" above the best error. The two noise-free tasks have mean humps of 1635 (synth_n0) and 20676 (digits_n0); 10^5 is only reached with label noise. The sentence now prints those two values with `\rhval`.
- results.tex H3: "lowest mean peak at 10^-3 for six tasks, with digits_n0.3 a tie". In the registry digits_n0.3 is lower at 10^-2 (0.0551) than at 10^-3 (0.0554), so 10^-3 is the minimum on five tasks, not six. Corrected to "five tasks, with digits_n0.3 essentially a tie". The H3 verdict does not depend on it.

## Rule 2: only real runs
- All 481 registry rows have a command behind them (`rh run`); none was logged by hand. Nothing to replace. `rh check` reports no hand-logged rows and no run-record problems.

## Rule 3: reproducible metrics
- `research.yaml: metrics` and the logged rows contain no wall-clock or throughput metric (run durations are in the provenance, not in the metrics), so no metric needed `nondeterministic: true`. No result metric was marked.
- All randomness is seeded from the run seed (`default_rng(10000 + seed)` for data, split and noise, `default_rng(20000 + seed)` for features). I re-executed five logged runs outside the registry (MinNorm synth_n1 seed 0 twice, MinNorm digits_n0.6 seed 3, TunedRidge synth_n0.5 seed 2, TunedRidge-LOO digits_n0.3 seed 1, GlobalRidge synth_n0 seed 4): every metric matched the registry exactly.
- Caveat, not hidden: this was checked on the machine that produced the runs, with 2 BLAS threads. The MinNorm metrics at N=n come from a nearly singular SVD (`peak_mse`, `log10_peak_mse`, `bump_rel`, `test_mse`, `peak_over_final`, and `train_mse_thresh`, which is rounding error of order 1e-30). They are deterministic given seed, BLAS build and thread count, but I have not shown they are identical to the last digit under a different BLAS or thread count.

## Rule 4: byline
- `paper/sections/author.tex` not edited; it is committed as the platform rewrote it.

## Rule 5: length and wording
- 6 pages. No "state of the art".
- introduction.tex: "We make no claim of theoretical novelty." reworded to "We do not claim a new theoretical result." (same meaning, avoids the word).

## Plumbing
- `paper/main.tex`: `rh paper build` added the `\input{generated/values}` line before `\begin{document}`.
- New files: `paper/generated/values.tex` (the `\rhval` macros), `paper/number_trace.json`.
- `paper/citations.json` refreshed by `rh lit verify`.

## Final gate output
- `rh paper build`: BUILD OK. `rh lit verify`: CITATIONS VERIFIED (12/12). `rh numbers`: 0 untraced. `rh check`: READY.
- `rh check` still prints the advisory warning it printed before this work (verdict tier 0 < target 2: TunedRidge is not the best system on synth_n0.5). The paper already says so; not changed.
