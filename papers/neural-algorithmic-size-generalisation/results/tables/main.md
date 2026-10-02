| Method | mae_sparse_n8 | mae_sparse_n16 | mae_sparse_n32 | mae_sparse_n64 | n |
|---|---|---|---|---|---|
| MPNN-sum + steps | 0.04 ± 0.01 | 0.12 ± 0.04 | 0.43 ± 0.24 | 54707.72 ± 122329.15 | 5 |
| MPNN-max | **0.01 ± 0.00** | **0.03 ± 0.01** | 0.25 ± 0.46 | _0.91 ± 1.22_ | 5 |
| MPNN-sum | _0.02 ± 0.00_ | _0.03 ± 0.01_ | **0.08 ± 0.06** | **0.23 ± 0.19** | 5 |
| MLP (flat adjacency) | 0.24 ± 0.00 | 0.67 ± 0.01 | 1.02 ± 0.02 | 1.33 ± 0.02 | 5 |
| MPNN-max + steps | 0.03 ± 0.01 | 0.08 ± 0.04 | _0.24 ± 0.18_ | 1.96 ± 2.05 | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: mae_sparse_n8 ↓, mae_sparse_n16 ↓, mae_sparse_n32 ↓, mae_sparse_n64 ↓.
