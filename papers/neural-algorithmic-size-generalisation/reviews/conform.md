# Conformance report

No claim, hypothesis verdict or experiment changed. No run was added to the registry.

## Rule 1: every number traced (`rh numbers`: 32 untraced before, 0 after)

Setup facts declared with `rh const add` (none is a result):
- `1000` (abstract, setup, results, limitations): declared `train_steps`, the Adam steps per run.
- `200` (setup, twice): declared `test_graphs_per_cell`, the test graphs per (family, size) cell.
- `10000` (setup): declared `eval_seed_offset`, the offset of the test-graph random stream.
- `12,770` (introduction, method): declared `mpnn_parameters`; recounted from the model definition in `method/run.py`, matches.
- `557,376` (introduction, method): declared `mlp_parameters`; recounted from the model definition, matches.
- `4160` (method): declared `mlp_input_dim`, the padded adjacency plus one-hot source.
- `128` (method): declared `mlp_hidden_width`.

Derived numbers removed or replaced (they were computed by `analysis/make_tables.py` or typed, not registry values):
- `perseed.tex`, D64/D8 block (`2.20`, `24.26`, `11.53`, `40.66`, `4e2`, `12.28`, `8.02`, `5.72`, `6.95` and the rest of the 25 per-seed ratios): removed; the block now lists the per-seed dense MAE at 8 nodes straight from the registry, so the table holds both terms of the ratio and no quotient.
- `robust.tex`, D64/D8 column (`2.304`, `24.255`, `12.279`): removed; replaced by a D8 column (registry median of `mae_dense_n8`).
- results, H3, `p<10^{-5}`: replaced by the two `rh compare` values via `\rhval{cmp/main/mlp-flat-adjacency/bellman_ford/mae_sparse_n16/welch_p:sci1}` and `.../paired_p:sci1`.
- results, H4, `10^{18}`, `5.72`, `8\times10^{2}` (ratios of the registered pair): sentence rewritten on the registry values (median D8 of both systems and the largest D64 of max+steps via `\rhval`, and the existing D64 statement for sum+steps). Verdict unchanged: direction as hypothesised in each of the five seeds, untested.
- results, H4, `24.255`, `12.279`, `8.39`, `40.66`, `2.02`, `4\times10^{2}` (ratios of the post hoc final-only pair): the sentence stating the median ratio and the ratio ranges was deleted; the text now says the per-seed D64 errors overlap and keeps the failure counts. Verdict unchanged: inconclusive. The one statement lost is "the median ratio is also larger for sum".
- ablations, "worse by a factor of more than eight at x4": a hand-computed ratio written as a word, so `rh numbers` did not flag it; reworded to "clearly worse at x4 than at x1" with a pointer to the sweep table. Same four of six models.
- captions of the two tables and the first sentence of the results section: updated to describe the D8 columns in place of the ratio.
- `results/RESULTS.md`: the same ratio numbers, the `p<1e-5` bound and the ">8x" removed, to keep it in line with the paper.

Text against registry: every number in the prose and the generated tables was compared with `results/runs.jsonl` and the `rh compare` CSVs. No disagreement was found, so no value was corrected.

Note on the tracer: several numbers were matched by `rh numbers` to an unrelated statistic of the same value (for example `10^{17}` in the abstract to a sweep-run maximum, `100` in a caption to a wall-clock time). They were checked by hand against the statistic they actually refer to and are correct.

## Rule 2: only real runs

- All 50 registry rows (25 main, 6 aggregation ablation, 18 step sweep, 1 sanity) carry an `rh run` command, log and exit code. No hand-logged row exists, so nothing was replaced.

## Rule 3: reproducible metrics

- `research.yaml`: added `train_seconds` under `metrics:` with `nondeterministic: true`. It is the only wall-clock metric logged. No result metric is marked.
- Check: three logged runs were re-executed outside the registry (output in `/tmp`): MLP seed 0, MPNN-max + steps seed 0, MPNN-sum seed 4 (which includes a non-finite D64 value). All 26 result metrics matched the registry to the last digit in each; only `train_seconds` differed.
- Not checked: the other 47 runs, and any other machine or library version. The runs are CPU-only with two threads and seed both generators (`torch.manual_seed`, `numpy.random.default_rng`); no unseeded randomness was found in `method/run.py`.

## Rule 4: byline

- `paper/sections/author.tex`: not edited; committed as the platform rewrote it.

## Rule 5: length and wording

- 6 pages. Neither "state of the art" nor "novel" occurs in the paper.

## Final state

- `rh paper build`: BUILD OK. `rh lit verify`: CITATIONS VERIFIED (14 of 14). `rh numbers`: 343 checked, 0 untraced. `rh check`: READY.
- `rh check` still prints one warning, unchanged from before: verdict tier 0 below target 2, because the method (MPNN-max + steps) is not the best system on the primary metric. That is the paper's negative finding and was left alone.
- The two figures were not changed.
