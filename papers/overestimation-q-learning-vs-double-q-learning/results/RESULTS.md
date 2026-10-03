# Results (5 seeds x 1,000 replicas; see paper/ for numbers, all from results/runs.jsonl)

- H1 (trap Q-bias, Double lower than Q-learning): supported in direction on the registered test (qbias_final, main group, rh compare); both values positive because of zero initialisation. Warm-start ablation (abl_warm) gives the clean contrast.
- H2 (trap suboptimal actions): supported (subopt_all, main, maxbias).
- H3 (random20): bias part refuted (Q-learning bias_final negative, Double more negative); action part supported (Double has higher subopt_all than Q-learning in main; reverses with warm start).
- H4: number-of-actions part supported at grid values (sweep_actions); noise part refuted (Q-learning final bias not increasing in sigma; sweep_sigma). Action-quality ranking flips only at sigma=4.
- Other: Weighted Double ~ Double; Maxmin controls bias but costs action quality for large n; simultaneous double update == Q-learning.
