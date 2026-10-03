| Method | val_loss | n |
|---|---|---|
| Warmup+Cosine (warmup=50) | _1.69 ± 0.01_ | 3 |
| Warmup+Cosine (warmup=0) | 2.25 ± 0.04 | 3 |
| Constant (warmup=100) | 1.81 ± 0.00 | 3 |
| Constant (warmup=300) | 1.80 ± 0.00 | 3 |
| Warmup+Cosine (warmup=300) | **1.67 ± 0.00** | 3 |

Mean ± std over seeds; bold = best, underline = second. Directions: val_loss ↓.
