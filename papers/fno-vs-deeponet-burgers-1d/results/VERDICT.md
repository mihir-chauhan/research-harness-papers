# Verdict: tier 2 (solid) — target tier 2 (solid)

Method: FNO | primary metric: rel_l2 | primary task: burgers_nu0.01

| Task | Ours | Best baseline | Their mean | Rel. gain | p | Cohen d | n |
|---|---|---|---|---|---|---|---|
| burgers_nu0.01 | 0.004884 | MLP | 0.08339 | +94.1% | 1.28e-05 | 15.99 | 5 |

| Ablation | Delta vs full | p | Matters? |
|---|---|---|---|
| FNO modes=4 | missing |  | NO |
| FNO modes=8 | missing |  | NO |
| FNO modes=32 | missing |  | NO |
| FNO no grid channel | missing |  | NO |
| FNO n=100 | missing |  | NO |
| FNO n=200 | missing |  | NO |
| DeepONet n=100 | missing |  | NO |
| DeepONet n=200 | missing |  | NO |
| DeepONet ep=500 | missing |  | NO |
| DeepONet ep=2000 | missing |  | NO |
| MLP ep=500 | missing |  | NO |
| MLP ep=2000 | missing |  | NO |

## Why this tier
- ablations that do not significantly hurt: FNO modes=4, FNO modes=8, FNO modes=32, FNO no grid channel, FNO n=100, FNO n=200, DeepONet n=100, DeepONet n=200, DeepONet ep=500, DeepONet ep=2000, MLP ep=500, MLP ep=2000

TARGET REACHED

## Notes added by hand (not produced by `rh verdict`)
- The p-value in the first table is the tool's paired t-test (it pairs runs when the seeds coincide). The test registered in `proposal.md` for H1 is the Welch test: p = 1.4e-05 against the MLP (`results/tables/h1.tex`, `rh compare --metric rel_l2 --group main`).
- The ablation rows read "missing / NO" because the tool looks for the method's own (FNO) rows inside each ablation group; the reference FNO runs are in group `main` and identical runs are not re-logged under another group. The rows are therefore not evaluated, which is not the same as "does not matter". Since the conform pass the seed 0-2 default runs are copied into the ablation groups (`rh log --from-run`) and the ratios and Welch p-values against the default rows are in `results/tables/compare_<group>_rel_l2.csv` (`rh compare`); `results/tables/ablsum.md` was removed and this file was not regenerated. The DeepONet/MLP rows are baseline sensitivity runs, not ablations of the method.
