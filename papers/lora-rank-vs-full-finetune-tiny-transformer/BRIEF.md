# Low-rank adaptation at tiny scale (brief)
**Question.** Tiny transformer pretrained on sort-ascending of 8 digits; adapt to sort-descending and reversal with full FT, LoRA r in {1,2,4,8}, last-block-only, head-only. Measure adaptation exact match, trainable parameters, forgetting of sort-ascending.
**Hypotheses.** H1-H4 in proposal.md / research.yaml.
**Method.** 2-layer, d=64, 4-head decoder-only transformer, vocab 14 (digits, separator, 3 task tokens). Task token first so forgetting is meaningful (the old task stays queryable). LoRA on q,k,v,o,ff1,ff2, alpha=2r.
**Baselines.** Full FT, last block + final LN + head, head only, scratch, no adaptation (all reimplemented).
**Metrics.** adapt_acc (exact match), trainable_params, pretask_acc, forgetting.
**Ablations.** LoRA target modules (q,v only); LR sweep; adaptation-steps curve.
**Decisions.** Pretraining task = sort ascending; two target tasks; 5 seeds (0-4), each seed has its own pretrained model; LR tuned on val split with separate seed 100; adapt set 2000 fixed examples.
**Out of scope.** Large scale, replay/EWC, other PEFT.
