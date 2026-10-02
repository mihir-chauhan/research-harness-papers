# Proposal
**Question.** Does replacing/augmenting the quadratic running cost of iLQR-MPC by a penalty on deviation of mechanical energy from its upright value improve swing-up from random initial states, and how sensitive is it to weights?

**Hypotheses** (see research.yaml): H1 success rate higher than quad; H2 lower control effort; H3 lower weight sensitivity; H4 on par with energy-shaping+LQR.
Refuted if: H1 no higher success on both tasks; H2 effort not lower; H3 spread across weights not smaller; H4 clearly worse success or slower.

**Method.** iLQR-MPC (numpy), horizon 30 at dt=0.05 s, same quadratic terminal cost for all MPC variants; running cost differs. Baselines: iLQR-Quad, iLQR-Quad+Energy, EnergyShaping-LQR (Astrom-Furuta, reimplemented).
**Tasks.** Torque-limited pendulum (|u|<=3 < mgl), cart-pole (|F|<=8, track +-2.4). 20 random initial states per seed, 5 seeds.
**Metrics.** success rate (1 s upright hold at end of 6 s), success on far starts (|theta0|>pi/2), control effort sum u^2 dt, time to upright (failures counted as 6 s), solve ms.
**Ablation/sensitivity.** sweep of wE; sweep of quadratic state-cost scale.
