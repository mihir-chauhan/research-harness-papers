| Method | pred_nrmse | lqr_cost | n |
|---|---|---|---|
| DMDc (linear LS) | 1.02 ± 0.05 | 32.59 ± 5.00 | 25 |
| Neural ODE (MLP) | 0.89 ± 0.42 | 27.88 ± 42.53 | 25 |
| True model (oracle) | **0.00 ± 0.00** | **1.07 ± 0.19** | 25 |
| SINDy (STLSQ) | _0.19 ± 0.13_ | _1.13 ± 0.22_ | 25 |

Mean ± std over seeds; bold = best, underline = second. Directions: pred_nrmse ↓, lqr_cost ↓.
