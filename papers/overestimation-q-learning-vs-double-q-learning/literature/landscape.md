# Landscape

- Maximisation bias of the max operator is classical (Smith & Winkler, optimizer's curse, `smith2006optimizer`); van Hasselt's Double Q-learning (2010, CWI report, no DOI/arXiv so not in refs.bib) introduced the decoupled estimator and the Sutton-Barto trap MDP (Sutton & Barto, Example 6.7).
- Deep variants: Double DQN (`hasselt2015deep`), TD3 clipped double Q (`fujimoto2018addressing`), Rainbow (`hessel2017rainbow`).
- Other tabular/estimator fixes: Weighted Double Q-learning (`zhang2017weighted`), Maxmin Q-learning (`lan2020maxmin`), weighted Q-learning (`cini2020deep`), variance/overestimation reduction (`sabry2019reduction`), automatic bias control (`kuznetsov2021automating`).
- Analyses of when the bias matters: `wagenbach2022factors` (factors of influence), `ren2021estimation` (estimation bias of double Q-learning, which can underestimate).
- Gap: controlled tabular comparison with exact V*, matched step size and exploration, and ablations separating decoupling from slower per-table learning and adaptive data collection. Closest work is the above analyses; this study is a small reproduction-plus-ablation, not a new algorithm.
