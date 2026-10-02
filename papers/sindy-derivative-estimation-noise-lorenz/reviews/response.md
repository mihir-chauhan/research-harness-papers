# Response to the audit (fix round on the revised paper)

All numbers in the paper come from runs in `results/runs.jsonl` and reach the text through `analysis/build.sh`
(`rh table`, `rh compare`, `analysis/make_report.py`). No main, sweep or ablation run was repeated in this round: the
tuned configurations did not change (see finding 1). New runs: six diagnostic runs on the tuning seeds (group
`tune_diag`). `rh check`: READY; `rh lit verify`: CITATIONS VERIFIED; 6 pages.

## 1. Major: "exact ties" are not identical models (FD at 5 %, spline at 10 %)
Accepted; the finding is correct and the earlier description was false.
- What the tuner does (unchanged): highest support rate, then lowest median coefficient error, then the largest
  threshold. A tie is equality of rate and median, nothing more. The text now says exactly this in
  `paper/sections/setup.tex` (Tuning), `method/tune.py` (docstring and comment), `experiments/PROTOCOL.md`,
  `method/DESIGN.md`, `BRIEF.md`, `results/RESULTS.md`. The "exact tie" wording is gone from all of them; only the
  log label `exact_ties_thr=` printed by `tune.py` is kept (with a comment), so that the script still reproduces
  `results/logs/tune.log` byte for byte.
- New diagnostic `method/tie_check.py` (committed before it was run; six registered runs, one per noise level,
  group `tune_diag`, tuning seeds 1000-1004 only). It repeats the tuner's grid, asserts that it reproduces
  `tuned.json`, and for each of the 30 cells compares the models (coefficient matrices) of all configurations tied
  with the selected one. Result: 19 cells have a tie; in 17 the tied configurations return identical models on all
  five trajectories, including the three TV cells the auditor had not checked; in 2 they do not: FD at 5 %
  (0.05 vs 0.1, different models on 3 of 5 trajectories, per-trajectory errors as the auditor reports, mean tuning
  error 0.0664 vs 0.0566) and spline at 10 % (0.4 vs 0.6, 1 of 5, 0.1214 vs 0.1212). No tie involves two different
  smoothing parameters.
- Why the rule was not changed again: the diagnostic also evaluates the auditor's alternative (break median ties by
  mean error, largest threshold only if the mean is equal too). It selects the same configuration in all 30 cells,
  so re-tuning would reproduce `tuned.json` and every run. Changing the code of the rule a third time for no change
  in any result would only add another post hoc step; the decision is recorded with `rh decide`.
- Paper: new paragraph "What a tie is" in the setup with these counts and the statement that the FD threshold at
  5 %, on which the H2 verdict turns, is a choice between different models made on five trajectories; the H2
  paragraph, the limitations and the ablation text refer to it. `analysis/make_report.py` asserts the counts
  (30 / 19 / 17 / 2) and writes `results/tables/rep_ties.tex` (not included in the paper for space; the prose gives
  only the counts).
- Run history: the first execution of the diagnostic did all six levels in one run under the task name
  `tuning_seeds`; `rh check` treats every task name in the registry as a task of the study, so that row was
  superseded (`rh supersede`, visible with `rh runs --all`) and the diagnostic was run once per noise level. Same
  values.

