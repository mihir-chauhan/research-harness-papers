# Verdict: tier 1 (marginal) — target tier 2 (solid)

Method: Small-loss (1 net) | primary metric: test_acc | primary task: digits_noise40

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| digits_noise0 | 0.9914 | Label smoothing | 0.9953 | -0.4% | 0.0249 | -1.77 | 5 |
| digits_noise20 | 0.9433 | Mixup | 0.9207 | +2.4% | 0.00767 | 1.49 | 5 |
| digits_noise40 | 0.896 | Mixup | 0.7616 | +17.6% | 5.21e-05 | 5.45 | 5 |
| digits_noise60 | 0.7711 | Mixup | 0.5227 | +47.5% | 1.12e-05 | 7.43 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| Small-loss, no warm-up/ramp | missing |  | NO |

## Why this tier
- loses on: digits_noise0

## To reach the next tier
- win on every task (or drop/justify the task in PROTOCOL.md)

TARGET NOT REACHED
