# Conformance report

Final state: `rh paper build` BUILD OK (6 pages), `rh lit verify` CITATIONS VERIFIED, `rh numbers` 495 checked / 0 untraced, `rh check` READY (one warning: the 20 failed per-mode rows, already disclosed in the paper). No new experiment was logged; `results/runs.jsonl` is unchanged.

## Rule 1: numbers

Setup facts declared with `rh const add` (none is a result):
- 128 (setup.tex twice, limitations.tex): declared `hidden_units`.
- 5000 (setup.tex twice): declared `train_steps`.
- 512 (setup.tex): declared `batch_size`.
- 1500 (method.tex, setup.tex): declared `eval_samples_per_class`.
- 6000 (setup.tex): declared `eval_samples_per_run`.
- 192 (setup.tex): declared `timing_trial_hidden_units`.
- 8000 (setup.tex): declared `timing_trial_train_steps`.
- Setup facts that were not flagged only because they happened to equal an unrelated result were declared as well: 100 diffusion steps (`diffusion_steps`), lr 2e-3 (`learning_rate`), sigma 0.6 / 0.35 (`sigma_overlap`, `sigma_sep`), mode weights 0.5 / 0.3 / 0.2 (`mode_weight_major/middle/minor`), default label dropout 0.1 (`label_dropout_default`), alpha 0.05 (`test_alpha`).

Run counts replaced by registry counts:
- 120 and 110 (setup.tex, "120 registry runs (110 grid runs plus 10 reference runs)"): replaced by `\rhval{count/...}` per group (141 ok runs: 30 main, 30 guidance-sweep, 25 temperature-sweep, 15 interval, 10 label-dropout, 10 reference, 20 per-mode, one smoke run); "Twenty ... failed" rows is now `\rhval{count/runs_failed}`.

Hand-computed hypothesis table (`generated/hyp.tex`, written by `analysis/analyze.py`) removed; Table III is now built from `rh compare --group main` (ref CFG w=3) via `\rhval{cmp/...}`:
- 0.1119, 3.2e-06 (H2 mode_tv) and 0.1174, 1.3e-04 (H2 std_ratio): now `\rhval` delta / paired_p from `rh compare` (same values). H1 and H3 rows likewise.
- 16.5, 6.5 (and 45.5, 15.8, which only "traced" by coinciding with unrelated statistics): the d_z column (mean over sd of paired differences) is not a registry statistic. Replaced by the Cohen's d that `rh compare` reports (pooled sd: 63.9, 15.9, -6.7, 11.1); caption and setup.tex say so. This is a different effect-size definition, not a changed result.
- H5 row (+0.0476, p=0.020, d_z=1.7) and H4 row (-0.0004, p=0.935, d_z=-0.1): deleted. `rh compare` cannot recompute them (H5 compares two registry groups, H4 is a difference of differences across tasks). These six numbers were not flagged by `rh numbers` only because they coincided with unrelated registry statistics; they were hand-computed, so they are removed rather than left as false traces.
- `analysis/analyze.py` no longer writes `hyp.tex` (it still prints the tests for reference).

Prose (results.tex, limitations.tex, abstract.tex, conclusion.tex):
- H1 "+0.0736, p=5.6e-8" and H3 "p=3.8e-6": now `\rhval` (same values).
- H2 "both p<1e-3": replaced by the two paired p-values from `rh compare` (3.2e-6, 1.3e-4).
- H4 "difference of differences -0.0004 (p=0.935)": deleted; replaced by the two mean differences from `rh compare` (0.1119 overlap, 0.1116 separation) and a sentence that the registered Welch test is not recomputed by the registry. Verdict (refuted) unchanged, now resting on the mean differences only.
- H4 post hoc "-0.173 vs -0.117, Welch p=0.012" and "+0.560 vs +0.663, p=0.0013": the four differences are now `\rhval` deltas from `rh compare` (same values); the two cross-task Welch p-values are deleted. Abstract and conclusion say "post hoc, descriptive" instead of "post hoc, uncorrected".
- H5 "mean difference +0.0476, p=0.020, d_z=1.7": deleted; the two means (0.055 vs 0.007) stay. Heading changed from "supported, small sample" to "supported descriptively, small sample", since no traced test statistic backs it any more.
- Limitations "H5 ... (p=0.020) ... (threshold 0.0083)": both numbers deleted; the caveat (borderline, would not survive Bonferroni) is kept in words.
- Failure case "swd is >10x the unguided value" (hand-computed ratio): replaced by the two traced means (1.473 against 0.120).

Text corrected where it disagreed with the registry or logs:
- "about 21 minutes in total" (setup.tex): registry run durations of the 120 grid and reference runs sum to 21.9 min; text now says "summed run time is about 22 minutes".
- "Training takes about 50 s": the run logs show 20 to 50 s; text now says "20 to 50 s".
- All other prose numbers were checked against the generated tables and agree.

## Rule 2: only real runs

- All 161 registry rows (141 ok, 20 failed) were logged by `rh run` with a recorded command and log; none was logged by hand. Nothing to replace.

## Rule 3: reproducible metrics

- `research.yaml` metrics: added `wall_s` with `nondeterministic: true` (the only wall-clock metric). No result metric is marked nondeterministic. (`rh const add` re-serialised research.yaml; apart from `constants` and `wall_s` its content is unchanged.)
- Checked by re-running logged commands to /tmp and comparing every result metric with the registry: main CFG w=3 mix_overlap seed 0 and main tau=0.5 mix_sep seed 1 (both retrained from scratch in an empty checkpoint directory), sweep w=8 seed 2 (cached network), real-sample reference seed 4, per-mode seeds 3 and 4. All identical to the last digit. All randomness is seeded; no unseeded result metric was found. This was verified on this machine only (CPU, 2 threads); bit-identical results on other hardware or library versions were not tested.
- `method/permode.py` loaded the cached network from `results/raw/ckpt/` (git-ignored) and crashed if it was missing. It now trains the network exactly as `method/run.py` does when the cache is absent (same command line, identical metrics, checked for seed 4 with an empty cache).

## Rule 4: byline

- `paper/sections/author.tex` not edited (the platform's rewrite is committed as found).

## Rule 5: length and wording

- 6 pages. No "state of the art" or "novel" in the text.

## Housekeeping

- `paper/main.tex`: `rh paper build` added the `\input{generated/values}` line for `\rhval`.
- New: `results/tables/compare_main_{mode_tv,std_ratio,swd}.csv` (output of `rh compare`), `paper/generated/values.tex`, `paper/number_trace.json`.
- `results/RESULTS.md` still lists the script-computed H4/H5 statistics as internal notes; it is not part of the paper.
