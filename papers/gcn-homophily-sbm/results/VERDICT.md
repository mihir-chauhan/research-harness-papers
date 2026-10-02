# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: GCN (reimplemented) | primary metric: accuracy | primary task: h0.4_mu1.0

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| h0.0_mu0.5 | 0.5293 | H2GCN-style (reimplemented) | 0.6833 | -22.5% | 1.48e-05 | -6.20 | 5 |
| h0.0_mu1.0 | 0.7093 | H2GCN-style (reimplemented) | 0.9107 | -22.1% | 0.000157 | -6.17 | 5 |
| h0.0_mu2.0 | 0.9019 | H2GCN-style (reimplemented) | 0.9837 | -8.3% | 0.000886 | -7.02 | 5 |
| h0.1_mu0.5 | 0.3974 | H2GCN-style (reimplemented) | 0.5037 | -21.1% | 0.00209 | -2.96 | 5 |
| h0.1_mu1.0 | 0.5422 | H2GCN-style (reimplemented) | 0.7237 | -25.1% | 0.000324 | -5.14 | 5 |
| h0.1_mu2.0 | 0.7304 | H2GCN-style (reimplemented) | 0.9252 | -21.1% | 0.000104 | -8.50 | 5 |
| h0.2_mu0.5 | 0.3581 | H2GCN-style (reimplemented) | 0.4315 | -17.0% | 0.00324 | -2.13 | 5 |
| h0.2_mu1.0 | 0.4441 | H2GCN-style (reimplemented) | 0.5874 | -24.4% | 0.000134 | -6.70 | 5 |
| h0.2_mu2.0 | 0.6033 | H2GCN-style (reimplemented) | 0.8478 | -28.8% | 7.77e-06 | -10.25 | 5 |
| h0.3_mu0.5 | 0.3719 | H2GCN-style (reimplemented) | 0.4011 | -7.3% | 0.313 | -0.94 | 5 |
| h0.3_mu1.0 | 0.4485 | MLP | 0.5393 | -16.8% | 0.00729 | -3.51 | 5 |
| h0.3_mu2.0 | 0.577 | MLP | 0.8304 | -30.5% | 1.5e-05 | -13.76 | 5 |
| h0.4_mu0.5 | 0.4 | MLP | 0.3904 | +2.5% | 0.584 | 0.28 | 5 |
| h0.4_mu1.0 | 0.5059 | MLP | 0.5393 | -6.2% | 0.142 | -1.30 | 5 |
| h0.4_mu2.0 | 0.6667 | MLP | 0.8304 | -19.7% | 0.000595 | -5.69 | 5 |
| h0.5_mu0.5 | 0.5059 | Label propagation (reimplemented) | 0.5007 | +1.0% | 0.535 | 0.25 | 5 |
| h0.5_mu1.0 | 0.6381 | H2GCN-style (reimplemented) | 0.6352 | +0.5% | 0.865 | 0.09 | 5 |
| h0.5_mu2.0 | 0.7874 | H2GCN-style (reimplemented) | 0.8648 | -9.0% | 0.00231 | -2.47 | 5 |
| h0.6_mu0.5 | 0.6241 | Label propagation (reimplemented) | 0.6644 | -6.1% | 0.0394 | -1.27 | 5 |
| h0.6_mu1.0 | 0.7922 | H2GCN-style (reimplemented) | 0.7696 | +2.9% | 0.0214 | 0.89 | 5 |
| h0.6_mu2.0 | 0.8974 | H2GCN-style (reimplemented) | 0.9141 | -1.8% | 0.101 | -0.73 | 5 |
| h0.7_mu0.5 | 0.7593 | Label propagation (reimplemented) | 0.8381 | -9.4% | 0.00345 | -3.70 | 5 |
| h0.7_mu1.0 | 0.9044 | H2GCN-style (reimplemented) | 0.89 | +1.6% | 0.168 | 0.96 | 5 |
| h0.7_mu2.0 | 0.9637 | H2GCN-style (reimplemented) | 0.9656 | -0.2% | 0.611 | -0.21 | 5 |
| h0.8_mu0.5 | 0.8807 | Label propagation (reimplemented) | 0.9596 | -8.2% | 0.000631 | -6.18 | 5 |
| h0.8_mu1.0 | 0.97 | H2GCN-style (reimplemented) | 0.967 | +0.3% | 0.338 | 0.29 | 5 |
| h0.8_mu2.0 | 0.9941 | H2GCN-style (reimplemented) | 0.9856 | +0.9% | 0.0635 | 1.34 | 5 |
| h0.9_mu0.5 | 0.9519 | Label propagation (reimplemented) | 0.9959 | -4.4% | 0.00263 | -5.06 | 5 |
| h0.9_mu1.0 | 0.9922 | Label propagation (reimplemented) | 0.9959 | -0.4% | 0.363 | -0.71 | 5 |
| h0.9_mu2.0 | 0.9963 | H2GCN-style (reimplemented) | 0.9978 | -0.1% | 0.242 | -0.45 | 5 |
| h1.0_mu0.5 | 0.9819 | Label propagation (reimplemented) | 1 | -1.8% | 0.00139 | -4.99 | 5 |
| h1.0_mu1.0 | 0.997 | Label propagation (reimplemented) | 1 | -0.3% | 0.0777 | -1.49 | 5 |
| h1.0_mu2.0 | 0.9993 | Label propagation (reimplemented) | 1 | -0.1% | 0.374 | -0.63 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| H2GCN without ego/neighbour separation | missing |  | NO |
| H2GCN with 2-hop neighbourhood | missing |  | NO |

## Why this tier
- not best on h0.4_mu1.0: ours 0.5059 vs MLP 0.5393

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
