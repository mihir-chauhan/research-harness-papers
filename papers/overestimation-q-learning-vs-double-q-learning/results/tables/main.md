| Method | Task | bias_first | bias_final | qbias_final | subopt_all | greedy_err_final | n |
|---|---|---|---|---|---|---|---|
| Q-learning | maxbias | 0.038 ± 0.001 | 0.008 ± 0.002 | 0.075 ± 0.002 | 0.380 ± 0.005 | 0.083 ± 0.013 | 5 |
| Weighted Double Q-learning | maxbias | _0.003 ± 0.000_ | 0.001 ± 0.000 | _0.073 ± 0.000_ | _0.127 ± 0.002_ | _0.020 ± 0.004_ | 5 |
| Maxmin Q-learning | maxbias | **0.000 ± 0.000** | **0.001 ± 0.000** | 0.080 ± 0.000 | 0.197 ± 0.002 | 0.024 ± 0.002 | 5 |
| Double Q-learning | maxbias | 0.003 ± 0.000 | _0.001 ± 0.000_ | **0.061 ± 0.001** | **0.119 ± 0.002** | **0.017 ± 0.002** | 5 |
| Q-learning | random20 | -2.960 ± 0.022 | -0.150 ± 0.011 | -0.444 ± 0.005 | **0.255 ± 0.002** | **0.173 ± 0.016** | 5 |
| Weighted Double Q-learning | random20 | _-3.283 ± 0.016_ | -0.360 ± 0.003 | -0.839 ± 0.005 | 0.313 ± 0.003 | 0.257 ± 0.010 | 5 |
| Maxmin Q-learning | random20 | **-3.428 ± 0.021** | **-0.721 ± 0.018** | **-1.175 ± 0.009** | _0.282 ± 0.002_ | _0.228 ± 0.026_ | 5 |
| Double Q-learning | random20 | -3.281 ± 0.017 | _-0.364 ± 0.007_ | _-0.840 ± 0.005_ | 0.312 ± 0.001 | 0.254 ± 0.011 | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: bias_first ↓, bias_final ↓, qbias_final ↓, subopt_all ↓, greedy_err_final ↓.
