# Conformance report: numbers traced, constants declared

No claim, experiment or framing was changed. No new runs were logged. One line per change.

## Numbers that `rh numbers` could not trace
- `10^{-7}` (method.tex, simulator-vs-gymnasium state difference): it is the output of `method/check_dynamics.py`, which is a result, not a setup fact, and is not a logged run. Removed the number; the sentence now says the simulator was checked against gymnasium over 30 steps and points to the script. (Re-running the script today prints 3.4e-07, so the removed figure was accurate.)
- `0.18` (ablations.tex, "no paired comparison against gate 0.8 is below p=0.18"): hand-typed bound. Deleted; the sentence now says no paired comparison is significant and gives the three p-values from `rh compare` as `\rhval{cmp/abl_curriculum/.../ret_robust/paired_p:2}`.

## Hand-typed derived numbers replaced (they passed the tracer only by coinciding with unrelated statistics)
- `p=0.96` curriculum vs wide DR on ret_robust (abstract.tex, results.tex): now `\rhval{cmp/main/success-gated-curriculum-dr/cartpole/ret_robust/paired_p:2}` (0.9593, prints 0.96).
- `p=0.97` curriculum vs wide DR on ret_ood (results.tex): now `\rhval{cmp/main/success-gated-curriculum-dr/cartpole/ret_ood/paired_p:2}` (0.9714, prints 0.97).
- `p=0.0007` H1, wide DR vs no DR on ret_robust (results.tex): now `\rhval{cmp/main/no-randomisation/cartpole/ret_robust/paired_p}` (prints 0.0006836).
- `0.19`, `0.22`, `0.85` gate ablation paired p vs gate 0.8 (ablations.tex): now `\rhval` of the three `cmp/abl_curriculum/.../paired_p:2` keys (same printed values).
- `p=0.003` and `p=0.004`, curriculum vs no DR and vs narrow DR on ret_robust (results.tex): DELETED. `rh compare --ref "Success-gated curriculum DR"` reproduces them (0.002984, 0.003847), but the registry keeps one reference per group and metric, and that slot is needed for the pre-registered H1 test (wide DR as reference). The sentence now says the curriculum is "higher than" no DR and narrow DR without a p-value; the means are in Table I.
- "about 70 runs" (setup.tex): registry has 76. Now `\rhval{count/runs}` "logged runs, one of them a smoke run".

## Text that disagreed with the registry (registry wins)
- "ret_robust differs by under 8 units" across the four gate variants (ablations.tex): the largest gap among the four is no gate (471.62) vs gate 0.95 (463.51), which is above 8. Reworded to what `rh compare` gives: each other variant differs from gate 0.8 by at most `\rhval{cmp/abl_curriculum/curriculum-gate-0.95/cartpole/ret_robust/delta:1}` (7.3) units. The conclusion (variants indistinguishable) is unchanged.
- All other numbers in the text were checked against `rh compare` / `rh values --list` and agree.

## Constants declared (`rh const add`, setup facts only, all read from method/run.py or research.yaml)
- eval_episodes_per_level=300, euler_step_tau=0.02, dynamics_check_steps=30, return_cap=500.
- mlp_inputs=4, mlp_hidden_units=8, mlp_outputs=1, mlp_parameters=49.
- cem_population=40, cem_envs_per_iteration=16, cem_elite_percent=20, cem_iterations=60, cem_noise_floor_decay=0.05, cem_noise_floor_const=0.01.
- curriculum_step_delta=0.05, curriculum_gate_rho=0.8, curriculum_w_max=1, ungated_rho=0, gate_high=0.95.
- width_narrow=0.25, width_half=0.5, eval_level_075=0.75, width_1p5=1.5, width_2=2, width_3=3.
- n_seeds=5, eval_shift_levels=6, sweep_widths=7.
- Note: the tracer still prints some of these setup facts against a coinciding aggregate (e.g. 300 against a median of ret_w200); the declared constant is the correct source.

## Rule 2: hand-logged rows
- None found. All 76 registry rows have a command, an exit code, a duration and an existing log file. Nothing replaced.

## Rule 3: reproducible metrics
- `research.yaml` `metrics:` lists only result metrics (ret_robust, ret_nominal, ret_ood, ret_w50, ret_w100) and the runs log no wall-clock or throughput metric, so nothing was marked `nondeterministic`.
- Result metrics are seeded (training `default_rng(seed)`, evaluation `default_rng(10000+seed)`). Re-executed two logged runs into /tmp without logging them (curriculum gate 0.8 seed 3; uniform DR width 3 seed 0): all 17 metrics identical to the registry in both. Only tested on this machine and numpy build.

## Other
- `paper/main.tex`: `rh paper build` added the line that inputs `generated/values.tex`. `research.yaml` was re-wrapped by `rh const add`; apart from the `constants:` block its content is identical.
- `results/tables/compare_*.csv` are unchanged (wide DR as reference in `main`, gate 0.8 in `abl_curriculum`).
- `paper/sections/author.tex`: not edited by me (platform rewrite left as is).
- Wording: no "state of the art" or "novel" in the paper. Length: 4 pages.
- `rh check` prints READY with one pre-existing warning (verdict tier 1 < target 2), which reflects the paper's negative result and was not touched.

## Final state
- `rh paper build`: BUILD OK. `rh lit verify`: CITATIONS VERIFIED. `rh numbers`: 194 checked, 0 untraced. `rh check`: READY.
