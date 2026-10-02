# Proposal
Question: on sklearn 8x8 digits, does SSL pretraining of a small CNN (rotation prediction, SimCLR-style) on an unlabeled pool improve
a linear probe trained on 10, 50 or 200 labels, relative to supervised-from-scratch training and PCA + logistic regression?

Hypotheses (test = accuracy on a held-out 497-image test split, 5 seeds, paired by seed):
- H1: SimCLR features + linear probe beat supervised-from-scratch at every label budget. Refuted if the paired mean difference is <= 0 at any budget or the seed-level CI includes 0 at n10 or n50.
- H2: SimCLR beats rotation prediction at every budget (8x8 digits are not rotation-invariant but rotation is a weak pretext task). Refuted if rotation >= SimCLR at any budget.
- H3: SSL linear probes beat PCA+LR at 10 labels, but the advantage shrinks as labels grow (at n200 within 2 points). Refuted if the gap does not shrink or if SSL does not beat PCA at n10.
- H4: SimCLR gains come from the augmentations: removing geometric augmentations or noise/brightness changes lowers accuracy. Refuted if no variant is lower than full by more than seed noise.
Baselines: pixels+LR, PCA+LR, random frozen CNN + probe (control), supervised scratch (same CNN), all reimplemented.
Ablations: SimCLR augmentation family, temperature, pretraining epochs.
