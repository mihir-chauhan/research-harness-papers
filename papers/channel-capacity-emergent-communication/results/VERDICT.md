# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: Gumbel-softmax sender-receiver | primary metric: heldout_acc | primary task: V8_L4

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| V16_L5 | 0.4872 | nan | nan | +nan% | nan | nan | 3 |
| V16_L8 | 0.4359 | Oracle compositional code (reference) | 0.8462 | -48.5% | 0.119 | -2.47 | 3 |
| V2_L5 | 0 | nan | nan | +nan% | nan | nan | 3 |
| V3_L5 | 0 | nan | nan | +nan% | nan | nan | 3 |
| V4_L4 | 0.01282 | Oracle compositional code (reference) | 1 | -98.7% | 0.000169 | -62.87 | 3 |
| V4_L5 | 0 | nan | nan | +nan% | nan | nan | 3 |
| V6_L2 | 0.01282 | nan | nan | +nan% | nan | nan | 3 |
| V6_L3 | 0.01282 | nan | nan | +nan% | nan | nan | 3 |
| V6_L4 | 0 | nan | nan | +nan% | nan | nan | 3 |
| V6_L6 | 0.141 | nan | nan | +nan% | nan | nan | 3 |
| V6_L8 | 0.07692 | nan | nan | +nan% | nan | nan | 3 |
| V8_L4 | 0.02564 | Oracle compositional code (reference) | 1 | -97.4% | 0.000173 | -62.05 | 3 |
| V8_L5 | 0.0641 | nan | nan | +nan% | nan | nan | 3 |

## Why this tier
- not best on V8_L4: ours 0.02564 vs Oracle compositional code (reference) 1

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
