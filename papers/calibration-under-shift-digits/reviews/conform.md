# Conformance report: numbers traced, constants declared

Scope: the paper's claims, hypotheses and verdicts are unchanged. No experiment was run. Every result in the text
and in the tables is now printed by `\rhval{<key>}` from the registry; nothing is typed by hand.
`rh numbers`: 709 checked, 709 traced, 0 untraced. `rh check`: READY. `rh lit verify`: CITATIONS VERIFIED. 7 pages.

## Rule 1: numbers

Registry versus text: every value the old text stated was compared with what the registry now prints in its place.
None disagreed, so no number in the paper was corrected.

Untraced numbers reported by `rh numbers` at the start (15):
- setup.tex 1797 (dataset size): declared constant `n_images`; printed with `\rhval{const/n_images}`.
- setup.tex 1078 (training images): declared constant `n_train`.
- setup.tex, ablations.tex, limitations.tex 269 (validation images): declared constant `n_val`.
- setup.tex, results.tex, limitations.tex 450 (test images): declared constant `n_test`.
- setup.tex 128, 128 (hidden width in "64--128--128--10"): declared constant `hidden_units`.
- results.tex, generated/hyp.tex, generated/ts_vs_mlp.tex 0.268 (H1 paired p, TS vs MLP ECE at r0): replaced by `\rhval{cmp/abl_oracle/mlp/rot0/ece/paired_p:3}` (`rh compare`); same value.
- generated/hyp.tex 50.245 and 38.689 (H2 ratio of TS ECE at r60 / n1.0 to r0): deleted. `rh compare` has no statistic across two conditions, so the table row now shows the two means and no ratio.

Derived numbers that the tracer had matched to an unrelated record by coincidence (treated the same way):
- abstract "about 50-fold", "about 39-fold"; results "a ratio of about 50", "about 39"; conclusion "about 50 and 39 times": deleted; the sentences now give the two means (`\rhval`) and say both exceed the registered factor of two.
- results H1 p=0.094 (NLL): `\rhval{cmp/abl_oracle/mlp/rot0/nll/paired_p:3}`.
- results H2 relative ECE change -33%, -3%, -36%, -8% and p=0.099: `\rhval{cmp/abl_oracle/mlp/<task>/ece/rel_delta:pct0}` and `.../paired_p:3`. Wording "improvement of TS over the MLP" became "change from the MLP to TS" because the printed values are negative.
- results "p<=0.020" (TS vs MLP NLL, shifted conditions): now "the largest paired p is `\rhval{cmp/abl_oracle/mlp/noise0.25/nll/paired_p:3}`, at n0.25".
- results H4 p=0.071 and "p rounds to 0.000": `\rhval{cmp/main/deep-ensemble-5/rot60/ece/paired_p:3}` and `.../noise1.0/ece/paired_p:sci1` (printed in scientific notation instead of as zero).
- results "ECE below 0.02 for all four": hand-typed bound replaced by the largest of the four means, `\rhval{main/mlp/rot0/ece/mean:3}`.
- results "ECE is 0.75--0.83": range now printed from its two end points (`main/mc-dropout/rot45` and `main/mlp/rot60` ECE means).
- ablations H5 "paired p rounds to 0.000 in each case": now the largest of the four, `\rhval{cmp/abl_oracle/ts-oracle-shifted-val/noise0.75/ece/paired_p:sci1}`.
- ablations "within 0.003 of each other" (a hand-computed difference): deleted; the three r0 means are printed instead.
- ablations Det-vs-MLP p=0.95, 0.086, 0.37, 0.004 and Det-vs-MCD p=0.47, "p<=0.023": `\rhval{cmp/abl_dropdet/mlp|mc-dropout/<task>/ece/paired_p}`; the bound became "the largest p is ..., at r60".
- conclusion "ECE gain shrank to 3%": `\rhval{cmp/abl_oracle/mlp/rot60/ece/rel_delta:pct0}`, worded as a relative change (prints -3).
- setup "412 logged runs ... about 40 minutes of summed run time (about 32 minutes wall-clock)": the hand-summed times are deleted; the paragraph says the study stayed within the 45-minute budget of research.yaml (the logged durations sum to less than that). Per-group run counts are `\rhval{count/...}`. The total 412 is no longer stated: the registry now has 632 rows (see below), and the paragraph says why.
- setup "p-values are computed by results/analysis.py (scipy), not by rh compare": replaced, since that is no longer true.
- all other means, temperatures and accuracies in abstract, results, ablations and conclusion: same values, now `\rhval{<group>/<system>/<task>/<metric>/mean}` so each is attributed to the right system and condition.

