| Method | Task | support_exact | coef_err | coef_err_oracle | false_pos | false_neg | runtime_s | n |
|---|---|---|---|---|---|---|---|---|
| SG-STLSQ (smoothed library) | lorenz_n2 | **0.85 ± 0.37** | **0.01 ± 0.00** | **0.00 ± 0.00** | **0.15 ± 0.37** | **0.00 ± 0.00** | **0.13 ± 0.04** | 20 |
| Spline-STLSQ (smoothed library) | lorenz_n2 | _0.85 ± 0.37_ | _0.01 ± 0.02_ | _0.00 ± 0.00_ | _0.15 ± 0.37_ | _0.05 ± 0.22_ | _0.16 ± 0.04_ | 20 |
| SG-STLSQ (smoothed library) | lorenz_n5 | **0.25 ± 0.44** | **0.03 ± 0.03** | **0.01 ± 0.01** | **0.85 ± 0.75** | **0.15 ± 0.37** | **0.12 ± 0.04** | 20 |
| Spline-STLSQ (smoothed library) | lorenz_n5 | _0.20 ± 0.41_ | _0.04 ± 0.03_ | _0.01 ± 0.01_ | _0.85 ± 0.67_ | _0.20 ± 0.41_ | _0.18 ± 0.08_ | 20 |

Mean ± std over seeds; bold = best, underline = second. Directions: support_exact ↑, coef_err ↓, coef_err_oracle ↓, false_pos ↓, false_neg ↓, runtime_s ↓.
