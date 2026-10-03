| Method | Task | bias_first | bias_final | qbias_final | subopt_all | n |
|---|---|---|---|---|---|---|
| Q-learning | random20 | 0.003 ± 0.003 | -0.053 ± 0.005 | -0.098 ± 0.001 | 0.164 ± 0.002 | 5 |
| Double Q-learning | random20 | _0.001 ± 0.002_ | _-0.100 ± 0.006_ | _-0.107 ± 0.002_ | _0.144 ± 0.002_ | 5 |
| Maxmin Q-learning | random20 | **-0.120 ± 0.002** | **-0.507 ± 0.002** | **-0.464 ± 0.001** | 0.164 ± 0.002 | 5 |
| Weighted Double Q-learning | random20 | 0.002 ± 0.001 | -0.069 ± 0.006 | -0.078 ± 0.002 | **0.141 ± 0.001** | 5 |
| Q-learning | maxbias | **0.000 ± 0.000** | 0.011 ± 0.001 | 0.075 ± 0.001 | 0.101 ± 0.002 | 5 |
| Double Q-learning | maxbias | _0.000 ± 0.000_ | 0.000 ± 0.000 | _0.007 ± 0.001_ | 0.052 ± 0.000 | 5 |
| Maxmin Q-learning | maxbias | 0.000 ± 0.000 | **0.000 ± 0.000** | **0.004 ± 0.000** | **0.050 ± 0.000** | 5 |
| Weighted Double Q-learning | maxbias | 0.000 ± 0.000 | _0.000 ± 0.000_ | 0.009 ± 0.001 | _0.052 ± 0.000_ | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: bias_first ↓, bias_final ↓, qbias_final ↓, subopt_all ↓.
