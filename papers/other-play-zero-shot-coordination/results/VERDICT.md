# Verdict: tier 1 (marginal) — target tier 2 (solid)

Method: Other-play | primary metric: cross_play | primary task: lever

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| lever | 0.1527 | Population (FCP-style) | 0.08796 | +73.6% | 0.0489 | 1.53 | 5 |
| safe | 0.5 | Population (FCP-style) | 0.4875 | +2.6% | 0.0826 | 1.46 | 5 |
| signal | 0.3999 | Population (FCP-style) | 0.3372 | +18.6% | 1.15e-05 | 16.95 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| OP-full (wrong group) | missing |  | NO |
| Population (FCP-style) | missing |  | NO |
| Other-play | missing |  | NO |

## Why this tier
- not significant on: safe

## To reach the next tier
- p < 0.05 on every task (more seeds or a larger effect)

TARGET NOT REACHED

Note (author): p-values in the table above are paired by seed (lever OP vs population: 0.0489); the paper reports Welch tests from `rh compare` (0.063, 0.053 vs SP), the more conservative reading. The ablation rows show "missing" because the harness cannot map our ablation group/config names to the method rows; the ablations are evaluated in the paper (Tables for symmetry, population size, init scale, training length), not here.
