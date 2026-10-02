# Conformance report: numbers traced, constants declared

Scope: bring the paper into line with the platform rules without changing its claims. No new experiment was logged; the
registry (`results/runs.jsonl`, 241 rows) is unchanged. One line per change.

## Rule 1: every number traced (`rh numbers`: 22 untraced before, 0 after)

Setup facts declared with `rh const add` (research.yaml: `constants`):
- 20,000 (setup.tex): declared `pretrain_sequences`.
- 1000 in "seed 1000+s" (setup.tex): declared `pretrain_data_seed_offset`.
- 2000 in "seed 2000+s", 2000 test/validation sequences, N=2000: declared `adapt_data_seed_offset`, `eval_sequences`, `adapt_set_size` (were passing only by coincidental matches).
- 5000, 7000 (setup.tex): declared `test_data_seed`, `val_data_seed`.
- 10^8 (setup.tex): declared `input_space_size` (10 digit values at 8 positions).
- 4000, batch 128, lr 2e-3 (setup.tex): declared `pretrain_steps`, `pretrain_batch_size`, `pretrain_lr`.
- 128 (method.tex): declared `ff_width`.
- 1500 (setup.tex, limitations.tex): declared `adapt_steps`.
- 500 (setup.tex): declared `curve_eval_sequences`.
- seed 100 (setup.tex), 15% (introduction.tex, results.tex), 0.5 (results.tex, "fail" threshold): declared `tuning_seed`, `h1_param_budget_pct`, `fail_threshold` (were passing only by coincidental matches with unrelated metrics).

Derived numbers replaced by `rh compare` statistics (`\rhval{cmp/...}`) or removed:
- 10.2% (results.tex, conclusion.tex): now `\rhval{cmp/main/lora-r-4/sort_desc/trainable_params/inv_ratio:pct1}` from `rh compare --group main --metric trainable_params --ref "Full fine-tuning"` (new `results/tables/compare_main_trainable_params.csv`).
- 10.2% and 49.3% (abstract.tex): replaced by the traced parameter counts ("7,168 of the 70,016 parameters", "34,496 parameters") so the abstract holds no derived number and no macro.
- 10.2, 20.5 and the rest of the "% full" column (tab_rank): now `\rhval{cmp/main/<system>/reverse/trainable_params/inv_ratio:pct1}`.
- "4.8 times LoRA r=4" (results.tex, H4): hand-computed ratio removed; the sentence now gives the two traced counts (34,496 against 7,168).
- +0.0003, p=0.816, -0.0007, p=0.374 (results.tex, H1): now `\rhval{cmp/main/full-fine-tuning/<task>/adapt_acc/delta|paired_p}`; same values.
- +0.031, p=0.0008 (results.tex, H4): now `\rhval{cmp/main/last-block/sort_desc/adapt_acc/delta|paired_p}`; same values.
- 0.0190 / "0.019 (paired p=0.0037)" and 0.1419 / "p=0.52", LoRA r=1 versus r=8 (tab_tests rows, results.tex H2): `rh compare` keeps one reference system per metric (LoRA r=4), so this hand-computed pair has no registry statistic. The two table rows were deleted and the two sentences now quote the `rh compare` statistics of rank 1 against rank 4 (0.018, paired p=0.0033 on descending sort; p=0.37 on reversal). The H2 verdict is unchanged (supported on descending sort, not interpretable on reversal), but the quoted test is now r=1 vs r=4, not r=1 vs r=8.
- 0.026, gap between all-linear and {q,v} at rank 4 (ablations.tex): hand-computed difference across two groups, deleted; the sentence keeps the parameter counts.
- "p>0.05 for all four comparisons" of LoRA r=1,4 with full fine-tuning at N=100/300 (ablations.tex) and the wording that depended on it ("no test is significant" in abstract.tex, "also not significant" in ablations.tex, "non-significant" in conclusion.tex): these p-values were computed by hand outside `rh compare`, which cannot pair runs within one value of N. The statements were removed; the text now says that no significance test is reported for these comparisons. The conclusion ("inconclusive", no ordering claimed) is unchanged.
- 350, 500, 550 and the 0.9 threshold (ablations.tex, adaptation speed): read off the curve CSVs, not in the registry; removed. The sentence keeps the qualitative order shown in Fig. curves.
- 110 "further runs" (setup.tex): hand-summed; replaced by the four registry counts `\rhval{count/abl_targets|sweep_ntrain|sweep_lr|curves/runs}` (20, 36, 42, 12). 41, 90 and 241 are now `\rhval{count/...}` too.
- 99.9% pretraining exact match (setup.tex): now `\rhval{main/no-adaptation/sort_desc/pretask_acc/mean:pct2}` (prints 99.95).
- 0.15--0.18, std 0.535, 0.80--0.96, 0.997--1.000 (ablations.tex, results.tex): same values, now `\rhval` keys of the registry aggregates / runs.

