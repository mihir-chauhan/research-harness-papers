# Conformance report

No claim, table, figure or sentence of the paper was changed. No experiment was added to the registry.

## Rule 1: every number is traced

`rh numbers` before: 234 checked, 4 untraced. After: 234 checked, 0 untraced.

Untraced numbers, all setup facts, declared with `rh const add`:

- `4000` (method.tex, held-out test targets per evaluation): declared constant `test_targets`.
- `10000` (setup.tex, validation seed offset): declared constant `val_seed_offset`.
- `20000` (setup.tex, test seed offset): declared constant `test_seed_offset`.
- `40000` (results.tex, figure caption, x-axis limit of the dense learning-curve panel): declared constant `curves_xlim_episodes`.

Setup facts that `rh numbers` already accepted, but only because a result statistic happens to round to the same value. Declared so the reviewers' constant list states what they are (the tool still prints the coincidental trace for them):

- `0.3` (method.tex, success radius; was matched to a noise-sweep success mean): declared constant `success_radius`.
- `0.25` (setup.tex, time step; was matched to a final_dist mean): declared constant `dt`.
- `3\times10^{-3}` (setup.tex, Adam learning rate; was matched to a final_dist std): declared constant `learning_rate`.
- `0.5` / `50\%` (method.tex, results.tex, abstract.tex, threshold of episodes_to_50; was matched to a success_auc mean): declared constant `threshold_50`.
- `0.9` / `90\%` (method.tex, results.tex, threshold of episodes_to_90; was matched to a success_rate statistic): declared constant `threshold_90`.

Not declared, left traced to the runs: `6400`, `640` and `128000` (evaluation intervals and total training episodes). They are setup facts in the prose but the same values are also logged results (the floor and the cap of episodes_to_50 / episodes_to_90), and a constant must never be a result.

Derived numbers: the prose contains no hand-typed difference, ratio, percentage change or p-value, so nothing was replaced or deleted. No result was retyped or computed by hand.

Text against registry: every result quoted in the prose was compared with `rh values --list` and the generated tables (main, xplay, abl_tau, dense_eval, sweeps_summary); all agree to the printed precision. No correction was needed.

Tables: `abl_tau.tex`, `dense_eval.tex` and `sweeps_summary.tex` are not hand-written; they are produced from `results/runs.jsonl` by `experiments/make_audit_tables.py` and `experiments/make_sweep_table.py` (not by `rh table`). Every cell traces. Left unchanged.

## Rule 2: only real runs count

All 150 registry rows carry a recorded command, exit code and log (`rh run`). No row was logged by hand, so nothing was replaced and no run was added.

## Rule 3: reproducible metrics

- `research.yaml` `metrics:` holds no wall-clock or throughput metric, and no run logs one (run time is only in each row's provenance, `duration_s`). Nothing was marked `nondeterministic`.
- Result metrics are seeded (`torch.manual_seed(seed)` for training, fixed generators for validation and test targets, `torch.manual_seed(0)` for cross-play). I found no unseeded randomness.
- Checked by re-running four logged configurations in a scratch copy under /tmp (not logged, workspace files untouched): main / discrete / seed 3, sweep_noise / continuous / noise 0.6 / seed 1, dense_eval / language / seed 2, xplay / continuous / seed 4. Every logged metric matched to the last digit.
- Caveats for the platform's re-run: only tested on this machine with 2 threads; a different CPU or BLAS could change floating-point results. Cross-play runs read the checkpoints in `results/ckpt` (tracked in git), so they reproduce only with those files present. The `main` rows predate the `episodes_to_90` and `val_success_final` outputs, so a re-run prints two metrics the logged rows do not have.

## Rule 4: byline

`paper/sections/author.tex` is the platform's version; not edited by me. It is committed as the platform left it.

## Rule 5: length and wording

5 pages. No "state of the art", no "novel" anywhere in the paper.

## Other

- Setup says each training run takes "about ten seconds": the registry's median training duration is 11.2 s (min 8.5 s, max 89.8 s for a run that overlapped others). The wording is not a traced number and was left as is.
- `rh paper build` added one line to `paper/main.tex` (loads `generated/values.tex`) and wrote `paper/generated/values.tex` and `paper/number_trace.json`; `rh const add` re-wrapped `research.yaml`. These are tool side effects, not edits to content.

## Final state

`rh paper build`: BUILD OK. `rh lit verify`: CITATIONS VERIFIED (11 of 11). `rh numbers`: 0 untraced. `rh check`: READY, with one warning that predates this pass (verdict tier 0 below target 2: the proposed language is not the best system, which the paper states).
