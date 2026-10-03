| Method | Task | success | collision | upper_frac | mode_balance | n |
|---|---|---|---|---|---|---|
| MSE-MLP | bimodal50 | 0.75 ± 0.06 | 0.25 ± 0.06 | _0.52 ± 0.11_ | 0.81 ± 0.12 | 10 |
| GMM head | bimodal50 | **1.00 ± 0.00** | **0.00 ± 0.00** | **0.52 ± 0.04** | _0.93 ± 0.05_ | 10 |
| DDPM head | bimodal50 | _1.00 ± 0.00_ | _0.00 ± 0.00_ | 0.51 ± 0.03 | **0.95 ± 0.03** | 10 |
| MSE-MLP | bimodal80 | 1.00 ± 0.01 | 0.01 ± 0.01 | **1.00 ± 0.00** | 0.00 ± 0.00 | 10 |
| GMM head | bimodal80 | **1.00 ± 0.00** | **0.00 ± 0.00** | 0.81 ± 0.02 | **0.38 ± 0.05** | 10 |
| DDPM head | bimodal80 | _1.00 ± 0.00_ | _0.00 ± 0.00_ | _0.82 ± 0.02_ | _0.36 ± 0.03_ | 10 |
| MSE-MLP | unimodal | **1.00 ± 0.00** | **0.00 ± 0.00** | **1.00 ± 0.00** | **0.00 ± 0.00** | 10 |
| GMM head | unimodal | _1.00 ± 0.00_ | _0.00 ± 0.00_ | _1.00 ± 0.00_ | _0.00 ± 0.00_ | 10 |
| DDPM head | unimodal | 1.00 ± 0.00 | 0.00 ± 0.00 | 1.00 ± 0.00 | 0.00 ± 0.00 | 10 |

Mean ± std over seeds; bold = best, underline = second. Directions: success ↑, collision ↓, upper_frac ↑, mode_balance ↑.
