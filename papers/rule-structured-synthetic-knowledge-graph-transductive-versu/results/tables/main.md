| Method | Task | mrr | hits1 | hits10 | n |
|---|---|---|---|---|---|
| Rule oracle (hand-written) | transductive | _0.937 ± 0.026_ | _0.931 ± 0.026_ | 0.940 ± 0.026 | 5 |
| TransE+fold-in (reimplemented) | transductive | 0.656 ± 0.029 | 0.423 ± 0.056 | 0.981 ± 0.005 | 5 |
| TransE (reimplemented) | transductive | 0.658 ± 0.024 | 0.424 ± 0.049 | _0.983 ± 0.005_ | 5 |
| Path-MP (2-hop) | transductive | **0.988 ± 0.004** | **0.985 ± 0.003** | **0.990 ± 0.005** | 5 |
| Rule oracle (hand-written) | inductive | _0.950 ± 0.020_ | _0.946 ± 0.019_ | 0.952 ± 0.020 | 5 |
| TransE+fold-in (reimplemented) | inductive | 0.644 ± 0.025 | 0.423 ± 0.046 | _0.982 ± 0.010_ | 5 |
| TransE (reimplemented) | inductive | 0.011 ± 0.002 | 0.000 ± 0.000 | 0.015 ± 0.006 | 5 |
| Path-MP (2-hop) | inductive | **0.989 ± 0.007** | **0.987 ± 0.008** | **0.992 ± 0.007** | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: mrr ↑, hits1 ↑, hits10 ↑.
