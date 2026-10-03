# Design
Single entrypoint `method/run.py`. Data: `data/four_mutations_full_data.csv` (columns Variants, Fitness; 149,361 rows; from https://github.com/J-SNACKKB/FLIP/raw/main/splits/gb1/four_mutations_full_data.csv.zip). Sites 39,40,41,54 (wild type V,D,G,V). Only the 4-residue variant and the fitness are used.
- ridge: one-hot (80 features), unpenalised intercept, alpha in 10^{-3..3} by 5-fold CV (MSE) on the training set.
- pairwise: one-hot + 6 site pairs x 400 one-hot pair features (2,480 features); same ridge/CV.
- gp: kernel s2*exp(-gamma*Hamming) + noise*I, targets standardised, (s2,gamma,noise) grid of 72 triples by log marginal likelihood.
- cnn: Embedding(20,16) -> Conv1d(16,64,k=2,pad=1) -> ReLU -> Dropout -> Linear(320,32) -> ReLU -> Linear(32,1); AdamW, batch 32, MSE on standardised targets. Defaults (dropout 0.2, wd 0.1, 200 epochs, lr 3e-3) chosen on tuning seed 100 (group tune_cnn), see PROTOCOL.md.
Training draw is seeded by 1000*seed+N and identical across systems.
