# Proposal
## Question
How do SINDy-STLSQ, an MLP neural ODE and DMDc compare in multi-step prediction error and in closed-loop LQR/MPC cost as measurement noise and data quantity vary, on an inverted damped pendulum and the Van der Pol oscillator?
## Hypotheses
- H1: SINDy < MLP, DMDc in pred_nrmse at low noise / small data; advantage shrinks with noise. Refuted if MLP or DMDc is as good or better at noise 0 or N=200.
- H2: closed-loop cost differences across models are much smaller than prediction-error differences. Refuted if cost ranks and relative gaps track prediction error.
- H3: SINDy depends on threshold and library: removing trig terms on the pendulum hurts; lam sweep shows U-shape. Refuted if flat.
## Method / baselines
SINDy (STLSQ), Neural ODE (MLP, RK4 one-step loss), DMDc (linear LS, reimplemented), oracle true model as reference. Tasks pendulum, vdp. Metrics: pred_nrmse (40-step open loop, normalised), lqr_cost, mpc_cost (sampling-based CEM MPC), fail rates, support_f1. Noise 0-0.1 of state std; N in 200-5000 samples; 5 seeds.
## Ablations
No trig library; Savitzky-Golay smoothing; threshold sweep.
## Risks
Small scale; reimplemented baselines; model-specific tuning is minimal.
