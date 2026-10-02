# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: RBM alpha=2 SR | primary metric: rel_energy_error | primary task: tfim_N10_g1.00

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| tfim_N10_g0.25 | 8.904e-05 | RBM alpha=4 SR | 2.357e-05 | -277.8% | 0.246 | -0.75 | 5 |
| tfim_N10_g0.50 | 8.288e-05 | RBM alpha=4 SR | 6.058e-05 | -36.8% | 0.597 | -0.39 | 5 |
| tfim_N10_g0.75 | nan | RBM alpha=4 SR | 9.561e-05 | +nan% | nan | -inf | 5 |
| tfim_N10_g1.00 | nan | RBM alpha=4 SR | 2.78e-05 | +nan% | nan | -inf | 5 |
| tfim_N10_g1.25 | nan | RBM alpha=4 SR | nan | +nan% | nan | -inf | 5 |
| tfim_N10_g1.50 | nan | RBM alpha=4 SR | nan | +nan% | nan | -inf | 5 |
| tfim_N10_g2.00 | nan | RBM alpha=1 SR | 9.224e-07 | +nan% | nan | -inf | 5 |
| tfim_N12_g0.50 | 6.144e-05 | RBM alpha=4 SR | nan | +nan% | nan | -inf | 5 |
| tfim_N12_g1.00 | nan | RBM alpha=4 SR | nan | +nan% | nan | -inf | 5 |
| tfim_N12_g1.50 | nan | RBM alpha=4 SR | nan | +nan% | nan | -inf | 5 |
| tfim_N8_g0.50 | 5.997e-05 | RBM alpha=4 SR | 5.218e-05 | -14.9% | 0.396 | -0.52 | 5 |
| tfim_N8_g1.00 | 1.739e-05 | RBM alpha=4 SR | nan | +nan% | nan | -inf | 5 |
| tfim_N8_g1.50 | 1.408e-06 | RBM alpha=4 SR | nan | +nan% | nan | -inf | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| RBM alpha=2 SR | missing |  | NO |
| Mean-field exact-gradient | missing |  | NO |
| Jastrow exact-gradient | missing |  | NO |
| RBM alpha=2 exact-gradient | missing |  | NO |

## Why this tier
- not best on tfim_N10_g1.00: ours nan vs RBM alpha=4 SR 2.78e-05

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
