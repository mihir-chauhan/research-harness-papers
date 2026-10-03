# Design
`method/run.py`: 2-layer, 4-head, d=128 pre-LN GPT (GELU MLP 4x, learned positions, vocab = 65 characters),
block 64, batch 32, 1500 steps, no dropout. Tiny Shakespeare (1,115,394 chars), first 90% train, last 10% validation.
Validation: 256 fixed random windows of 64 chars from the validation part (same for all runs); metric = mean token cross-entropy (nats) after the last step.
Optimiser (all systems, identical): AdamW written by hand (beta=(0.9,0.95), eps 1e-8, decoupled wd 0.1 on matrices only), global grad-norm clip 1.0.
Schedules (peak lr = eta): constant (no warmup); cosine (100 linear warmup steps, cosine to 0.1*eta); step (x0.3 at steps 500 and 1000, no warmup);
schedule-free AdamW (reimplemented from Defazio et al. 2024, Algorithm with r=0, weight power 2, beta1=0.9, 100 warmup steps; evaluation at the averaged iterate x).
Flags `--warmup N` override warmup length (ablation). Seeds control init and batch order.
