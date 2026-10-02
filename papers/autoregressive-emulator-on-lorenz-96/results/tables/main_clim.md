| Method | stable_frac | survival_time | var_ratio | roughness_ratio | ks | n |
|---|---|---|---|---|---|---|
| Linear stencil (ridge) | **1.000 ± 0.000** | **200.000 ± 0.000** | **0.001 ± 0.000** | **0.001 ± 0.000** | 0.468 ± 0.002 | 5 |
| CNN K=1 | _1.000 ± 0.000_ | _200.000 ± 0.000_ | 1.003 ± 0.003 | 1.005 ± 0.007 | 0.002 ± 0.001 | 5 |
| CNN K=4 | 1.000 ± 0.000 | 200.000 ± 0.000 | 1.002 ± 0.004 | 1.005 ± 0.010 | _0.002 ± 0.002_ | 5 |
| CNN K=8 | 1.000 ± 0.000 | 200.000 ± 0.000 | _0.998 ± 0.003_ | _0.997 ± 0.006_ | **0.002 ± 0.001** | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: stable_frac ↑, survival_time ↑, var_ratio ↓, roughness_ratio ↓, ks ↓.
