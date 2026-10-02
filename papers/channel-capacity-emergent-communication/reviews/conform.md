# Conformance report

Scope: bring the paper into line with the platform rules without changing its claims. No new experiment was logged; the registry (`results/runs.jsonl`, 73 rows) is unchanged.

## Rule 1: every number traced

`rh numbers` before: 336 checked, 16 untraced. After: 311 checked, 311 traced, 0 untraced.

Untraced numbers, one line each:

- abstract `1400` (peak step of the Gumbel curve): deleted; the sentence now says train accuracy "peaks early" and gives the 20000-step value from the registry (`\rhval{abl_longtrain/.../train_acc/max:3}`).
- abstract `0.24--0.29` (peak train accuracy from the curve CSVs; was matched by the tracer only by coincidence with unrelated statistics): deleted with the same sentence edit.
- results `0.239--0.291`, `600`, `1400` (peak values and peak steps from the curve CSVs): deleted; the sentence now says "peaks early and then collapses" and points to Fig. 2.
- results `0.017--0.083 at step 6000` (curve CSV values, traced only by coincidence): replaced by the min and max final train accuracy of the 6000-step main runs, `\rhval{main/gumbel-softmax-sender-receiver/v4_l4/train_acc/min:3}` and `.../max:3` (0.022--0.087). These are the registry's values for the same quantity; the curve values came from a different run and are not in the registry.
- results `at most 0.009 at 20000`: now `\rhval{abl_longtrain/gumbel-softmax-sender-receiver/v4_l4/train_acc/max:3}` (same value).
- limitations `0.25`, `1400` (peak near 0.25 within 1400 steps): deleted; "peaks early and then collapses".
- `generated/curve_summary.tex` (Table "Train-accuracy curves": `1400`, `0.291`, `1200`, `600`, `16500`, `16600`, `19500` untraced, and every other cell traced only by coincidence): the table was written by `method/curve_summary.py` from `results/raw/curve_*.csv`, not from the registry, so the whole table was removed from the paper together with both `Table~\ref{tab:curves}` references. Fig. 2 (the curves themselves) stays. The file remains in `results/tables/` as a project record and is copied to `paper/generated/` by the build, but the paper no longer inputs it.
- results "REINFORCE is still improving at 6000 steps (Table curves)": the reference now points to Fig. 2 and gives the registry values, mean train accuracy at 6000 steps and at 20000 steps (`\rhval{main/reinforce-sender-reimplemented/v4_l4/train_acc/mean:3}`, `\rhval{abl_longtrain/reinforce-sender-reimplemented/v4_l4/train_acc/mean:3}`).
- setup `128` (batch size): declared, `rh const add batch_size 128`.
- setup `3000`, `10000` (step budgets of the unrecorded timing probe): declared, `probe_steps_short`, `probe_steps_long`; the reason states that the probe is unrecorded and that these are settings, not results.
- setup `156` in "156--288 s each": disagreed with the registry (shortest control run is 157.0 s). Registry wins: now `\rhval{run/8d60797f26/wall_s:0}`--`\rhval{run/5fa2c104eb/wall_s:0}` (157--288).
- setup "about 26 s per run on average" and "about 29 minutes of run time": hand-computed over all runs, no registry key gives them (and the registry mean is nearer 27 than 26). Both deleted.
- setup "longest 52 s": now `\rhval{run/956d4e40d9/wall_s:0}`.
- setup "66 runs", "6 longer control runs": now `\rhval{count/main/runs}`, `\rhval{count/abl_longtrain/runs}`.

Hand-typed derived numbers (p-values), replaced by the `rh compare` statistics:

- results H3 "Welch p<0.01 for every task": now the three values, `\rhval{cmp/main/oracle-compositional-code-reference/<task>/topsim/welch_p}` (all below 0.01, as stated before).
- results H4 "p=0.72": `\rhval{cmp/main/reinforce-sender-reimplemented/v16_l8/heldout_acc/welch_p:2}`.
- results H4 "p=0.057 and 0.24", "p=0.004": `\rhval{cmp/main/reinforce-sender-reimplemented/{v4_l4,v8_l4,v16_l8}/topsim/welch_p}`.

Typed results that were traced but retyped by hand (many only matched an unrelated statistic by coincidence): every result in the abstract, results, ablations and conclusion is now a `\rhval{...}` of the system, task and metric the sentence names. I checked each old literal against the registry first; apart from `156` above none disagreed, so the printed values are the same. Two wording consequences: "V4_L4 reaches 0.013 for both" now prints the two values separately, and the random-code topsim "(0.004)" reads "(at most 0.004)" since it covers three tasks. The V6_L4 capacity "10.3 bits" is now `\rhval{.../v6_l4/capacity_bits/mean:1}`.

Setup constants declared so the reviewers see them (the tracer had matched them to unrelated results): `n_objects` 256, `holdout_frac` 0.1, `train_frac` 0.9, `learning_rate` 0.002, `baseline_decay` 0.99, `baseline_update` 0.01, `entropy_weight` 0.01, `curve_log_interval` 100. The tracer prefers a result match over a constant, so `number_trace.json` still attributes most of these literals to a coincidental aggregate; the declared list is the correct attribution.

## Rule 2: only real runs

No change needed. All 73 rows have a command, a log and exit code 0; none is marked hand-logged. I compared every row's metrics with the JSON line at the end of its log: all agree. The rows are legacy (no hashes), as they predate the hashed record.

## Rule 3: reproducible metrics

- `research.yaml`: added `metrics: wall_s: {higher_is_better: false, nondeterministic: true}`. `wall_s` is the only wall-clock metric the runs log. No result metric is marked.
- Result metrics are reproducible from the seed: torch, numpy and both `RandomState` generators are seeded in `method/run.py`. Checked by running five logged commands again with the output in /tmp (not logged): Gumbel V4_L4 seed 2, Gumbel V6_L2 seed 0, REINFORCE V4_L4 seed 0, random code V4_L4 seed 2, oracle V8_L4 seed 2. Every metric except `wall_s` matched within 1e-6. The six 20000-step control runs were not re-run.
- The setup section now says that wall-clock times are not reproducible to the digit.

## Rule 4: byline

`paper/sections/author.tex` not edited; the platform's rewrite is committed as found.

## Rule 5: length and wording

- 5 pages (was 6; one table removed).
- introduction: "novel attribute combinations" changed to "unseen attribute combinations" (it described held-out inputs, not a novelty claim). No "state of the art" in the paper.

## Other

- `paper/main.tex`: `rh paper build` added the `\input` of `generated/values.tex`.
- `rh check` still warns "verdict tier 0 < target 2" (the method does not beat the oracle reference). That is the paper's stated result, not a conformance issue.
- Not changed: `results/RESULTS.md` and `reviews/response.md` still quote the curve-peak numbers; they are project records, not the paper.
