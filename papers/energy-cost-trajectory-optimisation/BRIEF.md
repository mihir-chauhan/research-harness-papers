# Energy-deviation running cost for iLQR-MPC swing-up

## Question
Does a physics-based running cost (penalty on deviation of mechanical energy from the upright energy, optionally plus the quadratic cost) improve iLQR-based MPC swing-up of a pendulum and a cart-pole, relative to the quadratic cost and the classic energy-shaping+LQR controller?

## Hypotheses
H1 higher success rate than quadratic; H2 lower control effort; H3 less sensitivity to its weight; H4 comparable to energy shaping+LQR. Each falsifiable as in `proposal.md`/`research.yaml`.

## Method
numpy iLQR (Gauss-Newton Hessian, clipped controls), receding horizon 30 steps of 0.05 s, 4 iterations/step warm-started. Systems: iLQR-Quad, iLQR-Energy (ours), iLQR-Quad+Energy, EnergyShaping-LQR (reimplemented).
## Tasks / metrics
Pendulum and cart-pole, 20 random initial states x 5 seeds; success rate, far-start success, control effort, time to upright, solve time.
## Ablations
Sweeps of the energy weight and of the quadratic cost scale (3 seeds). Added in the fix round: a tuned comparison (each cost at its best swept weight, picked on seeds 0-2, seeds 3-4 added) and a diagnostic of the two state-cost terms under the combined cost.
## Out of scope
Hardware, model mismatch/noise, hard constraint handling, learned costs, theory guarantees, double pendulum.

## Decisions / status
Default weights set by hand (the a-priori status rests on an unlogged pilot); sweeps (3 seeds) are not used for the main table. Outcome: H2 supported at default weights but the cart-pole effort gap is mostly a product of the default Q (42.0 vs 48.6 after tuning q), H1/H3 not supported, H4 mixed (see results/RESULTS.md). Run driver bug (bash 3.2 assoc arrays mislabelled runs) found and fixed; mislabelled runs discarded and everything re-run.
