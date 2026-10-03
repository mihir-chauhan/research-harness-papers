# Proposal

## Direction
Low-N regression on the GB1 four-site landscape (149,361 variants, FLIP copy of Wu et al. 2016): one-hot ridge, one-hot + pairwise epistasis ridge, a Gaussian process and a small CNN trained on N = 48, 96, 384, 2000 random or single/double-mutant-only variants; Spearman and top-100 recall on the remaining variants over 5 draws.

## Landscape
GB1 four-site data come from Wu et al. [wu2016adaptation]; FLIP [dallago2021flip] uses an 8.7k-variant subsample with fixed splits. One-hot ridge is a strong low-N baseline [hsu2022learning]; GPs for fitness landscapes date to [romero2013navigating] and kernel regression with structure kernels is Kermut [groth2024kermut]; regression comparisons [michael2024systematic]; global epistasis [otwinowski2018inferring]; minimum epistasis interpolation [zhou2020minimum]. Representation baselines TAPE/UniRep [rao2019evaluating, alley2019unified]; PLMs [meier2021language]; ProteinGym [notin2023proteingym].

## Gap
Few controlled comparisons on the *complete* GB1 landscape that vary training-set composition (random vs. low-order mutants) and report top-k recall and error by distance from wild type with identically budgeted tuning.

## Contribution
An honest, reimplemented small study; not a new method. The "method" under test is pairwise-epistasis ridge.

## Hypotheses -> experiments
See research.yaml H1-H5; main group `main`, tests are paired Wilcoxon (rh compare) on spearman per task, 5 seeds (minimum attainable two-sided exact p = 0.0625, so "significant at 0.05" is not attainable; effects are reported descriptively with this caveat). Refutation: H1 refuted if pairwise >= ridge at N<=96 or <= ridge at N>=384 in mean; H2 refuted if GP mean < ridge mean at N<=96; H3 refuted if CNN mean >= best other at N<=384 or clearly > at 2000; H4 refuted if any system has dbl >= rand at HD>=3; H5 refuted if any mean recall >= 0.25 at N<=384.

## Planned baselines
One-hot ridge (Hsu et al. style), GP Hamming kernel, CNN; all reimplemented in method/run.py.

## Planned ablations
GP fixed vs ML-fitted hyperparameters; ridge alpha sweep at N=384; CNN tuning/ensemble/log-target variants.

## Risks
All models may be ~equal; GB1 has ~ many near-zero variants so Spearman is dominated by the dead/alive split.

## Amendment (recorded before writing results)
The hypotheses table above names a Wilcoxon signed-rank test. With five seeds its minimum two-sided p-value is above 0.05, and `rh compare` reports Welch and paired t-tests only. Verdicts therefore follow the mean-based refutation rules written above; paired t-test p-values are quoted descriptively. This choice was made after the main runs had been inspected.
