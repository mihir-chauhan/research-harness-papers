# Protocol
Task = peak learning rate (lr1e-3, lr3e-3, lr1e-2 in group main; lr3e-4, lr3e-2 added later, also logged in group main). Systems: constant, cosine, step, schedulefree (see method/DESIGN.md).
Seeds 0,1,2 for all groups. Hyperparameters other than the peak LR are fixed a priori and not tuned (no tuning budget; no test split exists, validation loss is the reported number and nothing was selected on it except the peak LR which is the studied axis).
Ablation abl_warmup: warmup length 0/50/300 for cosine and 0/100/300 for constant at peak 1e-2 (100 is the default in main).
Hardware: shared Apple-silicon CPU, 2 threads per run, two runs at a time.
Sensitivity: derived by analysis/sens.py (logged via rh run) from results/runs.jsonl.
