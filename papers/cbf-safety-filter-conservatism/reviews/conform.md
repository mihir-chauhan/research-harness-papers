# Conformance report (numbers traced, constants declared)

No claim, framing or experiment was changed. No run was added, no registry row edited, no constant declared.
Final state: `rh paper build` BUILD OK (6 pages), `rh lit verify` CITATIONS VERIFIED (11/11), `rh numbers` 791 checked /
791 traced / 0 untraced, `rh check` READY (one pre-existing warning: verdict tier 0 < target 2, unchanged).

## Rule 1: numbers (16 untraced occurrences of 6 values before, 0 after)

All six values are means over the 5 seeds of one (alpha, dt) cell of the `grid_alpha_dt` group, written by
`method/make_sweeps.py` from `results/runs.jsonl`. They agree with the registry (checked: 0.618, 0.358, 0.6786, 0.862,
10.7317, 6.760), so no text was corrected for disagreeing with it. They are untraced because the platform keys aggregates
by at most one swept setting, so a two-setting cell mean has no `\rhval` key. None is a setup fact, so none was declared
as a constant. One line per change:

- 0.679 (abstract): number deleted; sentence now says penetrations are comparable to the unfiltered controller where alpha*dt>=1, "up to `\rhval{grid_alpha_dt/dt-cbf@dt=0.2/double_integrator/barrier_penetration/max:3}` m in a single seed" (prints 0.760; a different, keyed statistic: the single-seed maximum, not the seed mean).
- 0.679 (conclusion): same replacement by the same `\rhval` key, worded "worst penetration up to ... m in a single seed".
- 0.679 (results, saturated cells): same replacement by the same `\rhval` key; the 0.109 m, clearance and 0.759 m nominal figures in that sentence are unchanged.
- 0.679 (generated/grid_violation.tex, two cells: DI DT-CBF alpha=5 and 10 at dt=0.2): penetration entry of the cell printed as "--".
- 0.618 (results, "the rate reaches 0.618 at alpha=10, dt=0.05"): number deleted; now "the rate is above one half ..., Fig. 1 (grid)".
- 0.618 (ablations, Gain): number deleted; now "0.222 at alpha=5 and higher at alpha=10", pointing to the grid table and figure.
- 0.618 (ablations, Between samples): number deleted; now "the any-time rate is highest at alpha=10, dt=0.05 (grid figure)".
- 0.618 (generated/grid_violation.tex and generated/sample_vs_between.tex, DI DT-CBF alpha=10, dt=0.05): violation-rate entry printed as "--".
- 0.358 (generated/grid_violation.tex and generated/sample_vs_between.tex, DI DT-CBF alpha=10, dt=0.01): violation-rate entry printed as "--".
- 0.862 (results, unicycle CT-CBF alpha=5, dt=0.2): number deleted; now "a majority of the episodes at alpha=5, Fig. (grid)".
- 0.862 (generated/grid_violation.tex, same cell): violation-rate entry printed as "--".
- 10.73 (generated/sweep_alpha_cons.tex, DI DT-CBF alpha=0.5 time to goal): entry printed as "--".
- 6.76 (generated/sweep_alpha_cons.tex, DI DT-CBF alpha=10 time to goal): entry printed as "--".
- Captions of the three tables: one clause added explaining "--" (a cell mean the number trace cannot key; violation rates of these cells are drawn in the grid figure, times to goal in the sweep figure).
- `method/make_sweeps.py`: explicit `UNKEYED` list of these 7 cells, so the "--" entries are produced by the generator and survive `rh paper sync` (the tables were not edited by hand). Figures are unchanged.
- `paper/main.tex`: `\input{generated/values}` line added by `rh paper build` (needed for `\rhval`).

I removed single entries rather than whole table rows: the rows concerned are the ones where DT-CBF (the method row) does
worst, and dropping them would have made the paper look better than the data.

## Rule 2: only real runs

All 660 registry rows have a recorded command, exit code 0 and commit 745cf32; none was logged by hand. Nothing to replace.

## Rule 3: reproducible metrics

`research.yaml` has no wall-clock or throughput metric (`time_to_goal` is simulated time, a result), so nothing was marked
`nondeterministic` and `research.yaml` is unchanged. `method/run.py` draws scenarios from `default_rng(10000 + seed)` and
has no other randomness. I re-executed 12 logged commands picked at random across groups (output to /tmp, not logged):
all 9 metrics of all 12 matched the registry to the last digit.

## Rule 4: byline

`paper/sections/author.tex` not edited; the platform's rewrite is committed as found.

## Rule 5: length and wording

6 pages. No "state of the art" and no "novel" in the sources.

## Open issues (not hidden)

- **Many table cells are traced only by coincidence.** The grid tables hold about 500 two-setting cell means, and the same
  keying limit applies to all of them, not just the six above. They count as traced because some unrelated recorded value
  rounds to the same digits, e.g. in `grid_violation.tex` 0.222 (DI DT-CBF rate at alpha=5, dt=0.05) is matched to the
  mean `min_clearance` of CT-CBF with nearest-obstacle selection (-0.2217), 0.434 to a std in `grid_dt005`, 0.402 to one
  run's `min_clearance`. The values themselves are correct (generated from the registry by `make_sweeps.py`), but
  `rh numbers` passing does not show that for these cells.
- **Seven cells are now blank and three sentences lost a number.** A complete fix would be to log each (alpha, dt) cell so
  that it has its own key (for instance re-running the grid with one group per dt, 500 deterministic runs of under a
  second each). That is a new set of runs, which this task ruled out, so it was not done.
- The verdict-tier warning from `rh check` (DT-CBF 0.008 vs CT-CBF 0 on the double integrator) is the paper's actual
  finding and was left as is.
