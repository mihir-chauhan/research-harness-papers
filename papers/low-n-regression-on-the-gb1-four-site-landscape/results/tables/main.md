| Method | Task | spearman | top100_recall | n |
|---|---|---|---|---|
| One-hot ridge (reimplemented) | rand_48 | 0.182 ± 0.052 | **0.006 ± 0.009** | 5 |
| GP Hamming kernel (reimplemented) | rand_48 | **0.202 ± 0.051** | 0.004 ± 0.009 | 5 |
| CNN (reimplemented) | rand_48 | 0.166 ± 0.072 | 0.004 ± 0.009 | 5 |
| One-hot + pairwise ridge | rand_48 | _0.188 ± 0.043_ | _0.006 ± 0.009_ | 5 |
| One-hot ridge (reimplemented) | rand_96 | 0.231 ± 0.036 | _0.016 ± 0.018_ | 5 |
| GP Hamming kernel (reimplemented) | rand_96 | _0.236 ± 0.030_ | 0.010 ± 0.017 | 5 |
| CNN (reimplemented) | rand_96 | **0.287 ± 0.042** | **0.022 ± 0.016** | 5 |
| One-hot + pairwise ridge | rand_96 | 0.229 ± 0.035 | 0.012 ± 0.016 | 5 |
| One-hot ridge (reimplemented) | rand_384 | 0.381 ± 0.037 | 0.024 ± 0.027 | 5 |
| GP Hamming kernel (reimplemented) | rand_384 | 0.389 ± 0.042 | **0.036 ± 0.025** | 5 |
| CNN (reimplemented) | rand_384 | **0.444 ± 0.023** | 0.030 ± 0.014 | 5 |
| One-hot + pairwise ridge | rand_384 | _0.396 ± 0.052_ | _0.034 ± 0.028_ | 5 |
| One-hot ridge (reimplemented) | rand_2000 | _0.480 ± 0.017_ | 0.084 ± 0.080 | 5 |
| GP Hamming kernel (reimplemented) | rand_2000 | 0.451 ± 0.006 | _0.152 ± 0.062_ | 5 |
| CNN (reimplemented) | rand_2000 | **0.506 ± 0.015** | **0.216 ± 0.109** | 5 |
| One-hot + pairwise ridge | rand_2000 | 0.478 ± 0.009 | 0.152 ± 0.063 | 5 |
| One-hot ridge (reimplemented) | dbl_48 | **0.212 ± 0.063** | **0.018 ± 0.027** | 5 |
| GP Hamming kernel (reimplemented) | dbl_48 | _0.199 ± 0.057_ | 0.014 ± 0.022 | 5 |
| CNN (reimplemented) | dbl_48 | 0.186 ± 0.081 | 0.012 ± 0.027 | 5 |
| One-hot + pairwise ridge | dbl_48 | 0.192 ± 0.048 | _0.016 ± 0.023_ | 5 |
| One-hot ridge (reimplemented) | dbl_96 | 0.262 ± 0.038 | 0.006 ± 0.009 | 5 |
| GP Hamming kernel (reimplemented) | dbl_96 | 0.252 ± 0.046 | **0.012 ± 0.011** | 5 |
| CNN (reimplemented) | dbl_96 | **0.289 ± 0.046** | 0.008 ± 0.008 | 5 |
| One-hot + pairwise ridge | dbl_96 | _0.263 ± 0.045_ | _0.010 ± 0.010_ | 5 |
| One-hot ridge (reimplemented) | dbl_384 | _0.320 ± 0.046_ | _0.020 ± 0.016_ | 5 |
| GP Hamming kernel (reimplemented) | dbl_384 | 0.299 ± 0.040 | 0.014 ± 0.013 | 5 |
| CNN (reimplemented) | dbl_384 | **0.332 ± 0.053** | **0.028 ± 0.013** | 5 |
| One-hot + pairwise ridge | dbl_384 | 0.247 ± 0.054 | 0.014 ± 0.013 | 5 |
| One-hot ridge (reimplemented) | dbl_2000 | _0.354 ± 0.005_ | 0.062 ± 0.011 | 5 |
| GP Hamming kernel (reimplemented) | dbl_2000 | 0.322 ± 0.013 | 0.114 ± 0.009 | 5 |
| CNN (reimplemented) | dbl_2000 | **0.387 ± 0.034** | **0.208 ± 0.023** | 5 |
| One-hot + pairwise ridge | dbl_2000 | 0.196 ± 0.010 | _0.128 ± 0.016_ | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: spearman ↑, top100_recall ↑.
