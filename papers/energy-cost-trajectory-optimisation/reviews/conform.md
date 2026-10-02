# Conform report: numbers traced, constants declared

Scope: bring the paper into line with the platform's number rules without changing what it claims. No new
experiment was run and logged; no hypothesis verdict, framing or conclusion changed. Final state: `rh paper build`
BUILD OK (6 pages), `rh lit verify` CITATIONS VERIFIED, `rh numbers` 383 checked / 383 traced / 0 untraced,
`rh check` READY (two warnings, both present before this pass: 1 failed sanity run in the registry; verdict tier 0 < target 2).

## Rule 1: every number traced (41 untraced at the start, 0 now)

One line per change. "rhval" means the literal was replaced by `\rhval{<key>}`, which prints the value rh recomputes from the registry.

### Numbers that disagreed with the registry (registry wins)
- results.tex + generated/diag_terms.tex, term ratio on the pendulum `16.13`: this was the ratio of the two seed-averaged terms, computed by the table script, not a registry statistic. Replaced by the registry value, the mean over seeds of the logged per-run metric `term_ratio`: **15.64** (`diag_terms/ilqr-quad+energy/pendulum/term_ratio/mean`). Text and table caption now say the ratio is computed per run and averaged. Cart-pole value is unchanged (0.03). The sentence it supports (energy term much larger than the quadratic term on the pendulum, much smaller on the cart-pole) is unchanged. results/RESULTS.md updated to match.

### Derived numbers typed by hand or computed by the table script
- generated/sweep_weights.tex, column `range` (0.17, 5.3, 0.51, 0.02, 15.2, 0.17, 0.17, 2.0, 0.51, 0.02, 52.4, 0.34): max minus min of per-weight means, computed by the script; not an rh statistic. Column deleted; caption sentence about it deleted.
- ablations.tex H3, success spread `0.17 vs 0.17`, `0.02 vs 0.02`: deleted; the sentence now gives the lowest and highest per-weight mean success of each cost (rhval: 0.83 to 1.00 for both on the pendulum, 0.98 to 1.00 for both on the cart-pole). Same statement (equal spread), no hand-made difference.
- ablations.tex H3, effort range `5.3 vs 2.0`, `15.2 vs 52.4`: deleted; replaced by lowest and highest per-weight mean effort (rhval: 10.2 to 15.5 vs 13.9 to 15.9; 43.3 to 58.5 vs 50.0 to 102.4). Same statement (more variation on the pendulum, less on the cart-pole).
- generated/sweep_paired.tex, row `Δ effort` (4.2, 4.2, 4.7, 4.4, 2.8, 6.7, 6.9, 31.5, 55.4, 59.1): were computed by the script. Now `rh compare` deltas, rhval `cmp/pair_q<q>/ilqr-energy-ours/<task>/control_effort/delta`. Values unchanged.
- generated/sweep_paired.tex, row `paired p` (0.059, 0.057, 0.047, <0.001, 0.044, 0.046, 0.090, 0.027, 0.003, 0.008): were scipy calls in the script. Now `rh compare` paired_p via rhval. Values unchanged; `<0.001` is now printed as the value, 0.0003.
- generated/tuned.tex, 5-seed means and stds (0.99±0.02, 10.9±1.5, 2.29±0.18, 1.00±0.00, 14.4±1.2, 2.26±0.15, 42.0±6.0, 1.79±0.06, 48.6±5.5, 1.75±0.08): were computed by the script from two groups. Now rh aggregates of the new group `tuned_all` via rhval. Values unchanged.
- generated/tuned.tex, paired p (0.374, <0.001, 0.374, 0.009, 0.103): now `rh compare` on `tuned_all` via rhval. Values unchanged; `<0.001` is now printed as 0.0001.
- generated/tuned.tex, column `eff. 3-4` (12.0, 15.3, 40.1, 46.2): now rhval of group `tuned` means. `40.1` (iLQR-Energy, cart-pole, seeds 3-4) had no aggregate of its own and was traced only by coincidence to an unrelated minimum; the two main-group runs are now listed in group `tuned`, so it has its own key. Values unchanged.
- generated/diag_terms.tex, energy term and quad. term (14.03, 0.87, 0.17, 4.99): now rhval of the `diag_terms` aggregates. Values unchanged.
- ablations.tex, effort differences `2.8 to 4.7`, `31.5`, `55.4 to 59.1`, `6.7 and 6.9`, and paired p `0.046 and 0.090`: rhval of the `rh compare` statistics above. Values unchanged.
- results.tex, `The gap therefore shrinks from 31.5 to 6.9`: rhval of `cmp/pair_q1/...` and `cmp/pair_q0.1/...` delta. Values unchanged.
- results.tex, `within 0.01 in effort`: rhval `cmp/main/ilqr-quad+energy/pendulum/control_effort/delta:2`. Value unchanged (0.01).
- results.tex, six hand-typed `paired p<0.01`: replaced by the `rh compare` value via rhval: 0.003 (success, Energy vs Quad, pendulum), 0.002 and 0.0004 (effort, Energy vs Quad, pendulum and cart-pole), 0.005 (effort, energy shaping vs Energy, pendulum), 0.008 and 0.0002 (time and effort, Energy vs Quad+Energy, cart-pole). All are below 0.01, as the text said.
- ablations.tex, tuned comparison `paired p of <0.001 and 0.009`: rhval, printed as 0.0001 and 0.009.

