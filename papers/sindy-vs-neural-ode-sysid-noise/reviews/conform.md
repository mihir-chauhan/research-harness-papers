# Conform report: numbers traced, constants declared

No claim, hypothesis verdict, experiment or run was changed. No run was added: the registry is the same 453 rows.
One line per change.

## Rule 1: untraced numbers (15 listed by `rh numbers`, now 0)
- `method.tex` 128 (MLP batch size): declared constant `mlp_batch_size`, printed with `\rhval{const/mlp_batch_size}`.
- `method.tex`, `limitations.tex`, `results.tex` 2500 (MLP gradient steps, 3 places): declared constant `mlp_gradient_steps`, printed with `\rhval`.
- `setup.tex` 450 (runs in the registry): replaced by `\rhval{count/runs}` (453) "of which `\rhval{count/diag_lqr/runs}` (3) diagnostic". The text said "450 ... plus three diagnostic runs", so the total is unchanged; the registry count is 453.
- `generated/noise_gap.tex` 0.478 and `results.tex` "0.478 to 0.341" (median paired MLP-SINDy gap): the gap column is deleted, no recorded statistic is a median paired difference. The sentence now cites the SINDy and MLP medians at noise 0.05 and 0.1 (`\rhval`, aggregates) and speaks of the difference between the medians; the pattern claimed (grows to 0.05 on both systems and to 0.1 on Van der Pol, falls on the pendulum between 0.05 and 0.1) is the same and is read from the same table.
- `generated/paired_lqr.tex` 2642.0, 2620.8, 142.5, 2816.0, 1010.4, 3716.0 (mean paired LQR difference in percent of the oracle, computed by my script): the whole table now prints the ratio of mean LQR cost to the oracle's mean cost from `rh compare --group main --metric lqr_cost --ref "True model (oracle)"` (`cmp/main/<system>/<task>/lqr_cost/inv_ratio`). Caption changed to say so.
- `results.tex` 142.5\%, 1010.4\% (MLP on the pendulum) and the neighbouring 4.9\%, 3\%, 23.1\%: replaced by the same `rh compare` ratios (1.048, 2.405, 11.419 for the MLP; at most 1.027 and 1.215 for SINDy).

## Rule 1: derived numbers that the tracer had matched to an unrelated value by coincidence
- `abstract.tex` and `results.tex` 6.7\% (MLP LQR cost above the oracle, Van der Pol, noise 0.1; was matched to a `seconds` value): replaced by the `rh compare` ratio, 1.063. REGISTRY WINS: the statistic changes from the mean of per-seed percentage differences (6.7\%) to the ratio of means (6.3\% above the oracle). The claim (all models close to the oracle on Van der Pol) is unchanged.
- `results.tex` 1.9--3.5\% (DMDc), 0.4\% (MLP), 0.2\% (SINDy) on Van der Pol: replaced by `rh compare` ratios (1.019 to 1.035, at most 1.004, at most 1.002).
- `results.tex` "23.1\%" for SINDy on the pendulum at noise 0.1 becomes ratio 1.215 (21.5\% above the oracle): same change of statistic as above, noted for the same reason.
- `results.tex` p <= 0.015 (pendulum, noise sweep), p = 0.819 and 0.998 (Van der Pol, noise 0.1): now `\rhval{cmp/main/.../pred_nrmse/paired_p}`. Values unchanged.
- `results.tex` p = 0.003 (pendulum N=200), p = 0.262 (Van der Pol N=200), p <= 0.014 (Van der Pol from N=500): deleted. `rh compare` compares per task and cannot split a sweep group by N, so these p-values have no recorded source. The H1 verdict did not rest on them (registered criterion: 3 of 5 seeds, means and medians, all still reported).
- `generated/ntrain_pred.tex` last column: p-values deleted for the same reason, the seed counts stay. Caption changed.
- `generated/noise_gap.tex` p-values: now `\rhval{cmp/main/...}`; the cells that read "<0.001" now print the value (e.g. 7.6e-6).
- `generated/abl_combined.tex` p-values and Delta-LQR: now `\rhval{cmp/abl_sindy/...}`. `rh compare` reports full minus variant, so the sign of the Delta-LQR column is reversed against the old table (old +17.904 is now -17.904); the caption states the new convention. Magnitudes unchanged.
- `setup.tex` "about 21 minutes in total": deleted (a sum typed by hand, no recorded value). "about 7 seconds" for the MLP is now `\rhval{main/neural-ode-mlp/pendulum_noise0.05/seconds/mean:0}`.
- `results.tex` "DMDc is near 1.0": now "near 1 (means between 0.997 and 1.031)" with the two means from the registry.

