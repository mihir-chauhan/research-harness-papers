# Results (5 seeds x 20 agents, exact evaluation; tables in results/tables/)
- H1 (SP gap): supported. SP self-play 0.991/1.000/0.978 (lever/safe/signal) vs cross-play 0.084/0.268/0.259 (main.md).
- H2 (OP > SP on every task): mixed. Safe (0.500 vs 0.268, p=5e-4) and signal (0.400 vs 0.259) clear; lever 0.153 vs 0.084, Welch p=0.053 -> inconclusive. OP wins on safe/signal by choosing the safe action / a non-communicating pooling policy.
- H3 (population between SP and OP, grows with K): supported on safe and signal (0.487, 0.337; K sweep rises), no effect on lever (0.088 vs 0.084; flat in K).
- H4 (right symmetry group needed): weak. Lever OP-full 0.108 vs OP 0.153 (p=0.16); no difference on safe.
- Sensitivity: OP lever cross-play falls with init std (0.179 at 0.5 -> 0.104 at 4) and does not improve with 10x more updates (0.153 -> 0.151).
- Registry: duplicated main entries from overlapping drivers were removed (values identical); verdict tier 1 (advisory).
