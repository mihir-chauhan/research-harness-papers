# Results (see paper/main.pdf for numbers; tables in results/tables/)

Main table: results/tables/main.md (Spearman, top-100 recall), results/tables/main_hd.md (per Hamming distance), results/tables/gap_hd.tex (random minus dbl training).
Ablations: abl_logtarget, abl_cnn, abl_gp, sweep_alpha (alpha_sweep.tex), tune_cnn (CNN configuration choice on seed 100).

| H | Verdict | Deciding rows |
|---|---|---|
| H1 pairwise helps only at N>=384 (random) | refuted by the mean rule; differences are within noise (no detectable effect); pairwise collapses under dbl training at N>=384 | main rand_48..rand_2000, dbl_384, dbl_2000 |
| H2 GP >= ridge at N<=96 | supported in the mean, statistically inconclusive | main rand_48, rand_96 |
| H3 CNN worse than best baseline at N<=384 | refuted (CNN highest mean at N=96, 384, 2000; lowest at 48) | main; caveat: log-target ablation removes most of the gap |
| H4 dbl training worse on HD>=3 for every system | refuted at N<=96 (HD3), supported at N>=384 | gap_hd.tex |
| H5 top-100 recall < 0.25 at N<=384 | supported | main top100_recall |

Tests: rh compare paired t-test p-values are descriptive (proposal amendment); verdicts follow the mean-based rules.
