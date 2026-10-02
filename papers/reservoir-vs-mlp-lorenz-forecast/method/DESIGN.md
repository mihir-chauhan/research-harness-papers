# Design
`lib.py`: data generation (RK4, dt 0.02 for L63, 0.05 for L96 D=10 F=8, 200 burn-in samples, three independent trajectories per seed: train, test (20 segments of 100 warm-up + 15 Lyapunov times), reference 15000 steps), standardisation with training mean/std, the forecasters, and the metrics (VPT, climate W1 from 20 free runs of 10000 steps).
- ESN: N=500 (default), average degree 3, spectral radius rho (dense `numpy.linalg.eigvals`, deterministic), input scale sigma, ridge beta, readout on [r with even entries squared]; r_{t+1}=tanh(A r_t + W_in x_t + b); x_{t+1}=W_out phi(r_{t+1}).
- MLP: 3x128 GELU, residual one-step map on `delays` delay coordinates, Adam, batch 256, cosine decay, input noise; steps and lr tuned.
- GRU: 1 layer, 64 units, linear head, residual output, Adam, batch 32 windows of 48, cosine decay, grad-clip 1, input noise, first 20 steps of a window unscored; steps and lr tuned.
- Truth: the true ODE integrated from the last warm-up state; reference row for the sampling floor of the climate metrics.
- All rollouts clamp the predicted state to [-1e3, 1e3] per component.
`tune.py` staged grid search on validation seed 100 (stage A model grid, stage B optimiser grid); `merge_tuned.py` writes `tuned.json`; `run.py` is the entrypoint (prints CONFIG and METRICS); `lyap.py` Benettin exponents (logged, group `lyapunov`).
Grids: ESN rho{0.4,0.9,1.4} x sigma{0.1,0.3,1} x ridge{1e-8,1e-6,1e-4}; MLP A: delays{1,2,4} x noise{0,.01,.03} at 4000 steps, lr 2e-3; MLP B: steps{4000,8000,16000} x lr{1e-3,2e-3,5e-3}; GRU A: noise{0,.01,.03,.1,.3} at 3000 steps, lr 3e-3; GRU B: steps{3000,6000} x lr{1e-3,3e-3,1e-2}.
Tuned: see `method/tuned.json`; every grid cell is in `experiments/tuning_*.json` and in the tuning logs (group `tuning2`).
