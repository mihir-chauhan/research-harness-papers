# Results (after the audit fix round)
Tables: results/tables/{maintab,lcurve,tests,abl,steps,grid,hp}.tex from experiments/analyze.py (ok, non-superseded rows of
results/runs.jsonl; maintab has the same numbers as `rh table --group main`). Tests: results/analysis_stats.txt and
`rh compare` (results/tables/compare_main_energy_mae*.csv). All p-values are two-sided Welch tests over seeds.

- H1 supported: at n=500 each invariant descriptor beats raw coordinates for both regressors (four tests, p < 0.001).
  Raw KRR is not distinguishable from the mean predictor (12.178 vs 12.203, p=0.90; p >= 0.062 at every n);
  raw MLP is worse than the mean predictor (15.028).
- H2 split: invariant systems unchanged, largest per-seed defect 8.34e-5 (SymFn-sum KRR; single configurations up to 4.2e-3
  in main, 8.2e-3 at n=50), below the registered 1e-4. Raw ">= 2x degradation" refuted (ratio about 1); raw defect 2.88 / 15.2.
- H3 supported with caveats: SF-KRR < sorted KRR at n=50 (2.65 vs 3.93, p=0.012) and n=150 (1.49 vs 2.07, p=0.032);
  still ahead at n=500 (0.889 vs 1.095, p=0.026), behind at n=1500 (0.71 vs 0.45, p=0.022). 3 seeds, uncorrected.
  The first version (narrow KRR grid) had the opposite direction; the verdict depends on the grid (table grid).
- H4 mixed: KRR ahead for raw (uninformative) and SF input; MLP ahead for sorted distances up to n=500, tie at 1500.
  Nominally supported by the registered majority criterion, weak.
- KRR grid sensitivity (n=500, 5 seeds): SF-KRR 1.587 (narrow), 0.907 (mid), 0.889 (wide); sorted KRR 1.096 / 1.095 / 1.095.
  Selected gamma interior in all wide-grid runs but one; selected lambda of SF-KRR is the smallest feasible value in 13/14 runs
  (not bracketable in double precision; disclosed in the paper).
- Linear ridge on the SF descriptor: 0.805 (p=0.27 vs RBF KRR); on sorted distances 5.647.
- Angular functions: no resolved effect (KRR radial-only 0.785 vs 0.889, p=0.19; MLP 4.582 vs 4.610, p=0.83).
- Augmentation of raw MLP: 9.773 vs 15.090 (p < 0.001), defect 1.7.
- MLP steps: sorted MLP 0.89 / 0.65 / 0.54 (1000 / 3000 / 12000; p=0.003, 0.006 vs 3000); SF MLP 4.81 / 4.61 / 4.39 (p=0.26, 0.056).
- Failure cases: SF-sum MLP (4.513) and atomwise MLP (3.130) are far worse than linear ridge on the same features;
  SF-KRR saturates between n=500 and 1500.

Note on results/VERDICT.md: its ablation table says "missing" because `rh verdict` looks for rows of the method inside the
ablation group, and the full-model rows live in group main (re-logging them under another group is not allowed).
The ablation tests are in results/tables/abl.tex and results/analysis_stats.txt.
