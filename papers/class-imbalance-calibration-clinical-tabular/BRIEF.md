# Imbalance corrections vs calibration on small clinical tabular data

## Question
Which class-imbalance corrections (class reweighting, random oversampling, SMOTE, decision-threshold moving) improve discrimination (AUROC, AUPRC) and which only distort predicted risk (Brier score, calibration slope, calibration-in-the-large), for logistic regression (LR) and gradient boosting (GB), on breast cancer Wisconsin (scikit-learn) at natural prevalence and artificially imbalanced 1:5, 1:20, 1:50?

## Decisions (no human available)
- Positive class = malignant. For 1:k, TRAINING positives are subsampled to n_neg_train/k. The test split keeps all held-out rows and test positives are weighted so the *evaluation prevalence equals the training prevalence 1:k*; all test metrics are weighted. Reason: raw 1:50 gives 7 positives in total (2 in a test split).
- 10 repeated stratified 70/30 splits (seeds 0-9). No tuning: fixed hyperparameters (LR C=1; GB 100 trees, depth 3, lr 0.1), so every system has the same budget (none).
- Corrections to a 1:1 target ratio; SMOTE, ROS implemented directly in numpy. Threshold moving = train without correction, cut-off at training prevalence (probabilities unchanged).
- The "method" arm is LR without correction (this is a comparison study, no new algorithm).
- Calibration slope: weighted logistic fit of y on logit(p) (p clipped to [1e-6,1-1e-6]); reported as |slope-1| for rankings.

## Hypotheses (falsifiable)
H1 corrections do not raise AUROC/AUPRC (gain < 0.01). H2 reweight/ROS/SMOTE worsen Brier and calibration-in-the-large at 1:20, 1:50. H3 threshold moving leaves all probability metrics unchanged and trades specificity for sensitivity. H4 analytic prior-shift logit offset restores Brier (within 0.005 of no correction). Tests in `proposal.md`.

## Methods / baselines
Five strategies x two learners; ablations: prior-shift correction (abl_priorcorr), SMOTE target ratio sweep (sweep_smote_ratio at 1:20).

## Metrics
AUROC, AUPRC, Brier, |slope-1|, |CITL|, balanced accuracy, sensitivity, specificity.

## Out of scope
Other datasets, undersampling, deep models, hyperparameter tuning, cost-sensitive thresholds from decision curves, external validation, confidence-interval calibration curves.

## Revision after audit
Signed calibration-in-the-large, signed slope and the operating point (sensitivity, specificity, balanced accuracy) of every correction are reported next to the registered |CITL| and |slope-1|; these analyses were not registered and are labelled as such in the paper.