## Rule 1: results in prose and tables now printed from the registry instead of retyped
- `results.tex`, `ablations.tex`: every result number (means, medians, standard deviations, single-seed values, failure rates, term counts) is now `\rhval{<key>}`. All of them expand to exactly the digits that were typed before; none disagreed with the registry.
- `experiments/make_figs.py`: the derived tables (`vdp_seeds`, `noise_gap`, `paired_lqr`, `abl_combined`, `ntrain_pred`, `ntrain_lqr`, `lam`, `diag_lqr`) are written with `\rhval` keys; the script no longer computes any reported statistic (it only lays out cells and counts seeds). Checked by expanding the new tables and diffing against the old ones: identical apart from the changes listed above. New flag `--tables-only`; figures were not regenerated.
- Seed counts such as "5 of 5" and "3/5" are still counted by the script from the registry; they are integers below 100, which the tracer does not check. They can be verified against the per-seed table.

## Rule 1: setup constants declared (`rh const add`) and printed with `\rhval{const/...}` in `method.tex`
- `dt` 0.05, `pendulum_damping` 0.5, `vdp_train_ic_bound` 1.5, `pendulum_cl_ic_bound` 0.5, `lqr_input_weight` 0.1, `sindy_default_lambda` 0.05, `mlp_learning_rate` 0.003, `mlp_weight_decay` 1e-5, `mlp_batch_size` 128, `mlp_gradient_steps` 2500, `cost_cap` 1000, `fail_norm` 0.5. All are values in `method/run.py`; none is a result. Before, ten of these were "traced" only because some unrelated result happened to round to the same digits.
- Not declared: noise levels, training sizes and thresholds (0.02, 0.05, 0.1, 200 ... 5000, 0.01 ... 1). They are run settings on the logged command lines. The tracer still shows some of them matched to an aggregate of the same value, because it prefers aggregates to settings.

## Rule 2: hand-logged rows
- None. All 453 rows have a command, exit code 0 and an existing log; `rh check` reports no hand-logged row. Nothing replaced.

## Rule 3: reproducible metrics
- `research.yaml`: added `seconds: {higher_is_better: false, nondeterministic: true}`. It is the only wall-clock metric.
- No result metric is marked. Checked by running 13 logged commands again (SINDy, DMDc, oracle, MLP in main, sweep, ablation and diagnostic groups) with output to /tmp: every metric except `seconds` equal within 1e-6 relative. All randomness is seeded (numpy `RandomState`, `torch.manual_seed`). The check covers this machine with 2 threads; I did not test another machine or thread count.
- `rh const add` rewrote `research.yaml` in block style; the content of the existing keys is unchanged.

## Rules 4 and 5
- `paper/sections/author.tex`: not edited (the platform's version is committed as it stands).
- Length: 7 pages. No "state of the art" or "novel" in the paper.

## Final state
- `rh paper build`: BUILD OK. `rh lit verify`: CITATIONS VERIFIED (11 of 11). `rh numbers`: 941 checked, 0 untraced. `rh check`: READY (one warning, unchanged from before: verdict tier 0 < target 2, because the oracle has zero prediction error).
