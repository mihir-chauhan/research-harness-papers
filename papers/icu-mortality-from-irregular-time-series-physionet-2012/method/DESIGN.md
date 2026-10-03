# Design
`method/data.py` builds hourly tensors. `method/run.py` holds all systems.
- Summary features: per variable min, max, mean, std, first, last, (count); plus static features and ICU-type one-hot. LR: median imputation, z-score, clip +-5, L2 C tuned. GBDT: sklearn HistGradientBoostingClassifier, NaN-native, lr 0.05, early stopping (patience 30, max 500 iters), min_samples_leaf 20, leaves/l2 tuned.
- Neural: own GRU cell, hidden tuned, Adam (lr tuned, wd 1e-4), batch 64, max 40 epochs, patience 6 on inner validation BCE, grad clip 5, head = dropout 0.2 -> Linear(H+static,32) -> ReLU -> Linear(1). Static input: 4 standardised + 4 ICU one-hot + 2 missing flags.
- GRU (forward-fill): input = z-scored forward-filled values (0 = training mean before first observation).
- GRU (mask+delta): input = [ffill, mask, delta/12].
- GRU-D: x_hat = m x + (1-m)(g_x x_last + (1-g_x) 0), g_x = exp(-relu(w*delta/12+b)) per variable; h <- exp(-relu(W d + b)) * h; GRU input [x_hat, m].
Flags `in_decay`, `h_decay`, `counts` used by ablations.
