# Landscape
- Bellemare et al. 2016 (1606.01868): pseudo-counts from density models -> count bonuses beyond tabular.
- Tang et al. 2016 (1611.04717): hashed state counts as bonus. Ostrovski et al. 2017 (1703.01310): neural density model pseudo-counts.
- Pathak et al. 2017 (1705.05363): forward-model curiosity in learned features. Burda et al. 2018 (1808.04355): large-scale curiosity study; stochastic observations attract it.
- Burda et al. 2018 (1810.12894): RND, prediction error vs a fixed random target.
- Osband et al. 2016 (1602.04621): epsilon-greedy dithering needs exponentially more data on chain-like problems.
- Strehl & Littman 2008 (10.1016/j.jcss.2007.08.009): MBIE-EB, bonus proportional to 1/sqrt(n(s,a)) in a model-based learner.
- Martin et al. 2017 (1706.08090): counts in the feature space used for value approximation.
- Rashid et al. 2020 (2002.12174): optimistic initialisation underlies provably efficient tabular model-free methods; count-based optimism for pessimistically initialised deep Q-networks. Relevant to our penalty-only control.
- Taiga et al. 2021 (2109.11052): bonus methods with one agent and protocol on Atari; higher scores on Montezuma's Revenge, no meaningful gain over epsilon-greedy otherwise.
- Mavor-Parker et al. 2021 (2102.04399), Jarrett et al. 2022 (2211.10515): making forward-model curiosity robust to noisy TVs (aleatoric uncertainty, hindsight representations).
Closest work: the RND and curiosity papers themselves, which evaluate on large Atari benchmarks. Gap: a tabular, learner-fixed comparison with growing size and a parametrised noisy-TV cell. We did not run an exhaustive search (the search APIs were rate-limited; candidates.jsonl contains unrelated hits from the first query).