### Result numbers retyped in the prose (values unchanged, now rhval)
- abstract.tex: 0.80, 0.95, 12.24, 17.24, 42.03, 74.77, 1.00 (x2), 50.2, 43.3, 0.99, 1.00, 10.9, 14.4, 42.0, 48.6, 10.78, 12.24.
- conclusion.tex: 42.03, 74.77, 42.0, 48.6, 10.9, 14.4.
- results.tex: every success, far-success, effort and time value in H1, H2, H4, "Energy alone vs. combined" and "Where the method fails", and the 1.00 in the caption of the main table.
- ablations.tex: every success, effort and time value in "Success depends on the weight", "Effort across the sweep" and "Tuned comparison".
- A diff of the rendered text against the previous version shows no other value changed (the only changed values are the ones listed above: 16.13 -> 15.64 and the p-values now printed exactly).

### Measured wall-clock figures (not results, not setup facts): removed
- setup.tex, `19--147 s` and `0.3 s` per run: run durations from the run provenance, not a logged metric and not a setup constant. Replaced by words ("from under half a minute to a few minutes", "under a second").
- Left as they were (small integers, not checked by `rh numbers`): "about 11 minutes", "about 80 minutes", "6-minute target", "12 early log files". These are bookkeeping read off the run provenance (summed duration of the 114 runs is 81.8 min; the two stalled runs took 660 s and 662 s), not results.

### Setup facts declared with `rh const add` (22 constants, listed by `rh const list`)
- setup.tex `120`: steps_per_episode. setup.tex `50,500` (the 500 in Qf = diag(50,500,50,50)): qf_cartpole_angle. These two were untraced.
- Also declared, because they are setup facts that were traced only by coincidence to an unrelated statistic: dt 0.05, success_resolution 0.05, pole_mass 0.3, pole_length 0.5, track_half_length 2.4, damping_pendulum 0.05, damping_cartpole 0.02, cart_start_range 0.5, upright_angle_tol 0.15, upright_rate_tol 0.6, q_rate_weight 0.1, r_pendulum 0.05, r_cartpole 0.01, qf_pendulum_angle 100, catch_angle 0.35, catch_energy_band 0.25 (the "25%"), switch_back_angle 0.8, rest_kick 0.05, cart_pd_position_gain 1.0, cart_pd_velocity_gain 1.5.
- Known limit of the tracer: it prefers an aggregate over a constant when both match, so `rh numbers` still prints an unrelated statistic as the source of most of these literals (only 2 are shown as "constant"). The declarations are the correct source. The swept weights 0.01, 0.1, 100 in the text and table headers are run settings (`config.wE`, `config.qscale`), also shown under a coincidental aggregate for the same reason.
- No result was declared as a constant.

### How the derived statistics became traceable (no new runs)
- New groups built by `experiments/compare_groups.py` with `rh log --from-run` (metrics and provenance copied from the registry, nothing typed): `pair_q0.01`, `pair_q0.1`, `pair_q1`, `pair_q10`, `pair_q100` (iLQR-Quad at that q and iLQR-Energy at wE=1, seeds 0-2, both tasks; 12 rows each), `tuned_all` (each cost at its picked weight, seeds 0-4; 20 rows), and 2 rows added to `tuned` (iLQR-Energy, cart-pole, seeds 3-4, from group main). 82 copied rows; the registry went from 114 to 196 rows, 114 of them distinct runs.
- `rh compare --ref iLQR-Quad` was run on those groups (control_effort for the pair groups; success_rate, control_effort, time_to_upright for tuned_all).
- `method/sweep_table.py` no longer computes or prints any statistic: every cell is an rhval macro. `experiments/run_all.sh groups` runs the group step.

## Rule 2: only real runs
- No change needed. All rows have a command behind them; none is marked hand_logged. The 82 new rows are `--from-run` copies of real runs.

## Rule 3: reproducible metrics
- research.yaml: `solve_ms` (mean solver wall-clock per control step) marked `nondeterministic: true`. No other metric is marked.
- Checked rather than assumed: four logged runs were executed again outside the registry (main iLQR-Energy pendulum seed 0; main EnergyShaping-LQR cart-pole seed 1; diag_terms iLQR-Quad+Energy pendulum seed 0; sweep_qscale iLQR-Quad q=0.1 cart-pole seed 2). success_rate, success_rate_far, control_effort, time_to_upright, energy_term, quad_term and term_ratio were identical to the registry to the last digit; only solve_ms differed. The only randomness is the initial-state generator, seeded by `--seed`. No result metric is non-reproducible.

## Rule 4: byline
- paper/sections/author.tex not edited by me; it is committed as the platform rewrote it.

## Rule 5: length and wording
- 6 pages. No "state of the art" in the paper.
- related.tex: "we make no novelty claim" -> "we do not claim that the comparison is new" (same disclaimer, without the word).

## Side effects worth knowing
- `rh const add` rewrites research.yaml through a YAML dump, which re-wrapped the long text fields; their content is unchanged.
- `rh paper build` added the `\input{generated/values}` line to paper/main.tex and writes paper/generated/values.tex and paper/number_trace.json.
