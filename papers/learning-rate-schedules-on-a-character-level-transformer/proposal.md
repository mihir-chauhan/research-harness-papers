# Proposal
Question: on a 2-layer d=128 char-GPT trained 1,500 steps on Tiny Shakespeare, how do constant, warmup+cosine, step decay and Schedule-Free AdamW differ in final validation loss and in sensitivity to the peak LR?
Hypotheses (tests in research.yaml): H1 cosine beats constant at each system's best LR; H2 Schedule-Free is less LR-sensitive than cosine; H3 warmup matters at the largest LR.
Method: all systems share one hand-written AdamW; only the LR schedule (or the schedule-free iterate averaging) differs. Peak LR in {1e-3,3e-3,1e-2} (+3e-4, 3e-2 sweep), 3 seeds (5 judged too expensive on the shared CPU: ~100 s/run).
Refutation: H1 refuted if difference not significant/ wrong sign; H2 if SF sensitivity >= cosine; H3 if no-warmup is not worse.
Sensitivity = max-min over LRs of the seed-mean... computed per seed as max_lr val_loss - min_lr val_loss.
