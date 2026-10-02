# Conformance report: numbers traced, constants declared

Scope: the paper's claims, hypotheses, verdicts, runs and figures are unchanged. No run was added, removed or re-logged.
Result at the end: `rh paper build` OK (7 pages), `rh lit verify` CITATIONS VERIFIED (12/12), `rh numbers` 687 checked / 0 untraced
(was 716 checked / 130 untraced), `rh check` READY (one pre-existing warning: verdict tier 0 < target 2).

## What you should know first
- No number in the text disagreed with the registry. Every prose figure was checked against tables regenerated from `results/runs.jsonl`; nothing had to be corrected.
- Most percentages in the old text "passed" the tracer only by coincidence (e.g. `-9.2%` matched the sd of an unrelated MAE, `10.6%` matched a multiseas MSE). They were derived by `experiments/analyze.py`, not recorded by `rh`, so all of them were replaced or removed, not only the 130 the tracer flagged.
- `rh compare` gives the ratio system/DLinear (`inv_ratio`), not the percent change (system - DLinear)/DLinear the paper used. Main-grid gaps are therefore now written as MSE ratios (win: ratio <= 0.95, the same 5% rule). Example: `-4.82%` is now `0.9518`.
- `rh compare` cannot compare one budget, dwell or noise value at a time, nor across groups (ablation vs main grid). For those cells the percent change was deleted and the two seed-mean MSEs it was computed from are given instead, each as `\rhval`.
- Still produced by `experiments/analyze.py` and not traceable by `rh`: the "seeds better" counts (0 to 3) and the win marks in Tables III, IV, VI, VII, and the two figures. They are verdicts of the registered rule, read from the per-run rows of the registry.
- The abstract's "less than 2%" for the no-decomposition check is now "less than the 5% registered for this check" (the H5 criterion); the 2% was a hand-derived bound.
- Table V: the "median of the per-seed changes" columns are replaced by the median over seeds of the MSE itself (a recorded statistic). The statement they support (nonlinear models degrade strongly on a typical seed, DLinear mildly) is unchanged.
- Table I: median run time was a median over all tasks, which `rh` does not record; it is now the median over the three seeds of the regime task (values differ slightly: e.g. PatchTST 47.9 s -> 54.1 s at 400 steps, 220.9 s -> 205.3 s at 2000 steps).

## Rule 1: numbers
### Setup facts declared with `rh const add` (28; none is a result)
- 400 -> `steps_main` (default training steps); 192 -> `horizon_long`; 336 -> `lookback`; 100 (checkpoint interval) -> `eval_every`
- 10^-5 -> `instnorm_eps`; 10^-4 -> `weight_decay`; 3*10^-3 -> `lr_dlinear_gru`; 10^-3 -> `lr_patchtst`; 128 -> `ff_width`; 0.1 -> `dropout`
- 8000 -> `series_len`; 1000 (seed offset) -> `gen_seed_offset`; 600, 1400 -> `trend_seg_min`, `trend_seg_max`; 168 -> `period_week`
- 500 -> `dwell_default`; 0.3 -> `noise_default`; 1.5 -> `noise_noisy`; 0.5 -> `ar1_rho`; 0.7, 0.4 -> `amp_week`, `amp_halfday`; 1.6, 0.6 -> `regime_period_scale_slow`, `regime_period_scale_fast`
- 14400, 8640, 2880 -> `etth1_rows`, `etth1_train_rows`, `etth1_valtest_rows`
- 5 (%) -> `win_threshold_pct`; 0.95 -> `win_ratio` (the same threshold written as a ratio)
- 96,192 in `H in {24,96,192}` and `H=96,192`: traced through `horizon_long`, no edit.

### `rh compare` run (reference DLinear)
- `--group main` for `mse_24`, `mse_96`, `mse_192`; `--group sweep_steps` for `mse_96` (used only for seas1, trend, multiseas, noisy, where the group holds the 2000-step runs alone; its regime/etth1 rows pool 1000 and 2000 steps and are not used).

### Generated tables (now written by `experiments/analyze.py` as `\rhval` macros only)
- Table III `rel.tex`: 36 percent changes (2.63, 2.38, 1.23, 11.11, 9.56, 10.87, 4.97, 4.82, 6.32, 6.82, 6.16, 6.79, ...) -> `\rhval{cmp/main/<system>/<task>/mse_<H>/inv_ratio:4}`.
- Table IV `budget.tex`: both "vs DL" columns deleted (9.8 and 51 others); MSE cells -> `\rhval` aggregates (`main/...` at 400 steps, `sweep_steps/<system>@steps=<n>/...` at 1000/2000).
- Tables VI `sw_dwell.tex`, `sw_dwell2000.tex` and VII `sw_noise.tex`: "vs DL (%)" columns deleted (23.8 and 29 others); MSE cells -> `\rhval`; seed counts moved to superscripts.
- Table V `abl_design_full.tex`: "mean (%)" and "median (%)" columns (66.5, 8.8, 218, 17665, 805, ...) and the bracketed change of the no-decomposition column deleted; added seed-median MSE columns (`.../mse_96/median`).
- Table I `size.tex`: 220.9 and the other cross-task medians -> `\rhval{.../regime/runtime_s/median:1}`; parameter counts -> `\rhval{main/<system>/regime/n_params_h96/mean}`.
- Table II `main.tex` (`rh table`): unchanged.

