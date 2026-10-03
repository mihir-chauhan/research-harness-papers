# Design
- `logic.py`: formulas (nested tuples over 5 variables, connectives not/and/or/imp), set-context G3cp sequent rules (all invertible),
  tactic = (side, index of a compound formula). Axiom closure is applied for free. Random provable sequent generators
  (4 kinds, see paper), optimal proof-size DP (`Oracle`, memoised min number of tactic applications) used only for training labels.
- `search.py`: one search engine shared by all systems. State = list of open goals; expansion pops a state and applies every
  candidate tactic to its first goal. `bfs` (FIFO by depth), `bestfirst` (cumulative step cost, ties deeper first), `greedy`.
  Hand heuristic = rank in a fixed ordering (non-branching rules first, then formula size).
- `policy.py`: transformer (3 layers, d=64, 4 heads, ff 256, pre-norm, sinusoidal positions, segment embedding; scores each candidate at its
  root token) and feature MLP (2x128 ReLU on per-candidate features).
- `run.py`: data (cached in /tmp, deterministic from the seed), training (AdamW lr 2e-3, wd 0.01, one-cycle, batch 128, 2000 steps,
  soft cross-entropy to the set of optimal tactics), evaluation on one task. Prints config and final metrics.
