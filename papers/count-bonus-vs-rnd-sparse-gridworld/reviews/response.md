# Response to the second audit

All experiments were repeated for this round: 492 runs through `rh run` from commit 24c3e27 (which contains the code), about 20 CPU-minutes. The 351 earlier rows are superseded in the registry and no longer feed any table or figure. Numbers below are from `results/tables/`.

1. **Major — RND normaliser divides by a near-zero std (method/run.py, Eq. 2; abstract, H1-H3, ablations, conclusion).**
   Fixed in the code, re-run, and all RND claims rewritten.
   - `RND.bonus` now has a guard: no intrinsic signal (b = 1) for the first W = 64 errors, then b = min(e/(sigma + 1e-8), 5). W and c were fixed a priori and recorded with `rh decide`; they were not tuned on results. Eq. (2) and `method/DESIGN.md` describe exactly this.
   - The old normaliser is kept as a flag (`--warmup 0 --clip 0`) and reported as the ablation "RND, unguarded normaliser (v1)" on all eight tasks. It reproduces the old RND numbers exactly (e.g. 69777 steps on room_4, 2/5 found) and the auditor's diagnosis: 20 of 40 runs have a bonus above 1e4 in the first 100 steps (max 1.44e7, |Q| up to 3.62e6), 1 of those 20 finds the reward (chain_10, 28656 steps), all 20 others find it (Table IV, Fig. 2, `abl_diag_per_run.md`).
   - To isolate the mechanism, two more variants were run on all tasks: clip only (39/40 found, no spike) and warm-up only (38/40 found, no spike). A clip sweep (c = 2, 5, 20, none) is Table V.
   - New headline for RND: with the guard it finds the reward in 39/40 runs but is slower than the count bonus and than the penalty-only control on every task. H1-H4 verdicts were redone with the registered tests (H1 supported as stated but explained by the offset; H2 supported; H3 not supported; H4 supported for TV time only). `results/RESULTS.md` and `results/VERDICT.md` were regenerated.

2. **Major — "normalised bonus stays at order one" (ablations.tex).**
   The sentence is deleted. Every run now logs bonus diagnostics (max, max over the first 100 steps, median, share of steps with b > 1, share clipped, largest |Q|). Table IV reports them: the guarded bonus has median 0.0005 and exceeds 1 on a share of 0.018 of the steps; the unguarded one reaches 1.44e7. The early blow-up is reported as the cause of the failed seeds of the first version. The remaining explanation of why normalised RND is slower than no bonus is marked as untested ("may").

3. **Minor — abstract: count vs penalty-only "only on chain_10 and chain_20".**
   Rewritten: the penalty-only control is within one standard deviation of the count bonus on every noise-free task, with the test now run (`rh compare --ref "Step penalty only (optimistic init)"`, Welch p >= 0.288, Table II). The one task with a difference (room_4_tv, p < 0.001 uncorrected) is reported in H1 with a caveat.

4. **Minor — conclusion: "the bonus systems found a sparse reward far faster".**
   Now "the count bonuses and the penalty-only control"; RND is described separately.

5. **Minor — H3: "TV attracts visits (0.10 for RND)" and framing.**
   The 0.10 came from the stuck seeds of the unguarded normaliser; it is gone from the paper. With the guard all RND seeds succeed on both TV tasks and the TV share is 0.062 / 0.025 (Table III). The split for the unguarded variant is kept in the repository (`results/tables/tv_frac_unguarded.md`: 0.062 for found seeds, 0.155 for not-found seeds on chain_20_tv). The introduction, related work, H3 and abstract now say that RND is designed to be robust to noisy-TV stochasticity, that our token set is finite, and that no forward-model bonus is among the systems, so non-reproduction is the expected outcome. Two noisy-TV references were added (Mavor-Parker et al. 2021, Jarrett et al. 2022).

6. **Minor — H2 is not evidence for the count signal.**
   The H2 paragraph now gives the penalty-only vs RND comparison (Table II, Welch p < 0.05 on five of six noise-free tasks, 0.062 on chain_10) and says so in its heading.

7. **Minor — Fig. 2 caption and labels, Table I tie marking, Fig. 1 legend.**
   The harness ablation figure with the delta labels is removed; Fig. 2 is now a per-run scatter (early bonus vs time to first reward) drawn by `method/make_tables.py`. Table I is a compact systems-by-tasks table built from the aggregate that `rh table --group main` writes (`main_agg.csv`); bold marks the lowest mean of a column and all ties are bold. Fig. 1 is redrawn one column wide on a log axis with the individual seeds and a larger legend. All tables are set at footnotesize or close to it (Table I about 7 pt) instead of being shrunk.

8. **Minor — provenance (261 rows with a commit that lacks the code; pilot not in the registry).**
   All runs were repeated from commit 24c3e27 after the code was committed; old rows are superseded with `rh supersede`. Non-RND systems reproduce their earlier numbers exactly. The seed-100 pilot is logged in group `pilot` (12 runs: count and RND bonuses without the offset fail on chain_40 and room_6). The README note is updated. Each run now prints its configuration and metrics and records its full config in the registry.

9. **Minor — VERDICT ablation row "missing"; uncited claim in the introduction.**
   The ablation variants are logged in group `main` and `research.yaml` names the group, so `rh verdict` now matches all four ablation rows. The sentence about published comparisons now cites Taiga et al. (2109.11052) for what that paper reports.

Other changes found in the self-audit:
- References: 7 -> 13 verified (added Strehl & Littman 2008, Martin et al. 2017, Rashid et al. 2020, Taiga et al. 2021, Mavor-Parker et al. 2021, Jarrett et al. 2022).
- The beta-sweep table and the K figure were moved out of the paper to stay within six pages; the beta result is one sentence pointing to `results/tables/sweep_beta_perconfig.md`, the K sweep is Table VI with a Welch test added.
- Sweep cells at the default value (beta 0.1, K 16, clip 5) reuse the `main` runs instead of repeating them; the ablation no longer duplicates method runs in a second group.
- The spike threshold (1e4) was chosen after looking at the data (early maxima are either below 122 or above 1.4e6); the paper says so.
- Not done: a tuned optimistic epsilon-greedy baseline, a forward-model (curiosity) bonus, stochastic dynamics. These are listed as limitations.
