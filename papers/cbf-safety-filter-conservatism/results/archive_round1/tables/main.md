| Method | Task | violation_rate | success_rate | time_to_goal | min_clearance | worst_penetration | n |
|---|---|---|---|---|---|---|---|
| Nominal (unfiltered) | double_integrator | 1.000 ± 0.000 | **1.000 ± 0.000** | **5.194 ± 0.003** | -0.517 ± 0.016 | 0.759 ± 0.011 | 5 |
| Distance-threshold braking (heuristic) | double_integrator | 0.216 ± 0.049 | 1.000 ± 0.000 | 7.458 ± 0.064 | 0.131 ± 0.015 | 0.401 ± 0.069 | 5 |
| Continuous-time CBF at discrete steps (reimplemented) | double_integrator | **0.000 ± 0.000** | _1.000 ± 0.000_ | 7.800 ± 0.094 | **0.205 ± 0.017** | **0.000 ± 0.000** | 5 |
| Discrete-time CBF (reimplemented) | double_integrator | _0.056 ± 0.021_ | 1.000 ± 0.000 | _7.408 ± 0.077_ | _0.196 ± 0.017_ | _0.011 ± 0.003_ | 5 |
| Nominal (unfiltered) | unicycle | 1.000 ± 0.000 | **1.000 ± 0.000** | **9.915 ± 0.026** | -0.519 ± 0.015 | 0.777 ± 0.013 | 5 |
| Distance-threshold braking (heuristic) | unicycle | _0.000 ± 0.000_ | 1.000 ± 0.000 | 12.603 ± 0.114 | **0.346 ± 0.005** | _0.000 ± 0.000_ | 5 |
| Continuous-time CBF at discrete steps (reimplemented) | unicycle | **0.000 ± 0.000** | _1.000 ± 0.000_ | 11.859 ± 0.127 | _0.153 ± 0.001_ | **0.000 ± 0.000** | 5 |
| Discrete-time CBF (reimplemented) | unicycle | 0.000 ± 0.000 | 1.000 ± 0.000 | _11.781 ± 0.118_ | 0.145 ± 0.001 | 0.000 ± 0.000 | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: violation_rate ↓, success_rate ↑, time_to_goal ↓, min_clearance ↑, worst_penetration ↓.
