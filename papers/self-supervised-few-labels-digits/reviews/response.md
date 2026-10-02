# Response to audit
Added `method/stats_extra.py` (paired t-tests read from `results/runs.jsonl`) -> `results/tables/stats_extra.tex`, shown as Table "Additional paired comparisons" in the results section. `rh compare` cannot compare ablation groups against the main rows, hence the script.

1. (major) H2 budgets swapped: fixed. Text now says rotation is below PCA at 10 and 50 labels (p=0.05, 0.10, unresolved) and about equal at 200.
2. (major) Abstract rotation claim: rewritten. Rotation is below random at 50/200 labels, not better than PCA at any budget; the causal "because" is now an explicitly untested hypothesis. Random-vs-rotation at 10 labels given as p=0.09 in results.
3. (major) Abstract "defaults not optimal": replaced with sensitivity at ~1 std, tau=1.0 nominally higher, saturation by 30 epochs; ablations text notes the tau comparison is post hoc.
4. (minor) H4: numbers corrected (0.028, 0.037), paired p reported (geom 0.09, photo 0.003); H4 now "partly supported".
5. (minor) Supervised+aug: now stated as indistinguishable from scratch (p=0.12 at n10) and below SimCLR at n10 (p=0.02).
6. (minor) Random-vs-pixels claim restricted (PCA at 50/200, pixels at 200 only).
7. (minor) "strong" PCA dropped; limitations note that pixels + LR is the stronger classical baseline and PCA is untuned. No PCA-dimension sweep was run.
8. (minor) BYOL wording, Kolesnikov paraphrase, Su et al. (rotation and jigsaw), dataset size (about 1800), uncited claims softened. Not changed: citing arXiv preprints rather than published venues (the harness generates the BibTeX from arXiv ids; we did not hand-edit it).
9. (minor) Compute paragraph now gives the 75/90 duplicates, the failed sanity run, ~52 min wall-clock vs 45 min plan, the 792 s rotation run, and drop-last batching.
10. (minor) Added a note that p-values are uncorrected and that budgets share the encoder and test split per seed.
