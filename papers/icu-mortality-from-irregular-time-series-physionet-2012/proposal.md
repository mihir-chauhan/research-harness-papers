# Proposal

## Direction
ICU mortality from irregular time series (PhysioNet 2012 set-a): LR and gradient boosting on per-variable summaries versus a GRU on forward-filled values, a GRU with mask and time-delta inputs, and GRU-D; AUROC, AUPRC, Brier under 5-fold patient-level CV.

## Landscape
See `literature/landscape.md`. GRU-D (che2016recurrent) introduced decay-based missing-value handling; the MIMIC-III benchmark (harutyunyan2017multitask) and HiRID/YAIB benchmarks (yche2021hirid, water2023yet) report that engineered-feature baselines are close to deep models; irregular-sampling models (shukla2019interpolation, horn2019set, zhang2021graph, tipirneni2021self, rubanova2019latent) are usually evaluated on PhysioNet 2012 with a single split or few seeds.

## Gap
Equal tuning budgets, repeated patient-level CV and ingredient-level decomposition (mask vs delta vs decay) on a cohort of only 4,000 stays are rarely reported together.

## Contribution
An honest controlled comparison, not a new method: which ingredient (summary features, masks/deltas, decay) buys AUROC/AUPRC/Brier on set-a, with all five systems tuned on an identical small grid on inner validation data of training folds only.

## Hypotheses -> experiments
| ID | Hypothesis | Group | Metric | Decides if |
|---|---|---|---|---|
| H1 | GRU-D does not beat GBDT | main | auroc | rh compare ref GRU-D vs GBDT; refuted if GRU-D > GBDT by >0.01 AUROC and p<0.05 |
| H2 | mask+delta GRUs beat forward-fill GRU | main | auroc | rh compare ref GRU (forward-fill), p<0.05 |
| H3 | decay adds over mask+delta | main, abl_decay | auroc | rh compare ref GRU (mask+delta), p<0.05 |
| H4 | count features help LR/GBDT | abl_counts | auroc | rh compare, p<0.05 |
| H5 | ranking stable under shorter horizon (exploratory) | sweep_horizon | auroc | descriptive |

All comparisons: paired by seed (5 seeds; each seed gives a different fold split and initialisation), unit of analysis = fold-averaged metric of a seed. Because the same 4,000 patients are reused in every seed, seed-to-seed variance understates sampling uncertainty; stated as a limitation.

## Planned baselines
LR (summary), GBDT (summary; sklearn HistGradientBoosting), GRU (forward-fill), GRU (mask+delta), GRU-D; all reimplemented.

## Planned ablations
Decay components (no input decay, no hidden decay, none); count features on/off for LR and GBDT; observation horizon 12/24 h.

## Risks and fallbacks
Neural models may match but not beat GBDT; reported plainly. Tuning budget identical across systems (small grid, inner validation of fold 0 of tuning seeds 100 and 101).
