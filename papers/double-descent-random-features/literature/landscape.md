# Landscape

Searches (see literature/candidates.jsonl): "double descent random features ridge regression", "random features model interpolation threshold test error peak", "optimal regularization removes double descent", "surprises in high-dimensional ridgeless least squares".

## What exists
- Belkin et al. (belkin2018reconciling) describe double descent empirically, including random Fourier features, and Nakkiran et al. (nakkiran2019deep) show it across model size, epochs and label noise in deep networks.
- Mei & Montanari (mei2019generalization) derive the asymptotic test error of random-features ridge regression, with a peak at N/n=1 that grows as the ridge goes to 0; d'Ascoli et al. (dascoli2020double) decompose it into bias and several variance terms; Hastie et al. (hastie2019surprises) treat ridgeless interpolation for linear and random-feature models.
- Nakkiran et al. (nakkiran2020optimal) prove that optimally tuned ridge gives monotone risk for isotropic linear regression and show experiments beyond it; Yilmaz & Heckel (yilmaz2022regularization) show risk can be double-descent shaped in the regularisation strength itself; Kan et al. (kan2020avoiding) avoid the peak in random-feature models with hybrid regularisation; Liu et al. (liu2021double) study RF trained with SGD; Meng et al. (meng2022multiple) show multiple descent with concatenated random features; Tsigler & Bartlett (tsigler2020benign) analyse ridge in overparametrised linear regression.

## Closest work and gap
Theory gives the asymptotic picture for Gaussian data and mostly noise-free or simple-noise settings; Nakkiran et al. test optimal ridge on RF only qualitatively. What is cheap and missing is a small, fully reproducible finite-sample (n=200) measurement, on one synthetic and one real (digits) task, of three quantities as label noise and ridge vary: peak height, peak position, and a defined "bump" statistic, together with a test of whether a validation-tuned ridge (per width), a single global ridge, or a leave-one-out tuned ridge removes the bump at this finite size. We claim no new theory; this is a replication-style empirical study with explicit pre-registered thresholds.
