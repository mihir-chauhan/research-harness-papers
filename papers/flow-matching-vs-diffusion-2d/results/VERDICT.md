# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: Flow Matching (Euler) | primary metric: sw_k4 | primary task: two_moons

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| checkerboard | 0.2188 | Flow Matching (Heun) | 0.03908 | -459.9% | 7.48e-07 | -23.38 | 5 |
| eight_gaussians | 0.08629 | Flow Matching (Heun) | 0.04584 | -88.2% | 5.89e-06 | -6.74 | 5 |
| two_moons | 0.2634 | Flow Matching (Heun) | 0.04143 | -535.7% | 2.43e-07 | -18.88 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| DDIM (cosine) | missing |  | NO |
| DDIM (cosine, start at ab>=4e-5) | missing |  | NO |
| Reflow-1 (teacher 4 steps) | missing |  | NO |
| Reflow-2 (Euler) | missing |  | NO |

## Why this tier
- not best on two_moons: ours 0.2634 vs Flow Matching (Heun) 0.04143

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
