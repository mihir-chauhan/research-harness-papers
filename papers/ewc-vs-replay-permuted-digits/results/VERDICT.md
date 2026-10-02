# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: Experience replay (M=100) | primary metric: average_accuracy | primary task: perm_dil

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| perm_dil | 0.8467 | Joint training | 0.9537 | -11.2% | 1.56e-05 | -11.88 | 5 |
| split_cil | 0.8961 | Joint training | 0.9567 | -6.3% | 0.00303 | -3.31 | 5 |
| split_til | 0.9839 | Joint training | 0.99 | -0.6% | 0.258 | -0.81 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| Experience replay | missing |  | NO |
| EWC | missing |  | NO |

## Why this tier
- not best on perm_dil: ours 0.8467 vs Joint training 0.9537

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
