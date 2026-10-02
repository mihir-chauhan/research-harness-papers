# Verdict: tier 1 (marginal) — target tier 2 (solid)

Method: SimCLR-style probe | primary metric: test_acc | primary task: n50

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| n10 | 0.8262 | Supervised scratch | 0.662 | +24.8% | 0.000285 | 4.07 | 5 |
| n200 | 0.9787 | Supervised scratch | 0.9763 | +0.2% | 0.178 | 0.25 | 5 |
| n50 | 0.9549 | Supervised scratch | 0.9183 | +4.0% | 0.024 | 2.46 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| abl_aug (geometric only, photometric only) | missing |  | NO |
| sweep_tau | missing |  | NO |
| sweep_epochs | missing |  | NO |

## Why this tier
- not significant on: n200

## To reach the next tier
- p < 0.05 on every task (more seeds or a larger effect)

TARGET NOT REACHED
