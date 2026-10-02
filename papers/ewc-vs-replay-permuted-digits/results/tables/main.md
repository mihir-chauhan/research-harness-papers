| Method | Task | average_accuracy | forgetting | backward_transfer | last_task_accuracy | n |
|---|---|---|---|---|---|---|
| Fine-tuning | perm_dil | 0.498 ± 0.021 | 0.584 ± 0.023 | -0.584 ± 0.023 | 0.973 ± 0.009 | 5 |
| EWC | perm_dil | 0.695 ± 0.019 | 0.303 ± 0.024 | -0.303 ± 0.024 | 0.917 ± 0.017 | 5 |
| Experience replay (M=20) | perm_dil | 0.670 ± 0.042 | 0.370 ± 0.052 | -0.370 ± 0.052 | _0.975 ± 0.009_ | 5 |
| Experience replay (M=100) | perm_dil | _0.847 ± 0.008_ | _0.148 ± 0.009_ | _-0.148 ± 0.009_ | **0.976 ± 0.011** | 5 |
| Joint training | perm_dil | **0.954 ± 0.010** | **0.010 ± 0.006** | **-0.004 ± 0.005** | 0.967 ± 0.009 | 5 |
| Fine-tuning | split_cil | 0.214 ± 0.031 | 0.973 ± 0.039 | -0.973 ± 0.039 | **0.997 ± 0.006** | 5 |
| EWC | split_cil | 0.246 ± 0.050 | 0.568 ± 0.136 | -0.568 ± 0.136 | 0.118 ± 0.263 | 5 |
| Experience replay (M=20) | split_cil | 0.728 ± 0.051 | 0.327 ± 0.062 | -0.327 ± 0.062 | _0.992 ± 0.012_ | 5 |
| Experience replay (M=100) | split_cil | _0.896 ± 0.021_ | _0.112 ± 0.032_ | _-0.112 ± 0.032_ | 0.986 ± 0.010 | 5 |
| Joint training | split_cil | **0.957 ± 0.015** | **0.028 ± 0.018** | **-0.026 ± 0.020** | 0.964 ± 0.018 | 5 |
| Fine-tuning | split_til | 0.946 ± 0.025 | 0.059 ± 0.028 | -0.058 ± 0.029 | **0.997 ± 0.006** | 5 |
| EWC | split_til | 0.973 ± 0.015 | _0.006 ± 0.005_ | _-0.005 ± 0.004_ | 0.945 ± 0.071 | 5 |
| Experience replay (M=20) | split_til | 0.973 ± 0.011 | 0.026 ± 0.014 | -0.025 ± 0.014 | 0.997 ± 0.006 | 5 |
| Experience replay (M=100) | split_til | _0.984 ± 0.006_ | 0.012 ± 0.009 | -0.010 ± 0.010 | 0.997 ± 0.006 | 5 |
| Joint training | split_til | **0.990 ± 0.009** | **0.005 ± 0.005** | **-0.003 ± 0.005** | _0.997 ± 0.006_ | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: average_accuracy ↑, forgetting ↓, backward_transfer ↑, last_task_accuracy ↑.
