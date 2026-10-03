| Method | Task | spearman_hd3 | spearman_hd4 | n |
|---|---|---|---|---|
| One-hot ridge (reimplemented) | rand_48 | 0.257 ± 0.181 | 0.145 ± 0.064 | 5 |
| GP Hamming kernel (reimplemented) | rand_48 | **0.284 ± 0.131** | **0.161 ± 0.089** | 5 |
| CNN (reimplemented) | rand_48 | 0.169 ± 0.174 | _0.152 ± 0.086_ | 5 |
| One-hot + pairwise ridge | rand_48 | _0.265 ± 0.152_ | 0.151 ± 0.075 | 5 |
| One-hot ridge (reimplemented) | rand_96 | 0.294 ± 0.060 | 0.209 ± 0.041 | 5 |
| GP Hamming kernel (reimplemented) | rand_96 | _0.316 ± 0.040_ | _0.209 ± 0.042_ | 5 |
| CNN (reimplemented) | rand_96 | **0.340 ± 0.039** | **0.268 ± 0.047** | 5 |
| One-hot + pairwise ridge | rand_96 | 0.296 ± 0.067 | 0.205 ± 0.037 | 5 |
| One-hot ridge (reimplemented) | rand_384 | 0.535 ± 0.026 | 0.322 ± 0.039 | 5 |
| GP Hamming kernel (reimplemented) | rand_384 | 0.538 ± 0.035 | 0.331 ± 0.044 | 5 |
| CNN (reimplemented) | rand_384 | **0.570 ± 0.036** | **0.395 ± 0.032** | 5 |
| One-hot + pairwise ridge | rand_384 | _0.549 ± 0.034_ | _0.338 ± 0.056_ | 5 |
| One-hot ridge (reimplemented) | rand_2000 | 0.633 ± 0.008 | _0.421 ± 0.021_ | 5 |
| GP Hamming kernel (reimplemented) | rand_2000 | 0.616 ± 0.016 | 0.391 ± 0.010 | 5 |
| CNN (reimplemented) | rand_2000 | **0.649 ± 0.015** | **0.455 ± 0.018** | 5 |
| One-hot + pairwise ridge | rand_2000 | _0.643 ± 0.010_ | 0.419 ± 0.013 | 5 |
| One-hot ridge (reimplemented) | dbl_48 | **0.438 ± 0.030** | _0.149 ± 0.076_ | 5 |
| GP Hamming kernel (reimplemented) | dbl_48 | _0.413 ± 0.046_ | **0.151 ± 0.064** | 5 |
| CNN (reimplemented) | dbl_48 | 0.320 ± 0.083 | 0.147 ± 0.086 | 5 |
| One-hot + pairwise ridge | dbl_48 | 0.376 ± 0.068 | 0.142 ± 0.057 | 5 |
| One-hot ridge (reimplemented) | dbl_96 | _0.469 ± 0.030_ | 0.209 ± 0.041 | 5 |
| GP Hamming kernel (reimplemented) | dbl_96 | 0.459 ± 0.032 | 0.213 ± 0.052 | 5 |
| CNN (reimplemented) | dbl_96 | **0.480 ± 0.033** | **0.250 ± 0.048** | 5 |
| One-hot + pairwise ridge | dbl_96 | 0.455 ± 0.048 | _0.217 ± 0.045_ | 5 |
| One-hot ridge (reimplemented) | dbl_384 | _0.525 ± 0.023_ | _0.262 ± 0.050_ | 5 |
| GP Hamming kernel (reimplemented) | dbl_384 | 0.501 ± 0.027 | 0.261 ± 0.042 | 5 |
| CNN (reimplemented) | dbl_384 | **0.539 ± 0.043** | **0.290 ± 0.058** | 5 |
| One-hot + pairwise ridge | dbl_384 | 0.324 ± 0.053 | 0.231 ± 0.057 | 5 |
| One-hot ridge (reimplemented) | dbl_2000 | _0.549 ± 0.002_ | 0.299 ± 0.005 | 5 |
| GP Hamming kernel (reimplemented) | dbl_2000 | 0.446 ± 0.007 | _0.310 ± 0.014_ | 5 |
| CNN (reimplemented) | dbl_2000 | **0.591 ± 0.033** | **0.347 ± 0.030** | 5 |
| One-hot + pairwise ridge | dbl_2000 | 0.245 ± 0.005 | 0.189 ± 0.013 | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: spearman_hd3 ↑, spearman_hd4 ↑.
