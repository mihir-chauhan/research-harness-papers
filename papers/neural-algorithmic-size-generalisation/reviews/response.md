# Response to the audit

No new experiments were run in this round; every change is to text, tables or figures, all regenerated from
`results/runs.jsonl` and the `rh compare` CSVs by `analysis/make_tables.py` and `analysis/hyp_table.py`.

1. **(major) "No trained processor is a stable fixed-point iteration" overgeneralised.** Fixed by scoping, not by new
   runs. Abstract, introduction (contribution iii), ablations and conclusion now say the sweep covers the two
   step-supervised systems on three seeds and that the final-only models were not swept (also added as limitation vii).
   While re-checking the claim seed by seed we found it was too strong even for the swept models: at S64, max+steps
   seed 0 (0.21 to 0.23) and sum+steps seed 1 (0.46 throughout) barely change with extra steps. Table VI now lists
   every seed next to the median, and the text says: S16 error rises at x2 and x4 in all six models, S64 error rises
   by more than 8x at x4 in four of six.
2. **"Diverged in all five seeds".** Fixed. Abstract, H1 paragraph and conclusion now say 4/5 non-finite and one seed of
   order 1e17; the non-finite D64 value of final-only MPNN-sum seed 4 is stated in "Where it fails" and the conclusion.
   A new per-seed table (Table III: S64, D64, D64/D8 for all 25 main runs) backs these statements.
3. **H4 "ranking depends on whether steps are used".** Removed. The H4 paragraph is rewritten around the registered
   pair (sum+steps vs max+steps, per-seed D64/D8): direction as hypothesised in 5/5 seeds, no test registered or
   possible on non-finite values. The final-only pair is reported as post hoc: same direction of medians, overlapping
   per-seed ranges, opposite failure counts, inconclusive.
4. **"A few thousand parameters".** Fixed: 12,770 (MPNN) and 557,376 (MLP), counted from the code, in the introduction
   and the method section.
5. **Primary metric vs post hoc median.** Fixed. Abstract, results opening and conclusion state that on the registered
   primary metric (mean S64 MAE) final-only MPNN-sum is lowest (0.23 vs 0.91) with no failing sparse seed, and that
   medians were chosen post hoc.
6. **Registered vs post hoc tests.** Fixed. Table IV marks the S16 rows of H1/H2 as post hoc and uncorrected; the
   caption no longer says "registered comparisons". H2 is now "not supported" on the registered S64 test, with the S16
   p=0.041 described as exploratory. The x4 multiplier is marked post hoc in Table VI, the ablation text and the setup;
   the setup has an explicit list of what was registered and what was not.
7. **Constant predictor.** Fixed by rewording: the MLP's relative error is compared with predicting zero (relative
   error 1 by definition); limitation (v) now says no trivial reference predictor was run.
8. **Per-seed test sets.** Fixed: the setup states that seed k is evaluated on its own 200 graphs per cell from a
   stream seeded 10000+k, independent of training and shared by all systems at that seed (PROTOCOL.md updated too).
9. **"The same group".** Fixed: "Bevilacqua et al. later propose ...". Also changed "stronger processors" to "other
   processors" for triplet-GMPNN and pointer graph networks, since we did not compare them.
10. **Rendering.** Fixed. `paper/main.tex` loads TeX Gyre Termes through fontspec, so bold, italic and small caps
    render (Table I's bold-best is visible); the indicator is typeset as a bold 1 with its meaning spelled out; Fig. 1
    draws non-finite values and finite values >= 1e5 at 1e5, with a dotted line and a caption that says so; Fig. 2's
    caption no longer mentions diverged runs (all plotted values are finite). Table IV was shrunk to illegibility by
    `\resizebox`; it now uses short column names at normal size. Figure legends and markers were enlarged.

Other changes from the self-audit:
- "about a thousand Adam steps" -> "1000"; "fail badly" -> "exceed our failure threshold".
- "Differences between aggregators at 64 nodes are within seed noise" -> "none of the registered comparisons at 64
  nodes is significant", which is what the three registered S64 tests show.
- "Failure is a per-seed property, not a stable ordering" -> a description of which seeds fail per configuration and
  "with five seeds we cannot rank the configurations by reliability". A possible cause of the non-finite outputs
  (activations growing with degree) is given with "may"; no run isolates it.
- Aggregation ablation table now carries failure counts, which the sentence about mean aggregation relies on.
- H3: states that only the comparison against max+steps was tested.
