# Verdict: tier 1 (marginal) — target tier 2 (solid)

Method: Weak-form STLSQ | primary metric: support_exact | primary task: lorenz_n2

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| lorenz_n0 | 1 | FD-STLSQ | 1 | +0.0% | nan | inf | 20 |
| lorenz_n0.5 | 1 | FD-STLSQ | 1 | +0.0% | nan | inf | 20 |
| lorenz_n1 | 1 | SG-STLSQ | 1 | +0.0% | nan | inf | 20 |
| lorenz_n10 | 0.1 | FD-STLSQ | 0 | +nan% | 0.163 | 0.46 | 20 |
| lorenz_n2 | 1 | SG-STLSQ | 0.9 | +11.1% | 0.163 | 0.46 | 20 |
| lorenz_n5 | 0.65 | TV-STLSQ | 0.4 | +62.5% | 0.0961 | 0.50 | 20 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| Weak-form STLSQ | missing |  | NO |
| SG-STLSQ (smoothed library) | missing |  | NO |
| Spline-STLSQ (smoothed library) | missing |  | NO |
| SG-STLSQ | missing |  | NO |
| FD-STLSQ | missing |  | NO |

## Why this tier
- loses on: lorenz_n0, lorenz_n0.5, lorenz_n1
- not significant on: lorenz_n0, lorenz_n0.5, lorenz_n1, lorenz_n10, lorenz_n2, lorenz_n5

## To reach the next tier
- win on every task (or drop/justify the task in PROTOCOL.md)
- p < 0.05 on every task (more seeds or a larger effect)

TARGET NOT REACHED
