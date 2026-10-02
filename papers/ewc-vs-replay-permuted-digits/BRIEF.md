# Brief: EWC vs replay on permuted / split sklearn digits

Question: on 5-task sequences from scikit-learn digits (8x8, 1797 images), how do fine-tuning, EWC, a small replay buffer and joint training compare in final average accuracy and forgetting, and how does the buffer size M compare with EWC's lambda as the single knob?

Scenarios: perm_dil (5 permuted-pixel tasks, 10-way single head), split_cil (5 two-class tasks, random class order per seed, single 10-way head, no task id), split_til (same split, task id at test time via logits masked to the task's classes).
Systems: Fine-tuning, EWC (reimplemented), Experience Replay (reimplemented; method of study), Joint (retrain on union, upper bound). Same MLP 64-100-100-10, SGD lr 0.1 (selected on val), 30 epochs/task, batch 32, grad clip 5.
Metrics: final average accuracy over all 5 tasks, forgetting, backward transfer, last-task accuracy; per-stage curves.
Hypotheses H1-H5: see proposal.md (tests registered there). Ablations: sweeps of lambda and M (sensitivity).
Out of scope: other CL methods, larger data, pretrained models, task-free settings.
Decisions: see `rh decide` log (seeds split: main 0-4, sweeps 10-14, lr tuning 100-101; lambda* chosen from validation accuracy on sweep seeds).
