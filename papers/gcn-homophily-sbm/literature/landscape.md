# Landscape
- GCN (Kipf & Welling 2017) aggregates normalised neighbourhoods with self loops: a low-pass filter, assumed to help under homophily.
- Beyond Homophily / H2GCN (Zhu et al. 2020) argues ego/neighbour separation, higher-order neighbourhoods and intermediate-representation combination help under heterophily.
- GPR-GNN (Chien et al. 2021) learns signed propagation weights.
- CSBM (Deshpande et al. 2018) is the standard synthetic model combining a SBM with Gaussian covariates; Baranwal et al. (2021) show graph convolution widens the linearly-separable regime under homophily, Ma et al. (2022) show GCN can do well under heterophily when neighbourhood label distributions are distinguishable, so homophily alone is not the criterion.
- Luan et al. (2022) argue that post-aggregation similarity, not homophily, explains when GNNs lose to MLPs; Platonov et al. (2023) show that tuned standard GNNs beat specialised heterophily models on cleaner benchmarks.
- Oono & Suzuki (2020): deep GCNs lose expressive power (we stay at 2 layers).
Gap: a seed-level, controlled map of four simple models over the (homophily x feature informativeness) plane, with a specific test of the mid-homophily GCN < MLP dip, including where label propagation wins.
