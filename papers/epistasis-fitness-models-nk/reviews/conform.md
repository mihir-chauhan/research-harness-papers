# Conformance to the platform's number rules

No claim, hypothesis verdict or experiment changed. No run was added or removed: the registry still has 440 rows. One line per change.

## Rule 1: every number is traced

Before: `rh numbers` listed 7 untraced numbers. After: 419 checked, 419 traced, 0 untraced.

### Setup facts declared as constants (`rh const add`, now in `research.yaml: constants`)
- `5000` (setup.tex, Table I caption): declared `n_test` = 5000, the test-set size (default `--n_test` of `method/run.py`).
- `7.6\times10^4` (method.tex) and `76{,}000` (results.tex): declared `pair_features_max` = 76000, the pair-feature count at L=20, A=20.
- `128` (method.tex): declared `mlp_hidden_units` = 128.
- `300` (method.tex): declared `net_max_epochs` = 300.
- `2\times10^{-3}` (method.tex): declared `net_lr` = 0.002. It was "traced" before only because an unrelated Random Spearman mean rounds to it.
- `20\%` (method.tex, twice): declared `ridge_holdout_frac` = 0.2. Before, it matched an unrelated fit time.
- `15\%` (method.tex): declared `net_val_frac` = 0.15. Before, it matched an unrelated fit time.
- `85\%` (method.tex, limitations.tex): declared `net_train_frac` = 0.85. Before, it matched an unrelated fit time.
- `0.95` (results.tex, H1 threshold): declared `h1_threshold` = 0.95. Before, it matched an unrelated fit time.
- `0.031` (setup.tex, "1/32 ≈ 0.031"): declared `wilcoxon_min_p` = 0.03125, a mathematical fact. Before, it matched an unrelated SD.
- Note: for the last six, the tracer still prints the coincidental aggregate as the source, because it prefers a result over a constant. The declared constant is the real source.

### Derived numbers with no registry source: deleted, the claim kept in words
- `0.259` (sweep table, the one untraced result) and the nine other Pairwise−Additive gaps in that column: column removed from `generated/sweep_n_summary.tex` (edited `analysis/tables_figs.py`, regenerated). The nine others had passed the tracer only by coincidence.
- `0.311`, `0.067`, `0.005`, `0.091` (ablations.tex, H5 gaps): replaced by the two means behind each gap, as `\rhval` keys (0.669 vs 0.358, 0.301 vs 0.234, 0.070 vs 0.065, 0.302 vs 0.211).
- `0.053`, `0.042` (ablations.tex, "gaps of"): deleted; the three means they came from stay.
- `\le 0.012` (ablations.tex, r-fixed differences): deleted; "within one seed standard deviation" stays.
- `0.11`, `0.005` (ablations.tex, worth of the oracle graph): deleted; now "raised mean Spearman clearly in those two cells and changed it little in the other six (Table V)".
- `0.52`, `0.24` (abstract, H4 rank correlation and leave-one-cell-out value): deleted; "is met ... one task cell carries it" stays.
- `0.52`, `0.24` (p=`0.16`), `0.59` (p=`0.12`) (results.tex, H4 rank correlations): deleted; the text now says the correlation is positive, smaller and not nominally significant without L15_A4_K1, and not nominally significant over the eight task means, and points to `results/hypotheses.txt`. These come from `analysis/hyp.py`, not from a logged run or `rh compare`, and had passed the tracer by coincidence.
- `p=0.031` (results.tex, H2 Wilcoxon): deleted as a typed p-value; the text now says the test takes its smallest attainable value with five seeds, 1/32.
- `0.09`, `0.10` (results.tex, p against exact chance): deleted; the text says those tests are not nominally significant and points to `results/hypotheses.txt`.
- `p \ge 0.14` (results.tex, learned models vs Random at K≥2): deleted; the statement stays and names the file `results/tables/compare_main_design_hit_ref_random.csv`.
- Table III (`generated/h4_summary.tex`, written by a script with typed statistics): file deleted. The three ρ rows and the two Add.−Chance rows (`0.155`, `0.065`, `0.09`, `0.10`) are gone. The five paired-difference rows are rebuilt in results.tex from `\rhval{cmp/...}` keys.

