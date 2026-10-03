# Proposal

## Question
How large is the estimated-minus-true value bias of tabular Q-learning versus Double Q-learning (and Weighted Double and Maxmin variants) on (a) the Sutton-Barto maximisation-bias MDP and (b) random 20-state MDPs, and what does it cost in suboptimal actions?

## Hypotheses (tests fixed before the main runs; see research.yaml)
- H1 (maxbias) Q-learning overestimates Q(A,left); Double does not. Refuted if Double's qbias_final is not lower than Q-learning's (Welch test, rh compare, 5 seeds).
- H2 (maxbias) Double takes fewer suboptimal start actions (subopt_all). Refuted if not lower (rh compare).
- H3 (random20) Q-learning's start-state bias is positive and Double removes it, and Double has no lower suboptimal-action rate. Refuted if Q-learning's bias_final is not positive. A seed-0 pilot while fixing the budget suggested the bias is negative (unconverged values), so refutation is expected; the pilot was used only to choose gamma, episode count and random start states, not any method parameter.
- H4 (sweeps) The Q-learning bias grows with noise sigma and with number of actions, Double stays below Q-learning at each swept value.

## Method / baselines
Tabular Q-learning, Double Q-learning, Weighted Double Q-learning, Maxmin Q-learning (N=2), all reimplemented, same alpha=0.1, epsilon=0.1, budget and seeds. Ablations: both-tables-updated Double Q, step-size sweep (Q-learning at alpha/2), warm start at Q*, epsilon sweep (including 1.0, non-adaptive data), sigma sweep, action-count sweep.

## Metrics
Estimated-minus-true value of the start state (max over actions of the acting values minus V*), estimated-minus-true Q (Q(A,left)-mu in maxbias; mean over all (s,a) in random20), fraction of suboptimal actions per episode, greedy-policy error at the end.

## Novelty
Incremental: no new algorithm; the contribution is a controlled comparison and the separation of effects. Searches: "double Q-learning maximization bias", "overestimation bias Q-learning estimators weighted maximum".
