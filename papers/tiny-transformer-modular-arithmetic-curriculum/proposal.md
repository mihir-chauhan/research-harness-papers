# Proposal
Question: does an operand-size curriculum (or its reverse) change the number of optimiser steps a 1-layer transformer needs to reach 95% held-out accuracy on (a+b) mod 23, and how does this interact with weight decay and training fraction?
Method: pool-growing sampler over difficulty key max(a,b); baselines: uniform sampling, anti-curriculum (reverse order). Same model, optimiser, budget, data splits per seed.
Metric: steps_to_95 (first eval, every 25 steps, with held-out acc >=0.95; censored at 4000 if not reached, plus `reached` rate). Secondary: steps_to_train95, grok_gap, final_test_acc.
Hypotheses (tests registered before main runs):
- H1 curriculum >=10% faster than uniform at wd=1, frac=0.5, 5 seeds, rh compare at alpha 0.05. Refuted otherwise.
- H2 anti-curriculum is not faster than uniform (same cell/test). Refuted if significantly faster.
- H3 at wd=0 nothing reaches 95% in 4000 steps (any ordering, grid fractions 0.4, 0.5, 0.7). Refuted if some ordering reaches 95% in a majority of seeds in some wd=0 cell.
- H4 curriculum-vs-uniform sign differs across grid cells (descriptive, 3 seeds). Refuted if same sign in every cell where both reach 95%.
Ablations: curriculum length T_c in {500,2000,4000}; shuffled-order control (same pacing, random difficulty key) isolating the ordering from the pool-growth schedule; wd x frac grid.
Out of scope: other moduli/operations, deeper models, mechanistic analysis, large seeds counts.
