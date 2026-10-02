# Verdict: tier 2 (solid) — target tier 2 (solid)

Method: Conditional AR designer | primary metric: succ_k100 | primary task: hp16

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| hp16 | 0.8645 | Contact heuristic | 0.6846 | +26.3% | 0.000604 | 4.59 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| Unconditional AR | -0.8645 | 6.09e-07 | yes |
| No reversal augmentation | +0.03333 | 0.0459 | NO |

## Why this tier
- ablations that do not significantly hurt: No reversal augmentation

TARGET REACHED
