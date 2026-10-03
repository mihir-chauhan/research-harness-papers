| Method | Task | solved | mean_exp | n |
|---|---|---|---|---|
| BFS | val_3_10 | 0.91 ± 0.03 | 21.03 ± 3.42 | 5 |
| Hand heuristic | val_3_10 | **1.00 ± 0.00** | **4.42 ± 0.28** | 5 |
| Feature-MLP policy | val_3_10 | _1.00 ± 0.00_ | _5.26 ± 0.76_ | 5 |
| Transformer policy | val_3_10 | 1.00 ± 0.00 | 5.99 ± 0.83 | 5 |
| BFS | test_11_20 | 0.47 ± 0.03 | 63.33 ± 2.73 | 5 |
| Hand heuristic | test_11_20 | **1.00 ± 0.00** | **11.31 ± 0.45** | 5 |
| Feature-MLP policy | test_11_20 | _0.89 ± 0.02_ | _27.16 ± 1.86_ | 5 |
| Transformer policy | test_11_20 | 0.82 ± 0.02 | 34.99 ± 1.37 | 5 |
| BFS | test_21_40 | 0.27 ± 0.06 | 80.82 ± 5.00 | 5 |
| Hand heuristic | test_21_40 | **0.96 ± 0.01** | **27.57 ± 2.35** | 5 |
| Feature-MLP policy | test_21_40 | _0.58 ± 0.03_ | _55.59 ± 3.83_ | 5 |
| Transformer policy | test_21_40 | 0.52 ± 0.05 | 59.82 ± 5.14 | 5 |
| BFS | test_41_70 | 0.20 ± 0.04 | 85.69 ± 1.69 | 5 |
| Hand heuristic | test_41_70 | **0.73 ± 0.03** | **47.34 ± 2.38** | 5 |
| Feature-MLP policy | test_41_70 | _0.46 ± 0.03_ | _65.25 ± 3.20_ | 5 |
| Transformer policy | test_41_70 | 0.41 ± 0.05 | 68.81 ± 4.19 | 5 |
| BFS | tune_21_35 | 0.30 ± 0.04 | 78.79 ± 3.25 | 5 |
| Feature-MLP policy | tune_21_35 | **0.63 ± 0.06** | **51.56 ± 4.28** | 5 |
| Transformer policy | tune_21_35 | _0.55 ± 0.05_ | _57.31 ± 3.81_ | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: solved ↑, mean_exp ↓.
