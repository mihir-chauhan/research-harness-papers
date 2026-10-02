# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: LR + no correction | primary metric: brier | primary task: bc_1to20

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| bc_1to20 | 0.008225 | LR + SMOTE | 0.008179 | -0.6% | 0.962 | -0.02 | 10 |
| bc_1to5 | 0.01599 | LR + threshold | 0.01599 | -0.0% | 1 | -0.00 | 10 |
| bc_1to50 | 0.004685 | LR + threshold | 0.004685 | -0.0% | nan | -0.00 | 10 |
| bc_natural | 0.02425 | LR + threshold | 0.02425 | -0.0% | 1 | -0.00 | 10 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| LR + reweight + prior corr | missing |  | NO |
| LR + ROS + prior corr | missing |  | NO |
| LR + SMOTE + prior corr | missing |  | NO |
| GB + reweight + prior corr | missing |  | NO |
| GB + ROS + prior corr | missing |  | NO |
| GB + SMOTE + prior corr | missing |  | NO |
| LR + SMOTE | missing |  | NO |
| GB + SMOTE | missing |  | NO |

## Why this tier
- not best on bc_1to20: ours 0.008225 vs LR + SMOTE 0.008179

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
