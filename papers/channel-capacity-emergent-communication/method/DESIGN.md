# Design
Objects: 4 attributes x 4 values (256), one-hot input. 10% of combinations (26) held out per seed (split seed 1000+seed; every
attribute value stays present in training). Sender: linear encoder -> GRUCell unrolled L steps, symbol embedding fed back,
hidden 64. Receiver: GRU over embedded messages, linear head with 4 softmax heads; loss = summed attribute cross-entropy.
Systems: gumbel (ST Gumbel-softmax, tau 1), reinforce (REINFORCE, reward = -CE, moving-average baseline 0.99, entropy bonus 0.01,
receiver by backprop), random_code (fixed iid random message per object incl. held-out; receiver learned), oracle_comp
(message position j = value of attribute j). Adam lr 2e-3, batch 128, 6000 steps, grad clip 5, greedy messages at evaluation.
Metrics: heldout_acc (all attributes correct), topsim (Spearman, Hamming distances, all 256 objects), gen_gap, shuffled-message control.
