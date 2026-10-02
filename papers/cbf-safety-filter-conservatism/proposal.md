# Proposal

**Question.** How do alpha and dt affect safety violations and conservatism for (a) CT-CBF at discrete steps, (b) discrete-time CBF, (c) a distance-threshold braking heuristic, on a double integrator and a unicycle with three circular obstacles?

**Hypotheses** (see research.yaml): H1 CT-CBF violations grow with dt and alpha; H2 DT-CBF is safer than CT-CBF at large dt at the cost of time to goal; H3 larger alpha lowers time to goal and clearance; H4 braking heuristic violates on the double integrator while CBF filters at moderate settings do not.

**Method.** One closed-form constraint, numpy only. Baselines: nominal, CT-CBF (reimplemented), braking heuristic. Tasks: double_integrator, unicycle. Metrics: violation_rate, success_rate, time_to_goal, min_clearance, worst_penetration. 5 seeds x 100 scenarios.

**Refutation.** H1: violation not increasing with dt/alpha. H2: DT-CBF violation >= CT-CBF at large dt. H3: time to goal not decreasing with alpha. H4: heuristic violation 0 or CBF violations > 0.

**Ablations.** alpha sweep, dt sweep, braking threshold sweep, obstacle selection (nearest vs most critical).
