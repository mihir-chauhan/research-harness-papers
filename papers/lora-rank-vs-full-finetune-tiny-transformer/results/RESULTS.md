# Results (tables: results/tables/main.md, tab_rank.md, tab_tests.md, tab_targets.md, tab_ntrain.md, tab_lr.md)
- H1 supported (this setting): LoRA r=4 (7168 params, 10.2% of full) 0.997 vs full 0.996 on sort_desc (paired p=0.82), 0.999 vs 1.000 on reverse (p=0.37). Caveat: from-scratch equals both at N=2000; ceiling effect.
- H2 supported on sort_desc (0.978, 0.994, 0.997, 0.997 for r=1,2,4,8); not interpretable on reverse: whole-run optimisation failures (r=1: 1/5, r=2: 1/5, r=8 partial) at the tuned lr.
- H3 not supported and uninformative: retention is at floor for every adapted system including head-only (pretask acc 0.000-0.004 mean), also across the lr sweep.
- H4 supported on sort_desc (last block 0.965 vs LoRA r=4 0.997, p=0.0008); equal on reverse. Head-only fails.
- Ablations: q,v-only LoRA worse at low rank; N sweep (3 seeds): pretrained full FT above scratch; LoRA r=1,4 have higher means than full FT but no paired test is significant (p>0.05, full-FT lr tuned at N=2000 only) so LoRA-vs-full at small N is inconclusive; r=8 fails; lr sweep: LoRA more lr-sensitive than full FT.

- Note: VERDICT.md ablation rows read 'missing' because the ablation deltas are in the custom tables (tab_targets, tab_ntrain, tab_lr), not in rh groups it can resolve. LoRA lr tuned at r=4 only.
