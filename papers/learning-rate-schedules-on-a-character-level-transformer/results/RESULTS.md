# Results (3 seeds; see paper for tables)
- H1 supported but conditional: best-of-3 cosine 1.67 vs constant 1.76 (Welch p=0.0014); no difference at 1e-3, constant better at 3e-4. High-LR gap is mostly warmup (constant+warmup100 at 1e-2: 1.81 vs 2.42 without).
- H2 refuted: sens3 SF 0.25 vs cosine 0.09 (p=0.0008); sens5 0.54 vs 0.40. SF has lowest best loss (1.63).
- H3 supported: cosine no warmup 2.25 vs 1.69 (50 steps) / 1.67 (300), p~0.001.
- Constant+warmup100 has lowest sens3 (0.06), descriptive only.
Decisive tables: results/tables/{main,sens,abl_warmup,abl_warmup_fair}.md; comparisons compare_*.csv.
