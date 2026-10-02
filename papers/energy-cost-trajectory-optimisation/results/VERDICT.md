# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: iLQR-Energy (ours) | primary metric: success_rate | primary task: pendulum

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| cartpole | 1 | iLQR-Quad | 1 | +0.0% | nan | inf | 5 |
| pendulum | 0.95 | EnergyShaping-LQR | 0.98 | -3.1% | 0.0705 | -0.74 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| iLQR-Energy (ours) | missing |  | NO |
| iLQR-Quad | missing |  | NO |

## Why this tier
- not best on pendulum: ours 0.95 vs EnergyShaping-LQR 0.98

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
