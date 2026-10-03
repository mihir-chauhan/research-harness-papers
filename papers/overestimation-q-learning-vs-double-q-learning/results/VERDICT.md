# Verdict: tier 1 (marginal) — target tier 2 (solid)

Method: Double Q-learning | primary metric: qbias_final | primary task: maxbias

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| maxbias | 0.06056 | Weighted Double Q-learning | 0.07255 | +16.5% | 4.86e-07 | 28.32 | 5 |
| random20 | -0.8404 | Maxmin Q-learning | -1.175 | -28.5% | 4.93e-08 | -44.37 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| double_both (both tables updated each step) | missing |  | NO |
| alpha sweep (Q-learning at half step size) | missing |  | NO |
| warm start at true Q | missing |  | NO |
| epsilon sweep | missing |  | NO |
| sigma sweep | missing |  | NO |
| number-of-actions sweep | missing |  | NO |

## Why this tier
- loses on: random20

## To reach the next tier
- win on every task (or drop/justify the task in PROTOCOL.md)

TARGET NOT REACHED
