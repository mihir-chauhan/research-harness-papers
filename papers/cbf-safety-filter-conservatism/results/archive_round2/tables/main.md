| Method | Task | violation_rate | success_rate | time_to_goal | min_clearance | worst_penetration | n |
|---|---|---|---|---|---|---|---|
| Nominal (unfiltered) | double_integrator | 1.000 ± 0.000 | **1.000 ± 0.000** | **5.170 ± 0.002** | -0.517 ± 0.016 | 0.759 ± 0.012 | 5 |
| Distance-threshold braking (heuristic) | double_integrator | 0.110 ± 0.010 | 1.000 ± 0.000 | _7.480 ± 0.056_ | **0.205 ± 0.016** | 0.184 ± 0.062 | 5 |
| Continuous-time CBF at discrete steps (reimplemented) | double_integrator | **0.000 ± 0.000** | _1.000 ± 0.000_ | 7.800 ± 0.094 | _0.205 ± 0.017_ | **0.000 ± 0.000** | 5 |
| Discrete-time CBF (reimplemented) | double_integrator | _0.008 ± 0.008_ | 1.000 ± 0.000 | 7.542 ± 0.126 | 0.129 ± 0.013 | _0.000 ± 0.000_ | 5 |
| Nominal (unfiltered) | unicycle | 1.000 ± 0.000 | **1.000 ± 0.000** | **9.938 ± 0.026** | -0.519 ± 0.015 | 0.775 ± 0.013 | 5 |
| Distance-threshold braking (heuristic) | unicycle | 0.000 ± 0.000 | 1.000 ± 0.000 | 12.567 ± 0.120 | **0.349 ± 0.006** | 0.000 ± 0.000 | 5 |
| Continuous-time CBF at discrete steps (reimplemented) | unicycle | **0.000 ± 0.000** | _1.000 ± 0.000_ | 11.859 ± 0.127 | _0.153 ± 0.001_ | **0.000 ± 0.000** | 5 |
| Discrete-time CBF (reimplemented) | unicycle | _0.000 ± 0.000_ | 1.000 ± 0.000 | _11.781 ± 0.118_ | 0.145 ± 0.001 | _0.000 ± 0.000_ | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: violation_rate ↓, success_rate ↑, time_to_goal ↓, min_clearance ↑, worst_penetration ↓.
