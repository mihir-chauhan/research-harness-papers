# Label-noise robustness of a small CNN on 8x8 digits: CE, label smoothing, mixup, small-loss selection

## Question
On scikit-learn 8x8 digits (1,797 images; no download needed), how do plain cross-entropy (CE), label smoothing (LS),
mixup and a one-network small-loss selection rule (co-teaching style, single network) compare in clean test accuracy and
in how much of the corrupted training labels they memorise, at symmetric label-noise rates 0/20/40/60%?

## Hypotheses (falsifiable)
- H1: Plain CE memorises: at 40% and 60% noise, its final-epoch training fit to the corrupted labels (mem_rate) exceeds 0.9 and its clean test accuracy falls by >10 points relative to 0% noise.
- H2: Label smoothing (eps=0.1) does not materially improve robustness: its test-accuracy gain over CE at 40% noise is <3 points (paired across seeds, not significant).
- H3: Mixup (alpha=1) reduces memorisation (mem_rate lower than CE at 40% noise) and improves test accuracy over CE at 20-60% noise.
- H4: Small-loss selection (with the true noise rate assumed known) gives the best test accuracy at 40% and 60% noise and the most negative mem_gap, but costs accuracy at 0% noise relative to CE.
- H5 (sensitivity): small-loss selection depends on the assumed forget rate: under-estimating the noise rate loses most of the gain.

## Method / systems (all reimplemented, identical CNN, optimizer, epochs, data)
CE; LS (eps=0.1); mixup (alpha=1, input mixing, loss mixing); small-loss selection (name: "Small-loss (1 net)"): per mini-batch keep the
(1 - r_t) fraction of lowest-loss samples, r_t ramps linearly to the noise rate after a warm-up. The seed names "co-teaching style with one network";
the paper's own method is the small-loss rule, i.e. the study is a comparison, not a new method.

## Tasks, data, metrics
Task = noise rate (digits_noise0/20/40/60). Fixed stratified 60/40 train/test split (1078/719); symmetric noise on train labels only (label replaced by a uniform other class
with prob. r); test labels clean. No validation set and no early stopping: all hyperparameters fixed a priori (no tuning on test), final-epoch model reported.
Metrics: test_acc (higher better); mem_rate = fraction of corrupted training samples predicted as their wrong label (lower better); recover_rate = fraction
predicted as their true label (higher better); mem_gap = mem_rate - recover_rate (lower better), the memorised-vs-clean-label gap.
Seeds 0-4 (seed controls noise draw, init, batch order).

## Ablations / sensitivity
abl_smallloss (40% noise): no warm-up/ramp (forgets from epoch 0), and misspecified assumed rate (0.2, 0.6 vs true 0.4).
sweep_mixup_alpha, sweep_ls_eps at 40% noise.

## Out of scope
Real-world noise, asymmetric/instance noise, two-network co-teaching, DivideMix-type semi-supervised methods, larger datasets, validation-based model selection.
