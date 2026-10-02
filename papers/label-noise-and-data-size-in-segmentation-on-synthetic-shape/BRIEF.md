# Label noise and data size in segmentation on synthetic shapes

## Seed
Label noise and data size in segmentation on synthetic shapes. generate 64x64 images of overlapping circles, squares and triangles on textured backgrounds with numpy (2k train / 500 test); train a small U-Net on CPU with 100-2,000 images and with 0-30 percent boundary/label noise, 3 seeds; measure mIoU per class. Keep it a small CPU study with reimplemented baselines, at least 5 seeds where cheap, and report negative or mixed results plainly.

## Research question
Label noise and data size in segmentation on synthetic shapes. generate 64x64 images of overlapping circles, squares and triangles on textured backgrounds with numpy (2k train / 500 test); train a small U-Net on CPU with 100-2,000 images and with 0-30 percent boundary/label noise, 3 seeds; measure mIoU per class. Keep it a small CPU study with reimplemented baselines, at least 5 seeds where cheap, and report negative or mixed results plainly.

Field: computer-vision detection-segmentation
Scale: quick study, cpu, about 30 minutes of experiments.

## Study design (final)
Question: how do training-set size (100-2000) and label-noise type (boundary jitter vs object class flips, level up to 0.3) jointly determine per-class IoU of a ~120k-parameter U-Net on synthetic 64x64 shapes, and do reimplemented robust losses (GCE, SCE) or a band-ignore CE help?
Hypotheses H1-H4 and their registered Welch tests are in proposal.md. Seeds: 4 in main and at N=100/2000, 3 in sweeps (budget). Ablations: size, flip-noise level, GCE q, training steps. Out of scope: sample-selection methods, Dice losses, real datasets, boundary-noise level sweep.
