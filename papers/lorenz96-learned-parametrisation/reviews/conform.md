# Conformance report: numbers traced, constants declared

No claim, hypothesis verdict or experiment was changed. No new run was logged. One line per change.

## Constants declared (`rh const add`; setup facts, not results)
- 256 (abstract): declared `n_fast_variables` = 256, the number of fast variables K*J = 8*32.
- 400 (method, setup, results, limitations): declared `free_run_length` = 400, the length of each free run in model time units (`method/run.py`, `T = 400.0`).
- 1024 (method): declared `mlp_batch_size` = 1024, the MLP minibatch size (`method/run.py`).

## Numbers removed
- 394 and 552 (setup): harness wall-clock durations of two MLP runs, held only in run provenance and not a metric; deleted the parenthetical "(394 s and 552 s as timed by the harness)". The in-process times 390 s and 549 s (logged `runtime_s`) stay.

## Hand-computed table rows removed (3-seed subsets of the 5-seed main group)
These rows were means over seeds 0-2 of main-group runs, computed by `experiments/analysis.py`; the registry has no such statistic. `rh numbers` flagged only 1.250 and 1.403, but every number in these rows was a subset mean (the others were matched to unrelated registry values by coincidence), so the whole rows were removed. `experiments/analysis.py` now writes only whole ablation groups; tables regenerated.
- Table `ar1_matched`: removed rows "Deterministic (sigma=0)" (1.372, 0.961, 0.229, 0.137) and "AR(1) fitted (sigma x1)" (1.250, 0.998, 0.083, 0.057).
- Table `degree`: removed row "Degree 4" (0.847, 1.372, 0.222, 0.229, 0.137).
- Table `mlp_in`: removed row "Local X_k" (0.849, 1.403, 0.209, 0.217, 0.124).
- Table `shift`: removed the three "20 (trained)" rows (1.372/1.403/1.250 and their climate columns).
- The four captions now point to the main table (five seeds) for these systems.

## Prose numbers that quoted those subset means: replaced by the registry value (`\rhval`, main group, 5 seeds)
The registry wins, so the text now gives the 5-seed main-group mean and says the ablation comparison (3 seeds) is not seed-matched. The direction of every comparison is unchanged.
- ablations, fitted AR(1) spec_err 0.057 (twice) -> `\rhval{main/ar-1-stochastic/f20_c10/spec_err/mean}` (0.05629).
- ablations, deterministic spec_err 0.137 -> `\rhval{main/polynomial-deg-4/f20_c10/spec_err/mean}` (0.1435).
- ablations, fitted AR(1) valid time 1.250 (twice) -> `\rhval{main/ar-1-stochastic/f20_c10/valid_time/mean}` (1.252).
- ablations, fitted AR(1) variance ratio 0.998 -> `\rhval{main/ar-1-stochastic/f20_c10/var_ratio/mean}` (0.9979).
- ablations, no-noise valid time 1.372 -> `\rhval{main/polynomial-deg-4/f20_c10/valid_time/mean}` (1.398).
- ablations, "degrees 4--6 are at 0.105--0.137" -> degrees 5 and 6 at 0.105 and 0.109 (generated table), degree 4 at `\rhval{main/polynomial-deg-4/f20_c10/spec_err/mean}` (0.1435).
- ablations, the R^2 and valid-time ranges over degree (0.791 to 0.848, 1.199 to 1.394) are unchanged but now stated for the ablation degrees 1, 2, 3, 5, 6 only (the 5-seed degree-4 valid time, 1.398, is not seed-matched and is not part of that trend statement).
- ablations, local-MLP offline R^2 0.849 -> `\rhval{main/mlp-32x2/f20_c10/offline_r2/mean}` (0.8497).
- ablations, local-MLP spec_err 0.124 -> `\rhval{main/mlp-32x2/f20_c10/spec_err/mean}` (0.1375).
- ablations, local-MLP mean_err 0.209 -> `\rhval{main/mlp-32x2/f20_c10/mean_err/mean}` (0.2372).
- ablations, local-MLP valid time 1.403 -> `\rhval{main/mlp-32x2/f20_c10/valid_time/mean}` (1.421).
- results (H4), polynomial w1_pdf at F=20 0.229 -> `\rhval{main/polynomial-deg-4/f20_c10/w1_pdf/mean}` (0.2427).

