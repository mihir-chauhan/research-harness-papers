| Method | Task | success_rate | success_rate_far | control_effort | time_to_upright | n |
|---|---|---|---|---|---|---|
| EnergyShaping-LQR | pendulum | **0.98 ± 0.04** | **0.96 ± 0.10** | **10.78 ± 1.66** | **2.25 ± 0.27** | 5 |
| iLQR-Quad | pendulum | 0.80 ± 0.08 | 0.52 ± 0.16 | 17.24 ± 3.68 | 2.75 ± 0.30 | 5 |
| iLQR-Quad+Energy | pendulum | 0.95 ± 0.04 | 0.88 ± 0.08 | _12.23 ± 2.20_ | 2.33 ± 0.20 | 5 |
| iLQR-Energy (ours) | pendulum | _0.95 ± 0.04_ | _0.88 ± 0.08_ | 12.24 ± 2.22 | _2.33 ± 0.20_ | 5 |
| EnergyShaping-LQR | cartpole | 0.97 ± 0.04 | 0.93 ± 0.10 | _54.91 ± 3.66_ | 2.70 ± 0.12 | 5 |
| iLQR-Quad | cartpole | _1.00 ± 0.00_ | _1.00 ± 0.00_ | 74.77 ± 3.48 | _1.71 ± 0.07_ | 5 |
| iLQR-Quad+Energy | cartpole | 1.00 ± 0.00 | 1.00 ± 0.00 | 69.52 ± 2.44 | **1.66 ± 0.07** | 5 |
| iLQR-Energy (ours) | cartpole | **1.00 ± 0.00** | **1.00 ± 0.00** | **42.03 ± 6.03** | 1.79 ± 0.06 | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: success_rate ↑, success_rate_far ↑, control_effort ↓, time_to_upright ↓.
