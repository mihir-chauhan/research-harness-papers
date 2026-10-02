| Method | Task | sw_k1 | sw_k4 | sw_k16 | sw_k100 | straight | n |
|---|---|---|---|---|---|---|---|
| Reflow-1 (teacher 4 steps) | eight_gaussians | _0.099 ± 0.004_ | _0.083 ± 0.004_ | _0.087 ± 0.007_ | _0.081 ± 0.002_ | _0.996 ± 0.001_ | 3 |
| Reflow-2 (Euler) | eight_gaussians | **0.033 ± 0.007** | **0.030 ± 0.002** | **0.037 ± 0.009** | **0.029 ± 0.006** | **1.000 ± 0.000** | 3 |
| Reflow-1 (teacher 4 steps) | two_moons | _0.269 ± 0.001_ | _0.256 ± 0.005_ | _0.262 ± 0.005_ | _0.258 ± 0.008_ | _0.995 ± 0.001_ | 3 |
| Reflow-2 (Euler) | two_moons | **0.025 ± 0.003** | **0.024 ± 0.004** | **0.030 ± 0.008** | **0.026 ± 0.008** | **1.000 ± 0.000** | 3 |
| Reflow-1 (teacher 4 steps) | checkerboard | _0.221 ± 0.006_ | _0.217 ± 0.006_ | _0.220 ± 0.007_ | _0.216 ± 0.006_ | _0.997 ± 0.001_ | 3 |
| Reflow-2 (Euler) | checkerboard | **0.031 ± 0.002** | **0.032 ± 0.001** | **0.034 ± 0.007** | **0.030 ± 0.001** | **1.000 ± 0.000** | 3 |

Mean ± std over seeds; bold = best, underline = second. Directions: sw_k1 ↓, sw_k4 ↓, sw_k16 ↓, sw_k100 ↓, straight ↑.
