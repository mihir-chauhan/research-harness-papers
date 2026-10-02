# Proposal

**Question.** With the same library (degree-2 polynomials in x,y,z; 30 coefficients, 7 truly nonzero) and the same STLSQ solver, how does the source of the derivative information (finite differences, Savitzky-Golay, smoothing spline, TV-regularised differentiation, weak form) determine the rate of exact support recovery and the coefficient error on Lorenz-63 as noise grows from 0 to 10 % of signal std?

**Method (the one we advocate testing): "Weak-form STLSQ"**: integrate against test functions (1-s^2)^3 on 200 windows, no differentiation. Baselines (all reimplemented): FD-STLSQ, SG-STLSQ, Spline-STLSQ, TV-STLSQ.

**Hypotheses** (primary metric support_exact; secondary coef_err; tasks = noise levels 0, 0.5, 1, 2, 5, 10 %; 20 seeds each)
- H1: At every noise level >= 1 %, Weak-form STLSQ has a higher exact-support rate than every derivative-based baseline. Test: `rh compare --metric support_exact` per task, Weak vs each baseline, p<0.05 (the harness test) AND higher mean. Refuted if any baseline matches or beats it at >= 1 % noise, or the difference is not significant.
- H2: Every smoothing derivative (SG, spline, TV) has lower mean coef_err than raw FD at noise >= 1 %. Test: `rh compare --metric coef_err` per task against FD. Refuted if any smoother is not lower at some level >= 1 %.
- H3: At 0 % noise all five systems recover the support in all seeds (sanity / ceiling). Refuted if any system has rate < 1.
- H4 (sensitivity): the weak-form advantage depends on the test-function window width; too narrow a window loses the advantage. Test: sweep of width at 2 % noise (table of support rate vs width); only reported descriptively.
- H5 (ablation): evaluating the library on the smoothed state (SG, spline) instead of the raw noisy state improves support recovery at 2 % noise. Descriptive comparison of the two groups.

**Out of scope**: ensemble/bagging SINDy, other systems, other libraries, implicit SINDy-PI, higher noise structure (non-Gaussian, colored), automatic hyperparameter selection without ground truth.

**Tuning budget.** Per system and noise level, a grid of 5-35 configurations (including the STLSQ threshold) scored on 5 independent tuning trajectories (seeds 1000-1004) using the ground truth; test seeds are 0-19. This is oracle-assisted tuning (ground truth is used for model selection on separate data), so absolute rates are optimistic for all systems alike.
