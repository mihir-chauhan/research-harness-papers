# Learning-rate schedules on a character-level transformer
Seed: 2-layer d=128 GPT, Tiny Shakespeare chars, 1,500 steps CPU; constant, warmup+cosine, step decay, schedule-free AdamW at 3 peak LRs; validation loss and peak-LR sensitivity; reimplemented baselines, report negative results.

## Question
Under one shared hand-written AdamW, how do four LR treatments differ in final validation loss and in sensitivity (worst-minus-best loss) to the peak LR?
## Hypotheses (tests)
H1 cosine < constant val loss at each system's best of 3 main LRs (Welch on per-seed best). H2 Schedule-Free sens3 < cosine sens3 (Welch on per-seed sens3). H3 at lr 1e-2 cosine without warmup is worse than with warmup (rh compare, abl_warmup).
## Method / baselines
Warmup+Cosine is the reference ("method"); Constant, Step decay, Schedule-free AdamW are reimplemented baselines (method/run.py, DESIGN.md).
## Tasks / metrics
Task = peak LR: 1e-3, 3e-3, 1e-2 (main) plus 3e-4, 3e-2 (also group main). Metrics: val_loss (primary), train_loss, diverged, sens3, sens5, best3.
## Ablations
Warmup length (abl_warmup, abl_warmup_fair), LR sweep. Seeds: 3 (5 not affordable: ~100 s/run on a shared CPU).
## Decisions
Constant and step decay have no warmup in main (as the seed lists them); warmup ablation added because this is a confound. Cosine/SF use 100 warmup steps. Not tuned: all non-LR hyperparameters. Out of scope: other models/budgets, tuning warmup, reference SF code.
