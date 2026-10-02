# Conformance to the stricter paper rules

No claim, framing or experiment changed. No new runs were logged. Final state: `rh paper build` BUILD OK (6 pages),
`rh lit verify` CITATIONS VERIFIED (13 of 13), `rh numbers` 905 checked / 905 traced / 0 untraced, `rh check` READY
(one warning, unchanged: verdict tier 1 below target 2, which is the paper's own negative result).

## Changes, one line each

Setup constants declared (`rh const add`, stored in `research.yaml: constants`):
- `1001` (setup.tex, samples per trajectory): declared as `samples_per_trajectory`.
- `1000` (setup.tex, first tuning seed): declared as `tuning_seed_first`.
- `1004` (setup.tex, last tuning seed): declared as `tuning_seed_last`.
- `161` (setup.tex, largest Savitzky-Golay window of the grid, read by the tracer as `81,161`): declared as `sg_window_max`.

Hand-summed run counts (setup.tex, Compute):
- `1540` (current experiment runs, a sum over five groups typed by hand): replaced by `\rhval{count/runs}` (1547, which also
  counts the smoke test and the six tie-diagnostic runs; the sentence now lists them inside the parenthesis).
- `600`, `600`, `200`, `60`, `80` (runs per group in the same sentence): replaced by `\rhval{count/<group>/runs}`; same values.
- `1100` (superseded first-version runs, a difference typed by hand): deleted; the sentence now gives
  `\rhval{count/runs_all}` (2648 logged runs) and says the others are superseded (first-version runs and one earlier
  tie diagnostic). No subtraction is typed.

Hand-typed p-values and differences (they passed the tracer only by coincidence, e.g. `0.119` matched a mean runtime):
- `p=0.042` (results.tex, H1, weak vs FD and spline at 2 %): replaced by `\rhval{cmp/main/fd-stlsq/lorenz_n2/support_exact/welch_p:3}`.
- `p=0.119` (results.tex, H1, weak vs TV at 5 %): replaced by `\rhval{cmp/main/tv-stlsq/lorenz_n5/support_exact/welch_p:3}`.
- `p=0.369` (results.tex, H2, TV vs FD at 5 %): deleted from the sentence, which now points to Table III(c) where the
  value is generated. This comparison uses FD as reference and has no `\rhval` key (see open points).
- `0.20 ... p=0.042` (results.tex, last paragraph): replaced by `\rhval{cmp/main/fd-stlsq/lorenz_n2/support_exact/delta:2}` and the welch_p key above.
- `0.15 ... p=0.083` (same sentence): replaced by `\rhval{cmp/main/tv-stlsq/lorenz_n2/support_exact/delta:2}` and `.../welch_p:3`.
- `0.25 ... p=0.119` (same sentence): replaced by `\rhval{cmp/main/tv-stlsq/lorenz_n5/support_exact/delta:2}` and `.../welch_p:3`.
- `the two p=0.042 cells` (same paragraph): replaced by the welch_p key above.
- `about 0.25` (limitations.tex, unresolved rate difference): replaced by `\rhval{cmp/main/tv-stlsq/lorenz_n5/support_exact/delta:2}`.
All ten comparison macros print the same digits as the text they replace.

Other files:
- `research.yaml`: `runtime_s` given `nondeterministic: true`. No other metric is marked.
- `paper/main.tex`: `rh paper build` added the line that inputs `generated/values.tex` (needed for `\rhval`).
- `paper/sections/author.tex`: not edited by me; the platform's rewrite is committed as found.

## Checked, nothing to change

- Rule 1, text against registry: every result number in the abstract, results, ablations, conclusion and setup prose was
  compared by hand with the aggregate it is meant to report (main, threshold grid, width, exponent, library-state,
  tie diagnostic, tuned thresholds of both versions). No disagreement found, so no number was corrected.
- Rule 2: the registry has no hand-logged row. All 2648 run rows carry a command; `rh check` reports no record problem.
- Rule 3: all result metrics are reproducible from the seed. Data and noise come from `np.random.default_rng(seed)`
  and nothing else is random. 44 logged runs (every group and system, including a tie diagnostic) were run again to a
  scratch file in /tmp and every metric except `runtime_s` was identical to the last digit. These re-runs were not logged.
- Rule 5: 6 pages; no "state of the art" and no "novel" in any section.

## Open points

- The tracer matches by value. Most result numbers in the prose are still typed literals (they agree with the
  registry, see above), and for many of them `rh numbers` names a different cell with the same value as the source
  (e.g. `0.65` is attributed to a false-positive mean). They were not converted to `\rhval`; only derived numbers were.
- Table III(c) (FD as reference) is generated from `results/tables/h2_fd_ref_coef_err.csv`, an `rh compare --ref
  FD-STLSQ` output that `analysis/build.sh` renames. The tracer only recomputes `compare_*.csv`, so these p-values
  have no `cmp/` key and are traced by value only.
- `p<0.05` (the registered significance level) is traced by value to an unrelated mean; it was not declared as a constant.
- The build log has overfull boxes in the author block (platform text) and in two tables; none was introduced here.
