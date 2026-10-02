# Brief: calibration under shift on digits

**Question.** Single MLP vs temperature scaling (TS, fitted in-distribution) vs MC dropout vs 5-member deep ensemble on scikit-learn digits under rotation and Gaussian noise shift of increasing intensity; accuracy, ECE, NLL, Brier per intensity. Does ID-fitted TS stay calibrated under shift?

**Hypotheses.** H1-H5 as in `proposal.md` (TS helps ID; TS ECE at least doubles at severe shift; ensemble best NLL/Brier at severe shift; ensemble ECE below MC dropout; oracle shift-matched TS fixes ECE).

**Method/baselines.** All reimplemented in `method/run.py` (torch MLP 64-128-128-10). 5 seeds, 11 shift conditions (rot 0-60 deg, noise sigma 0.25-1.0, one combined). Metrics: accuracy, 15-bin top-label ECE, NLL, multiclass Brier, mean confidence.

**Ablations.** Oracle-temperature TS; ensemble size sweep; dropout rate sweep.

**Decisions (also `rh decide`).** No proposed method exists in the seed, so the "method" slot is TS, the object of the question; other systems are baselines. The seed leaves split sizes and hyperparameters open: fixed a priori, none tuned on test. Each (system, shift, seed) is its own run; models are trained once per (system, seed) and cached on disk, so rows of one seed across shifts share the same trained network.

**Out of scope.** Other datasets/architectures, OOD detection, conformal, hyperparameter tuning, larger scale.
