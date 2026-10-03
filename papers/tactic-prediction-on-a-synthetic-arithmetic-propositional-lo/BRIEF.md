# Tactic prediction in a propositional sequent calculus (brief)
**Question.** Within a budget of 100 expansions, does best-first search guided by a learned tactic policy (small transformer / feature MLP, trained by imitating optimal tactics on 3-10 connective sequents) solve more provable sequents than BFS and a tuned hand-written heuristic, on sequents with 11-20, 21-40 and 41-70 connectives?
**Hypotheses.** H1 policy > BFS in every test bin; H2 policy > heuristic at 41-70; H3 policy-minus-heuristic gap shrinks monotonically 11-20 -> 41-70; H4 best-first with the policy > greedy decoding at 41-70. Tests: paired t over 5 seeds.
**Method.** G3cp invertible sequent calculus, tactic = compound formula to decompose, shared search engine (state = open goals, expansion = pop, children = all tactics on the first goal), policy cost -log p.
**Baselines.** BFS, hand heuristic (3 variants tuned on a 21-35 bin), feature-MLP policy (all reimplemented).
**Tasks/metrics.** val_3_10, test_11_20, test_21_40, test_41_70; solved rate, mean expansions. 5 seeds, 150 problems per task.
**Ablations.** greedy / rank cost, learned positions, training-set size, expansion budget, diagnostic of branching deferral.
**Out of scope.** Arithmetic, first-order logic, non-invertible calculi, large models, real libraries.
**Decision.** The seed mentions "arithmetic": not implemented (propositional only); generators mix four sequent families so that proofs are non-trivial (plain rejection sampling gave tiny proofs).
