| Method | Task | val_loss | train_loss | val_loss_y | n |
|---|---|---|---|---|---|
| Step decay | lr3e-3 | 1.85 ± 0.05 | 1.70 ± 0.05 | — | 3 |
| Schedule-free AdamW | lr3e-3 | _1.69 ± 0.01_ | _1.53 ± 0.00_ | **1.72 ± 0.01** | 3 |
| Constant | lr3e-3 | 1.82 ± 0.03 | 1.66 ± 0.03 | — | 3 |
| Warmup+Cosine | lr3e-3 | **1.67 ± 0.01** | **1.49 ± 0.00** | — | 3 |
| Step decay | lr1e-3 | 1.83 ± 0.00 | 1.68 ± 0.01 | — | 3 |
| Schedule-free AdamW | lr1e-3 | 1.88 ± 0.01 | 1.75 ± 0.01 | **1.88 ± 0.01** | 3 |
| Constant | lr1e-3 | **1.76 ± 0.01** | **1.60 ± 0.00** | — | 3 |
| Warmup+Cosine | lr1e-3 | _1.77 ± 0.01_ | _1.61 ± 0.01_ | — | 3 |
| Step decay | lr1e-2 | 2.35 ± 0.06 | 2.32 ± 0.05 | — | 3 |
| Schedule-free AdamW | lr1e-2 | **1.63 ± 0.00** | **1.49 ± 0.00** | **1.67 ± 0.01** | 3 |
| Constant | lr1e-2 | 2.42 ± 0.05 | 2.40 ± 0.04 | — | 3 |
| Warmup+Cosine | lr1e-2 | _1.68 ± 0.01_ | _1.50 ± 0.00_ | — | 3 |
| Step decay | lr3e-4 | 2.13 ± 0.01 | 2.09 ± 0.01 | — | 3 |
| Schedule-free AdamW | lr3e-4 | 2.17 ± 0.01 | 2.13 ± 0.01 | **2.17 ± 0.01** | 3 |
| Constant | lr3e-4 | **1.94 ± 0.02** | **1.83 ± 0.01** | — | 3 |
| Warmup+Cosine | lr3e-4 | _2.07 ± 0.01_ | _2.02 ± 0.01_ | — | 3 |
| Step decay | lr3e-2 | 2.50 ± 0.00 | 2.48 ± 0.00 | — | 3 |
| Schedule-free AdamW | lr3e-2 | **1.65 ± 0.02** | _1.55 ± 0.00_ | **1.71 ± 0.01** | 3 |
| Constant | lr3e-2 | 2.80 ± 0.05 | 2.76 ± 0.03 | — | 3 |
| Warmup+Cosine | lr3e-2 | _1.71 ± 0.01_ | **1.54 ± 0.00** | — | 3 |

Mean ± std over seeds; bold = best, underline = second. Directions: val_loss ↓, train_loss ↓, val_loss_y ↓.
