# Verdict: tier 1 (marginal) — target tier 2 (solid)

Method: LoRA r=4 | primary metric: adapt_acc | primary task: sort_desc

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| reverse | 0.9993 | From scratch | 1 | -0.1% | 0.374 | -0.63 | 5 |
| sort_desc | 0.9966 | From scratch | 0.9966 | +0.0% | 1 | 0.00 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| LoRA target modules (q,v vs all linear) | missing |  | NO |
| Learning-rate sweep (LoRA r4, full) | missing |  | NO |

## Why this tier
- loses on: reverse
- not significant on: reverse, sort_desc

## To reach the next tier
- win on every task (or drop/justify the task in PROTOCOL.md)
- p < 0.05 on every task (more seeds or a larger effect)

TARGET NOT REACHED
