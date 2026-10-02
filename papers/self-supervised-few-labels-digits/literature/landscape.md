# Landscape

Contrastive and pretext-task self-supervised learning (SSL) are established at ImageNet scale. SimCLR (chen2020simple)
learns representations by maximising agreement between two augmented views with a normalised-temperature cross-entropy loss;
MoCo (he2019momentum) and BYOL (grill2020bootstrap) change how negatives / targets are produced. Rotation prediction
(gidaris2018unsupervised) is a pretext task: classify which of four rotations was applied. Contrastive predictive coding
(oord2018representation) is the common ancestor of the InfoNCE objective.
Kolesnikov et al. (kolesnikov2019revisiting) show that pretext-task conclusions depend strongly on architecture and that linear-probe
quality is fragile. SSL helps label efficiency at scale: S4L (zhai2019s) and SimCLRv2 (chen2020big) use SSL for semi-supervised ImageNet.
Closest to our question: Konstantakos et al. (konstantakos2024self) compare SSL methods in the low-data regime (small pretraining sets)
and Su et al. (su2019boosting) use rotation as an auxiliary task for few-shot learning.

Gap: nearly all evidence is at ImageNet scale with large ResNets. How a few-hundred-parameter-thousand CNN with 1.3k unlabeled
8x8 images behaves, and whether it beats a PCA+logistic-regression baseline at 10/50/200 labels, is rarely reported with matched probes and seeds.
This study is a small, controlled, multi-seed measurement of that gap; it makes no claim of generality beyond digits.
