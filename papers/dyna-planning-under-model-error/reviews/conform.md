# Conformance report: numbers traced, constants declared

No claim, hypothesis verdict or experiment changed. `rh numbers`: 510 checked, 510 traced, 0 untraced. `rh check`: READY (one pre-existing warning: verdict tier 0 < target 2, Dyna-Q is not best on blocking, which is what the paper reports). Paper: 6 pages.

## Numbers that were untraced
- `1000` (setup.tex, results.tex Fig. 2 caption; change step of the blocking maze): declared constant `blocking_change_step`, written as `\rhval{const/blocking_change_step}`.
- `123.9` (sweep_n_tab.tex, n=0 column, shortcut): was the mean of a seed subset (Q-learning, main group, seeds 0-9) computed in `method/analyze.py`. The 50 Q-learning main runs of seeds 0-9 are now listed in group `sweep_n` (`rh log --from-run`, a copy of the logged run, not typed and not rerun); the cell is `\rhval{sweep_n/q-learning/shortcut/cum_reward/mean:1}`. Same value.
- `190.2`, `78.4` (sweep_kappa_tab.tex, Dyna-Q column, static and stochastic): same cause; the 50 Dyna-Q main runs of seeds 0-9 are listed in group `sweep_kappa`; cells are `\rhval{sweep_kappa/dyna-q/<task>/<metric>/mean:1}`. Same values.

## Numbers that traced only by coincidence (hand-typed results the tracer matched to an unrelated value) and are now keyed
- All three hand-written tables (`sweep_n_tab.tex`, `sweep_kappa_tab.tex`, `abl_compact.tex`; also the unused `sweep_n_post_tab.tex`): `method/analyze.py` no longer computes table cells; every cell is a `\rhval{...}` key. All printed means are unchanged.
- Table III (`abl_compact.tex`), standard errors in parentheses: a derived number (std/sqrt(n)) with no registry key. Replaced by the standard deviation, `\rhval{abl_dynaq_plus/<variant>/<task>/post_reward/std:1}`; caption changed from "mean (s.e.)" to "mean (standard deviation)". Means unchanged.
- Table IV, default-kappa column: now `\rhval{sweep_kappa/dyna-q+@kappa=0.001/...}` (the dedicated runs in group `sweep_kappa`) instead of the main-group seed subset. Same values. setup.tex said this column was "taken from the main group"; the registry has its own kappa=0.001 runs on seeds 0-9, so the text now says "plus the default, all on seeds 0-9".
- Every mean and standard deviation in the prose of abstract.tex, results.tex and ablations.tex (200.2, 86.2, 7.9, 1.6, 39.9, 64.5, 51.9, 28.2, 229.7, 165.8, 92.4, 39.6, 55.4, 45.8, 220.6, 84.2, 29.8, 18.6, 122.7, 188.8, 168.2, 36.8, 52.1, 128.4, 20.1, 46.1, 36.5, 50.8): replaced by the `\rhval` key of the aggregate. All print the same value.
- p-values vs Dyna-Q in group `main` (H1 cum 1.6e-6 and early 0.015; H2 0.025; H3 1.9e-18; H5 0.22, 0.10, 0.56 and early 0.014; abstract 0.014): replaced by `\rhval{cmp/main/.../paired_p}` from `rh compare --group main`. Same values.
- abstract.tex `p<10^{-5}` (Dyna-Q vs Q-learning, static): replaced by the exact value, `\rhval{cmp/main/q-learning/static/cum_reward/paired_p:sci1}` (1.6e-6).
- ablations.tex p-values vs Dyna-Q+ (`p<0.001` shortcut bonus, 0.069, 0.002): replaced by `\rhval{cmp/abl_dynaq_plus/.../paired_p}`; the bound `p<0.001` is now the exact value (6.7e-12).
- ablations.tex p-values vs Dyna-Q (`p<0.001` twice; 0.30, 0.16, 0.13): came from a hand-renamed CSV (`..._refDynaQ.csv`) the registry check does not read. The Dyna-Q and "w/o untried" rows of `abl_dynaq_plus` are now listed in group `abl_ref_dynaq` (`rh log --from-run`) and compared with `rh compare --group abl_ref_dynaq --metric post_reward --ref Dyna-Q`; text uses `\rhval{cmp/abl_ref_dynaq/...}`. Trends print the same (0.30, 0.16, 0.13); the two bounds are now exact (7.0e-6 static, 1.3e-4 stochastic).
- abstract.tex `p<0.001 against Dyna-Q+ and against Dyna-Q`: replaced by the larger of the two p-values of each comparison, by key (`p <= 4.4e-4` against Dyna-Q+, `p <= 1.3e-4` against Dyna-Q).
- H4 p-values vs Q-learning on the stochastic maze (0.007 at n=1; 0.44 and 0.14 at n=50, 100; abstract and results.tex): were computed by `method/tests_stochastic.py` outside the harness. The Dyna-Q runs at each n and the Q-learning runs of seeds 0-9 are now listed in groups `h4_n1`, `h4_n50`, `h4_n100` (`rh log --from-run`) and compared with `rh compare --group h4_n<n> --metric cum_reward --ref Q-learning`; text uses `\rhval{cmp/h4_n<n>/dyna-q/stochastic/cum_reward/paired_p}`. Same values. The file reference `tests_stochastic_n.csv` was replaced by "`rh compare` on the same runs".
- H4 `paired p=0.0016, n=1 versus 100` (abstract and results.tex): DELETED. `rh compare` compares systems by name and cannot pair one system at two values of n, so this p-value has no registry source. The sentence keeps the fall of the means (92.4 to 39.6, Table II), which is what it described.
- H2 "between roughly 18 and 30 for n>=5": replaced by the two means by key (17.8 at n=20, 29.6 at n=50).
- H5 "standard deviations of 40--50 goals": replaced by the smallest and largest of the standard deviations in question by key (38.8 and 50.0).

