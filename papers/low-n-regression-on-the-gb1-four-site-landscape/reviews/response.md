# Response to audit findings

1. **GP hyperparameters (major).** Rewrote the paragraph in ablations.tex: negligible effect at rand_384; fitting raises the mean at rand_2000 and lowers it at dbl_2000, where the fixed GP is about as good as additive ridge. Removed "not what limits the GP"; marginal-likelihood mis-selection is offered only as a possible mechanism ("may"), with no isolating run claimed. No new p-values quoted (none are in the registry for this comparison).
2. **CNN attribution (minor).** Abstract, conclusion, ablation text and limitations now say "consistent with", state that the gap closes at N<=384 and narrows but does not vanish at N=2000, that the CNN also gains from the log target, and that the CNN log-target run was not done on dbl tasks.
3. **Title (minor).** "Under Matched Budgets" replaced by "on Matched Training Draws".
4. **CNN tuning vs. splits paragraph (minor).** Setup splits paragraph now states the CNN was chosen manually on a separate draw overlapping the test pools; the abstract carries the caveat that the CNN lead is an upper estimate. No re-tuning was done.
5. **Page count (minor).** Now 7 pages (figure 1 made single-column, tables compacted, smaller bibliography font, a few redundant sentences cut).
6. **Padded constants (minor).** Used format specifiers (:1, :2, :3) so the text prints 76.9, 19.7, 8.76, 0.2, 0.003, 0.1.
7. **Stale counts / URL (minor).** PROTOCOL.md and BRIEF.md corrected to 2,168 and 147,193; URL added to PROTOCOL.md; paper points to method/DESIGN.md.
8. **Mislabelled superseded rows / compare CSVs (minor).** Noted the 30 mislabelled ridge rows in experiments/PROTOCOL.md (they stay in runs.jsonl, excluded from aggregation). Regenerated compare_main_spearman.csv and compare_main_top100_recall.csv for all tasks and systems.
9. **Wilcoxon -> paired t (minor).** Setup now says the substitution was made after the main results were inspected; the mean-based refutation rules were fixed beforehand.
10. **Uncited generalisation (minor).** Related-work sentence now restricted to FLIP and ProteinGym, with citations.
