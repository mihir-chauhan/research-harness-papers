# Verdict: tier 1 (marginal) — target tier 1 (marginal)

Method: Pairwise ridge | primary metric: spearman | primary task: L15_A4_K2

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| L15_A4_K0 | 1 | Additive ridge | 1 | -0.0% | 0.000129 | -9.20 | 5 |
| L15_A4_K1 | 0.9979 | MLP | 0.815 | +22.4% | 4.62e-05 | 12.71 | 5 |
| L15_A4_K2 | 0.5078 | CNN | 0.3837 | +32.3% | 0.00702 | 1.98 | 5 |
| L15_A4_K4 | 0.08009 | Additive ridge | 0.07891 | +1.5% | 0.778 | 0.06 | 5 |
| L20_A20_K0 | 0.9951 | Additive ridge | 1 | -0.5% | 1.34e-05 | -16.31 | 5 |
| L20_A20_K1 | 0.1382 | Additive ridge | 0.1097 | +26.0% | 0.0538 | 0.84 | 5 |
| L20_A20_K2 | 0.02517 | Additive ridge | 0.02131 | +18.1% | 0.16 | 0.25 | 5 |
| L20_A20_K4 | 0.01419 | Additive ridge | 0.01393 | +1.9% | 0.794 | 0.03 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| Pairwise ridge (r fixed) | missing |  | NO |
| Pairwise ridge (oracle graph) | missing |  | NO |

## Why this tier
- loses on: L15_A4_K0, L20_A20_K0
- not significant on: L15_A4_K4, L20_A20_K1, L20_A20_K2, L20_A20_K4

TARGET REACHED
