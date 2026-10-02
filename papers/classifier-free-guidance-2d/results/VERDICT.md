# Verdict: tier 2 (solid) — target tier 2 (solid)

Method: CFG (w=3) | primary metric: class_acc | primary task: mix_overlap

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| mix_overlap | 0.9995 | Low-temperature (tau=0.5) | 0.9932 | +0.6% | 3.8e-06 | 11.10 | 5 |
| mix_sep | 0.9998 | Low-temperature (tau=0.5) | 0.9988 | +0.1% | 0.00257 | 4.54 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| label dropout probability | missing |  | NO |
| guidance interval | missing |  | NO |
| guidance scale sweep | missing |  | NO |
| temperature sweep | missing |  | NO |

## Why this tier
- relative gain below 10% on: mix_overlap (+0.6%), mix_sep (+0.1%)
- ablations that do not significantly hurt: label dropout probability, guidance interval, guidance scale sweep, temperature sweep

TARGET REACHED
