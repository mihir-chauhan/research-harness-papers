# Proposal
**Question.** Train on random weighted graphs with 4-8 nodes to output single-source Bellman-Ford distances; test at 8, 16, 32, 64 nodes. Which of (aggregation: sum/max; supervision: final only / every Bellman-Ford round) governs extrapolation, and how does a flattened-adjacency MLP compare?

**Systems** (all reimplemented): MLP on zero-padded 64x64 weighted adjacency; MPNN-sum, MPNN-max (Velickovic et al. 2019 style), each with and without step-wise supervision (the MLP has no steps: final only).
**Data.** Connected undirected graphs (random spanning tree + ER edges), weights U(0.2,1), random source. Train: n uniform in 4..8, p=0.4. Test families: `sparse` (p=3/(n-1), constant expected degree) and `dense` (p=0.4, degree grows with n). Metric: MAE of the final distance per node (primary: mae_sparse_n64), also relative error and fraction within 0.05.
**Hypotheses.** H1 max-hint beats sum-hint at n=64 sparse; H2 steps help max; H3 MLP worse than every MPNN at n>=16; H4 in dense graphs sum degrades more than max (ratio of n=64 to n=8 MAE).
**Refutation.** Each is refuted if the sign is wrong or the difference is within seed noise under `rh compare` (5 seeds). Verdicts use `rh compare` as registered here.
**Ablations.** (a) mean aggregation with/without steps; (b) test-time steps multiplier {0.5,1,2}x(n-1) for max-hint and sum-hint.
