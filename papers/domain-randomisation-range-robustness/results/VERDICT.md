# Verdict: tier 1 (marginal) — target tier 2 (solid)

Method: Success-gated curriculum DR | primary metric: ret_robust | primary task: cartpole

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| cartpole | 470.8 | Uniform DR wide (w=1.0) | 470.4 | +0.1% | 0.959 | 0.04 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| Curriculum, no gate | missing |  | NO |
| Curriculum, gate 0.5 | missing |  | NO |
| Curriculum, gate 0.95 | missing |  | NO |
| Uniform DR | missing |  | NO |

## Why this tier
- not significant on: cartpole

## To reach the next tier
- p < 0.05 on every task (more seeds or a larger effect)

TARGET NOT REACHED
