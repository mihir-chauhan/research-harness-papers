# Design
Data: CSBM, K=3, N=900, mean degree 10 (N*d/2 random edges; intra-class w.p. h, else uniform other class), features mu*m_y + N(0,I) in R^16, m_y random unit vectors. Split 20/20/60 random per seed. Graph, features, split and init all depend on the seed.
Models (hidden 32, 2 layers, full batch Adam, 300 epochs, patience 100, test accuracy at best-validation epoch):
- MLP; GCN: D^-1/2(A+I)D^-1/2; H2GCN-style: H'=relu(H Ws + A1 H Wn), A1=D^-1/2 A D^-1/2 (no self loops), flags --sep 0 (tied weights) and --twohop 1 (strict 2-hop A2, extra Wn); no jumping knowledge.
- LP: F<-aS F+(1-a)Y0, 50 iterations, a in {0.5,0.9,0.99} picked on validation accuracy.
Hyperparameters (lr, dropout, wd) per system from method/tune.py (8-config grid, graphs seeds 100-102, validation accuracy): MLP (0.01,0.5,5e-3), GCN (0.05,0.5,5e-4), H2GCN (0.05,0.5,5e-3). Log in experiments/tuning_log.json.
