# Design
Encoder: 3 conv3x3 (32,64,64 ch) + BatchNorm + ReLU, one 2x2 max-pool, adaptive avg-pool to 2x2, flatten -> 256-d.
SimCLR-style: projection MLP 256-128-64, NT-Xent tau=0.5, batch 128, Adam lr 1e-3 wd 1e-5, 60 epochs on the 1300-image unlabeled pool.
Augmentations: "geom" = random rotation +-15 deg, shift +-1 px, scale +-10% (bilinear, zero pad); "photo" = brightness x(1+-0.2) and Gaussian noise 0.1; "full" = both. No flips.
Rotation: 4-way classification of rot90 copies, linear head, same optimiser/epochs/batch.
Supervised: same encoder + linear head, 300 Adam steps lr 1e-3 wd 1e-4, batch min(n,32), no augmentation, no early stopping.
Probes: StandardScaler + LogisticRegression(C=1) on frozen 256-d features (eval-mode BN).
PCA+LR: PCA(16) fitted on the unlabeled pool pixels. Pixels+LR: 64 raw pixels. Random CNN: untrained encoder + probe.
Entry: python method/run.py --system {pca_lr,pixels_lr,random_cnn,supervised,rotation,simclr} --task {n10,n50,n200} --seed S --out F
