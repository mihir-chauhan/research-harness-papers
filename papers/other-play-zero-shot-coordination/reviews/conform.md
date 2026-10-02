# Conformance report

Scope: bring the paper into line with the platform rules without changing its claims. No new experiments were logged; the registry (`results/runs.jsonl`) is untouched.

## Rule 1: every number traced (`rh numbers`: 315 checked, 0 untraced)

Setup facts declared with `rh const add`:

- 380 (setup, results, limitations): declared `pair_payoffs_per_seed` (20 agents x 19 partners).
- 1500 (method, setup, Table V caption and header): declared `train_updates` (default `--steps`).
- 20, 64, 0.05, 1 (agents, batch, Adam lr, init std): declared `n_agents`, `batch_size`, `adam_lr`, `init_std_default`.
- 0.9, 0.5, prior (0.4, 0.3, 0.2, 0.1): declared `lever_distinct_payoff`, `safe_action_payoff`, `card_prior_0..3` (game definitions).
- 0.11 (basin threshold): declared `basin_threshold` (the constant in `experiments/init_check.py`).
- 99, 6, 2 (smoke-test seed and configurations, CPU threads): declared `smoke_test_seed`, `smoke_test_configs`, `cpu_threads`.
- Note: `rh numbers` had already matched several of these (0.9, 0.5, the prior, 0.05, 0.11) to unrelated aggregates that happen to share the value; they are declared anyway so the stated source is the right one. The tool still prints the coincidental aggregate for them.

Hand-typed results replaced by `\rhval{...}` (rendered values unchanged unless stated):

- abstract, conclusion: SP cross-play range 0.08--0.27 -> `main/self-play/{lever,safe}/cross_play/mean:2`.
- abstract, results, conclusion: "self-play at least 0.97" -> `main/self-play/signal/self_play/mean` (0.9775, the smallest of the three task means; same claim, exact bound).
- abstract: OP vs SP lever 0.15 vs 0.08 -> `main/{other-play,self-play}/lever/cross_play/mean:2`.
- abstract, results, limitations: lever Welch p=0.053 -> `cmp/main/self-play/lever/cross_play/welch_p:3`.
- abstract, results: OP vs population safe p=0.08 -> `cmp/main/population-fcp-style/safe/cross_play/welch_p:2`.
- results H1: SP self-play (0.991, 1.000, 0.978), cross-play (0.084, 0.268, 0.259), gap (0.907, 0.731, 0.718) -> `main/self-play/...` keys; self-play now printed at four significant figures (0.9907, 0.9998, 0.9775).
- results H1: "worst pair below 10^-3 everywhere" -> the three `main/self-play/<task>/cross_play_min/max` values (8.5e-6, 5.5e-5, 1.2e-4); the bound was hand-typed, the claim is unchanged.
- results H2: safe 0.500 vs 0.268, p=5e-4, d=6.4 -> `main/...` means, `cmp/main/self-play/safe/cross_play/{welch_p,cohen_d:1}` (p now printed as 0.0005307).
- results H2: signal 0.400 vs 0.259, "p<10^-4" -> means and `cmp/main/self-play/signal/cross_play/welch_p` (3.965e-5).
- results H2: lever 0.153+-0.057 vs 0.084+-0.018, d=1.6 -> `main/.../cross_play/{mean,std}:3`, `cmp/main/self-play/lever/cross_play/cohen_d:1`.
- results H2: OP self-play 0.727, frac. special 0.35 (SP 0.09), init fraction 0.33 -> `main/.../self_play`, `.../frac_special`, `init_check/other-play@init_std=1/lever/frac_init_above/mean:2`.
- results: OP safe 0.500, OP signal 0.400, self-play 0.40 vs 0.98 -> `main/other-play/...`, `main/self-play/signal/self_play/mean:2`.
- results H3: 0.487 vs 0.268, 0.337 vs 0.259, 0.088 vs 0.084, p=1e-5 (signal), p=0.063 (lever) -> `main/population-fcp-style/...` means and `cmp/main/population-fcp-style/{signal,lever}/cross_play/welch_p` (signal p now printed as 1.147e-5).
- ablations H4: 0.108+-0.017 vs 0.153+-0.057, p=0.16, frac. special 0 vs 0.35, SP 0.084, safe 0.500 each, p=6e-6 for a difference of -2e-5 -> `abl_symmetry/...` and `cmp/abl_symmetry/op-full-wrong-group/{lever,safe}/cross_play/{welch_p,delta}` (printed as 6.295e-6 and -2.457e-5).
- limitations: OP-full vs OP p=0.16 -> `cmp/abl_symmetry/op-full-wrong-group/lever/cross_play/welch_p:2`.
- ablations, population size: 0.268, 0.500, 0.255, 0.359, 0.084--0.108, OP 0.400 -> `sweep_popsize/population-fcp-style@pop_size=K/...`; added "(at K=16)" because 0.359 is the K=16 cell.
- ablations, init scale: 0.082--0.093, 0.179+-0.076, 0.104+-0.036, 0.712, 0.840, 0.35, 0.18, 0.33, 0.17 -> `sweep_init/...@init_std=...`, `main/other-play/lever/frac_special`, `init_check/...` keys.
- ablations, training length: 0.727, 0.941, 0.153, 0.151, 0.350 -> `main/other-play/lever/...` and `sweep_steps/other-play@steps=15000/lever/...`.

