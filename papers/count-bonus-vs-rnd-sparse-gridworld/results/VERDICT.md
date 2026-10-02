# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: RND bonus | primary metric: steps_to_first_reward | primary task: room_4

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| chain_10 | 524.8 | Count bonus (obs) | 88.4 | -493.7% | 0.0432 | -1.73 | 5 |
| chain_20 | 2146 | Count bonus (obs) | 475.8 | -351.0% | 0.00193 | -4.62 | 5 |
| chain_20_tv | 2387 | Count bonus (state) | 500 | -377.5% | 8.4e-05 | -10.65 | 5 |
| chain_40 | 5242 | Count bonus (obs) | 2603 | -101.4% | 0.00429 | -4.48 | 5 |
| room_2 | 3905 | Step penalty only (optimistic init) | 982.4 | -297.5% | 0.00159 | -5.66 | 5 |
| room_4 | 1.843e+04 | Count bonus (obs) | 1.148e+04 | -60.6% | 0.0354 | -2.13 | 5 |
| room_4_tv | 1.518e+04 | Count bonus (obs) | 1.114e+04 | -36.3% | 0.0387 | -1.28 | 5 |
| room_6 | 7.628e+04 | Count bonus (obs) | 2.844e+04 | -168.2% | 0.00617 | -3.16 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| no bonus normalisation (rnd_nonorm) | +8079 | 0.0574 | NO |
| RND, unguarded normaliser (v1) | -2.639e+04 | 0.00124 | yes |
| RND, warm-up only | -1247 | 0.834 | NO |
| RND, clip only | -905 | 0.871 | NO |

## Why this tier
- not best on room_4: ours 1.843e+04 vs Count bonus (obs) 1.148e+04

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED

Note: the ablation deltas above pool all eight tasks (steps to first reward, lower is better; a negative delta means the variant is slower). Per-task numbers are in results/tables/main_compact.md. The "best baseline" column does not account for the offset confound: the penalty-only control explains the gain of the count bonus (results/RESULTS.md).
