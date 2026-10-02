# Sharpness-aware minimisation versus SGD on a small MLP with label noise

## Seed
Sharpness-aware minimisation versus SGD on a small MLP with label noise (scikit-learn digits or a synthetic two-spirals / Gaussian-mixture task). Does SAM improve test accuracy under label noise at this scale, how sensitive is it to the neighbourhood size rho, and does the measured sharpness (loss increase under weight perturbation) track the generalisation gap? Compare SGD, SGD with weight decay, and SAM.

Field: ml-theory-optimization
Scale: quick study, cpu, about 30 minutes of experiments.

## Research question
On a 3-layer ReLU MLP (width 128) trained from scratch with symmetric label noise, does SAM give higher clean test accuracy than SGD and than SGD with a validation-selected weight decay; how does that depend on rho; and is a fixed-norm loss-increase sharpness rank-correlated with the generalisation gap?

## Hypotheses (as registered in proposal.md before the main runs)
- H1: SAM (rho selected on a noisy validation split) has higher final clean test accuracy than SGD and SGD+WD on digits with 20% and 40% noise. Test: paired / Welch t-test over 5 seeds (`rh compare`), alpha 0.05. Refuted if the mean difference is <= 0 or not distinguishable from zero on both noisy digits tasks.
- H2: accuracy rises then falls with rho (interior optimum), and the useful range is wider/larger at 40% noise than at 0%. Test: 6-value rho sweep, 5 seeds per task. Refuted if flat within seed std or monotone.
- H3: fixed-norm sharpness (random-direction and one-step adversarial, norm 0.5, noisy training set) is positively rank-correlated with the gap. Test: Spearman over all evaluation runs, pooled and per task. Refuted if pooled and within-task correlations are not positive.

## Method and baselines (all reimplemented in method/run.py)
SAM (Foret et al.): one normalised-gradient ascent step of radius rho, gradient at the perturbed weights, momentum SGD update. Baselines: SGD with momentum; SGD with momentum and L2 weight decay. Shared, untuned: lr 0.1 cosine, momentum 0.9, batch 100, 150 epochs (epoch-matched; SAM uses two gradient evaluations per step).

## Tasks, data, seeds
scikit-learn digits (600 train / 300 val / 897 test, split by seed) with symmetric noise 0, 0.2, 0.4 in train and val labels, clean test labels; two-spirals (400/200/400) with noise 0.2. Evaluation seeds 0-4; tuning seeds 100-102 (on digits these re-split the same image pool, so tuning images overlap evaluation test images).

## Metrics
Clean test accuracy (primary); gap_acc (noisy-train minus clean-test accuracy); gap_loss; fraction of flipped labels memorised; sharp_adv and sharp_rand; weight norm.

## Ablations and sensitivity
rho sweep {0.02, 0.05, 0.1, 0.2, 0.5, 1.0}; weight-decay sweep {1e-4, 1e-3, 1e-2, 5e-2}; SAM with a random direction of the same radius; SAM+WD with the two separately selected values.

## Decisions left open by the seed
- Datasets: digits and two-spirals (the Gaussian-mixture option was not used; two tasks fit the budget).
- Selection on noisy validation labels (clean validation labels would not be available in practice).
- Final-epoch model, no early stopping.

## Out of scope
CNNs and larger models, SAM variants (ASAM, ESAM), instance-dependent noise, learning-rate tuning, joint tuning of SAM+WD, compute-matched baselines, early stopping.
