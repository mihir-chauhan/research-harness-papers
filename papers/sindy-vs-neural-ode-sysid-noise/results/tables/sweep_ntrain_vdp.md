| Method | pred_nrmse | pred_nrmse_h5 | lqr_cost | lqr_fail | mpc_cost | mpc_fail | support_f1 | n |
|---|---|---|---|---|---|---|---|---|
| DMDc (linear LS) | 0.34 ± 0.03 | 0.09 ± 0.01 | 0.70 ± 0.07 | _0.00 ± 0.00_ | **1.33 ± 0.13** | _0.00 ± 0.00_ | — | 25 |
| Neural ODE (MLP) | _0.20 ± 0.10_ | 0.06 ± 0.03 | 0.70 ± 0.07 | 0.00 ± 0.00 | 1.41 ± 0.11 | 0.00 ± 0.00 | — | 25 |
| True model (oracle) | **0.00 ± 0.00** | **0.00 ± 0.00** | **0.69 ± 0.07** | 0.00 ± 0.00 | _1.40 ± 0.14_ | 0.00 ± 0.00 | — | 25 |
| SINDy (STLSQ) | 0.86 ± 3.19 | _0.01 ± 0.02_ | _0.69 ± 0.07_ | **0.00 ± 0.00** | 1.42 ± 0.15 | **0.00 ± 0.00** | **0.54 ± 0.14** | 25 |

Mean ± std over seeds; bold = best, underline = second. Directions: pred_nrmse ↓, pred_nrmse_h5 ↓, lqr_cost ↓, lqr_fail ↓, mpc_cost ↓, mpc_fail ↓, support_f1 ↑.
