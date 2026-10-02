# Verdict: tier 1 (marginal) — target tier 2 (solid)

Method: ESN | primary metric: vpt | primary task: lorenz63

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| lorenz63 | 9.546 | MLP delay | 5.578 | +71.1% | 3.19e-05 | 15.49 | 5 |
| lorenz96 | 2.115 | MLP delay | 2.882 | -26.6% | 0.0178 | -2.51 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| ESN without squared features | -1.284 | 2.52e-05 | yes |

## Why this tier
- loses on: lorenz96

## To reach the next tier
- win on every task (or drop/justify the task in PROTOCOL.md)

TARGET NOT REACHED
