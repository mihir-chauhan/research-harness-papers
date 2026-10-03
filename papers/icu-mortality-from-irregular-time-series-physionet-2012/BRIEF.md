# ICU mortality from irregular time series (PhysioNet 2012)

## Seed
ICU mortality from irregular time series (PhysioNet 2012). Download set-a of the PhysioNet 2012 challenge (4,000 stays, open access). Compare logistic regression and gradient boosting on per-variable summary statistics against a GRU with mask and time-delta inputs (GRU-D style) and a GRU on forward-filled values. Report AUROC, AUPRC and Brier score with 5-fold patient-level CV. Keep it a small CPU study with reimplemented baselines, at least 5 seeds where cheap, and report negative or mixed results plainly.

## Precise question
On PhysioNet/CinC 2012 set-a (4,000 ICU stays, 13.9% in-hospital mortality), does a GRU that sees observation masks and time-deltas (GRU-D or a plain mask+delta GRU) beat (a) a GRU on forward-filled values and (b) logistic regression / gradient boosting on per-variable summary statistics, when all five systems get the same small tuning budget and are evaluated with repeated 5-fold patient-level CV?

## Hypotheses (tests registered in proposal.md)
H1 GRU-D does not beat GBDT (refuted if GRU-D > GBDT by >0.01 AUROC, p<0.05). H2 mask+delta GRUs beat forward-fill GRU. H3 GRU-D decay adds over mask+delta GRU. H4 count (missingness) features help LR/GBDT. H5 (exploratory) ranking is stable at 12 h / 24 h horizons.

## Method / systems (all reimplemented in method/run.py)
LR (L2) and HistGradientBoosting on per-variable min/max/mean/std/first/last/count + static features; GRU on hourly forward-filled values; GRU on [ffill, mask, delta]; GRU-D (input + hidden decay, mask input). Neural models share a head and static inputs.

## Protocol decisions (rh decide)
Hourly binning (48 steps, last value in bin); 5 seeds, where seed controls fold assignment and initialisation; fold-averaged metrics per seed; hyper-parameters selected on a 25% hold-out of fold-0 training data for tuning seeds 100/101 (disjoint from the evaluation seeds' use of test folds only in the sense that no test fold is used for tuning of that seed... see PROTOCOL.md); early stopping on a 15% inner validation split.

## Metrics
AUROC, AUPRC, Brier (fold-averaged), plus per-ICU-type AUROC from pooled out-of-fold predictions.

## Ablations
abl_decay (no input decay / no hidden decay / neither), abl_counts (LR and GBDT without count features), sweep_horizon (12 h, 24 h).

## Out of scope
Other irregular-sampling architectures, set-b/c, external validation, pre-training, calibration post-processing.
