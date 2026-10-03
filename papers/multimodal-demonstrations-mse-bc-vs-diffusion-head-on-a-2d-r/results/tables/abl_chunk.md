| Method | success | collision | mode_balance | n |
|---|---|---|---|---|
| MSE-MLP (K=4) | 0.22 ± 0.16 | 0.78 ± 0.16 | 0.43 ± 0.39 | 5 |
| MSE-MLP (K=8) | 0.03 ± 0.02 | 0.97 ± 0.02 | 0.00 ± 0.00 | 5 |
| GMM head (K=8) | _1.00 ± 0.00_ | _0.00 ± 0.00_ | **0.94 ± 0.04** | 5 |
| DDPM head (K=8) | 0.88 ± 0.01 | 0.02 ± 0.01 | 0.80 ± 0.10 | 5 |
| GMM head (K=4) | **1.00 ± 0.00** | **0.00 ± 0.00** | _0.94 ± 0.06_ | 5 |
| DDPM head (K=4) | 0.99 ± 0.01 | 0.00 ± 0.00 | 0.88 ± 0.10 | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: success ↑, collision ↓, mode_balance ↑.
