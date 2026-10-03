# Overestimation: Q-learning vs double Q-learning (brief)

Question: size of estimated-minus-true start-state value bias and fraction of suboptimal actions for tabular Q-learning vs Double Q-learning (plus Weighted Double and Maxmin), on the Sutton-Barto maximisation-bias MDP and on 20-state random MDPs, 1,000 runs per seed, 5 seeds.
Hypotheses H1-H4: see research.yaml and proposal.md. Baselines: Q-learning, Weighted Double Q-learning, Maxmin Q-learning (reimplemented). Ablations: both-table updates, step-size, warm start, epsilon, sigma, action-count sweeps.
Decisions: the true-value reference is V* (optimal), so the estimate is max_a Q; random20 uses gamma 0.7, 25-step episodes from random start states and 1,000 episodes because gamma 0.9 with 300 episodes was far from converged in a seed-0 pilot (bias dominated by zero initialisation); the same pilot suggested negative bias in random20 (H3 stated knowingly). Out of scope: function approximation, deep RL, theory.
