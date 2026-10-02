# Landscape

- **SINDy** (Brunton et al. 2016, `brunton2015discovering`) regresses time derivatives on a library of candidate terms with sequential thresholded least squares (STLSQ). It needs x-dot, which is not measured; numerically differentiating noisy data is the known weak point.
- **PDE-FIND** (Rudy et al. 2017, `rudy2016data`) uses sequentially thresholded ridge regression and polynomial/smoothed derivatives; noise sensitivity of the derivative is reported there.
- **PySINDy** (de Silva et al. 2020, `silva2020pysindy`) is the reference toolbox; it ships finite-difference, smoothed finite-difference and spline/TV differentiators, which is the set of options compared here (we reimplement them, we do not call PySINDy).
- **Numerical differentiation of noisy data**: Savitzky-Golay (`savitzky1964smoothing`), TV-regularised differentiation (Chartrand 2011, `chartrand2011numerical`), and the multi-objective, parameter-selection view of van Breugel et al. (`breugel2020numerical`).
- **Weak / integral formulation**: Weak SINDy (Messenger & Bortz, `messenger2020weak`) multiplies the dynamics by compactly supported test functions and integrates by parts so no derivative of the data is needed. Related robust variants: SINDy-PI (`kaheman2020sindy`), Ensemble-SINDy (`fasel2021ensemble`, bagging, out of scope here).
- Lorenz-63 (`lorenz1963deterministic`) is the standard test system.

**Gap.** The papers above each show their own method working; a controlled head-to-head of the *derivative source* with an identical STLSQ back end, identical data, a matched tuning budget on separate trajectories and exact-support-recovery rate as the headline metric over a noise grid is what this small study provides. It is a replication-style comparison, not a new algorithm. The weak form is reimplemented in its simplest form (one polynomial test-function family, equispaced windows, no adaptive width, no iteratively reweighted regression).

**Addendum (revision).** The ODE Weak SINDy paper (Messenger & Bortz 2021, `messenger2021weak`) is the direct precedent: it compares the weak form with standard SINDy and reports correct identification in small- and large-noise regimes. Our comparison differs by putting four derivative estimators and a much simpler weak form behind one STLSQ back end with one tuning protocol.
