# Response to audit

1. **Major, H2 paragraph (results.tex).** Rewrote: best grid value moves from 0.1-0.2 (no noise) to 0.5 (noise); under noise only rho=0.5 recovers the gain, so the window is narrow; the optimum is only bracketed in (0.2, 1.0). Removed "wider" and "between 0.5 and 1.0".
2. **Minor, sharpness ranking.** Abstract now says adversarial sharpness; Table II has a sharp_rand column; text states that random-direction sharpness ranks SAM flattest. Pooled correlation range is now 0.07-0.24 (abstract, conclusion, H3 paragraph).
3. **Minor, "same tuning effort".** Replaced in the introduction with the actual protocol (rho from 6 values, lambda from 4, shared untuned learning rate).
4. **Minor, "one seed SD".** Corrected to about two (0.015 vs SD 0.008); noted accuracy is flat for rho 0.02-0.5 without noise.
5. **Minor, correlation range.** See 2.
6. **Minor, H1 at 40%.** Added per-seed differences (one negative at 40%, one at 20%) and the Holm-adjusted paired p (0.10, recomputed over the 8 paired tests); verdict reads "supported only without multiple-comparison correction". Abstract and conclusion updated.
7. **Minor, random-direction ablation.** Qualified as a matched-norm, weak control; added the bimodal per-seed split of SAM+WD at 20% noise (four near 0.09, one 0.741).
8. **Minor, timing and uncited sentence.** Run time now 1.3-6.7 s (mean 2.7 s); wall-clock 46 min (17 min summed run time). Removed the uncited "convolutional networks on GPUs" sentence.
9. **Minor, layout.** Eq. (2) split into an align block; Table III resized to the column; Fig. 2 legend moved outside the axes; bold/underline removed from the main and ablation tables (and caption).

# Response to the second audit (fix round)

No experiment was re-run and no run was added: all findings concerned text, table formatting or disclosure. The registry still holds 381 runs.

1. **Major, results.tex "Where SAM fails" (0.888 attributed to rho=0.2).** Corrected to "0.888 at rho=0.1, 0.767 at rho=0.2 and 0.518, i.e. chance, at rho=0.5", copied from Table IV (`rho_sweep.md`). "Clearly worse" weakened to "worse", since rho=0.1 is only about one seed SD below SGD.
2. **Minor, tuning seeds re-split the same digits pool.** Setup now states that on digits the tuning train/validation images overlap the evaluation seeds' test images (spirals data are generated fresh per seed) and that this applies equally to SAM and SGD+WD; limitations repeat it. "Disjoint seeds" replaced by "separate tuning seeds" in the abstract and introduction. Also recorded in `experiments/PROTOCOL.md` and `BRIEF.md`.
3. **Minor, epoch-matched vs compute-matched.** Added to limitations (no SGD / SGD+WD run with twice the steps was made), to the training paragraph of the setup, to the abstract and to the conclusion.
4. **Minor, Fig. 1 caption.** Now "task means 0.103-0.136".
5. **Minor, RESULTS.md.** Rewritten to match the paper: H1 at 40% noise "supported only without multiple-comparison correction (Holm-adjusted paired p 0.101)", pooled Spearman 0.07-0.24, H2 and ablation wording aligned.
6. **Minor, sharp_rand printed as 0.00.** Tables II and VII are now typeset by `experiments/analyse.py` from the aggregates that `rh table` writes (`main_agg.csv`, `abl_sam_agg.csv`; same means and stds), with sharp_rand in units of 1e-3 and sharp_adv to 4 decimals, so no sharpness cell prints as zero. Table VII now has the same columns as Table II (3 decimals for accuracies), which also puts every ablation number quoted in the text (0.800, 0.623, 0.998, 0.972, 0.223 +/- 0.290, 0.901) in the table. Prose numbers for sharpness and weight norm were re-copied from the new tables.
7. **Minor, SAM+WD "best system without noise".** Now "comparable to SAM (0.972 +/- 0.006 vs 0.970 +/- 0.006)".

Changes from my own re-audit (not in the findings):
- Table III now carries the Holm-adjusted paired p for all 8 comparisons (the 0.101 quoted in H1 previously had no table cell); the unused Cohen's d column was dropped to keep the table to four numeric columns. Setup and limitations no longer say "no correction is applied"; they say the registered tests are uncorrected and the Holm values are given in addition.
- H2: "gain 0.015" was a rounding error (0.974 - 0.959 = 0.014); the sentence now gives the SGD mean and SD and says "under two seed standard deviations". "Flat within about 0.01" replaced by the actual range 0.960-0.974. The noisy-digits ranges are now given from rho=0.02 (0.807 to 0.938, 0.629 to 0.901) instead of an ambiguous 0.2-to-0.5 pair. "Best value 0.1-0.2 without noise" corrected to 0.2 (0.1 and 0.5 within 0.004). "A rho chosen at the grid edge" was wrong (0.5 is not the grid edge) and now reads "one grid step below the collapse". The verdict states explicitly that the "wider range under noise" part of H2 is not supported and that the registered refutation condition (monotone curve) is met on spirals.
- H3: verdict now refers to the registered criterion (positive pooled and within every task) and reads "not supported"; "lowers the per-task values" changed to "leaves", since the spirals correlation becomes less negative; the collapse threshold used by the exploratory rows is stated.
- Ablations: "equal to SGD" changed to "within 0.002 of SGD"; the random-vs-gradient loss change is quoted with numbers; the extreme weight norm of the collapsed SAM+WD runs (0.32 +/- 0.07 at 40% noise) is reported and explained; "comparable to the sweep resolution" (no supporting row) deleted; "untuned SAM" changed to "a badly chosen rho".
- Abstract and conclusion: the sharpness-ranking and collapse statements are restricted to noisy digits, where the table rows support them.
- `BRIEF.md` was still the scaffold seed; it now holds the question, hypotheses, method, baselines, tasks, metrics, ablations and out-of-scope list, taken from `proposal.md` (registered before the main runs).
- Tables II and VII are scaled to the text width (they overflowed by 10 pt and 56 pt after the new columns).

Checks after the changes: `pdfinfo` 6 pages, `rh lit verify` CITATIONS VERIFIED (10 references), `rh check` READY (remaining warning: verdict tier 1 < target 2, because SAM does not win on spirals, which the paper reports).
