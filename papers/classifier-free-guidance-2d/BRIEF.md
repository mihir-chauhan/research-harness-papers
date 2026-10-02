# What does classifier-free guidance trade away? (BRIEF, rewritten by the author)

**Question.** On a 2D conditional mixture with known ground truth (4 classes x 3 modes, unequal mode weights 0.5/0.3/0.2, modes interleaved on a ring so classes overlap), what does classifier-free guidance (CFG) gain and lose as the guidance scale w grows, and is that different from low-temperature sampling of the unguided conditional model?

**Hypotheses** H1-H5 with registered tests: see `proposal.md` / `research.yaml`.

**Method.** eps-prediction DDPM (cosine schedule, T=100) with a small MLP, label dropout 0.1; CFG eps=(1+w)eps_c - w eps_null; ancestral sampling.
**Baselines (reimplemented, same network and sampler).** Unguided conditional (w=0); low-temperature (initial and injected noise scaled by tau).
**Tasks.** mix_overlap (sigma=0.6) and mix_sep (sigma=0.35).
**Metrics.** class_acc (true Bayes posterior argmax == conditioning class), support_prec (within 3 sigma of a right-class mode), mode_cov (right-class modes holding >= half their true share), mode_tv (TV between sample and true mode weights), std_ratio (RMS within-mode deviation / sigma; <1 = variance collapse), off_support (outside 3 sigma of every mode), swd (sliced Wasserstein to true class distribution).
**Ablations/sensitivity.** w sweep, tau sweep, label dropout p, guidance interval.
**Decisions.** Seeds 0-4; one network per (task, seed, p) cached and shared by all sampling configs; x0 clipping to +-3 (normalised units) in every system.
**Out of scope.** Images, learned feature metrics, other guidance variants beyond the interval ablation, flow matching, theory.
