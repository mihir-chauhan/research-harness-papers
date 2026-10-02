# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: Templated language (proxy) | primary metric: success_rate | primary task: rendezvous

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| rendezvous | 0.9309 | Continuous vector (DIAL-style, reimplemented) | 1 | -6.9% | 0.000104 | -9.73 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| Templated language (proxy) | missing |  | NO |
| Discrete tokens (Gumbel-softmax, reimplemented) | missing |  | NO |
| Continuous vector (DIAL-style, reimplemented) | missing |  | NO |

## Why this tier
- not best on rendezvous: ours 0.9309 vs Continuous vector (DIAL-style, reimplemented) 1

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
