| Method | energy_mae | inv_defect | n |
|---|---|---|---|
| SymFn atomwise MLP (BP-style) | 4.62 ± 1.87 | 0.00 ± 0.00 | 9 |
| Sorted dist KRR | 2.15 ± 1.52 | 0.00 ± 0.00 | 9 |
| Raw coords KRR | 11.87 ± 0.65 | 2.63 ± 1.81 | 9 |
| Mean predictor | 12.12 ± 0.55 | 0.00 ± 0.00 | 9 |
| SymFn-sum MLP | 7.16 ± 4.49 | _0.00 ± 0.00_ | 9 |
| Sorted dist MLP | **1.35 ± 0.86** | **0.00 ± 0.00** | 9 |
| Raw coords MLP | 15.05 ± 1.58 | 14.34 ± 2.25 | 9 |
| SymFn-sum KRR | _1.62 ± 0.87_ | 0.00 ± 0.00 | 9 |

Mean ± std over seeds; bold = best, underline = second. Directions: energy_mae ↓, inv_defect ↓.
