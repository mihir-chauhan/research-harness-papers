# Design
`method/run.py` simulates 100 randomised episodes per (system, task, seed), vectorised in numpy. Plant integrated at h=0.005 s; control held constant (ZOH) for dt. Horizon 30 s, goal tolerance 0.15.
- Double integrator: p'=v, v'=a; nominal a=1.5(g-p)-2.5v. Constraint h=|p-c|^2-r^2 (relative degree 2).
- Unicycle: controlled look-ahead point at L=0.15 ahead of the axle (obstacle radius inflated by L), nominal go-to-goal with heading alignment, v<=1, |w|<=3.
- **ct**: continuous-time condition evaluated at the sampled state. DI: HOCBF hdd+2a hd+a^2 h>=0 (one linear constraint, closed-form projection). Unicycle: hd+alpha h>=0.
- **dt**: discrete-time condition h_{k+1}>=(1-gamma)h_k, gamma=min(1,alpha dt), on the exact ZOH successor. DI: z+ = z+dt v+0.5 dt^2 a, ||z+||>=rho=sqrt(r^2+(1-gamma)h_k); radial projection of z+(a0) onto the sphere (closed form). Unicycle: Euler successor of the look-ahead point, same projection with rho^2=(1-gamma)|z|^2+gamma rho_infl^2. Only enforced at sample instants.
- **heur**: if clearance < dth (1.0) and closing, remove the inward nominal component and add braking KB=4 (DI) / scale velocity by clearance/dth (unicycle). Does not use alpha.
- Obstacle selection: unicycle filters and the heuristic use the nearest obstacle; DI CBF filters use the most critical obstacle (min psi1); `--select nearest` ablation. One constraint only; no input limits so the QP is always feasible.
- Reported: violation_rate (episodes whose clearance ever <0), success_rate, time_to_goal (30 s if not reached), min_clearance (mean over episodes of per-episode minimum), worst_penetration.

Also reported (round 3): barrier_violation_rate / barrier_penetration (clearance of the controlled point against the radius the barrier uses; for the unicycle the look-ahead point against R+L, so no 0.15 m buffer; identical to violation_rate for the double integrator) and sample_violation_rate (barrier-level check at control sample instants only).

Default dt=0.05 (script default equals the paper default). Round-1 runs (approximate DT-CBF, heuristic/nominal accidentally at dt=0.1) are archived in results/archive_round1 and are not used.

Round 4 (final audit round): every violation rate (`violation_rate`, `barrier_violation_rate`, `sample_violation_rate`) counts an episode only if its clearance falls below -TOL, TOL = 1e-9 m, for every system. Without the tolerance the DT-CBF with gamma=1 was counted as violating at sample instants although its successor lies on the boundary to about 1e-14 m (round-off of the radial projection). `sample_penetration` (deepest barrier-level penetration at control sample instants within a seed's 100 episodes) is reported so that this can be checked. Penetration depths are raw (no tolerance). Systems are registered under the short names Nominal, CT-CBF, DT-CBF, Braking. The dt=0.005 s probe now covers both plants. Round-3 runs are archived in results/archive_round3 and are not used.

Goal arrival is tested at control instants, so `time_to_goal` has resolution dt. The double-integrator plant step is exact for a constant input; the unicycle uses a midpoint step in the heading.
