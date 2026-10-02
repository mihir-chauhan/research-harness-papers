# Proposal
Question: how do training-set size N in {100,250,500,1000,2000} and label noise (boundary jitter, object class flips; level 0-30%) jointly affect per-class IoU of a small U-Net on synthetic shapes, and do robust losses help?
Systems (same U-Net, optimiser, steps, data): CE; GCE (q=0.7) and SCE (alpha=0.1, beta=1) reimplemented; Band-ignore CE (ours, a trimap-style ignore band).
Hypotheses and registered tests (Welch t, alpha=0.05, 4 seeds in main and size at N=100,2000; 3 seeds elsewhere):
- H1 clean mIoU(N=2000) > mIoU(N=100). Refuted if difference within noise or negative.
- H2 flip_p0.3 hurts more than boundary_p0.3 at N=500. Refuted if boundary is not smaller-drop.
- H3 drop under flip_p0.3 larger at N=100 than N=2000. Refuted otherwise.
- H4 GCE/SCE/Band-ignore beat CE under noise and do not lose clean. Refuted per loss otherwise.
Metrics: mIoU (4 classes incl. bg), per-class IoU on clean test labels (500 images).
Sensitivity: GCE q, number of steps (memorisation), noise level sweep.
