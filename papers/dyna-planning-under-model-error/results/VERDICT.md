# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: Dyna-Q | primary metric: cum_reward | primary task: blocking

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| blocking | 64.5 | Dyna-Q+ | 92.55 | -30.3% | 0.00929 | -0.94 | 20 |
| shortcut | 256.8 | Dyna-Q+ | 315.9 | -18.7% | 6.49e-06 | -1.70 | 20 |
| static | 200.2 | Prioritized sweeping | 220.6 | -9.3% | 0.217 | -0.42 | 20 |
| stoch_blocking | 22 | Dyna-Q+ | 33.9 | -35.1% | 0.0182 | -0.94 | 20 |
| stochastic | 71.05 | Prioritized sweeping | 74.15 | -4.2% | 0.658 | -0.14 | 20 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| Dyna-Q+ w/o bonus | missing |  | NO |
| Dyna-Q+ w/o untried | missing |  | NO |
| Dyna-Q+ w/o both | missing |  | NO |

## Why this tier
- not best on blocking: ours 64.5 vs Dyna-Q+ 92.55

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
