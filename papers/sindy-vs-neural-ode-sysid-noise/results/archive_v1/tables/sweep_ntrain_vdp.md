| Method | pred_nrmse | lqr_cost | n |
|---|---|---|---|
| Neural ODE (MLP) | _0.21 ± 0.10_ | 0.70 ± 0.08 | 25 |
| True model (oracle) | **0.00 ± 0.00** | **0.69 ± 0.07** | 25 |
| DMDc (linear LS) | 0.34 ± 0.03 | 0.70 ± 0.07 | 25 |
| SINDy (STLSQ) | 0.88 ± 3.26 | _0.69 ± 0.07_ | 25 |

Mean ± std over seeds; bold = best, underline = second. Directions: pred_nrmse ↓, lqr_cost ↓.
