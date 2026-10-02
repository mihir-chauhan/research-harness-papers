# Results
Registered tests (proposal.md / research.yaml): `rh compare` on seed-level MAE against MPNN-max + steps, 5 seeds.
- H1 (max+steps beats sum+steps at S64): not supported (means 1.955 vs 5.5e4, Welch/paired p=0.374; medians 1.765 vs 0.460 point the other way). Post hoc S16 test: paired p=0.231.
- H2 (steps help max at S64): not supported (means 1.955 with steps vs 0.909 without, p=0.363; wrong sign, within noise). Post hoc, uncorrected: S16 paired p=0.041 with steps worse; exploratory only.
- H3 (MLP worse than every MPNN, n>=16): supported at S16 against max+steps (Welch p=7.5e-07, paired p=4.2e-06, from rh compare), not supported at S64 (p=0.535). Only the comparison against max+steps was tested.
- H4 (sum degrades more under growing degree, registered pair sum+steps vs max+steps, per-seed D64/D8): direction as hypothesised in 5/5 seeds (D8 errors similar; sum+steps D64 non-finite in 4 seeds and 1e17 in the fifth, max+steps D64 finite, at most 35.55); no test registered or possible. Final-only pair (post hoc): per-seed D64 errors overlap; inconclusive. The quotients are no longer printed (not registry values); perseed.tex lists D64 and D8 per seed.
- Primary metric (mean mae_sparse_n64): MPNN-sum 0.23 +/- 0.19 is lowest, then MPNN-max 0.91 +/- 1.22. Medians and failure counts are post hoc descriptive choices.
- Non-finite errors: sum+steps D64 in seeds 0,1,2,4 (seed 3: 1e17); MPNN-sum D64 seed 4.
- Step sweep (step-supervised systems only, seeds 0-2; x4 post hoc): S16 error rises at x2 and x4 in all six models; S64 error is clearly higher at x4 than at x1 in four of six (max+steps seed 0 and sum+steps seed 1 change little). Final-only systems were not swept.
Tables: results/tables/main.md, robust.tex, perseed.tex, hyp_table.tex, agg_table.tex, sweep_table.tex (built by analysis/make_tables.py and analysis/hyp_table.py from results/runs.jsonl and the rh compare CSVs). Figures: results/figures/.
