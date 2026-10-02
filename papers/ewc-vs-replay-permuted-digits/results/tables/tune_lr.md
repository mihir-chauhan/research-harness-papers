| Method | Task | val_average_accuracy | n |
|---|---|---|---|
| Fine-tuning lr0.01 | perm_dil | 0.49 ± 0.04 | 2 |
| Fine-tuning lr0.1 | perm_dil | 0.55 ± 0.01 | 2 |
| Joint training lr0.05 | perm_dil | _0.94 ± 0.02_ | 2 |
| Joint training lr0.1 | perm_dil | **0.96 ± 0.01** | 2 |
| Fine-tuning lr0.05 | perm_dil | 0.53 ± 0.01 | 2 |
| Joint training lr0.01 | perm_dil | 0.80 ± 0.01 | 2 |
| Fine-tuning lr0.01 | split_cil | 0.20 ± 0.00 | 2 |
| Fine-tuning lr0.1 | split_cil | 0.20 ± 0.00 | 2 |
| Joint training lr0.05 | split_cil | _0.94 ± 0.01_ | 2 |
| Joint training lr0.1 | split_cil | **0.95 ± 0.01** | 2 |
| Fine-tuning lr0.05 | split_cil | 0.20 ± 0.00 | 2 |
| Joint training lr0.01 | split_cil | 0.77 ± 0.02 | 2 |
| Fine-tuning lr0.01 | split_til | 0.93 ± 0.01 | 2 |
| Fine-tuning lr0.1 | split_til | 0.91 ± 0.06 | 2 |
| Joint training lr0.05 | split_til | _0.99 ± 0.00_ | 2 |
| Joint training lr0.1 | split_til | **0.99 ± 0.00** | 2 |
| Fine-tuning lr0.05 | split_til | 0.92 ± 0.04 | 2 |
| Joint training lr0.01 | split_til | 0.96 ± 0.01 | 2 |

Mean ± std over seeds; bold = best, underline = second. Directions: val_average_accuracy ↑.
