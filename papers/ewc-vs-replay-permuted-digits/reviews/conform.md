# Conformance pass: numbers traced, constants declared

No claim, hypothesis verdict or experiment changed. No run was added: the registry holds only `rh run` rows (561
with a command) and two `rh supersede` control rows; no row was logged by hand, so rule 2 needed no action.
`rh numbers` before: 664 checked, 23 untraced. After: 631 checked, 0 untraced.

## Untraced numbers (the 23 entries of `rh numbers`)
- `generated/paired_main.tex` 0.123, 0.107, 0.095, 10^-5, 10^-8, 0.650, 10^-6, 0.155, 0.258 (9 entries): table removed. It was written by my own script (`experiments/paired_stats.py`), not by `rh`. Table III is now built from `\rhval{cmp/main/...}` (`rh compare`, reference ER M=100) and keeps the 8 of the 12 old rows that involve ER M=100.
- `results.tex` 1.2x10^-4 (H1 p-value): replaced with `\rhval{cmp/main/ewc/perm_dil/average_accuracy/paired_p}`.
- `results.tex` 0.107 (joint above ER M=100 on perm_dil, twice): replaced with `\rhval{cmp/main/joint-training/perm_dil/average_accuracy/delta:3}`; it now prints as ER minus joint, -0.107.
- `results.tex` 0.650 (ER M=100 gain over EWC, split_cil): replaced with `\rhval{cmp/main/ewc/split_cil/average_accuracy/delta:3}`.
- `results.tex` 0.155 (ER M=100 vs EWC, split_til, p): replaced with `\rhval{cmp/main/ewc/split_til/average_accuracy/paired_p}`.
- `results.tex` 0.258 (ER M=100 vs joint, split_til, p, twice): replaced with `\rhval{cmp/main/joint-training/split_til/average_accuracy/paired_p}`.
- `setup.tex`, `limitations.tex` 1797 (three places): declared constant `n_images`.
- `setup.tex` 1078: declared constant `n_train_per_permuted_task`; checked against the data split (1078 for every seed), "about" dropped.
- `setup.tex` 215: declared constant `n_train_per_split_task`; checked against the data split (211 to 219 per task, "about 215" kept).
- `setup.tex`, `limitations.tex` 225 (sweep run count): replaced with `\rhval{count/sweep_buffer/runs}` and `\rhval{count/sweep_lambda/runs}` (120 and 105); the hand-typed sum is gone.

## Derived numbers that `rh numbers` passed only by coincidence
The tracer accepted these because some unrelated statistic had the same digits (for example the difference 0.152 matched the minimum backward transfer of a sweep row). They were still hand-typed derived numbers, so they were handled the same way.
- 0.152 (H1 difference), 0.682 (ER gain over fine-tuning, split_cil), 0.061 and 0.006 (joint vs ER M=100): replaced with `\rhval{cmp/main/.../delta:3}`.
- "both p<10^-4" (split_cil) and "both p<0.01" (H5): replaced with the four `\rhval{cmp/main/.../paired_p}` values.
- 0.050 (ER M=100 vs fine-tuning, split_til, p): replaced with `\rhval{cmp/main/fine-tuning/split_til/average_accuracy/paired_p}`.
- All 95% intervals ([-0.029, 0.094], "-0.000 to 0.075", the CI column): deleted. `rh compare` records no interval; they came from my script.
- 0.032 (EWC gain over fine-tuning, split_cil; abstract, results, conclusion) and its p=0.220: deleted. `rh compare` records differences against one reference system (ER M=100), so this pair has no `\rhval` key. The text now gives the two means and the EWC seed std (`\rhval{main/ewc/split_cil/average_accuracy/std:3}`) for "within noise"; the abstract and conclusion say "only slightly above fine-tuning".
- -0.025 and p=0.092 (ER M=20 vs EWC, perm_dil): deleted, same reason. The text now gives the two means and the ER M=20 seed std.
- 0.044 (fine-tuning to joint gap, split_til; results and conclusion): deleted, same reason. Results keeps "a gap inside the registered 0.10" with both means; the conclusion gives the range of means as the abstract does.
- p=0.023 and p=0.033 (joint vs fine-tuning and vs EWC, split_til) with the "twelve tests" remark: sentence deleted, same reason. It claimed no significance, and the conclusion that the continual methods cannot be ranked there stays.
- 0.001 ("three learning rates within 0.001", setup): replaced with the three `\rhval{tune_lr/...}` means.
- "near 0.2" (split_cil accuracy at small and large lambda, ablations): replaced with the `\rhval{sweep_lambda/...}` means.
- "roughly 5, 18 and 5 minutes" (setup): deleted. They were hand-read wall-clock totals; they agree with the registry timestamps, but no `rh` value carries them. The run counts beside them are now `\rhval{count/.../runs}`.
- "smaller than about 0.02" (limitations): reworded to "small differences"; it was a hand estimate.

## Retyped results
- Every mean and standard deviation quoted in the abstract, results, ablations, setup and conclusion (about 100 numbers) is now `\rhval{<key>:3}` instead of a typed copy of a table cell. Each one was first compared with the registry by meaning, not by digits: none disagreed, so no value in the text was corrected.

## Constants
- Declared `n_images` 1797, `n_train_per_permuted_task` 1078, `n_train_per_split_task` 215, and the registered hypothesis thresholds `h2_ewc_gain_threshold` 0.05, `h2_er_gain_threshold` 0.2, `h3_gap_threshold` 0.10.
- Known weakness: the tracer still attributes the literals 0.05, 0.2, 0.10, the learning rates 0.01/0.05/0.1 and the buffer size 100 to unrelated statistics with the same digits rather than to the constant or run setting. They are setup values, not results; I could not change which source the tracer picks.

## Metrics (rule 3)
- `research.yaml` `metrics:` holds seven result metrics and no wall-clock or throughput metric, so nothing was marked `nondeterministic` and no result metric was marked.
- All randomness in `method/run.py` is seeded (data split, permutations, initialisation, batch order, Fisher label sampling, buffer sampling). Check: two logged main runs were executed again outside the registry (EWC lambda=1000 split_cil seed 0; ER M=100 perm_dil seed 3) and all seven metrics matched the logged values to the last digit.

## Other files
- `paper/main.tex`: `rh paper build` added the line that loads `generated/values.tex`.
- `paper/sections/author.tex`: platform version left as is, not edited.
- `experiments/paired_stats.py`: no longer writes a table for the paper; kept as an auxiliary analysis. `results/tables/paired_main.tex` and `paper/generated/paired_main.tex` removed.
- `experiments/make_stats.sh`: ends with the default-reference `rh compare`, whose CSV (`results/tables/compare_main_average_accuracy.csv`) feeds the `\rhval{cmp/...}` keys. Re-running `rh compare --ref <other>` overwrites that CSV and changes those keys.
- Length 6 pages; no "state of the art" or "novel" in the text.

## Final checks
`rh paper build`: BUILD OK. `rh lit verify`: CITATIONS VERIFIED. `rh numbers`: ALL NUMBERS TRACED. `rh check`: READY (one warning that predates this pass: verdict tier 0 below target 2, joint training is above the method on perm_dil).
