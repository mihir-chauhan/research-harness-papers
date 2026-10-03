| Method | Task | val_loss | n |
|---|---|---|---|
| Step decay (warmup=100) | lr3e-3 | **1.71 ± 0.00** | 3 |
| Constant (warmup=100) | lr3e-3 | _1.74 ± 0.01_ | 3 |
| Step decay (warmup=100) | lr1e-3 | _1.83 ± 0.01_ | 3 |
| Constant (warmup=100) | lr1e-3 | **1.76 ± 0.02** | 3 |
| Step decay (warmup=100) | lr1e-2 | **1.71 ± 0.01** | 3 |

Mean ± std over seeds; bold = best, underline = second. Directions: val_loss ↓.
