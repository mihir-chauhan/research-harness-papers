# Protocol
Tasks: digits_noise{0,20,40,60}. Split 1078 train / 719 test (fixed). Seeds 0-4. Hyperparameters fixed a priori (see method/DESIGN.md), no tuning, no validation, no early stopping;
LS eps=0.1, mixup alpha=1.0 and sweeps reported separately (the sweeps evaluate on the test split and are not used to choose the main settings).
Hardware: CPU (2 threads, shared machine), about 12 s per run; main grid 80 runs, ablations and sensitivity sweeps 70 runs.
