# Results (5 seeds, 150 problems per task/seed; see paper for numbers)
- H1 supported: transformer > BFS in all three test bins (rh compare, paired p < 1e-4).
- H2 refuted: tuned heuristic > transformer at 41-70 (paired p ~ 4e-4).
- H3 refuted: gap tf-heuristic is non-monotone (smallest at 11-20, largest at 21-40, narrower at 41-70; ceiling effect).
- H4 refuted: greedy transformer beats best-first with -log p cost at 41-70 (analysis group).
- Exploratory (post hoc): same transformer with rank cost = heuristic level; MLP with rank cost > heuristic at 21-40 and 41-70; fewer training sequents extrapolate better; diag shows MLP defer rate falls with size.
