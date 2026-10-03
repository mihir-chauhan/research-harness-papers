# Landscape
- Carrasquilla & Melko (1605.01735): fully connected / CNN classifiers trained deep in each phase of the 2D Ising model; Tc read from the output crossing and finite-size collapse. Closest prior work; we reimplement the protocol at small scale.
- van Nieuwenburg et al. (1610.02048): learning by confusion; W-shaped accuracy vs trial critical point, the middle peak marks the transition. Label-free-ish alternative reimplemented here.
- Wang (1606.00318), Hu et al. (1704.00080): PCA recovers magnetisation as the first principal component; Hu et al. examine when this works. Reimplemented as PC1-fluctuation peak.
- Ch'ng et al. (1609.02552): neural-net phase classification on fermions; Suchsland & Wessel (1802.09876): the crossing of a classifier depends on training windows/parameters (diagnostics).
- Physics tools: Onsager (exact Tc), Swendsen-Wang / Wolff cluster updates, Fisher-Barber finite-size scaling, Binder cumulant.
- Gap: papers rarely compare, on identical data and with identical error definitions and many seeds, (i) linear vs nonlinear vs convolutional classifiers (the Z2 symmetry blinds a linear readout of raw spins), (ii) single-size crossing vs collapse, (iii) supervised vs PCA vs confusion, (iv) sensitivity to the training window. This is what the study measures, with negative results reported.
