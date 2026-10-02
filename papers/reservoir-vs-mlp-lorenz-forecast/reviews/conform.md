# Conformance report: numbers traced, constants declared

No claim, hypothesis verdict or experiment changed. No new experiment was run and no metric was typed. `rh numbers`
went from 19 untraced numbers to 0 (617 checked). One line per change below.

## Registry: runs listed in further groups (`rh log --from-run`, copies of existing run records; `analysis/list_copies.py`)

- `sweep_rho`, `sweep_size`: the ESN main runs of seeds 0-2 listed as the default point (rho 0.4, N 500). Traces 2.04 (and the rest of the default rows) in Table VII, which the analysis script used to compute from a 3-seed subset of group `main`.
- `sweep_ntrain`: the ESN, MLP and GRU main runs of seeds 0-2 listed as the 5000-sample row. Traces 2.04 in Table IV.
- `sweep_steps`: the MLP and GRU main runs of seeds 0-2 listed as the tuned-budget rows. Traces the fit times 28.5, 56.5, 62.5 in Table V.
- `abl_gru` (new group): GRU and GRU without input noise, 5 seeds, so that `rh compare --ref GRU` makes this comparison. Traces p=0.657 (Table III and ablation text).
- `nt500`, `nt2000`, `nt5000`, `nt10000` (new groups): ESN and MLP at one training length, seeds 0-2, for `rh compare --ref ESN`. Traces Delta=4.05 and p=0.228 (Table IV, results text).
- `st_mlp4000`, `st_mlp8000`, `st_mlp16000`, `st_mlp32000`, `st_gru3000`, `st_gru6000`, `st_gru12000` (new groups): the ESN next to one baseline at one optimiser budget, seeds 0-2, for `rh compare --ref ESN`. Gives the ESN/system ratios of Table V.
- 194 copy rows in total; each keeps the command, log and metrics of the run it copies. No row in the registry is hand-logged (rule 2: nothing to replace).

## Tables (`analysis/make.py`, `analysis/build.sh`)

- `analysis/make.py` no longer computes any test statistic (the scipy paired tests and the hand-computed ratios are removed); it reads the `rh compare` CSVs only to choose a sign and a number format.
- Table III (`tests.tex`): every difference, A/B ratio and p-value is now `\rhval{cmp/...}`. The GRU-versus-no-noise rows come from group `abl_gru`. Values unchanged; small p-values print as 3.6 x 10^-6 instead of 3.6e-06. The table is scaled to the column width.
- Table IV (`sweep_ntrain.tex`): Delta and p columns are now `\rhval{cmp/nt<N>/...}` (0.228, 4.05 and the other 14 cells). Values unchanged.
- Table V (`sweep_steps.tex`): the column "p against the tuned budget of the same system" is deleted (0.023, 0.348, 0.777 and the other cells): `rh compare` compares systems, not two settings of one system, so the platform cannot recompute these. The tuned row is marked with an asterisk instead. The ESN/sys. column is now `\rhval{cmp/st_.../ratio}`. Values unchanged.
- Table VII top (`sweep_rho.tex`): the hand-computed "max/min" row (4.18, 10.95) is deleted; caption adjusted.
- Stale `results/tables/compare_main_*_refESN.csv` and `*_refGRU.csv` removed (the tracer does not read them; `rh compare` writes `compare_<group>_<metric>.csv`).

## Text: result numbers replaced by `\rhval{<key>}` (99 replacements, each checked against the old literal: 0 differences)

