# Size generalisation in neural algorithmic reasoning

## Seed
Size generalisation in neural algorithmic reasoning: train small networks to execute Bellman-Ford shortest paths on random graphs with up to 8 nodes, and test on 16, 32 and 64 nodes. Compare an MLP on the flattened adjacency matrix, a message-passing network with sum aggregation, and one with max aggregation aligned with the algorithm's min/relaxation step, with and without step-wise supervision of intermediate distances.

## Research question
Size generalisation in neural algorithmic reasoning: train small networks to execute Bellman-Ford shortest paths on random graphs with up to 8 nodes, and test on 16, 32 and 64 nodes. Compare an MLP on the flattened adjacency matrix, a message-passing network with sum aggregation, and one with max aggregation aligned with the algorithm's min/relaxation step, with and without step-wise supervision of intermediate distances.

Field: math-reasoning algorithmic-reasoning
Scale: quick study, cpu, about 30 minutes of experiments.

## Decisions (author brief)
- Task: single-source weighted Bellman-Ford distances, undirected connected graphs, weights U(0.2,1); train n in 4..8 (p=0.4); test n in {8,16,32,64} on two families (sparse: constant expected degree; dense: p=0.4).
- Systems: MLP (padded 64x64 flat adjacency, final output only), MPNN-sum, MPNN-max, each +/- step supervision (MPNN only); extra ablation: mean aggregation, test-time step multiplier.
- Hypotheses H1-H4 and tests are in proposal.md. Metrics: MAE (primary mae_sparse_n64), relative error, fraction within 0.05.
- Budget: 1000 Adam steps, batch 32, lr 3e-3, hidden 32 (MLP 128), 5 seeds main, 3 seeds ablations. No hyperparameter tuning beyond defaults (none on test sizes).
- Out of scope: other algorithms, CLRS-30, transformers, larger training sizes, learned termination.
