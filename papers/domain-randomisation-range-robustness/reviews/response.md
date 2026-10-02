# Response to audit

1. **Major, Xie et al. mis-cited.** Fixed. Introduction and related work now say Xie et al. report direct transfer without dynamics randomisation; the "standard ingredient" claim is removed. Automatic Domain Randomization (OpenAI et al. 2019, `openai2019solving`, added with `rh lit cite`) is cited as the closest prior work to the success-gated widening, and the paper says we did not reimplement ADR.
2. **H1 untested.** Ran `rh compare` with wide DR as reference: ret_robust 470.4 vs 386.6, paired p=0.0007. Added to results.tex and RESULTS.md.
3. **Gate ablation.** Added gate-0.8 rows to the ablation group (5 registered runs; they reproduce the main curriculum runs exactly) and regenerated Table III. Text now says the variants are indistinguishable at 5 seeds (paired p vs gate 0.8: 0.19, 0.22, 0.85); the speculative explanation is dropped.
4. **Fig. 3 caption.** Now "mean and spread over 5 seeds".
5. **CEM std floor.** Added to method.tex.
6. **Uncited folklore / ADR.** The conservativeness claim is now worded as "often argued" with a note that no source measuring it was found; ADR cited (see 1).
7. **Smoke runs.** Not recorded in the registry; setup.tex now says so plainly, and limitations notes the design was adapted after seeing a reported seed.
8. **Ranking overstatement.** Reworded: all tie at w=0.25; ordering no DR < narrow < wide ≈ curriculum where systems separate (w>=0.75).
9. **Table legibility.** Main table reduced to 5 columns (dropped ret_w50) and the ablation table to 4 (dropped ret_w100 and train_width_end, removing the meaningless arrow).
10. **Logs/VERDICT/provenance.** run.py now prints the final metrics (used by the new gate-0.8 runs; older runs were not re-executed, since their outputs are unchanged by this print). VERDICT.md was regenerated but still lists ablation deltas as missing, because the ablation group's reference name for the method differs from the main-group method name; the comparison is given in the compare CSV and text instead. Provenance commit hashes for the earlier runs remain the scaffold commit and cannot be repaired retroactively; the code is now committed.
