| Method | success | collision | mode_balance | n |
|---|---|---|---|---|
| DDPM head (steps=1) | 0.11 ± 0.09 | 0.89 ± 0.09 | 0.04 ± 0.06 | 5 |
| DDPM head (steps=20) | **1.00 ± 0.00** | **0.00 ± 0.00** | **0.92 ± 0.06** | 5 |
| DDPM head (steps=10) | _0.99 ± 0.01_ | _0.01 ± 0.01_ | 0.90 ± 0.08 | 5 |
| DDPM head (steps=5) | 0.99 ± 0.01 | 0.01 ± 0.01 | _0.91 ± 0.06_ | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: success ↑, collision ↓, mode_balance ↑.
