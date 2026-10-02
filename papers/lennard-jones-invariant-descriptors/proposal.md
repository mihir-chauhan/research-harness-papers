# Proposal
## Question
On small LJ clusters (5-13 atoms) how do raw coordinates, sorted inverse pairwise distances and sum-pooled Behler-Parrinello symmetry functions compare, with KRR and a small MLP, on energy error, data efficiency and invariance to rotation and atom permutation of the test set?
## Hypotheses (tests registered before runs)
H1-H4 as in research.yaml (Welch tests via `rh compare`, ratios, learning curves).
## Refutation
H1 refuted if any invariant descriptor is not better than raw at n=500 for either regressor. H2 refuted if raw degradation < 2x or an invariant defect >= 1e-4. H3 refuted if SF-KRR is not lower than sorted-KRR at n=50/150. H4 refuted if KRR is not better at n<=150 for the majority of descriptors.
## Baselines
Raw/sorted-distance descriptors (Coulomb-matrix-style sorted representations [Rupp 2012]), MLP, BP-style atomwise network (reimplemented).
## Ablations
Radial-only SFs; on-the-fly rotation/permutation augmentation of the raw MLP; train-size sweep.
## Risks
Sorted distances may beat symmetry functions (they are a complete representation); the MLP may be undertrained at this budget. Both reported as found.

## Addendum (fix round)
Hypotheses and tests are unchanged. The KRR hyperparameter grid was widened after an audit (see BRIEF.md, decisions of the fix round);
added controls: linear ridge, KRR grid sensitivity, mean predictor at every n.
