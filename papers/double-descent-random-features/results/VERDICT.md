# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: TunedRidge | primary metric: bump_rel | primary task: synth_n0.5

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| digits_n0 | 0 | GlobalRidge | 0.0004527 | +100.0% | 0.178 | 1.03 | 5 |
| digits_n0.15 | 0.01554 | GlobalRidge | 0.00254 | -511.8% | 0.356 | -0.68 | 5 |
| digits_n0.3 | 0.009187 | GlobalRidge | 0.004257 | -115.8% | 0.205 | -0.77 | 5 |
| digits_n0.6 | 0.01393 | FixedRidge | 0.00466 | -198.9% | 0.374 | -0.62 | 5 |
| synth_n0 | 0.01363 | GlobalRidge | 0.006456 | -111.1% | 0.153 | -1.33 | 5 |
| synth_n0.25 | 0.02264 | GlobalRidge | 0.007456 | -203.6% | 0.077 | -1.31 | 5 |
| synth_n0.5 | 0.0328 | GlobalRidge | 0.01471 | -123.0% | 0.157 | -0.95 | 5 |
| synth_n1 | 0.02506 | FixedRidge | 0.0188 | -33.3% | 0.171 | -0.56 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| abl_tuning | missing |  | NO |
| sweep_lambda | missing |  | NO |

## Why this tier
- not best on synth_n0.5: ours 0.0328 vs GlobalRidge 0.01471

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
