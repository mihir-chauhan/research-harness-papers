# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: DT-CBF | primary metric: violation_rate | primary task: double_integrator

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| double_integrator | 0.008 | CT-CBF | 0 | +nan% | 0.0993 | -1.35 | 5 |
| unicycle | 0 | Braking | 0 | +nan% | nan | -inf | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| CT-CBF | missing |  | NO |
| DT-CBF | missing |  | NO |
| Braking | missing |  | NO |

## Why this tier
- not best on double_integrator: ours 0.008 vs CT-CBF 0

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
