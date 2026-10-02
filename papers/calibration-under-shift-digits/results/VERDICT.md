# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: MLP + temperature scaling | primary metric: ece | primary task: rot60

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| noise0.25 | 0.06725 | MC dropout | 0.04299 | -56.4% | 0.0251 | -1.40 | 5 |
| noise0.5 | 0.3352 | MC dropout | 0.2797 | -19.9% | 0.0587 | -1.24 | 5 |
| noise0.75 | 0.5237 | MC dropout | 0.4736 | -10.6% | 0.117 | -1.21 | 5 |
| noise1.0 | 0.618 | MC dropout | 0.5547 | -11.4% | 0.0216 | -1.81 | 5 |
| rot0 | 0.01597 | MC dropout | 0.01563 | -2.2% | 0.852 | -0.11 | 5 |
| rot10 | 0.07018 | MC dropout | 0.04239 | -65.6% | 0.0708 | -1.36 | 5 |
| rot20 | 0.1615 | MC dropout | 0.149 | -8.4% | 0.628 | -0.36 | 5 |
| rot30 | 0.3879 | MC dropout | 0.3606 | -7.6% | 0.427 | -0.36 | 5 |
| rot30_noise0.5 | 0.6119 | MC dropout | 0.5785 | -5.8% | 0.188 | -0.57 | 5 |
| rot45 | 0.7845 | MC dropout | 0.7523 | -4.3% | 0.189 | -0.44 | 5 |
| rot60 | 0.8025 | MC dropout | 0.7921 | -1.3% | 0.545 | -0.14 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| TS oracle (shifted val) | missing |  | NO |
| Deep ensemble | missing |  | NO |
| MC dropout | missing |  | NO |
| Dropout-trained MLP, deterministic | missing |  | NO |

## Why this tier
- not best on rot60: ours 0.8025 vs MC dropout 0.7921

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
