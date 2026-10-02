| Method | pred_nrmse | pred_nrmse_h5 | lqr_cost | lqr_fail | mpc_cost | mpc_fail | support_f1 | n |
|---|---|---|---|---|---|---|---|---|
| DMDc (linear LS) | 1.02 ± 0.05 | 0.34 ± 0.02 | 32.59 ± 5.00 | 0.84 ± 0.10 | 21.50 ± 5.02 | 0.77 ± 0.14 | — | 25 |
| Neural ODE (MLP) | 0.71 ± 0.28 | 0.14 ± 0.11 | 129.28 ± 329.09 | 0.23 ± 0.42 | 27.47 ± 45.94 | 0.22 ± 0.39 | — | 25 |
| True model (oracle) | **0.00 ± 0.00** | **0.00 ± 0.00** | **1.07 ± 0.19** | _0.00 ± 0.00_ | **2.44 ± 0.37** | _0.00 ± 0.00_ | — | 25 |
| SINDy (STLSQ) | _0.21 ± 0.16_ | _0.03 ± 0.01_ | _1.13 ± 0.22_ | **0.00 ± 0.00** | _2.57 ± 0.43_ | **0.00 ± 0.00** | **0.40 ± 0.11** | 25 |

Mean ± std over seeds; bold = best, underline = second. Directions: pred_nrmse ↓, pred_nrmse_h5 ↓, lqr_cost ↓, lqr_fail ↓, mpc_cost ↓, mpc_fail ↓, support_f1 ↑.