- Abstract: 9.546, 5.578, 3.787, 2.882, 2.115, p=0.018, ratios 2.74 and 1.73 are now `\rhval`.
- Abstract: "varies by a factor 4.18 (Lorenz-63) and 10.95 (Lorenz-96)" replaced by the two seed-means it was computed from ("ranges from 2.32 to 9.70 ... and from 0.21 to 2.30"), all `\rhval`. The best-to-worst ratio was a hand-computed number that no `rh` command records.
- Conclusion: 9.546, 1.71, 2.52, 2.115, 2.882, p=0.018, 2.74, 1.69 are now `\rhval`; "best/worst VPT ratios of 4.18 and 10.95" replaced by the same four seed-means as in the abstract.
- Results, H1: 1.71, 2.52, p=0.002, -0.77, p=0.018, 3.28, 2.72, 0.152, 0.158, 16-29 s are now `\rhval`; "both paired tests give p<10^-4" replaced by the two p-values themselves.
- Results, H2: 0.860, 0.850, 0.810, p=0.654, p=0.704, 2.52, 0.960 are now `\rhval`.
- Results, training length: p=0.228, p=0.372, p=0.016 are now `\rhval{cmp/nt...}`; "p<=0.004" replaced by "the largest of the three paired p-values is 0.004" (`\rhval`; the registry value is 0.0044).
- Ablations, optimiser budget: 3.51, 5.55, 5.68, 3.49, 2.74, 1.69, 1.56 are now `\rhval`. The four same-system p-values (0.015, 0.177, 0.108, 0.100) are deleted with the Table V column; the sentences now say that no significance claim is made for these steps, which is not stronger than "not individually significant".
- Ablations, components: 8.13, 9.55, 0.96, 2.11, 0.84, 0.85, 0.99, 0.01, 1.00, 0.63, 0.86 and p=0.008, 0.002, 0.657, 0.995, 0.205 are now `\rhval`.
- Ablations, spectral radius: "best-to-worst ratio is 4.18 and 10.95, both above 2" replaced by the best and worst seed-means (9.70, 2.30, 2.32, 0.21, `\rhval`) and "the best is more than twice the worst" (H3's registered rule; verdict unchanged). 0.78, 0.87, 0.13, 0.25 are now `\rhval`. "degrades by a factor of four" replaced by "to less than half of its best value".
- Ablations, reservoir size: 9.44, 6.80, 2.62, 0.34, 3.28, 0.85, 0.90 are now `\rhval`.
- Method: the Lyapunov exponents 0.905 and 1.158 are now `\rhval{lyapunov/...}`.
- Setup, Table I (selected hyperparameters, hand-written): every value is now `\rhval{tuning2/.../best_*}`; values unchanged.
- Setup, compute: "about 100 minutes of process time" deleted (a hand-added sum of run durations); the sentence still says the runs exceed the planned 30 minutes.
- Setup, data: "gave metrics identical" now says "the wall-clock training time aside"; the sweep default point is described as a copy of the main run's record.
- Setup: the provenance sentence now names the `rh values` macros and says the analysis script computes no test statistic.

## Text against registry

- No number in the text disagreed with the registry at its printed precision; nothing had to be corrected.

## Constants declared (`rh const add`; all are setup facts read from `method/lib.py`, `method/tune.py`, `research.yaml`)

- Previously untraced: `mlp_hidden_units` 128, `mlp_batch_size` 256, `climate_reference_steps` 15000, `burnin_samples` 200.
- Previously traced only by coincidence with an unrelated recorded value, now declared: `warmup_steps` 100, `rollout_clamp` 1000, `dt_lorenz63` 0.02, `dt_lorenz96` 0.05, `vpt_error_threshold` 0.4, `climate_ok_threshold` 0.1, `climate_run_steps` 10000, `esn_default_size` 500, `validation_seed` 100, `significance_alpha` 0.05, `tuning_grid_rho_mid` 0.9, `tuning_grid_ridge_mid` 1e-6, `tuning_grid_noise_low` 0.01.
- Caveat: the tracer prefers a recorded result over a constant, so several of these literals (for example 0.4, 0.1, 100) still show a result as their source in `paper/number_trace.json`; the declared constant is what they mean.

## Reproducible metrics (rule 3)

- `research.yaml`: `fit_seconds` (training wall-clock) is now `nondeterministic: true`. No other metric is marked. (`rh const add` rewrote the file in block style; content otherwise unchanged.)
- No result metric depends on unseeded randomness: data, model initialisation, minibatch sampling and input noise all use generators seeded from the run's seed, and the ESN spectral radius comes from a dense eigensolver.
- Checked by running seven logged commands again in a copy of the workspace (nothing logged): ESN Lorenz-63 seed 0, ESN Lorenz-96 seed 4, MLP Lorenz-96 seed 0, True system Lorenz-63 seed 1, ESN tuning Lorenz-63, GRU Lorenz-96 seed 0, GRU without input noise Lorenz-63 seed 2. Every metric except `fit_seconds` matched within 1e-6 relative.
- Superseded first-version rows do not reproduce with the current code (they were made with the pre-audit code); they carry status `superseded` and the paper does not use them.

## Other rules

- Byline: `paper/sections/author.tex` is the platform's version, not edited.
- Length: 6 pages. No "state of the art" and no "novel" in the text.
- `paper/main.tex`: `rh paper build` added the `\input{generated/values}` line.
- `results/RESULTS.md`: the H3 ratios and the two H4 p-values that the analysis script no longer computes are removed.
- Left as is: a 12.7 pt overfull box in Table VI (present before); the `rh check` warnings about 10 failed first-version runs and verdict tier 1 (the paper reports H1 as refuted on Lorenz-96).

## Final state

`rh paper build`: BUILD OK. `rh lit verify`: CITATIONS VERIFIED (17 of 17). `rh numbers`: ALL NUMBERS TRACED. `rh check`: READY.
