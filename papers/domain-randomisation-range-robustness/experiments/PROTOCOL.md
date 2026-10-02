# Protocol
Task: batched numpy re-implementation of gymnasium CartPole-v1 (verified against gymnasium: max abs state diff 3e-7 over 30 steps, `method/check_dynamics.py`), episode cap 500, return = steps survived.
Randomised parameters: cart mass, pole mass, pole length, force magnitude, each independently scaled by exp(U(-w,w)); w is the half-width (w=0 nominal, w=1 spans x0.37..x2.7).
Policy/learner: 4-8-1 tanh MLP (threshold action), cross-entropy method, 60 iterations, population 40, 20% elites, 16 environments per iteration (common random numbers across candidates).
Systems (group main): No randomisation (w=0), Uniform DR narrow (w=0.25), Uniform DR wide (w=1.0), Success-gated curriculum (w 0 -> 1.0, step 0.05, gate 0.8).
Evaluation (fresh RNG stream, 300 episodes per level): nominal, and shift levels w in {0.25,0.5,0.75,1.0,1.5,2.0}. ret_robust = mean over the six shift levels; ret_ood = mean of w=1.5 and 2.0 (outside every trained range except the sweep's widest). Levels up to w=1.0 are in-range for wide DR and curriculum.
Seeds: 0-4 for all systems. Ablations: curriculum without gate (thresh 0), gate 0.5, gate 0.95 (group abl_curriculum). Sweep: uniform DR w in {0,0.25,0.5,1,1.5,2,3} (group sweep_width).
No hyperparameter tuning was done on test results beyond initial smoke runs of seed 1 for choosing evaluation levels. Hardware: CPU, 2 threads, a few seconds per run.
Significance: `rh compare` (paired across seeds); 5 seeds, so low power.
