# Results (see paper/sections/results.tex and ablations.tex for the numbers; tables in results/tables/)
- H1 supported: perm_dil ER M=100 0.847 vs EWC 0.695 (paired p 1.2e-4), main.md.
- H2 partly supported / seed-dependent (EWC gain 0.032 on main seeds, paired p=0.22, CI straddles 0.05; 0.340 vs 0.196 on sweep seeds 10-14 with same config; ER half holds on both): split_cil EWC 0.246 vs fine-tuning 0.214 (gain 0.032 <= 0.05); ER M=100 0.896 (gain 0.682). EWC last-task accuracy 0.118 +- 0.263 (failure case).
- H3 supported: split_til fine-tuning 0.946 vs joint 0.990 (gap 0.044 < 0.10); continual methods not separable with 5 seeds.
- H4 supported with caveats: replay monotone in M for perm_dil and split_cil, not strictly for split_til; EWC interior optimum (lambda=10 perm_dil, 1000 split_cil, split_til); split_cil peak weak (0.340).
- H5 supported in means; split_til joint vs ER M=100 not significant (p=0.26).
Advisory verdict tier 0 because the method does not beat joint training (an upper bound by construction); this is a comparative study, not a new-method claim.
