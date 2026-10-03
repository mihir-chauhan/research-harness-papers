# Landscape
- GRU-D (che2016recurrent): GRU with trainable decay of inputs toward last observation / mean and of hidden state, plus masks; reported gains over GRU-mean/forward-fill and over feature baselines on PhysioNet 2012 and MIMIC-III.
- lipton2016modeling: shows missingness indicators alone are predictive in ICU data; motivates mask inputs.
- Benchmarks: harutyunyan2017multitask (MIMIC-III; LR on engineered features close to LSTMs), yche2021hirid (HiRID), water2023yet (YAIB): GBDT strong.
- Irregular-sampling neural models evaluated on PhysioNet 2012: shukla2019interpolation (interpolation-prediction), horn2019set (SeFT), rubanova2019latent (Latent ODE), zhang2021graph (Raindrop), tipirneni2021self (STraTS). Typically single split/few seeds; comparisons to GBDT often absent.
- grinsztajn2022why: tree ensembles remain strong on medium-sized tabular data; chen2016xgboost: gradient boosting.
- Gap: with 4,000 stays, are neural gains over tuned summary baselines real once seeds, folds and tuning budgets are equalised, and which ingredient of GRU-D matters? We do not claim a new method.
