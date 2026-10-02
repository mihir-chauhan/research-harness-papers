| Method | ret_nominal | ret_w100 | ret_ood | ret_robust | n |
|---|---|---|---|---|---|
| No randomisation | **500.00 ± 0.00** | 389.12 ± 28.75 | 243.19 ± 21.85 | 386.59 ± 16.59 | 5 |
| Uniform DR narrow (w=0.25) | _500.00 ± 0.00_ | 440.18 ± 29.22 | 292.36 ± 11.34 | 418.10 ± 10.98 | 5 |
| Uniform DR wide (w=1.0) | 500.00 ± 0.00 | _498.47 ± 1.71_ | _411.98 ± 34.30_ | _470.41 ± 11.70_ | 5 |
| Success-gated curriculum DR | 500.00 ± 0.00 | **499.27 ± 0.75** | **412.89 ± 38.93** | **470.84 ± 13.07** | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: ret_nominal ↑, ret_w100 ↑, ret_ood ↑, ret_robust ↑.
