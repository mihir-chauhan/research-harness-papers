# Conformance report: numbers traced, constants declared

Scope: bring the paper into line with the platform rules without changing its claims. No new experiment was run and no
claim, hypothesis verdict or framing was changed. `rh numbers` went from 10 untraced to 0; `rh check` prints READY.

## Rule 1: every number is traced

Result numbers in the text (replaced by `\rhval{<key>}`; values are now printed at the registry's four significant figures)
- abstract, count vs penalty `p >= 0.288`: now `\rhval{cmp/offset_control/count-bonus-state/chain_20/.../welch_p}` (0.2881).
- abstract, `18435 / 11476 / 11921` steps on room_4: now the three `main/.../room_4/steps_to_first_reward/mean` keys.
- abstract and ablations, largest unguarded bonus `1.44x10^7`: now `main/rnd-unguarded-normaliser-v1/chain_20/bonus_max/max` (14434239).
- abstract and ablations, TV share `0.016 -> 0.029` (RND) and `0.013 -> 0.027` (observation count): now the `sweep_k/...@k=1` and `@k=64` `tv_time_frac/mean` keys.
- results H1, RND means `5242`, `76276`: `\rhval`; `p<0.001` and `p=0.067` against epsilon-greedy: now the exact `cmp/main/epsilon-greedy-q-learning/{chain_40,room_6}/.../welch_p`.
- results H1, `p=0.521` and `0.109` (chain_10, room_2): now the `cmp/main/epsilon-greedy-q-learning/.../welch_p` keys.
- results H1, penalty vs count means `2638/2603`, `11921/11476`, `29105/28439`: `\rhval`.
- results H1, `Welch p >= 0.288`: `\rhval` (same key as the abstract).
- results H1, room_4_tv `11643 against 13231, p<0.001`: means as `\rhval`, p as `cmp/offset_control/count-bonus-state/room_4_tv/.../welch_p` (0.0006043).
- results H2, `2146/618`, `18435/11921`, `76276/29105` and `p=0.062` (chain_10): `\rhval` (`cmp/main/step-penalty-only-optimistic-init/chain_10/.../welch_p`).
- results "Where RND fails", `76276 +- 21269`, final return `0.45 +- 0.40`, chain gaps `525/122`, `2146/618`, `5242/2638`: `\rhval` mean and std keys.
- results H3, RND and observation-count means on the TV tasks and their twins, TV shares `0.025 +- 0.001`, `0.023 +- 0.001`, `0.013 +- 0.001`, `0.214`: `\rhval` mean and std keys.
- ablations, unguarded `|Q|` up to `3.62x10^6` and `28656` steps: `\rhval` max keys.
- ablations, clip-only and guarded means `915/6493/19682` and `525/5242/15184`: `\rhval`.
- ablations, warm-up-only bonus "reaches 29": now `main/rnd-warm-up-only/room_4/bonus_max/max` (28.99), with the task named.
- ablations, no-normalisation raw error "never exceeds 0.44": now `main/no-bonus-normalisation-rnd_nonorm/chain_20_tv/bonus_max/max` (0.4405).
- ablations, no-normalisation means `2620/2638`, `29808/29105`, `64/122`, `11439/13231`, `13206/11921`: `\rhval`.
- ablations, clip sweep `1730/2146`, `15396/18435`, `618`, `11921`: `\rhval` (`sweep_clip/rnd-bonus@clip=2.0/...` and `main/...`).
- setup, "all 492 runs": now the per-group run counts `\rhval{count/<group>/runs}` (400 main, 30 + 30 + 20 sweeps, 12 pilot).

Derived numbers that `rh` cannot produce (deleted, the surrounding statement kept in words)
- results H3 and Table III, Welch p of each TV task against its noise-free twin (`0.324`, `0.219`, `0.323`, `0.832`, and the whole `p` column incl. `0.635`, `0.847`, `0.873`, `0.447`): deleted. `rh compare` compares systems on one task, not one system across tasks. The text now states that each gap is below the twin's standard deviation and prints the means and standard deviations.
- results H1 and limitations, penalty-only room_4 vs room_4_tv `p=0.011`: deleted; replaced by its two means +- std (`\rhval`) and the statement that they differ by more than its standard deviation. The limitations sentence "one is below 0.05 for a control that cannot be affected" was reworded to match.
- ablations and Table VI, Welch p between K=1 and K=64 (`p<0.001`, `0.406`, `0.511`, and the table's `p` row): deleted. The text states the rise in words and that the K=1 and K=64 step means are within one standard deviation.
- ablations, "it stays below 0.03": replaced by the largest mean TV share as `\rhval`.
- ablations, pooled diagnostics typed in the text (`median 0.0005`, `share 0.018`, `share b>1: 0.000`): deleted from the text; the sentences now point to Table IV.
- ablations, `e x 10^8`: rewritten as `e/10^{-8}` (the declared normaliser epsilon), no new number.
- setup: "scipy for the twin and K comparisons" removed; the scipy tests are gone from `method/make_tables.py`.

Tables
- Table II (tests): every cell is now an `\rhval{cmp/...}` key instead of a number formatted by `method/make_tables.py`; exact p-values replace `<0.001`. Wrapped in `\resizebox` to fit the column.
- Table II, column cnt / pen (`0.844`, `0.679`, `0.619`, ...): `rh compare` keeps one reference per group, so these Welch tests against the penalty-only control now have their own group. `offset_control` holds 80 copies (`rh log --from-run`, original command and provenance kept, `copied_from` set) of the `main` rows of "Step penalty only" and "Count bonus (state)"; `rh compare --group offset_control --ref "Step penalty only (optimistic init)"` supplies the values. No run was executed for this. The registry now has 572 live rows for 492 executed runs.
- Table III (TV tasks): `p` column removed (see above).
- Table VI (K sweep): `p` row removed (see above).
- Table IV (bonus diagnostics): rows "max b", "max |Q|", "median b" and "share b>1" are now `\rhval` keys. "max b" and "max |Q|" are unchanged in value. **"median b" and "share b>1" changed statistic**: they were pooled over the 40 runs of a variant (median of per-run medians, mean of per-run shares), which `rh` does not record and which traced only by coincidence to unrelated registry values; they now show the per-task statistic `rh` records (5 seeds) for the task where it is largest. Values therefore changed (guarded: median 0.0005 -> 0.04261, share 0.018 -> 0.05782); the caption says so, and the claim they support ("close to zero most of the time", "a small share of the steps") is unchanged and now stated as an upper bound over tasks.

Declared constants (`rh const add`, 16; none is a result)
- `alpha` 0.5, `gamma` 0.99, `epsilon` 0.1, `beta` 0.1: learner settings.
- `beta_sweep_low` 0.03, `beta_sweep_mid` 0.3: beta sweep values.
- `predictor_lr` 0.003, `normaliser_eps` 1e-8: RND predictor learning rate, normaliser epsilon.
- `spike_threshold` 10000, `early_window_steps` 100: analysis threshold and window of the spike diagnostic.
- `pilot_seed` 100: seed of the pilot runs.
- `budget_chain_steps` 30000, `budget_room_steps` 100000: step budgets (censoring values).
- `final_return_window_pct` 20: final return window.
- `significance_level` 0.05: level the p-values are compared against.
- `room6_cells` 155: cells of the largest task.

Text against registry
- No result number in the text disagreed with the registry; every replaced value matched at the precision it was typed.
- limitations, "about 150 cells": corrected to the exact count, 155 (computed by `method/run.py`), and declared as a constant.

## Rule 2: only real runs count
- No row the paper uses was logged by hand: all 492 executed live rows have an `rh run` command, exit code 0 and a log file. The 80 `offset_control` rows are `--from-run` copies of such rows, not typed metrics.

## Rule 3: reproducible metrics
- `research.yaml` `metrics:` has no wall-clock or throughput metric and `method/run.py` logs none (run time is only in provenance), so nothing was marked `nondeterministic`. No result metric was marked.
- Every logged metric is reproducible from its seed: all randomness comes from one `numpy.random.default_rng(seed)`. Checked by re-running 14 logged runs (main, ablation and sweep rows) from their recorded commands: all 12 metrics identical to the digit in all 14.
- Six logged diagnostics (`bonus_max`, `bonus_max_early`, `bonus_median`, `bonus_gt1_frac`, `bonus_clip_frac`, `q_abs_max`) are not listed under `metrics:` in `research.yaml`; they are deterministic as well.

## Rule 4: byline
- `paper/sections/author.tex`: not edited; committed as the platform wrote it.

## Rule 5: length and wording
- 7 pages. No "state of the art"; "novel" occurs only inside "novelty" (the bonus signal), never as a claim about this work.

## Not checked by `rh numbers` (left as typed)
- Integers below 100 (seed counts, "39 of 40 runs", "19 of the 20", W = 64, c = 5, K values): they agree with the generated tables.
- Setup constants are reported by the tracer as coincidental matches to registry aggregates; they are declared all the same.
- "under 9 s per run, about 20 CPU-minutes": from the recorded run durations (maximum 8.5 s, sum 19.7 min).

## Other files
- `paper/main.tex`: `\input{generated/values}` added.
- `method/make_tables.py`, `experiments/build_results.sh`, `experiments/run_all.py` (`copies` stage), `experiments/PROTOCOL.md`, `README.md`, `results/RESULTS.md`: updated to the above.

## Final state
- `rh paper build`: BUILD OK. `rh lit verify`: CITATIONS VERIFIED. `rh numbers`: ALL NUMBERS TRACED. `rh check`: READY (one warning, unchanged from before: verdict tier 0 < target 2, the method is not the best system on room_4, which is the paper's stated negative result).