## 2. Minor: abstract, "every support once the threshold is at least 0.4"
Accepted. Abstract: "at a threshold of 0.4". The same over-statement in the ablation text ("irrelevant once
lambda >= 0.4") is rewritten: no difference at 0.4, almost none at 0.6 (only FD at 1 % drops, to 0.95).

## 3. Minor: conclusion, "lowest mean coefficient error ... clearest gap at 5 %"
Accepted. Conclusion now: lowest mean at every level, significantly against all four baselines only at 0 % and
10 %; the clearest separation at 5 % is in the median (0.0129 against 0.0456-0.0739), and the mean there is not
significantly below FD or TV.

## 4. Minor: H2 caveat missing from abstract and conclusion; TV
Accepted. Abstract, introduction and conclusion say that the H2 verdict is the registered test's and depends on the
finite-difference threshold. Results (H2) add: TV's higher mean is not significant (p=0.369) and TV is below FD in
all five equal-threshold columns of Table VI; spline is above FD at four of five thresholds (not at 0.05); only SG
at all five; on the true support FD is below SG and spline but not TV. The untested "may explain" sentence about
tuning for support was removed.

## 5. Minor: inconsistent statement of resolution
Accepted. One statement in the results, referenced from the limitations: 0.20 (1.00 against 0.80) gives p=0.042,
0.15 (p=0.083) and 0.25 between 0.65 and 0.40 (p=0.119) are not significant, and the two p=0.042 cells would not
survive a Bonferroni correction even over the four comparisons of that level. The H1 paragraph marks p=0.042 as
uncorrected. Limitations: "rate differences up to about 0.25 are not reliably resolved".

## 6. Minor: exponent ablation pointed to a file outside the paper
Accepted. The sentence gives the support rate (1.00 for p = 2, 3, 4, 6) and the four mean coefficient errors
(0.0039, 0.0035, 0.0033, 0.0031), with "differences not tested". A table did not fit in six pages.

## Other changes from the self-audit
- "the weak form's lead at 5 % holds against the best threshold of each baseline" is weakened everywhere to "its
  rate is above the best threshold of each baseline", and the ablation text adds that against TV the difference is
  not significant.
- "Means at 10 % are pulled up by a few trials" (a mechanism without a run) is replaced by the plain comparison of
  medians and means.
- The three p-value tabulars are merged into one (same cells; `rep_p_all.tex`), figures are regenerated at their
  printed size (same data), several sentences were shortened and three removed to stay within six pages; no number
  changed. The registry count in the setup now lists the smoke test and the six diagnostic runs.

---

# Previous round (kept for the record)

All experimental numbers in the revised paper come from runs in `results/runs.jsonl` and reach the text through
`analysis/build.sh` (`rh table`, `rh compare`, `analysis/make_report.py`). The first-version runs are kept in the
registry as superseded (`rh runs --all`).

## 1. Major: FD threshold at 5% noise chosen by an arbitrary tie-break
Accepted. Cause fixed, not the wording.
- `method/tune.py`: exact ties (configurations returning identical models on all 5 tuning trajectories) are now
  resolved toward the largest threshold instead of by grid order. Same tuning seeds, same grids, same rule for every
  system; smoothing parameters did not change. The tie rule had decided the threshold in 19 of 30 system x level cells,
  not only for FD at 5%, so the change moved 19 thresholds (first-version values in `method/tuned_v1.json`,
  `results/logs/tune_v1.log`; Table I of the paper lists both).
- Re-ran through `rh run`: all 600 main runs, the width sweep (200) and the exponent ablation (60). The library-state
  ablation (80 runs) was not re-run because the SG and spline settings at 2 and 5% are unchanged.
- Added the diagnostic the auditor asked for, for every system and level rather than FD at 5% only: 600
  threshold-grid runs (`run.py --thr-grid`, group `sweep_thr`), reported in Tables V and VI with the tuned and the
  first-version threshold marked. `make_report.py` asserts that the grid cell at the tuned threshold equals the main
  run and that the cell at the first-version threshold equals the superseded main run.
- Consequences for the claims: "smoothers below FD at every level from 1%" is gone; H2 is now refuted (at 5% all three
  smoothers have a higher mean error than FD at threshold 0.1; the text says this verdict depends on the FD threshold
  and gives the 0.05 value). "FD extreme failure, 4.75 spurious terms" is gone; FD at 5% is described with its tuned
  threshold (2.70 spurious terms, rate 0.00) and with its rates at 0.4 and 0.6. The weak-vs-FD coefficient-error test
  at 5% is now reported as not significant (p=0.179).
- Disclosure: setup has a paragraph "Revision of the tie rule" saying the new rule was adopted after the first test
  results were known and is therefore not a pre-registered choice; the abstract, introduction, results, limitations and
  conclusion say that the ordering below 5% noise reverses with the tie rule. FD at 5% (and all baselines at 10%) had
  0.00 tuning support at every threshold, so the threshold there is set by median error alone; this is stated.
- Note on the run history: the re-run was interrupted once; `experiments/launch.py` was made resumable and the
  remaining jobs were run. No run was dropped; the main rows record commits 56aba08 and 0e9ecd9, which differ only in
  the launcher.

## 2. Minor: "crossover between 2 and 5%" over-reads non-significant differences
Accepted. The sentence is removed. H1 is still refuted by the registered test, but the text now says the ordering
below 5% is not resolved and follows the threshold selection. The threshold sweep is extended to all five systems and
all six levels (Table V).

## 3. Minor: 0% failures of FD and SG attributed to discretisation error
Accepted. The H3 paragraph now says these two failures were small spurious terms below a threshold of 0.1 (both
systems are at 1.00 for every threshold >= 0.1, Table V). With the revised thresholds all systems are at 1.00 at 0%,
so H3 is supported.

## 4. Minor: H4 and H5 restated more loosely than registered
Accepted. Setup quotes the wording of `proposal.md`; `research.yaml` carries the same wording. H4 is reported as partly
supported with the directional part not supported (the narrowest window keeps the rate, wide windows lose it); H5,
registered for support recovery at 2%, is reported as not supported. `results/RESULTS.md` is rewritten accordingly.

## 5. Minor: self-contradictory "within +-0.05 except SG"
Accepted. Now: the rate "moves by at most 0.05 in either direction in all four cells".

## 6. Minor: ODE Weak SINDy paper not cited; uncited "existing papers" sentence; PDE-FIND "main obstacle"
Accepted. `messenger2021weak` (10.1137/20M1343166, added with `rh lit cite`) is cited in the introduction and related
work as the direct precedent, and the Gap paragraph is positioned against it. The uncited sentence and the PDE-FIND
"main obstacle" claim are removed; PDE-FIND is cited only for extending sparse regression to PDEs.

## 7. Minor: limitations
Accepted. Limitations open with "All data are simulated; no real measurements are used" and state that five tuning
trajectories do not determine the threshold (ties in 19 of 30 cells, rule changed after the first results).

## 8. Minor: Fig. 2 ticks, Table XI daggers
Accepted. Fig. 2 has explicit ticks at the six widths with minor ticks off. The old Table XI is replaced by the
threshold grid (shading and underline instead of daggers). The template font has no bold face, so the grid marks
use shading. The two tables that were shrunk with `\resizebox` (tuned thresholds, FP/FN) are transposed and set at
normal size.

## 9. Minor: citations.json timestamp
Committed after the final `rh lit verify`.

## Other changes from the self-audit
- Median coefficient error added to the main table: the means at 10% are pulled up by a few trials, and the
  weak-form gap in medians (0.1094 against 0.1224-0.1337) is much smaller than in means. The text says so.
- p-value tables mark cells where the difference is against the hypothesised direction.
- The exponent ablation is now a null result (same rate for p = 2, 3, 4, 6) and is reported in one sentence with a
  pointer to `results/tables/rep_p.tex`; its table was removed to stay within 6 pages.
- Runtime moved into Table I; Fig. 1 y-label shortened.