Hand-written tables (built by `method/report.py`, not by `rh table`):
- tab_rank, tab_targets, tab_ntrain, tab_lr, tab_tests: `method/report.py` now writes every cell as an `\rhval{<key>}` macro; no number is typed or computed in the .tex. Rendered values are identical to the previous tables for every cell that was kept.
- tab_tests: statistics now come from `rh compare` (reference LoRA r=4) for adapt_acc and pretask_acc (`rh compare --group main --metric pretask_acc`, new CSV); `compare_main_adapt_acc.csv` and `compare_main_forgetting.csv` were re-written by `rh compare` without `--task` so they hold both tasks.
- tab_ntrain, N=2000 column, and tab_lr, the two default-rate rows: these were means over seeds 0--2 of the five-seed main group, a subset statistic the registry does not record (they passed only by coincidental matches). Column and rows deleted; captions and setup.tex now point to Table main (five seeds). Two sentences in ablations.tex that quoted those subset means now quote the five-seed registry means: full fine-tuning at its default 0.998 -> 0.996, LoRA r=4 at its default 0.996 -> 0.997, and the full fine-tuning range over the swept rates is now 0.956 to 0.993. No claim rests on these. Fig. lr_sweep is unchanged and its caption now says where the default-rate points come from.
- results.tex "(i) ... with three seeds, r=4 was stable at the same rate in the sweep (Table lr)": the row it cited is gone; now "stable at that rate in all five seeds" (Table rank, 0/5 failures).

Text that disagreed with the registry (registry wins):
- ablations.tex: "Rank 8 is at or below 0.001 ... in one of three seeds at N=300". The registry has 0.003 for that seed (run seed 0, n_train=300). Corrected to the registry values (at or below 0.0005 at N=100; 0.003 in one seed at N=300).
- setup.tex: "the six runs that include pretraining 50--60 s". The registry has five such runs (seeds 1--4 and tuning seed 100); the first registered seed-0 run took 1.2 s because its checkpoint already existed. Corrected to five.

## Rule 2: only real runs

- No change needed: all 241 registry rows were logged by `rh run` with a command; `rh check` reports no hand-logged row.

## Rule 3: reproducible metrics

- research.yaml `metrics`: added `seconds` with `nondeterministic: true` (the only wall-clock metric logged). Added `pretask_acc_before` (logged by every run, was missing from the list; a result metric, not marked).
- No result metric is marked nondeterministic. Check performed: 12 logged runs were executed again outside the registry (9 with the existing pretraining checkpoints, 3 in a fresh copy that re-pretrains from the seed; systems full, scratch, last block, head, LoRA r=1/4/8, {q,v}, N=100, no adaptation). Every metric except `seconds` matched the registry to the last digit. All randomness is seeded (`torch.manual_seed`, a seeded `torch.Generator` for batches, seeded numpy data).
- Caveat, not hidden: `train_loss` is NaN in the 11 "pretrained / No adaptation" rows (no training happens). It is reproducibly NaN, but a digit-for-digit comparison that treats NaN != NaN would flag it. Bit-identical results were verified on this machine (CPU, 2 threads) only; another CPU or BLAS build may differ in the last digits.

## Rules 4 and 5

- `paper/sections/author.tex`: not edited (the platform's rewrite is committed as it was found).
- Length 6 pages; no "state of the art" or "novel" in the text. No change needed.

## Final gates

- `rh paper build`: BUILD OK. `rh lit verify`: CITATIONS VERIFIED. `rh numbers`: 0 untraced. `rh check`: READY (one advisory warning: verdict tier 1 < target 2, unchanged from before).
