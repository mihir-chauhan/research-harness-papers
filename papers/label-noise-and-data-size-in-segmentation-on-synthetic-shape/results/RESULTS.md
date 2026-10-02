# Results (all numbers in paper/sections/results.tex and ablations.tex via \rhval)
- H1 supported (clean mIoU N=100 -> 2000; Welch p=0.0015).
- H2 supported (flip vs boundary at N=500; Welch p=0.011); confounded by corrupted-pixel fraction.
- H3 refuted/inconclusive: flip drop is not larger at N=100 (0.19) than N=2000 (0.26); p=0.25.
- H4 not supported: GCE higher in mean under flips but n.s. (p=0.38); SCE no better; Band-ignore CE worse on clean and boundary.
- Sweeps: noise level monotone in mean; GCE q=0.9 worst; no late-training collapse up to 1200 steps at N=100.
