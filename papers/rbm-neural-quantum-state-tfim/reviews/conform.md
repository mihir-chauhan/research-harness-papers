# Conformance report: numbers traced, constants declared

Scope: the paper's claims are unchanged. No experiment was run and no run was added to the registry. `rh numbers` went from 30 untraced numbers to 0; `rh check` prints READY.

## Rule 1: every number traced

How the selected-state statistics became registry values (needed for most lines below):

- Registry group `selected` (650 rows): `experiments/list_selected.py` lists the selected run of every (system, task, seed) again with `rh log --from-run` (lower relative energy error of the two starts, the rule of PROTOCOL.md). Metrics, config and provenance are copied by the harness; nothing was typed and nothing was re-run.
- `rh compare --group selected --metric rel_energy_error --ref "RBM alpha=2 SR"` (written to `results/tables/compare_selected_rel_energy_error.csv`) now gives the ratios and paired p-values that `experiments/make_tables.py` had computed itself. All 39 ratios and 39 p-values of Table II agree with it.

Untraced numbers, one line each:

- `1300` (abstract, introduction, setup): declared constant `main_runs`; the text prints `\rhval{const/main_runs}`.
- `300` (setup, limitations, ablations): declared constant `iterations`; the text prints `\rhval{const/iterations}`.
- `4096` (introduction): declared constant `hilbert_dim_max`; the text prints it as 2^12.
- `8.55` and `71` (abstract, results; ratio of means to Jastrow-SR): now `\rhval{cmp/selected/jastrow-sr/.../inv_ratio}` at 12/1.5 and 8/1. Same values.
- `496` and `68` (abstract, results; SGD-to-SR ratio): now `\rhval{cmp/selected/rbm-alpha-2-sgd/.../inv_ratio}` at 10/1.5 and 12/1. Same values.
- `400` and "about 3" (ablations; RBM-SR median over its L-BFGS value at 10/0.25 and 10/0.5): hand-computed ratios across two groups, which `rh compare` cannot give. Replaced by the two values of each pair with `\rhval` (4.4e-5 against 1.6e-5; 2.8e-5 against 6.9e-8).
- Table II (`t_wins.tex`): `586`, `139`, `9612`, `317`, `33162`, `496`, `38751`, `1509`, `424`, `76682`, `407`, `282`, `19277`, `8.55`, `255`: table unchanged; each cell is now traced to the `rh compare` statistic of group `selected`.
- Table VIII (`t_check.tex`): `1272` (count of finite main runs in a row label): removed from the label.
- Table VIII: `1773 / 1749` (reported / superseded run counts, summed by the table script): row replaced by two rows of the registry's own per-group counts (`\rhval{count/<group>/runs}`: 650 / 650 / 78 and 315 / 25 / 25 / 30, which sum to the old 1773). The superseded count is no longer printed; the superseded rows stay in the registry.

Derived numbers that were traced only by coincidence (the tracer matched some other value) and were also replaced:

- Results, H1: `1.47`, `2.37`, `1.59`, `3.80` (ratios to Jastrow-SR): now `\rhval{cmp/selected/jastrow-sr/...}`. Same values.
- Results, H1: `p=0.207`: now `\rhval{cmp/selected/mean-field-sr/tfim_n10_g0.50/.../paired_p:3}`. Same value.
- Results, H1: "within about 30%" (Jastrow-SR against Jastrow L-BFGS, a hand-computed percentage): deleted; the sentence now gives the two values at 10/1 and at the largest gap, 12/1 (1.7e-3 against 1.3e-3), with `\rhval`.
- Results, H2: `2.07`, `15 to 23`: now `\rhval{cmp/selected/rbm-alpha-2-sgd/...}`. Same values.
- Results, H2: `p <= 0.015`. **Text corrected to the registry:** the largest p-value is 0.0153 (8/1), which is above 0.015. The text now says "p at most 0.0153 (at 8/1)".
- Results, H2: "at most by a factor of about 5" (Jastrow SGD against SR at 12/0.5): replaced by the two medians with `\rhval` (3.2e-4 against 6.0e-5).
- Conclusion: "below a factor of 2.5": now "at most a factor of 2.37" (`\rhval`, the largest ratio at Gamma <= 0.5, as in the abstract).
- Abstract: `1.47`, `2.37`, `2.07`, fidelity `0.5`: now `\rhval`. Same values.
- Results and ablations: the means, medians, minima and maxima quoted from the tables (for example 1.7e-5 / 4.0e-5 / 7.9e-5 in H5, 0.59 and 0.26 infidelity, the start-S and start-B medians): now `\rhval` on groups `selected`, `main`, `main_b`, `exact_opt`, `sweep_samples`. All print the same digits as before.
- Results: "epsilon_E below 10^-4 at Gamma=0.5": now the largest of the four medians, 7.5e-5, by `\rhval`.
- Ablations: `8.1e-5` (start-S median of RBM alpha=2 SR at 10/0.75), `5.6e-4` (M=32 median), `2.4e-5` (median MC-to-exact gap): removed from the prose, which now points to Tables VI, VII and VIII. These are medians over the non-diverged seeds or of a per-run difference; the registry has no such statistic (its aggregate over a group with a diverged run is NaN).

