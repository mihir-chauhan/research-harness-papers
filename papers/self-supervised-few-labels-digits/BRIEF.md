# Does self-supervised pretraining help with few labels at tiny scale?

## Question
On the sklearn 8x8 digits, does SSL pretraining (SimCLR-style, rotation) of a small CNN on an unlabeled pool improve a linear probe trained on 10, 50 or 200 labels, relative to supervised scratch training and PCA + logistic regression?

## Hypotheses (falsifiable)
- H1 SimCLR probe beats supervised scratch at every budget (paired over 5 seeds).
- H2 SimCLR beats rotation pretraining at every budget.
- H3 SSL probes beat PCA+LR at 10 labels and the gap is within 2 points at 200 labels.
- H4 Removing either augmentation family lowers SimCLR accuracy at 50 labels.

## Method, baselines, tasks, metrics
Method: SimCLR-style NT-Xent pretraining of a 3-conv encoder, frozen, standardised logistic-regression probe. Baselines (all reimplemented): rotation prediction, supervised scratch (same encoder), PCA(16)+LR, pixels+LR, random frozen encoder+probe. Tasks n10, n50, n200 (class-balanced labels); 5 seeds, 497-image stratified test split per seed, 1300-image unlabeled pool. Metric: test accuracy (higher better), identical for all systems.
Ablations: augmentation family (geom/photo only), scratch + augmentation, temperature, epochs. Decisions: no hyper-parameter tuning, no validation set (labels too scarce); see `rh decide`.

## Out of scope
Other datasets, larger models, MoCo/BYOL, encoder fine-tuning, tuned baselines.
