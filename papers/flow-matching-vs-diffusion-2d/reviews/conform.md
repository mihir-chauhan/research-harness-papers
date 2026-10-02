# Conformance report: numbers traced, constants declared

No claim, experiment or run was added. Final state: `rh paper build` BUILD OK (7 pages), `rh lit verify` CITATIONS VERIFIED,
`rh numbers` 721 checked / 721 traced / 0 untraced, `rh check` READY (one pre-existing warning: verdict tier 0 < target 2).

## Rule 1: every number is traced

Setup facts declared with `rh const add` (never results):
- 10000 (abstract, method, setup, results caption): declared `n_eval_points`.
- 3000 updates (abstract, introduction, setup, limitations): declared `train_updates`.
- 3000 MMD points (method, limitations): declared `mmd_points`.
- 5000 (setup, the update count planned before the budget cut): declared `train_updates_first_plan`.
- 512 (setup): declared `batch_size`.
- 128 (method, limitations): declared `mlp_width`.
- 1000 (method, T): declared `diffusion_timesteps`.
- 20000 (method, setup, results, limitations): declared `reflow_pairs`.
- 256 (method, limitations): declared `sw_directions`.
- 2000 (method, straightness samples): declared `straightness_samples`.
- 100 (largest K, teacher steps, straightness path length; all sections): declared `max_sampling_steps`.
- 2e-3, 0.999, 1e-4, 0.02, 0.008, 0.999 (method/setup hyper-parameters): declared `learning_rate`, `ema_decay`, `beta_min`, `beta_max`, `cosine_offset`, `cosine_beta_clip`.
- 0.1, 0.3 (MMD bandwidths), 0.1 (eight Gaussians std), 0.05 (two moons noise), 0.05 (alpha), 4e-5 (cosine start threshold): declared `mmd_bandwidth_1`, `mmd_bandwidth_2`, `eight_gaussians_std`, `two_moons_noise`, `test_alpha`, `cosine_start_alpha_bar`.
- Note: the tracer had matched these hyper-parameters, and many hand-typed results, to unrelated registry values of the same rounded size. Some declared constants are still listed by `rh numbers` under such an aggregate, because the tracer prefers an aggregate to a constant; each is a setup fact and is declared.

Derived numbers and hand-typed results:
- `rh compare` was run for group main: reference Flow Matching (Euler) for sw_k1, sw_k100, mmd_k1, straight; reference DDIM for sw_k4, mmd_k4. The 18 earlier per-task CSVs (`compare_main_<metric>_<task>.csv`) were deleted: the tracer does not read renamed files, so no comparison statistic was traceable before.
- Tests table (was `generated/tests_all.tex`, written by experiments/analyze.py; untraced 1.192, 0.899, 0.549, 0.252): replaced by `sections/tests_table.tex`, every cell a `\rhval{cmp/...}` delta, ratio or paired p. Differences are now "reference minus other" as `rh compare` reports them, so the H1, H3, MMD@4 and ancestral rows changed sign and label (e.g. "FM-DDIM -0.202" is now "DDIM-FM 0.202"); the values are the same. p values are printed as numbers, no longer as "<0.001".
- Tests table, 4 Heun equal-evaluation rows (Heun@4-Euler@8, Heun@4-DDIM@8, Heun@2-Euler@4, Heun@1-Euler@2): deleted. They compare two different metrics; `rh compare` cannot produce them.
- Tests table, 4 reflow-ablation rows (Reflow-2 and Teacher-4 against Reflow-1 on seeds 0-2): deleted. They pair across run groups; `rh compare` cannot produce them.
- Abstract, "within 0.020 of the real-data floor": hand-computed difference deleted; replaced by the two registry means on eight Gaussians (`\rhval`).
- Results H1: 0.013, 0.203, 0.263, 0.0145, 0.0252, 0.329 +/- 0.015, 0.288 +/- 0.043, 0.0087 and all p thresholds replaced by `\rhval` (means, stds, compare deltas, paired p). "p <= 0.001 on each task" for MMD@4 is now the three paired p values; the eight Gaussians one is 0.0011 in the registry, so the bound was slightly too tight and is corrected.
- Results H2: 0.77, 1.25, 0.057 +/- 0.028, 0.027 +/- 0.005, 0.086, 0.006, 0.048, 0.053 +/- 0.002, 0.031 +/- 0.003 replaced by `\rhval`; the 0.006 gap is now the signed FM-DDIM delta.
- Results H3: 0.042, 1.234, 0.0016, 0.0005 replaced by `\rhval`; "at most 0.0012 ... p<0.05" replaced by the three compare deltas and paired p values; "within 0.025 SW of the floor at every K" (hand-computed bound) deleted, sentence now says "stays close to the real-data floor".
- Results H4: the six straightness means replaced by `\rhval`; "0.9988 or more" replaced by the three Reflow-1 means; "p<0.001" replaced by the largest paired p.
- Results Heun paragraph: all means replaced by `\rhval`; the p values (two "<0.001", 0.034, 0.066) deleted with their table rows. "Not significantly on eight Gaussians (p=0.066)" became "we do not claim a reliable difference there", with the DDIM mean and std from the registry.
- Ablations: 0.054, 0.048, 0.074 replaced by `\rhval`; "above 0.99" replaced by the three straightness means; "worse by 0.05 to 0.24", "at most 0.009", "p<0.05 on all tasks", "at most 0.0003" deleted with their table rows and replaced by registry means of the ablation and of Reflow-1, stated as a comparison of table means (seeds 0-2 against 0-4).
- Limitations: floor range 0.014 to 0.022 replaced by `\rhval`; "four or two degrees of freedom" is now "four", since the three-seed paired tests are no longer reported; added that the Heun and reflow-ablation comparisons carry no paired test.
- Setup and results intro: tests are now attributed to `rh compare`, not to experiments/analyze.py.
- Text against registry: no reported value disagreed with the registry beyond the MMD@4 p bound above. Run times "3 to 54 s" and "35 minutes" match the `rh run` durations and timestamps in the registry.
- Housekeeping: analyze.py now writes its own test tables to `results/analysis/` so `rh paper sync` no longer copies them into `paper/generated/`; `experiments/make_tables.sh` and `results/RESULTS.md` updated to match. `main.tex` gained the `\input{generated/values}` line added by `rh paper build`.

## Rule 2: only real runs
- All 127 registry rows have a command behind them (`rh run`); none was logged by hand. No run was needed and none was made.

## Rule 3: reproducible metrics
- `train_plus_eval_s` (wall-clock): marked `nondeterministic: true` in research.yaml. No result metric is marked.
- Check made: three logged runs (DDIM two_moons seed 3, Reflow-1 checkerboard seed 1, FM-Heun eight_gaussians seed 2) were run again from scratch outside the workspace (no cached checkpoint, nothing logged). All 17 result metrics matched the registry to the last digit; only `train_plus_eval_s` differed. All randomness in method/run.py is seeded. This was checked on this machine only.

## Rule 4: byline
- `paper/sections/author.tex` not edited; the platform's rewrite is committed as found.

## Rule 5: length and wording
- 7 pages. No "state of the art" and no "novel" in the paper; nothing changed.
