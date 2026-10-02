# Landscape
- Chawla et al. (SMOTE, chawla2011smote): interpolates minority points toward minority neighbours; the standard synthetic oversampler. imbalanced-learn (lemaitre2016imbalanced) is the reference implementation; we reimplement SMOTE directly.
- Carriero et al. 2024 (carriero2024harms): Monte Carlo simulations; corrections degrade calibration for several learners, discrimination not improved.
- Andersen et al. 2026 (andersen2026tipping): ten clinical datasets, 1:1 SMOTE/RUS/ROS; calibration impact studied alongside discrimination.
- Sirikul et al. 2026 (sirikul2026class): GUSTO-I based simulation with penalised LR; corrections did not enhance discrimination, calibration or stability.
- Dal Pozzolo et al. 2015 (pozzolo2015calibrating): analytic prior-shift correction of posteriors after undersampling; basis of our prior-correction ablation.
- Guo et al. 2017 (guo2017calibration): calibration as a reliability property of modern models; motivates calibration as an explicit metric.
- Friedman 2001 / Chen & Guestrin 2016: gradient boosting; we use scikit-learn's implementation (pedregosa2012scikit).
Gap (narrow): the existing simulation and real-data studies already cover several learners and event fractions; what a tiny CPU study on a bundled public dataset can add is a threshold-moving arm (which cannot change probabilities) and a test of whether the analytic prior-shift offset repairs the corrected models.
