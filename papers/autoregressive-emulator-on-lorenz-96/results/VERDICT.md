# Verdict: tier 2 (solid) — target tier 2 (solid)

Method: CNN K=4 | primary metric: rmse_t20 | primary task: l96

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| l96 | 1.29 | CNN K=1 | 1.308 | +1.4% | 0.0319 | 0.46 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| rollout length K | missing |  | NO |
| input noise | missing |  | NO |

## Why this tier
- relative gain below 10% on: l96 (+1.4%)
- ablations that do not significantly hurt: rollout length K, input noise

TARGET REACHED

> Annotation: the automatic tier above rests on a +1.4% gain for K=4 (paired p=0.032, Welch p=0.49) and its ablation deltas are marked 'missing' by the tool. The paper's own reading is more conservative: H1 supported for K=8 (about 5% RMSE reduction at lead 2), weak for K=4; H2 and H3 not supported. The "TARGET REACHED" line should not be read as a strong result.
