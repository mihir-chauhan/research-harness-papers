# Results (20 seeds main, 10 seeds sweeps)
- H1 (static: planning raises early reward): Dyna-Q n=10 early_reward 7.9 vs Q-learning 1.6 on static, but std 10.6 (seed-level noise large); cum_reward 200.2 vs 86.2 (paired p=1.6e-06). SUPPORTED for cum_reward; early_reward difference is within the seed spread, paired p=0.015 (compare_main_early_reward.csv) -> weakly supported.
- H2 (blocking: post-change reward falls with n for Dyna-Q; Dyna-Q+ better): Dyna-Q post_reward is non-monotone in n (0.6, 23.4, 17.8, 29.6, 19.9 for n=1..100); low n is slow in general, so no staleness-driven decline is visible. Dyna-Q+ beats Dyna-Q (post 51.9 vs 28.2, paired p=0.025, uncorrected) and improves with n. First half REFUTED / second half SUPPORTED.
- H3 (shortcut): Dyna-Q+ 229.7 vs Dyna-Q 165.8 post_reward, paired p=1.9e-18. SUPPORTED. But kappa>=0.01 collapses Dyna-Q+.
- H4 (stochastic): cum_reward of Dyna-Q falls from 92.4 (n=1) to 39.6 (n=100), vs Q-learning n=0 55.4 on seeds 0-9: gaps at n>=50 within noise (paired p=0.44, 0.14; tests_stochastic_n.csv); n=1 vs n=100 paired p=0.0016. Verdict: benefit of planning shrinks (SUPPORTED in that sense); 'worse than Q-learning' NOT shown.
- H5 (PS): static cum 220.6 vs 200.2 (p=0.22), blocking post 29.8 vs 28.2 (p=0.88): indistinguishable on cum/post reward; early_reward PS 18.6 vs 7.9 (paired p=0.014). SUPPORTED only for cum/post reward (low power).
Dyna-Q+ components: the bonus alone (no untried-init) is harmful; untried-init alone helps on blocking/shortcut slightly; bonus helps on top.

Ablation tests: compare_abl_dynaq_plus_post_reward.csv (ref Dyna-Q+), ..._refDynaQ.csv (ref Dyna-Q). Bonus effect on blocking is a trend (p=0.069); w/o untried vs Dyna-Q significant only on static and stochastic.
