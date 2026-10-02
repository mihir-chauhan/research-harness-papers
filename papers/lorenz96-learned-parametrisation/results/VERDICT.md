# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: AR(1) stochastic | primary metric: valid_time | primary task: F20_c10

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| F20_c10 | 1.252 | MLP (32x2) | 1.421 | -11.9% | 0.00019 | -5.18 | 5 |
| F20_c4 | 0.9425 | MLP (32x2) | 1.099 | -14.2% | 0.00011 | -5.04 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| polynomial degree | missing |  | NO |
| AR(1) amplitude and phi | missing |  | NO |
| MLP stencil | missing |  | NO |
| forcing shift | missing |  | NO |

## Why this tier
- not best on F20_c10: ours 1.252 vs MLP (32x2) 1.421

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
