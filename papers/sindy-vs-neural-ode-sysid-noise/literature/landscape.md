# Landscape
- SINDy (Brunton et al. 2016) and SINDYc (Brunton et al. 2016, with control) identify sparse ODEs by (sequentially thresholded) regression on a function library. SINDy-MPC (Kaiser et al. 2018) shows MPC on a sparse model works in the low-data limit. Ensemble-SINDy (Fasel et al. 2022) and weak-form SINDy (Messenger & Bortz, ODEs 2020, extended to PDEs 2021) target noise robustness; PySINDy (Kaptanoglu et al. 2022) is an open-source package implementing these variants.
- Neural ODEs (Chen et al. 2018) and neural-network dynamics for MPC (Nagabandi et al. 2018) give flexible black-box models; Lusch et al. (2018) learn Koopman embeddings with networks.
- DMD with control (Proctor et al. 2016) fits a linear model by least squares; the standard linear baseline.
- Search results also include benchmark/noise-impact studies of SINDy (2024-2025) that evaluate identification accuracy, not closed-loop cost.
## Gap
Comparisons rarely report the closed-loop cost of controllers designed on each identified model while varying noise and data size together. We provide a small, controlled, reproducible CPU comparison. We do not claim a new method.
