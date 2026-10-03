# Proposal
**Question.** In a tiny propositional sequent calculus (G3cp with set contexts), does a learned tactic policy beat BFS and a tuned hand-written heuristic for best-first search with a 100-expansion budget, on formulas larger than the training formulas?

**Setup.** Tactic = (side, compound formula) to decompose; all rules invertible so every tactic keeps a valid sequent valid and the choice only affects proof size and search cost. 20k provable sequents (3-10 connectives) with labels from optimal proof sizes; test on 11-20, 21-40, 41-70 connectives (150 problems per bin per seed). Systems: BFS, hand heuristic (3 variants tuned on a separate tuning bin 21-35), feature MLP policy, transformer policy (method). Metrics: solved rate within 100 expansions (higher better), mean expansions with failures counted as 100 (lower better). 5 seeds (seed changes train data, test problems and initialisation).

**Hypotheses** (tests as in research.yaml): H1 policy > BFS on all bins; H2 policy > heuristic at 41-70; H3 the policy-minus-heuristic gap worsens with size; H4 search beats greedy policy decoding at 41-70.
**Refutation.** H1 refuted if policy <= BFS in any bin; H2 refuted if heuristic >= policy; H3 refuted if gap non-monotone; H4 refuted if greedy >= best-first.
**Prior.** The hand heuristic encodes the known optimal strategy for invertible calculi (defer branching), so I expect H2 to fail; the interesting measurement is how far imitation of optimal proofs gets and where it breaks.
