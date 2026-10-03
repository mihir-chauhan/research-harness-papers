# Low-N regression on the GB1 four-site landscape

**Question.** On the complete GB1 four-site landscape (149,361 variants; FLIP copy), how do one-hot ridge, one-hot + pairwise-epistasis ridge, a Hamming-kernel GP and a small CNN compare when trained on N in {48, 96, 384, 2000} variants, drawn either uniformly at random ("rand") or only from single/double mutants of wild type ("dbl")?

**Decisions (the seed left these open).** Test set = all variants not in training (rand) or all HD>=3 variants (dbl). Target = raw fitness. Hyperparameters: ridge alpha by 5-fold CV on training data; GP by marginal likelihood grid; CNN fixed after a small tuning on a separate seed (100). Seeds 0-4 (5 draws), same training draw across systems. The pairwise ridge is the nominal "method"; others are baselines. dbl pool has 2,168 variants, so dbl_2000 is almost the whole pool.

**Hypotheses.** H1-H5 in research.yaml / proposal.md. **Metrics.** Spearman, top-100 recall, Spearman by Hamming distance. **Ablations.** GP hyperparameters, ridge alpha sweep, CNN variants. **Out of scope.** Pretrained PLMs, other landscapes, active learning.
