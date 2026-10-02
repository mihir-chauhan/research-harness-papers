# Design
- l96.py: two-scale Lorenz-96, K=36 slow X, J=10 fast Y per slow variable (360 fast), F=10, h=1, c=b=10; RK4 with dt=0.005, snapshots every 0.05 time units (10 RK4 steps); 400 spin-up snapshots (20 time units) discarded.
- run.py: systems persistence, climatology (training-set mean), linear (5-point circular stencil, ridge 1e-3, fitted on one-step increments of normalised data), cnn.
- CNN: 4 circular Conv1d layers (1->32->32->32->1, kernel 5, GELU between), residual: x_{t+1} = x_t + f(x_t) in normalised units; 10,657 parameters. Adam lr 3e-3 cosine to 0, batch 32, 1500 steps, grad-clip 1.0; loss = mean over k=1..K of MSE(x^_{t+k}, x_{t+k}) with full backpropagation through the unrolled emulator; optional Gaussian input noise on the initial state only.
- Data per seed: 32 train trajectories x 1250 snapshots, 8 validation x 500, 32 test x 1500, all from independent initial conditions.
- Evaluation: forecasts from every 50th snapshot of each test trajectory (896 windows), 100 steps (5 time units); free run 4000 steps (200 time units) from 16 test states.
