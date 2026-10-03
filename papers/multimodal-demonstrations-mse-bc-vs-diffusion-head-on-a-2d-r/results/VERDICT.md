# Verdict: tier 0 (not best) — target tier 2 (solid)

Method: DDPM head | primary metric: success | primary task: bimodal50

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| bimodal50 | 0.999 | GMM head | 1 | -0.1% | 0.168 | -0.67 | 10 |
| bimodal80 | 0.9985 | GMM head | 1 | -0.2% | 0.343 | -0.45 | 10 |
| unimodal | 1 | GMM head | 1 | +0.0% | nan | inf | 10 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| denoising steps | missing |  | NO |
| GMM components | missing |  | NO |
| action chunk length | missing |  | NO |
| start jitter | missing |  | NO |

## Why this tier
- not best on bimodal50: ours 0.999 vs GMM head 1

## To reach the next tier
- beat the best baseline on the primary task

TARGET NOT REACHED
