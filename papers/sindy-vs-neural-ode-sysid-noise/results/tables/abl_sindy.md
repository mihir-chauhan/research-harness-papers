| Method | Task | pred_nrmse | support_f1 | n_terms | n |
|---|---|---|---|---|---|
| SINDy w/o trig library | pendulum_noise0.05 | 1.224 ± 0.250 | — | 14.200 ± 1.643 | 5 |
| SINDy + SG smoothing, lam 0.3 | pendulum_noise0.05 | **0.057 ± 0.021** | **0.933 ± 0.149** | **4.800 ± 1.789** | 5 |
| SINDy + SG smoothing | pendulum_noise0.05 | _0.086 ± 0.069_ | _0.514 ± 0.273_ | _14.000 ± 5.831_ | 5 |
| SINDy (STLSQ) | pendulum_noise0.05 | 0.156 ± 0.062 | 0.397 ± 0.079 | 16.800 ± 4.147 | 5 |
| SINDy w/o trig library | vdp_noise0.05 | **0.011 ± 0.004** | **0.982 ± 0.041** | **5.200 ± 0.447** | 5 |
| SINDy + SG smoothing, lam 0.3 | vdp_noise0.05 | 0.052 ± 0.011 | _0.778 ± 0.208_ | _8.600 ± 3.507_ | 5 |
| SINDy + SG smoothing | vdp_noise0.05 | 0.053 ± 0.011 | 0.516 ± 0.057 | 14.600 ± 2.302 | 5 |
| SINDy (STLSQ) | vdp_noise0.05 | _0.018 ± 0.004_ | 0.546 ± 0.130 | 14.000 ± 3.674 | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: pred_nrmse ↓, support_f1 ↑, n_terms ↓.