### Text
- abstract: 4.8% -> ratio `\rhval`; 10.6% -> the two means; "2.9% to 9.3%" -> the three means at 2000 steps, H=96; "less than 2%" -> "less than the 5% registered".
- method: one sentence added stating the win rule as a ratio (<= 0.95).
- setup: 108 runs -> `\rhval{count/sweep_steps/runs}` + `\rhval{count/sweep_dwell_2000/runs}`; 72, 36, 72 runs -> `\rhval{count/<group>/runs}`; Table I caption and sentence now say "regime task".
- results, budget paragraph: "at most 0.004" deleted, replaced by the three DLinear means; 0.322, 0.253, 0.446, 0.386, 0.291, 0.277, 0.438, 0.447 -> `\rhval`.
- results, H1: -1.11%, +11.11% -> ratio `\rhval` (main); +9.6%, -1.2%, -1.5%, +1.4%, +0.6%, +6.9% -> ratio `\rhval` (`cmp/main`, `cmp/sweep_steps`); "about one percent" deleted.
- results, H2: -4.97%, -4.82%, +1.41% -> ratio `\rhval`; -9.8%, -9.2%, -13.2%, -17.1%, -7.4%, -10.6%, -3.7%, -2.5%, -2.3%, -1.5%, -0.2%, -5.1%, -1.7%, -4.1%, +91.7%, -5.7%, -8.9%, -3.6%, +12.0% deleted, each replaced by the pair of seed-mean MSEs (`\rhval`).
- results, H3: -9.3%, -4.8%, -1.3%, -0.7%, -1.1%, +8.4%, -0.6%, -0.1%, -2.1% deleted, replaced by the MSE pairs (`\rhval`).
- results, H4: +6.32%, +6.82%, +6.16%, +6.79% -> ratio `\rhval`; +7.6%, +9.3%, +2.9%, +6.8%, -2.4%, -3.8% deleted, replaced by MSE pairs; 0.376, 0.410, 0.424, 0.512, 0.581 -> `\rhval`.
- results, failure list: 0.399, 0.400, 0.438, 1.587, 0.434 -> `\rhval`; +12.0%, +91.7% -> MSE pairs.
- results, captions: Table III now describes ratios; "-5.0 ... is -4.97 before rounding" deleted from the Table IV caption.
- ablations: -0.2%, +0.2%, +1.9%, +66.5%, +218%, 5.646, +8.8%, +134%, +805%, -5.6%, -1.9%, -3.6%, -5.4%, -1.2%, -3.5%, +10.1%, "less than 3%", -5.1%, -1.6% deleted or replaced by the seed-mean / seed-median MSEs (`\rhval`); captions of Tables V and VI rewritten to match.
- conclusion: 10.6% -> the two means.
- introduction, limitations, related, title, keywords: no edit (their numbers are declared constants or run settings).

## Rule 2: real runs
- All 289 registry rows carry the command that produced them (`rh run`); none was logged by hand. Nothing to replace.

## Rule 3: reproducible metrics
- `research.yaml`: `runtime_s` marked `nondeterministic: true` (wall-clock). No other metric is marked.
- Checked by running four logged commands again into /tmp (DLinear etth1 seed 0, DLinear trend seed 2, GRU regime seed 0, Seasonal naive seas1 seed 1): every MSE, MAE, validation MSE and parameter count was identical to the registry; only `runtime_s` differed. The data generator, initialisation, batch sampling and dropout are all seeded, so no result metric is unseeded. PatchTST was not rerun (code path seeded the same way).

## Rule 4: byline
- `paper/sections/author.tex` not edited; the platform's version is committed as it was found.

## Rule 5: length and wording
- 7 pages (was 6; the tables are narrower, the text slightly longer). No "state of the art" and no "novel" anywhere in the paper.

## Other files
- `experiments/analyze.py`: table writers emit `\rhval` keys; percent changes are still printed to the console and the CSVs for the notes in `results/RESULTS.md`, which is not part of the paper.
- `paper/main.tex`: `rh paper build` added the `\input{generated/values}` line.
- New: `paper/generated/values.tex`, `paper/number_trace.json`, `results/tables/compare_*.csv`.