## Hand-typed p-values replaced by `\rhval` (values of `rh compare`, reference Polynomial (deg 4)); none disagreed with the registry, they were rounded copies
- results H2: var_err p 1.7e-4 -> `cmp/main/ar-1-stochastic/f20_c10/var_err/welch_p` (0.0001695).
- results H2: spec_err p 5.6e-4 -> `cmp/main/ar-1-stochastic/f20_c10/spec_err/welch_p` (0.0005618).
- results H2: spec_err p 0.33 (c=4) -> `cmp/main/ar-1-stochastic/f20_c4/spec_err/welch_p` (0.3292).
- results H2: var_err p 0.11 (c=4) -> `cmp/main/ar-1-stochastic/f20_c4/var_err/welch_p` (0.1106).
- results H2: valid_time p 2.9e-4 -> `cmp/main/ar-1-stochastic/f20_c10/valid_time/welch_p` (0.0002893).
- results H2: valid_time p 8.1e-5 (c=4) -> `cmp/main/ar-1-stochastic/f20_c4/valid_time/welch_p` (8.141e-5).
- results H3: valid_time p 0.36 -> `cmp/main/mlp-32x2/f20_c10/valid_time/welch_p` (0.3608).
- results H3: spec_err p 0.67 -> `cmp/main/mlp-32x2/f20_c10/spec_err/welch_p` (0.6665).
- results H3: valid_time p 0.92 (c=4) -> `cmp/main/mlp-32x2/f20_c4/valid_time/welch_p` (0.9246).
- results H3: paired p 0.051 -> `cmp/main/mlp-32x2/f20_c10/valid_time/paired_p` (0.05077).
- results H1: the bound "p < 10^-6" is kept as written; `rh numbers` traces it to the largest of the six Welch p-values (No closure vs AR(1), F20_c4, 8.897e-7).
- `results/tables/compare_main_valid_time.csv` was rewritten by `rh compare --group main --metric valid_time --ref "Polynomial (deg 4)"`. The `cmp/.../valid_time/...` keys carry no reference name and follow the last `rh compare` of that metric, so this file must stay on the polynomial reference; rerunning `rh compare --metric valid_time` with another reference would change the six valid-time p-values printed in H2 and H3.
- `paper/main.tex`: added `\input{generated/values}` so `\rhval` resolves.

## Only real runs count
- Checked all 124 `ok` rows of `results/runs.jsonl`: every one has a logged command (`rh run`); none was logged by hand. Nothing to replace.

## Reproducible metrics
- `research.yaml`: added `runtime_s: {higher_is_better: false, nondeterministic: true}` (the only wall-clock metric the runs log). No result metric is marked nondeterministic.
- Evidence that result metrics are reproducible from the seed: 19 commands appear more than once in the registry (the forcing-shift runs and their superseded copies, 12 of them MLP runs); only `runtime_s` differs between copies. In addition, the main-group MLP and AR(1) runs (F20_c10, seed 0) were executed again to `/tmp` (not logged): all metrics equal the registry to the last digit except `runtime_s`. All random streams are seeded (`numpy` generators and `torch.manual_seed` from `--seed`); I found no unseeded randomness. This was checked on this machine only (CPU, 2 torch threads); bit-identity of the MLP runs on other hardware or library versions was not tested.

## Not changed
- `paper/sections/author.tex`: not edited (platform's version kept).
- Wording: no "state of the art" or "novel" in the paper. Length: 6 pages.
- Figure `tradeoff.pdf` still plots seeds 0-2 means for every configuration, including main-group systems, as its caption states; figures were regenerated by `experiments/analysis.py` with the same data (`degree_sweep.pdf` is not used in the paper).
- `rh const add` rewrote `research.yaml` in block style; apart from the `runtime_s` line and the `constants:` block the content is the same.
- `rh check` prints READY with one pre-existing warning (verdict tier 0 < target 2: the method is not best on valid_time), which the paper already reports.
