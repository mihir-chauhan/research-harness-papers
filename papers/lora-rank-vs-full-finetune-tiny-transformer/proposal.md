# Proposal
**Question.** After pretraining a 2-layer character-level transformer on sorting 8 digits ascending, how well do LoRA (r=1,2,4,8), full fine-tuning, last-block tuning and head-only tuning adapt it to (a) sorting descending and (b) reversal, and how much sort-ascending skill remains?

**Hypotheses (see research.yaml for tests).**
- H1: LoRA r=4 (all linear layers) is within 2 points of full fine-tuning in adaptation exact-match on both tasks, with <15% of parameters. Refuted if the gap is larger on either task.
- H2: Adaptation accuracy increases with rank 1->8; refuted if rank 1 is within 1 point of rank 8 on both tasks.
- H3: LoRA forgets less than full fine-tuning (drop in pretraining-task exact match). Refuted if not lower on at least one task.
- H4: Last-block tuning is worse than LoRA on sort_desc.

**Method / baselines.** All reimplemented in `method/run.py`: LoRA (Hu et al.), full fine-tuning, last-block tuning, head-only tuning, from-scratch training, no adaptation. Same data, steps (1500), batch (64), optimiser (AdamW, cosine, 50 warm-up) for all; only learning rate differs, tuned per system on a separate validation seed.
**Metrics.** exact-match accuracy on the target task (test set 2000 fresh sequences), trainable parameters, pretraining-task exact match after adaptation, forgetting = before minus after.
**Ablations.** LoRA target modules; learning-rate sweep (also shows the adaptation-forgetting trade-off).
**Out of scope.** Large models, natural language, continual-learning mitigations (replay, EWC), other PEFT variants.
