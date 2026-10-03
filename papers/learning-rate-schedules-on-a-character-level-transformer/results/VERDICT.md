# Verdict: tier 1 (marginal) — target tier 2 (solid)

Method: Warmup+Cosine | primary metric: val_loss | primary task: lr3e-3

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| lr1e-2 | 1.682 | Schedule-free AdamW | 1.629 | -3.2% | 0.00267 | -9.15 | 3 |
| lr1e-3 | 1.766 | Constant | 1.765 | -0.1% | 0.747 | -0.09 | 3 |
| lr3e-3 | 1.673 | Schedule-free AdamW | 1.695 | +1.3% | 0.00448 | 2.41 | 3 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| warmup length | missing |  | NO |
| peak-LR sweep (3e-4..3e-2) | missing |  | NO |

## Why this tier
- loses on: lr1e-2, lr1e-3
- not significant on: lr1e-3

## To reach the next tier
- win on every task (or drop/justify the task in PROTOCOL.md)
- p < 0.05 on every task (more seeds or a larger effect)

TARGET NOT REACHED
