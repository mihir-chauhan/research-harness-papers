| Method | success_rate | success_auc | final_dist | episodes_to_50 | n |
|---|---|---|---|---|---|
| No communication | 0.071 ± 0.006 | 0.068 ± 0.009 | 0.765 ± 0.005 | 128000.000 ± 0.000 | 5 |
| Continuous vector (DIAL-style, reimplemented) | **1.000 ± 0.000** | **0.951 ± 0.001** | **0.085 ± 0.002** | **6400.000 ± 0.000** | 5 |
| Discrete tokens (Gumbel-softmax, reimplemented) | 0.678 ± 0.059 | 0.619 ± 0.039 | 0.249 ± 0.015 | 12800.000 ± 4525.483 | 5 |
| Templated language (proxy) | _0.931 ± 0.010_ | _0.887 ± 0.005_ | _0.195 ± 0.002_ | _6400.000 ± 0.000_ | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: success_rate ↑, success_auc ↑, final_dist ↓, episodes_to_50 ↓.
