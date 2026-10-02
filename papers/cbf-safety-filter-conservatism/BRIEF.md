# Brief: class-K gain and sampling period in one-constraint CBF safety filters

**Question.** How do the class-K gain alpha and control period dt affect safety violations and conservatism (time to goal, minimum clearance) for a continuous-time CBF applied at discrete steps (CT), a discrete-time CBF condition (DT), and a distance-threshold braking heuristic, on a double integrator and a unicycle avoiding three circular obstacles?

**Hypotheses.** H1 CT violations grow with dt and alpha. H2 DT is safer than CT at large dt but slower. H3 larger alpha lowers time to goal. H4 the heuristic violates on the double integrator while CBF filters at moderate settings do not. (Outcomes in the final round: H2 refuted; H1, H3, H4 partly supported, with H1 and H4 failing their stated tests as written (H1 holds only as a joint effect in the post-hoc grid, H4 only for CT-CBF) and H3 holding on the double integrator only; see results/RESULTS.md.)

**Method.** numpy, closed-form single-constraint projections; ZOH at dt, plant at 0.005 s; DT-CBF imposed on the exact ZOH successor (DI) / Euler successor of the look-ahead point (unicycle). Defaults alpha=2, dt=0.05, braking threshold 1.0 (not tuned; in the first round the script default was dt=0.1, since then dt is passed explicitly). Decision: DI CBF filters use the most-critical obstacle (min first-order margin); nearest-obstacle is an ablation (see `rh decide`).

**Baselines.** Nominal (unfiltered), CT-CBF (reimplemented), Braking (heuristic); the method row is DT-CBF (reimplemented). Decision: on the double integrator CT-CBF is the second-order (high-order) condition and DT-CBF a first-order condition on position; this asymmetry is disclosed as a confound of H2. **Tasks.** double_integrator, unicycle; 5 seeds x 100 episodes. **Metrics.** violation_rate, success_rate, time_to_goal, min_clearance, worst_penetration, barrier_violation_rate, barrier_penetration, sample_violation_rate, sample_penetration; a violation is a clearance below -1e-9 m for every system.

**Ablations.** full alpha x dt grid (one-factor sweeps are slices), any-time vs at-sample violations with a dt=0.005 s probe on both plants, braking threshold sweep, obstacle selection.

**Out of scope.** Input limits, disturbances, model mismatch, multiple simultaneous constraints, learned CBFs, hardware.
