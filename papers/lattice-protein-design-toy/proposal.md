# Proposal
## Question
At equal oracle budget, does a conditional AR designer beat simulated annealing for unique-ground-state design on held-out HP-16 targets, and why?
## Hypotheses (tests registered before the main runs, using `rh compare` over 5 seeds on the shared per-seed test targets)
- H1: succ_k1 of AR > random search and > contact heuristic. Refuted if AR is not higher than either.
- H2: succ_k100 of AR > SA.
- H3: succ_k1000 of SA >= AR (SA catches up). Refuted if AR still higher.
- H4: unconditional AR succ_k100 < conditional AR (group abl_components).
- H5: succ_k1 of AR > AR without reversal augmentation; succ_k1 increases with data fraction (sweep_data_frac).
## Method / baselines / tasks / metrics
See BRIEF.md and method/DESIGN.md. Single task hp16, 5 seeds, metrics succ_k*, gap_k*.
## Refutation
Any hypothesis whose comparison goes the other way or whose paired difference is within seed noise is reported as refuted/inconclusive.
