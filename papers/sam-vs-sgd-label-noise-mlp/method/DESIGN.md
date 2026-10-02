# Design
`method/run.py` trains a 3-layer ReLU MLP (digits: 64-128-128-10; spirals: 2-128-128-2) with SGD+momentum 0.9, cosine lr from 0.1, batch 100, 150 epochs, cross-entropy.
Systems: `sgd`; `sgd_wd` (L2 weight decay in the optimiser); `sam` (global-norm adversarial ascent step e=rho g/||g|| on each minibatch, gradient at w+e applied by the same momentum SGD, no weight decay);
ablations `sam_random` (e = rho u/||u||, u Gaussian) and `sam_wd` (SAM plus weight decay). Metrics are measured at the last epoch (no early stopping).
Sharpness is measured on the full noisy training set with perturbation norm 0.5 (fixed across systems): `sharp_rand` = mean loss increase over 20 random directions, `sharp_adv` = loss increase after one normalised-gradient step.
`gap_acc` = noisy-train accuracy - clean test accuracy; `gap_loss` = test loss - train loss; `memorised` = fraction of flipped training samples predicted with their (wrong) noisy label.
`experiments/drive.py` runs the protocol through `rh run`.