Deleted because no `rh compare` value or `\rhval` key exists:

- Table IV row "Welch p vs sd 4" (0.057, 0.096, 0.155, 0.477): computed by my own scipy call in `experiments/make_sweeps.py`. `rh compare` cannot test one configuration of a system against another. Row and scipy import removed from the script; table and figure regenerated from the registry (all other cells identical).
- ablations: "Welch p=0.096 for sd 0.5 vs 4, 0.155 for sd 1 vs 4" deleted for the same reason; the sentence now says no p-value is reported.
- abstract, limitations, conclusion, ablations: "not significant at five seeds" for the init-scale trend reworded to "a difference is not established at five seeds", since the paper no longer shows a test for it. This is the one place where the stated support is weaker than before; the claim itself (a tendency, not a tested effect) is the same.
- setup, limitations: "about 51 minutes in total (about 56 minutes of wall clock)" deleted. The summed `duration_s` in the registry is 51.5 min, so the figure agreed, but it is a hand-computed sum with no key; the 56 min had no registry source. The text still says the summed run time exceeded the 30-minute budget and points to `rh budget`.

Registry wins (text corrected):

- setup: "run durations from about 3 to 200 s" -> `runtime_s` min and max from the registry, 1.8 s and 181.6 s. The old figures came from the harness `duration_s` field (1.2 to 202.5 s), which has no key; "about 3" did not match its minimum.
- results, cost: "about 2 s (SP), 2.5 s (OP), 9 s (population)" -> lever-game means `main/<system>/lever/runtime_s/mean:1` = 2.2, 2.6, 9.4 s; the sentence now names the lever game.
- No result number (payoff, gap, fraction, p, d) disagreed with the registry.

## Rule 2: only real runs

- All 227 registry rows have a real `rh run` command; none was logged by hand. Nothing replaced.
- Checked every ok row against the `metrics:` line of its own log: all payoff metrics identical. Three kept rows from the earlier deduplication (main, Self-play signal seeds 3 and 4, Population signal seed 4) point at the other duplicate's log, so their `runtime_s` differs from that log; payoff metrics are identical.

## Rule 3: reproducible metrics

- `research.yaml`: `runtime_s` marked `nondeterministic: true`. No result metric is marked.
- Re-ran six logged commands (output to /tmp, not logged): main SP lever s0, main OP signal s3, main Population safe s2, abl OP-full lever s1, init_check sd 4 s4, sweep_init OP s2. Every result metric matched the registry to the last digit; only `runtime_s` differed. All randomness goes through one seeded `torch.Generator`; I found no unseeded randomness.

## Rule 4: byline

- `paper/sections/author.tex` not edited by me; the platform's rewrite is committed as found.

## Rule 5: length and wording

- 5 pages. No "state of the art" or "novel" in the paper.

## Final checks

- `rh paper build`: BUILD OK. `rh lit verify`: CITATIONS VERIFIED (10 of 10). `rh numbers`: 0 untraced. `rh check`: READY.
- Remaining `rh check` warnings, unchanged from before: one failed sanity run kept in the registry; verdict tier 1 below target 2.
