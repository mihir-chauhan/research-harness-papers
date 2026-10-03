# Proposal
See BRIEF.md for the question, hypotheses H1-H6 with their registered tests, methods, baselines and metrics.

Closest prior work: Carrasquilla & Melko 2017 (supervised classifiers), van Nieuwenburg et al. 2017 (confusion), Wang 2016 and Hu et al. 2017 (PCA). Our contribution is not a new method: it is a seed-paired, equal-data comparison with a Binder/susceptibility reference, a collapse readout, and sensitivity studies.

Refutation criteria: H1 refuted if CNN/MLP error at L=32 is not lower than PCA (p>=0.05, rh compare); H2 if collapse error is not lower (paired Wilcoxon p >= 0.05); H3 if raw LogReg acc_far >= 0.6 or Z2-fixed < 0.6; H4 if PCA or confusion has lower FSS error than CNN with p<0.05; H5 if mean nu_error >= 0.25; H6 if any sweep setting has more than twice the default error.

Planned baselines: LogReg (raw/Z2-fixed), MLP, PCA, Confusion (MLP), Binder/chi reference. Ablations: training margin, training samples per temperature.
Risks: finite-size bias dominates; collapse is poorly conditioned with three small sizes (we report it as is).