Tables:
- generated/hyp.tex: was built by results/analysis.py with scipy. Now only `\rhval` keys. A-B and p come from `rh compare`. Rows H3 and H4 are oriented MC dropout minus ensemble and H5 TS minus oracle (the direction `rh compare` reports), so those differences changed sign; the H2 ratio column is gone.
- generated/ts_vs_mlp.tex: the Delta-ECE% and both p columns now come from `rh compare`; same values.
- generated/main_ece_nll.tex, main_acc_brier.tex, oracle_cmp.tex, dropdet.tex, sweeps.tex: cells are now `\rhval` keys; after expansion they are identical to the committed tables.
- generated/mcd_vs_ens.tex (Table V, added): the 33 paired differences and p-values behind the sentence "significant for NLL in all 11, ECE in 9 and Brier in 7", which the paper stated without showing them. The counts agree with `rh compare`.

How the comparisons were made:
- `rh compare --group main --metric ece|nll|brier --ref "MC dropout"`.
- `rh compare --group abl_oracle --metric ece|nll --ref "MLP + temperature scaling"`.
- `rh compare --group abl_dropdet --metric ece --ref "Dropout-trained MLP, deterministic"`.
- `rh compare` works inside one group, so 220 main-group rows were listed again with `rh log --from-run` (copies of metrics and provenance, no new run): MLP and TS in abl_oracle, MLP and MC dropout in abl_dropdet. `results/runs.jsonl` went from 412 to 632 rows; the 412 original rows are untouched.
- results/analysis.py: no longer computes p-values or ratios; selects the ablation systems by name so the copies do not enter the oracle and decomposition means; writes the `\rhval` tables. results/tables/hyp.csv, hyp.md and results/analysis_out.txt (scipy output) removed. Figures not regenerated.

Declared constants (13): n_images 1797, n_train 1078, n_val 269, n_test 450, hidden_units 128, epochs 100,
learning_rate 0.001, alpha 0.05, dropout_p 0.2, noise_sigma_1..4 = 0.25, 0.5, 0.75, 1.0. All are setup facts from
method/run.py and research.yaml; the last eight were being matched to unrelated results by value.

## Rule 2: real runs only

No change needed. All 412 original rows have a command and a log (`rh run`); none was logged with `rh log` by hand.
The 220 `--from-run` copies carry the command of the run they copy and are not marked hand-logged.

## Rule 3: reproducible metrics

- research.yaml `metrics:` unchanged. No run logs a wall-clock or throughput metric (run time is only in
  provenance), so nothing is marked `nondeterministic`. No result metric is marked.
- No unseeded randomness found: split, initialisation, minibatch order, dropout masks and noise are all seeded.
- Checked: 15 logged runs covering every group and system were recomputed with an empty weight cache (training from
  scratch); every metric matched the registry exactly.
- Not checked: the platform's own re-execution could not be dry-run here (its `sandbox-exec` guard cannot start
  inside this session's sandbox).
- Caveat: runs cache network weights in /tmp/calib_cache, outside the project. With the cache present a re-run loads
  the weights; without it the run retrains (the case checked above), which takes longer than the logged duration of a
  cached run. The slowest logged run that had to train (a 10-member ensemble) took 28 s, under the platform's 60 s
  limit, but on a heavily loaded machine a retraining ensemble row could come closer to it.

## Rule 4: byline

paper/sections/author.tex not edited; it is committed as the platform left it.

## Rule 5: length and wording

7 pages. No "state of the art" and no "novel" in the paper; nothing to change.
