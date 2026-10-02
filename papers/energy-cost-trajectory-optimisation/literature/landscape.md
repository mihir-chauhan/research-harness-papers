# Landscape

**Trajectory optimisation / MPC.** iLQR/DDP in a receding-horizon loop is a standard tool for nonlinear control [tassa2012synthesis]; Gauss-Newton and SQP views of iLQR are given in [roulet2022iterative, abhijeet2025sequential]. Sampling-based MPC (MPPI) [williams2017information] is the other common option. Cost design inside MPC is usually quadratic; stage-cost shaping has been studied from a suboptimality viewpoint in [beckenbach2019model].

**Energy-based swing-up.** The classic energy-shaping controller drives the pendulum energy to its upright value and hands over to a local stabiliser [strm2000swinging]. Its parameters are hard to choose and have been tuned by search [lee2019enhancement]; a reachability analysis of a switched energy/LQR controller on the cart-pole is in [jaffar2026reachability]. The pendulum as a benchmark: [boubaker2012inverted]. Tooling: [andersson2019casadi].

**Gap.** In the literature we looked at, energy shaping appears as a standalone feedback law, and MPC appears with quadratic costs. We did not find a controlled comparison of an energy-deviation running cost inside iLQR-MPC against both, with weight-sensitivity. This is a limited search (a few queries), so we make no novelty claim.
