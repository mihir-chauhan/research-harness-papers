# Proposal

**Question.** On a small MLP trained from scratch with symmetric label noise, does SAM beat SGD and SGD with weight decay in clean test accuracy; how sensitive is that to rho; and does a measured sharpness (loss increase under a fixed-norm weight perturbation) track the generalisation gap?

**Hypotheses (tests fixed before the main runs).**
- H1: SAM (rho selected on a noisy validation split) has higher final clean test accuracy than SGD and than SGD+WD on the noisy digits tasks (noise 0.2, 0.4). Test: per task, paired difference over 5 seeds (same data split and init), Welch/paired t-test via `rh compare`, alpha 0.05, plus mean difference. Refuted if the SAM-minus-baseline mean is <= 0 or the difference is not distinguishable from zero on both noisy digits tasks.
- H2: the benefit of SAM depends on rho: accuracy rises then falls with rho, with an interior optimum, and with 40% noise the useful range is wider/larger than with 0%. Test: sweep rho in {0.02,...,1.0} with 5 seeds per task; refuted if test accuracy is flat within seed std or monotone over the grid.
- H3: measured sharpness (random-direction and one-step adversarial loss increase, perturbation norm 0.5 on the training set) is positively rank-correlated with the generalisation gap (noisy-train accuracy minus test accuracy). Test: Spearman correlation over all runs (pooled, and within each task); refuted if pooled and within-task rho_s are not positive, or if it vanishes once the system is controlled for.

**Method.** SAM (Foret et al.): minimise max_{||e||<=rho} L(w+e), approximated by one normalised-gradient ascent step. Baselines (reimplemented): SGD with momentum; SGD with momentum and L2 weight decay. Ablations: random-direction perturbation instead of adversarial; SAM plus weight decay.

**Tasks.** sklearn digits (600 train/300 val/897 test) with symmetric label noise 0, 0.2, 0.4 in train and val labels (test clean); a two-spirals task (400/200/400) at noise 0.2.

**Metrics.** Clean test accuracy (primary), gap_acc, gap_loss, memorisation of flipped labels, sharpness. 5 seeds (0-4) for evaluation, 3 disjoint seeds (100-102) for hyperparameter selection on val accuracy.

**Out of scope.** Large models, CNNs, ASAM and other SAM variants, instance-dependent noise, learning-rate tuning.
