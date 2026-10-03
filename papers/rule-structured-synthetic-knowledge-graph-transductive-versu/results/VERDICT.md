# Verdict: tier 2 (solid) — target tier 2 (solid)

Method: Path-MP (2-hop) | primary metric: mrr | primary task: inductive

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| inductive | 0.9889 | Rule oracle (hand-written) | 0.9503 | +4.1% | 0.00382 | 2.59 | 5 |
| transductive | 0.9877 | Rule oracle (hand-written) | 0.9369 | +5.4% | 0.00961 | 2.73 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| sweep_layers | missing |  | NO |
| abl_nodrop | missing |  | NO |
| sweep_density | missing |  | NO |

## Why this tier
- relative gain below 10% on: inductive (+4.1%), transductive (+5.4%)
- ablations that do not significantly hurt: sweep_layers, abl_nodrop, sweep_density

TARGET REACHED
