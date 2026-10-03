| Method | Task | sens3 | sens5 | best3 | n |
|---|---|---|---|---|---|
| Step decay | sens | 0.53 ± 0.05 | 0.68 ± 0.02 | 1.82 ± 0.02 | 3 |
| Schedule-free AdamW | sens | _0.25 ± 0.01_ | _0.54 ± 0.01_ | **1.63 ± 0.00** | 3 |
| Constant | sens | 0.65 ± 0.05 | 1.03 ± 0.03 | 1.76 ± 0.01 | 3 |
| Warmup+Cosine | sens | **0.09 ± 0.01** | **0.40 ± 0.02** | _1.67 ± 0.01_ | 3 |

Mean ± std over seeds; bold = best, underline = second. Directions: sens3 ↓, sens5 ↓, best3 ↓.
