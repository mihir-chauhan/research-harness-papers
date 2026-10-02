| Method | Task | pred_nrmse | lqr_cost | mpc_cost | lqr_fail | n |
|---|---|---|---|---|---|---|
| Neural ODE (MLP) | pendulum_noise0.0 | 0.34 ± 0.15 | 1.09 ± 0.20 | 2.46 ± 0.34 | 0.00 ± 0.00 | 5 |
| True model (oracle) | pendulum_noise0.0 | **0.00 ± 0.00** | **1.07 ± 0.20** | _2.44 ± 0.40_ | _0.00 ± 0.00_ | 5 |
| DMDc (linear LS) | pendulum_noise0.0 | 1.03 ± 0.08 | 29.04 ± 4.46 | 18.80 ± 4.34 | 0.80 ± 0.16 | 5 |
| SINDy (STLSQ) | pendulum_noise0.0 | _0.05 ± 0.02_ | _1.07 ± 0.20_ | **2.37 ± 0.39** | **0.00 ± 0.00** | 5 |
| Neural ODE (MLP) | pendulum_noise0.02 | 0.42 ± 0.18 | 1.24 ± 0.29 | 2.94 ± 0.53 | 0.00 ± 0.00 | 5 |
| True model (oracle) | pendulum_noise0.02 | **0.00 ± 0.00** | **1.07 ± 0.20** | **2.44 ± 0.40** | _0.00 ± 0.00_ | 5 |
| DMDc (linear LS) | pendulum_noise0.02 | 1.03 ± 0.08 | 28.82 ± 4.51 | 18.62 ± 4.07 | 0.80 ± 0.16 | 5 |
| SINDy (STLSQ) | pendulum_noise0.02 | _0.06 ± 0.03_ | _1.07 ± 0.21_ | _2.45 ± 0.44_ | **0.00 ± 0.00** | 5 |
| Neural ODE (MLP) | pendulum_noise0.05 | 0.61 ± 0.14 | 2.27 ± 0.53 | 4.73 ± 2.57 | 0.00 ± 0.00 | 5 |
| True model (oracle) | pendulum_noise0.05 | **0.00 ± 0.00** | **1.07 ± 0.20** | _2.44 ± 0.40_ | _0.00 ± 0.00_ | 5 |
| DMDc (linear LS) | pendulum_noise0.05 | 1.02 ± 0.07 | 30.88 ± 4.88 | 19.78 ± 4.38 | 0.82 ± 0.13 | 5 |
| SINDy (STLSQ) | pendulum_noise0.05 | _0.15 ± 0.06_ | _1.10 ± 0.19_ | **2.43 ± 0.42** | **0.00 ± 0.00** | 5 |
| Neural ODE (MLP) | pendulum_noise0.1 | 0.85 ± 0.17 | 10.48 ± 7.51 | 16.83 ± 9.08 | 0.28 ± 0.39 | 5 |
| True model (oracle) | pendulum_noise0.1 | **0.00 ± 0.00** | **1.07 ± 0.20** | **2.44 ± 0.40** | _0.00 ± 0.00_ | 5 |
| DMDc (linear LS) | pendulum_noise0.1 | 1.00 ± 0.06 | 40.31 ± 6.21 | 27.03 ± 6.09 | 0.84 ± 0.11 | 5 |
| SINDy (STLSQ) | pendulum_noise0.1 | _0.46 ± 0.09_ | _1.28 ± 0.13_ | _2.79 ± 0.35_ | **0.00 ± 0.00** | 5 |
| Neural ODE (MLP) | vdp_noise0.0 | 0.10 ± 0.02 | _0.69 ± 0.08_ | 1.42 ± 0.10 | 0.00 ± 0.00 | 5 |
| True model (oracle) | vdp_noise0.0 | **0.00 ± 0.00** | **0.69 ± 0.08** | _1.40 ± 0.16_ | 0.00 ± 0.00 | 5 |
| DMDc (linear LS) | vdp_noise0.0 | 0.32 ± 0.02 | 0.70 ± 0.07 | **1.35 ± 0.17** | _0.00 ± 0.00_ | 5 |
| SINDy (STLSQ) | vdp_noise0.0 | _0.07 ± 0.01_ | 0.69 ± 0.08 | 1.41 ± 0.13 | **0.00 ± 0.00** | 5 |
| Neural ODE (MLP) | vdp_noise0.02 | 0.12 ± 0.03 | _0.69 ± 0.08_ | 1.41 ± 0.15 | 0.00 ± 0.00 | 5 |
| True model (oracle) | vdp_noise0.02 | **0.00 ± 0.00** | **0.69 ± 0.08** | _1.40 ± 0.16_ | 0.00 ± 0.00 | 5 |
| DMDc (linear LS) | vdp_noise0.02 | 0.32 ± 0.02 | 0.70 ± 0.07 | **1.35 ± 0.16** | _0.00 ± 0.00_ | 5 |
| SINDy (STLSQ) | vdp_noise0.02 | _0.07 ± 0.02_ | 0.69 ± 0.08 | 1.41 ± 0.17 | **0.00 ± 0.00** | 5 |
| Neural ODE (MLP) | vdp_noise0.05 | 0.19 ± 0.04 | 0.69 ± 0.07 | 1.41 ± 0.11 | 0.00 ± 0.00 | 5 |
| True model (oracle) | vdp_noise0.05 | **0.00 ± 0.00** | **0.69 ± 0.08** | _1.40 ± 0.16_ | 0.00 ± 0.00 | 5 |
| DMDc (linear LS) | vdp_noise0.05 | 0.33 ± 0.02 | 0.70 ± 0.08 | **1.32 ± 0.14** | _0.00 ± 0.00_ | 5 |
| SINDy (STLSQ) | vdp_noise0.05 | _0.07 ± 0.02_ | _0.69 ± 0.08_ | 1.42 ± 0.16 | **0.00 ± 0.00** | 5 |
| Neural ODE (MLP) | vdp_noise0.1 | _0.29 ± 0.06_ | 0.70 ± 0.07 | 1.40 ± 0.11 | 0.00 ± 0.00 | 5 |
| True model (oracle) | vdp_noise0.1 | **0.00 ± 0.00** | **0.69 ± 0.08** | 1.40 ± 0.16 | 0.00 ± 0.00 | 5 |
| DMDc (linear LS) | vdp_noise0.1 | 0.39 ± 0.03 | 0.71 ± 0.08 | **1.36 ± 0.15** | _0.00 ± 0.00_ | 5 |
| SINDy (STLSQ) | vdp_noise0.1 | 0.64 ± 1.25 | _0.69 ± 0.08_ | _1.39 ± 0.16_ | **0.00 ± 0.00** | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: pred_nrmse ↓, lqr_cost ↓, mpc_cost ↓, lqr_fail ↓.