Setup facts declared so the reviewers see them as constants (they were already passing by a coincidental match): `init_std` 0.01, `start_b_field` 0.5, `single_flip_fraction` 0.9, `global_flip_fraction` 0.1, `lbfgs_max_iterations` 1000, `significance_level` 0.05, `h4_window` 0.25, `large_error_threshold` 0.1.

Still traced by value match only, not by a key: the cells of the script-built tables that are medians over non-diverged seeds (Tables VI and VII), the MC-gap median, divergence and win counts, and run times (Table VIII). They are computed by `experiments/make_tables.py` from the registry and were not retyped; the tracer accepts them, but its stated source for such a cell is not the real one.

Other edits that follow from the above:

- `experiments/make_tables.py`: skips the `selected` copies when counting runs and run time; emits the two `\rhval` count rows. All other tables are byte-identical to the previous build.
- Setup section: one sentence says the selected runs are listed in group `selected` and that the tests are `rh compare` on it; "Run counts and times" became "Run counts per group and run times".
- `experiments/PROTOCOL.md`: describes group `selected` and the reproducibility limitation below.

## Rule 2: only real runs

- No change needed. Every ok row in the registry has a command behind it; the 40 rows without one are `supersede` control rows, which carry no metrics. The 650 `selected` rows are harness copies of `rh run` rows and keep their command and log.

## Rule 3: reproducible metrics

- `research.yaml`: `runtime_s` marked `nondeterministic: true` (wall-clock time). No result metric is marked.
- **A result metric is not fully reproducible from its seed.** The ED reference (`scipy` `eigsh` in `method/run.py`) is called without a start vector, so ARPACK draws one that the run seed does not control. The trained state, `energy` and `n_params` repeat exactly. `rel_energy_error`, `mc_energy_error`, `mz_error`, `mx_error` and `infidelity` depend on the reference and repeat only to its accuracy.
- Measured by re-running logged commands into /tmp (412 runs; nothing logged): all 400 main runs (both starts) of the four Gamma <= 0.5 tasks plus a sample of 12 runs from groups `main`, `main_b`, `exact_opt` and `tune_lr3`.
  - Everywhere except 10/0.25 the largest difference was 3.4e-10 absolute, inside the platform's tolerance (1e-6 relative or 1e-9 absolute).
  - At 10/0.25 the two lowest levels are nearly degenerate. 98 of 100 main runs were inside the tolerance; 2 were outside on `infidelity` by about 2e-6 relative: `d79bc5ba22` (RBM alpha=2 SR, seed 3, the method of record) and `55f673d9c9` (RBM alpha=1 SR, seed 4). Which runs fall outside can change from one repetition to the next.
  - Consequence: if the platform draws a 10/0.25 run, the re-execution can report a mismatch on `infidelity`. No number printed in the paper changes at its precision.
- Not fixed here: seeding the reference would change the code behind every logged run and require repeating all of them, which this task rules out. It is the first thing to fix in any further round (pass a fixed `v0` to `eigsh`).

## Rule 4: byline

- `paper/sections/author.tex` not edited; the platform's version is committed as it was found.

## Rule 5: length and wording

- 7 pages (was 6). No "state of the art", no "novel".

## Gates at the end

- `rh paper build`: BUILD OK. `rh lit verify`: CITATIONS VERIFIED (13 of 13). `rh numbers`: 675 checked, 0 untraced. `rh check`: READY, with the earlier warning that the verdict tier is below target (RBM alpha=4 SR beats the method of record at 10/1, as the paper states).