## Text that disagreed with the registry (registry wins)
- results.tex H4, standard deviation of Q-learning's cumulative reward on the stochastic maze, seeds 0-9: text said 33.6, registry value is 33.547, which prints as 33.5. Corrected through `\rhval{sweep_n/q-learning/stochastic/cum_reward/std:1}`. The statement it supports (gaps of 9.6 and 15.8 are within one standard deviation) is unaffected.

## Setup constants declared (`rh const add`), and written as `\rhval{const/...}` where they appear as plain numbers
- `grid_rows` 6, `grid_cols` 9 (maze size); `horizon_steps` 3000, `shortcut_horizon_steps` 6000 (T); `blocking_change_step` 1000, `shortcut_change_step` 3000; `reward_window_steps` 500 (early/late windows); `slip_prob` 0.3; `alpha` 0.5, `gamma` 0.95, `epsilon` 0.1, `kappa_default` 0.001, `theta` 0.0001 (hyperparameters, defaults of `method/run.py`).
- Left as literals: `100` (largest n; a run setting, `--n 100`), `0.01`, `10^{-2}`, `3*10^{-2}`, `10^{-3}`, `10^{-4}` (kappa values of the sweep, run settings; theta and the default kappa are also declared). The tracer lists the first value-match for these, which can be an unrelated aggregate; they are settings, not results.

## Only real runs
- No hand-logged row existed (0 of 1851 rows without a command, none flagged `hand_logged`), so no run had to be replaced. The 360 rows added by `rh log --from-run` carry the command, log and config of the run they copy (`provenance.copied_from`); no `rh run` was needed and no new experiment was run.

## Reproducible metrics
- `research.yaml`: `runtime_s` marked `nondeterministic: true` (wall-clock time). No result metric is marked.
- Checked: all 1851 logged commands were executed again (outputs to /tmp, nothing logged); every result metric (`cum_reward`, `pre_reward`, `post_reward`, `early_reward`, `late_reward`, `first_goal_step`) matched the registry exactly in all 1851. All randomness comes from `random.Random(seed)`; no unseeded randomness was found.

## Byline, length, wording
- `paper/sections/author.tex`: not edited (the platform's rewrite is committed as found).
- 6 pages. No "state of the art" or "novel" in the paper.

## Other
- setup.tex: the sentence on table conventions now says tables show the mean with the standard deviation where stated, figures show mean +/- standard error, sweep-table Q-learning/Dyna-Q columns are the main-comparison runs of seeds 0-9, and tests come from `rh compare`.
- results.tex H1: "the 500-step gap" reworded to "the gap over the first 500 steps" so the constant can be keyed.
- `rh paper build` added the `\input{generated/values}` line to `paper/main.tex`; `paper/generated/values.tex` and `paper/number_trace.json` are new. The three sweep figures were regenerated by `method/analyze.py` from the same runs (no data change).
- `method/tests_stochastic.py`, `results/tables/tests_stochastic_n.csv`, `..._refDynaQ.csv` and `results/RESULTS.md` are kept as history; the paper no longer draws on them (README note added). `results/RESULTS.md` still quotes the deleted p=0.0016.
