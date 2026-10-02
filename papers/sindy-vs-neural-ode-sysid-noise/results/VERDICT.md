# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: SINDy (STLSQ) | primary metric: pred_nrmse | primary task: pendulum_noise0.05

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| pendulum_noise0.0 | 0.006771 | True model (oracle) | 0 | +nan% | 2.94e-06 | -23.88 | 5 |
| pendulum_noise0.02 | 0.03002 | True model (oracle) | 0 | +nan% | 0.00926 | -2.98 | 5 |
| pendulum_noise0.05 | 0.1559 | True model (oracle) | 0 | +nan% | 0.00489 | -3.56 | 5 |
| pendulum_noise0.1 | 0.4635 | True model (oracle) | 0 | +nan% | 0.000926 | -5.56 | 5 |
| vdp_noise0.0 | 0.003789 | True model (oracle) | 0 | +nan% | 4.84e-06 | -21.07 | 5 |
| vdp_noise0.02 | 0.006475 | True model (oracle) | 0 | +nan% | 0.00107 | -5.35 | 5 |
| vdp_noise0.05 | 0.0184 | True model (oracle) | 0 | +nan% | 0.000641 | -6.11 | 5 |
| vdp_noise0.1 | 0.389 | True model (oracle) | 0 | +nan% | 0.316 | -0.72 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| SINDy w/o trig library | -0.5305 | 0.0202 | yes |
| SINDy + SG smoothing | +0.01772 | 0.385 | NO |
| SINDy + SG smoothing, lam 0.3 | +0.03228 | 0.229 | NO |

## Why this tier
- not best on pendulum_noise0.05: ours 0.1559 vs True model (oracle) 0

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
