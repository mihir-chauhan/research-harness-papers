# Protocol
Env: point mass, pos += clip(a, |a|<=0.05), start uniform in [-j,j]^2 (j=0.01 main), goal (1,0) radius 0.05, circular obstacle centre (0.5,0) radius 0.15, 40 steps; collision checked at 4 points per step segment. Success = reach goal without collision. Mode = sign of y at crossing x=0.5.
Demos: 2,000 scripted trajectories via waypoint (0.5, +-0.35)+N(0,0.02^2), action noise N(0,0.003^2). Tasks differ in P(upper): 0.5, 0.8, 1.0. No held-out split is needed for model selection: nothing is tuned per run; fixed hyperparameters, fixed epochs, no early stopping. Evaluation: 200 closed-loop rollouts from fresh start states (seeded).
Seeds 0-9 main; 0-4 for sweeps/ablations. Pilot (debugging and choice of default jitter 0.01) used seed 99 only, not reported.
Tuning budget: none per system; shared hyperparameters set a priori (width 128, lr 1e-3, 40 epochs). Hardware: CPU, 2 threads; each run ~10 s.
Groups: main; sweep_jitter (j in 0,0.003,0.03,0.1; j=0.01 is the main rows); abl_ddpm_steps (1,5,10,20); abl_gmm_comp (1,3,5); abl_chunk (K=4,8, all three systems).
