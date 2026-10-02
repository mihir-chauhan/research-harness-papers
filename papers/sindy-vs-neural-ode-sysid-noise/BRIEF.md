# System identification for control under measurement noise
Question, hypotheses H1-H3, baselines, tasks, metrics, ablations: see proposal.md (same content).
## Decisions
- Systems: inverted damped pendulum (unstable equilibrium, theta''=9.81 sin theta - 0.5 theta' + u) and Van der Pol (mu=1) with additive input; dt=0.05, 40-step trajectories, piecewise-constant random inputs.
- Noise: Gaussian on measured states, std = level x per-state std of clean data (levels 0, 0.02, 0.05, 0.1).
- Controllers: discrete LQR from the identified model's linearisation at the origin; MPC = CEM sampling planner (horizon 12) over the identified model with LQR terminal cost. Cost evaluated on the true system.
- Tuning: no tuning on the evaluation seeds beyond a fixed lam=0.05 (a sweep is reported separately as sensitivity).
- Out of scope: output feedback / state estimation, large nets, real data, guarantees.
- Fix round 2: the small-data clause of H1 is judged by the registered criterion (refuted on Van der Pol at N=200: two divergent SINDy seeds); capped LQR runs are diagnosed with registered sanity runs (group diag_lqr) instead of being explained by assumption; tables were restructured for legibility (main table two-column, sweeps with rows = size / lambda).
