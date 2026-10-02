# Response to audit
1. (major) Abstract/H4 claim: reworded to "lower mean ECE, NLL, Brier in all 11 conditions", with the uncorrected paired-test counts (NLL 11/11, ECE 9/11, Brier 7/11) and a note that the in-distribution ECE difference is within seed noise. Same qualification added to the H4 paragraph; table captions now say bold marks the lowest mean only (no significance).
2. (minor) Split sizes corrected to 1078/269/450 in setup, results, ablations, limitations, DESIGN.md and the run.py comment.
3. (minor) Hendrycks and Dietterich now cited only as the corruption benchmark; the transfer question cites Ovadia et al. and Tomani et al.
4. (minor) "within 0.003"; Det-vs-MLP and Det-vs-MCD paired p-values added; the mechanism wording now says the MC-averaging evidence is clearer and dropout regularisation "may" contribute.
5. (minor) Compute: about 40 min summed run time, about 32 min wall-clock.
6. (minor) Tables I-II: SDs not added (width); captions state bold = lowest mean only, and significance is given in the text.
7. (minor) Setup states p-values come from results/analysis.py. VERDICT.md regenerated with the current ablation names but the advisory tool still reports "missing", because it matches ablation rows against the method's rows in the main group, whereas our ablation groups compare other systems; explained in RESULTS.md. No numbers changed; no runs repeated.
