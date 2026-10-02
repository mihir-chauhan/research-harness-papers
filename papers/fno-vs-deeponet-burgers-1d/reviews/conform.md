# Conform report: numbers traced, constants declared

Scope: bring the paper into line with the platform rules without changing what it claims. No new training run was logged. Final state: `rh paper build` BUILD OK (6 pages), `rh lit verify` CITATIONS VERIFIED, `rh numbers` 342 checked / 0 untraced, `rh check` READY (one warning: the 2 failed tuning runs already disclosed in the paper).

## Things a reader should know first

- **Two numbers were removed because no logged run backs them.** The solver self-check values in the setup section (`5e-11` for halving the time step, `1e-8` for grid agreement) come from `python method/data.py`, which was never run through `rh run`. They are not setup facts, so I did not declare them as constants. The sentence now says the checks were run outside the registry and quotes no value. I re-ran the script unlogged to confirm the sentence is still true (it printed 5.0e-11, 3.8e-15 and 2.7e-9); those values are not in the paper. Logging the self-check with `rh run` would restore them, but that is a new registry row and I left it for you to decide.
- **One logged number is new in the text.** To keep the "all grids resolve the solution" statement backed by the registry, the setup section now quotes the metric `interp_floor_256` (already logged with every run, never cited before) through `\rhval`. It supports an existing claim; it is not a new claim, but it is a number the earlier version did not print.
- **The zero-shot ratio table is gone, and with it the factors 2.55 and 3.27.** A ratio of two metrics per seed is not a statistic the registry computes, and `rh compare` compares systems, not metrics. The H2 verdict is unchanged and is now stated with traced values: CNN mean error at 128, 256 and 512 points, plus its smallest per-seed 256-point error against its largest per-seed 128-point error.
- **Eight derived cells of the ablation table are now "--".** `rh compare` stores one reference system per group. In `sweep_ntrain` the reference is FNO and in `sweep_epochs` it is MLP, so the DeepONet rows (n=100, n=200, 500 epochs, 2000 epochs) no longer show a change and a Welch p against the DeepONet default. No sentence in the paper cited those eight cells; the means and standard deviations of the rows are unchanged.
- **No number in the text disagreed with the registry.** Every `rh compare` value matches what the hand-built table showed (Welch p 0.013, 0.897, 0.959, 0.279, 0.004, 0.001, 0.314, 0.145).
- **The tracer is permissive.** Before this pass it had "traced" several hand-derived numbers to unrelated statistics by coincidence (for example the Welch p 0.314 to a median training error, "36%" to a DeepONet training error). I replaced those by meaning, not only the 72 it listed. It still attributes some declared setup facts (128, 100, 1.5, 10%) to coincidental run statistics instead of the declared constant; I cannot change which source it picks.

## Rule 1: numbers

Declared constants (`rh const add`), all setup facts:

- `nu` 0.01: viscosity of the task.
- `grid_train` 128, `grid_fine_2x` 256, `grid_fine_4x` 512: training grid and the two zero-shot grids (512 is also the solver grid). Covers 256/512 in abstract, setup, results, conclusion and the main table header.
- `mlp_hidden_width` 512: the MLP layer sizes in the method section.
- `n_train` 400, `n_val` 100, `n_test` 100, `n_pool` 600: data split. Covers 400 and 600 in abstract, introduction, setup, results, ablations, limitations, conclusion.
- `data_seed_offset` 1000: generator seed `1000+s` in setup.
- `grad_steps_n200` 1000: "1000 steps at 200 pairs" in ablations (100 epochs x 10 batches, a setting).
- `epochs_main` 100, `tuning_seed` 100, `solver_dt` 1e-3, `weight_decay` 1e-5: training and solver settings.
- `h1_alpha` 0.05, `h1_min_gain` 0.1, `h2_ratio_threshold` 1.5: thresholds of the registered tests.

Numbers replaced with `\rhval`:

