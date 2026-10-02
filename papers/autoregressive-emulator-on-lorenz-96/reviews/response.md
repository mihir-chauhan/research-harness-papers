# Response to audit
1. (major) 5.2% headline: fixed. Abstract and results now say K=1 is 5.2% higher than K=8 (the rh rel_delta quantity), no longer "relative reduction". RESULTS.md states both 5.2% and the 4.98% reduction relative to K=1 (the latter appears only in RESULTS.md, not in the paper). Same rewording for K=4.
2. Conclusion: now "beyond about 4.5 time units the CNN RMSE exceeds that of climatology".
3. H3: Welch p for K=8 vs K=1 var_ratio is now reported next to the paired p; verdict unchanged (registered paired test, effect below one percent).
4. Method: truth bound changed to "about 15"; the divergence threshold of 50 is unchanged.
5. Tuning: setup now states that lr 0.003 is the upper edge of the two-point grid and that K=2,8 were untuned. A larger lr was not tried (no new runs).
6. Introduction: Chattopadhyay/Gagne described as multi-scale studies; "reproduction" changed to "study". Lorenz (1996) has no arXiv id or DOI available to `rh lit cite`, so it is not added (no hand-typed BibTeX).
7. Eq. (3) now splits over lines and Eq. (5) is narrower; checked on the rendered page 2.
8. DESIGN.md window count corrected to 896; PROTOCOL.md and proposal.md note that sweep_ntrain was added post-hoc.
9. VERDICT.md annotated: the automatic tier is more favourable than the paper's reading (K=4 gain is weak, H2/H3 not supported).
10. Citation abstract re-check: not redone (API limit); citations.json timestamp change is harmless.
