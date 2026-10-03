# Protocol
- Tasks: val_3_10 (held-out, training range), test_11_20, test_21_40, test_41_70 (connective counts), tune_21_35 (heuristic tuning only). 150 provable sequents per task, generated from seed-specific RNG; seed also changes the 20k training sequents (3-10 connectives) and initialisation.
- Budget: 100 expansions (pops), identical for all systems; failures count as 100 in mean_exp.
- Systems: BFS, Hand heuristic (variant chosen on tune_21_35 with seeds 0-4), Feature-MLP policy, Transformer policy; same search engine.
- Training: 2000 steps, batch 128, AdamW 2e-3, one-cycle; no tuning of policy hyperparameters beyond what is stated (none on test bins).
- Ablations: greedy decoding, rank cost, learned positions (3 seeds? no: 5), training size sweep, budget sweep.
- Hardware: shared CPU, 2 threads. Metrics are deterministic functions of the seed.