- abstract: 0.005, 0.083, 0.22 (FNO, MLP, DeepONet/CNN test error) -> `main/<system>/.../rel_l2/mean`; DeepONet and CNN are now given separately.
- abstract, conclusion: "factors of 2.55 and 3.27" -> CNN mean error at 128, 256 and 512 points (`main/cnn/.../rel_l2{,_256,_512}/mean`).
- results: 0.1314 and 0.1276 (DeepONet at 500 and 2000 epochs) -> `sweep_epochs/deeponet-ep-{500,2000}/.../rel_l2/mean`.
- results H2: "FNO ratio is 1.00 ... CNN ratio exceeds 1.5 (ratio table)" -> CNN means plus `main/cnn/.../rel_l2_256/min` and `main/cnn/.../rel_l2/max`; reference moved to the main table.
- results H2: "their ratio is 1.00" (MLP, DeepONet) -> "their error does not grow on the finer grids (main table)".
- results, failure cases: "more than three times its own training-grid error" -> the three CNN means; "errors above 0.2" -> DeepONet and CNN means.
- setup: "validation error of about 1" -> `tune/tune-{cnn,deeponet}@lr=0.01/.../rel_l2_val/mean`.
- setup: "differ by less than 2e-4" -> the two MLP validation errors (`tune/tune-mlp@lr=0.001` and `@lr=0.003`).
- setup: solver self-check values 5e-11 and 1e-8 -> removed (see above); `interp_floor_256` added.
- ablations H3: "about 1%" -> `cmp/sweep_modes/fno-modes-8/.../rel_delta:pct1` (0.9%); "36% worse" -> `cmp/sweep_modes/fno-modes-4/.../inv_ratio:2` (1.36 times).
- ablations H4: "about threefold" -> `cmp/sweep_ntrain/fno-n-100/.../inv_ratio:1` (3.3 times).
- ablations, training length: "by about 40%" -> DeepONet means at 100, 500 and 2000 epochs; "training error halves, to about a third of the test error" -> the two training-error means.
- ablations: Welch p 0.314 and 0.145 -> `cmp/sweep_epochs/mlp-ep-{500,2000}/.../welch_p:3`.

Tables:

- Ablation table (`generated/ablsum.tex`, written by `experiments/make_figs.py` with its own Welch test): replaced by a table in `paper/sections/ablations.tex` made only of `\rhval` keys. The "change" column (+36%, -1%, ...) is now "ratio" (1.36, 0.99, ...), from `rh compare`.
- Ratio table (`generated/ratios.tex`): deleted, together with its caption and both references.
- Main table (`generated/maintab.tex`): parameter counts written as `139745` instead of `139\,745`, which the tracer read as two numbers (139 and 745). Values unchanged.
- `experiments/make_figs.py`: the code that computed ratios, percentage changes and p-values is removed; figures and the other tables are regenerated with identical values.
- `results/tables/ablsum.tex`, `ablsum.md`, `ratios.tex`: deleted. Pointers in `results/RESULTS.md`, `results/VERDICT.md` and `experiments/PROTOCOL.md` updated; the hand-derived 2.55/3.27 and 36% in `RESULTS.md` replaced by registry values.

Registry changes made to get those `rh compare` values:

- 18 rows added with `rh log --from-run`: the seed 0-2 default runs of FNO (into `sweep_modes`, `abl_grid`, `sweep_ntrain`), DeepONet (into `sweep_ntrain`, `sweep_epochs`) and MLP (into `sweep_epochs`). Each copy keeps the original command and metrics and records `copied_from`. No metric was typed.
- `rh compare --metric rel_l2` run for `sweep_modes`, `abl_grid`, `sweep_ntrain` (reference FNO) and `sweep_epochs` (reference MLP).
- `rh verdict` was not re-run, so `results/VERDICT.md` is the earlier file with an updated note. In a scratch copy it still gives tier 2 with the copies present.

## Rule 2: only real runs

- All 74 rows that existed before this pass carry a command, an exit code and a log; none was logged by hand, so nothing had to be re-run.
- The 18 new rows are copies made by `rh log --from-run`, not real runs. The paper uses them only as the default rows of the ablation table and as the reference in `rh compare`; each points to the real run it copies.
- The only values the paper used without a logged run were the two solver self-check numbers; the paper no longer uses them.

## Rule 3: reproducible metrics

- `research.yaml`: `train_s` marked `nondeterministic: true`. It is the only wall-clock metric. No result metric is marked.
- Seeding: `method/run.py` seeds torch and numpy from `--seed`, the data generator uses `default_rng(1000 + seed)`, and the thread count is fixed at 2. There is no unseeded randomness.
- Checked by re-running four logged runs outside the registry, in a scratch copy with the data cache deleted so the solver also ran again: main-group DeepONet, MLP, FNO and CNN, seed 0. All eight result metrics matched the registry to the last digit in all four; only `train_s` differed.
- Limit of that check: same machine, same environment. I did not test another machine or thread count.

## Rule 4: byline

- `paper/sections/author.tex` not edited. It shows as modified in git because the platform rewrote it; that change is committed as found.

## Rule 5: length and wording

- 6 pages (minimum 4). Neither "state of the art" nor "novel" occurs in the paper.