### Derived numbers replaced by `rh compare` values
- Ran `rh compare --group main --metric design_hit --ref "Additive ridge"`; it rewrote `results/tables/compare_main_design_hit.csv` (was reference Random; that output is still in `compare_main_design_hit_ref_random.csv`).
- Table III, Pairwise vs Additive design_hit at L15_A4_K1, L15_A4_K2, L20_A20_K1: now `\rhval{cmp/main/pairwise-ridge/<task>/design_hit/delta|paired_p}`. Values −0.52 (p 0.003), −0.08 (p 0.34), −0.04 (p 0.48): the same magnitudes and p-values as before, but the sign is flipped because `rh compare` reports reference minus system, so the rows are now labelled Add.−Pair.
- Table III, Additive vs Random at L20_A20_K2 and K4: now `\rhval{cmp/main/random/<task>/design_hit/delta|paired_p}` (0.20, p 0.15; 0.10, p 0.30; unchanged).
- `0.08` (`p=0.34`) (results.tex, design_hit gain at L15_A4_K2): now the two means (0.10 to 0.18) and the `rh compare` paired p as `\rhval`.
- `p=0.15`, `0.30` (results.tex, Additive vs Random): now `\rhval` keys.
- `0.05` (results.tex, Welch test at L20_A20_K2): now `\rhval{cmp/main/random/l20_a20_k2/design_hit/welch_p:2}` for additive ridge; the pairwise-ridge Welch value has no key under this reference and is described in words.

### Results typed by hand that did match the registry: now `\rhval`
- Every mean and SD in the prose of abstract, results, ablations and conclusion (about 90 literals) and the run count `440` (abstract, setup) are now `\rhval{...}` keys. Expanding the macros and diffing against the old text shows every one prints the same digits as before.
- **No number in the text disagreed with the registry**, so no value was corrected.

### Left as typed
- Run settings (N = 250, 500, 1000, 2000, 4000) and the hyperparameter grids in method.tex: setup facts that the run commands and `hp_*` values record.
- "about 22 s" and "about 14 minutes" (setup.tex): integers below 100 are not checked. They come from run durations in the registry via `analysis/hyp.py`, not from a metric.
- Tables I, II, IV, V are still written by `analysis/tables_figs.py`, not by `rh table`; every cell is a mean or SD that the tracer recomputes from the registry.

## Rule 2: only real runs
- All 440 rows have a command, exit code 0 and a log. None was logged by hand, so nothing was rerun or dropped.

## Rule 3: reproducible metrics
- `research.yaml`: `fit_seconds` now has `nondeterministic: true`. It is the only wall-clock metric.
- Checked by rerunning 11 logged commands to `/tmp` (all seven systems, all three groups): `spearman`, `design_hit`, `design_gain`, `frac_mutants_better` and the `hp_*` values matched the registry to the last digit; only `fit_seconds` differed. No result metric is unseeded, so none needs a caveat.

## Rule 4: byline
- `paper/sections/author.tex`: not edited; the platform's version is committed as it was found.

## Rule 5: length and wording
- 7 pages (was 6; the inline Table III and longer sentences added one). No "state of the art" and no "novel" anywhere in the paper.

## Other files touched
- `paper/main.tex`: `rh paper build` added the `\input{generated/values}` line.
- `paper/generated/values.tex`, `paper/number_trace.json`: written by `rh`.
- `results/RESULTS.md`, `results/hypotheses.txt`, `experiments/PROTOCOL.md`: not changed; they still hold the rank correlations and chance-rate tests the paper now only points to.

## Final gates
- `rh paper build`: BUILD OK. `rh lit verify`: CITATIONS VERIFIED (11 of 11). `rh numbers`: ALL NUMBERS TRACED. `rh check`: READY.
