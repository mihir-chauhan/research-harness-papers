# Conformance report: numbers traced, constants declared

No claim, hypothesis verdict or experiment changed. `rh numbers`: 264 checked, 264 traced, 0 untraced. `rh check`: READY. Paper: 5 pages.

## Rule 1: numbers
- 1797 (dataset size, setup; intro said "about 1800"): declared constant `dataset_images`; intro now says 1797.
- 497 (test split), 1300 (unlabeled pool): declared constants `test_split_images`, `unlabeled_pool_images` (checked against `get_split` for seeds 0-4).
- 200 (largest label budget; abstract, intro, setup, results, conclusion): declared constant `label_budget_max`.
- 256 (encoder feature dimension), 128 (projection hidden width; pretraining batch size), 300 (supervised steps): declared constants `encoder_feature_dim`, `projection_hidden_dim`, `pretrain_batch_size`, `supervised_steps`.
- 10^-3 (learning rate), 10^-5 and 10^-4 (weight decays), tau = 0.5, scale 10%, brightness 0.2, noise sigma 0.1: declared constants `pretrain_lr`, `pretrain_weight_decay`, `supervised_weight_decay`, `simclr_temperature_default`, `aug_scale_range`, `aug_brightness_range`, `aug_noise_sigma`. They were "traced" before only because unrelated registry values happened to round to them.
- 236 (raw registry rows before de-duplication): declared constant `raw_registry_rows` (line count of `results/runs_raw_with_duplicates.jsonl`).
- 161 ("rows kept"): deleted; the registry now has more rows (comparison-group copies, below), so the count no longer describes it.
- 160 ("All 160 runs"): replaced by the per-group counts `\rhval{count/<group>/runs}` (main 90, abl_aug 30, abl_supaug 15, sweep_tau 15, sweep_epochs 10) and a sentence saying the cmp_* rows are copies, not additional runs.
- 792 s (slowest rotation run, seed 1, n50): DISAGREED WITH THE REGISTRY. 792.4 s is the harness wall-clock of the whole command; the run's logged `seconds` metric is 787 s. Text now uses `\rhval{run/c65513a19f/seconds:0}` (787 s).
- "about 52 minutes" total wall-clock: number deleted (I had computed it from registry timestamps; `rh` records no such value). The sentence still says the total exceeded the 45-minute plan.
- Table "Additional paired comparisons" (`generated/stats_extra.tex`, 24 rows, 48 numbers computed by my own script `method/stats_extra.py`): every cell replaced by `\rhval{cmp/cmp_*/.../delta:3}` and `.../paired_p:3` from `rh compare`. To let `rh compare` pair systems across groups, the existing runs were listed again in four groups (`cmp_aug`, `cmp_supaug`, `cmp_rotation`, `cmp_random`; 180 rows) with `rh log --from-run` (copies of metrics and provenance; nothing typed, nothing re-run; `experiments/make_cmp_groups.py`). All 48 values equal the previous table at three decimals. The two augmentation-ablation blocks are now printed as "SimCLR-style probe minus ablation" (positive drops) because `rh compare` reports reference minus system.
- "A wins" column of that table, and "0/5 seeds higher" / "3/5 seeds" in the ablation text: deleted (seed-win counts were computed by my script; `rh` has no such statistic).
- Table "SimCLR-style probe minus baseline" (`generated/stats_main.tex`, 45 numbers reformatted by `method/stats_table.py`): cells replaced by `\rhval{cmp/main/.../delta:3 | paired_p:4 | cohen_d:1}`; same values.
- Abstract: p = 0.18 (SimCLR vs scratch, n200), p = 0.003 and -0.028 / p = 0.09 (augmentation ablations at n50), 0.963 vs 0.955 (tau sweep): replaced by `\rhval` keys; values unchanged. (0.18, 0.003, 0.09 and 0.028 had been "traced" to unrelated timing and loss statistics.)
- Results: 0.002 / p = 0.18, 0.164, 0.037 (SimCLR minus scratch); p = 0.02, 0.004, 0.09 (rotation vs random encoder); p = 0.05, 0.10 (rotation vs PCA); 0.321, 0.135, 0.065 (SimCLR minus PCA); 0.441 vs 0.505; +-0.118; p = 0.12 (random encoder vs pixels, n50): replaced by `\rhval` keys; values unchanged.
- Ablations: 0.955, 0.927, 0.918; drops 0.028 (p = 0.09) and 0.037 (p = 0.003); std 0.116; 0.713 vs 0.662, std 0.099, p = 0.12; p = 0.02; 0.963, 0.955, 0.942: replaced by `\rhval` keys; values unchanged ("lower values (0.942)" now prints both tau = 0.1 and tau = 0.2 means, each 0.942).
- "10 epochs costs about 0.015 compared with 60": the hand-computed difference was deleted; the sentence now gives the two means, `\rhval` 0.940 (10 epochs) against 0.955 (60 epochs). 30 epochs: `\rhval` 0.955.
- `paper/main.tex`: `rh paper build` added the `\input{generated/values}` line.

## Rule 2: real runs
- No hand-logged row: all 160 original ok rows have the `rh run` command and log. The 180 new cmp_* rows are `rh log --from-run` copies carrying the command and log of the run they copy. No run was replaced.

## Rule 3: reproducible metrics
- `research.yaml` `metrics.seconds`: added with `nondeterministic: true` (wall-clock). No result metric is marked.
- Reproducibility test (re-ran the logged commands in a clean /tmp directory, nothing logged): Pixels + LR, PCA + LR, Random CNN, Supervised scratch, SimCLR and Rotation at n50 seed 0, Supervised + aug at n10 seed 3, and SimCLR n200 seed 0 both with and without the encoder cache. `test_acc`, `train_acc` and `pretrain_loss` matched the registry to the last digit in all 9 re-runs (22 values); only `seconds` differed. All randomness in `method/run.py` is seeded; I found no unseeded source.
- Caveat, not hidden: SimCLR and rotation rows for n10 and n200 (and their ablation counterparts) loaded the encoder cached by the n50 run of the same seed (`results/cache/`, not committed), so their recorded durations are a few seconds. Without the cache the same command pretrains again and gives the same metrics, but takes about 40-80 s on this machine instead of the recorded few seconds.
- I could not dry-run the platform's own re-execution from this session (its sandbox does not start inside mine: `sandbox_apply: Operation not permitted`); the evidence above is from my own re-runs.

## Rule 4: byline
- `paper/sections/author.tex`: not edited (the platform's version is committed as it was found).

## Rule 5: length and wording
- 5 pages. No "state of the art", no "novel" in the paper; no wording change needed.

## Final checks
- `rh paper build`: BUILD OK. `rh lit verify`: CITATIONS VERIFIED (11/11). `rh numbers`: ALL NUMBERS TRACED. `rh check`: READY (two warnings unchanged from before: one failed sanity run in the registry; verdict tier 1 < target 2 because n200 is not significant, which the paper states).
