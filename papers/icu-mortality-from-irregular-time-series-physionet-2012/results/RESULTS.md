# Results (PhysioNet 2012 set-a, 5 seeds x 5-fold patient-level CV)
All numbers are in the run registry (`rh values --list`) and reach the paper only through `\rhval` or generated tables; see `paper/sections/results.tex` and `ablations.tex`.

| Hypothesis | Verdict | Deciding rows |
|---|---|---|
| H1 GRU-D does not beat GBDT | Supported (GRU-D is lower; refutation criterion not met) | main AUROC; `rh compare --group main --metric auroc` (paired p); analysis `d_grud_gbdt_auroc` |
| H2 mask+delta helps GRU over forward-fill | Not supported at 48 h; supported at 12 h and 24 h | analysis `*_md_ffill`, `*_grud_ffill`; group sweep_horizon |
| H3 decay adds over mask+delta | Not supported (also no effect in abl_decay) | analysis `grud_md`, `noin/nohid/nodecay_grud` |
| H4 count features help LR/GBDT | Supported for LR, not for GBDT | group abl_counts; analysis `lrnocnt_lr`, `gbnocnt_gb` |
| H5 ranking stable across horizons (exploratory) | Partly: GBDT first by AUROC at every horizon; GRU-D vs forward-fill gap grows at short horizons; GRU-D ~ LR at 12/24 h | group sweep_horizon, analysis `h12_*`, `h24_*` |
