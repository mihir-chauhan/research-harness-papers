# Design
method/run.py: data (sklearn digits scaled to [0,1], fixed stratified 60/40 split random_state=1234), symmetric noise on train labels (seeded),
CNN conv16-conv32-pool-conv64-pool-FC64-FC10 with BatchNorm (~41k params, 40,618 exactly), SGD momentum 0.9, lr 0.05 cosine, wd 5e-4, batch 64, 60 epochs, final-epoch model.
Systems: ce; ls (eps 0.1); mixup (alpha 1, input mixup within batch, mixed loss); smallloss (warm-up 10 epochs, then forget rate ramps linearly over 10 epochs to the noise rate, kept = lowest-loss samples in the batch).
Identical settings for all systems; only the flagged hyperparameters differ.
