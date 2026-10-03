# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: One-hot + pairwise ridge | primary metric: spearman | primary task: rand_384

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| dbl_2000 | 0.1956 | CNN (reimplemented) | 0.3874 | -49.5% | 0.000207 | -7.75 | 5 |
| dbl_384 | 0.2468 | CNN (reimplemented) | 0.332 | -25.7% | 0.0669 | -1.58 | 5 |
| dbl_48 | 0.1923 | One-hot ridge (reimplemented) | 0.2116 | -9.1% | 0.172 | -0.34 | 5 |
| dbl_96 | 0.263 | CNN (reimplemented) | 0.2889 | -8.9% | 0.28 | -0.57 | 5 |
| rand_2000 | 0.4784 | CNN (reimplemented) | 0.5055 | -5.4% | 0.0334 | -2.25 | 5 |
| rand_384 | 0.3955 | CNN (reimplemented) | 0.4443 | -11.0% | 0.0599 | -1.22 | 5 |
| rand_48 | 0.1885 | GP Hamming kernel (reimplemented) | 0.2025 | -6.9% | 0.365 | -0.30 | 5 |
| rand_96 | 0.2289 | CNN (reimplemented) | 0.287 | -20.3% | 0.0701 | -1.49 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| GP hyperparameters fixed vs marginal likelihood | missing |  | NO |
| ridge alpha sweep | missing |  | NO |
| CNN ensemble/log target | missing |  | NO |

## Why this tier
- not best on rand_384: ours 0.3955 vs CNN (reimplemented) 0.4443

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
