# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: SymFn-sum KRR | primary metric: energy_mae | primary task: lj_clusters

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| lj_clusters | 0.889 | Sorted dist MLP | 0.6347 | -40.1% | 0.0175 | -2.53 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| SymFn-sum KRR radial-only | missing |  | NO |
| SymFn-sum MLP radial-only | missing |  | NO |
| Raw coords MLP + rot/perm aug | missing |  | NO |
| SymFn-sum linear ridge | missing |  | NO |
| SymFn-sum linear ridge radial-only | missing |  | NO |
| Sorted dist linear ridge | missing |  | NO |
| SymFn-sum KRR (narrow grid) | missing |  | NO |
| SymFn-sum KRR (mid grid) | missing |  | NO |

## Why this tier
- not best on lj_clusters: ours 0.889 vs Sorted dist MLP 0.6347

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
