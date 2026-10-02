# Conformance report (numbers traced, constants declared)

No claim was added or reframed and no run was added. All 150 registry rows were logged by `rh run` with a command and a log (none by `rh log`), so rule 2 required no replacement.

## Constants declared (`rh const add`, setup facts only)
- 1,797 (setup): declared `n_images`, size of the scikit-learn digits dataset.
- 1234 (setup): declared `split_random_state`, random_state of the fixed split.
- 1,078 (setup, limitations): declared `n_train`, training images in the fixed split.
- 719 (setup): declared `n_test`, test images in the fixed split.
- 256 (setup, FC(256->64)): declared `fc_in`, input width of the first fully connected layer.
- 20, 40, 60 (noise rates in percent): declared `noise_rate_20/40/60`. They were already counted as traced, but only by coincidence with unrelated statistics; the tracer still prefers the coincidental match (e.g. "40%" is reported as the std of a runtime), so the declaration documents them without changing the trace.
- 0.05, 0.9, 0.1 (learning rate, momentum, main-grid label-smoothing epsilon): declared `learning_rate`, `momentum`, `ls_eps_main`, for the same reason.

## Derived numbers replaced by registry values
- Table "paired" (generated/paired.tex, hand-computed by analysis/make_extras.py: 0.5740, 0.0429, 0.581, 0.0141, 0.053, 0.720, 0.0948, 0.087, 0.142 and the rest of its 27 cells): file deleted; the table is now written in results.tex from `\rhval{cmp/main/<system>/<task>/test_acc|mem_rate/delta:3}` and `.../test_acc/paired_p` (from `rh compare --group main --metric test_acc|mem_rate --ref CE`).
- Sign convention: the registry delta is CE minus system, the old table was system minus CE. The table header, caption and one sentence in the results say so; magnitudes and conclusions are unchanged.
- results.tex H2: p=0.5740, Delta=-0.041 / p=0.0141, Delta=-0.026 / p=0.0948 replaced by the `\rhval` keys (now printed as CE minus LS 0.041, 0.026).
- results.tex H2: "a difference of 0.4 points" replaced by `\rhval{cmp/main/label-smoothing/digits_noise0/test_acc/delta:pct1}` (CE minus LS, -0.4).
- results.tex H3: Delta=+0.024, +0.053, +0.087 and p 0.0429, 0.0003, 0.0018 replaced by `\rhval` keys (CE minus mixup).
- results.tex H4: Delta=+0.187, +0.335 and "p<0.0001" replaced by `\rhval` keys; the two p-values are now printed exactly (6.857e-5, 4.251e-5) instead of as a bound.
- p-values now print with the registry's four significant figures (0.01411, 0.09484, 0.04288, 0.0002774, 0.001751, 0.0007546) instead of four decimals. No text value disagreed with the registry beyond this rounding.
- setup.tex and limitations.tex "two runs exceeded 300 s": replaced by the two slowest runs' logged runtime, `\rhval{run/5cecfeef8b/runtime_s:0}` and `\rhval{run/053a6b0376/runtime_s:0}` (334 s, 367 s).
- ablations.tex "about 1,000 examples": replaced by the declared constant 1,078 (training examples).

## Numbers removed because the registry cannot produce them
- Table "curves" (generated/curves.tex; 0.916, 0.904, 0.603, 0.634 and all epoch-10 / best-checkpoint cells): deleted. These are means over run-log curves computed by analysis/make_curves.py, not registry metrics. Most of its cells had been "traced" only by coincidence with unrelated statistics.
- results.tex "best logged checkpoint is 0.805 for CE, 0.854 for LS, 0.891 for mixup and 0.904 for small-loss" and "(best checkpoint at 40%: 0.854 vs 0.805)": numbers deleted. The claim itself (LS above CE and mixup close to small-loss at the best logged checkpoint, so the ranking is specific to final-epoch evaluation) is kept in words in the abstract, results, limitations and conclusion, with a sentence saying the values are in the run logs and are not registry metrics. NOTE: this claim is now supported only by the logs and analysis/make_curves.py, not by a traced number; getting traced values would need the 60 main-grid runs re-logged with epoch-10 and best-checkpoint metrics, which the brief did not allow.
- Table "warm" (generated/warmup_paired.tex; +0.028, p=0.0030, -0.133, p<0.0001): deleted, together with the words "uncorrected t-test". The no-warm-up rows are in group abl_smallloss and the main small-loss rows in group main; `rh compare` only compares inside one group ("nothing to compare"), so the paired difference and p-value cannot come from the registry. These cells had passed `rh numbers` only by coincidence (e.g. 0.028 matched an unrelated std). The paper now gives the two registry means (0.924 vs 0.896, mem_rate 0.146 vs 0.280) and states that no test is reported.

## Reproducible metrics
- research.yaml: added `runtime_s` under `metrics:` with `nondeterministic: true` (the only wall-clock metric the runs log).
- No result metric is marked nondeterministic. All randomness in method/run.py is seeded (noise draw, initialisation, batch order, mixup lambda and permutation). Checked by re-running two logged commands outside the registry (Mixup/digits_noise40/seed 3, Small-loss/digits_noise60/seed 1): every metric except runtime_s matched to the last digit.

## Other
- paper/sections/author.tex: platform rewrite left untouched (committed as found).
- paper/main.tex: `rh paper build` added the `\input{generated/values}` line; paper/generated/values.tex is tool-written.
- results/tables/compare_main_test_acc.csv: regenerated with `--ref CE` (was ref Small-loss); compare_main_mem_rate.csv added. The `cmp/` keys do not encode the reference, so these files must stay at ref CE.
- analysis/make_extras.py no longer writes paired.tex; analysis/make_curves.py prints only (diagnostic). results/RESULTS.md has a note on both.
- Length 5 pages (was 6, two tables removed; minimum 4). No "state of the art" or "novel" in the text.
