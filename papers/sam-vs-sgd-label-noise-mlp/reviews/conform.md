# Conformance report

No claim, verdict or experiment of the study changed. `rh numbers`: 691 checked, 691 traced, 0 untraced (before: 34 untraced). `rh check`: READY. 6 pages.
No number in the text disagreed with the registry: after the rewrite every value printed by `\rhval` equals the literal it replaced (checked file by file), apart from the format changes listed below.

## Rule 1: numbers

Setup facts declared with `rh const add` (research.yaml `constants`):
- 150 (abstract, setup): `epochs`.
- 128 (method x5, limitations): `hidden_width`.
- 1797 (setup x2, limitations): `digits_images`.
- 600, 300, 897 (setup, limitations): `digits_train`, `digits_val`, `digits_test`.
- 400, 200 (setup, limitations): `spirals_train` (also the test size), `spirals_val`.
- 900 (setup): `digits_steps`.
- Also declared, because no run records them and the tracer had only matched them to unrelated values by coincidence: `batch_size` 100, `learning_rate` 0.1, `momentum` 0.9, `spiral_turns` 1.5, `sharpness_radius` 0.5, `noise_low` 0.2, `noise_high` 0.4, `alpha` 0.05.

Derived numbers that no registry statistic covered: now computed by `experiments/derive.py` and logged through `rh run` (22 rows, group `derived`, driver `experiments/drive.py derived`), then printed with `\rhval`:
- 260, 219 and the other n of Table VI (corr.tex; 260 also in introduction, results text, Fig. 2 caption): metric `n_runs` of the `corr ...` rows.
- All Spearman correlations (Table VI, abstract, conclusion, H3 paragraph): metrics `rand_acc`, `rand_loss`, `adv_acc`, `adv_loss` of the `corr ...` rows. Before, they came from `analyse.py` and were traced only by coincidence with unrelated aggregates.
- Holm-adjusted p (0.000311 untraced in cmp.tex, the rest of the column, 0.101 in H1): metric `holm_p` of the `SAM minus SGD` / `SAM minus SGD+WD` rows.
- Per-seed differences SAM minus SGD+WD at 20% and 40% noise (H1): metrics `diff_seed0..4` of the same rows.
- The three pooled correlation rows are filed under task digits_n0.4, because a registry row needs a task and `rh check` requires the method to have main runs on every task name; the row name, config (`pooled_over`), row note and the Table VI caption say what they pool.

Rescaled or hand-typed results replaced by registry values:
- 1.125, 1.353, 1.108, 1.059 (main.tex), 1.053, 1.044 (abl_sam.tex) and the whole sharp_rand column, which was printed in units of 1e-3: now `\rhval{.../sharp_rand/mean:sci2}` and `std:sci1` in native units (e.g. 1.13 x 10^-3); captions of Tables II and VII changed accordingly.
- 1.125, 1.353, 0.615, 0.539, 1.804, 2.424 "in units of 10^-3" (H3 text) and 1.125 x 10^-3 (ablations): same keys, scientific notation; "in units of 10^-3" deleted.
- Tables II, III, IV, V, VI, VII: every result cell is now `\rhval{<key>}`, written by `experiments/analyse.py`; no cell is a typed or formatted number. Table I (selected hyper-parameters) keeps its run settings.
- Differences and p-values in abstract, results, ablations, conclusion (0.008/0.0078, 0.027, 0.010, 0.139, 0.276, paired and Welch p): `\rhval{cmp/main/...}` (the statistics of `rh compare`).
- All other result numbers in the prose (means, stds, memorised, sharpness, weight norms, sweep values, run counts 120/60/100/60/40): `\rhval` of the aggregate, sweep or count key.

Hand-computed numbers deleted or reworded (no key exists and none was computed):
- "p < 10^-4 under both tests" (H1): replaced by the two paired p-values (`\rhval`, 8.7 x 10^-5 and 3.9 x 10^-5) and a pointer to Table III for the Welch values.
- "within 0.002 of SGD" (ablations): now "against 0.799 and 0.625 for SGD".
- "(0.1 and 0.5 are within 0.004 of it)" (H2): now "(0.1 and 0.5 reach 0.970 and 0.970)".
- "four seeds are near 0.09" (ablations): now "four seeds are near chance, the median is 0.094".
- "weight norms differ by a factor of up to 3" (limitations): now the two weight norms at 40% noise (8.77 and 26.14).
- Compute paragraph (setup): "1.3-6.7 s (mean 2.7 s)", "SAM about 1.3-1.6x the time of SGD", "all 381 logged runs", "46 minutes", "17 minutes" deleted; replaced by the mean run time of SGD and SAM in the main group on digits at 20% noise (`\rhval`, 3.5 s and 5.0 s) and a sentence on the 22 analysis rows.

## Rule 2: real runs
- All 381 existing rows already had a command and a log (`rh run`); nothing was hand-logged, nothing replaced. The 22 new rows are `rh run` rows.

## Rule 3: reproducible metrics
- `runtime_s` added to research.yaml `metrics` with `nondeterministic: true` (wall-clock).
- No result metric is marked. Checked by repeating 11 logged training runs (main, sweeps, tuning, ablation) and 5 derived rows: every metric except `runtime_s` came back identical. All randomness is seeded (split, label noise, initialisation, batch order, random perturbation and sharpness directions).

## Rule 4: byline
- `paper/sections/author.tex` not edited; the platform's version is committed as it was found.

## Rule 5: length and wording
- 6 pages. The paper contains neither "state of the art" nor "novel"; nothing to change.

## Other files
- `experiments/analyse.py`: tables typeset with `\rhval` keys. `experiments/drive.py`: `derived` step. `experiments/PROTOCOL.md`: derived rows, constants, rebuild order. `paper/main.tex`: the `\input{generated/values}` line added by `rh paper build`.
- Not updated: `results/RESULTS.md` and the `.md`/`.csv` copies in `results/tables/` (not part of the paper).
