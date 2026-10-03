| Method | auroc | auprc | brier | n |
|---|---|---|---|---|
| LR (summary) | _0.8429 ± 0.0034_ | _0.4936 ± 0.0054_ | _0.0926 ± 0.0006_ | 5 |
| GBDT (summary) | **0.8576 ± 0.0048** | **0.5072 ± 0.0112** | **0.0925 ± 0.0013** | 5 |
| GRU (forward-fill) | 0.8323 ± 0.0037 | 0.4837 ± 0.0096 | 0.0944 ± 0.0010 | 5 |
| GRU (mask+delta) | 0.8329 ± 0.0023 | 0.4884 ± 0.0064 | 0.0941 ± 0.0004 | 5 |
| GRU-D | 0.8301 ± 0.0021 | 0.4896 ± 0.0075 | 0.0942 ± 0.0009 | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: auroc ↑, auprc ↑, brier ↓.
