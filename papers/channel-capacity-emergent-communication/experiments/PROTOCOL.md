# Protocol
Groups: main (4 systems x tasks V4_L4, V8_L4, V16_L8 x seeds 0,1,2), sweep_vocab (gumbel, L=5, V in 2,3,4,8,16),
sweep_length (gumbel, V=6, L in 2,3,4,6,8), seeds 0-2. All runs: 6000 steps, hidden 64, batch 128, lr 2e-3, tau 1, ent 0.01.
No hyperparameter tuning was done on held-out data (only a 3000/10000-step timing probe at seed 0 on V4_L4/V8_L4/V16_L6, used to
fix the step budget). Hardware: shared CPU, 2 threads, ~25 s per run. Test split: 10% random held-out combinations.
