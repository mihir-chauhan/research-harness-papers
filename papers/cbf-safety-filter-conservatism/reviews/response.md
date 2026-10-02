# Response to the final audit round

All 660 runs were re-executed after the metric change (code commit 745cf32, recorded in every run); the previous 630 runs are archived in `results/archive_round3/`. Earlier responses are in the git history of this file.

## Major

1. **Saturated-cell at-sample violations were round-off - fixed in the metric, re-run, text rewritten.** Confirmed by re-simulation (worst at-sample penetration about 1e-14 m in every double-integrator DT-CBF cell that the old table showed as non-zero). `method/run.py` now counts a violation only if clearance < -1e-9 m, for all three violation rates and all systems, and also records `sample_penetration`. With the tolerance the DT-CBF at-sample rate on the double integrator is 0.000 in every cell of Table IV except alpha=10, dt=0.2 (0.002: one real episode in 500, at-sample depth 0.014 m, not investigated and stated as such). Any-time rates are unchanged. Ablations, Limitations, abstract, conclusion and RESULTS.md now say that the saturated-cell failures are inter-sample too (gamma=1 only requires the successor on the boundary; the "why deep" mechanism carries "may"). Limitations records the earlier wrong reading. The dt=0.005 s probe was extended to the unicycle (30 extra runs), which shows the opposite regime there: DT-CBF violations are at the samples and remain at dt = plant step.
2. **Wrong bounds for alpha*dt<1 - fixed.** Text now gives the Table II maxima: any-time rate up to 0.618 (alpha=10, dt=0.05), mean worst penetration up to 0.016 m (alpha=2, dt=0.2), and 0.000 m at three decimals only for dt<=0.02. Same numbers in Results, abstract and conclusion.

## Minor

3. **Period, adjacent steps - fixed.** Now: steps up to dt=0.1 are within the seed spread, the last step (0.018 to 0.070) exceeds it.
4. **Hypothesis tally - fixed.** Introduction, Results, BRIEF.md and RESULTS.md agree: H2 refuted; H1, H3, H4 partly supported, with H1 and H4 failing their stated tests as written and H3 holding on the double integrator only. Each verdict in Results now names the stated test first.
5. **100 unicycle cells - fixed** (50).
6. **CT-CBF at-sample sentence - fixed.** Scoped to the gains of Table IV; the alpha=0.5, dt=0.2 cell is mentioned as also having at-sample violations.
7. **Run time - fixed.** "typically under one second (a few seconds at most)"; registry durations in this round: median 0.4 s, one run 4.8 s.
8. **Pre-registration claims - fixed.** "as stated in the proposal"; "fixed before running" removed; Limitations states that hypotheses were first committed together with the first results and that the round-1 script default was dt=0.1 s.
9. **Design-order confound - fixed.** Named in the abstract, the H2 verdict, Method, Limitations and conclusion ("first-order discrete-time condition" vs "second-order continuous-time filter"). A high-order DT-CBF was not implemented (out of budget for this round); stated.
10. **"One linear constraint" - fixed.** Now one scalar constraint with a closed-form projection (half-space / ball exterior).
11. **0.679 m - fixed.** Called "mean worst penetration" everywhere (table captions define it as the mean over seeds of each seed's deepest violation); the single-seed maximum 0.760 m is in RESULTS.md.
12. **Singletary et al. - fixed.** "analytically and with supporting experiments".
13. **Table I legibility - fixed.** Systems are registered under short names (Nominal, Braking, CT-CBF, DT-CBF; defined in Setup and the caption); the table now scales to about 85% instead of being unreadable. Tables III and V were transposed to single-column tables at footnotesize.

## Found in the self-audit

- Table V (braking threshold) was captioned "barrier level" but used the axle metrics; it now uses the barrier-level metrics (values on these rows are identical).
- "DT-CBF was not safer on either plant" contradicted the one cell where it is lower; abstract and conclusion now say "lower in one grid cell only".
- "at most 0.035 m" for unicycle DT-CBF depth ignored the alpha=1, dt=0.2 cell; now "at most 0.043 m over the whole grid".
- "nearly zero for alpha<=1" is exactly zero; "grows" replaced by "does not decrease".
- Removed an unverifiable anecdote about an early version and two mechanism sentences without a run; the unicycle Euler-successor explanation carries "may" and "consistent with".
- PROTOCOL.md said 600 runs; it now lists the groups and 660 runs.
- Setup now states that time to goal is resolved to dt and how the plants are integrated.
