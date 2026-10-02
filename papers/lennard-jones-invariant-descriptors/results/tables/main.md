| Method | energy_mae | mae_rot_perm | inv_defect | n |
|---|---|---|---|---|
| Raw coords MLP | 15.03 ± 0.43 | 14.92 ± 0.64 | 15.23 ± 0.44 | 5 |
| Raw coords KRR | 12.18 ± 0.33 | 12.14 ± 0.40 | 2.88 ± 2.42 | 5 |
| Mean predictor | 12.20 ± 0.30 | 12.20 ± 0.30 | 0.00 ± 0.00 | 5 |
| Sorted dist KRR | 1.09 ± 0.06 | 1.09 ± 0.06 | 0.00 ± 0.00 | 5 |
| SymFn atomwise MLP (BP-style) | 3.13 ± 0.21 | 3.13 ± 0.21 | 0.00 ± 0.00 | 5 |
| Sorted dist MLP | **0.63 ± 0.02** | **0.63 ± 0.02** | **0.00 ± 0.00** | 5 |
| SymFn-sum MLP | 4.51 ± 0.14 | 4.51 ± 0.14 | _0.00 ± 0.00_ | 5 |
| SymFn-sum KRR | _0.89 ± 0.14_ | _0.89 ± 0.14_ | 0.00 ± 0.00 | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: energy_mae ↓, mae_rot_perm ↓, inv_defect ↓.
