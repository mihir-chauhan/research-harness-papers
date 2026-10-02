# Proposal
## Question
Which imbalance corrections help discrimination, and which only distort predicted risk, for LR and GB on breast cancer Wisconsin at natural, 1:5, 1:20, 1:50 prevalence?

## Hypotheses and refutation tests (registered before the main runs)
- H1: reweight/ROS/SMOTE give no AUROC/AUPRC gain >= 0.01 (vs no correction, same learner and task). Refuted for a cell if mean paired gain >= 0.01 with paired p < 0.05 (`rh compare`).
- H2: reweight/ROS/SMOTE increase Brier and |CITL| vs no correction at 1:20 and 1:50. Refuted for a cell if Brier is not higher, or lower, than no correction.
- H3: threshold moving gives metric values equal to no correction for AUROC, AUPRC, Brier, slope; sensitivity higher, specificity lower. Refuted if probability metrics differ or sensitivity does not rise.
- H4: with prior correction, mean Brier of reweight/ROS/SMOTE is within 0.005 of no correction. Refuted if the gap exceeds 0.005 in a cell.

## Method
Reference arm: LR without correction. Baselines (reimplemented): reweighting, ROS, SMOTE, threshold moving; both learners. Ablations: prior-shift correction; SMOTE target ratio sweep.
## Tasks / metrics
bc_natural, bc_1to5, bc_1to20, bc_1to50; AUROC, AUPRC, Brier, calibration slope, CITL, sensitivity/specificity. 10 seeds.
## Novelty checks
Closest: carriero2024harms, andersen2026tipping, sirikul2026class. Ours is a small reproducible replication-style study with threshold moving and the analytic offset; it makes no claim of novelty beyond that. Queries: see literature/candidates.jsonl.
