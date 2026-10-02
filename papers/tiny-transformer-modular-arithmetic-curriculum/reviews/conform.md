# Conformance to the stricter paper rules (no change to claims)

Before: `rh numbers` 15 untraced, `rh check` NOT READY. After: 0 untraced, READY.

## Numbers (rule 1)
- 529 (method.tex, setup.tex): setup fact, declared constant `num_pairs`.
- 256 (method.tex): setup fact, declared constant `mlp_hidden_width`.
- 128 (method.tex): setup fact, declared constant `batch_size`.
- Other setup facts stated in the paper that the tracer had only matched by coincidence to an unrelated statistic or had not needed (23, 64, 3e-3, 0.9, 0.98, 0.15, 32, 25, 4000, 1000, 0.95, pilot seed 100): declared as constants `modulus`, `d_model`, `learning_rate`, `adam_beta1`, `adam_beta2`, `pool_start_fraction`, `min_pool_size`, `eval_every`, `step_budget`, `default_curriculum_length`, `accuracy_threshold`, `pilot_seed`. All are defaults or literals of method/run.py; none is a result.
- 3246, 3789 (abstract.tex, conclusion.tex; pooled 7-seed means): replaced by `\rhval{pooled7/<system>/wd1_f0.5/steps_to_95/mean}`. To make these registry statistics, the 15 main-cell rows (group main) and 6 rows (group curves) were copied with `rh log --from-run` into a new group `pooled7` (21 copies, original command and log kept, `copied_from` set; no new runs, no typed metrics).
- 3246, 979, 3789, 466, 3993 and all other means/stds in generated/pooled7.tex: analysis/pooled.py now writes `\rhval{...}` keys (groups main, curves, pooled7) and no longer computes anything with scipy/numpy.
- 0.22, 0.27 (pooled Welch/paired p, results.tex and pooled7.tex): replaced by `\rhval{cmp/pooled7/uniform-sampling/wd1_f0.5/steps_to_95/welch_p:2}` and `.../paired_p:2`. The tracer had matched them to unrelated standard deviations.
- 543 (results.tex, pooled curriculum-uniform gap): replaced by `\rhval{cmp/pooled7/uniform-sampling/wd1_f0.5/steps_to_95/delta:0}`.
- 1010 (results.tex): replaced by `\rhval{cmp/main/uniform-sampling/wd1_f0.5/steps_to_95/delta}`.
- 0.09, 0.09 (results.tex, registered Welch and paired p): replaced by `\rhval{cmp/main/uniform-sampling/wd1_f0.5/steps_to_95/welch_p:2}` and `.../paired_p:2`.
- -35, +1010, 0.49, 0.51, 0.09, 0.09 (generated/tests.tex, hand-formatted table of differences and p-values): analysis/make_tables.py now writes `\rhval{cmp/main/...}` keys. The "+" sign in front of 1010 is no longer printed.
- 0.09, 0.09 (anti-curriculum vs uniform, pooled; results.tex and pooled7.tex): kept, value taken from `rh compare --group pooled7 --metric steps_to_95 --ref "Uniform sampling"` (saved as results/tables/compare_pooled7_steps_to_95_ref_uniform.csv; pooled.py reads the CSV). There is no `\rhval` key for a comparison whose reference is not the method, so `rh numbers` matches this 0.09 to an unrelated statistic; the real source is the CSV.
- 2133 (results.tex, mean grok gap of the three uniform seeds that reached 95%): hand-computed subset mean, no registry key. Sentence now lists the three per-run gaps with `\rhval{run/<id>/grok_gap}` (seeds 4, 1, 3) and gives no mean.
- 1700, 2450, 2575 (results.tex, per-seed uniform steps): replaced by `\rhval{run/<id>/steps_to_95}`.
- 0.47 (results.tex, plateau level read off Fig. 2): removed; the sentence now says "well below the 95% threshold". The value came from the curve CSVs in results/raw (git-ignored, not in the registry) and the tracer had matched it to the std of a wall-clock metric.
- Text vs registry: every count and mean stated in the text (reached counts per group, 27 runs at wd=0, 5 of 9 empty grid cells, train-fit steps, pooled statistics, p-values) was re-checked against results/runs.jsonl; no disagreement was found, so no value was corrected.

## Runs (rule 2)
- No row was logged by hand: all 119 original rows have a command, exit code 0 and a log whose `metrics:` line equals the registry metrics (checked for every row). The 21 `pooled7` rows are platform copies of such rows. No re-run was needed.
- Known and already documented in experiments/PROTOCOL.md: the 72 grid rows were relabelled from group grid to group main after the runs; metrics and provenance are untouched.

## Reproducible metrics (rule 3)
- research.yaml: `wall_s` marked `nondeterministic: true`. No result metric is marked.
- Result metrics are seeded (torch.manual_seed and numpy default_rng from --seed, 2 threads). Four logged runs were executed again outside the registry (main uniform seed 4, curves curriculum seed 5, main anti-curriculum wd3_f0.7 seed 1, abl_shuffled seed 2): every metric except `wall_s` was identical to the last digit. No unseeded randomness found.
- Not fixed: results/raw/ is git-ignored and the logged commands write `--out results/raw/...`; in a fresh clone that directory must exist before a logged command is run again.

## Byline, length, wording (rules 4, 5)
- paper/sections/author.tex: not edited (platform version committed as is).
- 6 pages. No "state of the art" and no "novel" in the paper.

## Other files touched
- paper/main.tex: `rh paper build` added the `\input{generated/values}` line; paper/generated/values.tex and paper/number_trace.json are platform output.
- experiments/PROTOCOL.md: one sentence describing group `pooled7`.
- results/VERDICT.md is unchanged.
