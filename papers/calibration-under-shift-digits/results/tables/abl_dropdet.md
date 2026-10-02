| Method | Task | accuracy | ece | nll | brier | n |
|---|---|---|---|---|---|---|
| Dropout-trained MLP, deterministic | rot0 | **0.98 ± 0.00** | **0.02 ± 0.01** | **0.08 ± 0.02** | **0.04 ± 0.01** | 5 |
| Dropout-trained MLP, deterministic | rot10 | **0.84 ± 0.01** | **0.07 ± 0.01** | **0.54 ± 0.06** | **0.24 ± 0.02** | 5 |
| Dropout-trained MLP, deterministic | rot20 | **0.65 ± 0.03** | **0.20 ± 0.04** | **1.59 ± 0.31** | **0.54 ± 0.06** | 5 |
| Dropout-trained MLP, deterministic | rot30 | **0.41 ± 0.06** | **0.43 ± 0.06** | **3.73 ± 0.58** | **0.97 ± 0.12** | 5 |
| Dropout-trained MLP, deterministic | rot45 | **0.14 ± 0.04** | **0.79 ± 0.08** | **10.58 ± 1.37** | **1.61 ± 0.13** | 5 |
| Dropout-trained MLP, deterministic | rot60 | **0.14 ± 0.03** | **0.82 ± 0.06** | **12.70 ± 1.95** | **1.66 ± 0.10** | 5 |
| Dropout-trained MLP, deterministic | noise0.25 | **0.86 ± 0.03** | **0.08 ± 0.02** | **0.56 ± 0.11** | **0.22 ± 0.04** | 5 |
| Dropout-trained MLP, deterministic | noise0.5 | **0.51 ± 0.03** | **0.36 ± 0.03** | **3.06 ± 0.42** | **0.82 ± 0.07** | 5 |
| Dropout-trained MLP, deterministic | noise0.75 | **0.31 ± 0.03** | **0.55 ± 0.03** | **5.87 ± 0.70** | **1.20 ± 0.05** | 5 |
| Dropout-trained MLP, deterministic | noise1.0 | **0.23 ± 0.02** | **0.64 ± 0.03** | **7.79 ± 0.87** | **1.36 ± 0.05** | 5 |
| Dropout-trained MLP, deterministic | rot30_noise0.5 | **0.20 ± 0.04** | **0.65 ± 0.05** | **7.71 ± 1.08** | **1.40 ± 0.09** | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: accuracy ↑, ece ↓, nll ↓, brier ↓.
