# Proposal

**Question.** On scikit-learn digits with rotation and Gaussian-noise shift of increasing intensity, how do a single MLP, temperature scaling fitted on in-distribution validation data (TS), MC dropout and a 5-member deep ensemble compare in accuracy, ECE, NLL and Brier score, and does ID-fitted TS stay calibrated under shift?

**Systems.** MLP (T=1); MLP+TS (method in focus; single scalar T fitted on a held-out ID validation split); MC dropout (20 stochastic passes); Deep ensemble (5 independently initialised MLPs, probability averaging). All reimplemented.

**Tasks.** 11 test conditions: rot0 (in-distribution), rot10/20/30/45/60 degrees; Gaussian noise sigma 0.25/0.5/0.75/1.0 (pixel scale [0,1]); and rot30+noise0.5.

**Hypotheses and refutation criteria** (paired comparisons across 5 seeds, `rh compare`, alpha 0.05; no multiple-comparison correction, so verdicts are descriptive).
- H1: In distribution (rot0), TS lowers NLL relative to the uncalibrated MLP. Refuted if NLL(TS) >= NLL(MLP) or the paired difference is not significant.
- H2: ID-fitted TS does NOT stay calibrated: ECE of TS at the strongest shifts (rot60, noise1.0) is at least 2x its rot0 value, and its NLL gain over the MLP shrinks with intensity. Refuted if ECE(TS) at those shifts is < 2x its ID value.
- H3: The 5-member ensemble has the lowest NLL and Brier score of the four systems at rot60 and noise1.0. Refuted if any other system is lower there on mean over seeds.
- H4: Ensemble ECE < MC dropout ECE at rot60 and noise1.0 (paired).
- H5 (mechanism, ablation): fitting T on validation data transformed like the test shift ("oracle TS") yields lower ECE than ID-fitted TS at the severe shifts, so that the failure is a temperature mismatch rather than a limit of scalar rescaling. Refuted if oracle-TS ECE is not lower.
Sensitivity: ensemble size M in {1,2,3,5,10}; dropout rate p in {0.1,0.2,0.3,0.5}.
**Out of scope.** Other datasets, CNNs, OOD detection, conformal methods, tuned hyperparameters.
