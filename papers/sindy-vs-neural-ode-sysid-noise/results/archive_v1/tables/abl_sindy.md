| Method | Task | pred_nrmse | support_f1 | lqr_cost | mpc_cost | n |
|---|---|---|---|---|---|---|
| SINDy w/o trig library | pendulum_noise0.05 | 1.26 ± 0.26 | — | 18.32 ± 7.30 | 22.32 ± 11.42 | 5 |
| SINDy + SG smoothing, lam 0.3 | pendulum_noise0.05 | **0.10 ± 0.04** | **0.85 ± 0.23** | _1.08 ± 0.21_ | **2.41 ± 0.35** | 5 |
| SINDy + SG smoothing | pendulum_noise0.05 | _0.11 ± 0.06_ | _0.42 ± 0.09_ | **1.07 ± 0.21** | _2.41 ± 0.36_ | 5 |
| SINDy (STLSQ) | pendulum_noise0.05 | 0.15 ± 0.06 | 0.35 ± 0.06 | 1.10 ± 0.19 | 2.43 ± 0.42 | 5 |
| SINDy w/o trig library | vdp_noise0.05 | **0.07 ± 0.01** | **0.79 ± 0.07** | _0.69 ± 0.08_ | _1.40 ± 0.15_ | 5 |
| SINDy + SG smoothing, lam 0.3 | vdp_noise0.05 | 0.11 ± 0.02 | _0.68 ± 0.08_ | 0.70 ± 0.08 | 1.41 ± 0.14 | 5 |
| SINDy + SG smoothing | vdp_noise0.05 | 0.11 ± 0.02 | 0.50 ± 0.06 | 0.70 ± 0.08 | **1.38 ± 0.13** | 5 |
| SINDy (STLSQ) | vdp_noise0.05 | _0.07 ± 0.02_ | 0.47 ± 0.07 | **0.69 ± 0.08** | 1.42 ± 0.16 | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: pred_nrmse ↓, support_f1 ↑, lqr_cost ↓, mpc_cost ↓.
